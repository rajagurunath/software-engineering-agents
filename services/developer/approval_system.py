import asyncio
from typing import Dict, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from models.schemas import ApprovalRequest, TaskStatus
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ApprovalService:
    def __init__(self):
        self.slack_client = WebClient(token=settings.slack_bot_token)
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        
    async def request_approval(self, approval_request: ApprovalRequest) -> None:
        """Request approval via Slack"""
        self.pending_approvals[approval_request.execution_id] = approval_request
        
        await self.send_approval_request(approval_request)
        
    async def send_approval_request(self, approval_request: ApprovalRequest) -> None:
        """Send approval request to Slack"""
        context = approval_request.context
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🚨 *Approval Required*\n\n"
                           f"**Type**: {approval_request.approval_type}\n"
                           f"**Requested by**: <@{approval_request.requested_by}>\n"
                           f"**Execution ID**: {approval_request.execution_id}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Details**:\n"
                           f"Repository: {context.get('repo_url', 'N/A')}\n"
                           f"Branch: {context.get('branch_name', 'N/A')}\n"
                           f"Description: {context.get('description', 'N/A')}"
                }
            },
            {
                "type": "actions",
                "block_id": f"approval_actions_{approval_request.execution_id}",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Approve"},
                        "style": "primary",
                        "action_id": "approve",
                        "value": approval_request.execution_id
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Reject"},
                        "style": "danger",
                        "action_id": "reject",
                        "value": approval_request.execution_id
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "ℹ️ Details"},
                        "action_id": "details",
                        "value": approval_request.execution_id
                    }
                ]
            }
        ]
        
        try:
            # Send to approval channel (configure channel in settings)
            response = await self.slack_client.chat_postMessage(
                channel=settings.approvals_channel,
                text="Approval Required",
                blocks=blocks
            )
            
            logger.info(f"Approval request sent: {response['ts']}")
            
        except SlackApiError as e:
            logger.error(f"Failed to send approval request: {e}")
            raise
            
    async def wait_for_approval_response(self, execution_id: str) -> bool:
        """Wait for approval response"""
        # In a real implementation, this would use DBOS durable execution
        # For now, we'll simulate waiting
        await asyncio.sleep(1)
        return True  # Simulated approval
        
    def handle_approval_response(self, execution_id: str, approved: bool,
                               approver_id: str) -> None:
        """Handle approval response from Slack"""
        if execution_id in self.pending_approvals:
            approval_request = self.pending_approvals[execution_id]
            
            logger.info(f"Approval response for {execution_id}: {approved} by {approver_id}")
            
            # Update approval status
            # This would trigger the workflow to continue
            
            # Remove from pending
            del self.pending_approvals[execution_id]