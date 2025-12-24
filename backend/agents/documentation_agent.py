"""
Documentation Agent for Code Review.

Reviews code documentation quality, docstrings, comments, and README files.
"""

from typing import Any, Dict, List

from ..tools.ast_analyzer import ASTAnalyzer
from .base_agent import BaseCodeReviewAgent


class DocumentationAgent(BaseCodeReviewAgent):
    """
    Agent specialized in reviewing code documentation.
    
    Reviews:
    - Function/class docstrings
    - Inline comments
    - README quality
    - API documentation
    - Code clarity and self-documentation
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        api_key: str = None
    ):
        """
        Initialize the Documentation Agent.
        
        Args:
            model_name: Gemini model name
            temperature: LLM temperature
            api_key: Gemini API key
        """
        system_prompt = """You are a documentation quality reviewer. Your role is to:
1. Review function and class docstrings
2. Check comment quality and relevance
3. Identify missing documentation
4. Review code clarity (self-documenting code)
5. Check documentation consistency
6. Suggest documentation improvements

Focus on:
- Completeness of documentation
- Clarity and usefulness of docstrings
- Appropriate level of commenting
- Self-documenting code practices
- Documentation standards (Google style, NumPy style, etc.)"""
        
        super().__init__(
            role="Documentation Reviewer",
            system_prompt=system_prompt,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        self.ast_analyzer = ASTAnalyzer()
    
    def review(
        self,
        code: str,
        language: str = "python",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Review code for documentation quality.
        
        Args:
            code: Source code to review
            language: Programming language
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with documentation analysis results
        """
        # Analyze code structure
        ast_result = {}
        docstring_stats = {}
        
        if language.lower() == "python":
            ast_result = self.ast_analyzer.parse(code, language)
            if ast_result.get("valid"):
                docstring_stats = self._analyze_docstrings(ast_result, code)
        
        # Check documentation patterns
        doc_issues = self._check_documentation_patterns(code, language, docstring_stats)
        
        # Prepare documentation analysis prompt
        analysis_input = f"""Code to review for documentation quality ({language}):

```{language}
{code}
```

Documentation Statistics:
{self._format_docstring_stats(docstring_stats)}

Detected Documentation Issues:
{self._format_doc_issues(doc_issues)}

Review this code for documentation quality. Check for:
1. Missing function/class docstrings
2. Quality and completeness of existing docstrings
3. Inline comment quality and relevance
4. Code clarity and self-documentation
5. Documentation consistency
6. Appropriate level of documentation
7. Documentation standards adherence

For each issue found, provide:
- Issue type and severity
- Description of the documentation problem
- Location (function/class name or line number)
- Suggested improvement
- Documentation standard reference if applicable

Format your response clearly with actionable documentation improvements."""
        
        analysis_result = self._invoke(analysis_input)
        
        # Extract documentation issues
        issues = self._extract_documentation_issues(analysis_result, doc_issues)
        
        # Calculate documentation score
        doc_score = self._calculate_documentation_score(issues, docstring_stats)
        
        return {
            "agent": self.role,
            "language": language,
            "issues": issues,
            "issue_count": len(issues),
            "docstring_stats": docstring_stats,
            "documentation_score": doc_score,
            "analysis": analysis_result,
            "severity": "medium" if issues else "none"
        }
    
    def _analyze_docstrings(
        self,
        ast_result: Dict[str, Any],
        code: str
    ) -> Dict[str, Any]:
        """Analyze docstring coverage and quality."""
        import ast as ast_module
        
        stats = {
            "functions_with_docstrings": 0,
            "functions_without_docstrings": 0,
            "classes_with_docstrings": 0,
            "classes_without_docstrings": 0,
            "total_functions": 0,
            "total_classes": 0
        }
        
        if not ast_result.get("valid"):
            return stats
        
        try:
            tree = ast_result.get("ast_tree")
            if not tree:
                return stats
            
            # Count functions
            for node in ast_module.walk(tree):
                if isinstance(node, ast_module.FunctionDef):
                    stats["total_functions"] += 1
                    if ast_module.get_docstring(node):
                        stats["functions_with_docstrings"] += 1
                    else:
                        stats["functions_without_docstrings"] += 1
                
                elif isinstance(node, ast_module.ClassDef):
                    stats["total_classes"] += 1
                    if ast_module.get_docstring(node):
                        stats["classes_with_docstrings"] += 1
                    else:
                        stats["classes_without_docstrings"] += 1
            
            # Calculate coverage
            total_documented = (
                stats["functions_with_docstrings"] +
                stats["classes_with_docstrings"]
            )
            total_items = stats["total_functions"] + stats["total_classes"]
            
            if total_items > 0:
                stats["coverage_percentage"] = (total_documented / total_items) * 100
            else:
                stats["coverage_percentage"] = 0.0
            
        except Exception as e:
            print(f"Error analyzing docstrings: {e}")
        
        return stats
    
    def _check_documentation_patterns(
        self,
        code: str,
        language: str,
        docstring_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for documentation issues."""
        issues = []
        
        # Check docstring coverage
        coverage = docstring_stats.get("coverage_percentage", 100.0)
        if coverage < 50.0:
            issues.append({
                "type": "low_docstring_coverage",
                "severity": "high",
                "message": f"Low docstring coverage: {coverage:.1f}%",
                "suggestion": "Add docstrings to functions and classes"
            })
        elif coverage < 80.0:
            issues.append({
                "type": "moderate_docstring_coverage",
                "severity": "medium",
                "message": f"Moderate docstring coverage: {coverage:.1f}%",
                "suggestion": "Consider adding more docstrings"
            })
        
        # Check for TODO/FIXME comments without context
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            if ("todo" in line_lower or "fixme" in line_lower) and len(line.strip()) < 20:
                issues.append({
                    "type": "vague_todo",
                    "severity": "low",
                    "line": i,
                    "message": "TODO/FIXME comment lacks detail",
                    "suggestion": "Add more context to TODO/FIXME comments"
                })
        
        return issues
    
    def _format_docstring_stats(self, stats: Dict[str, Any]) -> str:
        """Format docstring statistics for the prompt."""
        if not stats:
            return "No documentation statistics available."
        
        return f"""Functions with docstrings: {stats.get('functions_with_docstrings', 0)}/{stats.get('total_functions', 0)}
Classes with docstrings: {stats.get('classes_with_docstrings', 0)}/{stats.get('total_classes', 0)}
Documentation Coverage: {stats.get('coverage_percentage', 0):.1f}%"""
    
    def _format_doc_issues(self, issues: List[Dict[str, Any]]) -> str:
        """Format documentation issues for the prompt."""
        if not issues:
            return "No obvious documentation issues detected."
        
        formatted = []
        for issue in issues[:10]:
            line_info = f" (line {issue['line']})" if issue.get("line") else ""
            formatted.append(
                f"- {issue['type']}{line_info}: {issue['message']} "
                f"(severity: {issue['severity']})"
            )
        
        return "\n".join(formatted)
    
    def _extract_documentation_issues(
        self,
        analysis_text: str,
        pattern_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract documentation issues from analysis text."""
        issues = pattern_issues.copy()
        
        # Parse LLM response
        lines = analysis_text.split("\n")
        current_issue = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect documentation issue markers
            if any(keyword in line_lower for keyword in [
                "docstring", "documentation", "comment", "missing", "unclear"
            ]):
                if current_issue:
                    issues.append(current_issue)
                
                # Determine severity
                severity = "medium"
                if "missing" in line_lower or "critical" in line_lower:
                    severity = "high"
                elif "minor" in line_lower or "suggestion" in line_lower:
                    severity = "low"
                
                current_issue = {
                    "type": "documentation_issue",
                    "severity": severity,
                    "message": line.strip(),
                    "category": "documentation"
                }
            elif current_issue:
                # Try to extract location
                if "line" in line_lower or "function" in line_lower or "class" in line_lower:
                    try:
                        import re
                        line_match = re.search(r'line\s+(\d+)', line_lower)
                        if line_match:
                            current_issue["line"] = int(line_match.group(1))
                    except Exception:
                        pass
                current_issue["message"] += " " + line.strip()
        
        if current_issue:
            issues.append(current_issue)
        
        return issues
    
    def _calculate_documentation_score(
        self,
        issues: List[Dict[str, Any]],
        docstring_stats: Dict[str, Any]
    ) -> float:
        """Calculate documentation score (0-10, higher is better)."""
        score = 10.0
        
        # Deduct points for issues
        for issue in issues:
            severity = issue.get("severity", "medium")
            if severity == "high":
                score -= 2.0
            elif severity == "medium":
                score -= 1.0
            else:
                score -= 0.5
        
        # Deduct points for low coverage
        coverage = docstring_stats.get("coverage_percentage", 100.0)
        if coverage < 50.0:
            score -= 3.0
        elif coverage < 80.0:
            score -= 1.5
        
        return max(0.0, score)
