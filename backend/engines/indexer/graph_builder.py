"""Build queryable, deterministic structural graphs."""

from engines.indexer.dependency_analyzer import DependencyAnalyzer
from engines.indexer.models import DependencyEdge, ProjectIndex, PythonFileInfo


class GraphBuilder:
    @staticmethod
    def build(files: list[PythonFileInfo]) -> ProjectIndex:
        dependencies = DependencyAnalyzer.analyze(files)
        dependencies.extend(GraphBuilder._inheritance_edges(files))
        return ProjectIndex(files=files, dependencies=dependencies)

    @staticmethod
    def _inheritance_edges(files: list[PythonFileInfo]) -> list[DependencyEdge]:
        """Add INHERITS_FROM edges where base classes map to indexed modules."""
        module_to_path = {
            item.module_path: item.relative_path or item.path
            for item in files
            if item.module_path
        }
        edges: list[DependencyEdge] = []
        for item in files:
            for class_info in item.classes:
                for base in class_info.bases:
                    base_name = base.split(".")[-1] if base else ""
                    for module_path, relative_path in module_to_path.items():
                        if module_path.endswith(f".{base_name}") or module_path == base_name:
                            edges.append(
                                DependencyEdge(
                                    source=item.relative_path or item.path,
                                    target=relative_path,
                                    relationship="INHERITS_FROM",
                                    import_type="inheritance",
                                    line=class_info.line,
                                    resolved=True,
                                )
                            )
                            break
        return edges

    @staticmethod
    def get_file_dependencies(index: ProjectIndex, file_path: str) -> list[DependencyEdge]:
        return [edge for edge in index.dependencies if edge.source == file_path]

    @staticmethod
    def get_dependents(index: ProjectIndex, module: str) -> list[DependencyEdge]:
        return [edge for edge in index.dependencies if edge.target == module]
