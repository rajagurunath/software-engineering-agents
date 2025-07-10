# core/sandbox.py
import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from git import Repo
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class SandboxEnvironment:
    def __init__(self, sandbox_id: str, base_path: str = "/tmp/sandbox"):
        self.sandbox_id = sandbox_id
        self.base_path = Path(base_path)
        self.sandbox_path = self.base_path / sandbox_id
        self.repo: Optional[Repo] = None
        
    def create(self) -> None:
        """Create sandbox directory"""
        self.sandbox_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created sandbox: {self.sandbox_path}")
        
    def _inject_token(self, repo_url: str) -> str:
        """Insert GitHub token into HTTPS URL if available and not already present."""
        from urllib.parse import urlparse, urlunparse
        from config.settings import settings

        token = settings.github_token
        if not token or "@" in repo_url:
            return repo_url
        parsed = urlparse(repo_url)
        if parsed.scheme != "https":
            return repo_url
        netloc = f"{token}@{parsed.netloc}"
        return urlunparse(parsed._replace(netloc=netloc))

    def clone_repo(self, repo_url: str, branch: str = "main") -> str:
        """Clone repository into sandbox using token if provided"""
        repo_path = self.sandbox_path / "repo"
        if repo_path.exists():
            shutil.rmtree(repo_path)

        repo_url_with_token = self._inject_token(repo_url)
        self.repo = Repo.clone_from(repo_url_with_token, repo_path, branch=branch)
        logger.info(f"Cloned {repo_url} to {repo_path}")
        return str(repo_path)
        
    def create_branch(self, branch_name: str) -> None:
        """Create and checkout new branch"""
        if not self.repo:
            raise ValueError("Repository not cloned")
            
        # Create new branch from current HEAD
        new_branch = self.repo.create_head(branch_name)
        new_branch.checkout()
        logger.info(f"Created and checked out branch: {branch_name}")
        
    def run_command(self, command: str, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run shell command in sandbox"""
        if cwd is None:
            cwd = self.sandbox_path / "repo"
            
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        logger.info(f"Command: {command}, Exit code: {result.returncode}")
        if result.returncode != 0:
            logger.error(f"Command failed: {result.stderr}")
            
        return result
        
    def run_tests(self) -> Dict[str, Any]:
        """Run test suite in sandbox"""
        repo_path = self.sandbox_path / "repo"
        
        # Try different test runners
        test_commands = [
            "python -m pytest --tb=short",
            "python -m unittest discover",
            "npm test",
            "make test"
        ]
        
        results = {}
        for cmd in test_commands:
            try:
                result = self.run_command(cmd)
                if result.returncode == 0:
                    results[cmd] = {
                        "status": "passed",
                        "output": result.stdout
                    }
                    break
                else:
                    results[cmd] = {
                        "status": "failed",
                        "output": result.stderr
                    }
            except Exception as e:
                results[cmd] = {
                    "status": "error",
                    "output": str(e)
                }
                
        return results
        
    def commit_changes(self, message: str) -> str:
        """Commit changes to repository"""
        if not self.repo:
            raise ValueError("Repository not cloned")
            
        # Add all changes
        self.repo.git.add(A=True)
        
        # Commit changes
        commit = self.repo.index.commit(message)
        logger.info(f"Committed changes: {commit.hexsha}")
        return commit.hexsha
        
    def push_branch(self, branch_name: str) -> None:
        """Push branch to remote"""
        if not self.repo:
            raise ValueError("Repository not cloned")
            
        origin = self.repo.remote("origin")
        origin.push(branch_name)
        logger.info(f"Pushed branch: {branch_name}")
        
    def cleanup(self) -> None:
        """Clean up sandbox directory"""
        if self.sandbox_path.exists():
            shutil.rmtree(self.sandbox_path)
            logger.info(f"Cleaned up sandbox: {self.sandbox_path}")

class SandboxManager:
    def __init__(self, base_path: str = "/tmp/sandbox", max_concurrent: int = 5):
        self.base_path = base_path
        self.max_concurrent = max_concurrent
        self.active_sandboxes: Dict[str, SandboxEnvironment] = {}
        
    @contextmanager
    def get_sandbox(self, sandbox_id: str):
        """Context manager for sandbox lifecycle"""
        if len(self.active_sandboxes) >= self.max_concurrent:
            raise RuntimeError("Maximum concurrent sandboxes reached")
            
        sandbox = SandboxEnvironment(sandbox_id, self.base_path)
        sandbox.create()
        
        self.active_sandboxes[sandbox_id] = sandbox
        
        try:
            yield sandbox
        finally:
            sandbox.cleanup()
            self.active_sandboxes.pop(sandbox_id, None)