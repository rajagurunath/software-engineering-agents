"""
Centralized Slack utility functions for consistent messaging across different bot agents.
"""
import os
import tempfile
import logging
import plotly.io as pio
import plotly.graph_objects as go
from typing import Dict, Any, List
from slack_sdk import WebClient

logger = logging.getLogger(__name__)

def save_plotly_image_from_json(plotly_json: str) -> str:
    """Save Plotly chart as image and return file path"""
    fig = pio.from_json(plotly_json)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        fig.write_image(tmpfile.name)
        return tmpfile.name

async def send_review_results(say, result):
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

async def send_creation_results(say, result):
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

async def send_comment_handling_results(say, result):
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

async def send_architect_results(say, result, client: WebClient, channel: str, thread_ts: str) -> None:
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
                        await client.files_upload_v2(
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
                await client.files_upload_v2(
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

def create_say_function(client: WebClient, channel: str, thread_ts: str):
    """Create a say function for architect results"""
    async def say(text=None, blocks=None):
        await client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks,
            thread_ts=thread_ts
        )
    return say

def get_architect_help_message() -> str:
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