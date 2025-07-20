"""
Tool integrations for the Architect Agent
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import plotly.io as pio
import plotly.graph_objects as go

# Import existing services
from services.developer.pr_reviewer import PRReviewService
from services.developer.pr_creator import PRCreatorService
from services.developer.pr_comment_handler import PRCommentHandler
from rag.sql_rag.qdrant_vector_store import IONetDataBot, add_sql_layer, refresh_preset_token
from rag.docs_rag.docs_store import create_rag_assistant
from models.schemas import PRReviewRequest, PRCreationRequest, PRCommentHandlingRequest
from config.settings import settings

logger = logging.getLogger(__name__)

class ArchitectTools:
    """Centralized tool manager for the Architect Agent"""
    
    def __init__(self):
        self.pr_reviewer = PRReviewService()
        self.pr_creator = PRCreatorService()
        self.pr_comment_handler = PRCommentHandler()
        
        # Initialize data bot
        self.data_bot = None
        self._initialize_data_bot()
        
        # Initialize docs assistant
        self.docs_assistant = create_rag_assistant(backend="qdrant")
        
    def _initialize_data_bot(self):
        """Initialize the IONetDataBot with proper configuration"""
        try:
            refresh_preset_token()
            self.data_bot = IONetDataBot()
            add_sql_layer(self.data_bot)
            logger.info("IONetDataBot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize IONetDataBot: {e}")
            self.data_bot = None

    # CODING TOOLS
    async def review_pr(self, pr_url: str, user_id: str, thread_id: str = None) -> Dict[str, Any]:
        """Review a pull request"""
        try:
            request = PRReviewRequest(
                pr_url=pr_url,
                thread_id=thread_id or "architect-review",
                user_id=user_id
            )
            
            result = await self.pr_reviewer.review_pr(request)
            
            return {
                "success": True,
                "data": {
                    "quality_score": result.code_quality_score,
                    "bugs_found": result.bugs_found,
                    "recommendations": result.recommendations,
                    "ci_status": result.ci_status,
                    "summary": result.review_summary
                }
            }
        except Exception as e:
            logger.error(f"PR review failed: {e}")
            return {"success": False, "error": str(e)}

    async def create_pr(self, description: str, repo_url: str, base_branch: str, 
                       user_id: str, thread_id: str = None) -> Dict[str, Any]:
        """Create a new pull request"""
        try:
            import uuid
            branch_name = f"architect-feature-{uuid.uuid4().hex[:8]}"
            
            request = PRCreationRequest(
                description=description,
                repo_url=repo_url,
                base_branch=base_branch,
                branch_name=branch_name,
                channel_id="architect",
                thread_id=thread_id or "architect-creation",
                user_id=user_id
            )
            
            result = await self.pr_creator.create_pr(request)
            
            return {
                "success": True,
                "data": {
                    "pr_url": result.pr_url,
                    "branch_name": result.branch_name,
                    "files_changed": result.files_changed,
                    "test_results": result.test_results
                }
            }
        except Exception as e:
            logger.error(f"PR creation failed: {e}")
            return {"success": False, "error": str(e)}

    async def handle_pr_comments(self, pr_url: str, user_id: str, 
                                thread_id: str = None) -> Dict[str, Any]:
        """Handle PR comments and feedback"""
        try:
            request = PRCommentHandlingRequest(
                pr_url=pr_url,
                thread_id=thread_id or "architect-comments",
                user_id=user_id,
                channel_id="architect"
            )
            
            result = await self.pr_comment_handler.handle_pr_comments(request)
            
            return {
                "success": True,
                "data": {
                    "comments_handled": result.comments_handled,
                    "files_modified": result.files_modified,
                    "commits_made": result.commits_made,
                    "summary": result.summary
                }
            }
        except Exception as e:
            logger.error(f"PR comment handling failed: {e}")
            return {"success": False, "error": str(e)}

    # DATA TOOLS
    def query_data(self, question: str) -> Dict[str, Any]:
        """Query io.net data using IONetDataBot"""
        try:
            if not self.data_bot:
                return {"success": False, "error": "Data bot not initialized"}
            
            # Use the data bot to answer the question
            result = self.data_bot.ask(question)
            
            # Extract plotly chart if present
            plotly_json = None
            if hasattr(result, 'plotly_json') and result.plotly_json:
                plotly_json = result.plotly_json
            elif isinstance(result, dict) and 'plotly_json' in result:
                plotly_json = result['plotly_json']
            
            return {
                "success": True,
                "data": {
                    "answer": str(result),
                    "plotly_json": plotly_json,
                    "query_type": "data_analysis"
                }
            }
        except Exception as e:
            logger.error(f"Data query failed: {e}")
            return {"success": False, "error": str(e)}

    def generate_sql_query(self, question: str) -> Dict[str, Any]:
        """Generate SQL query for the given question"""
        try:
            if not self.data_bot:
                return {"success": False, "error": "Data bot not initialized"}
            
            sql = self.data_bot.generate_sql(question)
            
            return {
                "success": True,
                "data": {
                    "sql_query": sql,
                    "question": question
                }
            }
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return {"success": False, "error": str(e)}

    def execute_sql_query(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        try:
            if not self.data_bot:
                return {"success": False, "error": "Data bot not initialized"}
            
            result = self.data_bot.run_sql(sql)
            
            return {
                "success": True,
                "data": {
                    "sql_result": result.to_dict() if hasattr(result, 'to_dict') else str(result),
                    "row_count": len(result) if hasattr(result, '__len__') else 0
                }
            }
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            return {"success": False, "error": str(e)}

    # DOCS TOOLS
    def search_docs(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search io.net documentation"""
        try:
            result = self.docs_assistant.answer(query, top_k=top_k)
            
            return {
                "success": True,
                "data": {
                    "answer": result["answer"],
                    "sources": result["sources"],
                    "relevant_links": result.get("relevant_source_links", []),
                    "followup_questions": result.get("followup_questions", [])
                }
            }
        except Exception as e:
            logger.error(f"Docs search failed: {e}")
            return {"success": False, "error": str(e)}

    def get_documentation_insights(self, topic: str) -> Dict[str, Any]:
        """Get comprehensive insights about a documentation topic"""
        try:
            # Perform multiple searches for comprehensive coverage
            queries = [
                f"What is {topic}?",
                f"How to use {topic}?",
                f"{topic} troubleshooting",
                f"{topic} best practices"
            ]
            
            insights = []
            all_sources = []
            
            for query in queries:
                result = self.docs_assistant.answer(query, top_k=3)
                if result["answer"] and "couldn't find" not in result["answer"].lower():
                    insights.append({
                        "query": query,
                        "answer": result["answer"],
                        "sources": len(result["sources"])
                    })
                    all_sources.extend(result["sources"])
            
            return {
                "success": True,
                "data": {
                    "topic": topic,
                    "insights": insights,
                    "total_sources": len(all_sources),
                    "coverage_score": len(insights) / len(queries)
                }
            }
        except Exception as e:
            logger.error(f"Documentation insights failed: {e}")
            return {"success": False, "error": str(e)}

    # UTILITY METHODS
    def create_plotly_visualization(self, data: Dict[str, Any], chart_type: str = "bar") -> Optional[str]:
        """Create a Plotly visualization from data"""
        try:
            if chart_type == "bar" and "x" in data and "y" in data:
                fig = go.Figure(data=go.Bar(x=data["x"], y=data["y"]))
                fig.update_layout(title=data.get("title", "Data Visualization"))
                return pio.to_json(fig)
            
            # Add more chart types as needed
            return None
        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            return None

    async def execute_tool_action(self, tool_type: str, action: str, query: str, 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a tool action based on type and action"""
        context = context or {}
        
        try:
            if tool_type == "coding":
                return await self._execute_coding_action(action, query, context)
            elif tool_type == "data":
                return self._execute_data_action(action, query, context)
            elif tool_type == "docs":
                return self._execute_docs_action(action, query, context)
            else:
                return {"success": False, "error": f"Unknown tool type: {tool_type}"}
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_coding_action(self, action: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coding-related actions"""
        user_id = context.get("user_id", "architect")
        thread_id = context.get("thread_id")
        
        if action == "review_pr":
            # Extract PR URL from query
            pr_url = self._extract_pr_url(query)
            if pr_url:
                return await self.review_pr(pr_url, user_id, thread_id)
            else:
                return {"success": False, "error": "No PR URL found in query"}
        
        elif action == "create_pr":
            repo_url = context.get("repo_url")
            base_branch = context.get("base_branch", "main")
            if repo_url:
                return await self.create_pr(query, repo_url, base_branch, user_id, thread_id)
            else:
                return {"success": False, "error": "Repository URL required for PR creation"}
        
        elif action == "handle_comments":
            pr_url = self._extract_pr_url(query)
            if pr_url:
                return await self.handle_pr_comments(pr_url, user_id, thread_id)
            else:
                return {"success": False, "error": "No PR URL found in query"}
        
        else:
            return {"success": False, "error": f"Unknown coding action: {action}"}

    def _execute_data_action(self, action: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data-related actions"""
        if action == "query_data":
            return self.query_data(query)
        elif action == "generate_sql":
            return self.generate_sql_query(query)
        elif action == "execute_sql":
            return self.execute_sql_query(query)
        else:
            return {"success": False, "error": f"Unknown data action: {action}"}

    def _execute_docs_action(self, action: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation-related actions"""
        if action == "search_docs":
            top_k = context.get("top_k", 5)
            return self.search_docs(query, top_k)
        elif action == "get_insights":
            return self.get_documentation_insights(query)
        else:
            return {"success": False, "error": f"Unknown docs action: {action}"}

    def _extract_pr_url(self, text: str) -> Optional[str]:
        """Extract GitHub PR URL from text"""
        import re
        pr_pattern = r'https://github\.com/[\w-]+/[\w-]+/pull/\d+'
        match = re.search(pr_pattern, text)
        return match.group(0) if match else None