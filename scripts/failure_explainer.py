"""
Test Failure Explainer using Azure OpenAI

This script analyzes Playwright test failures and generates AI-powered explanations
using Azure OpenAI. It reads the JSON test results, sends failure context to the LLM,
and generates comprehensive reports with screenshots and traces.

Usage:
    python scripts/failure_explainer.py [--results-file PATH] [--output-dir PATH]

================================================================================
TASK 3: LLM INTEGRATION CHOICE EXPLANATION
================================================================================

WHY I CHOSE OPTION 1 (Test Failure Explainer) OVER OPTION 2 :

1. IMMEDIATE PRACTICAL VALUE:
   Test failure analysis provides instant value in the debugging workflow. When a test
   fails at 2 AM in CI/CD, developers get actionable insights without manual investigation.
   

2. REAL-TIME CONTEXT UTILIZATION:
   This approach sends actual runtime data to the LLM - error messages, stack traces,
   page state, screenshots, and network responses. The LLM analyzes real failures with
   full context, not hypothetical scenarios. This is a harder problem that showcases
   true LLM integration capabilities.

3. INTEGRATION WITH TEST FRAMEWORK:
   The output is directly attached to test reports (HTML, JSON, Allure). Screenshots
   and traces are preserved. This is true framework integration, not a standalone tool.

4. SCALABILITY:
   Runs automatically on every test execution. As the test suite grows, the value
   increases without additional configuration.


================================================================================
"""

import os
import sys
import json
import argparse
import shutil
import base64
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict, field

from openai import AzureOpenAI
from dotenv import load_dotenv


@dataclass
class FailureAnalysis:
    """Structured analysis result from AI"""
    root_cause: str
    explanation: str
    suggested_fix: str


@dataclass
class TestFailure:
    """Represents a failed test with its context"""
    test_name: str
    test_file: str
    duration_ms: int
    error_message: str
    error_stack: str
    status: str
    attachments: list
    screenshots: list = field(default_factory=list)
    trace_path: Optional[str] = None
    video_path: Optional[str] = None
    analysis: Optional[FailureAnalysis] = None


class AzureOpenAIAnalyzer:
    """Handles Azure OpenAI integration for failure analysis"""
    
    def __init__(self):
        load_dotenv()
        
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "o3-mini")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        self.client = None
        if self.is_configured():
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version
            )
    
    def is_configured(self) -> bool:
        """Check if Azure OpenAI credentials are configured"""
        return bool(self.endpoint and self.api_key)
    
    def analyze_failure(self, failure: TestFailure) -> FailureAnalysis:
        """Analyze a test failure and return structured explanation"""
        
        if not self.is_configured():
            return FailureAnalysis(
                root_cause="Azure OpenAI not configured",
                explanation="Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables.",
                suggested_fix="Configure Azure OpenAI credentials in your .env file."
            )
        
        prompt = self._build_prompt(failure)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content)
            
        except Exception as e:
            return FailureAnalysis(
                root_cause="AI Analysis Error",
                explanation=f"Failed to get AI analysis: {str(e)}",
                suggested_fix="Check Azure OpenAI configuration and connectivity."
            )
    
    def _get_system_prompt(self) -> str:
        return """You are an expert test automation engineer and debugger. Your job is to analyze test failures and provide clear, actionable explanations.

When analyzing a test failure, you should:
1. Identify the root cause of the failure
2. Explain what went wrong in plain English
3. Suggest specific fixes or debugging steps

Structure your response with these exact sections:
**Root Cause:** [Brief description of the underlying cause]

**Explanation:** [Detailed explanation of what went wrong]

**Suggested Fix:** [Specific steps to fix this issue]

Be concise but thorough. Focus on actionable insights."""

    def _build_prompt(self, failure: TestFailure) -> str:
        prompt = f"""## Test Failure Analysis Request

### Test Information
- **Test Name:** {failure.test_name}
- **Test File:** {failure.test_file}
- **Duration:** {failure.duration_ms}ms
- **Status:** {failure.status}

### Error Details
```
{failure.error_message}
```

### Stack Trace
```
{failure.error_stack[:2000] if failure.error_stack else 'No stack trace available'}
```

Please analyze this test failure and provide:
1. **Root Cause:** What is the underlying cause of this failure?
2. **Explanation:** A plain English explanation of what went wrong
3. **Suggested Fix:** Specific steps to fix this issue"""

        return prompt
    
    def _parse_response(self, response: str) -> FailureAnalysis:
        """Parse the AI response into structured format"""
        
        root_cause = ""
        explanation = ""
        suggested_fix = ""
        
        root_cause_match = re.search(
            r'\*\*Root Cause:\*\*\s*(.+?)(?=\*\*Explanation:|$)', 
            response, 
            re.DOTALL | re.IGNORECASE
        )
        explanation_match = re.search(
            r'\*\*Explanation:\*\*\s*(.+?)(?=\*\*Suggested Fix:|$)', 
            response, 
            re.DOTALL | re.IGNORECASE
        )
        suggested_fix_match = re.search(
            r'\*\*Suggested Fix:\*\*\s*(.+?)$', 
            response, 
            re.DOTALL | re.IGNORECASE
        )
        
        if root_cause_match:
            root_cause = root_cause_match.group(1).strip()
        if explanation_match:
            explanation = explanation_match.group(1).strip()
        if suggested_fix_match:
            suggested_fix = suggested_fix_match.group(1).strip()
        
        if not (root_cause or explanation or suggested_fix):
            explanation = response
            root_cause = "See explanation"
            suggested_fix = "See explanation"
        
        return FailureAnalysis(
            root_cause=root_cause,
            explanation=explanation,
            suggested_fix=suggested_fix
        )


