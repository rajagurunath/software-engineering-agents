# services/pr_creator.py
import asyncio
import uuid
from typing import Optional, Dict, Any,List
from pathlib import Path
from slack_sdk import WebClient
from utils.opik_tracer import trace
from core.sandbox import SandboxManager
from core.integrations.github_client import GitHubClient
from core.integrations.linear_client import LinearClient
from core.integrations.llm_client import LLMClient
from models.schemas import PRCreationRequest, PRCreationResponse
from services.code_analyzer import CodeAnalyzer
import logging

logger = logging.getLogger(__name__)

class PRCreatorService:
    def __init__(self):
        self.sandbox_manager = SandboxManager()
        self.github_client = GitHubClient()
        self.linear_client = LinearClient()
        self.llm_client = LLMClient()
        self.code_analyzer = CodeAnalyzer()
        
    async def create_pr(self, request: PRCreationRequest) -> PRCreationResponse:
        """Create PR in sandbox environment"""
        logger.info(f"Starting PR creation for: {request.description}")
        trace("pr_creator.start", {"description": request.description, "repo": request.repo_url})
        
        sandbox_id = f"pr-{uuid.uuid4().hex[:8]}"
        
        # Get Linear context if available
        linear_context = None
        if request.linear_issue_id:
            try:
                linear_context = await self.linear_client.get_issue_details(request.linear_issue_id)
            except Exception as e:
                logger.warning(f"Failed to fetch Linear context: {e}")
            
        with self.sandbox_manager.get_sandbox(sandbox_id) as sandbox:
            # Clone repository
            repo_path = sandbox.clone_repo(request.repo_url)
            
            # Create feature branch
            sandbox.create_branch(request.branch_name)
            
            # Clarification step
            from config.settings import settings
            if (not settings.skip_clarifications) and not request.clarification_questions:
                clarifications = await self._get_clarifications(
                    request.description, linear_context
                )
                return PRCreationResponse(
                    pr_url="",
                    branch_name=request.branch_name,
                    commits=[],
                    test_results={},
                    files_changed=[],
                    clarification_questions=clarifications
                )
            
            # Generate implementation plan
            implementation_plan = await self._generate_implementation_plan(
                request, linear_context, repo_path
            )
            
            # Share plan to Slack if configured
            from config.settings import settings
            if settings.share_plan_to_slack and request.thread_id:
                await self._post_plan_to_slack(request, implementation_plan)

            # Implement changes
            changes_made = await self._implement_changes(
                sandbox, implementation_plan, repo_path
            )
            
            # Run tests
            test_results = sandbox.run_tests()
            
            # If tests fail, attempt to fix
            if not self._tests_passed(test_results):
                fix_attempts = await self._fix_test_failures(
                    sandbox, test_results, changes_made
                )
                test_results = sandbox.run_tests()
                
            # Commit changes
            commit_message = f"feat: {request.description}"
            if linear_context:
                commit_message += f" (Linear: {linear_context['title']})"
                
            commit_sha = sandbox.commit_changes(commit_message)
            
            # Push branch
            sandbox.push_branch(request.branch_name)
            
            # Create PR
            owner, repo = self._parse_repo_url(request.repo_url)
            pr_response = await self.github_client.create_pr(
                owner=owner,
                repo=repo,
                title=f"feat: {request.description}",
                body=self._generate_pr_body(request, linear_context, changes_made),
                head=request.branch_name
            )
            
            result = PRCreationResponse(
                pr_url=pr_response["html_url"],
                branch_name=request.branch_name,
                commits=[commit_sha],
                test_results=test_results,
                files_changed=changes_made["files_changed"]
            )
            trace("pr_creator.finish", {"pr_url": result.pr_url, "files_changed": len(result.files_changed)})
            return result
            
    async def _get_clarifications(self, description: str, 
                                linear_context: Optional[Dict]) -> List[str]:
        """Generate clarification questions"""
        context = f"Description: {description}\n"
        if linear_context:
            context += f"Linear Context: {linear_context.get('description', '')}\n"
            
        prompt = f"""
        Based on the following request, generate clarification questions:
        
        {context}
        
        Generate 3-5 specific questions that would help implement this feature correctly.
        """

        questions = await self.llm_client.generate_clarifications(prompt)
        return questions.get("questions", [])

    async def _post_plan_to_slack(self, request: PRCreationRequest, plan: Dict) -> None:
        """Post understanding, plan, and file list to Slack thread"""
        from config.settings import settings
        try:
            client = WebClient(token=settings.slack_bot_token)
            files = [fc["path"] for fc in plan.get("file_changes", [])]
            message = (
                f"*📝 Understanding:*\n{request.description}\n\n"
                f"*🛠 Implementation Plan:*\n{plan.get('summary', '')}\n\n"
                f"*📄 Files to be created/modified:*\n" + "\n".join(f"- {p}" for p in files)
            )
            await client.chat_postMessage(channel=request.channel_id, text=message, thread_ts=request.thread_id)
        except Exception as e:
            logger.warning(f"Failed to post plan to Slack: {e}")

    async def _generate_implementation_plan(self, request: PRCreationRequest, linear_context: Optional[Dict], repo_path: str) -> Dict:
        """Generate detailed implementation plan"""
        trace("pr_creator.analyze_repo", {"repo_path": repo_path})
        
        # Perform comprehensive code analysis
        repo_analysis = self.code_analyzer.analyze_repository(repo_path)
        code_context = self.code_analyzer.get_code_context(repo_path)
        
        trace("pr_creator.repo_analysis", {
            "primary_language": repo_analysis['primary_language'],
            "frameworks": repo_analysis['frameworks'],
            "file_count": repo_analysis['file_count']
        })

        # Build comprehensive context for LLM
        context = f"""
        TASK: {request.description}
        
        REPOSITORY ANALYSIS:
        {self._format_repo_analysis(repo_analysis)}
        
        CODE CONTEXT:
        {code_context}
        """
        
        if linear_context:
            context += f"\nLINEAR ISSUE CONTEXT:\n"
            context += f"Title: {linear_context.get('title', '')}\n"
            context += f"Description: {linear_context.get('description', '')}\n"
            
        prompt = f"""You are a senior software engineer. Create a detailed implementation plan based on the repository analysis and task requirements.
        
        {context}
        
        IMPORTANT REQUIREMENTS:
        1. Use the CORRECT programming language and framework identified in the analysis
        2. Follow the existing code patterns and structure
        3. Respect the project's architecture and conventions
        4. Only suggest changes that make sense for this technology stack
        
        Provide a JSON response with:
        {{
            "summary": "Brief description of the implementation approach",
            "file_changes": [
                {{
                    "path": "relative/path/to/file",
                    "type": "create|modify|delete",
                    "content": "actual file content",
                    "reasoning": "why this change is needed"
                }}
            ],
            "test_files": [
                {{
                    "path": "path/to/test/file",
                    "content": "test file content",
                    "framework": "testing framework to use"
                }}
            ],
            "dependencies": [
                {{
                    "name": "dependency-name",
                    "version": "version",
                    "type": "production|development"
                }}
            ]
        }}
        """
        
        trace("pr_creator.generate_plan", {"description": request.description})
        plan = await self.llm_client.generate_implementation_plan(prompt)
        trace("pr_creator.plan_generated", {"files_to_change": len(plan.get("file_changes", []))})
        
        return plan
    
    def _format_repo_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format repository analysis for LLM context."""
        return f"""
