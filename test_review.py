"""
Test script for Code Review Agent System.

Tests the orchestrator with sample code containing various issues.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path.parent))

from backend.core.orchestrator import CodeReviewOrchestrator  # noqa: E402
from backend.core.report_generator import ReportGenerator  # noqa: E402

# Sample code with various issues for testing
SAMPLE_CODE = """
import os
import sys

# Hardcoded password - security issue
PASSWORD = "admin123"

def process_user_data(user_input):
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    result = execute_query(query)
    return result

def calculate_total(items):
    total = 0
    for i in range(len(items)):
        for j in range(len(items)):
            total += items[i] * items[j]  # O(n^2) - performance issue
    return total

def getUserData(id):
    # Naming convention issue (should be snake_case)
    # Missing docstring
    data = fetch_data(id)
    return data

class UserManager:
    def __init__(self):
        self.users = []
        self.admin_users = []
        self.regular_users = []
        self.premium_users = []
        self.free_users = []
        # Too many responsibilities - best practices issue
    
    def add_user(self, user):
        self.users.append(user)
    
    def remove_user(self, user):
        self.users.remove(user)
    
    def get_user(self, id):
        for user in self.users:  # Inefficient search
            if user.id == id:
                return user
        return None

def main():
    # Magic numbers
    if len(users) > 100:
        process_batch(users)
    
    # String concatenation in loop
    result = ""
    for item in items:
        result += str(item)  # Performance issue
"""


def main():
    """Run a test code review."""
    print("=" * 70)
    print("Code Review Agent - Test Run")
    print("=" * 70)
    print()

    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not set. Using placeholder.")
        print("Set your API key in .env file for actual reviews.")
        print()

    try:
        # Initialize orchestrator
        print("Initializing orchestrator...")
        orchestrator = CodeReviewOrchestrator()
        print("Orchestrator initialized successfully!")
        print()

        # Run review
        print("Running code review on sample code...")
        print("-" * 70)
        results = orchestrator.review(code=SAMPLE_CODE, language="python")
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

        # Generate and display report
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

        print(f"Report saved to: {report_path}")
        print()
        print("=" * 70)
        print("REPORT PREVIEW (first 100 lines)")
        print("=" * 70)
        print()
        print("\n".join(report.split("\n")[:100]))
        if len(report.split("\n")) > 100:
            print("\n... (report truncated, see full report in file)")

        print()
        print("=" * 70)
        print("Test completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"Error during review: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
