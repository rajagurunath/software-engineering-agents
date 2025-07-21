"""
Architect Bot Handler - Dedicated Slack bot for the Software Architect Agent
"""
import logging
import re
import asyncio
from typing import Dict, Any, Optional
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from services.architect.service import ArchitectService
from services.architect.models import ResearchType
from utils.slack_response_helpers import (
    send_architect_results, 
    save_plotly_image_from_json,
    get_architect_help_message,
    create_say_function
)
from config.settings import settings
from utils.opik_tracer import trace
import plotly.io as pio
import tempfile
import os

logger = logging.getLogger(__name__)

class ArchitectBotHandler:
    """Dedicated Slack bot handler for the Software Architect Agent"""
    
    def __init__(self):
        self.app = AsyncApp(
            token=settings.slack_architect_bot_token,
            signing_secret=settings.slack_architect_signing_secret
        )
        self.architect_service = ArchitectService()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all Architect-specific Slack event handlers"""
        
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
                    await say(get_architect_help_message())
                    return
                
                # Send initial response
                await say(f"🏗️ Starting deep research on: *{research_params['query']}*\n"
                         f"Research type: {research_params.get('type', 'auto-detected')}\n"
                         f"Generating up to {research_params.get('num_charts', 5)} charts.\n"
                         f"This may take a few minutes...")
                
                # Conduct research
                result = await self.architect_service.conduct_research(
                    query=research_params['query'],
                    user_id=user_id,
                    research_type=research_params.get('type'),
                    thread_id=thread_ts,
                    channel_id=channel,
                    include_visualizations=research_params.get('num_charts', 5) > 0,
                    num_charts=research_params.get('num_charts', 5),
                    user_id_context=research_params.get('user_id_context'),
                    device_id_context=research_params.get('device_id_context')
                )
                
                # Send results to Slack
                await send_architect_results(say, result, self.app.client, channel, thread_ts)
                
                trace("slack.architect_complete", {
                    "research_id": result.research_id,
                    "findings_count": len(result.detailed_findings)
                })
                
            except Exception as e:
                logger.error(f"Architect request failed: {e}")
                trace("slack.architect_error", {"error": str(e)})
                await say(f"❌ Research failed: {str(e)}")

        @self.app.message("data-analyst")
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
                query = text.replace('data-analyst', '').strip()
                if not query:
                    await say("Please provide a data query. Example: `data-analyst How many devices are online?`")
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

        @self.app.message("engineer docs")
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
                query = text.replace('engineer docs', '').strip()
                if not query:
                    await say("Please provide a documentation query. Example: `engineer docs How to stake IO tokens?`")
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

        @self.app.event("assistant_thread_started")
        async def handle_assistant_thread_started_events(body, logger, say):
            logger.info(body)
            user_id = body['event']['assistant_thread']['user_id']
            await say(f"Hello <@{user_id}>, I am your Software Architect! I can help you with deep research, data analysis, and documentation searches. How can I assist you today?")

    def _parse_architect_command(self, text: str) -> Dict[str, str]:
        """Parse architect command from Slack message"""
        text = text.strip()
        
        if not text.startswith('ask architect'):
            return None
        
        query_text = text[12:].strip()
        
        if not query_text:
            return None
        
        params = {
            'query': query_text,
            'type': None,
            'num_charts': 5,  # Default
            'user_id_context': None,
            'device_id_context': None,
        }

        # Extract UUID and determine if it's a user_id or device_id
        uuid_match = re.search(r'(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', query_text, re.IGNORECASE)
        if uuid_match:
            uuid_str = uuid_match.group('id')
            # Check for keywords before the UUID to determine context
            context_window = query_text[:uuid_match.start()]
            if 'device' in context_window.lower():
                params['device_id_context'] = uuid_str
            else: # Default to user_id if no specific context is found
                params['user_id_context'] = uuid_str

        # Handle chart count first, as it's more specific
        charts_match = re.search(r'--(?:no-)?charts[=\s](?P<num>\d+)', query_text)
        if charts_match:
            params['num_charts'] = int(charts_match.group('num'))
            query_text = query_text.replace(charts_match.group(0), '').strip()
        elif '--no-charts' in query_text or '--no-viz' in query_text:
            params['num_charts'] = 0
            query_text = query_text.replace('--no-charts', '').replace('--no-viz', '').strip()

        # Handle research type
        if '--type=' in query_text:
            parts = query_text.split('--type=')
            query_text = parts[0].strip()
            type_part = parts[1].split()[0]
            
            try:
                params['type'] = ResearchType(type_part)
            except ValueError:
                pass  # Invalid type, will auto-detect
        
        params['query'] = query_text.strip()
        
        return params

    async def start(self):
        """Start the Architect Slack bot"""
        logger.info("Starting Architect Slack bot...")
        
        handler = AsyncSocketModeHandler(self.app, settings.slack_architect_app_token)
        await handler.start_async()