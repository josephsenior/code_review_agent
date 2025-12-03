"""
Mock test for Code Review Agent System.

Simulates full agent workflow with mock responses to test the orchestrator
and report generator without requiring API calls.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path.parent))

from backend.core.orchestrator import CodeReviewOrchestrator
from backend.core.report_generator import ReportGenerator


# Sample code with various issues
SAMPLE_CODE = """
import os

# Hardcoded password
PASSWORD = "admin123"

def process_user_data(user_input):
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    return execute_query(query)

def calculate_total(items):
    total = 0
    for i in range(len(items)):
        for j in range(len(items)):
            total += items[i] * items[j]
    return total

def getUserData(id):
    data = fetch_data(id)
    return data
"""


def create_mock_agent_response(agent_name: str) -> str:
    """Create mock LLM responses for different agents."""
    responses = {
        "syntax": """Analysis Results:

The code has valid Python syntax. No syntax errors detected.
All functions and classes are properly defined.
Indentation is correct throughout the code.""",
        
        "security": """Security Analysis:

CRITICAL: Hardcoded password detected at line 4
- Issue: PASSWORD = "admin123" contains hardcoded credentials
- Severity: Critical
- Recommendation: Use environment variables or secure credential storage

HIGH: SQL injection vulnerability at line 8
- Issue: String concatenation in SQL query allows injection
- Severity: High
- Recommendation: Use parameterized queries or ORM

Line 8: query = "SELECT * FROM users WHERE name = '" + user_input + "'" """,
        
        "performance": """Performance Analysis:

HIGH IMPACT: Nested loops causing O(n^2) complexity at lines 12-14
- Issue: calculate_total function uses nested loops
- Current complexity: O(n^2)
- Recommendation: Optimize algorithm or use built-in functions
- Expected improvement: Significant for large datasets

Line 12-14: Nested loop structure""",
        
        "style": """Style Review:

MAJOR: Naming convention violation at line 16
- Issue: Function getUserData uses camelCase instead of snake_case
- PEP 8 violation
- Recommendation: Rename to get_user_data

MINOR: Line length issues
- Some lines exceed recommended length
- Recommendation: Break long lines""",
        
        "best_practices": """Best Practices Review:

MEDIUM: Missing docstrings
- Functions lack documentation
- Recommendation: Add docstrings following Google or NumPy style

MEDIUM: Magic numbers
- Hardcoded values without constants
- Recommendation: Define named constants""",
        
        "documentation": """Documentation Review:

HIGH: Missing docstrings for all functions
- Functions: process_user_data, calculate_total, getUserData
- Recommendation: Add comprehensive docstrings

Documentation Coverage: 0%
- No functions have docstrings
- No classes have docstrings"""
    }
    
    return responses.get(agent_name, "Analysis complete.")


def test_with_mocks():
    """Test orchestrator with mocked agent responses."""
    print("=" * 70)
    print("Code Review Agent - Mock Test (Full Workflow)")
    print("=" * 70)
    print()
    
    # Mock the LLM chain invoke method
    def mock_invoke(input_dict):
        """Mock LLM response based on input content."""
        input_text = input_dict.get("input", "")
        
        if "syntax" in input_text.lower() or "syntax error" in input_text.lower():
            return create_mock_agent_response("syntax")
        elif "security" in input_text.lower() or "vulnerability" in input_text.lower():
            return create_mock_agent_response("security")
        elif "performance" in input_text.lower() or "bottleneck" in input_text.lower():
            return create_mock_agent_response("performance")
        elif "style" in input_text.lower() or "pep" in input_text.lower():
            return create_mock_agent_response("style")
        elif "best practice" in input_text.lower() or "solid" in input_text.lower():
            return create_mock_agent_response("best_practices")
        elif "documentation" in input_text.lower() or "docstring" in input_text.lower():
            return create_mock_agent_response("documentation")
        else:
            return "Analysis complete."
    
    try:
        # Patch the base agent's _invoke method
        with patch('backend.agents.base_agent.BaseCodeReviewAgent._invoke', side_effect=mock_invoke):
            # Also need to set a dummy API key for initialization
            import os
            original_key = os.environ.get("OPENAI_API_KEY")
            os.environ["OPENAI_API_KEY"] = "test-key-for-mock"
            
            try:
                print("Initializing orchestrator with mocks...")
                orchestrator = CodeReviewOrchestrator()
                print("[OK] Orchestrator initialized")
                print()
                
                print("Running code review...")
                print("-" * 70)
                results = orchestrator.review(
                    code=SAMPLE_CODE,
                    language="python"
                )
                print("-" * 70)
                print()
                
                # Display summary
                summary = results.get("summary", {})
                print("=" * 70)
                print("REVIEW SUMMARY")
                print("=" * 70)
                print(f"Overall Score: {summary.get('overall_score', 0):.1f}/10")
                print(f"Overall Severity: {summary.get('overall_severity', 'none')}")
                print(f"Total Issues: {summary.get('total_issues', 0)}")
                print(f"  - Critical: {summary.get('critical_issues', 0)}")
                print(f"  - High: {summary.get('high_issues', 0)}")
                print(f"  - Medium: {summary.get('medium_issues', 0)}")
                print(f"  - Low: {summary.get('low_issues', 0)}")
                print()
                
                # Display agent scores
                scores = summary.get("scores", {})
                if scores:
                    print("Agent Scores:")
                    for agent, score in scores.items():
                        print(f"  - {agent.replace('_', ' ').title()}: {score:.1f}/10")
                    print()
                
                # Generate report
                print("=" * 70)
                print("GENERATING REPORT")
                print("=" * 70)
                print()
                
                report_generator = ReportGenerator()
                report = report_generator.generate_report(results, format_type="markdown")
                
                # Save report
                report_path = Path("test_review_report.md")
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(report)
                
                print(f"[OK] Report saved to: {report_path}")
                print()
                print("Report Preview:")
                print("-" * 70)
                print("\n".join(report.split("\n")[:80]))
                if len(report.split("\n")) > 80:
                    print("\n... (see full report in file)")
                print("-" * 70)
                
                print()
                print("=" * 70)
                print("[OK] Mock test completed successfully!")
                print("=" * 70)
                print()
                print("The system is working correctly!")
                print("To test with real API calls, set OPENAI_API_KEY and run:")
                print("  python test_review.py")
                
            finally:
                # Restore original API key
                if original_key:
                    os.environ["OPENAI_API_KEY"] = original_key
                elif "OPENAI_API_KEY" in os.environ:
                    del os.environ["OPENAI_API_KEY"]
        
    except Exception as e:
        print(f"Error during mock test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(test_with_mocks())

