import asyncio
from typing import Dict, List, Any,Optional
from core.integrations.github_client import GitHubClient
from core.integrations.linear_client import LinearClient
from core.integrations.llm_client import LLMClient
from models.schemas import PRReviewRequest, PRReviewResponse
import logging

logger = logging.getLogger(__name__)

class PRReviewService:
    def __init__(self):
        self.github_client = GitHubClient()
        self.linear_client = LinearClient()
        self.llm_client = LLMClient()
        
    async def review_pr(self, request: PRReviewRequest) -> PRReviewResponse:
        """Comprehensive PR review"""
        logger.info(f"Starting PR review for: {request.pr_url}")
        
        # Parse PR URL to get owner, repo, and PR number
        owner, repo, pr_number = self._parse_pr_url(request.pr_url)
        
        # Gather PR information
        pr_details, pr_diff, pr_files, linear_context = await asyncio.gather(
            self.github_client.get_pr_details(owner, repo, pr_number),
            self.github_client.get_pr_diff(owner, repo, pr_number),
            self.github_client.get_pr_files(owner, repo, pr_number),
            self._get_linear_context(request.linear_issue_id) if request.linear_issue_id else asyncio.sleep(0, result=None)
        )
        
        # Get CI status
        ci_status = await self.github_client.get_ci_status(
            owner, repo, pr_details["head"]["sha"]
        )
        
        # Perform code quality analysis
        quality_analysis = await self._analyze_code_quality(pr_diff, pr_files)
        
        # Find potential bugs
        bugs_found = await self._find_bugs(pr_diff, pr_files)
        
        # Check test coverage
        test_coverage = await self._check_test_coverage(pr_files)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            pr_details, pr_diff, quality_analysis, bugs_found, linear_context
        )

        # Build review summary text
        review_summary = await self._generate_review_summary(
            pr_details, quality_analysis, bugs_found, ci_status
        )

        # Post review as a comment to the PR
        try:
            comment_body = (
                "## 🔍 Automated PR Review\n\n"
                f"{review_summary}\n\n"
                "### Recommendations\n" + "\n".join(f"- {rec}" for rec in recommendations)
            )
            await self.github_client.add_pr_comment(owner, repo, pr_number, comment_body)
        except Exception as e:
            logger.warning(f"Failed to add PR comment: {e}")
        
        return PRReviewResponse(
            pr_url=request.pr_url,
            review_summary=review_summary,
            code_quality_score=quality_analysis["overall_score"],
            bugs_found=bugs_found,
            test_coverage_issues=test_coverage,
            ci_status=ci_status["state"],
            recommendations=recommendations,
            linear_context=linear_context
        )
        
    def _parse_pr_url(self, pr_url: str) -> tuple:
        """Parse GitHub PR URL to extract owner, repo, and PR number"""
        # Example: https://github.com/owner/repo/pull/123
        parts = pr_url.split("/")
        owner = parts[3]
        repo = parts[4]
        pr_number = int(parts[6])
        return owner, repo, pr_number
        
    async def _get_linear_context(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get Linear issue context"""
        if not issue_id:
            return None
        return await self.linear_client.get_issue_details(issue_id)
        
    async def _analyze_code_quality(self, diff: str, files: List[Dict]) -> Dict[str, Any]:
        """Analyze code quality using LLM"""
        prompt = f"""
        Analyze the following code diff for quality issues:
        
        {diff}
        
        Please provide:
        1. Overall quality score (1-10)
        2. Specific issues found
        3. Code style violations
        4. Complexity concerns
        5. Performance issues
        
        Files changed: {len(files)}
        """
        
        analysis = await self.llm_client.analyze_code(prompt)
        return {
            "overall_score": analysis.get("score", 7),
            "issues": analysis.get("issues", []),
            "style_violations": analysis.get("style_violations", []),
            "complexity_issues": analysis.get("complexity_issues", []),
            "performance_issues": analysis.get("performance_issues", [])
        }
        
    async def _find_bugs(self, diff: str, files: List[Dict]) -> List[str]:
        """Find potential bugs in the code"""
        prompt = f"""
        Review the following code diff for potential bugs:
        
        {diff}
        
        Focus on:
        1. Logic errors
        2. Null pointer exceptions
        3. Memory leaks
        4. Race conditions
        5. Error handling issues
        
        Return a list of potential bugs with line numbers where possible.
        """
        
        bugs = await self.llm_client.find_bugs(prompt)
        return bugs.get("bugs", [])
        
    async def _check_test_coverage(self, files: List[Dict]) -> List[str]:
        """Check for test coverage issues"""
        test_files = [f for f in files if "test" in f["filename"].lower()]
        source_files = [f for f in files if "test" not in f["filename"].lower()]
        
        issues = []
        
        if not test_files and source_files:
            issues.append("No test files found for code changes")
            
        if len(test_files) < len(source_files) * 0.5:
            issues.append("Test coverage appears low compared to source changes")
            
        return issues
        
    async def _generate_recommendations(self, pr_details: Dict, diff: str, 
                                      quality_analysis: Dict, bugs: List[str],
                                      linear_context: Optional[Dict]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Code quality recommendations
        if quality_analysis["overall_score"] < 7:
            recommendations.append("Consider refactoring to improve code quality")
            
        # Bug fix recommendations
        if bugs:
            recommendations.append("Address the potential bugs identified")
            
        # Linear context recommendations
        if linear_context:
            recommendations.append(f"Ensure changes align with Linear issue: {linear_context.get('title', '')}")
            
        return recommendations
        
    async def _generate_review_summary(self, pr_details: Dict, quality_analysis: Dict,
                                     bugs: List[str], ci_status: Dict) -> str:
        """Generate comprehensive review summary"""
        summary = f"""
        ## PR Review Summary
        
        **PR Title**: {pr_details['title']}
        **Author**: {pr_details['user']['login']}
        **Changes**: {pr_details['additions']} additions, {pr_details['deletions']} deletions
        
        **Code Quality Score**: {quality_analysis['overall_score']}/10
        **Bugs Found**: {len(bugs)}
        **CI Status**: {ci_status['state']}
        
        ### Key Findings:
        {chr(10).join(f"- {issue}" for issue in quality_analysis['issues'][:3])}
        
        ### Recommendations:
        - Review and address identified issues
        - Ensure adequate test coverage
        - Consider code style improvements
        """
        
        return summary