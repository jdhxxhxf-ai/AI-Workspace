"""Class definition analyzer."""

import ast

from engines.indexer.function_analyzer import FunctionAnalyzer
from engines.indexer.models import ClassInfo


class ClassAnalyzer:
    """Analyzes class definitions from an AST."""

    @staticmethod
    def analyze(tree: ast.Module) -> list[ClassInfo]:
        """Extract class definitions from an AST module."""
        classes: list[ClassInfo] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(ClassAnalyzer._build_class_info(node))

        return classes

    @staticmethod
    def _build_class_info(node: ast.ClassDef) -> ClassInfo:
        return ClassInfo(
            name=node.name,
            line=node.lineno,
            methods=FunctionAnalyzer.analyze_class_methods(node),
            docstring=ast.get_docstring(node),
        )
