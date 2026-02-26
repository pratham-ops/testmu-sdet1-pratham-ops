"""
Test Failure Explainer using Azure OpenAI

This script analyzes Playwright test failures and generates AI-powered explanations
using Azure OpenAI. It reads the JSON test results, sends failure context to the LLM,
and generates comprehensive reports.

Usage:
    python scripts/failure_explainer.py [--results-file PATH] [--output-dir PATH]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict

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
                # max_tokens=1500,
                # temperature=0.3
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
        
        # Try to extract sections
        import re
        
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
        
        # Fallback if parsing failed
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
        
        # Playwright JSON structure has suites containing specs containing tests
        def process_suite(suite: dict, parent_file: str = ""):
            suite_failures = []
            
            file_path = suite.get('file', parent_file)
            
            # Process specs (test cases)
            for spec in suite.get('specs', []):
                for test in spec.get('tests', []):
                    for result in test.get('results', []):
                        status = result.get('status', '')
                        if status in ['failed', 'timedOut']:
                            error_msg = ""
                            error_stack = ""
                            
                            # Extract error information
                            if result.get('errors'):
                                error = result['errors'][0]
                                error_msg = error.get('message', '')
                                error_stack = error.get('stack', '')
                            elif result.get('error'):
                                error = result['error']
                                error_msg = error.get('message', '')
                                error_stack = error.get('stack', '')
                            
                            failure = TestFailure(
                                test_name=spec.get('title', 'Unknown'),
                                test_file=file_path,
                                duration_ms=result.get('duration', 0),
                                error_message=error_msg,
                                error_stack=error_stack,
                                status=status,
                                attachments=result.get('attachments', [])
                            )
                            suite_failures.append(failure)
            
            # Process nested suites
            for child_suite in suite.get('suites', []):
                suite_failures.extend(process_suite(child_suite, file_path))
            
            return suite_failures
        
        # Process all top-level suites
        for suite in self.results.get('suites', []):
            failures.extend(process_suite(suite))
        
        return failures


class ReportGenerator:
    """Generates HTML and JSON reports for failure analysis"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_report(self, failures: list[TestFailure]) -> Path:
        """Generate an HTML report with all failure analyses"""
        
        test_rows = "\n".join([
            self._generate_test_row(f) for f in failures
        ])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Failure Analysis Report</title>
    <style>
        :root {{
            --bg-color: #1a1a2e;
            --card-bg: #16213e;
            --text-color: #eee;
            --accent-color: #e94560;
            --success-color: #4ade80;
            --warning-color: #fbbf24;
            --border-color: #0f3460;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 2rem;
        }}
        
        .container {{ max-width: 1200px; margin: 0 auto; }}
        
        header {{
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: linear-gradient(135deg, var(--card-bg) 0%, #1a1a2e 100%);
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }}
        
        header h1 {{ color: var(--accent-color); margin-bottom: 0.5rem; }}
        
        .summary {{
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin-top: 1rem;
        }}
        
        .summary-item {{ text-align: center; }}
        .summary-item .value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent-color);
        }}
        
        .test-failure {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
        }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        
        .test-header h3 {{ color: var(--accent-color); }}
        .duration {{ color: var(--warning-color); font-size: 0.9rem; }}
        .test-file {{ color: #888; font-size: 0.9rem; margin-bottom: 1rem; }}
        
        .error-section {{
            background: rgba(233, 69, 96, 0.1);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid var(--accent-color);
        }}
        
        .error-section h4 {{ color: var(--accent-color); margin-bottom: 0.5rem; }}
        
        .error-message {{
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            word-break: break-word;
            color: #ff8fa3;
        }}
        
        .analysis-section {{ display: grid; gap: 1rem; }}
        
        .root-cause, .explanation, .suggested-fix {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1rem;
        }}
        
        .root-cause h4 {{ color: #f472b6; }}
        .explanation h4 {{ color: #60a5fa; }}
        .suggested-fix h4 {{ color: var(--success-color); }}
        
        .root-cause {{ border-left: 4px solid #f472b6; }}
        .explanation {{ border-left: 4px solid #60a5fa; }}
        .suggested-fix {{ border-left: 4px solid var(--success-color); }}
        
        h4 {{ margin-bottom: 0.5rem; }}
        .content {{ font-size: 0.95rem; white-space: pre-wrap; }}
        
        footer {{
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            color: #666;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Test Failure Analysis Report</h1>
            <p>AI-powered analysis of test failures using Azure OpenAI</p>
            <div class="summary">
                <div class="summary-item">
                    <div class="value">{len(failures)}</div>
                    <div>Failed Tests</div>
                </div>
                <div class="summary-item">
                    <div class="value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                    <div>Generated</div>
                </div>
            </div>
        </header>

        <main>
            {test_rows if test_rows else '<p style="text-align: center; color: #4ade80;">✅ All tests passed - no failures to analyze!</p>'}
        </main>

        <footer>
            Generated by Failure Explainer | Powered by Azure OpenAI
        </footer>
    </div>
</body>
</html>"""
        
        output_path = self.output_dir / "failure-explanations.html"
        output_path.write_text(html, encoding='utf-8')
        return output_path
    
    def _generate_test_row(self, failure: TestFailure) -> str:
        analysis = failure.analysis or FailureAnalysis("", "", "")
        
        return f"""
        <div class="test-failure">
            <div class="test-header">
                <h3>{self._escape_html(failure.test_name)}</h3>
                <span class="duration">{failure.duration_ms}ms</span>
            </div>
            <div class="test-file">{self._escape_html(failure.test_file)}</div>
            
            <div class="error-section">
                <h4>❌ Error</h4>
                <pre class="error-message">{self._escape_html(failure.error_message[:1000])}</pre>
            </div>

            <div class="analysis-section">
                <div class="root-cause">
                    <h4>🎯 Root Cause</h4>
                    <div class="content">{self._escape_html(analysis.root_cause)}</div>
                </div>
                
                <div class="explanation">
                    <h4>💡 Explanation</h4>
                    <div class="content">{self._escape_html(analysis.explanation)}</div>
                </div>
                
                <div class="suggested-fix">
                    <h4>🔧 Suggested Fix</h4>
                    <div class="content">{self._escape_html(analysis.suggested_fix)}</div>
                </div>
            </div>
        </div>
        """
    
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
    
    args = parser.parse_args()
    
    # Find results file
    results_file = args.results_file
    if not results_file:
        # Try common locations
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
    print(f"{'='*50}")
    print(f"📄 Results file: {results_file}")
    
    # Parse results
    parser_obj = PlaywrightResultsParser(results_file)
    if not parser_obj.load():
        sys.exit(1)
    
    failures = parser_obj.get_failures()
    print(f"❌ Found {len(failures)} failed test(s)")
    
    if not failures:
        print("\n✅ All tests passed - no failures to analyze!")
        
        # Still generate empty report
        generator = ReportGenerator(args.output_dir)
        html_path = generator.generate_html_report([])
        json_path = generator.generate_json_report([])
        print(f"\n📊 Reports generated:")
        print(f"   HTML: {html_path}")
        print(f"   JSON: {json_path}")
        return
    
    # Initialize Azure OpenAI analyzer
    analyzer = AzureOpenAIAnalyzer()
    if not analyzer.is_configured():
        print("\n⚠️  Azure OpenAI not configured!")
        print("   Set environment variables:")
        print("   - AZURE_OPENAI_ENDPOINT")
        print("   - AZURE_OPENAI_API_KEY")
        print("   - AZURE_OPENAI_DEPLOYMENT_NAME (optional, default: gpt-4)")
    else:
        print(f"✅ Azure OpenAI configured: {analyzer.deployment}")
    
    # Analyze each failure
    print(f"\n🤖 Analyzing failures...")
    for i, failure in enumerate(failures, 1):
        print(f"\n[{i}/{len(failures)}] {failure.test_name}")
        print(f"    File: {failure.test_file}")
        
        analysis = analyzer.analyze_failure(failure)
        failure.analysis = analysis
        
        print(f"    ✅ Analysis complete")
        print(f"    🎯 Root Cause: {analysis.root_cause[:80]}...")
    
    # Generate reports
    print(f"\n📊 Generating reports...")
    generator = ReportGenerator(args.output_dir)
    
    html_path = generator.generate_html_report(failures)
    json_path = generator.generate_json_report(failures)
    
    print(f"\n{'='*50}")
    print(f"✅ Analysis complete!")
    print(f"\n📄 Reports saved to:")
    print(f"   HTML: {html_path}")
    print(f"   JSON: {json_path}")
    print(f"\n💡 Open the HTML report in a browser to view detailed analysis.")


if __name__ == "__main__":
    main()
