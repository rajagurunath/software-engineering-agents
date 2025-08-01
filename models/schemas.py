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

class TrivyFinding(BaseModel):
    id: str  # e.g., CVE-2023-12345 or Pkg vulns id
    severity: str  # CRITICAL|HIGH|MEDIUM|LOW|UNKNOWN
    title: Optional[str] = None
    description: Optional[str] = None
    package_name: Optional[str] = None
    current_version: Optional[str] = None
    fixed_version: Optional[str] = None
    installed_path: Optional[str] = None  # e.g., requirements.txt line or file path
    references: List[str] = []
    type: Optional[str] = None  # os-pkgs, library, config, secret, misconfiguration
    target: Optional[str] = None  # file or image scanned
    class Config:
        arbitrary_types_allowed = True

class TrivyScanRequest(BaseModel):
    repo_url: str
    base_branch: str
    branch_name: Optional[str] = None
    description: Optional[str] = None
    trivy_raw_logs: str  # text pasted from Slack (non-JSON supported)
    trivy_json: Optional[Dict[str, Any]] = None  # future: structured JSON if available
    thread_id: str
    channel_id: str
    user_id: str

class TrivyFixChange(BaseModel):
    path: str
    type: str  # modify|create|delete
    content: str
    reasoning: Optional[str] = None

class TrivyScanResponse(BaseModel):
    pr_url: str
    branch_name: str
    commits: List[str]
    files_changed: List[str]
    fixes_applied: List[TrivyFixChange]
    unresolved_findings: List[TrivyFinding]
    summary: str
