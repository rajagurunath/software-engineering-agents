"""
Architect Service - Main service interface for the Architect Agent
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .agent import ArchitectAgent
from .models import ArchitectRequest, ResearchResult, ResearchType
from utils.opik_tracer import trace

logger = logging.getLogger(__name__)

class ArchitectService:
    """
    Service layer for the Architect Agent that handles research requests
    and provides a clean interface for integration with other systems.
    """
    
    def __init__(self):
        self.agent = ArchitectAgent()
        self.active_research: Dict[str, ResearchResult] = {}
    
    async def conduct_research(
        self,
        query: str,
        user_id: str,
        research_type: Optional[ResearchType] = None,
        thread_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        priority: str = "medium",
        include_visualizations: bool = True,
        max_research_steps: int = 10,
        num_charts: int = 5,
        user_id_context: Optional[str] = None,
        device_id_context: Optional[str] = None
    ) -> ResearchResult:
        """
        Conduct comprehensive research on the given query
        
        Args:
            query: The research question or topic
            user_id: ID of the user requesting research
            research_type: Type of research to conduct (optional, will be auto-determined)
            thread_id: Thread ID for tracking (optional)
            channel_id: Channel ID for notifications (optional)
            priority: Priority level (low, medium, high)
            include_visualizations: Whether to include data visualizations
            max_research_steps: Maximum number of research steps to execute
            
        Returns:
            ResearchResult with comprehensive findings and analysis
        """
        trace("architect_service.research_start", {
            "query": query,
            "user_id": user_id,
            "research_type": research_type
        })
        
        try:
            # Create research request
            request = ArchitectRequest(
                query=query,
                research_type=research_type,
                user_id=user_id,
                thread_id=thread_id,
                channel_id=channel_id,
                priority=priority,
                include_visualizations=include_visualizations,
                max_research_steps=max_research_steps,
                num_charts=num_charts,
                user_id_context=user_id_context,
                device_id_context=device_id_context
            )
            
            # Conduct research
            result = await self.agent.conduct_research(request)
            
            # Store result for future reference
            self.active_research[result.research_id] = result
            
            trace("architect_service.research_complete", {
                "research_id": result.research_id,
                "duration_seconds": result.total_duration_seconds,
                "findings_count": len(result.detailed_findings)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Research failed for query '{query}': {e}")
            trace("architect_service.research_error", {"error": str(e)})
            raise

    async def get_research_status(self, research_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a research request"""
        if research_id in self.active_research:
            result = self.active_research[research_id]
            return {
                "research_id": research_id,
                "status": "completed",
                "query": result.original_query,
                "completed_at": result.completed_at,
                "duration_seconds": result.total_duration_seconds,
                "findings_count": len(result.detailed_findings),
                "has_visualizations": len(result.data_visualizations) > 0,
                "has_html_report": result.html_report_path is not None
            }
        return None

    def get_research_result(self, research_id: str) -> Optional[ResearchResult]:
        """Get the full research result by ID"""
        return self.active_research.get(research_id)

    async def quick_data_analysis(self, question: str, user_id: str) -> Dict[str, Any]:
        """
        Perform quick data analysis without full research workflow
        """
        try:
            result = self.agent.tools.query_data(question)
            
            if result["success"]:
                return {
                    "success": True,
                    "answer": result["data"]["answer"],
                    "plotly_json": result["data"].get("plotly_json"),
                    "query": question,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Quick data analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def quick_docs_search(self, question: str, user_id: str) -> Dict[str, Any]:
        """
        Perform quick documentation search without full research workflow
        """
        try:
            result = self.agent.tools.search_docs(question)
            
            if result["success"]:
                return {
                    "success": True,
                    "answer": result["data"]["answer"],
                    "sources": result["data"]["sources"],
                    "relevant_links": result["data"].get("relevant_links", []),
                    "followup_questions": result["data"].get("followup_questions", []),
                    "query": question,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Quick docs search failed: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_pr(self, pr_url: str, user_id: str) -> Dict[str, Any]:
        """
        Perform quick PR analysis without full research workflow
        """
        try:
            result = await self.agent.tools.review_pr(pr_url, user_id)
            
            if result["success"]:
                return {
                    "success": True,
                    "pr_url": pr_url,
                    "quality_score": result["data"]["quality_score"],
                    "bugs_found": result["data"]["bugs_found"],
                    "recommendations": result["data"]["recommendations"],
                    "ci_status": result["data"]["ci_status"],
                    "summary": result["data"]["summary"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"PR analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def cleanup_old_research(self, max_age_hours: int = 24):
        """Clean up old research results to free memory"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for research_id, result in self.active_research.items():
            if result.completed_at.timestamp() < cutoff_time:
                to_remove.append(research_id)
        
        for research_id in to_remove:
            del self.active_research[research_id]
            logger.info(f"Cleaned up old research: {research_id}")

    async def get_available_capabilities(self) -> Dict[str, Any]:
        """Get information about available research capabilities"""
        return {
            "research_types": [rt.value for rt in ResearchType],
            "coding_tools": [
                "review_pr - Analyze pull requests for quality and issues",
                "create_pr - Generate new pull requests with implementations", 
                "handle_comments - Address PR feedback automatically"
            ],
            "data_tools": [
                "query_data - Query io.net metrics and generate visualizations",
                "generate_sql - Create SQL queries for specific data needs",
                "execute_sql - Run custom SQL queries on the database"
            ],
            "docs_tools": [
                "search_docs - Search platform documentation and guides",
                "get_insights - Get comprehensive insights on documentation topics"
            ],
            "output_formats": [
                "Structured JSON results",
                "HTML reports with visualizations", 
                "Plotly interactive charts",
                "Executive summaries and recommendations"
            ]
        }
