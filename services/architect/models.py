from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum

class ResearchType(str, Enum):
    """Types of research the architect can perform"""
    CODE_REVIEW = "code_review"
    DATA_ANALYSIS = "data_analysis"
    DOCUMENTATION = "documentation"
    COMPREHENSIVE = "comprehensive"

class ToolType(str, Enum):
    """Available tool types"""
    CODING = "coding"
    DATA = "data"
    DOCS = "docs"

class ResearchStep(BaseModel):
    """Individual research step"""
    step_id: str
    tool_type: ToolType
    action: str
    query: str
    result: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_seconds: Optional[float] = None

class ResearchPlan(BaseModel):
    """Research plan with multiple steps"""
    research_id: str
    research_type: ResearchType
    original_query: str
    steps: List[ResearchStep]
    estimated_duration_minutes: int
    created_at: datetime = Field(default_factory=datetime.now)

class ResearchResult(BaseModel):
    """Final research result"""
    research_id: str
    original_query: str
    research_type: ResearchType
    executive_summary: str
    detailed_findings: List[Dict[str, Any]]
    recommendations: List[str]
    data_visualizations: List[Dict[str, Any]] = []  # Plotly graphs
    data_analysis_results: List[Dict[str, Any]] = []  # Enhanced data results
    code_analysis: Optional[Dict[str, Any]] = None
    documentation_insights: Optional[Dict[str, Any]] = None
    html_report_path: Optional[str] = None
    completed_at: datetime = Field(default_factory=datetime.now)
    total_duration_seconds: float

class ArchitectRequest(BaseModel):
    """Request to the architect agent"""
    query: str
    research_type: Optional[ResearchType] = None
    user_id: str
    thread_id: Optional[str] = None
    channel_id: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"
    include_visualizations: bool = True
    max_research_steps: int = 10
    num_charts: int = 5
    user_id_context: Optional[str] = None
    device_id_context: Optional[str] = None
