"""
Metrics Calculator Tool for Code Review Agent.

Calculates various code metrics for analysis.
"""

from typing import Any, Dict


class MetricsCalculator:
    """
    Calculates code metrics like complexity, maintainability, etc.
    """
    
    def __init__(self):
        """Initialize the metrics calculator."""
        pass
    
    def calculate_metrics(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Calculate code metrics.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Dictionary with calculated metrics
        """
        lines = code.split("\n")
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith("#")]),
            "comment_lines": len([line for line in lines if line.strip().startswith("#")]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "average_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0,
            "language": language
        }
        
        return metrics
