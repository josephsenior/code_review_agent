"""
Best Practices Agent for Code Review.

Reviews code against language-specific best practices, design patterns, and architectural principles.
"""

from typing import Any, Dict, List

from ..tools.ast_analyzer import ASTAnalyzer
from .base_agent import BaseCodeReviewAgent


class BestPracticesAgent(BaseCodeReviewAgent):
    """
    Agent specialized in reviewing code against best practices.
    
    Checks for:
    - Design patterns
    - Anti-patterns
    - Architectural issues
    - SOLID principles
    - DRY (Don't Repeat Yourself) violations
    - Code organization
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        api_key: str = None
    ):
        """
        Initialize the Best Practices Agent.
        
        Args:
            model_name: Gemini model name
            temperature: LLM temperature
            api_key: Gemini API key
        """
        system_prompt = """You are a software architecture and best practices expert. Your role is to:
1. Review code against language-specific best practices
2. Identify design patterns and anti-patterns
3. Check SOLID principles adherence
4. Detect DRY (Don't Repeat Yourself) violations
5. Review code organization and structure
6. Identify architectural issues
7. Suggest improvements based on best practices

Focus on maintainability, scalability, and code quality principles.
Provide actionable recommendations for improvement."""
        
        super().__init__(
            role="Best Practices Reviewer",
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
        Review code for best practices violations.
        
        Args:
            code: Source code to review
            language: Programming language
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with best practices analysis results
        """
        # Analyze code structure
        ast_result = {}
        if language.lower() == "python":
            ast_result = self.ast_analyzer.parse(code, language)
        
        # Identify anti-patterns
        anti_patterns = self._identify_anti_patterns(code, language, ast_result)
        
        # Prepare best practices analysis prompt
        analysis_input = f"""Code to review for best practices ({language}):

```{language}
{code}
```

Code Structure:
{self._format_structure_info(ast_result)}

Detected Patterns:
{self._format_anti_patterns(anti_patterns)}

Review this code against best practices. Check for:
1. Design patterns and anti-patterns
2. SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
3. DRY violations (code duplication)
4. Code organization and modularity
5. Separation of concerns
6. Error handling best practices
7. Resource management
8. Architectural issues

For each issue found, provide:
- Issue type and category
- Description of the best practice violation
- Location (line number if possible)
- Explanation of why it's an issue
- Suggested improvement following best practices

Format your response clearly with prioritized recommendations."""
        
        analysis_result = self._invoke(analysis_input)
        
        # Extract best practices issues
        issues = self._extract_best_practices_issues(analysis_result, anti_patterns)
        
        # Calculate best practices score
        score = self._calculate_best_practices_score(issues)
        
        return {
            "agent": self.role,
            "language": language,
            "issues": issues,
            "issue_count": len(issues),
            "anti_patterns": anti_patterns,
            "best_practices_score": score,
            "analysis": analysis_result,
            "severity": "high" if issues else "none"
        }
    
    def _identify_anti_patterns(
        self,
        code: str,
        language: str,
        ast_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify common anti-patterns."""
        anti_patterns = []
        lines = code.split("\n")
        
        # Check for code duplication (simple check)
        function_bodies = {}
        if ast_result.get("valid"):
            functions = ast_result.get("functions", [])
            for func in functions:
                func_name = func.get("name", "")
                # Simple duplication check - look for repeated function patterns
                if func_name in function_bodies:
                    anti_patterns.append({
                        "type": "potential_duplication",
                        "message": f"Potential code duplication in function '{func_name}'",
                        "category": "DRY violation"
                    })
        
        # Check for god class/function (too many responsibilities)
        if ast_result.get("valid"):
            complexity = ast_result.get("complexity", {})
            if complexity.get("cyclomatic", 0) > 15:
                anti_patterns.append({
                    "type": "high_complexity",
                    "message": "High cyclomatic complexity suggests potential god function",
                    "category": "Single Responsibility Principle"
                })
        
        # Check for magic numbers
        import re
        for i, line in enumerate(lines, 1):
            # Look for standalone numbers (potential magic numbers)
            numbers = re.findall(r'\b\d+\b', line)
            if len(numbers) > 2 and "=" in line:
                anti_patterns.append({
                    "type": "magic_numbers",
                    "line": i,
                    "message": "Potential magic numbers detected",
                    "category": "Code clarity"
                })
        
        return anti_patterns
    
    def _format_structure_info(self, ast_result: Dict[str, Any]) -> str:
        """Format structure information for the prompt."""
        if not ast_result or not ast_result.get("valid"):
            return "No structure information available."
        
        info = []
        info.append(f"Functions: {len(ast_result.get('functions', []))}")
        info.append(f"Classes: {len(ast_result.get('classes', []))}")
        info.append(f"Complexity: {ast_result.get('complexity', {})}")
        
        return "\n".join(info)
    
    def _format_anti_patterns(self, anti_patterns: List[Dict[str, Any]]) -> str:
        """Format anti-patterns for the prompt."""
        if not anti_patterns:
            return "No obvious anti-patterns detected."
        
        formatted = []
        for pattern in anti_patterns[:10]:
            line_info = f" (line {pattern['line']})" if pattern.get("line") else ""
            formatted.append(
                f"- {pattern['type']}{line_info}: {pattern['message']} "
                f"[{pattern.get('category', 'general')}]"
            )
        
        return "\n".join(formatted)
    
    def _extract_best_practices_issues(
        self,
        analysis_text: str,
        anti_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract best practices issues from analysis text."""
        issues = []
        
        # Add anti-patterns as issues
        for pattern in anti_patterns:
            issues.append({
                "type": pattern["type"],
                "category": pattern.get("category", "best_practices"),
                "message": pattern["message"],
                "line": pattern.get("line"),
                "severity": "medium"
            })
        
        # Parse LLM response
        lines = analysis_text.split("\n")
        current_issue = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect best practices issue markers
            if any(keyword in line_lower for keyword in [
                "anti-pattern", "violation", "principle", "best practice",
                "design", "architecture", "solid", "dry"
            ]):
                if current_issue:
                    issues.append(current_issue)
                
                current_issue = {
                    "type": "best_practice_issue",
                    "category": "best_practices",
                    "message": line.strip(),
                    "severity": "medium"
                }
            elif current_issue:
                # Try to extract line number or category
                if "line" in line_lower:
                    try:
                        import re
                        line_match = re.search(r'line\s+(\d+)', line_lower)
                        if line_match:
                            current_issue["line"] = int(line_match.group(1))
                    except Exception:
                        pass
                
                # Detect category
                if "solid" in line_lower:
                    current_issue["category"] = "SOLID principles"
                elif "dry" in line_lower:
                    current_issue["category"] = "DRY violation"
                
                current_issue["message"] += " " + line.strip()
        
        if current_issue:
            issues.append(current_issue)
        
        return issues
    
    def _calculate_best_practices_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate best practices score (0-10, higher is better)."""
        if not issues:
            return 10.0
        
        score = 10.0
        for issue in issues:
            severity = issue.get("severity", "medium")
            if severity == "high":
                score -= 2.0
            elif severity == "medium":
                score -= 1.0
            else:
                score -= 0.5
        
        return max(0.0, score)
