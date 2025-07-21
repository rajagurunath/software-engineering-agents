"""
Prompts for the Architect Agent - inspired by open_deep_research patterns
"""

RESEARCH_PLANNER_PROMPT = """You are an expert research architect for io.net, a decentralized GPU network platform.

Your role is to create comprehensive research plans that leverage multiple specialized tools:

AVAILABLE TOOLS:
1. CODING TOOLS:
   - PR Review: Analyze pull requests for code quality, bugs, and improvements
   - PR Creation: Create new pull requests with implementation plans
   - Handle PR Comments: Address and resolve PR feedback automatically

2. DATA TOOLS:
   - IONetDataBot: Query io.net's database for metrics, device performance, block rewards, etc.
   - Generates SQL queries and creates Plotly visualizations
   - Covers: devices, earnings, staking, network health, usage patterns

3. DOCS TOOLS:
   - RagAssistant: Search and analyze io.net documentation
   - Covers: platform features, setup guides, troubleshooting, API references

RESEARCH TYPES:
- CODE_REVIEW: Focus on code analysis, PR reviews, technical implementation
- DATA_ANALYSIS: Focus on metrics, performance data, network analytics
- DOCUMENTATION: Focus on platform knowledge, user guides, feature explanations
- COMPREHENSIVE: Combine all tools for thorough multi-faceted research

Given the user query: "{query}"

Create a detailed research plan with 3-8 steps that will provide comprehensive insights.

For each step, specify:
1. Tool type (coding/data/docs)
2. Specific action to take
3. Focused query for that tool
4. How it contributes to the overall research

Prioritize steps that will yield the most valuable insights for the user's question.

Return a JSON research plan with this structure:
{{
    "research_type": "one of the research types",
    "estimated_duration_minutes": "realistic estimate",
    "steps": [
        {{
            "tool_type": "coding|data|docs",
            "action": "specific action name",
            "query": "focused query for this step"
        }}
    ]
}}
"""

EXECUTIVE_SUMMARY_PROMPT = """You are an expert analyst creating an executive summary for io.net research.

RESEARCH QUERY: {query}
RESEARCH TYPE: {research_type}

FINDINGS FROM RESEARCH STEPS:
{findings}

Create a comprehensive executive summary that:
1. Clearly states what was researched
2. Highlights the most important findings
3. Provides actionable insights
4. Identifies any critical issues or opportunities
5. Maintains technical accuracy while being accessible

Keep the summary concise but thorough (200-400 words).

Executive Summary:
"""

RECOMMENDATIONS_PROMPT = """Based on the research findings, provide 3-7 specific, actionable recommendations.

RESEARCH QUERY: {query}
FINDINGS: {findings}

CRITICAL REQUIREMENTS for recommendations:
1. Keep recommendations SHORT and ACTIONABLE (max 2 sentences each)
2. ALWAYS check if the recommendation is already implemented in io.net
3. If already implemented, mention: "✅ Already implemented" 
4. If not implemented, mention: "🚀 Recommended for implementation"
5. If needs brainstorming, mention: "💡 Requires further analysis"
6. Focus on NEW insights or improvements, not existing features
7. Prioritize recommendations that add immediate value

Format as a numbered list with status indicators.

Recommendations:
"""

DATA_ANALYSIS_PROMPT = """You are analyzing data from io.net's decentralized GPU network.

QUERY: {query}

Available data includes:
- Device performance metrics
- Block reward distributions
- Network utilization patterns
- Staking information
- Earnings data

Generate specific SQL-focused queries that will provide insights for this research.
Consider what visualizations would be most helpful.

Provide 2-4 focused data queries:
"""

CODE_ANALYSIS_PROMPT = """You are analyzing code and development aspects of io.net.

QUERY: {query}

Consider:
- Code quality and architecture
- PR review insights
- Implementation patterns
- Technical debt
- Security considerations
- Performance optimizations

Provide specific areas to investigate:
"""

DOCS_ANALYSIS_PROMPT = """You are researching io.net documentation and platform knowledge.

QUERY: {query}

Focus on:
- Platform capabilities and features
- User experience and onboarding
- Technical documentation quality
- Common issues and solutions
- API and integration guides

Provide specific documentation areas to explore:
"""

HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IO.NET Research Report - {title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .executive-summary {{
            background: #e8f4fd;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin: 20px 0;
        }}
        .recommendations {{
            background: #f0f9ff;
            border-left: 4px solid #10b981;
        }}
        .visualization {{
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #e1e5e9;
            border-radius: 6px;
            background: white;
        }}
        .visualization h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .metadata {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            font-size: 0.9em;
            color: #6c757d;
        }}
        .step-result {{
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #6c757d;
        }}
        .tool-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 10px;
        }}
        .tool-coding {{ background: #ffeaa7; color: #2d3436; }}
        .tool-data {{ background: #74b9ff; color: white; }}
        .tool-docs {{ background: #00b894; color: white; }}
        .markdown-content {{
            line-height: 1.6;
        }}
        .markdown-content h1, .markdown-content h2, .markdown-content h3 {{
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        .markdown-content code {{
            background: #f1f2f6;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
        }}
        .markdown-content pre {{
            background: #f1f2f6;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        .markdown-content blockquote {{
            border-left: 4px solid #3498db;
            margin: 0;
            padding-left: 20px;
            color: #666;
        }}
        .markdown-content ul, .markdown-content ol {{
            padding-left: 20px;
        }}
        .markdown-content table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        .markdown-content th, .markdown-content td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        .markdown-content th {{
            background-color: #f2f2f2;
        }}
        .status-implemented {{ color: #10b981; }}
        .status-recommended {{ color: #3498db; }}
        .status-analysis {{ color: #f39c12; }}
        .question-chart-pair {{
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            background: #fafbfc;
        }}
        .question-title {{
            font-size: 1.1em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            padding: 10px;
            background: #e8f4fd;
            border-radius: 6px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏗️ IO.NET Research Report</h1>
        <p><strong>Query:</strong> {query}</p>
        <p><strong>Research Type:</strong> {research_type}</p>
        <p><strong>Generated:</strong> {timestamp}</p>
    </div>

    <div class="section executive-summary">
        <h2>📋 Executive Summary</h2>
        <div class="markdown-content" id="executive-summary-content">
            {executive_summary}
        </div>
    </div>

    <div class="section recommendations">
        <h2>💡 Recommendations</h2>
        <div class="markdown-content" id="recommendations-content">
            {recommendations_html}
        </div>
    </div>

    {data_analysis_section}

    {visualizations_html}

    <div class="section">
        <h2>🔍 Detailed Findings</h2>
        <div class="markdown-content">
            {detailed_findings_html}
        </div>
    </div>

    <div class="section">
        <h2>📊 Research Metadata</h2>
        <div class="metadata">
            <p><strong>Research ID:</strong> {research_id}</p>
            <p><strong>Total Duration:</strong> {duration} seconds</p>
            <p><strong>Steps Completed:</strong> {steps_count}</p>
            <p><strong>Tools Used:</strong> {tools_used}</p>
        </div>
    </div>

    <script>
        // Render markdown content
        function renderMarkdown() {{
            const summaryElement = document.getElementById('executive-summary-content');
            if (summaryElement) {{
                summaryElement.innerHTML = marked.parse(summaryElement.textContent);
            }}
            
            const recElement = document.getElementById('recommendations-content');
            if (recElement) {{
                recElement.innerHTML = marked.parse(recElement.textContent);
            }}
        }}
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            renderMarkdown();
        }});
    </script>
</body>
</html>"""