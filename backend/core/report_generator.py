"""
Report Generator for Code Review Agent.

Generates comprehensive, formatted reports from code review results.
"""

from typing import Dict, Any, List
from datetime import datetime


class ReportGenerator:
    """
    Generates formatted reports from code review results.
    
    Supports multiple formats:
    - Markdown (default)
    - Plain text
    - JSON (structured data)
    """
    
    def __init__(self):
        """Initialize the report generator."""
        pass
    
    def generate_report(
        self,
        review_results: Dict[str, Any],
        format_type: str = "markdown"
    ) -> str:
        """
        Generate a comprehensive review report.
        
        Args:
            review_results: Results from CodeReviewOrchestrator
            format_type: Report format ("markdown", "text", "json")
            
        Returns:
            Formatted report string
        """
        if format_type.lower() == "markdown":
            return self._generate_markdown_report(review_results)
        elif format_type.lower() == "text":
            return self._generate_text_report(review_results)
        elif format_type.lower() == "json":
            import json
            return json.dumps(review_results, indent=2)
        else:
            return self._generate_markdown_report(review_results)
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown formatted report."""
        report = []
        
        # Header
        report.append("# Code Review Report")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Language:** {results.get('language', 'unknown')}")
        report.append("")
        
        # Summary
        summary = results.get("summary", {})
        report.append("## Summary")
        report.append("")
        report.append(f"- **Overall Score:** {summary.get('overall_score', 0):.1f}/10")
        report.append(f"- **Overall Severity:** {summary.get('overall_severity', 'none')}")
        report.append(f"- **Total Issues:** {summary.get('total_issues', 0)}")
        report.append(f"  - Critical: {summary.get('critical_issues', 0)}")
        report.append(f"  - High: {summary.get('high_issues', 0)}")
        report.append(f"  - Medium: {summary.get('medium_issues', 0)}")
        report.append(f"  - Low: {summary.get('low_issues', 0)}")
        report.append("")
        
        # Metrics
        metrics = results.get("metrics", {})
        if metrics:
            report.append("## Code Metrics")
            report.append("")
            report.append(f"- **Total Lines:** {metrics.get('total_lines', 0)}")
            report.append(f"- **Code Lines:** {metrics.get('code_lines', 0)}")
            report.append(f"- **Comment Lines:** {metrics.get('comment_lines', 0)}")
            report.append(f"- **Average Line Length:** {metrics.get('average_line_length', 0):.1f}")
            report.append("")
        
        # Agent Results
        agent_results = results.get("agent_results", {})
        
        # Syntax
        if "syntax" in agent_results:
            syntax = agent_results["syntax"]
            if not syntax.get("skipped") and not syntax.get("error"):
                report.append("## Syntax Analysis")
                report.append("")
                if syntax.get("syntax_valid"):
                    report.append("[OK] **Syntax is valid**")
                else:
                    report.append("[ERROR] **Syntax errors detected**")
                    report.append("")
                    for issue in syntax.get("issues", [])[:10]:
                        report.append(f"- **Line {issue.get('line', '?')}:** {issue.get('message', 'Unknown error')}")
                report.append("")
        
        # Security
        if "security" in agent_results:
            security = agent_results["security"]
            if not security.get("skipped") and not security.get("error"):
                report.append("## Security Analysis")
                report.append("")
                report.append(f"**Security Score:** {security.get('security_score', 0):.1f}/10")
                report.append(f"**Vulnerabilities Found:** {security.get('vulnerability_count', 0)}")
                report.append("")
                
                vulns = security.get("vulnerabilities", [])
                if vulns:
                    for vuln in vulns[:10]:
                        severity = vuln.get("severity", "medium")
                        severity_marker = "[CRITICAL]" if severity == "critical" else "[HIGH]" if severity == "high" else "[MEDIUM]"
                        report.append(f"{severity_marker} **{severity.upper()}:** {vuln.get('message', 'Unknown')}")
                        if vuln.get("line"):
                            report.append(f"  - Line {vuln['line']}")
                else:
                    report.append("[OK] No security vulnerabilities detected")
                report.append("")
        
        # Performance
        if "performance" in agent_results:
            performance = agent_results["performance"]
            if not performance.get("skipped") and not performance.get("error"):
                report.append("## Performance Analysis")
                report.append("")
                report.append(f"**Performance Score:** {performance.get('performance_score', 0):.1f}/10")
                report.append(f"**Issues Found:** {performance.get('issue_count', 0)}")
                report.append("")
                
                issues = performance.get("issues", [])
                if issues:
                    for issue in issues[:10]:
                        impact = issue.get("impact", "medium")
                        report.append(f"- **{impact.upper()} Impact:** {issue.get('message', 'Unknown')}")
                        if issue.get("line"):
                            report.append(f"  - Line {issue['line']}")
                else:
                    report.append("[OK] No performance issues detected")
                report.append("")
        
        # Style
        if "style" in agent_results:
            style = agent_results["style"]
            if not style.get("skipped") and not style.get("error"):
                report.append("## Style Review")
                report.append("")
                report.append(f"**Style Score:** {style.get('style_score', 0):.1f}/10")
                report.append(f"**Style Guide:** {style.get('style_guide', 'N/A')}")
                report.append(f"**Issues Found:** {style.get('issue_count', 0)}")
                report.append("")
                
                issues = style.get("issues", [])
                if issues:
                    for issue in issues[:10]:
                        severity = issue.get("severity", "minor")
                        report.append(f"- **{severity.upper()}:** {issue.get('message', 'Unknown')}")
                        if issue.get("line"):
                            report.append(f"  - Line {issue['line']}")
                else:
                    report.append("[OK] Code style is good")
                report.append("")
        
        # Best Practices
        if "best_practices" in agent_results:
            best_practices = agent_results["best_practices"]
            if not best_practices.get("skipped") and not best_practices.get("error"):
                report.append("## Best Practices Review")
                report.append("")
                report.append(f"**Best Practices Score:** {best_practices.get('best_practices_score', 0):.1f}/10")
                report.append(f"**Issues Found:** {best_practices.get('issue_count', 0)}")
                report.append("")
                
                issues = best_practices.get("issues", [])
                if issues:
                    for issue in issues[:10]:
                        report.append(f"- **{issue.get('category', 'General')}:** {issue.get('message', 'Unknown')}")
                        if issue.get("line"):
                            report.append(f"  - Line {issue['line']}")
                else:
                    report.append("[OK] Code follows best practices")
                report.append("")
        
        # Documentation
        if "documentation" in agent_results:
            documentation = agent_results["documentation"]
            if not documentation.get("skipped") and not documentation.get("error"):
                report.append("## Documentation Review")
                report.append("")
                report.append(f"**Documentation Score:** {documentation.get('documentation_score', 0):.1f}/10")
                
                doc_stats = documentation.get("docstring_stats", {})
                if doc_stats:
                    coverage = doc_stats.get("coverage_percentage", 0)
                    report.append(f"**Docstring Coverage:** {coverage:.1f}%")
                    report.append(f"  - Functions with docstrings: {doc_stats.get('functions_with_docstrings', 0)}/{doc_stats.get('total_functions', 0)}")
                    report.append(f"  - Classes with docstrings: {doc_stats.get('classes_with_docstrings', 0)}/{doc_stats.get('total_classes', 0)}")
                
                report.append(f"**Issues Found:** {documentation.get('issue_count', 0)}")
                report.append("")
                
                issues = documentation.get("issues", [])
                if issues:
                    for issue in issues[:10]:
                        severity = issue.get("severity", "medium")
                        report.append(f"- **{severity.upper()}:** {issue.get('message', 'Unknown')}")
                        if issue.get("line"):
                            report.append(f"  - Line {issue['line']}")
                else:
                    report.append("[OK] Documentation is adequate")
                report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        
        if summary.get("critical_issues", 0) > 0:
            report.append("**Priority 1 - Critical Issues:**")
            report.append("- Address critical security vulnerabilities immediately")
            report.append("- Fix syntax errors that prevent code execution")
            report.append("")
        
        if summary.get("high_issues", 0) > 0:
            report.append("**Priority 2 - High Priority Issues:**")
            report.append("- Address high-severity security vulnerabilities")
            report.append("- Fix performance bottlenecks")
            report.append("- Resolve major style violations")
            report.append("")
        
        if summary.get("overall_score", 0) < 7.0:
            report.append("**General Recommendations:**")
            report.append("- Review and address medium-priority issues")
            report.append("- Improve code documentation")
            report.append("- Consider refactoring for better maintainability")
            report.append("")
        
        # Footer
        report.append("---")
        report.append("")
        report.append(f"*Report generated by Code Review Agent System*")
        
        return "\n".join(report)
    
    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """Generate plain text formatted report."""
        # Convert markdown to plain text (simple version)
        markdown_report = self._generate_markdown_report(results)
        
        # Remove markdown formatting
        text_report = markdown_report
        text_report = text_report.replace("**", "")
        text_report = text_report.replace("#", "")
        text_report = text_report.replace("✓", "[OK]")
        text_report = text_report.replace("✗", "[ERROR]")
        text_report = text_report.replace("🔴", "[CRITICAL]")
        text_report = text_report.replace("🟠", "[HIGH]")
        text_report = text_report.replace("🟡", "[MEDIUM]")
        
        return text_report

