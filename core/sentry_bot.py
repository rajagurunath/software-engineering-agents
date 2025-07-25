"""
Sentry Bot Handler - Dedicated Slack bot for the Sentry Agent
"""
import logging
from typing import Dict, Any, Optional
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from services.developer.sentry_debugger import SentryDebugger
from config.settings import settings
from utils.opik_tracer import trace

logger = logging.getLogger(__name__)

class SentryBotHandler:
    """Dedicated Slack bot handler for the Sentry Agent"""
    
    def __init__(self):
        self.app = AsyncApp(
            token=settings.slack_sentry_bot_token,
            signing_secret=settings.slack_sentry_signing_secret
        )
        self.sentry_debugger = SentryDebugger()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all Sentry-specific Slack event handlers"""
        
        @self.app.message("handle sentry")
        async def handle_sentry_issue(message, say, context):
            """Handle Sentry issue debugging requests"""
            trace("slack.sentry_issue_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                await self.sentry_debugger.handle_sentry_issue(
                    message, say, context, self.app.client
                )
                
                trace("slack.sentry_issue_complete", {
                    "user_id": message['user']
                })
                
            except Exception as e:
                logger.error(f"Error in Sentry issue handling: {e}")
                trace("slack.sentry_issue_error", {"error": str(e)})
                await say(f"❌ Error handling Sentry issue: {str(e)}")
        
        @self.app.event("app_mention")
        async def handle_app_mention(event, say):
            """Handles mentions of the bot"""
            user_id = event.get("user")
            text = event.get("text")
            
            trace("slack.app_mention", {
                "user_id": user_id,
                "text": text[:200] if text else ""
            })
            
            # Acknowledge the mention and offer help
            await say(
                f"Hi <@{user_id}>! I'm the Sentry Bot. How can I help you today? "
                "You can ask me to:\n"
                "• `handle sentry` in a thread with a Sentry alert.\n"
                "• `debug error <error description or Sentry URL>`.\n"
                "• `analyze logs <log content>`."
            )

        @self.app.message("debug error")
        async def handle_error_debugging(message, say, context):
            """Handle general error debugging requests"""
            trace("slack.error_debugging_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                channel = message['channel']
                
                # Extract error description (remove command prefix)
                error_description = text.replace('debug error', '').strip()
                if not error_description:
                    await say("Please provide an error description or Sentry URL. Example: `debug error https://sentry.io/organizations/org/issues/123456/`")
                    return
                
                await say(f"🔍 Analyzing error: *{error_description[:100]}...*")
                
                # Check if it's a Sentry URL
                if 'sentry.io' in error_description:
                    # Handle as Sentry issue
                    await self.sentry_debugger.handle_sentry_issue(
                        message, say, context, self.app.client
                    )
                else:
                    # Handle as general error description
                    await say("For detailed error analysis, please provide a Sentry issue URL. I can also help with general debugging if you use the `handle sentry` command in a thread with Sentry alerts.")
                
            except Exception as e:
                logger.error(f"Error debugging failed: {e}")
                await say(f"❌ Error debugging failed: {str(e)}")

        @self.app.message("analyze logs")
        async def handle_log_analysis(message, say, context):
            """Handle log analysis requests"""
            trace("slack.log_analysis_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                
                # Extract log content or request (remove command prefix)
                log_content = text.replace('analyze logs', '').strip()
                if not log_content:
                    await say("""
🔍 **Log Analysis Commands:**

• `analyze logs <log content>` - Analyze provided log content
• `handle sentry` - Analyze Sentry issues in thread
• `debug error <error description>` - General error debugging

**Example:**
```
analyze logs
ERROR: Connection timeout after 30s
at database.connect(db.py:45)
```

For Sentry issues, use `handle sentry` in the alert thread.
                    """)
                    return
                
                await say(f"📋 Analyzing logs...")
                
                # Simple log analysis (could be enhanced with LLM)
                analysis = self._analyze_log_content(log_content)
                
                await say(f"**Log Analysis Result:**\n{analysis}")
                
            except Exception as e:
                logger.error(f"Log analysis failed: {e}")
                await say(f"❌ Log analysis failed: {str(e)}")
                


        @self.app.event("assistant_thread_started")
        async def handle_assistant_thread_started_events(body, logger, say):
            logger.info(body)
            user_id = body['event']['assistant_thread']['user_id']
            await say(f"Hello <@{user_id}>, I am your Sentry Agent! I can help you debug errors, analyze Sentry issues, and examine logs. How can I assist you today?")

    def _analyze_log_content(self, log_content: str) -> str:
        """Analyze log content and provide insights"""
        lines = log_content.split('\n')
        
        # Simple analysis
        error_count = sum(1 for line in lines if 'ERROR' in line.upper())
        warning_count = sum(1 for line in lines if 'WARNING' in line.upper() or 'WARN' in line.upper())
        
        analysis = f"**Log Summary:**\n"
        analysis += f"• Total lines: {len(lines)}\n"
        analysis += f"• Errors found: {error_count}\n"
        analysis += f"• Warnings found: {warning_count}\n\n"
        
        if error_count > 0:
            analysis += "**Error Lines:**\n"
            error_lines = [line for line in lines if 'ERROR' in line.upper()]
            for error_line in error_lines[:3]:  # Show first 3 errors
                analysis += f"• {error_line.strip()}\n"
            if len(error_lines) > 3:
                analysis += f"• ... and {len(error_lines) - 3} more errors\n"
        
        if warning_count > 0:
            analysis += "\n**Warning Lines:**\n"
            warning_lines = [line for line in lines if 'WARNING' in line.upper() or 'WARN' in line.upper()]
            for warning_line in warning_lines[:2]:  # Show first 2 warnings
                analysis += f"• {warning_line.strip()}\n"
            if len(warning_lines) > 2:
                analysis += f"• ... and {len(warning_lines) - 2} more warnings\n"
        
        if error_count == 0 and warning_count == 0:
            analysis += "**Status:** No obvious errors or warnings detected in the logs."
        
        return analysis

    async def start(self):
        """Start the Sentry Slack bot"""
        logger.info("Starting Sentry Slack bot...")
        
        handler = AsyncSocketModeHandler(self.app, settings.slack_sentry_app_token)
        await handler.start_async()
