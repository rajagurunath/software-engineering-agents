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
from services.architect.service import ArchitectService
from config.settings import settings
from utils.opik_tracer import trace
import re
import json
import tempfile
import os
logger = logging.getLogger(__name__)

class SentryBotHandler:
    """Dedicated Slack bot handler for the Sentry Agent"""
    
    def __init__(self):
        self.app = AsyncApp(
            token=settings.slack_sentry_bot_token,
            signing_secret=settings.slack_sentry_signing_secret
        )
        self.sentry_debugger = SentryDebugger()
        self.architect_service = ArchitectService()
        self._register_handlers()
    
    async def _get_thread_summary(self, client: WebClient, channel: str, thread_ts: str) -> (Optional[str], Optional[list]):
        """Fetches and summarizes a Slack thread, returning the summary text and messages."""
        all_messages = []
        cursor = None
        while True:
            history = await client.conversations_replies(
                channel=channel,
                ts=thread_ts,
                limit=200,
                cursor=cursor
            )
            messages = history.get('messages', [])
            all_messages.extend(messages)
            
            if not history.get('has_more'):
                break
            cursor = history.get('response_metadata', {}).get('next_cursor')

        user_names_cache = {}
        formatted_messages = []
        for msg in all_messages:
            msg_user_id = msg.get('user')
            msg_text = msg.get('text', '').strip()
            if not msg_user_id or not msg_text:
                continue
            
            if msg_user_id not in user_names_cache:
                user_names_cache[msg_user_id] = f"<@{msg_user_id}>"
                # try:
                #     user_info = await client.users_info(user=msg_user_id)
                #     user_names_cache[msg_user_id] = user_info['user']['profile']['real_name_normalized']
                # except SlackApiError:
                #     user_names_cache[msg_user_id] = f"<@{msg_user_id}>"
            
            user_name = user_names_cache[msg_user_id]
            formatted_messages.append(f"**{user_name}**: {msg_text}")

        if not formatted_messages:
            return "There doesn't seem to be any text content to summarize in this thread.", None
        
        thread_content = "\n".join(formatted_messages)
        summary_text = await self.architect_service.summarize_thread(thread_content)
        return summary_text, all_messages
    
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
                
        @self.app.event("app_mention")
        async def handle_mention(body, say, context, client: WebClient, logger):
            """Handle direct mentions of the bot for research or thread summarization."""
            event = body['event']
            text = event['text']
            user_id = event['user']
            thread_ts = event.get('thread_ts', event['ts'])
            channel = event['channel']

            bot_user_id = context.get("bot_user_id", "")
            query_text = re.sub(f"<@{bot_user_id}>", "", text).strip()
            if "handle sentry" in query_text.lower():
                return await handle_sentry_issue(event, say, context)
            # Check for summarization keywords
            if any(keyword in query_text.lower() for keyword in ['summary', 'summarise', 'summarize']):
                url_match = re.search(r"<https?://[\w.-]+\.slack\.com/archives/(\w+)/p(\d+)>", query_text)
                if url_match:
                    # URL summarization
                    summarize_channel_id = url_match.group(1)
                    ts_string = url_match.group(2)
                    summarize_thread_ts = f"{ts_string[:-6]}.{ts_string[-6:]}"
                    
                    await client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=f"Sure, I'll summarize the linked thread for you. One moment... 🧐")
                    try:
                        summary_text, messages = await self._get_thread_summary(client, summarize_channel_id, summarize_thread_ts)
                        if messages:
                            try:
                                messages_json = json.dumps(messages, indent=2)
                                with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as temp_file:
                                    temp_file.write(messages_json)
                                    temp_file_path = temp_file.name
                                
                                await client.files_upload_v2(
                                    channel=channel,
                                    thread_ts=thread_ts,
                                    file=temp_file_path,
                                    title="Thread Messages (JSON)",
                                    initial_comment="Here are the raw messages from the thread for debugging."
                                )
                                os.remove(temp_file_path)
                            except Exception as json_e:
                                logger.error(f"Failed to serialize and upload messages as JSON: {json_e}")
                        if summary_text:
                            await client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=summary_text)
                    except Exception as e:
                        logger.error(f"URL Thread summarization failed: {e}", exc_info=True)
                        await client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=f"❌ I ran into an issue trying to summarize the linked thread: {str(e)}")
                else:
                    # Current thread summarization
                    if 'thread_ts' not in event:
                        await say("I can only summarize conversations in a thread. Please mention me in a reply to the thread you want summarized.")
                        return
                    
                    await say(f"Sure, I'll summarize this thread for you. One moment... 🧐")
                    try:
                        summary_text, messages = await self._get_thread_summary(client, channel, thread_ts)
                        if summary_text:
                            await say(summary_text)
                        if messages:
                            try:
                                messages_json = json.dumps(messages, indent=2)
                                with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as temp_file:
                                    temp_file.write(messages_json)
                                    temp_file_path = temp_file.name
                                
                                await client.files_upload_v2(
                                    channel=channel,
                                    thread_ts=thread_ts,
                                    file=temp_file_path,
                                    title="Thread Messages (JSON)",
                                    initial_comment="Here are the raw messages from the thread for debugging."
                                )
                                os.remove(temp_file_path)
                            except Exception as json_e:
                                logger.error(f"Failed to serialize and upload messages as JSON: {json_e}")
                    except Exception as e:
                        logger.error(f"Thread summarization failed: {e}", exc_info=True)
                        await say(f"❌ I ran into an issue trying to summarize the thread: {str(e)}")
                return

            # --- Fallback to original research logic ---
            if not query_text:
                await say("How can I help you? You can ask me to debug a issue or `summarize` a thread.", thread_ts=thread_ts)
                return
            
            # await say(f"🏗️ Starting deep research on: *{query_text}*", thread_ts=thread_ts)
            # try:
            #     result = await self.architect_service.conduct_research(
            #         query=query_text,
            #         user_id=user_id,
            #         thread_id=thread_ts,
            #         channel_id=channel,
            #         include_visualizations=True,
            #         num_charts=5
            #     )
            #     await send_architect_results(say, result, self.app.client, channel, thread_ts)
            # except Exception as e:
            #     logger.error(f"Mention request for research failed: {e}", exc_info=True)
            #     await say(f"❌ Research failed: {str(e)}", thread_ts=thread_ts)

        @self.app.event("message")
        async def handle_message_events(body, logger):
            logger.info(body)

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
