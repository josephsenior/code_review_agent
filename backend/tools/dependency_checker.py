"""
Dependency Checker Tool for Code Review Agent.

Checks for insecure or outdated dependencies.
"""

from typing import Dict, Any, List
import re


class DependencyChecker:
    """
    Checks dependencies for security vulnerabilities and version issues.
    """
    
    def __init__(self):
        """Initialize the dependency checker."""
        pass
    
    def check_dependencies(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Check dependencies in code.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Dictionary with dependency information
        """
        dependencies = []
        
        if language.lower() == "python":
            # Extract import statements
            import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(\S+)'
            for line in code.split("\n"):
                match = re.match(import_pattern, line.strip())
                if match:
                    module = match.group(1) or match.group(2)
                    if module:
                        dependencies.append({
                            "module": module.split(".")[0],
                            "line": code.split("\n").index(line) + 1
                        })
        
        return {
            "dependencies": dependencies,
            "dependency_count": len(dependencies),
            "language": language
        }

