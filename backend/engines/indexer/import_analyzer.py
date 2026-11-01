"""Import statement analyzer."""

import ast

from engines.indexer.models import ImportInfo


class ImportAnalyzer:
    """Analyzes import statements from an AST."""

    @staticmethod
    def analyze(tree: ast.Module) -> list[ImportInfo]:
        """Extract all import statements from an AST module."""
        imports: list[ImportInfo] = []

        for node in tree.body:
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(
                        ImportInfo(module=name.name, imported=[])
                    )
            elif isinstance(node, ast.ImportFrom):
                imports.append(
                    ImportInfo(
                        module=node.module or "",
                        imported=[n.name for n in node.names],
                    )
                )

        return imports
