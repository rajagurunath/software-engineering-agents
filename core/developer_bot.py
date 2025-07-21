"""
Developer Bot Handler - Dedicated Slack bot for Junior/Senior Engineer Agent
"""
import logging
import re
import uuid
from typing import Dict, Any, Optional
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from core.workflows import PRWorkflows
from services.developer.approval_system import ApprovalService
from models.schemas import PRReviewRequest, PRCreationRequest, PRCommentHandlingRequest
from utils.slack_response_helpers import (
    send_review_results,
    send_creation_results, 
    send_comment_handling_results
)
from config.settings import settings
from utils.opik_tracer import trace

logger = logging.getLogger(__name__)

class DeveloperBotHandler:
    """Dedicated Slack bot handler for Junior/Senior Engineer Agent"""
    
    def __init__(self):
        self.app = AsyncApp(
            token=settings.slack_developer_bot_token,
            signing_secret=settings.slack_developer_signing_secret
        )
        self.workflows = PRWorkflows()
        self.approval_service = ApprovalService()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all Developer-specific Slack event handlers"""
   
        @self.app.message("review pr")
        async def handle_pr_review(message, say, context):
            """Handle PR review requests"""
            trace("slack.pr_review_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
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
                await send_review_results(say, result)
                
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
                
                # Parse the structured command
                parsed_input = self._parse_structured_pr_command(text)
                if not parsed_input:
                    await say("""
🚀 **Create PR Command Formats:**

**Option 1: Multi-line structured format**
```
create pr
repo: https://github.com/owner/repo
branch: main
description: Add dark theme support
```

**Option 2: Multi-line with Linear**
```
create pr
repo: https://github.com/owner/repo  
branch: develop
linear: https://linear.app/team/issue/ABC-123
```

**Option 3: One-line format**
```
create pr --repo=https://github.com/owner/repo --branch=main --desc="Add dark theme"
```

**Option 4: One-line with Linear**
```
create pr --repo=https://github.com/owner/repo --branch=develop --linear=https://linear.app/team/issue/ABC-123
```

**Note:** URLs should not have angle brackets < >
                    """)
                    return
                
                # Debug logging
                logger.info(f"Parsed input: {parsed_input}")
                    
                # Extract values from parsed input
                repo_url = parsed_input['repo_url']
                base_branch = parsed_input['base_branch']
                description = parsed_input['description']
                linear_url = parsed_input.get('linear_url')
                
                # Validate URL format
                if not repo_url.startswith('https://github.com/'):
                    await say(f"❌ Invalid GitHub URL format: {repo_url}\nPlease use: https://github.com/owner/repo")
                    return
                
                # Handle Linear ticket if provided
                linear_issue_id = None
                if linear_url:
                    linear_issue_id = self._extract_linear_issue_id(linear_url)
                    if linear_issue_id:
                        try:
                            from core.integrations.linear_client import LinearClient
                            linear_client = LinearClient()
                            linear_context = await linear_client.get_issue_details(linear_issue_id)
                            if linear_context:
                                description = linear_context.get('title', description)
                            else:
                                await say(f"⚠️ Could not fetch Linear details for {linear_issue_id}")
                        except Exception as e:
                            logger.warning(f"Linear API error: {e}")
                            await say(f"⚠️ Linear API error: {str(e)}")
                
                # Generate feature branch name
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
                await send_creation_results(say, result)
                
                trace("slack.pr_creation_complete", {
                    "pr_url": result.pr_url,
                    "files_changed": len(result.files_changed)
                })
                
            except Exception as e:
                logger.error(f"Error in PR creation: {e}")
                trace("slack.pr_creation_error", {"error": str(e)})
                await say(f"❌ Error creating PR: {str(e)}")

        @self.app.message("handle comments")
        async def handle_pr_comments(message, say, context):
            """Handle PR comments requests"""
            trace("slack.pr_comments_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                channel_id = message['channel']
                
                # Extract PR URL from message
                pr_url = self._extract_pr_url(text)
                if not pr_url:
                    await say("""
🔧 **Handle Comments Command Format:**

```
handle comments for the pr url https://github.com/owner/repo/pull/123
```

