# core/integrations/github_client.py
import httpx
from typing import Dict, List, Optional, Any
from config.settings import settings

class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {settings.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    async def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Get PR diff content"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={**self.headers, "Accept": "application/vnd.github.v3.diff"}
            )
            response.raise_for_status()
            return response.text
            
    async def get_pr_details(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get PR details"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get files changed in PR"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_ci_status(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """Get CI/CD status for commit"""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{sha}/status"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def create_pr(self, owner: str, repo: str, title: str, body: str, 
                       head: str, base: str = "main") -> Dict[str, Any]:
        """Create a new PR"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
            "draft": True
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
            
    async def add_pr_comment(self, owner: str, repo: str, pr_number: int, 
                           body: str) -> Dict[str, Any]:
        """Add comment to PR"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        data = {"body": body}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()