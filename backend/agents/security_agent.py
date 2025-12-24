"""
Security Agent for Code Review.

Identifies security vulnerabilities, risks, and insecure coding practices.
Uses Guardrails pattern to ensure code safety.
"""

from typing import Any, Dict, List

from ..tools.ast_analyzer import ASTAnalyzer
from .base_agent import BaseCodeReviewAgent


class SecurityAgent(BaseCodeReviewAgent):
    """
    Agent specialized in detecting security vulnerabilities and risks.
    
    Uses Guardrails pattern to ensure code safety by identifying:
    - SQL injection vulnerabilities
    - XSS vulnerabilities
    - Insecure dependencies
    - Hardcoded secrets
    - Authentication/authorization issues
    - Input validation problems
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.2,
        api_key: str = None
    ):
        """
        Initialize the Security Agent.
        
        Args:
            model_name: Gemini model name
            temperature: LLM temperature (low for consistent security checks)
            api_key: Gemini API key
        """
        system_prompt = """You are a security expert specializing in code security review. Your role is to:
1. Identify security vulnerabilities (SQL injection, XSS, CSRF, etc.)
2. Detect hardcoded secrets, API keys, or credentials
3. Check for insecure dependencies or outdated packages
4. Identify authentication and authorization flaws
5. Find input validation and sanitization issues
6. Detect insecure data handling (encryption, hashing)
7. Identify security anti-patterns

Be thorough and prioritize critical security issues. Use OWASP Top 10 as a reference. 
Report issues with severity levels: critical, high, medium, low."""
        
        super().__init__(
            role="Security Analyst",
            system_prompt=system_prompt,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        self.ast_analyzer = ASTAnalyzer()
        self.security_patterns = self._load_security_patterns()
    
    def review(
        self,
        code: str,
        language: str = "python",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Review code for security vulnerabilities.
        
        Args:
            code: Source code to review
            language: Programming language
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with security analysis results
        """
        # Analyze code structure
        
        # Check for security patterns
        pattern_matches = self._check_security_patterns(code, language)
        
        # Prepare security analysis prompt
        analysis_input = f"""Code to analyze for security vulnerabilities ({language}):

```{language}
{code}
```

Detected Security Patterns:
{self._format_pattern_matches(pattern_matches)}

Analyze this code thoroughly for security vulnerabilities. Check for:
1. SQL injection vulnerabilities
2. Cross-site scripting (XSS) risks
3. Hardcoded secrets, API keys, or credentials
4. Insecure authentication/authorization
5. Input validation issues
6. Insecure data handling
7. Dependency vulnerabilities
8. Security anti-patterns

For each issue found, provide:
- Issue type and severity (critical/high/medium/low)
- Description of the vulnerability
- Location (line number if possible)
- Potential impact
- Recommended fix

Format your response clearly with prioritized issues."""
        
        analysis_result = self._invoke(analysis_input)
        
        # Extract security issues
        vulnerabilities = self._extract_vulnerabilities(analysis_result, pattern_matches)
        
        # Calculate security score
        security_score = self._calculate_security_score(vulnerabilities)
        
        return {
            "agent": self.role,
            "language": language,
            "vulnerabilities": vulnerabilities,
            "vulnerability_count": len(vulnerabilities),
            "critical_count": len([v for v in vulnerabilities if v.get("severity") == "critical"]),
            "high_count": len([v for v in vulnerabilities if v.get("severity") == "high"]),
            "security_score": security_score,
            "pattern_matches": pattern_matches,
            "analysis": analysis_result,
            "severity": "critical" if vulnerabilities else "none"
        }
    
    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load common security anti-patterns to check for."""
        return {
            "hardcoded_secrets": [
                "password", "secret", "api_key", "apikey", "token", "credential",
                "aws_access_key", "private_key", "passwd", "pwd"
            ],
            "sql_injection": [
                "execute(", "query(", "sql", "raw_sql", "format(", "%s %"
            ],
            "eval_usage": [
                "eval(", "exec(", "__import__", "compile("
            ],
            "insecure_random": [
                "random.", "randint", "choice("
            ],
            "path_traversal": [
                "../", "..\\", "open(", "file(", "read("
            ]
        }
    
    def _check_security_patterns(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Check code for known security anti-patterns."""
        matches = []
        code_lower = code.lower()
        
        for pattern_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                if pattern.lower() in code_lower:
                    # Find line numbers
                    lines = code.split("\n")
                    matching_lines = [
                        i + 1 for i, line in enumerate(lines)
                        if pattern.lower() in line.lower()
                    ]
                    
                    matches.append({
                        "type": pattern_type,
                        "pattern": pattern,
                        "lines": matching_lines[:5],  # Limit to first 5 matches
                        "severity": self._get_pattern_severity(pattern_type)
                    })
        
        return matches
    
    def _get_pattern_severity(self, pattern_type: str) -> str:
        """Get severity level for a pattern type."""
        severity_map = {
            "hardcoded_secrets": "critical",
            "eval_usage": "critical",
            "sql_injection": "high",
            "insecure_random": "medium",
            "path_traversal": "high"
        }
        return severity_map.get(pattern_type, "medium")
    
    def _format_pattern_matches(self, matches: List[Dict[str, Any]]) -> str:
        """Format pattern matches for the prompt."""
        if not matches:
            return "No obvious security patterns detected."
        
        formatted = []
        for match in matches[:10]:  # Limit to 10 matches
            formatted.append(
                f"- {match['type']}: Found '{match['pattern']}' "
                f"at lines {match['lines']} (severity: {match['severity']})"
            )
        
        return "\n".join(formatted)
    
    def _extract_vulnerabilities(
        self,
        analysis_text: str,
        pattern_matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract vulnerabilities from analysis text."""
        vulnerabilities = []
        
        # Add pattern matches as vulnerabilities
        for match in pattern_matches:
            if match["severity"] in ["critical", "high"]:
                vulnerabilities.append({
                    "type": match["type"],
                    "severity": match["severity"],
                    "message": f"Security pattern detected: {match['pattern']}",
                    "lines": match["lines"],
                    "category": "security_pattern"
                })
        
        # Parse LLM response for additional vulnerabilities
        lines = analysis_text.split("\n")
        current_vuln = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect vulnerability markers
            if any(keyword in line_lower for keyword in ["vulnerability", "security", "risk", "insecure"]):
                if current_vuln:
                    vulnerabilities.append(current_vuln)
                
                # Determine severity
                severity = "medium"
                if "critical" in line_lower:
                    severity = "critical"
                elif "high" in line_lower:
                    severity = "high"
                elif "low" in line_lower:
                    severity = "low"
                
                current_vuln = {
                    "type": "security_issue",
                    "severity": severity,
                    "message": line.strip(),
                    "category": "security"
                }
            elif current_vuln:
                # Try to extract line number or additional info
                if "line" in line_lower:
                    try:
                        import re
                        line_match = re.search(r'line\s+(\d+)', line_lower)
                        if line_match:
                            current_vuln["line"] = int(line_match.group(1))
                    except Exception:
                        pass
                current_vuln["message"] += " " + line.strip()
        
        if current_vuln:
            vulnerabilities.append(current_vuln)
        
        return vulnerabilities
    
    def _calculate_security_score(self, vulnerabilities: List[Dict[str, Any]]) -> float:
        """Calculate security score (0-10, higher is better)."""
        if not vulnerabilities:
            return 10.0
        
        score = 10.0
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "medium")
            if severity == "critical":
                score -= 3.0
            elif severity == "high":
                score -= 2.0
            elif severity == "medium":
                score -= 1.0
            else:
                score -= 0.5
        
        return max(0.0, score)
