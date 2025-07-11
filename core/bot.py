import logging
from typing import List, Dict
from slack_bolt import App, BoltContext, Say, Ack
from slack_sdk import WebClient
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_sdk.errors import SlackApiError
from core.workflows import PRWorkflows
from services.approval_system import ApprovalService
from models.schemas import PRReviewRequest, PRCreationRequest
from config.settings import settings
import re
from utils.opik_tracer import trace
# from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio

logger = logging.getLogger(__name__)

class SlackBotHandler:
    def __init__(self):
        self.app = AsyncApp(
            token=settings.slack_bot_token,
            signing_secret=settings.slack_signing_secret
        )
        self.workflows = PRWorkflows()
        self.approval_service = ApprovalService()
        
        self._register_handlers()
        
    def _register_handlers(self):
        """Register all Slack event handlers"""
        
        @self.app.message("review pr")
        async def handle_pr_review(message, say, context):
            """Handle PR review requests"""
            trace("slack.pr_review_request", {
                "user_id": message['user'],
                "text": message['text'][:200]  # First 200 chars
            })
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                
                # Extract PR URL from message
                pr_url = self._extract_pr_url(text)
                if not pr_url:
                    await say("Please provide a valid GitHub PR URL")
                    return
                    
                # Extract Linear issue ID if present
                linear_issue_id = self._extract_linear_issue_id(text)
                
                # Create review request
                review_request = PRReviewRequest(
                    pr_url=pr_url,
                    thread_id=thread_ts,
                    user_id=user_id,
                    linear_issue_id=linear_issue_id
                )
                
                await say("🔍 Starting PR review... This may take a moment.")
                
                # Start workflow
                result = await self.workflows.pr_review_workflow(review_request)
                
                # Send results
                await self._send_review_results(say, result)
                
                trace("slack.pr_review_complete", {
                    "pr_url": pr_url,
                    "quality_score": result.code_quality_score
                })
                
            except Exception as e:
                logger.error(f"Error in PR review: {e}")
                trace("slack.pr_review_error", {"error": str(e)})
                await say(f"❌ Error reviewing PR: {str(e)}")
                
        @self.app.message("create pr")
        async def handle_pr_creation(message, say, context):
            """Handle PR creation requests"""
            trace("slack.pr_creation_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                
                # Parse the command: create pr <github_url> <branch_name> <description_or_linear_ticket>
                parsed_input = self._parse_create_pr_command(text)
                if not parsed_input:
                    await say("""
Please use the format: `create pr <github_url> <branch_name> <description_or_linear_ticket>`

Examples:
- `create pr https://github.com/owner/repo main Add dark theme support`
- `create pr https://github.com/owner/repo develop https://linear.app/team/issue/ABC-123`
- `create pr https://github.com/owner/repo feature/auth Fix login validation bug`
                    """)
                    return
                    
                repo_url = parsed_input['repo_url']
                base_branch = parsed_input['branch_name']
                description_or_linear = parsed_input['description']
                
                # Check if it's a Linear ticket or description
                linear_issue_id = None
                description = description_or_linear
                
                if 'linear.app' in description_or_linear:
                    linear_issue_id = self._extract_linear_issue_id(description_or_linear)
                    if linear_issue_id:
                        # Try to get Linear context for description
                        try:
                            from core.integrations.linear_client import LinearClient
                            linear_client = LinearClient()
                            linear_context = await linear_client.get_issue_details(linear_issue_id)
                            if linear_context:
                                description = linear_context.get('title', description_or_linear)
                                await say(f"📋 Found Linear issue: {description}")
                        except Exception as e:
                            logger.warning(f"Failed to fetch Linear context: {e}")
                            await say(f"⚠️ Could not fetch Linear details, using provided text as description")
                            description = description_or_linear
                
                # Generate new feature branch name
                feature_branch_name = self._generate_feature_branch_name(description)
                
                # Create PR request
                pr_request = PRCreationRequest(
                    description=description,
                    linear_issue_id=linear_issue_id,
                    repo_url=repo_url,
                    base_branch=base_branch,
                    branch_name=feature_branch_name,
                    channel_id=message['channel'],
                    thread_id=thread_ts,
                    user_id=user_id
                )
                
                await say(f"🚀 Starting PR creation...\n📂 Repository: {repo_url}\n🌿 Base branch: {base_branch}\n🆕 Feature branch: {feature_branch_name}\n📝 Description: {description}")
                
                # Start workflow
                result = await self.workflows.pr_creation_workflow(pr_request)
                
                # Send results
                await self._send_creation_results(say, result)
                
                trace("slack.pr_creation_complete", {
                    "pr_url": result.pr_url,
                    "files_changed": len(result.files_changed)
                })
                
            except Exception as e:
                logger.error(f"Error in PR creation: {e}")
                trace("slack.pr_creation_error", {"error": str(e)})
                await say(f"❌ Error creating PR: {str(e)}")
                
        @self.app.action("approve")
        async def handle_approval(ack, body, say):
            """Handle approval button clicks"""
            await ack()
            
            execution_id = body['actions'][0]['value']
            user_id = body['user']['id']
            
            self.approval_service.handle_approval_response(
                execution_id, True, user_id
            )
            
            await say(f"✅ <@{user_id}> approved execution {execution_id}")
            
        @self.app.action("reject")
        async def handle_rejection(ack, body, say):
            """Handle rejection button clicks"""
            await ack()
            
            execution_id = body['actions'][0]['value']
            user_id = body['user']['id']
            
            self.approval_service.handle_approval_response(
                execution_id, False, user_id
            )
            
            await say(f"❌ <@{user_id}> rejected execution {execution_id}")

        @self.app.event("message")
        async def handle_message_events(body, logger):
            logger.info(body)
            "Message received"
            
    def _parse_create_pr_command(self, text: str) -> Optional[Dict[str, str]]:
        """Parse create pr command with github_url, branch_name, and description"""
        import re
        
        # Remove "create pr" from the beginning
        cleaned_text = re.sub(r'^create\s+pr\s+', '', text, flags=re.IGNORECASE).strip()
        
        # Extract GitHub URL
        github_pattern = r'(https://github\.com/[\w-]+/[\w-]+(?:\.git)?)'
        github_match = re.search(github_pattern, cleaned_text)
        
        if not github_match:
            return None
            
        repo_url = github_match.group(1)
        
        # Remove the GitHub URL from the text
        remaining_text = cleaned_text.replace(repo_url, '').strip()
        
        # Split remaining text into parts
        parts = remaining_text.split(None, 1)  # Split into max 2 parts
        
        if len(parts) < 2:
            return None
            
        branch_name = parts[0]
        description = parts[1]
        
        return {
            'repo_url': repo_url,
            'branch_name': branch_name,
            'description': description
        }
        
    def _extract_pr_url(self, text: str) -> str:
        """Extract PR URL from message text"""
        pr_pattern = r'https://github\.com/[\w-]+/[\w-]+/pull/\d+'
        match = re.search(pr_pattern, text)
        return match.group(0) if match else None
        
    def _extract_linear_issue_id(self, text: str) -> str:
        """Extract Linear issue ID from message text"""
        linear_pattern = r'linear\.app/[\w-]+/issue/([\w-]+)'
        match = re.search(linear_pattern, text)
        return match.group(1) if match else None
        
    def _generate_feature_branch_name(self, description: str) -> str:
        """Generate feature branch name from description"""
        import uuid
        # Convert to lowercase, replace spaces with hyphens
        branch_name = description.lower().replace(' ', '-')
        # Remove special characters
        branch_name = re.sub(r'[^a-z0-9-]', '', branch_name)
        # Limit length
        branch_name = branch_name[:50]
        # Add unique suffix to avoid conflicts
        unique_suffix = uuid.uuid4().hex[:6]
        return f"feature/{branch_name}-{unique_suffix}"
        
    async def _send_review_results(self, say, result):
        """Send PR review results to Slack"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"## 🔍 PR Review Complete\n\n"
                           f"**Quality Score**: {result.code_quality_score}/10\n"
                           f"**Bugs Found**: {len(result.bugs_found)}\n"
                           f"**CI Status**: {result.ci_status}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Summary**:\n{result.review_summary}"
                }
            }
        ]
        
        if result.bugs_found:
            bug_text = "\n".join(f"• {bug}" for bug in result.bugs_found[:5])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Bugs Found**:\n{bug_text}"
                }
            })
            
        if result.recommendations:
            rec_text = "\n".join(f"• {rec}" for rec in result.recommendations[:5])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Recommendations**:\n{rec_text}"
                }
            })
            
        await say(blocks=blocks)
        
    async def _send_creation_results(self, say, result):
        """Send PR creation results to Slack"""
        status_emoji = "✅" if result.pr_url else "❌"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji} **PR Creation Complete**\n\n"
                           f"**PR URL**: {result.pr_url}\n"
                           f"**Branch**: {result.branch_name}\n"
                           f"**Files Changed**: {len(result.files_changed)}\n"
                           f"**Commits**: {len(result.commits)}"
                }
            }
        ]
        
        if result.files_changed:
            files_text = "\n".join(f"• {file}" for file in result.files_changed[:10])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Files Changed**:\n{files_text}"
                }
            })
            
        # Add test results
        test_status = "✅ Passed" if any(
            r.get("status") == "passed" for r in result.test_results.values()
        ) else "❌ Failed"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"**Test Results**: {test_status}"
            }
        })
        
        await say(blocks=blocks)
        
    async def start(self):
        """Start the Slack bot"""
        logger.info("Starting Slack bot...")
        
        # self.app.start(port=int(settings.slack_port))
        handler = AsyncSocketModeHandler(self.app, settings.slack_app_token)
        await handler.start_async()