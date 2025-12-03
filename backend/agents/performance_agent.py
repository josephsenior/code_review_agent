"""
Performance Agent for Code Review.

Analyzes code for performance bottlenecks, inefficiencies, and optimization opportunities.
"""

from typing import Dict, Any, List
from .base_agent import BaseCodeReviewAgent
from ..tools.ast_analyzer import ASTAnalyzer


class PerformanceAgent(BaseCodeReviewAgent):
    """
    Agent specialized in performance analysis and optimization recommendations.
    
    Identifies:
    - Time complexity issues
    - Memory inefficiencies
    - Bottlenecks and slow operations
    - Inefficient algorithms
    - Resource leaks
    - Optimization opportunities
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        api_key: str = None
    ):
        """
        Initialize the Performance Agent.
        
        Args:
            model_name: OpenAI model name
            temperature: LLM temperature
            api_key: OpenAI API key
        """
        system_prompt = """You are a performance optimization expert. Your role is to:
1. Analyze time complexity (Big O notation)
2. Identify memory inefficiencies
3. Detect performance bottlenecks
4. Find inefficient algorithms or data structures
5. Identify resource leaks (file handles, connections)
6. Suggest optimization opportunities
7. Check for unnecessary computations or redundant operations

Focus on actionable performance improvements. Consider:
- Algorithm efficiency
- Data structure choices
- Loop optimizations
- Caching opportunities
- Database query optimization
- I/O operations"""
        
        super().__init__(
            role="Performance Analyst",
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
        Review code for performance issues.
        
        Args:
            code: Source code to review
            language: Programming language
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with performance analysis results
        """
        # Analyze code structure
        ast_result = {}
        complexity_metrics = {}
        
        if language.lower() == "python":
            ast_result = self.ast_analyzer.parse(code, language)
            if ast_result.get("valid"):
                complexity_metrics = ast_result.get("complexity", {})
        
        # Identify performance patterns
        performance_issues = self._identify_performance_patterns(code, language, complexity_metrics)
        
        # Prepare performance analysis prompt
        analysis_input = f"""Code to analyze for performance issues ({language}):

```{language}
{code}
```

Code Complexity Metrics:
{self._format_complexity_metrics(complexity_metrics)}

Detected Performance Patterns:
{self._format_performance_issues(performance_issues)}

Analyze this code for performance problems. Check for:
1. Time complexity issues (nested loops, inefficient algorithms)
2. Memory inefficiencies (large data structures, memory leaks)
3. Performance bottlenecks (slow operations, blocking calls)
4. Inefficient data structures or algorithms
5. Resource leaks (unclosed files, connections)
6. Unnecessary computations or redundant operations
7. Opportunities for caching or memoization
8. Database query optimization needs

For each issue found, provide:
- Issue type and impact level (high/medium/low)
- Description of the performance problem
- Location (line number if possible)
- Current complexity (if applicable)
- Suggested optimization
- Expected improvement

Format your response clearly with prioritized recommendations."""
        
        analysis_result = self._invoke(analysis_input)
        
        # Extract performance issues
        issues = self._extract_performance_issues(analysis_result, performance_issues)
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(issues, complexity_metrics)
        
        return {
            "agent": self.role,
            "language": language,
            "issues": issues,
            "issue_count": len(issues),
            "high_impact_count": len([i for i in issues if i.get("impact") == "high"]),
            "complexity_metrics": complexity_metrics,
            "performance_score": performance_score,
            "analysis": analysis_result,
            "severity": "high" if issues else "none"
        }
    
    def _identify_performance_patterns(
        self,
        code: str,
        language: str,
        complexity_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify common performance anti-patterns."""
        issues = []
        code_lower = code.lower()
        lines = code.split("\n")
        
        # Check for nested loops
        nesting_level = complexity_metrics.get("max_nesting", 0)
        if nesting_level > 3:
            issues.append({
                "type": "high_nesting",
                "impact": "high",
                "message": f"High nesting level detected: {nesting_level}",
                "suggestion": "Consider refactoring to reduce nesting"
            })
        
        # Check for common performance issues
        performance_patterns = {
            "nested_loops": ["for", "while", "for", "while"],
            "inefficient_search": [".find(", ".index(", "in list"],
            "string_concat": ["+=", "str + str"],
            "large_list_comprehension": ["[", "for", "if", "for"],
            "unclosed_file": ["open(", "with open("]
        }
        
        # Simple pattern detection
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            # Check for inefficient list operations
            if any(pattern in line_lower for pattern in ["in [", "in list", ".find("]):
                if "for" in line_lower or "if" in line_lower:
                    issues.append({
                        "type": "inefficient_search",
                        "impact": "medium",
                        "line": i,
                        "message": "Potentially inefficient search operation",
                        "suggestion": "Consider using sets or dictionaries for O(1) lookup"
                    })
            
            # Check for string concatenation in loops
            if "+=" in line and "str" in line_lower:
                issues.append({
                    "type": "string_concat",
                    "impact": "low",
                    "line": i,
                    "message": "String concatenation in loop",
                    "suggestion": "Consider using join() or list comprehension"
                })
        
        return issues
    
    def _format_complexity_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format complexity metrics for the prompt."""
        if not metrics:
            return "No complexity metrics available."
        
        return f"""Cyclomatic Complexity: {metrics.get('cyclomatic', 'N/A')}
Max Nesting Level: {metrics.get('max_nesting', 'N/A')}
Function Count: {metrics.get('function_count', 'N/A')}
Class Count: {metrics.get('class_count', 'N/A')}"""
    
    def _format_performance_issues(self, issues: List[Dict[str, Any]]) -> str:
        """Format performance issues for the prompt."""
        if not issues:
            return "No obvious performance patterns detected."
        
        formatted = []
        for issue in issues[:10]:
            line_info = f" (line {issue['line']})" if issue.get("line") else ""
            formatted.append(
                f"- {issue['type']}{line_info}: {issue['message']} "
                f"(impact: {issue['impact']})"
            )
        
        return "\n".join(formatted)
    
    def _extract_performance_issues(
        self,
        analysis_text: str,
        pattern_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract performance issues from analysis text."""
        issues = pattern_issues.copy()
        
        # Parse LLM response
        lines = analysis_text.split("\n")
        current_issue = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect performance issue markers
            if any(keyword in line_lower for keyword in ["performance", "bottleneck", "slow", "inefficient", "optimization"]):
                if current_issue:
                    issues.append(current_issue)
                
                # Determine impact
                impact = "medium"
                if "high" in line_lower or "critical" in line_lower:
                    impact = "high"
                elif "low" in line_lower or "minor" in line_lower:
                    impact = "low"
                
                current_issue = {
                    "type": "performance_issue",
                    "impact": impact,
                    "message": line.strip(),
                    "category": "performance"
                }
            elif current_issue:
                # Try to extract line number
                if "line" in line_lower:
                    try:
                        import re
                        line_match = re.search(r'line\s+(\d+)', line_lower)
                        if line_match:
                            current_issue["line"] = int(line_match.group(1))
                    except:
                        pass
                current_issue["message"] += " " + line.strip()
        
        if current_issue:
            issues.append(current_issue)
        
        return issues
    
    def _calculate_performance_score(
        self,
        issues: List[Dict[str, Any]],
        complexity_metrics: Dict[str, Any]
    ) -> float:
        """Calculate performance score (0-10, higher is better)."""
        score = 10.0
        
        # Deduct points for issues
        for issue in issues:
            impact = issue.get("impact", "medium")
            if impact == "high":
                score -= 2.0
            elif impact == "medium":
                score -= 1.0
            else:
                score -= 0.5
        
        # Deduct points for high complexity
        cyclomatic = complexity_metrics.get("cyclomatic", 1)
        if cyclomatic > 20:
            score -= 2.0
        elif cyclomatic > 10:
            score -= 1.0
        
        nesting = complexity_metrics.get("max_nesting", 0)
        if nesting > 4:
            score -= 1.5
        elif nesting > 3:
            score -= 0.5
        
        return max(0.0, score)

