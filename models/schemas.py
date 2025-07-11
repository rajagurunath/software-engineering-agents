from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"

class PRReviewRequest(BaseModel):
    pr_url: str
    thread_id: str
    user_id: str
    linear_issue_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class PRReviewResponse(BaseModel):
    pr_url: str
    review_summary: str
    code_quality_score: int
    bugs_found: List[str]
    test_coverage_issues: List[str]
    ci_status: str
    recommendations: List[str]
    linear_context: Optional[Dict[str, Any]] = None

class PRCreationRequest(BaseModel):
    description: str
    linear_issue_id: Optional[str] = None
    repo_url: str
    base_branch: str
    branch_name: str
    channel_id: str
    thread_id: str
    user_id: str
    clarification_questions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)

class PRCreationResponse(BaseModel):
    pr_url: str
    branch_name: str
    commits: List[str]
    test_results: Dict[str, Any]
    files_changed: List[str]

class WorkflowExecution(BaseModel):
    execution_id: str
    workflow_type: str
    status: TaskStatus
    thread_id: str
    user_id: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    approval_required: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ApprovalRequest(BaseModel):
    execution_id: str
    approval_type: str
    context: Dict[str, Any]
    requested_by: str
    requested_at: datetime = Field(default_factory=datetime.now)
class PRCommentHandlingRequest(BaseModel):
    pr_url: str
    thread_id: str
    user_id: str
    channel_id: str
    created_at: datetime = Field(default_factory=datetime.now)

class PRCommentHandlingResponse(BaseModel):
    pr_url: str
    comments_handled: int
    commits_made: List[str]
    files_modified: List[str]
    summary: str
    unresolved_comments: List[Dict[str, Any]]