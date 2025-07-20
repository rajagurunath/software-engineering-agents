import logging
from typing import List, Dict
from slack_bolt import App, BoltContext, Say, Ack
from slack_sdk import WebClient
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_sdk.errors import SlackApiError
from core.workflows import PRWorkflows
from services.developer.approval_system import ApprovalService
from models.schemas import PRReviewRequest, PRCreationRequest, PRCommentHandlingRequest
from config.settings import settings
from services.architect.service import ArchitectService
from services.architect.models import ResearchType
import re
from utils.opik_tracer import trace
import asyncio
import plotly.io as pio
import plotly.graph_objects as go
import tempfile
import os
import json


def save_plotly_image_from_json(plotly_json: str) -> str:
    fig = pio.from_json(plotly_json)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        fig.write_image(tmpfile.name)
        return tmpfile.name

logger = logging.getLogger(__name__)

class SlackBotHandler:
    def __init__(self):
        self.app = AsyncApp(
            token=settings.slack_bot_token,
            signing_secret=settings.slack_signing_secret
        )
        # self.sql_app = AsyncApp(
        #     token=settings.slack_sql_bot_token,
        #     signing_secret=settings.slack_sql_signing_secret
        # )
        self.workflows = PRWorkflows()
        self.approval_service = ApprovalService()
        
        # Initialize architect service
        self.architect_service = ArchitectService()
        
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
        
        # @self.app.message("sql bot")
        # async def handle_sql_bot(message, say, context):
        #     """Handle SQL bot requests"""
        #     trace("slack.sql_bot_request", {
        #         "user_id": message['user'],
        #         "text": message['text'][:200]
        #     })
        #     await say("Hello, I am the SQL bot. How can I help you today?")
        #     try:
        #         text = message['text']
        #         user_id = message['user']
        #         thread_ts = message.get('thread_ts', message['ts'])
        #         import requests
        #         response = requests.post(settings.sql_bot_url, json={"query": text,"top_k": 5})
        #         response_json = response.json()
        #         print(response_json)
        #         await say(response_json["data"])
        #     except Exception as e:
        #         logger.error(f"Error in SQL bot: {e}")
        @self.app.message("sql bot")
        async def handle_sql_bot(message, say, context):
            trace("slack.sql_bot_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            await say("Hello, I am the SQL bot. How can I help you today?")
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                channel = message['channel']
                import requests
                response = requests.post(settings.sql_bot_url, json={"query": text, "top_k": 5})
                response_json = response.json()

                # Send the data as a formatted message
                data = response_json.get("data")
                if data is not None:
                    # Format as pretty JSON for Slack
                    formatted_data = f"```{json.dumps(data, indent=2)}```"
                    await say(formatted_data)

                # Send the plotly chart if present
                plotly_json = response_json.get("plotly_json")
                if plotly_json:
                    image_path = save_plotly_image_from_json(plotly_json)
                    try:
                        await self.app.client.files_upload_v2(
                            channel=channel,
                            thread_ts=thread_ts,
                            file=image_path,
                            title="Chart"
                        )
                    finally:
                        os.remove(image_path)

                # Optionally, send follow-up questions if present
                followups = response_json.get("followup_questions")
                if followups:
                    if isinstance(followups, list):
                        followup_text = "*Follow-up questions you can ask:*\n" + "\n".join(f"- {q}" for q in followups if q)
                        await say(followup_text)

            except Exception as e:
                logger.error(f"Error in SQL bot: {e}")

        @self.app.message("ask architect")
        async def handle_architect_request(message, say, context):
            """Handle architect research requests"""
            trace("slack.architect_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                channel = message['channel']
                
                # Parse architect command
                research_params = self._parse_architect_command(text)
                if not research_params:
                    await say(self._get_architect_help_message())
                    return
                
                # Send initial response
                await say(f"🏗️ Starting deep research on: *{research_params['query']}*\n"
                         f"Research type: {research_params.get('type', 'auto-detected')}\n"
                         f"This may take a few minutes...")
                
                # Conduct research
                result = await self.architect_service.conduct_research(
                    query=research_params['query'],
                    user_id=user_id,
                    research_type=research_params.get('type'),
                    thread_id=thread_ts,
                    channel_id=channel,
                    include_visualizations=research_params.get('include_viz', True)
                )
                
                # Send results to Slack
                await self._send_architect_results(say, result, channel, thread_ts)
                
                trace("slack.architect_complete", {
                    "research_id": result.research_id,
                    "findings_count": len(result.detailed_findings)
                })
                
            except Exception as e:
                logger.error(f"Architect request failed: {e}")
                trace("slack.architect_error", {"error": str(e)})
                await say(f"❌ Research failed: {str(e)}")

        @self.app.message("quick data")
        async def handle_quick_data(message, say, context):
            """Handle quick data queries"""
            trace("slack.quick_data_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                channel = message['channel']
                
                # Extract query (remove command prefix)
                query = text.replace('quick data', '').strip()
                if not query:
                    await say("Please provide a data query. Example: `quick data How many devices are online?`")
                    return
                
                await say(f"📊 Analyzing data for: *{query}*")
                
                result = await self.architect_service.quick_data_analysis(query, user_id)
                
                if result["success"]:
                    response = f"**Data Analysis Result:**\n{result['answer']}"
                    await say(response)
                    
                    # Handle Plotly visualization
                    if result.get("plotly_json"):
                        image_path = save_plotly_image_from_json(result["plotly_json"])
                        try:
                            await self.app.client.files_upload_v2(
                                channel=channel,
                                thread_ts=thread_ts,
                                file=image_path,
                                title="Data Visualization"
                            )
                        finally:
                            os.remove(image_path)
                else:
                    await say(f"❌ Data query failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Quick data query failed: {e}")
                await say(f"❌ Data query failed: {str(e)}")

        @self.app.message("quick docs")
        async def handle_quick_docs(message, say, context):
            """Handle quick documentation searches"""
            trace("slack.quick_docs_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                
                # Extract query (remove command prefix)
                query = text.replace('quick docs', '').strip()
                if not query:
                    await say("Please provide a documentation query. Example: `quick docs How to stake IO tokens?`")
                    return
                
                await say(f"📚 Searching documentation for: *{query}*")
                
                result = await self.architect_service.quick_docs_search(query, user_id)
                
                if result["success"]:
                    response = f"**Documentation Search Result:**\n{result['answer']}"
                    
                    # Add relevant links if available
                    if result.get("relevant_links"):
                        response += "\n\n**Relevant Links:**\n"
                        for link in result["relevant_links"][:3]:
                            response += f"• {link}\n"
                    
                    # Add followup questions if available
                    if result.get("followup_questions"):
                        response += "\n**Related Questions:**\n"
                        for question in result["followup_questions"][:3]:
                            response += f"• {question}\n"
                    
                    await say(response)
                else:
                    await say(f"❌ Documentation search failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Quick docs search failed: {e}")
                await say(f"❌ Documentation search failed: {str(e)}")

        @self.app.message("quick pr")
        async def handle_quick_pr_analysis(message, say, context):
            """Handle quick PR analysis requests"""
            trace("slack.quick_pr_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                
                # Extract PR URL
                pr_url = self._extract_pr_url(text)
                if not pr_url:
                    await say("Please provide a valid GitHub PR URL. Example: `quick pr https://github.com/owner/repo/pull/123`")
                    return
                
                await say(f"🔍 Analyzing PR: {pr_url}")
                
                result = await self.architect_service.analyze_pr(pr_url, user_id)
                
                if result["success"]:
                    response = f"""**PR Analysis Complete:**

**Quality Score:** {result['quality_score']}/10
**CI Status:** {result['ci_status']}
**Bugs Found:** {len(result['bugs_found'])}

**Summary:**
{result['summary']}

**Recommendations:**
"""
                    for rec in result['recommendations'][:5]:
                        response += f"• {rec}\n"
                    
                    await say(response)
                else:
                    await say(f"❌ PR analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"PR analysis failed: {e}")
                await say(f"❌ PR analysis failed: {str(e)}")

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
                await self._send_creation_results(say, result)
                
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
                await self._send_comment_handling_results(say, result)
                
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
        async def handle_assistant_thread_started_events(body, logger,say):
            logger.info(body)
            user_id = body['event']['assistant_thread']['user_id']
            await say(f"Hello <@{user_id}>, I am your assistant! How can I help you today?")

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
        
    async def _send_comment_handling_results(self, say, result):
        """Send PR comment handling results to Slack"""
        status_emoji = "✅" if result.comments_handled > 0 else "ℹ️"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji} **PR Comment Handling Complete**\n\n"
                           f"**PR URL**: {result.pr_url}\n"
                           f"**Comments Handled**: {result.comments_handled}\n"
                           f"**Files Modified**: {len(result.files_modified)}\n"
                           f"**Commits Made**: {len(result.commits_made)}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Summary**:\n{result.summary}"
                }
            }
        ]
        
        if result.files_modified:
            files_text = "\n".join(f"• {file}" for file in result.files_modified[:10])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Files Modified**:\n{files_text}"
                }
            })
        
        if result.unresolved_comments:
            unresolved_text = "\n".join(f"• {comment.get('body', '')[:100]}..." for comment in result.unresolved_comments[:3])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Unresolved Comments** ({len(result.unresolved_comments)}):\n{unresolved_text}"
                }
            })
        
        await say(blocks=blocks)
        
    def _parse_architect_command(self, text: str) -> Dict[str, str]:
        """Parse architect command from Slack message"""
        text = text.strip()
        
        # Check for architect command
        if not text.startswith('ask architect'):
            return None
        
        # Remove 'ask architect' prefix
        query_text = text[12:].strip()
        
        if not query_text:
            return None
        
        # Parse optional parameters
        params = {
            'query': query_text,
            'type': None,
            'include_viz': True
        }
        
        # Check for research type specification
        if '--type=' in query_text:
            parts = query_text.split('--type=')
            params['query'] = parts[0].strip()
            type_part = parts[1].split()[0]
            
            try:
                params['type'] = ResearchType(type_part)
            except ValueError:
                pass  # Invalid type, will auto-detect
        
        # Check for visualization flag
        if '--no-viz' in query_text:
            params['include_viz'] = False
            params['query'] = params['query'].replace('--no-viz', '').strip()
        
        return params

    async def _send_architect_results(self, say, result, channel: str, thread_ts: str) -> None:
        """Send comprehensive research results to Slack"""
        try:
            # Send executive summary
            summary_blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"## 🏗️ Research Complete\n\n"
                               f"**Query**: {result.original_query}\n"
                               f"**Type**: {result.research_type.value}\n"
                               f"**Duration**: {result.total_duration_seconds:.1f}s\n"
                               f"**Steps**: {len(result.detailed_findings)}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"**Executive Summary**:\n{result.executive_summary}"
                    }
                }
            ]
            
            await say(blocks=summary_blocks)
            
            # Send recommendations
            if result.recommendations:
                rec_text = "\n".join(f"• {rec}" for rec in result.recommendations[:5])
                rec_blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"**💡 Recommendations**:\n{rec_text}"
                        }
                    }
                ]
                await say(blocks=rec_blocks)
            
            # Upload visualizations
            for viz in result.data_visualizations:
                if viz.get("plotly_json"):
                    image_path = save_plotly_image_from_json(viz["plotly_json"])
                    if image_path:
                        try:
                            await self.app.client.files_upload_v2(
                                channel=channel,
                                thread_ts=thread_ts,
                                file=image_path,
                                title=viz.get("title", "Data Visualization")
                            )
                        finally:
                            os.remove(image_path)
            
            # Upload HTML report if available
            if result.html_report_path:
                try:
                    await self.app.client.files_upload_v2(
                        channel=channel,
                        thread_ts=thread_ts,
                        file=result.html_report_path,
                        title=f"Research Report - {result.original_query[:30]}",
                        filetype="html"
                    )
                except Exception as e:
                    logger.error(f"Failed to upload HTML report: {e}")
            
        except Exception as e:
            logger.error(f"Failed to send research results: {e}")
            await say(f"✅ Research completed, but failed to send full results: {str(e)}")

    def _get_architect_help_message(self) -> str:
        """Get help message for architect commands"""
        return """🏗️ **Architect Agent Commands:**

**Deep Research:**
• `ask architect <your question>` - Comprehensive multi-tool research
• `ask architect <question> --type=data_analysis` - Focus on data analysis
• `ask architect <question> --type=code_review` - Focus on code analysis
• `ask architect <question> --type=documentation` - Focus on docs
• `ask architect <question> --no-viz` - Skip visualizations

**Quick Queries:**
• `quick data <question>` - Quick data analysis with charts
• `quick docs <question>` - Quick documentation search
• `quick pr <github_url>` - Quick PR analysis

**Examples:**
• `ask architect How is the io.net network performing this month?`
• `quick data How many devices earned block rewards today?`
• `quick docs How to set up staking?`
• `quick pr https://github.com/owner/repo/pull/123`

The Architect Agent combines coding tools, data analysis, and documentation search to provide comprehensive insights about io.net."""
        
    async def start(self):
        """Start the Slack bot"""
        logger.info("Starting Slack bot...")
        
        handler = AsyncSocketModeHandler(self.app, settings.slack_app_token)
        # sql_handler = AsyncSocketModeHandler(self.sql_app, settings.slack_sql_app_token)
        # await asyncio.gather(
        #     handler.start_async(),
        #     sql_handler.start_async()
        # )
        await handler.start_async()