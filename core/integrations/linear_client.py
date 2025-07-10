# core/integrations/linear_client.py
import httpx
from typing import Dict, Optional, Any
from config.settings import settings

class LinearClient:
    def __init__(self):
        self.base_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": f"Bearer {settings.linear_api_key}",
            "Content-Type": "application/json"
        }
        
    async def get_issue_details(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get Linear issue details"""
        query = """
        query GetIssue($id: String!) {
            issue(id: $id) {
                id
                title
                description
                priority
                state {
                    name
                }
                assignee {
                    name
                    email
                }
                project {
                    name
                }
                labels {
                    nodes {
                        name
                        color
                    }
                }
                comments {
                    nodes {
                        body
                        user {
                            name
                        }
                        createdAt
                    }
                }
            }
        }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": {"id": issue_id}}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("issue")
            
    async def update_issue_status(self, issue_id: str, status: str) -> bool:
        """Update issue status"""
        mutation = """
        mutation UpdateIssue($id: String!, $status: String!) {
            issueUpdate(id: $id, input: {stateId: $status}) {
                success
            }
        }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json={"query": mutation, "variables": {"id": issue_id, "status": status}}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("issueUpdate", {}).get("success", False)