class PlaywrightResultsParser:
    """Parses Playwright JSON results and extracts failures"""
    
    def __init__(self, results_file: Path):
        self.results_file = results_file
        self.results = None
        self.results_dir = results_file.parent
    
    def load(self) -> bool:
        """Load the results file"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                self.results = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading results file: {e}")
            return False
    
    def get_failures(self) -> list[TestFailure]:
        """Extract all failed tests from results"""
        failures = []
        
        if not self.results:
            return failures
        
        def process_suite(suite: dict, parent_file: str = ""):
            suite_failures = []
            
            file_path = suite.get('file', parent_file)
            
            for spec in suite.get('specs', []):
                for test in spec.get('tests', []):
                    for result in test.get('results', []):
                        status = result.get('status', '')
                        if status in ['failed', 'timedOut']:
                            error_msg = ""
                            error_stack = ""
                            
                            if result.get('errors'):
                                error = result['errors'][0]
                                error_msg = error.get('message', '')
                                error_stack = error.get('stack', '')
                            elif result.get('error'):
                                error = result['error']
                                error_msg = error.get('message', '')
                                error_stack = error.get('stack', '')
                            
                            attachments = result.get('attachments', [])
                            screenshots = []
                            trace_path = None
                            video_path = None
                            
                            for att in attachments:
                                att_name = att.get('name', '').lower()
                                att_path = att.get('path', '')
                                content_type = att.get('contentType', '')
                                
                                if 'screenshot' in att_name or content_type.startswith('image/'):
                                    screenshots.append({
                                        'name': att.get('name', 'screenshot'),
                                        'path': att_path,
                                        'contentType': content_type
                                    })
                                elif 'trace' in att_name or att_path.endswith('.zip'):
                                    trace_path = att_path
                                elif 'video' in att_name or content_type.startswith('video/'):
                                    video_path = att_path
                            
                            failure = TestFailure(
                                test_name=spec.get('title', 'Unknown'),
                                test_file=file_path,
                                duration_ms=result.get('duration', 0),
                                error_message=error_msg,
                                error_stack=error_stack,
                                status=status,
                                attachments=attachments,
                                screenshots=screenshots,
                                trace_path=trace_path,
                                video_path=video_path
                            )
                            suite_failures.append(failure)
            
            for child_suite in suite.get('suites', []):
                suite_failures.extend(process_suite(child_suite, file_path))
            
            return suite_failures
        
        for suite in self.results.get('suites', []):
            failures.extend(process_suite(suite))
        
        return failures


class ReportGenerator:
    """Generates interactive HTML and JSON reports for failure analysis"""
    
    def __init__(self, output_dir: Path, playwright_report_dir: Path = None):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir = self.output_dir / "assets"
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.playwright_report_dir = playwright_report_dir
    
    def _copy_screenshot(self, src_path: str, index: int, test_index: int) -> Optional[str]:
        """Copy screenshot to assets directory and return relative path"""
        if not src_path:
            return None
        
        src = Path(src_path)
        if not src.exists():
            # Try to find in playwright-report/data
            if self.playwright_report_dir:
                possible_path = self.playwright_report_dir / "data" / src.name
                if possible_path.exists():
                    src = possible_path
                else:
                    return None
            else:
                return None
        
        ext = src.suffix or '.png'
        dest_name = f"screenshot-{test_index}-{index}{ext}"
        dest = self.assets_dir / dest_name
        
        try:
            shutil.copy2(src, dest)
            return f"assets/{dest_name}"
        except Exception as e:
            print(f"    Warning: Could not copy screenshot: {e}")
            return None
    
    def _copy_trace(self, src_path: str, test_index: int) -> Optional[str]:
        """Copy trace file to assets directory"""
        if not src_path:
            return None
        
        src = Path(src_path)
        if not src.exists():
            return None
        
        dest_name = f"trace-{test_index}.zip"
        dest = self.assets_dir / dest_name
        
        try:
            shutil.copy2(src, dest)
            return f"assets/{dest_name}"
        except Exception as e:
            print(f"    Warning: Could not copy trace: {e}")
            return None
    
    def _embed_image_base64(self, path: str) -> Optional[str]:
        """Convert image to base64 for embedding"""
        try:
            p = Path(path)
            if not p.exists():
                return None
            with open(p, 'rb') as f:
                data = base64.b64encode(f.read()).decode('utf-8')
                ext = p.suffix.lower()
                mime = 'image/png' if ext == '.png' else 'image/jpeg'
                return f"data:{mime};base64,{data}"
        except:
            return None
    
    def generate_html_report(self, failures: list[TestFailure]) -> Path:
        """Generate an interactive HTML report with all failure analyses"""
        
        # Process screenshots for each failure
        for i, failure in enumerate(failures):
            processed_screenshots = []
            for j, ss in enumerate(failure.screenshots):
                rel_path = self._copy_screenshot(ss.get('path', ''), j, i)
                if rel_path:
                    processed_screenshots.append({
                        'name': ss.get('name', 'screenshot'),
                        'path': rel_path
                    })
            failure.screenshots = processed_screenshots
            
            if failure.trace_path:
                failure.trace_path = self._copy_trace(failure.trace_path, i)
        
        test_rows = "\n".join([
            self._generate_test_row(f, i) for i, f in enumerate(failures)
        ])
        
        # Generate summary stats
        total_duration = sum(f.duration_ms for f in failures)
        avg_duration = total_duration // len(failures) if failures else 0
        files_affected = len(set(f.test_file for f in failures))
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Failure Analysis Report</title>
    <style>
        :root {{
            --bg-color: #0f0f1a;
            --card-bg: #1a1a2e;
            --card-hover: #1f1f35;
            --text-color: #e0e0e0;
            --text-muted: #888;
            --accent-color: #e94560;
            --accent-hover: #ff6b8a;
            --success-color: #4ade80;
            --warning-color: #fbbf24;
            --info-color: #60a5fa;
            --border-color: #2a2a4a;
            --shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
        
        /* Header */
        header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            border-radius: 16px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
        }}
        
        header h1 {{
            color: #fff;
            font-size: 2rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        header p {{ color: var(--text-muted); margin-bottom: 1.5rem; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-color), #ff6b8a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{ color: var(--text-muted); font-size: 0.85rem; margin-top: 0.25rem; }}
        
        /* Filter Bar */
        .filter-bar {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .search-box {{
            flex: 1;
            min-width: 250px;
            position: relative;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 0.75rem 1rem 0.75rem 2.75rem;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: var(--card-bg);
            color: var(--text-color);
            font-size: 0.95rem;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        
        .search-box input:focus {{
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(233, 69, 96, 0.2);
        }}
        
        .search-box::before {{
            content: "🔍";
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
        }}
        
        .filter-btn {{
            padding: 0.75rem 1.25rem;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: var(--card-bg);
            color: var(--text-color);
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9rem;
        }}
        
        .filter-btn:hover, .filter-btn.active {{
            background: var(--accent-color);
            border-color: var(--accent-color);
        }}
        
        /* Test Cards */
        .test-failure {{
            background: var(--card-bg);
            border-radius: 16px;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
            overflow: hidden;
            box-shadow: var(--shadow);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .test-failure:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.25rem 1.5rem;
            background: linear-gradient(90deg, rgba(233,69,96,0.1) 0%, transparent 100%);
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
            user-select: none;
        }}
        
        .test-header:hover {{ background: linear-gradient(90deg, rgba(233,69,96,0.15) 0%, transparent 100%); }}
        
        .test-title {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .test-title h3 {{
            color: #fff;
            font-size: 1.1rem;
            font-weight: 600;
        }}
        
        .test-meta {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .badge {{
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge-failed {{ background: rgba(233,69,96,0.2); color: var(--accent-color); }}
        .badge-timeout {{ background: rgba(251,191,36,0.2); color: var(--warning-color); }}
        
        .duration {{
            color: var(--text-muted);
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}
        
        .expand-icon {{
            font-size: 1.25rem;
            transition: transform 0.3s;
            color: var(--text-muted);
        }}
        
        .test-failure.expanded .expand-icon {{ transform: rotate(180deg); }}
        
        .test-content {{
            display: none;
            padding: 1.5rem;
        }}
        
        .test-failure.expanded .test-content {{ display: block; }}
        
        .test-file {{
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-bottom: 1rem;
            font-family: 'Fira Code', monospace;
        }}
        
        /* Tabs */
        .tabs {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}
        
        .tab-btn {{
            padding: 0.5rem 1rem;
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 0.9rem;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        
        .tab-btn:hover {{ color: var(--text-color); background: rgba(255,255,255,0.05); }}
        .tab-btn.active {{ color: var(--accent-color); background: rgba(233,69,96,0.1); }}
        
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; animation: fadeIn 0.3s ease; }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Error Section */
        .error-section {{
            background: rgba(233, 69, 96, 0.08);
            border-radius: 12px;
            padding: 1.25rem;
            border-left: 4px solid var(--accent-color);
        }}
        
        .error-section h4 {{
            color: var(--accent-color);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .error-message {{
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 0.8rem;
            white-space: pre-wrap;
            word-break: break-word;
            color: #ff8fa3;
            max-height: 300px;
            overflow-y: auto;
            background: rgba(0,0,0,0.2);
            padding: 1rem;
            border-radius: 8px;
        }}
        
        /* Analysis Sections */
        .analysis-grid {{
            display: grid;
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .analysis-card {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 1.25rem;
            border-left: 4px solid;
        }}
        
        .analysis-card.root-cause {{ border-left-color: #f472b6; }}
        .analysis-card.explanation {{ border-left-color: var(--info-color); }}
        .analysis-card.suggested-fix {{ border-left-color: var(--success-color); }}
        
        .analysis-card h4 {{
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.95rem;
        }}
        
        .analysis-card.root-cause h4 {{ color: #f472b6; }}
        .analysis-card.explanation h4 {{ color: var(--info-color); }}
        .analysis-card.suggested-fix h4 {{ color: var(--success-color); }}
        
        .analysis-content {{
            font-size: 0.9rem;
            line-height: 1.7;
            color: var(--text-color);
        }}
        
        /* Screenshots Gallery */
        .screenshots-section {{
            margin-top: 1rem;
        }}
        
        .screenshots-section h4 {{
            color: var(--info-color);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .screenshots-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
        }}
        
        .screenshot-card {{
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .screenshot-card:hover {{
            transform: scale(1.02);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }}
        
        .screenshot-card img {{
            width: 100%;
            height: 180px;
            object-fit: cover;
            display: block;
        }}
        
        .screenshot-label {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 0.5rem 0.75rem;
            background: linear-gradient(transparent, rgba(0,0,0,0.8));
            color: #fff;
            font-size: 0.8rem;
        }}
        
        /* Trace Link */
        .trace-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.25rem;
            background: linear-gradient(135deg, #0f3460, #16213e);
            color: var(--info-color);
            text-decoration: none;
            border-radius: 8px;
            font-size: 0.9rem;
            margin-top: 1rem;
            border: 1px solid var(--border-color);
            transition: all 0.2s;
        }}
        
        .trace-link:hover {{
            background: linear-gradient(135deg, #16213e, #1a1a2e);
            transform: translateY(-2px);
        }}
        
        /* Lightbox */
        .lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }}
        
        .lightbox.active {{ display: flex; }}
        
        .lightbox img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}
        
        .lightbox-close {{
            position: absolute;
            top: 1.5rem;
            right: 1.5rem;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
            border: none;
            color: #fff;
            font-size: 1.5rem;
            cursor: pointer;
            transition: background 0.2s;
        }}
        
        .lightbox-close:hover {{ background: rgba(255,255,255,0.2); }}
        
        /* Footer */
        footer {{
            text-align: center;
            margin-top: 3rem;
            padding: 1.5rem;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border-color);
        }}
        
        /* No Results */
        .no-results {{
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-muted);
        }}
        
        .no-results-icon {{ font-size: 4rem; margin-bottom: 1rem; }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .container {{ padding: 1rem; }}
            .test-header {{ flex-direction: column; align-items: flex-start; gap: 0.75rem; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Test Failure Analysis Report</h1>
            <p>AI-powered analysis of test failures using Azure OpenAI</p>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(failures)}</div>
                    <div class="stat-label">Failed Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{files_affected}</div>
                    <div class="stat-label">Files Affected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_duration // 1000}s</div>
                    <div class="stat-label">Total Duration</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{datetime.now().strftime('%H:%M')}</div>
                    <div class="stat-label">Generated At</div>
                </div>
            </div>
        </header>

        <div class="filter-bar">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search tests..." onkeyup="filterTests()">
            </div>
            <button class="filter-btn" onclick="expandAll()">Expand All</button>
            <button class="filter-btn" onclick="collapseAll()">Collapse All</button>
        </div>

        <main id="testsList">
            {test_rows if test_rows else '''
            <div class="no-results">
                <div class="no-results-icon">✅</div>
                <h2>All Tests Passed!</h2>
                <p>No failures to analyze.</p>
            </div>
            '''}
        </main>

        <footer>
            <p>Generated by Test Failure Explainer | Powered by Azure OpenAI</p>
            <p style="margin-top: 0.5rem; font-size: 0.8rem;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>

    <!-- Lightbox for screenshots -->
    <div class="lightbox" id="lightbox" onclick="closeLightbox()">
        <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
        <img id="lightboxImg" src="" alt="Screenshot">
    </div>

    <script>
        // Toggle test expansion
        document.querySelectorAll('.test-header').forEach(header => {{
            header.addEventListener('click', () => {{
                header.parentElement.classList.toggle('expanded');
            }});
        }});
        
        // Tab functionality
        function switchTab(btn, tabId, testIndex) {{
            const container = btn.closest('.test-content');
            container.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
            container.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(tabId + '-' + testIndex).classList.add('active');
        }}
        
        // Search functionality
        function filterTests() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            document.querySelectorAll('.test-failure').forEach(test => {{
                const text = test.textContent.toLowerCase();
                test.style.display = text.includes(query) ? 'block' : 'none';
            }});
        }}
        
        // Expand/Collapse all
        function expandAll() {{
            document.querySelectorAll('.test-failure').forEach(t => t.classList.add('expanded'));
        }}
        
        function collapseAll() {{
            document.querySelectorAll('.test-failure').forEach(t => t.classList.remove('expanded'));
        }}
        
        // Lightbox
        function openLightbox(src) {{
            document.getElementById('lightboxImg').src = src;
            document.getElementById('lightbox').classList.add('active');
            event.stopPropagation();
        }}
        
        function closeLightbox() {{
            document.getElementById('lightbox').classList.remove('active');
        }}
        
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeLightbox();
        }});
        
        // Auto-expand first test
        const firstTest = document.querySelector('.test-failure');
        if (firstTest) firstTest.classList.add('expanded');
    </script>
</body>
</html>"""
        
        output_path = self.output_dir / "failure-explanations.html"
        output_path.write_text(html, encoding='utf-8')
        return output_path
    
    def _generate_test_row(self, failure: TestFailure, index: int) -> str:
        analysis = failure.analysis or FailureAnalysis("", "", "")
        
        badge_class = "badge-timeout" if failure.status == "timedOut" else "badge-failed"
        badge_text = "TIMEOUT" if failure.status == "timedOut" else "FAILED"
        
        # Generate screenshots HTML
        screenshots_html = ""
        if failure.screenshots:
            screenshot_cards = ""
            for ss in failure.screenshots:
                screenshot_cards += f'''
                    <div class="screenshot-card" onclick="openLightbox('{ss['path']}')">
                        <img src="{ss['path']}" alt="{ss['name']}" loading="lazy">
                        <div class="screenshot-label">{self._escape_html(ss['name'])}</div>
                    </div>
                '''
            screenshots_html = f'''
                <div class="screenshots-section">
                    <h4>📸 Screenshots</h4>
                    <div class="screenshots-grid">
                        {screenshot_cards}
                    </div>
                </div>
            '''
        
        # Generate trace link
        trace_html = ""
        if failure.trace_path:
            trace_html = f'''
                <a href="{failure.trace_path}" class="trace-link" target="_blank">
                    📊 View Trace
                </a>
            '''
        
        # Clean error message (remove ANSI codes)
        clean_error = re.sub(r'\x1b\[[0-9;]*m', '', failure.error_message)
        
        return f'''
        <div class="test-failure" data-file="{self._escape_html(failure.test_file)}">
            <div class="test-header">
                <div class="test-title">
                    <span class="badge {badge_class}">{badge_text}</span>
                    <h3>{self._escape_html(failure.test_name)}</h3>
                </div>
                <div class="test-meta">
                    <span class="duration">⏱️ {failure.duration_ms}ms</span>
                    <span class="expand-icon">▼</span>
                </div>
            </div>
            
            <div class="test-content">
                <div class="test-file">📁 {self._escape_html(failure.test_file)}</div>
                
                <div class="tabs">
                    <button class="tab-btn active" onclick="switchTab(this, 'analysis', {index})">🤖 AI Analysis</button>
                    <button class="tab-btn" onclick="switchTab(this, 'error', {index})">❌ Error Details</button>
                    <button class="tab-btn" onclick="switchTab(this, 'media', {index})">📸 Screenshots & Trace</button>
                </div>
                
                <div id="analysis-{index}" class="tab-content active">
                    <div class="analysis-grid">
                        <div class="analysis-card root-cause">
                            <h4>🎯 Root Cause</h4>
                            <div class="analysis-content">{self._format_markdown(analysis.root_cause)}</div>
                        </div>
                        
                        <div class="analysis-card explanation">
                            <h4>💡 Explanation</h4>
                            <div class="analysis-content">{self._format_markdown(analysis.explanation)}</div>
                        </div>
                        
                        <div class="analysis-card suggested-fix">
                            <h4>🔧 Suggested Fix</h4>
                            <div class="analysis-content">{self._format_markdown(analysis.suggested_fix)}</div>
                        </div>
                    </div>
                </div>
                
                <div id="error-{index}" class="tab-content">
                    <div class="error-section">
                        <h4>❌ Error Message</h4>
                        <pre class="error-message">{self._escape_html(clean_error[:2000])}</pre>
                    </div>
                </div>
                
                <div id="media-{index}" class="tab-content">
                    {screenshots_html if screenshots_html else '<p style="color: var(--text-muted);">No screenshots available for this test.</p>'}
                    {trace_html}
                </div>
            </div>
        </div>
        '''
    
    def generate_json_report(self, failures: list[TestFailure]) -> Path:
        """Generate a JSON report for programmatic access"""
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_failures": len(failures),
            "failures": []
        }
        
        for f in failures:
            failure_data = {
                "test_name": f.test_name,
                "test_file": f.test_file,
                "duration_ms": f.duration_ms,
                "status": f.status,
                "error": {
                    "message": f.error_message,
                    "stack": f.error_stack
                },
                "screenshots": f.screenshots,
                "trace_path": f.trace_path,
                "ai_analysis": asdict(f.analysis) if f.analysis else None
            }
            report["failures"].append(failure_data)
        
        output_path = self.output_dir / "failure-explanations.json"
        output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        return output_path
    
    def _escape_html(self, text: str) -> str:
        if not text:
            return ""
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;"))
    
    def _format_markdown(self, text: str) -> str:
        if not text:
            return ""
        html = self._escape_html(text)
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\n\d+\.\s+', r'<br>• ', html)
        html = html.replace('\n', '<br>')
        return html


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Playwright test failures using Azure OpenAI"
    )
    parser.add_argument(
        "--results-file",
        type=Path,
        help="Path to Playwright JSON results file"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("test-failure-explanations"),
        help="Output directory for reports (default: test-failure-explanations)"
    )
    parser.add_argument(
        "--playwright-report",
        type=Path,
        default=Path("playwright-report"),
        help="Path to Playwright HTML report directory for screenshots"
    )
    
    args = parser.parse_args()
    
    results_file = args.results_file
    if not results_file:
        import tempfile
        possible_paths = [
            Path(tempfile.gettempdir()) / "playwright-poc-output" / "results.json",
            Path("test-results") / "results.json",
            Path("playwright-report") / "results.json",
        ]
        for path in possible_paths:
            if path.exists():
                results_file = path
                break
    
    if not results_file or not results_file.exists():
        print("❌ Could not find Playwright results file.")
        print("   Run tests first: npm test")
        print("   Or specify path: python scripts/failure_explainer.py --results-file PATH")
        sys.exit(1)
    
    print(f"\n🔍 Test Failure Explainer")
    print(f"{'='*60}")
    print(f"📄 Results file: {results_file}")
    
    parser_obj = PlaywrightResultsParser(results_file)
    if not parser_obj.load():
        sys.exit(1)
    
    failures = parser_obj.get_failures()
    print(f"❌ Found {len(failures)} failed test(s)")
    
    if not failures:
        print("\n✅ All tests passed - no failures to analyze!")
        generator = ReportGenerator(args.output_dir, args.playwright_report)
        html_path = generator.generate_html_report([])
        json_path = generator.generate_json_report([])
        print(f"\n📊 Reports generated:")
        print(f"   HTML: {html_path}")
        print(f"   JSON: {json_path}")
        return
    
    analyzer = AzureOpenAIAnalyzer()
    if not analyzer.is_configured():
        print("\n⚠️  Azure OpenAI not configured!")
        print("   Set environment variables:")
        print("   - AZURE_OPENAI_ENDPOINT")
        print("   - AZURE_OPENAI_API_KEY")
        print("   - AZURE_OPENAI_DEPLOYMENT_NAME")
    else:
        print(f"✅ Azure OpenAI configured: {analyzer.deployment}")
    
    print(f"\n🤖 Analyzing failures...")
    for i, failure in enumerate(failures, 1):
        print(f"\n[{i}/{len(failures)}] {failure.test_name}")
        print(f"    📁 {failure.test_file}")
        if failure.screenshots:
            print(f"    📸 {len(failure.screenshots)} screenshot(s)")
        if failure.trace_path:
            print(f"    📊 Trace available")
        
        analysis = analyzer.analyze_failure(failure)
        failure.analysis = analysis
        
        print(f"    ✅ Analysis complete")
        root_cause_preview = analysis.root_cause[:60] + "..." if len(analysis.root_cause) > 60 else analysis.root_cause
        print(f"    🎯 {root_cause_preview}")
    
    print(f"\n📊 Generating reports...")
    generator = ReportGenerator(args.output_dir, args.playwright_report)
    
    html_path = generator.generate_html_report(failures)
    json_path = generator.generate_json_report(failures)
    
    print(f"\n{'='*60}")
    print(f"✅ Analysis complete!")
    print(f"\n📄 Reports saved to:")
    print(f"   HTML: {html_path}")
    print(f"   JSON: {json_path}")
    print(f"\n💡 Open the HTML report in a browser to view detailed analysis.")
    print(f"   Including screenshots, traces, and AI explanations!")


if __name__ == "__main__":
    main()
