import requests
import json
import re
from urllib.parse import urlparse
from config.settings import settings

class SentryTool:
    """
    A Python tool for interacting with the Sentry API, designed to fetch
    and format issue details for analysis by an LLM.
    """
    def __init__(self, auth_token: str, organization_slug: str = None, project_slug: str = None):
        """
        Initializes the SentryTool client.

        Args:
            auth_token (str): Your Sentry API authentication token.
            organization_slug (str, optional): The slug of your organization. 
                                               Required for listing project issues.
            project_slug (str, optional): The slug of your project. 
                                          Required for listing project issues.
        """
        if not auth_token:
            raise ValueError("Sentry auth_token must be provided.")
            
        self.auth_token = auth_token
        self.organization_slug = organization_slug
        self.project_slug = project_slug
        self.base_url = "https://sentry.io/api/0/"
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict | None:
        """Helper method to make requests to the Sentry API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.content.decode()}")
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
        return None

    @staticmethod
    def _extract_issue_id_from_url(sentry_url: str) -> str | None:
        """Extracts the issue ID from a Sentry issue URL."""
        try:
            path = urlparse(sentry_url).path
            match = re.search(r'/issues/(\d+)/?', path)
            if match:
                return match.group(1)
        except Exception as e:
            print(f"Could not parse URL: {e}")
        return None

    def get_issue_details(self, issue_id: str) -> dict | None:
        """Retrieves detailed information for a single issue by its ID."""
        print(f"Fetching details for issue: {issue_id}...")
        return self._make_request('GET', f"issues/{issue_id}/")

    def get_latest_event_for_issue(self, issue_id: str) -> dict | None:
        """Retrieves the latest event for a given issue, which contains the stack trace."""
        print(f"Fetching latest event for issue: {issue_id}...")
        return self._make_request('GET', f"issues/{issue_id}/events/latest/")

    @staticmethod
    def _extract_error_location(event_details: dict) -> dict | None:
        """Parses an event to find the most relevant error location from the stack trace."""
        if not event_details:
            return None
        
        stacktrace = None
        # Prioritize the 'exception' entry in the event
        for entry in event_details.get('entries', []):
            if entry.get('type') == 'exception':
                values = entry.get('data', {}).get('values', [])
                if values:
                    stacktrace = values[-1].get('stacktrace')
                    break
        
        # If no exception, look for other stacktrace sources
        if not stacktrace:
            stacktrace = event_details.get('stacktrace')

        if stacktrace and 'frames' in stacktrace:
            # Iterate in reverse to find the last (most recent) frame from the user's app
            for frame in reversed(stacktrace.get('frames', [])):
                if frame.get('in_app'):
                    return {
                        'filename': frame.get('filename'),
                        'function': frame.get('function'),
                        'lineno': frame.get('lineno'),
                        'context': frame.get('context_line'),
                        'code_context': frame.get('context')
                    }
        return None

    def get_issue_analysis_for_llm(self, sentry_url: str) -> str:
        """
        Orchestrates the fetching and formatting of issue data into a single
        string suitable for an LLM prompt.

        Args:
            sentry_url (str): The full URL to the Sentry issue.

        Returns:
            str: A formatted string with issue details for LLM analysis, or an error message.
        """
        issue_id = self._extract_issue_id_from_url(sentry_url)
        if not issue_id:
            return "Error: Could not extract a valid issue ID from the provided URL."

        # 1. Get high-level issue details
        issue_details = self.get_issue_details(issue_id)
        if not issue_details:
            return f"Error: Failed to fetch details for issue ID {issue_id}."

        # 2. Get the latest event for the stack trace
        latest_event = self.get_latest_event_for_issue(issue_id)
        if not latest_event:
            return f"Error: Failed to fetch the latest event for issue ID {issue_id}."

        # 3. Extract the key error location
        error_location = self._extract_error_location(latest_event)

        # 4. Build the analysis string for the LLM
        analysis = []
        analysis.append(f"Sentry Issue Analysis: {issue_details.get('title')}")
        analysis.append(f"Issue ID: {issue_id}")
        analysis.append(f"Level: {issue_details.get('level')}")
        analysis.append(f"Status: {issue_details.get('status')}")
        analysis.append(f"First Seen: {issue_details.get('firstSeen')}")
        analysis.append(f"Link: {issue_details.get('permalink')}")
        
        tags = latest_event.get('tags', [])
        if tags:
            analysis.append("\n--- Tags ---")
            for tag in tags:
                analysis.append(f"- {tag['key']}: {tag['value']}")

        if error_location:
            analysis.append("\n--- Root Cause Analysis ---")
            analysis.append(f"File: {error_location.get('filename')}")
            analysis.append(f"Function: {error_location.get('function')}")
            analysis.append(f"Line Number: {error_location.get('lineno')}")
            analysis.append(f"Error Line: {error_location.get('context')}")
            
            code_context = error_location.get('code_context')
            if code_context:
                analysis.append("\n--- Code Context ---")
                for line_no, line_code in code_context:
                    marker = ">>" if line_no == error_location.get('lineno') else "  "
                    analysis.append(f"{marker} {line_no:4d}| {line_code}")
        else:
            analysis.append("\n--- Root Cause Analysis ---")
            analysis.append("Could not automatically determine the exact in-app error location from the stack trace.")

        # Include the full raw stacktrace for more context for the LLM
        if latest_event.get('entries'):
             for entry in latest_event.get('entries', []):
                if entry.get('type') == 'exception':
                    values = entry.get('data', {}).get('values', [])
                    if values and values[-1].get('stacktrace'):
                        analysis.append("\n--- Full Stack Trace ---")
                        for frame in reversed(values[-1]['stacktrace']['frames']):
                            in_app_marker = "[APP] " if frame.get('in_app') else "[LIB] "
                            analysis.append(f"{in_app_marker}{frame.get('filename')} in {frame.get('function')} at line {frame.get('lineno')}")

        return "\n".join(analysis)

def test_sentry_api(sentry_issue_url):
    SENTRY_AUTH_TOKEN = settings.sentry_auth_token
    if "YOUR_SENTRY_AUTH_TOKEN" in SENTRY_AUTH_TOKEN:
        print("="*60)
        print("!!! PLEASE REPLACE PLACEHOLDER VALUES !!!")
        print("Please edit this script and replace SENTRY_AUTH_TOKEN with your actual Sentry data.")
        print("="*60)
    else:
        # Initialize the tool
        sentry_tool = SentryTool(auth_token=SENTRY_AUTH_TOKEN)

        # Get the analysis string to pass to an LLM
        llm_prompt = sentry_tool.get_issue_analysis_for_llm(sentry_issue_url)

        print("--- Generated Prompt for LLM ---")
        print(llm_prompt)

        # Now, you would pass this 'llm_prompt' to your chosen LLM
        # For example:
        #
        # from your_llm_library import generate_summary
        # summary = generate_summary(llm_prompt)
        # print("\n--- LLM Summary (mock) ---")
        # print(summary)

# --- Example Usage for Slack Bot ---
if __name__ == '__main__':
    test_sentry_api("https://sentry.io/organizations/apple/issues/1234567890/")  # Replace with a valid Sentry issue URL
   