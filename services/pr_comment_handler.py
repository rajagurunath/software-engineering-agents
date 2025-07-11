"""Service for handling PR comments and automatically addressing them."""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
from utils.opik_tracer import trace
from core.sandbox import SandboxManager
from core.integrations.github_client import GitHubClient
from core.integrations.llm_client import LLMClient
from models.schemas import PRCommentHandlingRequest, PRCommentHandlingResponse
from services.code_analyzer import CodeAnalyzer
import logging

logger = logging.getLogger(__name__)

class PRCommentHandler:
    def __init__(self):
        self.sandbox_manager = SandboxManager()
        self.github_client = GitHubClient()
        self.llm_client = LLMClient()
        self.code_analyzer = CodeAnalyzer()
        
    async def handle_pr_comments(self, request: PRCommentHandlingRequest) -> PRCommentHandlingResponse:
        """Handle all comments on a PR by making appropriate code changes"""
        logger.info(f"Starting PR comment handling for: {request.pr_url}")
        trace("pr_comment_handler.start", {"pr_url": request.pr_url})
        
        # Parse PR URL
        owner, repo, pr_number = self._parse_pr_url(request.pr_url)
        
        # Get PR details and comments
        pr_details, review_comments, issue_comments = await asyncio.gather(
            self.github_client.get_pr_details(owner, repo, pr_number),
            self.github_client.get_pr_review_comments(owner, repo, pr_number),
            self.github_client.get_pr_issue_comments(owner, repo, pr_number)
        )
        
        # Filter actionable comments (exclude resolved, bot comments, etc.)
        actionable_comments = self._filter_actionable_comments(review_comments, issue_comments)
        
        if not actionable_comments:
            return PRCommentHandlingResponse(
                pr_url=request.pr_url,
                comments_handled=0,
                commits_made=[],
                files_modified=[],
                summary="No actionable comments found to handle.",
                unresolved_comments=[]
            )
        
        trace("pr_comment_handler.comments_found", {"count": len(actionable_comments)})
        
        # Create sandbox and clone the PR branch
        sandbox_id = f"comment-handler-{uuid.uuid4().hex[:8]}"
        
        with self.sandbox_manager.get_sandbox(sandbox_id) as sandbox:
            # Clone the PR branch
            repo_url = pr_details["head"]["repo"]["clone_url"]
            pr_branch = pr_details["head"]["ref"]
            
            repo_path = sandbox.clone_repo(repo_url, pr_branch)
            
            # Analyze repository structure
            repo_analysis = self.code_analyzer.analyze_repository(repo_path)
            
            # Group comments by file for efficient processing
            comments_by_file = self._group_comments_by_file(actionable_comments)
            
            commits_made = []
            files_modified = []
            handled_comments = []
            unresolved_comments = []
            
            # Process each file's comments
            for file_path, file_comments in comments_by_file.items():
                try:
                    result = await self._handle_file_comments(
                        sandbox, repo_path, file_path, file_comments, repo_analysis
                    )
                    
                    if result["modified"]:
                        # Commit changes for this file
                        commit_message = f"Address comments in {file_path}\n\n" + \
                                       "\n".join([f"- {c['summary']}" for c in result["handled_comments"]])
                        
                        commit_sha = sandbox.commit_changes(commit_message)
                        commits_made.append(commit_sha)
                        files_modified.append(file_path)
                        handled_comments.extend(result["handled_comments"])
                        
                        # Mark comments as resolved on GitHub
                        for comment in result["handled_comments"]:
                            try:
                                if comment.get("id"):
                                    await self.github_client.resolve_review_comment(
                                        owner, repo, comment["id"]
                                    )
                            except Exception as e:
                                logger.warning(f"Failed to resolve comment {comment.get('id')}: {e}")
                    else:
                        unresolved_comments.extend(file_comments)
                        
                except Exception as e:
                    logger.error(f"Failed to handle comments for {file_path}: {e}")
                    unresolved_comments.extend(file_comments)
            
            # Push all changes
            if commits_made:
                sandbox.push_branch(pr_branch)
                
            # Generate summary
            summary = self._generate_summary(handled_comments, commits_made, files_modified, unresolved_comments)
            
            result = PRCommentHandlingResponse(
                pr_url=request.pr_url,
                comments_handled=len(handled_comments),
                commits_made=commits_made,
                files_modified=files_modified,
                summary=summary,
                unresolved_comments=[self._sanitize_comment(c) for c in unresolved_comments]
            )
            
            trace("pr_comment_handler.complete", {
                "comments_handled": len(handled_comments),
                "commits_made": len(commits_made)
            })
            
            return result
    
    def _parse_pr_url(self, pr_url: str) -> tuple:
        """Parse GitHub PR URL to extract owner, repo, and PR number"""
        # Example: https://github.com/owner/repo/pull/123
        parts = pr_url.split("/")
        owner = parts[3]
        repo = parts[4]
        pr_number = int(parts[6])
        return owner, repo, pr_number
    
    def _filter_actionable_comments(self, review_comments: List[Dict], issue_comments: List[Dict]) -> List[Dict]:
        """Filter comments to find actionable ones"""
        actionable = []
        
        # Process review comments (line-specific)
        for comment in review_comments:
            if self._is_actionable_comment(comment):
                actionable.append({
                    "type": "review",
                    "id": comment["id"],
                    "body": comment["body"],
                    "path": comment.get("path"),
                    "line": comment.get("line"),
                    "diff_hunk": comment.get("diff_hunk"),
                    "user": comment["user"]["login"],
                    "created_at": comment["created_at"]
                })
        
        # Process issue comments (general PR comments)
        for comment in issue_comments:
            if self._is_actionable_comment(comment):
                actionable.append({
                    "type": "issue",
                    "id": comment["id"],
                    "body": comment["body"],
                    "user": comment["user"]["login"],
                    "created_at": comment["created_at"]
                })
        
        return actionable
    
    def _is_actionable_comment(self, comment: Dict) -> bool:
        """Determine if a comment is actionable"""
        body = comment["body"].lower()
        user = comment["user"]["login"]
        
        # Skip bot comments
        if "bot" in user.lower():
            return False
            
        # Skip resolved comments
        if comment.get("resolved", False):
            return False
            
        # Skip very short comments (likely just reactions)
        if len(body.strip()) < 10:
            return False
            
        # Skip common non-actionable phrases
        non_actionable_phrases = [
            "lgtm", "looks good", "approved", "nice work", "great job",
            "thanks", "thank you", "+1", "👍", "✅"
        ]
        
        for phrase in non_actionable_phrases:
            if phrase in body:
                return False
        
        # Look for actionable keywords (expanded list)
        actionable_keywords = [
            "fix", "change", "update", "modify", "refactor", "improve",
            "should", "could", "need", "please", "consider", "suggestion",
            "bug", "issue", "problem", "error", "typo", "mistake",
            "why", "how", "what", "css", "style", "not working", "broken",
            "missing", "add", "remove", "delete", "incorrect", "wrong"
        ]
        
        # If comment contains actionable keywords, it's actionable
        has_actionable_keywords = any(keyword in body for keyword in actionable_keywords)
        
        # If comment is longer than 20 characters and doesn't contain non-actionable phrases,
        # consider it potentially actionable even without specific keywords
        is_substantial_comment = len(body.strip()) > 20
        
    
    def _group_comments_by_file(self, comments: List[Dict]) -> Dict[str, List[Dict]]:
        """Group comments by file path"""
        grouped = {}
        
        for comment in comments:
            if comment["type"] == "review" and comment.get("path"):
                file_path = comment["path"]
                if file_path not in grouped:
                    grouped[file_path] = []
                grouped[file_path].append(comment)
            elif comment["type"] == "issue":
                # General comments go to a special "general" category
                if "general" not in grouped:
                    grouped["general"] = []
                grouped["general"].append(comment)
        
        return grouped
    
    async def _handle_file_comments(self, sandbox, repo_path: str, file_path: str, 
                                  comments: List[Dict], repo_analysis: Dict) -> Dict[str, Any]:
        """Handle all comments for a specific file"""
        if file_path == "general":
            # Handle general PR comments
            return await self._handle_general_comments(sandbox, repo_path, comments, repo_analysis)
        
        # Handle file-specific comments
        full_file_path = Path(repo_path) / file_path
        
        if not full_file_path.exists():
            logger.warning(f"File {file_path} not found")
            return {"modified": False, "handled_comments": []}
        
        # Read current file content
        with open(full_file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Prepare context for LLM
        context = self._prepare_file_context(file_path, current_content, comments, repo_analysis)
        
        # Ask LLM to address the comments
        response = await self.llm_client.address_pr_comments(context)
        
        if response.get("modified", False) and response.get("new_content"):
            # Write the modified content
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(response["new_content"])
            
            return {
                "modified": True,
                "handled_comments": response.get("handled_comments", [])
            }
        
        return {"modified": False, "handled_comments": []}
    
    async def _handle_general_comments(self, sandbox, repo_path: str, 
                                     comments: List[Dict], repo_analysis: Dict) -> Dict[str, Any]:
        """Handle general PR comments that don't target specific files"""
        # For general comments, we need to understand what files they might affect
        context = f"""
        Repository Analysis: {self._format_repo_analysis(repo_analysis)}
        
        General PR Comments to Address:
        {self._format_comments_for_llm(comments)}
        
        Please analyze these general comments and determine what files need to be modified.
        Provide specific file changes to address the feedback.
        """
        
        response = await self.llm_client.address_general_pr_comments(context)
        
        modified_files = []
        handled_comments = []
        
        # Apply file changes suggested by LLM
        for file_change in response.get("file_changes", []):
            file_path = file_change["path"]
            new_content = file_change["content"]
            
            full_path = Path(repo_path) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            modified_files.append(file_path)
        
        if modified_files:
            handled_comments = response.get("handled_comments", [])
        
        return {
            "modified": len(modified_files) > 0,
            "handled_comments": handled_comments
        }
    
    def _prepare_file_context(self, file_path: str, content: str, 
                            comments: List[Dict], repo_analysis: Dict) -> str:
        """Prepare context for LLM to address file comments"""
        comments_text = self._format_comments_for_llm(comments)
        
        return f"""
        File: {file_path}
        Repository Type: {repo_analysis.get('primary_language', 'Unknown')}
        Frameworks: {', '.join(repo_analysis.get('frameworks', []))}
        
        Current File Content:
        ```
        {content}
        ```
        
        Comments to Address:
        {comments_text}
        
        Please modify the file content to address all the comments.
        Maintain the existing code style and structure.
        Only make necessary changes to address the feedback.
        """
    
    def _format_comments_for_llm(self, comments: List[Dict]) -> str:
        """Format comments for LLM consumption"""
        formatted = []
        
        for i, comment in enumerate(comments, 1):
            comment_text = f"{i}. {comment['user']} commented:\n"
            comment_text += f"   {comment['body']}\n"
            
            if comment.get('line'):
                comment_text += f"   (Line {comment['line']})\n"
            
            if comment.get('diff_hunk'):
                comment_text += f"   Context: {comment['diff_hunk'][:200]}...\n"
            
            formatted.append(comment_text)
        
        return "\n".join(formatted)
    
    def _format_repo_analysis(self, analysis: Dict) -> str:
        """Format repository analysis for LLM"""
        return f"""
        Primary Language: {analysis.get('primary_language', 'Unknown')}
        Frameworks: {', '.join(analysis.get('frameworks', []))}
        Build Tools: {', '.join(analysis.get('build_tools', []))}
        Entry Points: {', '.join(analysis.get('entry_points', []))}
        """
    
    def _generate_summary(self, handled_comments: List[Dict], commits: List[str], 
                         files_modified: List[str], unresolved: List[Dict]) -> str:
        """Generate a summary of the comment handling session"""
        summary = f"""
## PR Comment Handling Summary

### ✅ Successfully Handled
- **Comments Addressed**: {len(handled_comments)}
- **Commits Made**: {len(commits)}
- **Files Modified**: {len(files_modified)}

### 📝 Files Changed:
{chr(10).join(f"- {file}" for file in files_modified)}

### 💬 Comments Addressed:
{chr(10).join(f"- {comment.get('summary', comment.get('body', '')[:100])}..." for comment in handled_comments[:5])}

### ⚠️ Unresolved Comments: {len(unresolved)}
{chr(10).join(f"- {comment.get('body', '')[:100]}..." for comment in unresolved[:3]) if unresolved else "None"}

### 🔗 Commits:
{chr(10).join(f"- {commit[:8]}" for commit in commits)}
        """
        
        return summary.strip()
    
    def _sanitize_comment(self, comment: Dict) -> Dict[str, Any]:
        """Sanitize comment for response"""
        return {
            "body": comment.get("body", ""),
            "user": comment.get("user", ""),
            "line": comment.get("line"),
            "path": comment.get("path")
        }