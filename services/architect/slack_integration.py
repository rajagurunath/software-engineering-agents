"""
Slack integration for the Architect Agent
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import json
import tempfile
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .service import ArchitectService
from .models import ResearchType
from config.settings import settings
from utils.opik_tracer import trace

logger = logging.getLogger(__name__)

class ArchitectSlackHandler:
    """
    Handles Slack interactions for the Architect Agent
    """
    
    def __init__(self):
        self.architect_service = ArchitectService()
        self.slack_client = WebClient(token=settings.slack_bot_token)
    
    async def handle_research_request(self, message: Dict[str, Any], say) -> None:
        """Handle research requests from Slack"""
        try:
            text = message['text']
            user_id = message['user']
            thread_ts = message.get('thread_ts', message['ts'])
            channel = message['channel']
            
            # Parse research command
            research_params = self._parse_research_command(text)
            if not research_params:
                await say(self._get_help_message())
                return
            
            # Send initial response
            await say(f"🏗️ Starting deep research on: *{research_params['query']}*\n"
                     f"Research type: {research_params.get('type', 'auto-detected')}\n"
                     f"This may take a few minutes...")
            
            trace("architect_slack.research_start", {
                "user_id": user_id,
                "query": research_params['query']
            })
            
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
            await self._send_research_results(say, result, channel, thread_ts)
            
            trace("architect_slack.research_complete", {
                "research_id": result.research_id,
                "findings_count": len(result.detailed_findings)
            })
            
        except Exception as e:
            logger.error(f"Research request failed: {e}")
            await say(f"❌ Research failed: {str(e)}")
            trace("architect_slack.research_error", {"error": str(e)})

    async def handle_quick_data_query(self, message: Dict[str, Any], say) -> None:
        """Handle quick data queries"""
        try:
            text = message['text']
            user_id = message['user']
            
            # Extract query (remove command prefix)
            query = text.replace('data query', '').strip()
            if not query:
                await say("Please provide a data query. Example: `data query How many devices are online?`")
                return
            
            await say(f"📊 Analyzing data for: *{query}*")
            
            result = await self.architect_service.quick_data_analysis(query, user_id)
            
            if result["success"]:
                response = f"**Data Analysis Result:**\n{result['answer']}"
                
                # Handle Plotly visualization
                if result.get("plotly_json"):
                    # Save plot as image and upload
                    image_path = await self._save_plotly_as_image(result["plotly_json"])
                    if image_path:
                        try:
                            await self.slack_client.files_upload_v2(
                                channel=message['channel'],
                                thread_ts=message.get('thread_ts', message['ts']),
                                file=image_path,
                                title="Data Visualization"
                            )
                        finally:
                            os.remove(image_path)
                
                await say(response)
            else:
                await say(f"❌ Data query failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Quick data query failed: {e}")
            await say(f"❌ Data query failed: {str(e)}")

    async def handle_quick_docs_search(self, message: Dict[str, Any], say) -> None:
        """Handle quick documentation searches"""
        try:
            text = message['text']
            user_id = message['user']
            
            # Extract query (remove command prefix)
            query = text.replace('docs search', '').strip()
            if not query:
                await say("Please provide a documentation query. Example: `docs search How to stake IO tokens?`")
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

    async def handle_pr_analysis(self, message: Dict[str, Any], say) -> None:
        """Handle PR analysis requests"""
        try:
            text = message['text']
            user_id = message['user']
            
            # Extract PR URL
            pr_url = self._extract_pr_url(text)
            if not pr_url:
                await say("Please provide a valid GitHub PR URL. Example: `analyze pr https://github.com/owner/repo/pull/123`")
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

    def _parse_research_command(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse research command from Slack message"""
        text = text.strip()
        
        # Check for research command
        if not text.startswith('research'):
            return None
        
        # Remove 'research' prefix
        query_text = text[8:].strip()
        
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

    def _extract_pr_url(self, text: str) -> Optional[str]:
        """Extract GitHub PR URL from text"""
        import re
        pr_pattern = r'https://github\.com/[\w-]+/[\w-]+/pull/\d+'
        match = re.search(pr_pattern, text)
        return match.group(0) if match else None

    async def _send_research_results(self, say, result, channel: str, thread_ts: str) -> None:
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
                    image_path = await self._save_plotly_as_image(viz["plotly_json"])
                    if image_path:
                        try:
                            await self.slack_client.files_upload_v2(
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
                    await self.slack_client.files_upload_v2(
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

    async def _save_plotly_as_image(self, plotly_json: str) -> Optional[str]:
        """Save Plotly chart as image file"""
        try:
            import plotly.io as pio
            import plotly.graph_objects as go
            
            fig = pio.from_json(plotly_json)
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                fig.write_image(tmpfile.name, width=800, height=600)
                return tmpfile.name
                
        except Exception as e:
            logger.error(f"Failed to save Plotly image: {e}")
            return None

    def _get_help_message(self) -> str:
        """Get help message for Slack users"""
        return """🏗️ **Architect Agent Commands:**

**Deep Research:**
• `research <your question>` - Comprehensive multi-tool research
• `research <question> --type=data_analysis` - Focus on data analysis
• `research <question> --type=code_review` - Focus on code analysis
• `research <question> --type=documentation` - Focus on docs
• `research <question> --no-viz` - Skip visualizations

**Quick Queries:**
• `data query <question>` - Quick data analysis with charts
• `docs search <question>` - Quick documentation search
• `analyze pr <github_url>` - Quick PR analysis

**Examples:**
• `research How is the io.net network performing this month?`
• `data query How many devices earned block rewards today?`
• `docs search How to set up staking?`
• `analyze pr https://github.com/owner/repo/pull/123`

The Architect Agent combines coding tools, data analysis, and documentation search to provide comprehensive insights about io.net."""

# Integration function for the main Slack bot
def register_architect_handlers(app):
    """Register Architect Agent handlers with the main Slack app"""
    handler = ArchitectSlackHandler()
    
    @app.message("research")
    async def handle_research(message, say, context):
        await handler.handle_research_request(message, say)
    
    @app.message("data query")
    async def handle_data_query(message, say, context):
        await handler.handle_quick_data_query(message, say)
    
    @app.message("docs search")
    async def handle_docs_search(message, say, context):
        await handler.handle_quick_docs_search(message, say)
    
    @app.message("analyze pr")
    async def handle_pr_analysis(message, say, context):
        await handler.handle_pr_analysis(message, say)
    
    @app.message("architect help")
    async def handle_help(message, say, context):
        await say(handler._get_help_message())