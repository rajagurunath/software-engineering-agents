from core.integrations.github_client import GitHubClient
from core.integrations.sentry_client import SentryTool
import re
import logging
from config.settings import settings
from core.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)

class SentryDebugger:
    """
    A class to handle Sentry issue debugging and retrieval.
    """
    def __init__(self):
        self.sentry_tool = SentryTool(auth_token=settings.sentry_auth_token)
        self.llm_client = LLMClient()

    async def handle_sentry_issue(self, message, say, context, client):
        """
        Gets all Sentry issue URLs from all messages in a Slack conversation thread,
        analyzes each, and posts a summary for each unique issue.
        """
        try:
            # This command must be used in a thread
            if 'thread_ts' not in message:
                await say("This command only works in a thread. Please use it as a reply to a Sentry alert.")
                return

            thread_ts = message['thread_ts']
            channel_id = message['channel']

            # Fetch the entire thread history
            history = await client.conversations_replies(
                channel=channel_id,
                ts=thread_ts,
                inclusive=True,
                limit=1000  # Slack's max limit per call
            )

            if not history['messages']:
                await say("Could not retrieve messages in this thread.")
                return

            # Collect all Sentry URLs from all messages in the thread
            sentry_url_pattern = r'(https://[a-zA-Z0-9.-]+\.sentry\.io/issues/\d+)'
            sentry_urls = set()
            for msg in history['messages']:
                text = msg.get('text', '')
                matches = re.findall(sentry_url_pattern, text)
                sentry_urls.update(matches)

            if not sentry_urls:
                await say("I couldn't find any Sentry issue URLs in this thread.")
                return

            for sentry_url in sentry_urls:
                await say(f"Found Sentry link: {sentry_url}\n🔍 Analyzing the issue, please wait...", thread_ts=thread_ts)

                # 1. Use the SentryTool to get the analysis data
                sentry_issue_data = self.sentry_tool.get_issue_analysis_for_llm(sentry_url)

                if sentry_issue_data.startswith("Error:"):
                    await say(f"❌ Failed to analyze Sentry issue: {sentry_issue_data}", thread_ts=thread_ts)
                    continue

                # 2. Get the LLM prompt template
                llm_prompt_template = """
You are an expert Senior Software Engineer and a master at debugging production issues. Your task is to analyze the following Sentry issue report, which was automatically fetched by a tool.

Your goal is to provide a clear, concise, and actionable summary for the development team.

Please structure your response in three distinct sections:

1. **Summary:** Start with a high-level overview. What is the error, where is it happening, and what is the immediate impact?
2. **Detailed Analysis:** Dive deeper into the root cause. Use the stack trace and tags to explain the sequence of events that led to the error. If the stack trace points to a specific function or library, explain its role and why it might be failing.
3. **Recommended Actions:** Provide a numbered, prioritized list of concrete steps the team should take to investigate and resolve the issue. For each action, briefly explain *why* it's important.

Here is the Sentry issue data:

---

{sentry_data}
"""
                # 3. Combine the prompt template with the Sentry data
                final_prompt = llm_prompt_template.format(sentry_data=sentry_issue_data)

                # 4. Call the LLM to get the summary
                summary = await self.llm_client.generate_text("You are a Senior Software Engineer and a master at debugging production issues.", final_prompt)

                # 5. Post the final summary to the thread
                await say(text=summary, thread_ts=thread_ts)

        except Exception as e:
            logger.error(f"Error in handle_sentry_issue: {e}", exc_info=True)
            await say(f"❌ An unexpected error occurred: {str(e)}")
