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
import json
from rag.multimedia_rag.audio_transcriper import process_slack_audio_event
from rag.multimedia_rag.video_rag import process_slack_video_event, process_video_with_rag
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
                    response += f"Executed SQL: `{result.get('query', 'N/A')}`"
                    response += f"\n\n*Follow-up Questions:* {', '.join(result.get('followup_questions', []))}" if result.get('followup_questions') else ""
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
                await say("How can I help you? You can ask me to research a topic or `summarize` a thread.", thread_ts=thread_ts)
                return
            
            await say(f"🏗️ Starting deep research on: *{query_text}*", thread_ts=thread_ts)
            try:
                result = await self.architect_service.conduct_research(
                    query=query_text,
                    user_id=user_id,
                    thread_id=thread_ts,
                    channel_id=channel,
                    include_visualizations=True,
                    num_charts=5
                )
                await send_architect_results(say, result, self.app.client, channel, thread_ts)
            except Exception as e:
                logger.error(f"Mention request for research failed: {e}", exc_info=True)
                await say(f"❌ Research failed: {str(e)}", thread_ts=thread_ts)

        @self.app.event("message")
        async def handle_message_events(body, logger, say, client: WebClient):
            event = body.get('event', {})
            files = event.get('files', [])
            if event.get('subtype') == 'file_share' and files:
                for f in files:
                    mimetype = f.get('mimetype', '')
                    
                    # Handle audio files
                    if mimetype.startswith('audio/') or mimetype in ['audio/mp4', 'audio/mpeg', 'audio/x-m4a']:
                        user = event.get('user')
                        ts = event.get('ts')
                        channel = event.get('channel')
                        
                        transcript = None
                        try:
                            transcript = process_slack_audio_event(body)

                            if transcript:
                                await self.app.client.chat_postMessage(channel=channel, text=f"📝 Transcript: {transcript}", thread_ts=ts)
                                
                                # Pass transcript to architect agent for analysis
                                try:
                                    result = await self.architect_service.conduct_research(
                                        query=transcript,
                                        user_id=user,
                                        research_type=None,
                                        thread_id=ts,
                                        channel_id=channel,
                                        include_visualizations=True
                                    )
                                    await self._send_architect_results(say, result, channel, ts)
                                except Exception as e:
                                    logger.error(f"Architect request from audio transcript failed: {e}")
                                    await self.app.client.chat_postMessage(channel=channel, text=f"❌ Architect agent failed: {str(e)}", thread_ts=ts)
                            else:
                                await self.app.client.chat_postMessage(channel=channel, text=f"❌ Audio transcription failed.", thread_ts=ts)
                        except Exception as e:
                            logger.error(f"Audio processing error: {e}")
                    
                    # Handle video files
                    elif mimetype.startswith('video/'):
                        user = event.get('user')
                        ts = event.get('ts')
                        channel = event.get('channel')
                        
                        try:
                            await self.app.client.chat_postMessage(
                                channel=channel, 
                                text=f"🎥 Video detected! Processing... This may take a moment.", 
                                thread_ts=ts
                            )
                            
                            # Download and prepare video
                            video_info = process_slack_video_event(body)
                            
                            if video_info and video_info.get('success'):
                                # Process video with RAG
                                video_result = await process_video_with_rag(video_info)
                                
                                if video_result and video_result.get('success'):
                                    # Post video understanding first
                                    understanding_text = f"🎥 **Video Understanding:**\n{video_result['video_understanding']}"
                                    if video_result.get('audio_transcript'):
                                        understanding_text += f"\n\n📝 **Audio Transcript:**\n{video_result['audio_transcript']}"
                                    
                                    await self.app.client.chat_postMessage(
                                        channel=channel, 
                                        text=understanding_text, 
                                        thread_ts=ts
                                    )
                                    
                                    # Pass combined analysis to architect agent
                                    combined_query = video_result['combined_analysis']
                                    if combined_query:
                                        await self._process_architect_request_from_media(combined_query, user, channel, ts)
                                else:
                                    await self.app.client.chat_postMessage(
                                        channel=channel, 
                                        text=f"❌ Video processing failed.", 
                                        thread_ts=ts
                                    )
                            else:
                                await self.app.client.chat_postMessage(
                                    channel=channel, 
                                    text=f"❌ Could not process video file.", 
                                    thread_ts=ts
                                )
                                
                        except Exception as e:
                            logger.error(f"Video processing error: {e}")
                            await self.app.client.chat_postMessage(
                                channel=channel, 
                                text=f"❌ Video processing error: {str(e)}", 
                                thread_ts=ts
                            )
        
        

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
