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
import pandas as pd
import tempfile
import os

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
        # Reuse existing services - DON'T REINVENT THE WHEEL
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
        """Review a pull request using existing PRReviewService"""
        try:
            request = PRReviewRequest(
                pr_url=pr_url,
                thread_id=thread_id or "architect-review",
                user_id=user_id
            )
            
            # Use existing PR review service - DON'T REINVENT
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
        """Create a new pull request using existing PRCreatorService"""
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
            
            # Use existing PR creator service - DON'T REINVENT
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
        """Handle PR comments and feedback using existing PRCommentHandler"""
        try:
            request = PRCommentHandlingRequest(
                pr_url=pr_url,
                thread_id=thread_id or "architect-comments",
                user_id=user_id,
                channel_id="architect"
            )
            
            # Use existing PR comment handler - DON'T REINVENT
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

    # DATA TOOLS - ENHANCED WITH MULTIPLE QUESTIONS AND CHARTS
    def query_data(self, question: str, generate_related: bool = True) -> Dict[str, Any]:
        """Query io.net data using IONetDataBot with enhanced multi-question analysis"""
        try:
            if not self.data_bot:
                return {"success": False, "error": "Data bot not initialized"}
            
            # Generate related questions for comprehensive analysis
            related_questions = []
            if generate_related:
                related_questions = self._generate_related_data_questions(question)
            
            # Process main question
            main_result = self._process_single_data_question(question)
            
            # Process related questions
            related_results = []
            for related_q in related_questions:
                try:
                    result = self._process_single_data_question(related_q)
                    if result.get("success"):
                        related_results.append({
                            "question": related_q,
                            "result": result
                        })
                except Exception as e:
                    logger.warning(f"Failed to process related question '{related_q}': {e}")
            
            return {
                "success": True,
                "data": {
                    "main_question": question,
                    "main_result": main_result,
                    "related_analysis": related_results,
                    "total_charts": 1 + len(related_results)
                }
            }
        except Exception as e:
            logger.error(f"Data query failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _process_single_data_question(self, question: str) -> Dict[str, Any]:
        """Process a single data question using IONetDataBot"""
        try:
            # Use IONetDataBot with the exact pattern specified
            sql = self.data_bot.generate_sql(question=question)
            data = self.data_bot.run_sql(sql=sql)
            temp_df = pd.DataFrame(data)
            plotly_code = self.data_bot.generate_plotly_code(question=question, sql=sql, df_metadata=temp_df)
            fig = self.data_bot.get_plotly_figure(plotly_code=plotly_code, df=temp_df)
            plotly_json = fig.to_json()
            followup_questions = self.data_bot.generate_followup_questions(question=question, sql=sql, df=temp_df, n_questions=5)
            
            return {
                "success": True,
                "answer": f"Query executed successfully. Found {len(data)} records.",
                "sql_query": sql,
                "data": data,
                "plotly_json": plotly_json,
                "followup_questions": followup_questions,
                "row_count": len(data)
            }
        except Exception as e:
            logger.error(f"Single data query failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_related_data_questions(self, main_question: str) -> List[str]:
        """Generate related questions for comprehensive data analysis"""
        # Use docs assistant to identify relevant tables and generate related questions
        try:
            # Query docs for table information
            table_info = self.docs_assistant.answer(f"What database tables are relevant for: {main_question}")
            
            # Generate related questions based on the main question
            related_questions = []
            
            # Check if it's about a specific user/device owner
            if any(keyword in main_question.lower() for keyword in ['user', 'owner', 'email', '@']):
                related_questions.extend([
                    f"How many devices does this user own?",
                    f"What are the total block rewards earned by this user?",
                    f"How many clusters were created on this user's devices?",
                    f"Which devices are co-staked for this user?"
                ])
            
            # Check if it's about devices
            elif any(keyword in main_question.lower() for keyword in ['device', 'gpu', 'cpu', 'hardware']):
                related_questions.extend([
                    f"What is the device utilization trend over time?",
                    f"How many devices are currently earning block rewards?",
                    f"What is the distribution of device types in the network?",
                    f"Which devices have the highest uptime?"
                ])
            
            # Check if it's about block rewards
            elif any(keyword in main_question.lower() for keyword in ['block', 'reward', 'earning']):
                related_questions.extend([
                    f"What is the trend of block rewards over the last 30 days?",
                    f"How many unique devices earned rewards today?",
                    f"What is the average reward per device?",
                    f"Which device types earn the most rewards?"
                ])
            
            # Check if it's about clusters/jobs
            elif any(keyword in main_question.lower() for keyword in ['cluster', 'job', 'hire']):
                related_questions.extend([
                    f"What is the cluster utilization rate?",
                    f"How many jobs were completed successfully?",
                    f"What is the average job duration?",
                    f"Which device types are most frequently hired?"
                ])
            
            # Default related questions
            else:
                related_questions.extend([
                    f"What are the key metrics related to this query?",
                    f"How has this metric changed over time?",
                    f"What factors influence this data?",
                    f"Are there any anomalies or trends to note?"
                ])
            
            return related_questions[:4]  # Limit to 4 related questions
            
        except Exception as e:
            logger.warning(f"Failed to generate related questions: {e}")
            return []

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

    # DOCS TOOLS - USE EXISTING RAGASSISTANT
    def search_docs(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search io.net documentation using existing RagAssistant"""
        try:
            # Use existing RagAssistant - DON'T REINVENT
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
                # Use existing RagAssistant
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
            return self.query_data(query, generate_related=True)
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