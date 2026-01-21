"""
Main Orchestrator for the Code Review Agent System.

Coordinates all specialized agents and manages the code review workflow.
"""

from typing import Any, Dict, List, Optional

from ..agents.best_practices_agent import BestPracticesAgent
from ..agents.documentation_agent import DocumentationAgent
from ..agents.performance_agent import PerformanceAgent
from ..agents.security_agent import SecurityAgent
from ..agents.style_agent import StyleAgent
from ..agents.syntax_analyzer import SyntaxAnalyzerAgent
from ..tools.ast_analyzer import ASTAnalyzer
from ..tools.dependency_checker import DependencyChecker
from ..tools.metrics_calculator import MetricsCalculator


class CodeReviewOrchestrator:
    """
    Main orchestrator that coordinates all code review agents.

    Workflow:
    1. Syntax Analyzer checks for basic errors
    2. Security Agent identifies vulnerabilities
    3. Performance Agent analyzes bottlenecks
    4. Style Agent reviews code style
    5. Best Practices Agent checks design patterns
    6. Documentation Agent reviews documentation
    7. Synthesize all results into comprehensive report
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.3,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Code Review Orchestrator.

        Args:
            model_name: Gemini model name
            temperature: LLM temperature
            api_key: Gemini API key
        """
        # Initialize tools
        self.ast_analyzer = ASTAnalyzer()
        self.dependency_checker = DependencyChecker()
        self.metrics_calculator = MetricsCalculator()

        # Initialize all agents
        self.syntax_agent = SyntaxAnalyzerAgent(
            model_name=model_name, temperature=0.1, api_key=api_key
        )

        self.security_agent = SecurityAgent(
            model_name=model_name, temperature=0.2, api_key=api_key
        )

        self.performance_agent = PerformanceAgent(
            model_name=model_name, temperature=0.3, api_key=api_key
        )

        self.style_agent = StyleAgent(
            model_name=model_name, temperature=0.3, api_key=api_key
        )

        self.best_practices_agent = BestPracticesAgent(
            model_name=model_name, temperature=0.3, api_key=api_key
        )

        self.documentation_agent = DocumentationAgent(
            model_name=model_name, temperature=0.3, api_key=api_key
        )

    def review(
        self,
        code: str,
        language: str = "python",
        include_agents: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive code review using all agents.

        Args:
            code: Source code to review
            language: Programming language
            include_agents: Optional list of agent names to include
                          (if None, includes all agents)

        Returns:
            Complete review result with all agent findings
        """
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        # Default to all agents if not specified
        if include_agents is None:
            include_agents = [
                "syntax",
                "security",
                "performance",
                "style",
                "best_practices",
                "documentation",
            ]

        # No logging for clean execution unless requested
        pass

        # Calculate basic metrics first
        metrics = self.metrics_calculator.calculate_metrics(code, language)
        dependencies = self.dependency_checker.check_dependencies(code, language)

        results = {
            "code": code,
            "language": language,
            "metrics": metrics,
            "dependencies": dependencies,
            "agent_results": {},
            "summary": {},
        }

        # Use individual agents for specific checks
        try:
            if not include_agents or "syntax" in include_agents:
                results["agent_results"]["syntax"] = self.syntax_agent.review(code, language)
        except Exception as e:
            results["agent_results"]["syntax"] = {"error": str(e), "skipped": True}

        try:
            if not include_agents or "security" in include_agents:
                results["agent_results"]["security"] = self.security_agent.review(code, language)
        except Exception as e:
            results["agent_results"]["security"] = {"error": str(e), "skipped": True}

        try:
            if not include_agents or "performance" in include_agents:
                results["agent_results"]["performance"] = self.performance_agent.review(
                    code, language
                )
        except Exception as e:
            results["agent_results"]["performance"] = {"error": str(e), "skipped": True}

        try:
            if not include_agents or "style" in include_agents:
                results["agent_results"]["style"] = self.style_agent.review(code, language)
        except Exception as e:
            results["agent_results"]["style"] = {"error": str(e), "skipped": True}

        try:
            if not include_agents or "best_practices" in include_agents:
                results["agent_results"]["best_practices"] = self.best_practices_agent.review(
                    code, language
                )
        except Exception as e:
            results["agent_results"]["best_practices"] = {"error": str(e), "skipped": True}

        try:
            if not include_agents or "documentation" in include_agents:
                results["agent_results"]["documentation"] = self.documentation_agent.review(
                    code, language
                )
        except Exception as e:
            results["agent_results"]["documentation"] = {"error": str(e), "skipped": True}

        # Generate summary
        results["summary"] = self._generate_summary(results)

        print("[Orchestrator] Code review complete!")

        return results

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary of all review results.

        Args:
            results: Complete review results from all agents

        Returns:
            Summary dictionary with overall scores and statistics
        """
        agent_results = results.get("agent_results", {})

        # Collect all issues
        all_issues = []
        critical_issues = []
        high_issues = []

        # Collect scores
        scores = {}

        for agent_name, agent_result in agent_results.items():
            if agent_result.get("skipped") or agent_result.get("error"):
                continue

            # Collect issues
            issues = agent_result.get("issues", []) or agent_result.get(
                "vulnerabilities", []
            )
            for issue in issues:
                issue["agent"] = agent_name
                all_issues.append(issue)

                severity = issue.get("severity", "medium")
                if severity == "critical":
                    critical_issues.append(issue)
                elif severity == "high":
                    high_issues.append(issue)

            # Collect scores
            if "syntax_valid" in agent_result:
                scores["syntax"] = 10.0 if agent_result["syntax_valid"] else 0.0
            if "security_score" in agent_result:
                scores["security"] = agent_result["security_score"]
            if "performance_score" in agent_result:
                scores["performance"] = agent_result["performance_score"]
            if "style_score" in agent_result:
                scores["style"] = agent_result["style_score"]
            if "best_practices_score" in agent_result:
                scores["best_practices"] = agent_result["best_practices_score"]
            if "documentation_score" in agent_result:
                scores["documentation"] = agent_result["documentation_score"]

        # Calculate overall score
        if scores:
            overall_score = sum(scores.values()) / len(scores)
        else:
            overall_score = 0.0

        # Determine overall severity
        overall_severity = "none"
        if critical_issues:
            overall_severity = "critical"
        elif high_issues:
            overall_severity = "high"
        elif all_issues:
            overall_severity = "medium"

        return {
            "total_issues": len(all_issues),
            "critical_issues": len(critical_issues),
            "high_issues": len(high_issues),
            "medium_issues": len(
                [i for i in all_issues if i.get("severity") == "medium"]
            ),
            "low_issues": len([i for i in all_issues if i.get("severity") == "low"]),
            "scores": scores,
            "overall_score": overall_score,
            "overall_severity": overall_severity,
            "agents_run": len(
                [
                    r
                    for r in agent_results.values()
                    if not r.get("skipped") and not r.get("error")
                ]
            ),
            "agents_failed": len([r for r in agent_results.values() if r.get("error")]),
        }
