"""
Dry-run test for Code Review Agent System.

Tests the system structure and tools without requiring API calls.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path.parent))

import warnings  # noqa: E402

from backend.tools.ast_analyzer import ASTAnalyzer  # noqa: E402
from backend.tools.dependency_checker import DependencyChecker  # noqa: E402
from backend.tools.metrics_calculator import MetricsCalculator  # noqa: E402

# Silence LangChain deprecation messages during tests (if langchain is present)
warnings.filterwarnings(
    "ignore",
    message=r".*Importing chat models from langchain is deprecated.*",
)

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
    
    def add_user(self, user):
        self.users.append(user)
    
    def get_user(self, id):
        for user in self.users:  # Inefficient search
            if user.id == id:
                return user
        return None
"""


def test_ast_analyzer():
    """Test AST analyzer."""
    print("Testing AST Analyzer...")
    print("-" * 70)

    analyzer = ASTAnalyzer()
    result = analyzer.parse(SAMPLE_CODE, "python")

    if result.get("valid"):
        print("[OK] Code parsed successfully")
        print(f"  Functions found: {len(result.get('functions', []))}")
        print(f"  Classes found: {len(result.get('classes', []))}")
        print(f"  Imports found: {len(result.get('imports', []))}")
        print(f"  Complexity: {result.get('complexity', {})}")

        print("\nFunctions:")
        for func in result.get("functions", []):
            print(f"  - {func['name']} (line {func['line']}, {func['args']} args)")

        print("\nClasses:")
        for cls in result.get("classes", []):
            print(
                f"  - {cls['name']} (line {cls['line']}, {cls['method_count']} methods)"
            )
    else:
        print(f"[ERROR] Parse error: {result.get('error')}")

    print()
    assert result.get("valid") is True
    assert isinstance(result.get("functions"), list)
    assert isinstance(result.get("classes"), list)
    assert isinstance(result.get("imports"), list)


def test_dependency_checker():
    """Test dependency checker."""
    print("Testing Dependency Checker...")
    print("-" * 70)

    checker = DependencyChecker()
    result = checker.check_dependencies(SAMPLE_CODE, "python")

    print(f"[OK] Dependencies found: {result.get('dependency_count', 0)}")
    for dep in result.get("dependencies", []):
        print(f"  - {dep['module']} (line {dep['line']})")

    print()
    assert isinstance(result.get("dependencies"), list)
    assert result.get("dependency_count", 0) >= 0


def test_metrics_calculator():
    """Test metrics calculator."""
    print("Testing Metrics Calculator...")
    print("-" * 70)

    calculator = MetricsCalculator()
    result = calculator.calculate_metrics(SAMPLE_CODE, "python")

    print("[OK] Metrics calculated:")
    print(f"  Total lines: {result.get('total_lines', 0)}")
    print(f"  Code lines: {result.get('code_lines', 0)}")
    print(f"  Comment lines: {result.get('comment_lines', 0)}")
    print(f"  Blank lines: {result.get('blank_lines', 0)}")
    print(f"  Average line length: {result.get('average_line_length', 0):.1f}")

    print()
    assert result.get("total_lines", 0) > 0
    assert result.get("code_lines", 0) >= 0


def test_security_patterns():
    """Test security pattern detection."""
    print("Testing Security Pattern Detection...")
    print("-" * 70)

    code_lower = SAMPLE_CODE.lower()
    security_patterns = {
        "hardcoded_secrets": ["password", "secret", "api_key"],
        "sql_injection": ["execute(", "query(", "sql"],
        "eval_usage": ["eval(", "exec("],
    }

    found_patterns = []
    for pattern_type, patterns in security_patterns.items():
        for pattern in patterns:
            if pattern in code_lower:
                lines = [
                    i + 1
                    for i, line in enumerate(SAMPLE_CODE.split("\n"))
                    if pattern in line.lower()
                ]
                found_patterns.append(
                    {"type": pattern_type, "pattern": pattern, "lines": lines[:3]}
                )

    if found_patterns:
        print(f"[OK] Security patterns detected: {len(found_patterns)}")
        for pattern in found_patterns:
            print(
                f"  - {pattern['type']}: '{pattern['pattern']}' at lines {pattern['lines']}"
            )
    else:
        print("[OK] No obvious security patterns detected")

    print()
    # At minimum the sample includes a hardcoded password and SQL pattern
    assert isinstance(found_patterns, list)
    assert any(p["type"] == "hardcoded_secrets" for p in found_patterns) or any(
        p["type"] == "sql_injection" for p in found_patterns
    )


def main():
    """Run all tests."""
    print("=" * 70)
    print("Code Review Agent - Dry Run Test")
    print("=" * 70)
    print()
    print("Testing system components without API calls...")
    print()

    try:
        # Test AST analyzer
        ast_result = test_ast_analyzer()

        # Test dependency checker
        dep_result = test_dependency_checker()

        # Test metrics calculator
        _ = test_metrics_calculator()

        # Test security patterns
        test_security_patterns()

        # Summary
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"[OK] AST Analyzer: {'PASS' if ast_result.get('valid') else 'FAIL'}")
        print(
            f"[OK] Dependency Checker: PASS ({dep_result.get('dependency_count', 0)} dependencies)"
        )
        print("[OK] Metrics Calculator: PASS")
        print("[OK] Security Pattern Detection: PASS")
        print()
        print("All core tools are working correctly!")
        print()
        print("Note: To test with full LLM agents, set GEMINI_API_KEY in .env file")
        print("      and run: python test_review.py")
        print()

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
