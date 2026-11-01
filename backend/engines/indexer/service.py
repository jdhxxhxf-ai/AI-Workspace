"""High-level Project Intelligence service."""

import time
from pathlib import Path

from engines.indexer.database.repository import IndexRepository, index_repository
from engines.indexer.discovery import ProjectDiscovery
from engines.indexer.graph_builder import GraphBuilder
from engines.indexer.language import is_indexable_language
from engines.indexer.models import IndexStats, ProjectIndex, PythonFileInfo
from engines.indexer.parser import PythonParser
from engines.indexer.scanner import ProjectScanner
from shared.exceptions import IndexerError, ProjectNotFoundError, WorkspaceNotFoundError
from shared.logger import get_logger

logger = get_logger("indexer.service")


class ProjectIntelligenceService:
    """Orchestrates scanning, parsing, persistence, and deterministic queries."""

    def __init__(self, repository: IndexRepository | None = None) -> None:
        self.repository = repository or index_repository
        self.parser = PythonParser()

    def index_project(self, project_path: str) -> dict:
        """Perform a full project index and persist results."""
        started = time.perf_counter()
        root = self._resolve_project_path(project_path)
        discovery = ProjectDiscovery(str(root)).discover()
        scanner = ProjectScanner(str(root))
        scanned_files = scanner.scan_files()
        parsed_files, failed = self._parse_python_files(scanned_files, str(root))
        index = GraphBuilder.build(parsed_files)
        stats = IndexStats(
            scanned=len(scanned_files),
            indexed=len(parsed_files),
            new=len(parsed_files),
            failed=failed,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        self.repository.index_project(
            str(root), parsed_files, index.dependencies, stats, discovery, scanned_files
        )
        return self._legacy_scan_response(index, stats)

    def refresh_project(self, project_path: str) -> dict:
        """Perform incremental indexing based on content hashes."""
        started = time.perf_counter()
        root = self._resolve_project_path(project_path)
        discovery = ProjectDiscovery(str(root)).discover()
        scanner = ProjectScanner(str(root))
        scanned_files = scanner.scan_files()
        existing_hashes = self.repository.get_file_hashes(str(root))

        to_parse: list = []
        unchanged = 0
        changed = 0
        new = 0
        failed = 0
        scanned_paths = {item.relative_path for item in scanned_files}
        deleted_paths = sorted(set(existing_hashes) - scanned_paths)

        for file_info in scanned_files:
            if not is_indexable_language(file_info.language):
                continue
            if not file_info.indexable:
                continue
            previous_hash = existing_hashes.get(file_info.relative_path)
            if previous_hash is None:
                new += 1
                to_parse.append(file_info)
            elif previous_hash != file_info.content_hash:
                changed += 1
                to_parse.append(file_info)
            else:
                unchanged += 1

        parsed_files, failed = self._parse_scanned_files(to_parse, str(root))
        unchanged_files = self._load_unchanged_python_files(
            str(root), scanned_files, existing_hashes, to_parse
        )
        all_parsed = parsed_files + unchanged_files
        index = GraphBuilder.build(all_parsed)
        stats = IndexStats(
            scanned=len(scanned_files),
            indexed=len(all_parsed),
            unchanged=unchanged,
            changed=changed,
            new=new,
            deleted=len(deleted_paths),
            failed=failed,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        self.repository.refresh_project(
            str(root),
            scanned_files,
            parsed_files,
            index.dependencies,
            stats,
            discovery,
            deleted_paths,
        )
        return {
            "stats": stats.model_dump(),
            "files": [item.model_dump() for item in index.files],
            "dependencies": [item.model_dump() for item in index.dependencies],
        }

    def get_project_summary(self, project_path: str) -> dict:
        """Return deterministic project summary."""
        root = str(self._resolve_project_path(project_path))
        return self.repository.get_summary(root).model_dump()

    def list_files(
        self, project_path: str, language: str | None = None, limit: int = 200
    ) -> dict:
        root = str(self._resolve_project_path(project_path))
        return {"files": self.repository.list_files(root, language, limit)}

    def get_file_intelligence(self, project_path: str, relative_path: str) -> dict:
        root = str(self._resolve_project_path(project_path))
        result = self.repository.get_file(root, relative_path)
        if result is None:
            raise IndexerError(f"File not found in index: {relative_path}")
        return result

    def search_symbols(
        self,
        project_path: str,
        query: str,
        symbol_type: str | None = None,
        limit: int | None = None,
    ) -> dict:
        root = str(self._resolve_project_path(project_path))
        return {
            "symbols": self.repository.search_symbols(
                root, query, symbol_type, limit
            )
        }

    def get_dependencies(self, project_path: str, source_path: str) -> dict:
        root = str(self._resolve_project_path(project_path))
        return {
            "dependencies": self.repository.get_dependencies(root, source_path)
        }

    def get_dependents(self, project_path: str, target_path: str) -> dict:
        root = str(self._resolve_project_path(project_path))
        return {"dependents": self.repository.get_dependents(root, target_path)}

    def get_graph(self, project_path: str) -> dict:
        root = str(self._resolve_project_path(project_path))
        return self.repository.get_graph(root)

    def list_indexes(self) -> dict:
        return {"indexes": self.repository.list_all()}

    def _resolve_project_path(self, project_path: str) -> Path:
        root = Path(project_path).resolve()
        if not root.is_dir():
            raise WorkspaceNotFoundError(project_path)
        return root

    def _parse_python_files(
        self, scanned_files: list, project_root: str
    ) -> tuple[list[PythonFileInfo], int]:
        to_parse = [
            item
            for item in scanned_files
            if is_indexable_language(item.language) and item.indexable
        ]
        return self._parse_scanned_files(to_parse, project_root)

    def _parse_scanned_files(
        self, files: list, project_root: str
    ) -> tuple[list[PythonFileInfo], int]:
        parsed: list[PythonFileInfo] = []
        failed = 0
        for file_info in files:
            result = self.parser.parse(file_info.absolute_path, project_root)
            if result.parse_error:
                failed += 1
                logger.warning(
                    "Parse failed for %s: %s",
                    file_info.relative_path,
                    result.parse_error,
                )
            parsed.append(result)
        return parsed, failed

    def _load_unchanged_python_files(
        self,
        project_path: str,
        scanned_files: list,
        existing_hashes: dict[str, str],
        changed_files: list,
    ) -> list[PythonFileInfo]:
        changed_paths = {item.relative_path for item in changed_files}
        unchanged_paths = [
            item.relative_path
            for item in scanned_files
            if (
                is_indexable_language(item.language)
                and item.indexable
                and item.relative_path in existing_hashes
                and item.relative_path not in changed_paths
            )
        ]
        if not unchanged_paths:
            return []
        try:
            record = self.repository.get(project_path)
        except ProjectNotFoundError:
            return []
        if record is None:
            return []
        by_path = {
            item.relative_path or item.path: item for item in record.index.files
        }
        return [by_path[path] for path in unchanged_paths if path in by_path]

    @staticmethod
    def _legacy_scan_response(index: ProjectIndex, stats: IndexStats) -> dict:
        return {
            "files": [item.model_dump() for item in index.files],
            "dependencies": [item.model_dump() for item in index.dependencies],
            "stats": stats.model_dump(),
        }


project_intelligence = ProjectIntelligenceService()
