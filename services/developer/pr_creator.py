# services/pr_creator.py
import asyncio
import uuid
from typing import Optional, Dict, Any,List
from pathlib import Path
from slack_sdk import WebClient
from utils.opik_tracer import trace
from core.sandbox import SandboxManager
from core.integrations.github_client import GitHubClient
from core.integrations.linear_client import LinearClient
from core.integrations.llm_client import LLMClient
from models.schemas import PRCreationRequest, PRCreationResponse
from models.schemas import TrivyScanRequest, TrivyScanResponse, TrivyFinding, TrivyFixChange
from services.developer.code_analyzer import CodeAnalyzer
import logging

logger = logging.getLogger(__name__)

class PRCreatorService:
    def __init__(self):
        self.sandbox_manager = SandboxManager()
        self.github_client = GitHubClient()
        self.linear_client = LinearClient()
        self.llm_client = LLMClient()
        self.code_analyzer = CodeAnalyzer()
        
    async def create_pr(self, request: PRCreationRequest) -> PRCreationResponse:
        """Create PR in sandbox environment"""
        logger.info(f"Starting PR creation for: {request.description}")
        trace("pr_creator.start", {"description": request.description, "repo": request.repo_url})
        
        sandbox_id = f"pr-{uuid.uuid4().hex[:8]}"
        
        # Get Linear context if available
        linear_context = None
        if request.linear_issue_id:
            try:
                linear_context = await self.linear_client.get_issue_details(request.linear_issue_id)
            except Exception as e:
                logger.warning(f"Failed to fetch Linear context: {e}")
            
        with self.sandbox_manager.get_sandbox(sandbox_id) as sandbox:
            # Clone repository and checkout base branch
            repo_path = sandbox.clone_repo(request.repo_url, request.base_branch)
            
            # Create feature branch from base branch
            sandbox.create_branch(request.branch_name)
            
            # Clarification step
            from config.settings import settings
            if (not settings.skip_clarifications) and not request.clarification_questions:
                clarifications = await self._get_clarifications(
                    request.description, linear_context
                )
                return PRCreationResponse(
                    pr_url="",
                    branch_name=request.branch_name,
                    commits=[],
                    test_results={},
                    files_changed=[],
                    clarification_questions=clarifications
                )
            
            # Generate implementation plan
            implementation_plan = await self._generate_implementation_plan(
                request, linear_context, repo_path
            )
            
            # Share plan to Slack if configured
            from config.settings import settings
            if settings.share_plan_to_slack and request.thread_id:
                await self._post_plan_to_slack(request, implementation_plan)

            # Implement changes
            changes_made = await self._implement_changes(
                sandbox, implementation_plan, repo_path
            )
            
            # Run tests
            test_results = sandbox.run_tests()
            
            # If tests fail, attempt to fix
            if not self._tests_passed(test_results):
                try:
                    fix_attempts = await self._fix_test_failures(
                        sandbox, test_results, changes_made
                    )
                    # Re-run tests after fixes
                    if fix_attempts.get("fixes"):
                        test_results = sandbox.run_tests()
                        trace("pr_creator.tests_rerun", {"fixes_applied": len(fix_attempts["fixes"])})
                except Exception as e:
                    logger.error(f"Failed to fix test failures: {e}")
                    trace("pr_creator.fix_tests_error", {"error": str(e)})
                    # Continue with original test results
                
            # Commit changes
            commit_message = f"feat: {request.description}"
            if linear_context:
                commit_message += f" (Linear: {linear_context['title']})"
                
            commit_sha = sandbox.commit_changes(commit_message)
            
            # Push branch
            sandbox.push_branch(request.branch_name)
            
            # Create PR
            owner, repo = self._parse_repo_url(request.repo_url)
            pr_response = await self.github_client.create_pr(
                owner=owner,
                repo=repo,
                title=f"feat: {request.description}",
                body=self._generate_pr_body(request, linear_context, changes_made),
                head=request.branch_name,
                base=request.base_branch
            )
            
            result = PRCreationResponse(
                pr_url=pr_response["html_url"],
                branch_name=request.branch_name,
                commits=[commit_sha],
                test_results=test_results,
                files_changed=changes_made["files_changed"]
            )
            trace("pr_creator.finish", {"pr_url": result.pr_url, "files_changed": len(result.files_changed)})
            return result

    async def create_trivy_pr(self, request: TrivyScanRequest) -> TrivyScanResponse:
        """
        Take Trivy logs, analyze repository, generate a concrete plan of edits (e.g. requirements.txt upgrades,
        Dockerfile base image updates, config hardening), apply changes, run tests, and open a PR.
        """
        logger.info("Starting Trivy vulnerability PR creation")
        trace("trivy_pr_creator.start", {"repo": request.repo_url})

        # Derive a branch name if not provided
        branch_name = request.branch_name or f"security/trivy-fixes-{uuid.uuid4().hex[:6]}"
        description = request.description or "Fix security vulnerabilities reported by Trivy"

        sandbox_id = f"trivy-{uuid.uuid4().hex[:8]}"
        with self.sandbox_manager.get_sandbox(sandbox_id) as sandbox:
            # Clone repository and checkout base branch
            repo_path = sandbox.clone_repo(request.repo_url, request.base_branch)

            # Create branch
            sandbox.create_branch(branch_name)

            # Analyze repo for context
            repo_analysis = self.code_analyzer.analyze_repository(repo_path)
            code_context = self.code_analyzer.get_code_context(repo_path)

            # Parse Trivy logs (raw or json)
            findings = await self._parse_trivy_logs(request.trivy_raw_logs, request.trivy_json)

            # Build LLM prompt to create a concrete plan of file changes
            plan_prompt = self._build_trivy_fix_plan_prompt(description, findings, repo_analysis, code_context)
            plan = await self.llm_client.generate_implementation_plan(plan_prompt)

            # Ensure plan is normalized into list of file_changes compatible with _implement_changes
            normalized_plan = self._normalize_trivy_plan(plan)

            # Implement changes
            changes_made = await self._implement_changes(sandbox, normalized_plan, repo_path)

            # If uv-based repo, update lockfile and sync environment before tests
            if self._uses_uv(repo_path):
                chk = sandbox.run_command("uv --version")
                if chk.returncode == 0:
                    sandbox.run_command("uv lock")
                    sandbox.run_command("uv sync")
                else:
                    logger.warning("uv detected in repo but 'uv' CLI not found in sandbox; skipping uv sync")

            # Run tests if any test tool exists in repo
            test_results = sandbox.run_tests()

            # Commit changes
            commit_msg = self._generate_trivy_commit_message(findings, description)
            commit_sha = sandbox.commit_changes(commit_msg)

            # Push and open PR
            sandbox.push_branch(branch_name)
            owner, repo = self._parse_repo_url(request.repo_url)
            pr_body = self._generate_trivy_pr_body(description, findings, changes_made, normalized_plan)
            pr_response = await self.github_client.create_pr(
                owner=owner,
                repo=repo,
                title=f"chore(security): {description}",
                body=pr_body,
                head=branch_name,
                base=request.base_branch
            )

            # Build response
            unresolved = self._compute_unresolved_findings(findings, normalized_plan)
            return TrivyScanResponse(
                pr_url=pr_response["html_url"],
                branch_name=branch_name,
                commits=[commit_sha],
                files_changed=changes_made.get("files_changed", []),
                fixes_applied=[
                    TrivyFixChange(path=fc["path"], type=fc["type"], content=fc["content"], reasoning=fc.get("reasoning"))
                    for fc in normalized_plan.get("file_changes", [])
                ],
                unresolved_findings=unresolved,
                summary=f"Opened PR to address {len(findings)} findings; changed {len(changes_made.get('files_changed', []))} files."
            )

    async def _parse_trivy_logs(self, raw_logs: str, json_obj: Optional[Dict[str, Any]]) -> List[TrivyFinding]:
        """
        Parse Trivy output either from structured JSON or heuristics on raw text.
        Focus on Python/library and config/Dockerfile findings that can be auto-remediated.
        """
        parsed: List[TrivyFinding] = []

        # Prefer JSON if provided
        if json_obj:
            try:
                # Trivy JSON schema summary:
                # Results[].Vulnerabilities[] with fields: VulnerabilityID, PkgName, InstalledVersion, FixedVersion, Severity, PrimaryURL
                results = json_obj.get("Results", [])
                for r in results:
                    target = r.get("Target")
                    cls = r.get("Class") or r.get("Type")  # e.g., os-pkgs, lang-pkgs, config, secret
                    # Vulnerabilities (packages)
                    vulns = r.get("Vulnerabilities") or []
                    for v in vulns:
                        refs = []
                        if v.get("PrimaryURL"):
                            refs.append(v["PrimaryURL"])
                        vrefs = v.get("References")
                        if isinstance(vrefs, list):
                            refs.extend([x for x in vrefs if isinstance(x, str)])
                        pkg_path = v.get("PkgPath") or target
                        parsed.append(TrivyFinding(
                            id=v.get("VulnerabilityID", "") or v.get("VulnID", ""),
                            severity=v.get("Severity", "UNKNOWN"),
                            title=v.get("Title"),
                            description=v.get("Description"),
                            package_name=v.get("PkgName"),
                            current_version=v.get("InstalledVersion"),
                            fixed_version=v.get("FixedVersion"),
                            installed_path=pkg_path,
                            references=refs,
                            type=cls or "library",
                            target=target
                        ))
                    # Misconfigurations (e.g., IaC/config findings)
                    misconfs = r.get("Misconfigurations") or []
                    for m in misconfs:
                        refs = []
                        refs_raw = m.get("References")
                        if isinstance(refs_raw, list):
                            for ref in refs_raw:
                                if isinstance(ref, dict) and ref.get("URL"):
                                    refs.append(ref["URL"])
                                elif isinstance(ref, str):
                                    refs.append(ref)
                        parsed.append(TrivyFinding(
                            id=m.get("ID") or m.get("RuleID") or (m.get("Title") or "MISCONFIG"),
                            severity=m.get("Severity", "UNKNOWN"),
                            title=m.get("Title"),
                            description=m.get("Description") or m.get("Message"),
                            package_name=None,
                            current_version=None,
                            fixed_version=None,
                            installed_path=target,
                            references=refs,
                            type="misconfiguration",
                            target=target
                        ))
                    # Secrets
                    secrets = r.get("Secrets") or []
                    for s in secrets:
                        parsed.append(TrivyFinding(
                            id=s.get("RuleID") or "SECRET",
                            severity=s.get("Severity", "UNKNOWN"),
                            title=s.get("Title"),
                            description=s.get("Description") or s.get("Match") or "",
                            package_name=s.get("Category"),
                            current_version=None,
                            fixed_version=None,
                            installed_path=target,
                            references=[],
                            type="secret",
                            target=target
                        ))
            except Exception as e:
                logger.warning(f"Failed to parse provided Trivy JSON: {e}")

        # Heuristic parse raw logs when JSON not available
        if not parsed and raw_logs:
            import re
            # Common patterns like:
            # "CVE-2023-12345 HIGH some-lib 1.2.3 fixed in 1.2.5 (path: requirements.txt)"
            pat = re.compile(
                r'(?P<id>CVE-\d{4}-\d+)\s+(?P<sev>CRITICAL|HIGH|MEDIUM|LOW|UNKNOWN)\s+(?P<pkg>[A-Za-z0-9._\-]+)\s+(?P<curr>[0-9a-zA-Z\.\-\+]+)\s+(?:fixed\s+in\s+(?P<fix>[0-9a-zA-Z\.\-\+]+))?.*?(?:path:\s*(?P<path>[^\s]+))?',
                re.IGNORECASE
            )
            for m in pat.finditer(raw_logs):
                parsed.append(TrivyFinding(
                    id=m.group("id"),
                    severity=m.group("sev").upper(),
                    package_name=m.group("pkg"),
                    current_version=m.group("curr"),
                    fixed_version=(m.group("fix") or None),
                    installed_path=(m.group("path") or None),
                    references=[],
                    type="library"
                ))

            # Basic Dockerfile base image detection
            docker_pat = re.compile(r'(CVE-\d{4}-\d+).*(?i)(alpine|debian|ubuntu).*?(?i)fixed\s+in\s+([0-9a-zA-Z\.\-\:_]+)')
            for m in docker_pat.finditer(raw_logs):
                parsed.append(TrivyFinding(
                    id=m.group(1),
                    severity="UNKNOWN",
                    package_name=m.group(2),
                    fixed_version=m.group(3),
                    type="os-pkgs",
                    installed_path="Dockerfile",
                ))

        return parsed

    def _build_trivy_fix_plan_prompt(self, description: str, findings: List[TrivyFinding], repo_analysis: Dict[str, Any], code_context: str) -> str:
        deps = []
        for f in findings:
            if f.package_name and (f.fixed_version or f.current_version):
                deps.append(f"{f.package_name} {f.current_version or ''} -> {f.fixed_version or 'latest secure'}")
        deps_text = "\n".join(f"- {d}" for d in deps) or "- None"

        misconfs = []
        for f in findings:
            if f.type == "misconfiguration":
                title = f.title or f.id
                loc = f.installed_path or f.target or ""
                misconfs.append(f"{title} at {loc} [{f.severity}]")
        mis_text = "\n".join(f"- {m}" for m in misconfs) or "- None"

        secrets_list = []
        for f in findings:
            if f.type == "secret":
                title = f.title or f.id
                loc = f.installed_path or f.target or ""
                secrets_list.append(f"{title} at {loc} [{f.severity}]")
        secrets_text = "\n".join(f"- {s}" for s in secrets_list) or "- None"

        context = f"""
TASK: {description}

REPOSITORY ANALYSIS:
Primary Language: {repo_analysis.get('primary_language')}
Frameworks: {', '.join(repo_analysis.get('frameworks', []))}
Test Frameworks: {', '.join(repo_analysis.get('test_frameworks', []))}
Entry Points: {', '.join(repo_analysis.get('entry_points', []))}

CODE CONTEXT (trimmed):
{code_context[:4000]}
"""

        prompt = f"""You are a senior security engineer. Given Trivy vulnerability findings and the repository context,
produce a concrete remediation plan as JSON with the following schema:

{{
  "summary": "High-level summary of changes",
  "file_changes": [
    {{
      "path": "relative/path",
      "type": "modify|create|delete",
      "content": "FULL desired file content after change",
      "reasoning": "why this change fixes the issue"
    }}
  ],
  "dependencies": []
}}

Rules:
- Prefer updating Python dependencies in requirements.txt or constraints files.
- If the repository uses uv (pyproject.toml and/or uv.lock present), update dependencies in pyproject.toml instead of requirements.txt. Do NOT include uv.lock in file_changes; it will be regenerated by 'uv lock'.
- Keep other versions pinned; bump minimally to secure fixed_version where provided.
- If Dockerfile base image needs update, update FROM to a patched tag and justify.
- Address misconfigurations by updating configuration files (Dockerfile, YAML, TOML, JSON). Explain the hardened setting in comments.
- Do NOT commit secrets. Replace plaintext secrets with environment variables or placeholders and document changes in the PR body.
- Add inline comments in content to explain changes when appropriate.
- Preserve existing formatting and non-security content.
- Only include files that exist or make sense for this repo type.

Findings to address (dependencies):
{deps_text}

Misconfigurations to address:
{mis_text}

Secrets to address:
{secrets_text}

{context}
"""
        return prompt

    def _normalize_trivy_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure needed keys exist
        file_changes = plan.get("file_changes", [])
        normalized = {"file_changes": []}
        for fc in file_changes:
            path = fc.get("path")
            ctype = fc.get("type", "modify")
            content = fc.get("content", "")
            reasoning = fc.get("reasoning")
            if path and content is not None:
                normalized["file_changes"].append({
                    "path": path,
                    "type": ctype,
                    "content": content,
                    "reasoning": reasoning
                })
        # surface dependencies array even if unused
        normalized["dependencies"] = plan.get("dependencies", [])
        normalized["summary"] = plan.get("summary", "")
        return normalized

    def _generate_trivy_commit_message(self, findings: List[TrivyFinding], description: str) -> str:
        sev_counts: Dict[str, int] = {}
        for f in findings:
            sev_counts[f.severity] = sev_counts.get(f.severity, 0) + 1
        sev_summary = ", ".join(f"{k}:{v}" for k, v in sorted(sev_counts.items(), reverse=True))
        return f"chore(security): {description} [{sev_summary}]"

    def _generate_trivy_pr_body(self, description: str, findings: List[TrivyFinding], changes_made: Dict[str, Any], plan: Dict[str, Any]) -> str:
        files_changed = "\n".join(f"- {p}" for p in changes_made.get("files_changed", []))
        created = "\n".join(f"- {p}" for p in changes_made.get("files_created", []))
        summary = plan.get("summary", "")
        finding_lines = []
        for f in findings[:50]:
            finding_lines.append(f"- {f.id} [{f.severity}] {f.package_name or ''} {f.current_version or ''} -> {f.fixed_version or 'patched'} ({f.installed_path or f.target or ''})")
        findings_md = "\n".join(finding_lines)

        body = f"""
## Security Remediation PR
{description}

### Summary
{summary}

### Changes
- Files Modified: {len(changes_made.get('files_changed', []))}
- Files Created: {len(changes_made.get('files_created', []))}

#### Files Modified:
{files_changed or '- None'}

#### Files Created:
{created or '- None'}

### Trivy Findings Addressed
{findings_md}
"""
        return body

    def _compute_unresolved_findings(self, findings: List[TrivyFinding], plan: Dict[str, Any]) -> List[TrivyFinding]:
        # Heuristic: if a planned change targets the same file/area as the finding, consider it resolved.
        planned_paths = {fc.get("path", "") for fc in plan.get("file_changes", [])}

        def is_resolved(f: TrivyFinding) -> bool:
            inst = (f.installed_path or f.target or "") or ""
            inst_lower = inst.lower()
            for p in planned_paths:
                p_lower = (p or "").lower()
                if not p_lower:
                    continue
                # Direct path match or containment
                if p_lower in inst_lower or inst_lower in p_lower:
                    return True
                # requirements.txt change likely addresses library vulns
                if "requirements" in p_lower and (f.type in ("library", "lang-pkgs") or (f.package_name or "")):
                    return True
                # Dockerfile changes likely address os-pkgs and base image issues
                if "dockerfile" in p_lower and (f.type in ("os-pkgs", "library") or "dockerfile" in inst_lower):
                    return True
            return False

        return [f for f in findings if not is_resolved(f)]
            
    async def _get_clarifications(self, description: str, 
                                linear_context: Optional[Dict]) -> List[str]:
        """Generate clarification questions"""
        context = f"Description: {description}\n"
        if linear_context:
            context += f"Linear Context: {linear_context.get('description', '')}\n"
            
        prompt = f"""
        Based on the following request, generate clarification questions:
        
        {context}
        
        Generate 3-5 specific questions that would help implement this feature correctly.
        """

        questions = await self.llm_client.generate_clarifications(prompt)
        return questions.get("questions", [])

    async def _post_plan_to_slack(self, request: PRCreationRequest, plan: Dict) -> None:
        """Post understanding, plan, and file list to Slack thread"""
        from config.settings import settings
        try:
            client = WebClient(token=settings.slack_bot_token)
            files = [fc["path"] for fc in plan.get("file_changes", [])]
            message = (
                f"*📝 Understanding:*\n{request.description}\n\n"
                f"*🛠 Implementation Plan:*\n{plan.get('summary', '')}\n\n"
                f"*📄 Files to be created/modified:*\n" + "\n".join(f"- {p}" for p in files)
            )
            client.chat_postMessage(channel=request.channel_id, text=message, thread_ts=request.thread_id)
        except Exception as e:
            logger.warning(f"Failed to post plan to Slack: {e}")

    async def _generate_implementation_plan(self, request: PRCreationRequest, linear_context: Optional[Dict], repo_path: str) -> Dict:
        """Generate detailed implementation plan"""
        trace("pr_creator.analyze_repo", {"repo_path": repo_path})
        
        # Perform comprehensive code analysis
        repo_analysis = self.code_analyzer.analyze_repository(repo_path)
        code_context = self.code_analyzer.get_code_context(repo_path)
        
        trace("pr_creator.repo_analysis", {
            "primary_language": repo_analysis['primary_language'],
            "frameworks": repo_analysis['frameworks'],
            "file_count": repo_analysis['file_count']
        })

        # Build comprehensive context for LLM
        context = f"""
        TASK: {request.description}
        
        REPOSITORY ANALYSIS:
        {self._format_repo_analysis(repo_analysis)}
        
        CODE CONTEXT:
        {code_context}
        """
        
        if linear_context:
            context += f"\nLINEAR ISSUE CONTEXT:\n"
            context += f"Title: {linear_context.get('title', '')}\n"
            context += f"Description: {linear_context.get('description', '')}\n"
            
        prompt = f"""You are a senior software engineer. Create a detailed implementation plan based on the repository analysis and task requirements.
        
        {context}
        
        IMPORTANT REQUIREMENTS:
        1. Use the CORRECT programming language and framework identified in the analysis
        2. Follow the existing code patterns and structure
        3. Respect the project's architecture and conventions
        4. Only suggest changes that make sense for this technology stack
        
        Provide a JSON response with:
        {{
            "summary": "Brief description of the implementation approach",
            "file_changes": [
                {{
                    "path": "relative/path/to/file",
                    "type": "create|modify|delete",
                    "content": "actual file content",
                    "reasoning": "why this change is needed"
                }}
            ],
            "test_files": [
                {{
                    "path": "path/to/test/file",
                    "content": "test file content",
                    "framework": "testing framework to use"
                }}
            ],
            "dependencies": [
                {{
                    "name": "dependency-name",
                    "version": "version",
                    "type": "production|development"
                }}
            ]
        }}
        """
        
        trace("pr_creator.generate_plan", {"description": request.description})
        plan = await self.llm_client.generate_implementation_plan(prompt)
        trace("pr_creator.plan_generated", {"files_to_change": len(plan.get("file_changes", []))})
        
        return plan
    
    def _format_repo_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format repository analysis for LLM context."""
        return f"""
