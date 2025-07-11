from openai import AsyncOpenAI
from typing import Dict, List, Any
from config.settings import settings
from opik.integrations.openai import track_openai
import os
from utils.opik_tracer import trace
os.environ["OPIK_URL_OVERRIDE"] = "http://localhost:5173/api"

class LLMClient:
    def __init__(self):
        """Initialise Opik-instrumented OpenAI async client."""
        raw_client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        self.client = track_openai(raw_client)
        
        
    async def analyze_code(self, prompt: str) -> Dict[str, Any]:
        """Analyze code quality using GPT"""
        response = await self.client.chat.completions.create(
            model=settings.io_model,
            messages=[
                {"role": "system", "content": "You are a senior code reviewer. Analyze code and provide structured feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            
        )
        
        # Parse structured response
        content = response.choices[0].message.content
        return self._parse_code_analysis(content)
        
    async def find_bugs(self, prompt: str) -> Dict[str, Any]:
        """Find potential bugs in code"""
        response = await self.client.chat.completions.create(
            model=settings.io_model,
            messages=[
                {"role": "system", "content": "You are a bug detection specialist. Find potential bugs and security issues."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        return self._parse_bug_analysis(content)
        
    async def generate_clarifications(self, prompt: str) -> Dict[str, List[str]]:
        """Generate clarification questions"""
        response = await self.client.chat.completions.create(
            model=settings.io_model,
            messages=[
                {"role": "system", "content": "Generate specific clarification questions for software development tasks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        return {"questions": self._extract_questions(content)}
        
    async def generate_implementation_plan(self, prompt: str) -> Dict[str, Any]:
        """Generate detailed implementation plan"""
        trace("llm.generate_implementation_plan", {"prompt_length": len(prompt)})
        
        response = await self.client.chat.completions.create(
            model=settings.io_model,
            messages=[
                {"role": "system", "content": """You are a senior software architect and full-stack developer with expertise in multiple programming languages and frameworks. 
                
CRITICAL INSTRUCTIONS:
1. Always analyze the repository structure and technology stack FIRST
2. Use the CORRECT programming language and framework for the project
3. Follow existing code patterns and conventions
4. Provide complete, working code that fits the project structure
5. Return valid JSON format as specified
6. Never suggest changes in the wrong programming language

Your response must be valid JSON that can be parsed."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        trace("llm.implementation_plan_generated", {"response_length": len(content)})
        
        try:
            import json
            plan = json.loads(content)
            return plan
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response content: {content}")
            # Fallback to old parsing method
            return self._parse_implementation_plan(content)
        
    async def suggest_test_fixes(self, prompt: str) -> Dict[str, Any]:
        """Suggest fixes for test failures"""
        trace("llm.suggest_test_fixes", {"prompt_length": len(prompt)})
        
        response = await self.client.chat.completions.create(
            model=settings.io_model,
            messages=[
                {"role": "system", "content": """You are a testing expert. Analyze test failures and suggest specific fixes.
                
IMPORTANT:
1. Only suggest fixes for files that actually exist or were mentioned as changed
2. Provide complete file content, not just snippets
3. Use the correct file paths relative to repository root
4. Return valid JSON format
5. If no fixes are needed, return empty fixes array

Return JSON in this format:
{
    "fixes": [
        {
            "file": "relative/path/to/file",
            "content": "complete file content",
            "reasoning": "explanation of the fix"
        }
    ]
}"""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        trace("llm.test_fixes_generated", {"response_length": len(content)})
        
        try:
            import json
            fixes = json.loads(content)
            return fixes
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse test fixes JSON: {e}")
            logger.error(f"Response content: {content}")
            return {"fixes": []}
        
    def _parse_code_analysis(self, content: str) -> Dict[str, Any]:
        """Parse code analysis response"""
        # Simple parsing - in production, use more robust parsing
        lines = content.split('\n')
        analysis = {
            "score": 7,  # default
            "issues": [],
            "style_violations": [],
            "complexity_issues": [],
            "performance_issues": []
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if "score:" in line.lower():
                try:
                    analysis["score"] = int(line.split(":")[-1].strip().split("/")[0])
                except:
                    pass
            elif "issues:" in line.lower():
                current_section = "issues"
            elif "style:" in line.lower():
                current_section = "style_violations"
            elif "complexity:" in line.lower():
                current_section = "complexity_issues"
            elif "performance:" in line.lower():
                current_section = "performance_issues"
            elif line.startswith("-") and current_section:
                analysis[current_section].append(line[1:].strip())
                
        return analysis
        
    def _parse_bug_analysis(self, content: str) -> Dict[str, Any]:
        """Parse bug analysis response"""
        lines = content.split('\n')
        bugs = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("-"):
                bugs.append(line[1:].strip())
                
        return {"bugs": bugs}
        
    def _extract_questions(self, content: str) -> List[str]:
        """Extract questions from response"""
        lines = content.split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                questions.append(line[1:].strip())
            elif "?" in line:
                questions.append(line.strip())
                
        return questions[:5]  # Limit to 5 questions
        
    def _parse_implementation_plan(self, content: str) -> Dict[str, Any]:
        """Parse implementation plan"""
        logger.warning("Using fallback implementation plan parser")
        
        # Extract file changes from markdown-style content
        lines = content.split('\n')
        file_changes = []
        current_file = None
        current_content = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block and current_file:
                    # End of code block
                    file_changes.append({
                        "path": current_file,
                        "type": "modify",
                        "content": '\n'.join(current_content),
                        "reasoning": "Generated by LLM"
                    })
                    current_content = []
                    current_file = None
                in_code_block = not in_code_block
            elif in_code_block:
                current_content.append(line)
            elif line.strip().startswith('File:') or line.strip().startswith('Path:'):
                current_file = line.split(':', 1)[1].strip()
        
        return {
            "summary": "Implementation plan generated from text parsing",
            "file_changes": file_changes,
            "test_files": [],
            "dependencies": []
        }
        
    def _parse_test_fixes(self, content: str) -> Dict[str, Any]:
        """Parse test fix suggestions"""
        logger.warning("Using fallback test fixes parser")
        
        # Try to extract file paths and content from markdown-style response
        lines = content.split('\n')
        fixes = []
        current_file = None
        current_content = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block and current_file:
                    # End of code block
                    fixes.append({
                        "file": current_file,
                        "content": '\n'.join(current_content),
                        "reasoning": "Generated from fallback parser"
                    })
                    current_content = []
                    current_file = None
                in_code_block = not in_code_block
            elif in_code_block:
                current_content.append(line)
            elif line.strip().startswith('File:') or line.strip().startswith('Path:'):
                current_file = line.split(':', 1)[1].strip()
        
        return {"fixes": fixes}
        
    async def address_pr_comments(self, context: str) -> Dict[str, Any]:
        """Address PR comments for a specific file"""
        trace("llm.address_pr_comments", {"context_length": len(context)})
        
        response = await self.client.chat.completions.create(
            model=settings.io_model,
            messages=[
                {"role": "system", "content": """You are a senior software engineer addressing PR review comments.
                
INSTRUCTIONS:
1. Carefully read the file content and all comments
2. Address each comment by modifying the code appropriately
3. Maintain existing code style and structure
4. Only make necessary changes to address the feedback
5. Return valid JSON with the modified file content

Return JSON in this format:
{
    "modified": true/false,
    "new_content": "complete modified file content",
    "handled_comments": [
        {
            "id": "comment_id",
            "summary": "brief description of how this comment was addressed"
        }
    ],
    "reasoning": "explanation of changes made"
}"""},
                {"role": "user", "content": context}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        trace("llm.pr_comments_addressed", {"response_length": len(content)})
        
        try:
            import json
            result = json.loads(content)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PR comment response as JSON: {e}")
            return {"modified": False, "handled_comments": []}
    
    async def address_general_pr_comments(self, context: str) -> Dict[str, Any]:
        """Address general PR comments that don't target specific files"""
        trace("llm.address_general_pr_comments", {"context_length": len(context)})
        
        response = await self.client.chat.completions.create(
            model=settings.io_model,
            messages=[
                {"role": "system", "content": """You are a senior software engineer addressing general PR feedback.
                
INSTRUCTIONS:
1. Analyze the general comments and determine what files need changes
2. Provide specific file modifications to address the feedback
3. Consider the repository structure and technology stack
4. Make appropriate changes across multiple files if needed

Return JSON in this format:
{
    "file_changes": [
        {
            "path": "relative/path/to/file",
            "content": "complete file content",
            "reasoning": "why this file was modified"
        }
    ],
    "handled_comments": [
        {
            "summary": "brief description of how this comment was addressed"
        }
    ]
}"""},
                {"role": "user", "content": context}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        trace("llm.general_pr_comments_addressed", {"response_length": len(content)})
        
        try:
            import json
            result = json.loads(content)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse general PR comment response as JSON: {e}")
            return {"file_changes": [], "handled_comments": []}