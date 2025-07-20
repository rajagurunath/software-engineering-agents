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
from services.developer.code_analyzer import CodeAnalyzer
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
        logger.info(f"Fetched PR details for {owner}/{repo}#{pr_number}")
        trace("pr_comment_handler.fetched_details", {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "review_comments_count": len(review_comments),
            "issue_comments_count": len(issue_comments)
        })
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
                        
                        # Reply to each handled comment and mark as resolved
                        for i, comment in enumerate(result["handled_comments"]):
                            try:
                                # Reply to the specific comment
                                await self._reply_to_individual_comment(
                                    owner, repo, pr_number, comment, file_comments[i]
                                )
                            except Exception as e:
                                logger.warning(f"Failed to reply/resolve comment {comment.get('id')}: {e}")
                    else:
                        unresolved_comments.extend(file_comments)
                        
                except Exception as e:
                    logger.error(f"Failed to handle comments for {file_path}: {e}")
                    unresolved_comments.extend(file_comments)
            
            # Handle general comments separately
            if "general" in comments_by_file:
                try:
                    result = await self._handle_general_comments(
                        sandbox, repo_path, comments_by_file["general"], repo_analysis
                    )
                    
                    if result["modified"]:
                        # Commit changes for general comments
                        commit_message = "Address general PR feedback\n\n" + \
                                       "\n".join([f"- {c['summary']}" for c in result["handled_comments"]])
                        
                        commit_sha = sandbox.commit_changes(commit_message)
                        commits_made.append(commit_sha)
                        handled_comments.extend(result["handled_comments"])
                        
                        # Reply to each general comment
                        for i, comment in enumerate(result["handled_comments"]):
                            try:
                                await self._reply_to_individual_comment(
                                    owner, repo, pr_number, comment, comments_by_file["general"][i]
                                )
                            except Exception as e:
                                logger.warning(f"Failed to reply to general comment: {e}")
                    else:
                        unresolved_comments.extend(comments_by_file["general"])
                        
                except Exception as e:
                    logger.error(f"Failed to handle general comments: {e}")
                    unresolved_comments.extend(comments_by_file["general"])
            
            # Push all changes
            if commits_made:
                sandbox.push_branch(pr_branch)
                
            # Post summary comment to GitHub PR
            if handled_comments or commits_made:
                await self._post_github_summary_comment(
                    owner, repo, pr_number, handled_comments, commits_made, 
                    files_modified, unresolved_comments
                )
                
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
                "commits_made": len(commits_made),
                "github_summary_posted": len(handled_comments) > 0 or len(commits_made) > 0
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
        logger.info(f"Filtering actionable comments from {len(review_comments)} review comments and {len(issue_comments)} issue comments...")
        # Process review comments (line-specific)
        for comment in review_comments:
            if self._is_actionable_comment(comment):
                logger.info(f"Adding actionable review comment from {comment['user']['login']}: {comment['body'][:50]}...")
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
            logger.debug(f"Processing issue comment: {comment['body'][:50]}...")
            if self._is_actionable_comment(comment):
                logger.info(f"Adding actionable issue comment from {comment['user']['login']}: {comment['body'][:50]}...")
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
        return has_actionable_keywords or is_substantial_comment
        
    
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
    
    async def _reply_to_individual_comment(self, owner: str, repo: str, pr_number: int,
                                         handled_comment: Dict, original_comment: Dict) -> None:
        """Reply to an individual comment with details of how it was addressed"""
        try:
            # Create a personalized reply
            user = original_comment.get("user", "")
            summary = handled_comment.get("summary", "Your comment has been addressed")
            
            if original_comment["type"] == "review":
                # For review comments (line-specific), reply directly
                reply_body = f"@{user} ✅ **Comment Addressed**\n\n{summary}\n\n*This change was automatically implemented by the PR Comment Handler bot.*"
                reply_body += f"\n\n**Please review the changes and resolve this comment if you're satisfied with the implementation.**"
                
                await self.github_client.reply_to_review_comment(
                    owner, repo, pr_number, original_comment["id"], reply_body
                )
                logger.info(f"Replied to review comment {original_comment['id']} by {user}")
                
            elif original_comment["type"] == "issue":
                # For general issue comments, create a new comment mentioning the user
                reply_body = f"@{user} ✅ **Your comment has been addressed**\n\n> {original_comment['body'][:100]}{'...' if len(original_comment['body']) > 100 else ''}\n\n{summary}\n\n*This change was automatically implemented by the PR Comment Handler bot.*"
                reply_body += f"\n\n**Please review the changes and resolve this comment if you're satisfied with the implementation.**"
                
                await self.github_client.reply_to_issue_comment(
                    owner, repo, pr_number, reply_body
                )
                logger.info(f"Replied to issue comment by {user}")
                
        except Exception as e:
            logger.error(f"Failed to reply to comment: {e}")
    
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
    
    async def _post_github_summary_comment(self, owner: str, repo: str, pr_number: int,
                                         handled_comments: List[Dict], commits: List[str],
                                         files_modified: List[str], unresolved: List[Dict]) -> None:
        """Post a summary comment to the GitHub PR"""
        try:
            # Create a comprehensive summary comment
            comment_body = self._generate_github_comment_body(
                handled_comments, commits, files_modified, unresolved
            )
            
            # Post the comment to GitHub
            await self.github_client.add_pr_comment(owner, repo, pr_number, comment_body)
            logger.info(f"Posted summary comment to PR #{pr_number}")
            
        except Exception as e:
            logger.error(f"Failed to post summary comment to GitHub PR: {e}")
    
    def _generate_github_comment_body(self, handled_comments: List[Dict], commits: List[str],
                                    files_modified: List[str], unresolved: List[Dict]) -> str:
        """Generate the GitHub comment body with summary"""
        
        # Header with bot identification
        comment_body = "## 🤖 Automated Comment Resolution\n\n"
        comment_body += f"I've automatically addressed **{len(handled_comments)}** review comments. Here's what I did:\n\n"
        
        # Summary stats
        comment_body += "### 📊 Summary\n"
        comment_body += f"- **Comments Addressed**: {len(handled_comments)}\n"
        comment_body += f"- **Files Modified**: {len(files_modified)}\n"
        comment_body += f"- **Commits Made**: {len(commits)}\n"
        
        if unresolved:
            comment_body += f"- **Unresolved Comments**: {len(unresolved)}\n"
        
        comment_body += "\n"
        
        # Files changed section
        if files_modified:
            comment_body += "### 📝 Files Modified\n"
            for file_path in files_modified:
                comment_body += f"- `{file_path}`\n"
            comment_body += "\n"
        
        # Detailed changes section
        if handled_comments:
            comment_body += "### ✅ Comments Addressed\n"
            for i, comment in enumerate(handled_comments[:10], 1):  # Limit to first 10
                summary = comment.get('summary', 'Comment addressed')
                comment_body += f"{i}. {summary}\n"
            
            if len(handled_comments) > 10:
                comment_body += f"... and {len(handled_comments) - 10} more comments\n"
            comment_body += "\n"
        
        # Commits section
        if commits:
            comment_body += "### 🔗 Commits Made\n"
            for commit in commits:
                short_sha = commit[:8] if len(commit) > 8 else commit
                comment_body += f"- [`{short_sha}`](../../commit/{commit})\n"
            comment_body += "\n"
        
        # Unresolved comments section
        if unresolved:
            comment_body += "### ⚠️ Unresolved Comments\n"
            comment_body += f"I couldn't automatically address {len(unresolved)} comment(s). These may require manual review:\n\n"
            
            for i, comment in enumerate(unresolved[:5], 1):  # Show first 5 unresolved
                body_preview = comment.get('body', '')[:100]
                if len(comment.get('body', '')) > 100:
                    body_preview += "..."
                comment_body += f"{i}. {body_preview}\n"
            
            if len(unresolved) > 5:
                comment_body += f"... and {len(unresolved) - 5} more unresolved comments\n"
            comment_body += "\n"
        
        # Footer
        comment_body += "---\n"
        comment_body += "*This comment was automatically generated by the PR Comment Handler bot. "
        comment_body += "Please review the changes and let me know if any adjustments are needed.*"
        
        return comment_body
    
    def _sanitize_comment(self, comment: Dict) -> Dict[str, Any]:
        """Sanitize comment for response"""
        return {
            "body": comment.get("body", ""),
            "user": comment.get("user", ""),
            "line": comment.get("line"),
            "path": comment.get("path")
        }