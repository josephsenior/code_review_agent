"""
AST Analyzer Tool for Code Review Agent.

Parses code into Abstract Syntax Trees and extracts structural information.
"""

import ast
from typing import Any, Dict, List


class ASTAnalyzer:
    """
    Analyzes code using Abstract Syntax Trees.

    Provides:
    - Syntax validation
    - Structure analysis
    - Function/class extraction
    - Complexity metrics
    """

    def __init__(self):
        """Initialize the AST analyzer."""
        pass

    def parse(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Parse code into AST and extract information.

        Args:
            code: Source code to analyze
            language: Programming language (currently supports python)

        Returns:
            Dictionary with AST information and metrics
        """
        if language.lower() != "python":
            return {
                "valid": False,
                "error": f"AST analysis not yet supported for {language}",
                "language": language,
            }

        try:
            tree = ast.parse(code)

            # Extract information
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)
            imports = self._extract_imports(tree)
            complexity = self._calculate_complexity(tree)

            return {
                "valid": True,
                "language": language,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "complexity": complexity,
                "ast_tree": tree,
            }

        except SyntaxError as e:
            return {
                "valid": False,
                "error": str(e),
                "error_type": "SyntaxError",
                "line": e.lineno,
                "language": language,
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "language": language,
            }

    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function definitions from AST."""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "args": len(node.args.args),
                        "decorators": [ast.unparse(d) for d in node.decorator_list]
                        if hasattr(ast, "unparse")
                        else [],
                        "has_docstring": ast.get_docstring(node) is not None,
                    }
                )

        return functions

    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions from AST."""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods,
                        "method_count": len(methods),
                        "has_docstring": ast.get_docstring(node) is not None,
                    }
                )

        return classes

    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import statements from AST."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {"module": alias.name, "alias": alias.asname, "type": "import"}
                    )
            elif isinstance(node, ast.ImportFrom):
                imports.append(
                    {
                        "module": node.module or "",
                        "names": [alias.name for alias in node.names],
                        "type": "from_import",
                    }
                )

        return imports

    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate basic complexity metrics."""
        complexity = {
            "cyclomatic": 1,  # Base complexity
            "max_nesting": 0,
            "function_count": 0,
            "class_count": 0,
        }

        def visit_node(node, depth=0):
            complexity["max_nesting"] = max(complexity["max_nesting"], depth)

            # Count decision points (if, for, while, etc.)
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity["cyclomatic"] += 1

            if isinstance(node, ast.FunctionDef):
                complexity["function_count"] += 1

            if isinstance(node, ast.ClassDef):
                complexity["class_count"] += 1

            # Recursively visit children
            for child in ast.iter_child_nodes(node):
                visit_node(child, depth + 1)

        visit_node(tree)

        return complexity
