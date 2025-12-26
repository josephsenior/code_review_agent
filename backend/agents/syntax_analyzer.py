"""
Syntax Analyzer Agent for Code Review.

Analyzes code for syntax errors, basic structure issues, and fundamental problems.
"""

from typing import Any, Dict

from ..tools.ast_analyzer import ASTAnalyzer
from .base_agent import BaseCodeReviewAgent


class SyntaxAnalyzerAgent(BaseCodeReviewAgent):
    """
    Agent specialized in detecting syntax errors and basic code structure issues.

    Uses AST parsing to validate syntax and identify fundamental problems.
    """

    def __init__(
        self, model_name: str = "gpt-4", temperature: float = 0.1, api_key: str = None
    ):
        """
        Initialize the Syntax Analyzer Agent.

        Args:
            model_name: Gemini model name
            temperature: LLM temperature (very low for syntax checking)
            api_key: Gemini API key
        """
        system_prompt = """You are a syntax analyzer for code review. Your role is to:
1. Identify syntax errors and basic structural issues
2. Check for missing imports or undefined references
3. Validate code structure and indentation
4. Identify basic type errors or obvious mistakes
5. Report any parsing or compilation issues

Be precise and focus only on syntax and basic structural problems. Don't comment on style or best practices - that's handled by other agents."""

        super().__init__(
            role="Syntax Analyzer",
            system_prompt=system_prompt,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
        )

        self.ast_analyzer = ASTAnalyzer()

    def review(self, code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
        """
        Review code for syntax errors and basic issues.

        Args:
            code: Source code to review
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Dictionary with syntax analysis results
        """
        # First, use AST analyzer for Python
        ast_result = {}
        if language.lower() == "python":
            ast_result = self.ast_analyzer.parse(code, language)

        # Prepare analysis prompt
        analysis_input = f"""Code to analyze ({language}):

```{language}
{code}
```

AST Analysis Results:
{self._format_ast_results(ast_result)}

Analyze this code for syntax errors and basic structural issues. Report:
1. Any syntax errors found
2. Missing imports or undefined references
3. Basic structural problems
4. Indentation issues
5. Any parsing or compilation problems

Format your response clearly, listing each issue with its line number if possible."""

        analysis_result = self._invoke(analysis_input)

        # Compile results
        issues = self._extract_issues(analysis_result, ast_result)

        return {
            "agent": self.role,
            "language": language,
            "syntax_valid": ast_result.get("valid", True) if ast_result else True,
            "issues": issues,
            "issue_count": len(issues),
            "ast_info": ast_result if ast_result else {},
            "analysis": analysis_result,
            "severity": "high" if issues else "none",
        }

    def _format_ast_results(self, ast_result: Dict[str, Any]) -> str:
        """Format AST results for the prompt."""
        if not ast_result:
            return "No AST analysis available."

        if not ast_result.get("valid"):
            return f"AST Parse Error: {ast_result.get('error', 'Unknown error')}"

        info = []
        info.append(f"Functions: {len(ast_result.get('functions', []))}")
        info.append(f"Classes: {len(ast_result.get('classes', []))}")
        info.append(f"Imports: {len(ast_result.get('imports', []))}")
        info.append(f"Complexity: {ast_result.get('complexity', {})}")

        return "\n".join(info)

    def _extract_issues(self, analysis_text: str, ast_result: Dict[str, Any]) -> list:
        """Extract issues from analysis text."""
        issues = []

        # If AST parsing failed, that's a critical issue
        if ast_result and not ast_result.get("valid"):
            issues.append(
                {
                    "type": "syntax_error",
                    "severity": "critical",
                    "message": ast_result.get("error", "Syntax error detected"),
                    "line": ast_result.get("line"),
                    "category": "syntax",
                }
            )

        # Parse LLM response for additional issues
        lines = analysis_text.split("\n")
        current_issue = None

        for line in lines:
            line_lower = line.lower()

            # Detect issue markers
            if any(
                keyword in line_lower
                for keyword in ["error", "issue", "problem", "warning"]
            ):
                if current_issue:
                    issues.append(current_issue)

                current_issue = {
                    "type": "syntax_issue",
                    "severity": "high" if "error" in line_lower else "medium",
                    "message": line.strip(),
                    "category": "syntax",
                }
            elif current_issue and ("line" in line_lower or ":" in line):
                # Try to extract line number
                try:
                    import re

                    line_match = re.search(r"line\s+(\d+)", line_lower)
                    if line_match:
                        current_issue["line"] = int(line_match.group(1))
                except Exception:
                    pass

        if current_issue:
            issues.append(current_issue)

        return issues
