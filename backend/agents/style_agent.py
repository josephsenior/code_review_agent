"""
Style Agent for Code Review.

Reviews code style, conventions, and formatting according to language-specific standards.
"""

from typing import Any, Dict, List

from .base_agent import BaseCodeReviewAgent


class StyleAgent(BaseCodeReviewAgent):
    """
    Agent specialized in code style and convention checking.
    
    Reviews:
    - PEP 8 (Python)
    - ESLint/Prettier rules (JavaScript/TypeScript)
    - Naming conventions
    - Code formatting
    - Style consistency
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        api_key: str = None
    ):
        """
        Initialize the Style Agent.
        
        Args:
            model_name: Gemini model name
            temperature: LLM temperature
            api_key: Gemini API key
        """
        system_prompt = """You are a code style reviewer. Your role is to:
1. Check code style against language-specific conventions (PEP 8 for Python, etc.)
2. Review naming conventions (variables, functions, classes)
3. Check code formatting and indentation
4. Identify style inconsistencies
5. Suggest style improvements
6. Ensure code readability

Be specific about style violations and provide clear suggestions for improvement.
Focus on readability and maintainability."""
        
        super().__init__(
            role="Style Reviewer",
            system_prompt=system_prompt,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        self.style_guides = self._load_style_guides()
    
    def review(
        self,
        code: str,
        language: str = "python",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Review code for style issues.
        
        Args:
            code: Source code to review
            language: Programming language
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with style analysis results
        """
        # Check for style patterns
        style_issues = self._check_style_patterns(code, language)
        
        # Prepare style analysis prompt
        style_guide = self.style_guides.get(language.lower(), "general coding standards")
        
        analysis_input = f"""Code to review for style issues ({language}):

```{language}
{code}
```

Style Guide: {style_guide}

Detected Style Patterns:
{self._format_style_issues(style_issues)}

Review this code for style violations. Check for:
1. Naming conventions (variables, functions, classes)
2. Code formatting and indentation
3. Line length and spacing
4. Import organization
5. Style consistency throughout the code
6. Readability issues

For each style issue found, provide:
- Issue type and severity (minor/major)
- Description of the style violation
- Location (line number if possible)
- Suggested improvement
- Reference to style guide if applicable

Format your response clearly with actionable style improvements."""
        
        analysis_result = self._invoke(analysis_input)
        
        # Extract style issues
        issues = self._extract_style_issues(analysis_result, style_issues)
        
        # Calculate style score
        style_score = self._calculate_style_score(issues)
        
        return {
            "agent": self.role,
            "language": language,
            "style_guide": style_guide,
            "issues": issues,
            "issue_count": len(issues),
            "major_count": len([i for i in issues if i.get("severity") == "major"]),
            "style_score": style_score,
            "analysis": analysis_result,
            "severity": "major" if issues else "none"
        }
    
    def _load_style_guides(self) -> Dict[str, str]:
        """Load style guide references for different languages."""
        return {
            "python": "PEP 8 - Python Enhancement Proposal 8",
            "javascript": "ESLint and Prettier standards",
            "typescript": "TypeScript style guide and ESLint",
            "java": "Google Java Style Guide",
            "cpp": "Google C++ Style Guide",
            "go": "Effective Go and Go Code Review Comments"
        }
    
    def _check_style_patterns(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Check code for common style issues."""
        issues = []
        lines = code.split("\n")
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            
            # Check line length (common across languages)
            if len(line) > 100:
                issues.append({
                    "type": "line_length",
                    "severity": "minor",
                    "line": i,
                    "message": f"Line {i} exceeds 100 characters ({len(line)} chars)"
                })
            
            # Language-specific checks
            if language.lower() == "python":
                # Check for mixed tabs/spaces (basic check)
                if "\t" in line and "    " in line:
                    issues.append({
                        "type": "mixed_indentation",
                        "severity": "major",
                        "line": i,
                        "message": "Mixed tabs and spaces detected"
                    })
                
                # Check naming conventions (basic)
                if "def " in stripped:
                    func_name = stripped.split("def ")[1].split("(")[0].strip()
                    if func_name and not func_name[0].islower() and "_" not in func_name:
                        issues.append({
                            "type": "naming_convention",
                            "severity": "minor",
                            "line": i,
                            "message": f"Function '{func_name}' should use snake_case"
                        })
        
        return issues
    
    def _format_style_issues(self, issues: List[Dict[str, Any]]) -> str:
        """Format style issues for the prompt."""
        if not issues:
            return "No obvious style patterns detected."
        
        formatted = []
        for issue in issues[:10]:
            formatted.append(
                f"- Line {issue['line']}: {issue['type']} - {issue['message']} "
                f"(severity: {issue['severity']})"
            )
        
        return "\n".join(formatted)
    
    def _extract_style_issues(
        self,
        analysis_text: str,
        pattern_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract style issues from analysis text."""
        issues = pattern_issues.copy()
        
        # Parse LLM response
        lines = analysis_text.split("\n")
        current_issue = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect style issue markers
            if any(keyword in line_lower for keyword in ["style", "naming", "format", "convention", "pep"]):
                if current_issue:
                    issues.append(current_issue)
                
                # Determine severity
                severity = "minor"
                if "major" in line_lower or "critical" in line_lower:
                    severity = "major"
                
                current_issue = {
                    "type": "style_issue",
                    "severity": severity,
                    "message": line.strip(),
                    "category": "style"
                }
            elif current_issue:
                # Try to extract line number
                if "line" in line_lower:
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
    
    def _calculate_style_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate style score (0-10, higher is better)."""
        if not issues:
            return 10.0
        
        score = 10.0
        for issue in issues:
            severity = issue.get("severity", "minor")
            if severity == "major":
                score -= 1.0
            else:
                score -= 0.5
        
        return max(0.0, score)
