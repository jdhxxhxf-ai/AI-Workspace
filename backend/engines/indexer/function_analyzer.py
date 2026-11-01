"""Function definition analyzer."""

import ast

from engines.indexer.models import FunctionInfo


class FunctionAnalyzer:
    """Analyzes function definitions from an AST."""

    @staticmethod
    def analyze(tree: ast.Module) -> list[FunctionInfo]:
        """Extract top-level function definitions from an AST module."""
        functions: list[FunctionInfo] = []

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(FunctionAnalyzer._build_function_info(node))

        return functions

    @staticmethod
    def analyze_class_methods(class_node: ast.ClassDef) -> list[FunctionInfo]:
        """Extract method definitions from a class node."""
        methods: list[FunctionInfo] = []

        for child in class_node.body:
            if isinstance(child, ast.FunctionDef):
                methods.append(FunctionAnalyzer._build_function_info(child))

        return methods

    @staticmethod
    def _build_function_info(node: ast.FunctionDef) -> FunctionInfo:
        return FunctionInfo(
            name=node.name,
            line=node.lineno,
            decorators=[ast.unparse(d) for d in node.decorator_list],
            docstring=ast.get_docstring(node),
        )
