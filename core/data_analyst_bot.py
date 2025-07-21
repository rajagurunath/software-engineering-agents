"""
Data Analyst Bot Handler - Dedicated Slack bot for the Data Analyst Agent
"""
import logging
import os
from typing import Dict, Any, Optional
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from services.architect.service import ArchitectService
from utils.slack_response_helpers import save_plotly_image_from_json
from config.settings import settings
from utils.opik_tracer import trace

logger = logging.getLogger(__name__)

class DataAnalystBotHandler:
    """Dedicated Slack bot handler for the Data Analyst Agent"""
    
    def __init__(self):
        self.app = AsyncApp(
            token=settings.slack_data_analyst_bot_token,
            signing_secret=settings.slack_data_analyst_signing_secret
        )
        self.architect_service = ArchitectService()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all Data Analyst-specific Slack event handlers"""
        
        @self.app.message("analyze data")
        async def handle_data_analysis(message, say, context):
            """Handle data analysis requests"""
            trace("slack.data_analysis_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                channel = message['channel']
                
                # Extract query (remove command prefix)
                query = text.replace('analyze data', '').strip()
                if not query:
                    await say("Please provide a data analysis query. Example: `analyze data How many devices are online?`")
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
                    await say(f"❌ Data analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Data analysis failed: {e}")
                await say(f"❌ Data analysis failed: {str(e)}")

        @self.app.message("sql query")
        async def handle_sql_query(message, say, context):
            """Handle SQL query requests"""
            trace("slack.sql_query_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                channel = message['channel']
                
                # Extract query (remove command prefix)
                query = text.replace('sql query', '').strip()
                if not query:
                    await say("Please provide a SQL query request. Example: `sql query Show me device uptime statistics`")
                    return
                
                await say(f"🔍 Generating SQL query for: *{query}*")
                
                # Use architect service for data analysis
                result = await self.architect_service.quick_data_analysis(query, user_id)
                
                if result["success"]:
                    response = f"**SQL Query Result:**\n{result['answer']}"
                    await say(response)
                    
                    # Handle Plotly visualization
                    if result.get("plotly_json"):
                        image_path = save_plotly_image_from_json(result["plotly_json"])
                        try:
                            await self.app.client.files_upload_v2(
                                channel=channel,
                                thread_ts=thread_ts,
                                file=image_path,
                                title="SQL Query Visualization"
                            )
                        finally:
                            os.remove(image_path)
                else:
                    await say(f"❌ SQL query failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"SQL query failed: {e}")
                await say(f"❌ SQL query failed: {str(e)}")

        @self.app.message("generate report")
        async def handle_report_generation(message, say, context):
            """Handle report generation requests"""
            trace("slack.report_generation_request", {
                "user_id": message['user'],
                "text": message['text'][:200]
            })
            try:
                text = message['text']
                user_id = message['user']
                thread_ts = message.get('thread_ts', message['ts'])
                channel = message['channel']
                
                # Extract query (remove command prefix)
                query = text.replace('generate report', '').strip()
                if not query:
                    await say("Please provide a report topic. Example: `generate report Network performance summary for this week`")
                    return
                
                await say(f"📋 Generating report for: *{query}*")
                
                # Use architect service for comprehensive research
                result = await self.architect_service.conduct_research(
                    query=query,
                    user_id=user_id,
                    research_type=None,
                    thread_id=thread_ts,
                    channel_id=channel,
                    include_visualizations=True,
                    num_charts=3
                )
                
                # Send executive summary as report
                summary_blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"## 📋 Report Generated\n\n"
                                   f"**Topic**: {result.original_query}\n"
                                   f"**Generated**: {result.completed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                                   f"**Analysis Duration**: {result.total_duration_seconds:.1f}s"
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
                
                # Upload visualizations
                for viz in result.data_visualizations:
                    if viz.get("plotly_json"):
                        image_path = save_plotly_image_from_json(viz["plotly_json"])
                        try:
                            await self.app.client.files_upload_v2(
                                channel=channel,
                                thread_ts=thread_ts,
                                file=image_path,
                                title=viz.get("title", "Report Visualization")
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
                            title=f"Detailed Report - {result.original_query[:30]}",
                            filetype="html"
                        )
                    except Exception as e:
                        logger.error(f"Failed to upload HTML report: {e}")
                
                trace("slack.report_generation_complete", {
                    "research_id": result.research_id,
                    "visualizations_count": len(result.data_visualizations)
                })
                
            except Exception as e:
                logger.error(f"Report generation failed: {e}")
                await say(f"❌ Report generation failed: {str(e)}")

        @self.app.event("assistant_thread_started")
        async def handle_assistant_thread_started_events(body, logger, say):
            logger.info(body)
            user_id = body['event']['assistant_thread']['user_id']
            await say(f"Hello <@{user_id}>, I am your Data Analyst! I can help you analyze data, generate SQL queries, and create reports. How can I assist you today?")

    async def start(self):
        """Start the Data Analyst Slack bot"""
        logger.info("Starting Data Analyst Slack bot...")
        
        handler = AsyncSocketModeHandler(self.app, settings.slack_data_analyst_app_token)
        await handler.start_async()