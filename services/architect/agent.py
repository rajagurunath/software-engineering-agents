"""
Architect Agent - Deep Research Agent for io.net using PydanticAI
"""
import asyncio
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import plotly.io as pio

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from .models import (
    ResearchType, ResearchStep, ResearchPlan, ResearchResult, 
    ArchitectRequest, ToolType
)
from .prompts import (
    RESEARCH_PLANNER_PROMPT, EXECUTIVE_SUMMARY_PROMPT, 
    RECOMMENDATIONS_PROMPT, HTML_REPORT_TEMPLATE
)
from .tools import ArchitectTools
from config.settings import settings
from utils.opik_tracer import trace

logger = logging.getLogger(__name__)

class ArchitectAgent:
    """
    Deep Research Agent for io.net that can orchestrate multiple tools
    to provide comprehensive analysis and reports.
    """
    
    def __init__(self):
        self.tools = ArchitectTools()
        
        # Initialize PydanticAI agent
        self.model = OpenAIModel(
            model_name=settings.io_model,
            api_key=settings.iointelligence_api_key,
            base_url=settings.openai_base_url,
        )
        
        # Create the main research agent
        self.research_agent = Agent(
            model=self.model,
            system_prompt=self._get_system_prompt(),
            retries=2
        )
        
        # Create specialized agents for different tasks
        self.planner_agent = Agent(
            model=self.model,
            system_prompt="You are a research planning expert. Create detailed, actionable research plans.",
            retries=2
        )
        
        self.summarizer_agent = Agent(
            model=self.model,
            system_prompt="You are an expert at creating executive summaries and recommendations.",
            retries=2
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the main research agent"""
        return """You are the Architect Agent for io.net, a decentralized GPU network platform.

You are an expert researcher capable of conducting deep, multi-faceted analysis by orchestrating various specialized tools:

CODING TOOLS:
- PR Review: Analyze code quality, find bugs, assess technical implementation
- PR Creation: Generate new features and improvements
- Handle PR Comments: Address feedback and resolve issues

DATA TOOLS:
- IONetDataBot: Query network metrics, device performance, earnings, staking data
- Generate SQL queries and create visualizations
- Analyze network health and usage patterns

DOCS TOOLS:
- RagAssistant: Search platform documentation and knowledge base
- Provide user guidance and technical explanations

Your research methodology:
1. Understand the user's query and determine research scope
2. Create a strategic research plan using multiple tools
3. Execute research steps systematically
4. Synthesize findings into actionable insights
5. Generate comprehensive reports with visualizations

Always provide thorough, evidence-based analysis that helps users make informed decisions about io.net."""

    async def conduct_research(self, request: ArchitectRequest) -> ResearchResult:
        """
        Conduct comprehensive research based on the request
        """
        trace("architect.research_start", {
            "query": request.query,
            "research_type": request.research_type,
            "user_id": request.user_id
        })
        
        start_time = datetime.now()
        research_id = f"research-{uuid.uuid4().hex[:8]}"
        
        try:
            # Step 1: Create research plan
            logger.info(f"Creating research plan for: {request.query}")
            research_plan = await self._create_research_plan(request, research_id)
            
            # Step 2: Execute research steps
            logger.info(f"Executing {len(research_plan.steps)} research steps")
            executed_steps = await self._execute_research_steps(research_plan, request)
            
            # Step 3: Synthesize results
            logger.info("Synthesizing research results")
            result = await self._synthesize_results(
                research_id, request, executed_steps, start_time
            )
            
            # Step 4: Generate HTML report
            if request.include_visualizations:
                logger.info("Generating HTML report")
                result.html_report_path = await self._generate_html_report(result)
            
            trace("architect.research_complete", {
                "research_id": research_id,
                "steps_completed": len(executed_steps),
                "duration_seconds": result.total_duration_seconds
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            trace("architect.research_error", {"error": str(e)})
            raise

    async def _create_research_plan(self, request: ArchitectRequest, research_id: str) -> ResearchPlan:
        """Create a detailed research plan"""
        
        # Determine research type if not specified
        research_type = request.research_type or await self._determine_research_type(request.query)
        
        # Generate research plan using the planner agent
        plan_prompt = RESEARCH_PLANNER_PROMPT.format(query=request.query)
        
        try:
            response = await self.planner_agent.run(plan_prompt)
            plan_data = json.loads(response.data)
            
            # Convert to ResearchStep objects
            steps = []
            for i, step_data in enumerate(plan_data["steps"]):
                step = ResearchStep(
                    step_id=f"{research_id}-step-{i+1}",
                    tool_type=ToolType(step_data["tool_type"]),
                    action=step_data["action"],
                    query=step_data["query"]
                )
                steps.append(step)
            
            return ResearchPlan(
                research_id=research_id,
                research_type=research_type,
                original_query=request.query,
                steps=steps,
                estimated_duration_minutes=plan_data.get("estimated_duration_minutes", 10)
            )
            
        except Exception as e:
            logger.error(f"Failed to create research plan: {e}")
            # Fallback to default plan
            return self._create_default_plan(request, research_id, research_type)

    async def _determine_research_type(self, query: str) -> ResearchType:
        """Determine the most appropriate research type for the query"""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ["pr", "code", "review", "implementation", "bug"]):
            return ResearchType.CODE_REVIEW
        elif any(keyword in query_lower for keyword in ["data", "metrics", "performance", "analytics", "sql"]):
            return ResearchType.DATA_ANALYSIS
        elif any(keyword in query_lower for keyword in ["docs", "documentation", "guide", "how to"]):
            return ResearchType.DOCUMENTATION
        else:
            return ResearchType.COMPREHENSIVE

    def _create_default_plan(self, request: ArchitectRequest, research_id: str, 
                           research_type: ResearchType) -> ResearchPlan:
        """Create a default research plan as fallback"""
        steps = []
        
        if research_type == ResearchType.DATA_ANALYSIS:
            steps = [
                ResearchStep(
                    step_id=f"{research_id}-step-1",
                    tool_type=ToolType.DATA,
                    action="query_data",
                    query=request.query
                )
            ]
        elif research_type == ResearchType.DOCUMENTATION:
            steps = [
                ResearchStep(
                    step_id=f"{research_id}-step-1",
                    tool_type=ToolType.DOCS,
                    action="search_docs",
                    query=request.query
                )
            ]
        else:
            # Comprehensive approach
            steps = [
                ResearchStep(
                    step_id=f"{research_id}-step-1",
                    tool_type=ToolType.DOCS,
                    action="search_docs",
                    query=request.query
                ),
                ResearchStep(
                    step_id=f"{research_id}-step-2",
                    tool_type=ToolType.DATA,
                    action="query_data",
                    query=request.query
                )
            ]
        
        return ResearchPlan(
            research_id=research_id,
            research_type=research_type,
            original_query=request.query,
            steps=steps,
            estimated_duration_minutes=5
        )

    async def _execute_research_steps(self, plan: ResearchPlan, 
                                    request: ArchitectRequest) -> List[ResearchStep]:
        """Execute all research steps in the plan"""
        executed_steps = []
        
        context = {
            "user_id": request.user_id,
            "thread_id": request.thread_id,
            "channel_id": request.channel_id
        }
        
        for step in plan.steps:
            step_start = datetime.now()
            
            try:
                logger.info(f"Executing step: {step.action} with {step.tool_type}")
                
                result = await self.tools.execute_tool_action(
                    tool_type=step.tool_type.value,
                    action=step.action,
                    query=step.query,
                    context=context
                )
                
                step.result = result
                step.duration_seconds = (datetime.now() - step_start).total_seconds()
                
                executed_steps.append(step)
                
                # Add small delay between steps to avoid overwhelming services
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Step {step.step_id} failed: {e}")
                step.result = {"success": False, "error": str(e)}
                step.duration_seconds = (datetime.now() - step_start).total_seconds()
                executed_steps.append(step)
        
        return executed_steps

    async def _synthesize_results(self, research_id: str, request: ArchitectRequest,
                                executed_steps: List[ResearchStep], 
                                start_time: datetime) -> ResearchResult:
        """Synthesize all research findings into a comprehensive result"""
        
        # Collect all findings
        findings = []
        visualizations = []
        code_analysis = None
        documentation_insights = None
        
        for step in executed_steps:
            if step.result and step.result.get("success"):
                step_finding = {
                    "step_id": step.step_id,
                    "tool_type": step.tool_type.value,
                    "action": step.action,
                    "query": step.query,
                    "result": step.result["data"],
                    "duration": step.duration_seconds
                }
                findings.append(step_finding)
                
                # Extract visualizations
                if "plotly_json" in step.result.get("data", {}):
                    plotly_json = step.result["data"]["plotly_json"]
                    if plotly_json:
                        visualizations.append({
                            "title": f"Data Analysis: {step.query}",
                            "plotly_json": plotly_json,
                            "step_id": step.step_id
                        })
                
                # Categorize findings
                if step.tool_type == ToolType.CODING:
                    code_analysis = step.result["data"]
                elif step.tool_type == ToolType.DOCS:
                    documentation_insights = step.result["data"]
        
        # Generate executive summary
        findings_text = json.dumps(findings, indent=2)
        summary_prompt = EXECUTIVE_SUMMARY_PROMPT.format(
            query=request.query,
            research_type=request.research_type or "comprehensive",
            findings=findings_text
        )
        
        try:
            summary_response = await self.summarizer_agent.run(summary_prompt)
            executive_summary = summary_response.data
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            executive_summary = f"Research completed for: {request.query}. Please review detailed findings below."
        
        # Generate recommendations
        recommendations_prompt = RECOMMENDATIONS_PROMPT.format(
            query=request.query,
            findings=findings_text
        )
        
        try:
            rec_response = await self.summarizer_agent.run(recommendations_prompt)
            recommendations_text = rec_response.data
            recommendations = [line.strip() for line in recommendations_text.split('\n') if line.strip()]
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            recommendations = ["Review the detailed findings for insights and next steps."]
        
        total_duration = (datetime.now() - start_time).total_seconds()
        
        return ResearchResult(
            research_id=research_id,
            original_query=request.query,
            research_type=request.research_type or ResearchType.COMPREHENSIVE,
            executive_summary=executive_summary,
            detailed_findings=findings,
            recommendations=recommendations,
            data_visualizations=visualizations,
            code_analysis=code_analysis,
            documentation_insights=documentation_insights,
            total_duration_seconds=total_duration
        )

    async def _generate_html_report(self, result: ResearchResult) -> str:
        """Generate an HTML report with embedded visualizations"""
        try:
            # Prepare visualizations HTML
            visualizations_html = ""
            if result.data_visualizations:
                visualizations_html = '<div class="section"><h2>📊 Data Visualizations</h2>'
                
                for i, viz in enumerate(result.data_visualizations):
                    viz_id = f"viz-{i}"
                    visualizations_html += f'''
                    <div class="visualization">
                        <h3>{viz["title"]}</h3>
                        <div id="{viz_id}"></div>
                        <script>
                            Plotly.newPlot('{viz_id}', {viz["plotly_json"]});
                        </script>
                    </div>
                    '''
                
                visualizations_html += '</div>'
            
            # Prepare detailed findings HTML
            detailed_findings_html = ""
            for finding in result.detailed_findings:
                tool_class = f"tool-{finding['tool_type']}"
                detailed_findings_html += f'''
                <div class="step-result">
                    <span class="tool-badge {tool_class}">{finding['tool_type'].upper()}</span>
                    <strong>{finding['action']}</strong>: {finding['query']}
                    <div style="margin-top: 10px;">
                        {self._format_finding_result(finding['result'])}
                    </div>
                    <small>Duration: {finding.get('duration', 0):.2f}s</small>
                </div>
                '''
            
            # Prepare recommendations HTML
            recommendations_html = ""
            for rec in result.recommendations:
                recommendations_html += f"<li>{rec}</li>"
            
            # Generate HTML report
            html_content = HTML_REPORT_TEMPLATE.format(
                title=result.original_query[:50],
                query=result.original_query,
                research_type=result.research_type.value,
                timestamp=result.completed_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                executive_summary=result.executive_summary,
                recommendations_html=recommendations_html,
                visualizations_html=visualizations_html,
                detailed_findings_html=detailed_findings_html,
                research_id=result.research_id,
                duration=result.total_duration_seconds,
                steps_count=len(result.detailed_findings),
                tools_used=", ".join(set(f['tool_type'] for f in result.detailed_findings))
            )
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                return f.name
                
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return None

    def _format_finding_result(self, result: Dict[str, Any]) -> str:
        """Format a finding result for HTML display"""
        if isinstance(result, dict):
            if "answer" in result:
                return f"<p>{result['answer']}</p>"
            elif "summary" in result:
                return f"<p>{result['summary']}</p>"
            else:
                # Format as key-value pairs
                formatted = "<ul>"
                for key, value in result.items():
                    if key not in ["plotly_json"]:  # Skip large JSON data
                        formatted += f"<li><strong>{key}:</strong> {value}</li>"
                formatted += "</ul>"
                return formatted
        else:
            return f"<p>{str(result)}</p>"

# Factory function for easy instantiation
def create_architect_agent() -> ArchitectAgent:
    """Create and return a configured ArchitectAgent instance"""
    return ArchitectAgent()