This will:
- Fetch all review comments from the PR
- Analyze each comment and determine required changes
- Make code modifications to address the feedback
- Commit changes with descriptive messages
- Provide a summary of all changes made
                    """)
                    return
                
                # Validate it's a PR URL
                if '/pull/' not in pr_url:
                    await say("❌ Please provide a valid GitHub PR URL (must contain '/pull/')")
                    return
                
                # Create comment handling request
                comment_request = PRCommentHandlingRequest(
                    pr_url=pr_url,
                    thread_id=thread_ts,
                    user_id=user_id,
                    channel_id=channel_id
                )
                
                await say(f"🔧 Starting to handle PR comments for: {pr_url}\n⏳ This may take a few minutes...")
                
                # Start workflow
                result = await self.workflows.pr_comment_handling_workflow(comment_request)
                
                # Send results
                await send_comment_handling_results(say, result)
                
                trace("slack.pr_comments_complete", {
                    "pr_url": pr_url,
                    "comments_handled": result.comments_handled
                })
                
            except Exception as e:
                logger.error(f"Error in PR comment handling: {e}")
                trace("slack.pr_comments_error", {"error": str(e)})
                await say(f"❌ Error handling PR comments: {str(e)}")

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

        @self.app.event("assistant_thread_started")
        async def handle_assistant_thread_started_events(body, logger, say):
            logger.info(body)
            user_id = body['event']['assistant_thread']['user_id']
            await say(f"Hello <@{user_id}>, I am your Development Engineer! I can help you with PR reviews, PR creation, and handling PR comments. How can I assist you today?")

    def _parse_structured_pr_command(self, text: str) -> Dict[str, str]:
        """Parse structured PR command with multiple format support"""
        import re
        
        # Try one-line format first: create pr --repo=... --branch=... --desc=...
        oneline_pattern = r'create\s+pr\s+--repo=([^\s]+)\s+--branch=([^\s]+)\s+--(?:desc|description)="([^"]+)"'
        oneline_match = re.search(oneline_pattern, text, re.IGNORECASE)
        
        if oneline_match:
            repo_url = oneline_match.group(1).strip('<>')  # Remove angle brackets
            return {
                'repo_url': repo_url,
                'base_branch': oneline_match.group(2),
                'description': oneline_match.group(3),
            }
        
        # Try one-line with linear: create pr --repo=... --branch=... --linear=...
        oneline_linear_pattern = r'create\s+pr\s+--repo=([^\s]+)\s+--branch=([^\s]+)\s+--linear=([^\s]+)'
        oneline_linear_match = re.search(oneline_linear_pattern, text, re.IGNORECASE)
        
        if oneline_linear_match:
            repo_url = oneline_linear_match.group(1).strip('<>')  # Remove angle brackets
            return {
                'repo_url': repo_url,
                'base_branch': oneline_linear_match.group(2),
                'description': 'From Linear ticket',
                'linear_url': oneline_linear_match.group(3).strip('<>'),
            }
        
        # Try structured multi-line format
        lines = text.split('\n')
        if len(lines) < 4:  # Need at least 4 lines for structured format
            return None
            
        parsed = {}
        
        for line in lines[1:]:  # Skip first line "create pr"
            line = line.strip()
            if ':' not in line:
                continue
                
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip().strip('<>')  # Remove angle brackets and whitespace
            
            if key == 'repo':
                parsed['repo_url'] = value
            elif key == 'branch':
                parsed['base_branch'] = value
            elif key in ['description', 'desc']:
                parsed['description'] = value
            elif key == 'linear':
                parsed['linear_url'] = value
                if 'description' not in parsed:
                    parsed['description'] = 'From Linear ticket'
        
        # Validate required fields
        if 'repo_url' not in parsed or 'base_branch' not in parsed:
            return None
            
        if 'description' not in parsed and 'linear_url' not in parsed:
            return None
        
        return parsed
        
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
        # Convert to lowercase, replace spaces with hyphens
        branch_name = description.lower().replace(' ', '-')
        # Remove special characters
        branch_name = re.sub(r'[^a-z0-9-]', '', branch_name)
        # Limit length
        branch_name = branch_name[:50]
        # Add unique suffix to avoid conflicts
        unique_suffix = uuid.uuid4().hex[:6]
        return f"feature/{branch_name}-{unique_suffix}"

    async def start(self):
        """Start the Developer Slack bot"""
        logger.info("Starting Developer Slack bot...")
        
        handler = AsyncSocketModeHandler(self.app, settings.slack_developer_app_token)
        await handler.start_async()