Primary Language: {analysis['primary_language']}
All Languages: {', '.join(analysis['languages'].keys())}
Frameworks: {', '.join(analysis['frameworks'])}
Build Tools: {', '.join(analysis['build_tools'])}
Test Frameworks: {', '.join(analysis['test_frameworks'])}
Entry Points: {', '.join(analysis['entry_points'])}
Total Files: {analysis['file_count']}
Total Lines: {analysis['total_lines']}

Dependencies:
{self._format_dependencies(analysis['dependencies'])}
        """.strip()
    
    def _format_dependencies(self, dependencies: Dict[str, Any]) -> str:
        """Format dependencies for display."""
        formatted = []
        for dep_type, deps in dependencies.items():
            if isinstance(deps, dict):
                for category, dep_list in deps.items():
                    if dep_list:
                        formatted.append(f"{dep_type} {category}: {', '.join(list(dep_list.keys())[:5])}")
            elif isinstance(deps, list):
                formatted.append(f"{dep_type}: {', '.join(deps[:5])}")
        return '\n'.join(formatted) if formatted else "No dependencies found"
        
    async def _implement_changes(self, sandbox, plan: Dict, repo_path: str) -> Dict[str, Any]:
        """Implement the planned changes"""
        trace("pr_creator.implement_changes", {"plan_files": len(plan.get("file_changes", []))})
        
        changes_made = {
            "files_changed": [],
            "files_created": [],
            "tests_added": []
        }
        
        # Install dependencies first if needed
        dependencies = plan.get("dependencies", [])
        if dependencies:
            await self._install_dependencies(sandbox, dependencies, repo_path)
        
        # Process each file change
        for file_change in plan.get("file_changes", []):
            file_path = file_change["path"]
            change_type = file_change["type"]  # modify, create, delete
            content = file_change["content"]
            
            full_path = Path(repo_path) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if change_type == "create":
                with open(full_path, "w") as f:
                    f.write(content)
                changes_made["files_created"].append(file_path)
            elif change_type == "modify":
                with open(full_path, "w") as f:
                    f.write(content)
                changes_made["files_changed"].append(file_path)
                
        # Add tests
        for test_file in plan.get("test_files", []):
            test_path = test_file["path"]
            test_content = test_file["content"]
            
            test_full_path = Path(repo_path) / test_path
            test_full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(test_full_path, "w") as f:
                f.write(test_content)
            changes_made["tests_added"].append(test_path)
            
        return changes_made
    
    async def _install_dependencies(self, sandbox, dependencies: List[Dict], repo_path: str) -> None:
        """Install required dependencies."""
        trace("pr_creator.install_dependencies", {"count": len(dependencies)})
        
        # Group dependencies by type
        npm_deps = []
        pip_deps = []
        
        for dep in dependencies:
            name = dep.get("name", "")
            version = dep.get("version", "")
            dep_string = f"{name}@{version}" if version else name
            
            # Determine package manager based on repo structure
            if (Path(repo_path) / "package.json").exists():
                npm_deps.append(dep_string)
            elif (Path(repo_path) / "requirements.txt").exists():
                pip_deps.append(dep_string)
        
        # Install npm dependencies
        if npm_deps:
            cmd = f"npm install {' '.join(npm_deps)}"
            result = sandbox.run_command(cmd)
            if result.returncode != 0:
                logger.warning(f"Failed to install npm dependencies: {result.stderr}")
        
        # Install pip dependencies
        if pip_deps:
            cmd = f"pip install {' '.join(pip_deps)}"
            result = sandbox.run_command(cmd)
            if result.returncode != 0:
                logger.warning(f"Failed to install pip dependencies: {result.stderr}")
        
    def _tests_passed(self, test_results: Dict[str, Any]) -> bool:
        """Check if tests passed"""
        for result in test_results.values():
            if result.get("status") == "passed":
                return True
        return False
        
    async def _fix_test_failures(self, sandbox, test_results: Dict, 
                               changes_made: Dict) -> Dict[str, Any]:
        """Attempt to fix test failures"""
        failure_info = []
        for cmd, result in test_results.items():
            if result.get("status") == "failed":
                failure_info.append(f"Command: {cmd}\nError: {result.get('output', '')}")
                
        # Use LLM to suggest fixes
        fix_prompt = f"""
        The following test failures occurred:
        
        {chr(10).join(failure_info)}
        
        Files changed: {changes_made['files_changed']}
        
        Suggest specific fixes for these test failures.
        """
        
        fixes = await self.llm_client.suggest_test_fixes(fix_prompt)
        
        # Apply fixes
        for fix in fixes.get("fixes", []):
            file_path = fix["file"]
            new_content = fix["content"]
            
            with open(file_path, "w") as f:
                f.write(new_content)
                
        return fixes
        
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Parse GitHub repo URL to get owner and repo"""
        # Example: https://github.com/owner/repo.git
        parts = repo_url.replace(".git", "").split("/")
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo
        
    def _generate_pr_body(self, request: PRCreationRequest,
                         linear_context: Optional[Dict],
                         changes_made: Dict) -> str:
        """Generate PR body content"""
        body = f"""
## Description
{request.description}

## Changes Made
- Files Modified: {len(changes_made['files_changed'])}
- Files Created: {len(changes_made['files_created'])}
- Tests Added: {len(changes_made['tests_added'])}

### Files Changed:
{chr(10).join(f"- {file}" for file in changes_made['files_changed'])}

### Files Created:
{chr(10).join(f"- {file}" for file in changes_made['files_created'])}

### Tests Added:
{chr(10).join(f"- {file}" for file in changes_made['tests_added'])}
        """
        
        if linear_context:
            body += f"""
## Linear Issue
- **Title**: {linear_context.get('title', 'N/A')}
- **Priority**: {linear_context.get('priority', 'N/A')}
- **Status**: {linear_context.get('state', {}).get('name', 'N/A')}

[View in Linear]({linear_context.get('url', '')})
            """
            
        return body