Primary Language: {analysis['primary_language']}
All Languages: {', '.join(analysis['languages'].keys())}
Frameworks: {', '.join(analysis['frameworks'])}
Build Tools: {', '.join(analysis['build_tools'])}
Test Frameworks: {', '.join(analysis['test_frameworks'])}
Entry Points: {', '.join(analysis['entry_points'])}
Total Files: {analysis['file_count']}
Total Lines: {analysis['total_lines']}

Dependencies:
{self._format_dependencies(analysis['dependencies'])}
        """.strip()
    
    def _format_dependencies(self, dependencies: Dict[str, Any]) -> str:
        """Format dependencies for display."""
        formatted = []
        for dep_type, deps in dependencies.items():
            if isinstance(deps, dict):
                for category, dep_list in deps.items():
                    if dep_list:
                        formatted.append(f"{dep_type} {category}: {', '.join(list(dep_list.keys())[:5])}")
            elif isinstance(deps, list):
                formatted.append(f"{dep_type}: {', '.join(deps[:5])}")
        return '\n'.join(formatted) if formatted else "No dependencies found"
        
    async def _implement_changes(self, sandbox, plan: Dict, repo_path: str) -> Dict[str, Any]:
        """Implement the planned changes"""
        trace("pr_creator.implement_changes", {"plan_files": len(plan.get("file_changes", []))})
        
        changes_made = {
            "files_changed": [],
            "files_created": [],
            "tests_added": []
        }
        
        # Install dependencies first if needed
        dependencies = plan.get("dependencies", [])
        if dependencies:
                try:
                    await self._install_dependencies(sandbox, dependencies, repo_path)
                except Exception as e:
                    logger.warning(f"Failed to install dependencies: {e}")
                    # Continue without dependencies
        
        # Process each file change (suppress requirements*.txt for UV-managed repos)
        use_uv_repo = self._uses_uv(repo_path)
        orig_file_changes = plan.get("file_changes", [])
        filtered_file_changes = []
        suppressed_paths: List[str] = []
        for fc in orig_file_changes:
            p = (fc.get("path") or "").lower()
            if use_uv_repo and self._is_requirements_file(p):
                suppressed_paths.append(fc.get("path") or "")
                continue
            filtered_file_changes.append(fc)
        if suppressed_paths:
            logger.info(f"Suppressing requirements-like files in UV repo: {suppressed_paths}")

        for file_change in filtered_file_changes:
            file_path = file_change["path"]
            change_type = file_change["type"]  # modify, create, delete
            content = file_change["content"]
            
            full_path = Path(repo_path) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if change_type == "create":
                with open(full_path, "w") as f:
                    f.write(content)
                changes_made["files_created"].append(file_path)
                logger.info(f"Created file: {file_path}")
            elif change_type == "modify":
                with open(full_path, "w") as f:
                    f.write(content)
                changes_made["files_changed"].append(file_path)
                logger.info(f"Modified file: {file_path}")
                
        # Add tests
        for test_file in plan.get("test_files", []):
            test_path = test_file["path"]
            test_content = test_file["content"]
            
            test_full_path = Path(repo_path) / test_path
            test_full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(test_full_path, "w") as f:
                f.write(test_content)
            changes_made["tests_added"].append(test_path)
            logger.info(f"Added test file: {test_path}")
            
        return changes_made
    
    def _is_requirements_file(self, path: str) -> bool:
        try:
            name = Path(path).name.lower()
        except Exception:
            name = (path or "").lower()
        patterns = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-test.txt",
            "constraints.txt",
        ]
        if name in patterns:
            return True
        if name.startswith("requirements") and name.endswith(".txt"):
            return True
        if name.startswith("constraints") and name.endswith(".txt"):
            return True
        return False

    def _uses_uv(self, repo_path: str) -> bool:
        try:
            rp = Path(repo_path)
            if (rp / "uv.lock").exists():
                return True
            # If pyproject.toml exists and no requirements.txt, likely uv/PEP 621 workflow
            if (rp / "pyproject.toml").exists() and not (rp / "requirements.txt").exists():
                return True
        except Exception:
            pass
        return False

    async def _install_dependencies(self, sandbox, dependencies: List[Dict], repo_path: str) -> None:
        """Install required dependencies."""
        trace("pr_creator.install_dependencies", {"count": len(dependencies)})
        
        # Group dependencies by ecosystem and detect uv
        npm_deps: List[str] = []
        pip_deps: List[str] = []
        uv_deps_prod: List[str] = []
        uv_deps_dev: List[str] = []
        use_uv = self._uses_uv(repo_path)
        
        for dep in dependencies:
            name = dep.get("name", "")
            version = dep.get("version", "")
            dep_type = (dep.get("type") or "").lower()  # production|development
            if not name:
                continue

            if (Path(repo_path) / "package.json").exists():
                # Node project
                dep_string = f"{name}@{version}" if version else name
                npm_deps.append(dep_string)
            elif use_uv:
                # UV-managed Python project: collect as 'name==version'
                spec = f"{name}=={version}" if version else name
                if dep_type in ("dev", "development"):
                    uv_deps_dev.append(spec)
                else:
                    uv_deps_prod.append(spec)
            elif (Path(repo_path) / "requirements.txt").exists():
                # Pip-managed Python project
                dep_string = f"{name}=={version}" if version else name
                pip_deps.append(dep_string)
        
        # Install npm dependencies
        if npm_deps:
            cmd = f"npm install {' '.join(npm_deps)}"
            result = sandbox.run_command(cmd)
            if result.returncode != 0:
                logger.warning(f"Failed to install npm dependencies: {result.stderr}")

        # Install uv dependencies (if applicable)
        if use_uv and (uv_deps_prod or uv_deps_dev):
            check = sandbox.run_command("uv --version")
            if check.returncode != 0:
                logger.warning("uv not available in sandbox; falling back to pip if possible")
            else:
                if uv_deps_prod:
                    cmd = "uv add " + " ".join(uv_deps_prod)
                    res = sandbox.run_command(cmd)
                    if res.returncode != 0:
                        logger.warning(f"Failed to add UV production deps: {res.stderr}")
                if uv_deps_dev:
                    cmd = "uv add --dev " + " ".join(uv_deps_dev)
                    res = sandbox.run_command(cmd)
                    if res.returncode != 0:
                        logger.warning(f"Failed to add UV dev deps: {res.stderr}")
                # Refresh lock and sync environment
                sandbox.run_command("uv lock")
                sandbox.run_command("uv sync")
        
        # Install pip dependencies
        if pip_deps:
            cmd = f"pip install {' '.join(pip_deps)}"
            result = sandbox.run_command(cmd)
            if result.returncode != 0:
                logger.warning(f"Failed to install pip dependencies: {result.stderr}")
        
    def _tests_passed(self, test_results: Dict[str, Any]) -> bool:
        """Check if tests passed"""
        for result in test_results.values():
            if result.get("status") == "passed":
                return True
        return False
        
    async def _fix_test_failures(self, sandbox, test_results: Dict, 
                               changes_made: Dict) -> Dict[str, Any]:
        """Attempt to fix test failures"""
        trace("pr_creator.fix_test_failures", {"test_results": list(test_results.keys())})
        
        failure_info = []
        for cmd, result in test_results.items():
            if result.get("status") == "failed":
                failure_info.append(f"Command: {cmd}\nError: {result.get('output', '')}")
        
        if not failure_info:
            return {"fixes": []}
            
        # Use LLM to suggest fixes
        fix_prompt = f"""
        The following test failures occurred:
        
        {chr(10).join(failure_info)}
        
        Files changed: {changes_made['files_changed']}
        Files created: {changes_made['files_created']}
        
        Suggest specific fixes for these test failures. Only suggest fixes for files that actually exist.
        Provide the complete file path relative to the repository root.
        """
        
        fixes = await self.llm_client.suggest_test_fixes(fix_prompt)
        
        # Apply fixes
        for fix in fixes.get("fixes", []):
            file_path = fix["file"]
            new_content = fix["content"]
            
            # Ensure the file path is relative to repo root
            full_path = Path(sandbox.sandbox_path) / "repo" / file_path
            
            # Only apply fix if the file exists or is in our changes
            if full_path.exists() or file_path in changes_made.get('files_changed', []) or file_path in changes_made.get('files_created', []):
                try:
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_path, "w") as f:
                        f.write(new_content)
                    logger.info(f"Applied fix to {file_path}")
                except Exception as e:
                    logger.error(f"Failed to apply fix to {file_path}: {e}")
            else:
                logger.warning(f"Skipping fix for non-existent file: {file_path}")
                
        return fixes
        
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Parse GitHub repo URL to get owner and repo"""
        # Example: https://github.com/owner/repo.git
        parts = repo_url.replace(".git", "").split("/")
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo
        
    def _generate_pr_body(self, request: PRCreationRequest,
                         linear_context: Optional[Dict],
                         changes_made: Dict) -> str:
        """Generate PR body content"""
        body = f"""
## Description
{request.description}

## Branch Information
- **Base Branch**: {request.base_branch}
- **Feature Branch**: {request.branch_name}

## Changes Made
- Files Modified: {len(changes_made['files_changed'])}
- Files Created: {len(changes_made['files_created'])}
- Tests Added: {len(changes_made['tests_added'])}

### Files Changed:
{chr(10).join(f"- {file}" for file in changes_made['files_changed'])}

### Files Created:
{chr(10).join(f"- {file}" for file in changes_made['files_created'])}

### Tests Added:
{chr(10).join(f"- {file}" for file in changes_made['tests_added'])}
        """
        
        if linear_context:
            body += f"""
## Linear Issue
- **Title**: {linear_context.get('title', 'N/A')}
- **Priority**: {linear_context.get('priority', 'N/A')}
- **Status**: {linear_context.get('state', {}).get('name', 'N/A')}

[View in Linear](https://linear.app/issue/{request.linear_issue_id})
            """
            
        return body
