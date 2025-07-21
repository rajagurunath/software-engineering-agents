"""
Main Dispatcher Bot - Optional central bot that can direct users to specialized agents
"""
import logging
from typing import Dict, Any, Optional
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config.settings import settings
from utils.opik_tracer import trace
from rag.multimedia_rag.audio_transcriper import process_slack_audio_event
from rag.multimedia_rag.video_rag import process_slack_video_event, process_video_with_rag

logger = logging.getLogger(__name__)

class MainDispatcherBotHandler:
    """Main dispatcher bot that can direct users to specialized agents"""
    
    def __init__(self):
        self.app = AsyncApp(
            token=settings.slack_bot_token,
            signing_secret=settings.slack_signing_secret
        )
        self._register_handlers()
    
    def _register_handlers(self):
        """Register general event handlers and dispatcher logic"""
        
        @self.app.message("help")
        async def handle_help_request(message, say, context):
            """Provide help and direct users to specialized agents"""
            await say(self._get_help_message())

        @self.app.message("agents")
        async def handle_agents_list(message, say, context):
            """List available specialized agents"""
            await say(self._get_agents_list())

        @self.app.event("message")
        async def handle_message_events(body, logger, say):
            """Handle file uploads and multimedia content"""
            logger.info(body)
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
                                await self.app.client.chat_postMessage(
                                    channel=channel, 
                                    text=f"📝 Transcript: {transcript}\n\n💡 *Tip: You can ask the **Architect Agent** to analyze this transcript by mentioning `ask architect` followed by your question.*", 
                                    thread_ts=ts
                                )
                            else:
                                await self.app.client.chat_postMessage(
                                    channel=channel, 
                                    text=f"❌ Audio transcription failed.", 
                                    thread_ts=ts
                                )
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
                                    
                                    understanding_text += f"\n\n💡 *Tip: You can ask the **Architect Agent** to analyze this content by mentioning `ask architect` followed by your question.*"
                                    
                                    await self.app.client.chat_postMessage(
                                        channel=channel, 
                                        text=understanding_text, 
                                        thread_ts=ts
                                    )
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
            await say(f"Hello <@{user_id}>, I am the Main Dispatcher! I can help you find the right specialized agent for your needs. Type `help` to see available agents and commands.")

    def _get_help_message(self) -> str:
        """Get comprehensive help message"""
        return """🤖 **Agent Team Help**

**Available Specialized Agents:**

🏗️ **Architect Agent** - Deep research, data analysis, documentation
• `ask architect <question>` - Comprehensive research
• `data-analyst <question>` - Quick data analysis  
• `engineer docs <question>` - Documentation search

👨‍💻 **Developer Agent** - Code reviews, PR management
• `review pr <github_url>` - Review pull requests
• `create pr` - Create new pull requests
• `handle comments <pr_url>` - Address PR feedback

📊 **Data Analyst Agent** - Data analysis and reporting
• `analyze data <question>` - Analyze network data
• `sql query <request>` - Generate SQL queries
• `generate report <topic>` - Create comprehensive reports

🚨 **Sentry Agent** - Error debugging and monitoring
• `handle sentry` - Debug Sentry issues (use in alert threads)
• `debug error <description>` - General error debugging
• `analyze logs <content>` - Analyze log files

**General Commands:**
• `help` - Show this help message
• `agents` - List all available agents

**File Support:**
• Upload audio/video files for automatic transcription and analysis
• Supported formats: MP3, MP4, WAV, MOV, etc.

Each agent is specialized for specific tasks. Choose the right agent for your needs!"""

    def _get_agents_list(self) -> str:
        """Get list of available agents"""
        return """🤖 **Available Specialized Agents:**

🏗️ **Architect Agent** (`@architect-bot`)
- Deep research and analysis
- Data visualization and insights
- Documentation search and synthesis
- Multi-tool orchestration

👨‍💻 **Developer Agent** (`@developer-bot`)  
- Pull request reviews and creation
- Code quality analysis
- PR comment handling and resolution
- GitHub integration

📊 **Data Analyst Agent** (`@data-analyst-bot`)
- Network data analysis
- SQL query generation and execution
- Report generation with visualizations
- Performance metrics and insights

🚨 **Sentry Agent** (`@sentry-bot`)
- Error debugging and analysis
- Sentry issue investigation
- Log analysis and troubleshooting
- Production issue resolution

**How to Use:**
1. Mention the specific agent in your message
2. Use the agent's specialized commands
3. Each agent has its own expertise and capabilities

Type `help` for detailed command information for each agent."""

    async def start(self):
        """Start the Main Dispatcher Slack bot"""
        logger.info("Starting Main Dispatcher Slack bot...")
        
        handler = AsyncSocketModeHandler(self.app, settings.slack_app_token)
        await handler.start_async()