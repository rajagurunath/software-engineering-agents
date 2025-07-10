from openai import AsyncOpenAI
from typing import Dict, List, Any
from config.settings import settings
from opik.integrations.openai import track_openai
import os
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
        response = await self.client.chat.completions.create(
            model=settings.io_model,
            messages=[
                {"role": "system", "content": "You are a senior software architect. Create detailed implementation plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        return self._parse_implementation_plan(content)
        
    async def suggest_test_fixes(self, prompt: str) -> Dict[str, Any]:
        """Suggest fixes for test failures"""
        response = await self.client.chat.completions.create(
            model=settings.io_model,
            messages=[
                {"role": "system", "content": "You are a testing expert. Analyze test failures and suggest fixes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        return self._parse_test_fixes(content)
        
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
        # This is a simplified parser - in production, use structured prompts
        return {
            "file_changes": [
                {
                    "path": "src/example.py",
                    "type": "modify",
                    "content": "# Generated code would go here"
                }
            ],
            "test_files": [
                {
                    "path": "tests/test_example.py",
                    "content": "# Generated test code would go here"
                }
            ],
            "dependencies": []
        }
        
    def _parse_test_fixes(self, content: str) -> Dict[str, Any]:
        """Parse test fix suggestions"""
        return {
            "fixes": [
                {
                    "file": "src/example.py",
                    "content": "# Fixed code would go here"
                }
            ]
        }