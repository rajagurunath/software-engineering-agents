"""Code analysis service for understanding repository structure and technology stack."""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import logging

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Analyzes repository structure and determines technology stack."""
    
    def __init__(self):
        self.language_extensions = {
            'python': {'.py', '.pyx', '.pyi'},
            'javascript': {'.js', '.jsx', '.mjs', '.cjs'},
            'typescript': {'.ts', '.tsx'},
            'java': {'.java'},
            'go': {'.go'},
            'rust': {'.rs'},
            'c++': {'.cpp', '.cc', '.cxx', '.hpp', '.h'},
            'c': {'.c', '.h'},
            'php': {'.php'},
            'ruby': {'.rb'},
            'swift': {'.swift'},
            'kotlin': {'.kt', '.kts'},
            'scala': {'.scala'},
            'dart': {'.dart'},
            'shell': {'.sh', '.bash', '.zsh'},
        }
        
        self.framework_indicators = {
            'react': ['package.json', 'src/App.jsx', 'src/App.tsx', 'public/index.html'],
            'vue': ['package.json', 'src/App.vue', 'vue.config.js'],
            'angular': ['package.json', 'angular.json', 'src/app/app.module.ts'],
            'django': ['manage.py', 'settings.py', 'urls.py', 'requirements.txt'],
            'flask': ['app.py', 'requirements.txt', 'templates/'],
            'fastapi': ['main.py', 'requirements.txt', 'app/'],
            'express': ['package.json', 'server.js', 'app.js'],
            'nextjs': ['package.json', 'next.config.js', 'pages/', 'app/'],
            'spring': ['pom.xml', 'build.gradle', 'src/main/java/'],
            'rails': ['Gemfile', 'config/application.rb', 'app/'],
        }
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Perform comprehensive repository analysis."""
        repo_path = Path(repo_path)
        
        analysis = {
            'primary_language': None,
            'languages': {},
            'frameworks': [],
            'build_tools': [],
            'test_frameworks': [],
            'structure': {},
            'entry_points': [],
            'config_files': [],
            'dependencies': {},
            'file_count': 0,
            'total_lines': 0,
        }
        
        # Analyze file structure and languages
        self._analyze_files(repo_path, analysis)
        
        # Detect frameworks and tools
        self._detect_frameworks(repo_path, analysis)
        
        # Analyze dependencies
        self._analyze_dependencies(repo_path, analysis)
        
        # Find entry points
        self._find_entry_points(repo_path, analysis)
        
        # Determine primary language
        if analysis['languages']:
            analysis['primary_language'] = max(
                analysis['languages'].items(), 
                key=lambda x: x[1]['file_count']
            )[0]
        
        return analysis
    
    def _analyze_files(self, repo_path: Path, analysis: Dict) -> None:
        """Analyze all files in the repository."""
        structure = {}
        languages = {}
        total_lines = 0
        file_count = 0
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                'node_modules', '__pycache__', 'venv', 'env', 'build', 'dist', 'target'
            }]
            
            rel_path = os.path.relpath(root, repo_path)
            if rel_path == '.':
                rel_path = ''
            
            structure[rel_path] = {
                'directories': dirs,
                'files': files
            }
            
            # Analyze each file
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                file_ext = file_path.suffix.lower()
                
                # Count lines and determine language
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1
                        
                        # Determine language
                        for lang, extensions in self.language_extensions.items():
                            if file_ext in extensions:
                                if lang not in languages:
                                    languages[lang] = {'file_count': 0, 'line_count': 0}
                                languages[lang]['file_count'] += 1
                                languages[lang]['line_count'] += lines
                                break
                except Exception as e:
                    logger.debug(f"Could not read file {file_path}: {e}")
        
        analysis['structure'] = structure
        analysis['languages'] = languages
        analysis['total_lines'] = total_lines
        analysis['file_count'] = file_count
    
    def _detect_frameworks(self, repo_path: Path, analysis: Dict) -> None:
        """Detect frameworks and build tools."""
        frameworks = []
        build_tools = []
        test_frameworks = []
        config_files = []
        
        # Check for framework indicators
        for framework, indicators in self.framework_indicators.items():
            for indicator in indicators:
                if (repo_path / indicator).exists():
                    frameworks.append(framework)
                    break
        
        # Check for build tools and config files
        build_configs = {
            'package.json': 'npm',
            'yarn.lock': 'yarn',
            'pnpm-lock.yaml': 'pnpm',
            'requirements.txt': 'pip',
            'Pipfile': 'pipenv',
            'poetry.lock': 'poetry',
            'Cargo.toml': 'cargo',
            'go.mod': 'go modules',
            'pom.xml': 'maven',
            'build.gradle': 'gradle',
            'Makefile': 'make',
            'CMakeLists.txt': 'cmake',
        }
        
        for config_file, tool in build_configs.items():
            if (repo_path / config_file).exists():
                build_tools.append(tool)
                config_files.append(config_file)
        
        # Detect test frameworks
        test_indicators = {
            'jest': ['jest.config.js', 'package.json'],
            'pytest': ['pytest.ini', 'conftest.py', 'requirements.txt'],
            'unittest': ['test_*.py', '*_test.py'],
            'mocha': ['mocha.opts', 'package.json'],
            'jasmine': ['jasmine.json', 'package.json'],
        }
        
        for test_fw, indicators in test_indicators.items():
            for indicator in indicators:
                if (repo_path / indicator).exists():
                    test_frameworks.append(test_fw)
                    break
        
        analysis['frameworks'] = frameworks
        analysis['build_tools'] = build_tools
        analysis['test_frameworks'] = test_frameworks
        analysis['config_files'] = config_files
    
    def _analyze_dependencies(self, repo_path: Path, analysis: Dict) -> None:
        """Analyze project dependencies."""
        dependencies = {}
        
        # Node.js dependencies
        package_json = repo_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    dependencies['npm'] = {
                        'dependencies': data.get('dependencies', {}),
                        'devDependencies': data.get('devDependencies', {}),
                    }
            except Exception as e:
                logger.debug(f"Could not parse package.json: {e}")
        
        # Python dependencies
        requirements_txt = repo_path / 'requirements.txt'
        if requirements_txt.exists():
            try:
                with open(requirements_txt, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    dependencies['pip'] = deps
            except Exception as e:
                logger.debug(f"Could not parse requirements.txt: {e}")
        
        analysis['dependencies'] = dependencies
    
    def _find_entry_points(self, repo_path: Path, analysis: Dict) -> None:
        """Find likely entry points for the application."""
        entry_points = []
        
        common_entry_points = [
            'main.py', 'app.py', 'server.py', 'index.py',
            'main.js', 'app.js', 'server.js', 'index.js',
            'main.ts', 'app.ts', 'server.ts', 'index.ts',
            'Main.java', 'Application.java',
            'main.go',
            'main.rs',
        ]
        
        for entry_point in common_entry_points:
            if (repo_path / entry_point).exists():
                entry_points.append(entry_point)
        
        # Check src directory
        src_dir = repo_path / 'src'
        if src_dir.exists():
            for entry_point in common_entry_points:
                if (src_dir / entry_point).exists():
                    entry_points.append(f'src/{entry_point}')
        
        analysis['entry_points'] = entry_points
    
    def get_code_context(self, repo_path: str, max_files: int = 10) -> str:
        """Get relevant code context for LLM analysis."""
        repo_path = Path(repo_path)
        analysis = self.analyze_repository(repo_path)
        
        context = f"""
Repository Analysis:
- Primary Language: {analysis['primary_language']}
- Languages: {', '.join(analysis['languages'].keys())}
- Frameworks: {', '.join(analysis['frameworks'])}
- Build Tools: {', '.join(analysis['build_tools'])}
- Entry Points: {', '.join(analysis['entry_points'])}

Key Files:
"""
        
        # Include content of key configuration files
        key_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod']
        files_included = 0
        
        for key_file in key_files:
            if files_included >= max_files:
                break
                
            file_path = repo_path / key_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) < 2000:  # Only include small config files
                            context += f"\n--- {key_file} ---\n{content}\n"
                            files_included += 1
                except Exception as e:
                    logger.debug(f"Could not read {key_file}: {e}")
        
        # Include entry point files (first few lines)
        for entry_point in analysis['entry_points'][:3]:
            if files_included >= max_files:
                break
                
            file_path = repo_path / entry_point
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:20]  # First 20 lines
                        context += f"\n--- {entry_point} (first 20 lines) ---\n"
                        context += ''.join(lines)
                        files_included += 1
                except Exception as e:
                    logger.debug(f"Could not read {entry_point}: {e}")
        
        return context