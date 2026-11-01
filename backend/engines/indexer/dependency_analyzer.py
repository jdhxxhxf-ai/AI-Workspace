"""Deterministic internal Python import resolution."""

import sys
from pathlib import Path

from engines.indexer.models import DependencyEdge, PythonFileInfo

STDLIB_MODULES = getattr(sys, "stdlib_module_names", None) or {
    "abc", "argparse", "ast", "asyncio", "collections", "contextlib", "dataclasses",
    "datetime", "enum", "functools", "hashlib", "importlib", "io", "itertools",
    "json", "logging", "os", "pathlib", "re", "sqlite3", "sys", "tempfile",
    "threading", "time", "typing", "unittest", "uuid", "warnings",
}


class DependencyAnalyzer:
    """Resolve imports to indexed Python modules where this is provable."""

    @staticmethod
    def analyze(files: list[PythonFileInfo]) -> list[DependencyEdge]:
        module_to_path = {
            item.module_path: item.relative_path or item.path
            for item in files
            if item.module_path
        }
        edges: list[DependencyEdge] = []
        for item in files:
            for imported in item.imports:
                module = DependencyAnalyzer._absolute_module(
                    item.module_path, imported.module, imported.relative_level
                )
                target = module_to_path.get(module)
                if target is None and module:
                    init_target = f"{module}.__init__"
                    target = module_to_path.get(init_target)
                if target:
                    imported.resolved_path = target
                    imported.kind = "internal"
                    edges.append(
                        DependencyEdge(
                            source=item.relative_path or item.path,
                            target=target,
                            import_type="relative" if imported.relative_level else "direct",
                            line=imported.line,
                            resolved=True,
                        )
                    )
                elif module.split(".")[0] in STDLIB_MODULES:
                    imported.kind = "stdlib"
                elif imported.relative_level:
                    imported.kind = "unresolved"
                else:
                    imported.kind = "third_party"
        return edges

    @staticmethod
    def _absolute_module(current: str, module: str, level: int) -> str:
        if not level:
            return module
        parts = current.split(".")[:-1]
        keep = max(0, len(parts) - level + 1)
        prefix = parts[:keep]
        return ".".join(prefix + ([module] if module else []))
