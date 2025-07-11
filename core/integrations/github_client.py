# core/integrations/github_client.py
import httpx
from typing import Dict, List, Optional, Any
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

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
            "draft": False
        }
        
        logger.info(f"Creating PR: {title} from {head} to {base}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            
            if response.status_code == 422:
                # Log the error details for debugging
                error_details = response.json()
                logger.error(f"GitHub PR creation failed (422): {error_details}")
                
                # Check for common issues
                if 'errors' in error_details:
                    for error in error_details['errors']:
                        if 'message' in error:
                            logger.error(f"GitHub error: {error['message']}")
                            
                # Try to provide helpful error message
                if 'message' in error_details:
                    raise Exception(f"GitHub PR creation failed: {error_details['message']}")
                    
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
            
    async def get_pr_review_comments(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get review comments (line-specific comments) for a PR"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_pr_issue_comments(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get general issue comments for a PR"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def reply_to_review_comment(self, owner: str, repo: str, pr_number: int, 
                                    comment_id: int, body: str) -> Dict[str, Any]:
        """Reply to a specific review comment"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        
        data = {
            "body": body,
            "in_reply_to": comment_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
            
    async def reply_to_issue_comment(self, owner: str, repo: str, pr_number: int, 
                                   body: str) -> Dict[str, Any]:
        """Reply to a general issue comment (these don't support direct replies, so we mention the user)"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        data = {"body": body}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
            
    async def resolve_review_comment(self, owner: str, repo: str, comment_id: int) -> Dict[str, Any]:
        """Mark a review comment as resolved"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/comments/{comment_id}"
        
        data = {"resolved": True}
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
            
    async def get_file_content(self, owner: str, repo: str, file_path: str, ref: str = "main") -> str:
        """Get content of a specific file"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        
        params = {"ref": ref}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Decode base64 content
            import base64
            return base64.b64decode(data["content"]).decode("utf-8")