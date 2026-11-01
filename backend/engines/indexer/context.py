"""Structural project context for future Context/RAG engines."""

from engines.indexer.database.repository import IndexRepository, index_repository
from engines.indexer.service import project_intelligence
from shared.exceptions import ProjectNotFoundError


class ProjectContextBuilder:
    """Build compact deterministic project context without LLM involvement."""

    def __init__(self, repository: IndexRepository | None = None) -> None:
        self._repository = repository

    @property
    def repository(self) -> IndexRepository:
        return self._repository or project_intelligence.repository

    def build(self, project_path: str, focus_path: str | None = None) -> dict:
        """Return structural context suitable for downstream engines."""
        summary = self.repository.get_summary(project_path)
        files = self.repository.list_files(project_path, limit=50)
        graph = self.repository.get_graph(project_path)

        context = {
            "project": {
                "path": summary.project_path,
                "name": summary.name,
                "languages": summary.languages,
                "entry_points": summary.entry_points,
            },
            "counts": {
                "files": summary.file_count,
                "python_files": summary.python_file_count,
                "symbols": summary.symbol_count,
                "classes": summary.class_count,
                "functions": summary.function_count,
                "imports": summary.import_count,
                "internal_dependencies": summary.internal_dependency_count,
            },
            "important_files": files[:20],
            "relationships": graph["edges"][:100],
        }

        if focus_path:
            file_intel = self.repository.get_file(project_path, focus_path)
            if file_intel:
                context["focus_file"] = file_intel
                context["focus_dependencies"] = self.repository.get_dependencies(
                    project_path, focus_path
                )
                context["focus_dependents"] = self.repository.get_dependents(
                    project_path, focus_path
                )

        return context


project_context_builder = ProjectContextBuilder()
