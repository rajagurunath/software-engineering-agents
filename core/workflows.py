from dbos import DBOS, DBOSConfig
from typing import Dict, Any, Optional
from models.schemas import (
    PRReviewRequest, PRReviewResponse, 
    PRCreationRequest, PRCreationResponse,
    WorkflowExecution, TaskStatus, ApprovalRequest
)
from services.developer.pr_reviewer import PRReviewService
from services.developer.pr_creator import PRCreatorService
from services.developer.pr_comment_handler import PRCommentHandler
from services.developer.approval_system import ApprovalService
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class PRWorkflows:
    def __init__(self):
        self.pr_reviewer = PRReviewService()
        self.pr_creator = PRCreatorService()
        self.pr_comment_handler = PRCommentHandler()
        self.approval_service = ApprovalService()
        
    # DBOS.workflow()
    async def pr_review_workflow(self, request: PRReviewRequest) -> PRReviewResponse:
        """Complete PR review workflow"""
        execution_id = f"review-{request.thread_id}-{request.pr_url.split('/')[-1]}"
        
        # Update execution status
        await self._update_execution_status(
            execution_id, TaskStatus.IN_PROGRESS, request.dict()
        )
        
        try:
            # Perform PR review
            review_result = await self.pr_reviewer.review_pr(request)
            
            # Update status to completed
            await self._update_execution_status(
                execution_id, TaskStatus.COMPLETED, review_result.dict()
            )
            
            return review_result
            
        except Exception as e:
            logger.exception("PR review workflow failed")
            await self._update_execution_status(
                execution_id, TaskStatus.FAILED, {"error": str(e)}
            )
            raise
            
    DBOS.workflow()
    async def pr_comment_handling_workflow(self, request) -> Any:
        """Handle PR comments workflow"""
        from models.schemas import PRCommentHandlingRequest
        
        execution_id = f"comments-{request.thread_id}-{request.pr_url.split('/')[-1]}"
        
        # Update execution status
        await self._update_execution_status(
            execution_id, TaskStatus.IN_PROGRESS, request.dict()
        )
        
        try:
            # Handle PR comments
            result = await self.pr_comment_handler.handle_pr_comments(request)
            
            # Update status to completed
            await self._update_execution_status(
                execution_id, TaskStatus.COMPLETED, result.dict()
            )
            
            return result
            
        except Exception as e:
            logger.exception("PR comment handling workflow failed")
            await self._update_execution_status(
                execution_id, TaskStatus.FAILED, {"error": str(e)}
            )
            raise
    
    DBOS.workflow()
    async def pr_creation_workflow(self, request: PRCreationRequest) -> PRCreationResponse:
        """Complete PR creation workflow with approval"""
        execution_id = f"create-{request.thread_id}-{request.branch_name}"
        
        # Update execution status
        await self._update_execution_status(
            execution_id, TaskStatus.IN_PROGRESS, request.dict()
        )
        
        try:
            # Check if approval is required for this type of change
            approval_required = (not settings.skip_approvals) and await self._check_approval_required(request)
            
            if approval_required:
                # Request approval
                approval_request = ApprovalRequest(
                    execution_id=execution_id,
                    approval_type="pr_creation",
                    context=request.dict(),
                    requested_by=request.user_id
                )
                
                await self.approval_service.request_approval(approval_request)
                
                # Update status to waiting for approval
                await self._update_execution_status(
                    execution_id, TaskStatus.WAITING_APPROVAL, request.dict()
                )
                
                # Wait for approval (this will be resumed when approval is granted)
                approval_result = await self._wait_for_approval(execution_id)
                
                if not approval_result:
                    await self._update_execution_status(
                        execution_id, TaskStatus.REJECTED, {"reason": "Approval denied"}
                    )
                    raise Exception("PR creation was rejected")
                    
                await self._update_execution_status(
                    execution_id, TaskStatus.APPROVED, {}
                )
            
            # Create PR
            creation_result = await self.pr_creator.create_pr(request)
            
            # Update status to completed
            await self._update_execution_status(
                execution_id, TaskStatus.COMPLETED, creation_result.dict()
            )
            
            return creation_result
            
        except Exception as e:
            logger.exception("PR creation workflow failed")
            await self._update_execution_status(
                execution_id, TaskStatus.FAILED, {"error": str(e)}
            )
            raise
            
    DBOS.step()
    async def _update_execution_status(self, execution_id: str, 
                                     status: TaskStatus, 
                                     data: Dict[str, Any]) -> None:
        """Update workflow execution status in database"""
        # This would update the database with execution status
        logger.info(f"Execution {execution_id} status: {status}")
        
        # In a real implementation, this would update the database
        # For now, we'll just log the status change
        
    DBOS.step()
    async def _check_approval_required(self, request: PRCreationRequest) -> bool:
        """Check if approval is required for this PR creation"""
        # Define approval rules
        approval_rules = [
            lambda req: "production" in req.repo_url.lower(),
            lambda req: "main" in req.branch_name.lower(),
            lambda req: req.linear_issue_id is None,  # No Linear issue
        ]
        
        for rule in approval_rules:
            if rule(request):
                return True
                
        return False
        
    DBOS.step()
    async def _wait_for_approval(self, execution_id: str) -> bool:
        """Wait for approval to be granted"""
        # This would implement a durable wait mechanism
        # For now, we'll return True (approved)
        return True
        
    DBOS.workflow()
    async def approval_workflow(self, approval_request: ApprovalRequest) -> bool:
        """Handle approval workflow"""
        # Send approval request to Slack
        await self.approval_service.send_approval_request(approval_request)
        
        # Wait for response
        result = await self.approval_service.wait_for_approval_response(
            approval_request.execution_id
        )
        
        return result