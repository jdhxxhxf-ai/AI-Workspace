"""SQLite-backed persistent repository for Project Intelligence."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config.settings import settings
from engines.indexer.database.models import IndexMetadata, IndexRecord
from engines.indexer.database.schema import initialize_schema
from engines.indexer.models import (
    DependencyEdge,
    FileInfo,
    ImportInfo,
    IndexStats,
    ProjectIndex,
    ProjectSummary,
    PythonFileInfo,
    SymbolInfo,
)
from shared.exceptions import ProjectNotFoundError
from shared.logger import get_logger

logger = get_logger("indexer.repository")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class IndexRepository:
    """Persistent SQLite repository for project indexes."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.indexer_db_path
        initialize_schema(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def save(self, project_path: str, index: ProjectIndex) -> IndexRecord:
        """Full save for Stage 1 compatibility — replaces project index data."""
        stats = self.index_project(project_path, index.files, index.dependencies)
        record = self.get(project_path)
        if record is None:
            raise ProjectNotFoundError(project_path)
        record.file_count = stats.indexed
        return record

    def index_project(
        self,
        project_path: str,
        parsed_files: list[PythonFileInfo],
        dependencies: list[DependencyEdge],
        stats: IndexStats | None = None,
        discovery: dict | None = None,
        scanned_files: list[FileInfo] | None = None,
    ) -> IndexStats:
        """Persist a complete indexing result."""
        root = str(Path(project_path).resolve())
        discovery = discovery or {}
        now = _utc_now()
        final_stats = stats or IndexStats(indexed=len(parsed_files))

        with self._connect() as connection:
            project_id = self._ensure_project(connection, root, discovery, now)
            self._replace_project_data(connection, project_id, parsed_files, dependencies, scanned_files)
            self._record_index_run(connection, project_id, final_stats, now)
            connection.commit()

        logger.info("Indexed project %s (%d files)", root, final_stats.indexed)
        return final_stats

    def refresh_project(
        self,
        project_path: str,
        scanned_files: list[FileInfo],
        parsed_files: list[PythonFileInfo],
        dependencies: list[DependencyEdge],
        stats: IndexStats,
        discovery: dict | None = None,
        deleted_paths: list[str] | None = None,
    ) -> IndexStats:
        """Apply incremental indexing changes to persistent storage."""
        root = str(Path(project_path).resolve())
        discovery = discovery or {}
        now = _utc_now()
        deleted_paths = deleted_paths or []

        with self._connect() as connection:
            project_id = self._ensure_project(connection, root, discovery, now)

            for relative_path in deleted_paths:
                connection.execute(
                    "DELETE FROM files WHERE project_id = ? AND relative_path = ?",
                    (project_id, relative_path),
                )

            parsed_by_path = {
                item.relative_path or item.path: item for item in parsed_files
            }
            for file_info in scanned_files:
                if file_info.language != "Python":
                    self._upsert_non_python_file(connection, project_id, file_info)
                    continue
                parsed = parsed_by_path.get(file_info.relative_path)
                if parsed is None:
                    continue
                file_id = self._upsert_python_file(connection, project_id, file_info, parsed)
                self._replace_file_analysis(connection, project_id, file_id, parsed)

            connection.execute(
                "DELETE FROM dependencies WHERE project_id = ?",
                (project_id,),
            )
            for edge in dependencies:
                connection.execute(
                    """
                    INSERT INTO dependencies(
                        project_id, source_path, target_path, relationship,
                        import_type, line, resolved
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        edge.source,
                        edge.target,
                        edge.relationship,
                        edge.import_type,
                        edge.line,
                        int(edge.resolved),
                    ),
                )

            self._record_index_run(connection, project_id, stats, now)
            connection.execute(
                "UPDATE projects SET updated_at = ?, last_indexed_at = ? WHERE id = ?",
                (now, now, project_id),
            )
            connection.commit()

        return stats

    def get(self, project_path: str) -> IndexRecord | None:
        """Retrieve a legacy-compatible project index record."""
        root = str(Path(project_path).resolve())
        with self._connect() as connection:
            project = connection.execute(
                "SELECT * FROM projects WHERE path = ?", (root,)
            ).fetchone()
            if project is None:
                return None
            files = self._load_python_files(connection, project["id"])
            dependencies = self._load_dependencies(connection, project["id"])
            return IndexRecord(
                project_path=root,
                index=ProjectIndex(files=files, dependencies=dependencies),
                created_at=project["last_indexed_at"] or project["created_at"],
                file_count=len(files),
            )

    def list_all(self) -> list[IndexMetadata]:
        """List metadata for all stored indexes."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT p.path, p.last_indexed_at, p.created_at,
                       COUNT(DISTINCT f.id) AS file_count,
                       COUNT(DISTINCT d.id) AS dependency_count
                FROM projects p
                LEFT JOIN files f ON f.project_id = p.id
                LEFT JOIN dependencies d ON d.project_id = p.id
                GROUP BY p.id
                ORDER BY p.path
                """
            ).fetchall()
        return [
            IndexMetadata(
                project_path=row["path"],
                file_count=row["file_count"],
                dependency_count=row["dependency_count"],
                created_at=row["last_indexed_at"] or row["created_at"],
            )
            for row in rows
        ]

    def delete(self, project_path: str) -> bool:
        """Delete a stored project index."""
        root = str(Path(project_path).resolve())
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM projects WHERE path = ?", (root,)
            )
            connection.commit()
            return cursor.rowcount > 0

    def get_summary(self, project_path: str) -> ProjectSummary:
        """Return deterministic project summary."""
        root = str(Path(project_path).resolve())
        with self._connect() as connection:
            project = connection.execute(
                "SELECT * FROM projects WHERE path = ?", (root,)
            ).fetchone()
            if project is None:
                raise ProjectNotFoundError(root)

            languages = json.loads(project["languages_json"])
            entry_points = json.loads(project["entry_points_json"])
            file_count = connection.execute(
                "SELECT COUNT(*) FROM files WHERE project_id = ?",
                (project["id"],),
            ).fetchone()[0]
            python_file_count = connection.execute(
                "SELECT COUNT(*) FROM files WHERE project_id = ? AND language = 'Python'",
                (project["id"],),
            ).fetchone()[0]
            symbol_count = connection.execute(
                "SELECT COUNT(*) FROM symbols WHERE project_id = ?",
                (project["id"],),
            ).fetchone()[0]
            class_count = connection.execute(
                """
                SELECT COUNT(*) FROM symbols
                WHERE project_id = ? AND symbol_type = 'class'
                """,
                (project["id"],),
            ).fetchone()[0]
            function_count = connection.execute(
                """
                SELECT COUNT(*) FROM symbols
                WHERE project_id = ? AND symbol_type IN ('function', 'method')
                """,
                (project["id"],),
            ).fetchone()[0]
            import_count = connection.execute(
                "SELECT COUNT(*) FROM imports WHERE project_id = ?",
                (project["id"],),
            ).fetchone()[0]
            internal_dependency_count = connection.execute(
                """
                SELECT COUNT(*) FROM dependencies
                WHERE project_id = ? AND resolved = 1
                """,
                (project["id"],),
            ).fetchone()[0]

        return ProjectSummary(
            project_path=root,
            name=project["name"],
            languages=languages,
            file_count=file_count,
            python_file_count=python_file_count,
            symbol_count=symbol_count,
            class_count=class_count,
            function_count=function_count,
            import_count=import_count,
            internal_dependency_count=internal_dependency_count,
            entry_points=entry_points,
            last_indexed_at=project["last_indexed_at"],
        )

    def list_files(
        self, project_path: str, language: str | None = None, limit: int = 200
    ) -> list[dict]:
        """List indexed files for a project."""
        root = str(Path(project_path).resolve())
        with self._connect() as connection:
            project_id = self._project_id(connection, root)
            query = """
                SELECT relative_path, language, size, content_hash, indexable, parse_error
                FROM files WHERE project_id = ?
            """
            params: list = [project_id]
            if language:
                query += " AND language = ?"
                params.append(language)
            query += " ORDER BY relative_path LIMIT ?"
            params.append(limit)
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_file(self, project_path: str, relative_path: str) -> dict | None:
        """Return structural intelligence for a single file."""
        root = str(Path(project_path).resolve())
        with self._connect() as connection:
            project_id = self._project_id(connection, root)
            row = connection.execute(
                """
                SELECT * FROM files
                WHERE project_id = ? AND relative_path = ?
                """,
                (project_id, relative_path),
            ).fetchone()
            if row is None:
                return None
            symbols = connection.execute(
                """
                SELECT name, qualified_name, symbol_type, line_start, line_end, parent_symbol
                FROM symbols WHERE file_id = ? ORDER BY line_start
                """,
                (row["id"],),
            ).fetchall()
            imports = connection.execute(
                """
                SELECT module, imported_symbols_json, alias, relative_level, line,
                       resolved_path, kind
                FROM imports WHERE file_id = ? ORDER BY line
                """,
                (row["id"],),
            ).fetchall()
        return {
            "relative_path": row["relative_path"],
            "language": row["language"],
            "module_path": row["module_path"],
            "module_docstring": row["module_docstring"],
            "parse_error": row["parse_error"],
            "content_hash": row["content_hash"],
            "symbols": [dict(item) for item in symbols],
            "imports": [
                {
                    "module": item["module"],
                    "imported": json.loads(item["imported_symbols_json"]),
                    "alias": item["alias"],
                    "relative_level": item["relative_level"],
                    "line": item["line"],
                    "resolved_path": item["resolved_path"],
                    "kind": item["kind"],
                }
                for item in imports
            ],
        }

    def search_symbols(
        self,
        project_path: str,
        query: str,
        symbol_type: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Search symbols by name within a project."""
        root = str(Path(project_path).resolve())
        limit = limit or settings.indexer_search_limit
        with self._connect() as connection:
            project_id = self._project_id(connection, root)
            sql = """
                SELECT s.name, s.qualified_name, s.symbol_type, s.line_start, s.line_end,
                       f.relative_path AS file
                FROM symbols s
                JOIN files f ON f.id = s.file_id
                WHERE s.project_id = ? AND s.name LIKE ?
            """
            params: list = [project_id, f"%{query}%"]
            if symbol_type:
                sql += " AND s.symbol_type = ?"
                params.append(symbol_type)
            sql += " ORDER BY s.name LIMIT ?"
            params.append(limit)
            rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def get_dependencies(self, project_path: str, source_path: str) -> list[dict]:
        """Return direct dependencies for a file/module."""
        root = str(Path(project_path).resolve())
        with self._connect() as connection:
            project_id = self._project_id(connection, root)
            rows = connection.execute(
                """
                SELECT source_path, target_path, relationship, import_type, line, resolved
                FROM dependencies
                WHERE project_id = ? AND source_path = ?
                ORDER BY line
                """,
                (project_id, source_path),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_dependents(self, project_path: str, target_path: str) -> list[dict]:
        """Return reverse dependencies for a file/module."""
        root = str(Path(project_path).resolve())
        with self._connect() as connection:
            project_id = self._project_id(connection, root)
            rows = connection.execute(
                """
                SELECT source_path, target_path, relationship, import_type, line, resolved
                FROM dependencies
                WHERE project_id = ? AND target_path = ?
                ORDER BY source_path, line
                """,
                (project_id, target_path),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_graph(self, project_path: str) -> dict:
        """Return a structural dependency graph."""
        root = str(Path(project_path).resolve())
        with self._connect() as connection:
            project_id = self._project_id(connection, root)
            files = connection.execute(
                """
                SELECT relative_path, language, module_path
                FROM files WHERE project_id = ?
                """,
                (project_id,),
            ).fetchall()
            edges = connection.execute(
                """
                SELECT source_path, target_path, relationship, resolved
                FROM dependencies WHERE project_id = ?
                """,
                (project_id,),
            ).fetchall()
        nodes = [
            {
                "id": row["relative_path"],
                "type": "module" if row["language"] == "Python" else "file",
                "language": row["language"],
                "module_path": row["module_path"],
            }
            for row in files
        ]
        return {
            "nodes": nodes,
            "edges": [
                {
                    "source": row["source_path"],
                    "target": row["target_path"],
                    "relationship": row["relationship"],
                    "resolved": bool(row["resolved"]),
                }
                for row in edges
            ],
        }

    def get_file_hashes(self, project_path: str) -> dict[str, str]:
        """Return stored content hashes keyed by relative path."""
        root = str(Path(project_path).resolve())
        with self._connect() as connection:
            project = connection.execute(
                "SELECT id FROM projects WHERE path = ?", (root,)
            ).fetchone()
            if project is None:
                return {}
            rows = connection.execute(
                """
                SELECT relative_path, content_hash FROM files
                WHERE project_id = ? AND content_hash IS NOT NULL
                """,
                (project["id"],),
            ).fetchall()
        return {row["relative_path"]: row["content_hash"] for row in rows}

    def _project_id(self, connection: sqlite3.Connection, project_path: str) -> int:
        row = connection.execute(
            "SELECT id FROM projects WHERE path = ?", (project_path,)
        ).fetchone()
        if row is None:
            raise ProjectNotFoundError(project_path)
        return row["id"]

    def _ensure_project(
        self,
        connection: sqlite3.Connection,
        project_path: str,
        discovery: dict,
        now: str,
    ) -> int:
        row = connection.execute(
            "SELECT id FROM projects WHERE path = ?", (project_path,)
        ).fetchone()
        languages_json = json.dumps(discovery.get("languages", {}))
        entry_points_json = json.dumps(discovery.get("entry_points", []))
        manifest_files_json = json.dumps(discovery.get("manifest_files", []))
        name = discovery.get("name", Path(project_path).name)

        if row is None:
            cursor = connection.execute(
                """
                INSERT INTO projects(
                    path, name, languages_json, entry_points_json,
                    manifest_files_json, created_at, updated_at, last_indexed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_path,
                    name,
                    languages_json,
                    entry_points_json,
                    manifest_files_json,
                    now,
                    now,
                    now,
                ),
            )
            return cursor.lastrowid

        connection.execute(
            """
            UPDATE projects
            SET name = ?, languages_json = ?, entry_points_json = ?,
                manifest_files_json = ?, updated_at = ?, last_indexed_at = ?
            WHERE id = ?
            """,
            (
                name,
                languages_json,
                entry_points_json,
                manifest_files_json,
                now,
                now,
                row["id"],
            ),
        )
        return row["id"]

    def _replace_project_data(
        self,
        connection: sqlite3.Connection,
        project_id: int,
        parsed_files: list[PythonFileInfo],
        dependencies: list[DependencyEdge],
        scanned_files: list[FileInfo] | None = None,
    ) -> None:
        connection.execute("DELETE FROM files WHERE project_id = ?", (project_id,))
        connection.execute(
            "DELETE FROM dependencies WHERE project_id = ?", (project_id,)
        )
        scanned_map = {item.relative_path: item for item in (scanned_files or [])}
        for file_info in scanned_files or []:
            if file_info.language != "Python":
                self._upsert_non_python_file(connection, project_id, file_info)

        for parsed in parsed_files:
            rel = parsed.relative_path or Path(parsed.path).name
            scanned_info = scanned_map.get(rel)
            if scanned_info:
                file_info = scanned_info
            else:
                file_info = FileInfo(
                    relative_path=rel,
                    absolute_path=parsed.path,
                    extension=".py",
                    language="Python",
                    size=0,
                    modified_at=0.0,
                    indexable=True,
                )
            file_id = self._upsert_python_file(
                connection, project_id, file_info, parsed
            )
            self._replace_file_analysis(connection, project_id, file_id, parsed)

        for edge in dependencies:
            connection.execute(
                """
                INSERT INTO dependencies(
                    project_id, source_path, target_path, relationship,
                    import_type, line, resolved
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    edge.source,
                    edge.target,
                    edge.relationship,
                    edge.import_type,
                    edge.line,
                    int(edge.resolved),
                ),
            )

    def _upsert_non_python_file(
        self,
        connection: sqlite3.Connection,
        project_id: int,
        file_info: FileInfo,
    ) -> None:
        connection.execute(
            """
            INSERT INTO files(
                project_id, relative_path, absolute_path, extension, language,
                size, modified_at, content_hash, indexable, skip_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, relative_path) DO UPDATE SET
                absolute_path = excluded.absolute_path,
                size = excluded.size,
                modified_at = excluded.modified_at,
                content_hash = excluded.content_hash,
                indexable = excluded.indexable,
                skip_reason = excluded.skip_reason
            """,
            (
                project_id,
                file_info.relative_path,
                file_info.absolute_path,
                file_info.extension,
                file_info.language,
                file_info.size,
                file_info.modified_at,
                file_info.content_hash,
                int(file_info.indexable),
                file_info.skip_reason,
            ),
        )

    def _upsert_python_file(
        self,
        connection: sqlite3.Connection,
        project_id: int,
        file_info: FileInfo,
        parsed: PythonFileInfo,
    ) -> int:
        connection.execute(
            """
            INSERT INTO files(
                project_id, relative_path, absolute_path, extension, language,
                size, modified_at, content_hash, indexable, skip_reason,
                module_path, module_docstring, parse_error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, relative_path) DO UPDATE SET
                absolute_path = excluded.absolute_path,
                size = excluded.size,
                modified_at = excluded.modified_at,
                content_hash = excluded.content_hash,
                indexable = excluded.indexable,
                skip_reason = excluded.skip_reason,
                module_path = excluded.module_path,
                module_docstring = excluded.module_docstring,
                parse_error = excluded.parse_error
            """,
            (
                project_id,
                file_info.relative_path,
                file_info.absolute_path,
                file_info.extension,
                file_info.language,
                file_info.size,
                file_info.modified_at,
                file_info.content_hash,
                int(file_info.indexable),
                file_info.skip_reason,
                parsed.module_path,
                parsed.module_docstring,
                parsed.parse_error,
            ),
        )
        row = connection.execute(
            """
            SELECT id FROM files
            WHERE project_id = ? AND relative_path = ?
            """,
            (project_id, file_info.relative_path),
        ).fetchone()
        return row["id"]

    def _replace_file_analysis(
        self,
        connection: sqlite3.Connection,
        project_id: int,
        file_id: int,
        parsed: PythonFileInfo,
    ) -> None:
        connection.execute("DELETE FROM symbols WHERE file_id = ?", (file_id,))
        connection.execute("DELETE FROM imports WHERE file_id = ?", (file_id,))

        for symbol in parsed.symbols:
            connection.execute(
                """
                INSERT INTO symbols(
                    project_id, file_id, name, qualified_name, symbol_type,
                    line_start, line_end, parent_symbol, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    file_id,
                    symbol.name,
                    symbol.qualified_name,
                    symbol.symbol_type,
                    symbol.line_start,
                    symbol.line_end,
                    symbol.parent_symbol,
                    json.dumps(symbol.metadata),
                ),
            )

        for imported in parsed.imports:
            connection.execute(
                """
                INSERT INTO imports(
                    project_id, file_id, module, imported_symbols_json, alias,
                    relative_level, line, resolved_path, kind
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    file_id,
                    imported.module,
                    json.dumps(imported.imported),
                    imported.alias,
                    imported.relative_level,
                    imported.line,
                    imported.resolved_path,
                    imported.kind,
                ),
            )

    def _record_index_run(
        self,
        connection: sqlite3.Connection,
        project_id: int,
        stats: IndexStats,
        now: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO index_runs(
                project_id, started_at, completed_at, scanned, indexed, unchanged,
                changed, new_count, deleted, failed, duration_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                now,
                now,
                stats.scanned,
                stats.indexed,
                stats.unchanged,
                stats.changed,
                stats.new,
                stats.deleted,
                stats.failed,
                stats.duration_ms,
            ),
        )

    def _load_python_files(
        self, connection: sqlite3.Connection, project_id: int
    ) -> list[PythonFileInfo]:
        rows = connection.execute(
            """
            SELECT * FROM files
            WHERE project_id = ? AND language = 'Python'
            ORDER BY relative_path
            """,
            (project_id,),
        ).fetchall()
        files: list[PythonFileInfo] = []
        for row in rows:
            symbols = self._load_symbols(connection, row["id"])
            imports = self._load_imports(connection, row["id"])
            files.append(
                PythonFileInfo(
                    path=row["absolute_path"],
                    relative_path=row["relative_path"],
                    module_path=row["module_path"] or "",
                    module_docstring=row["module_docstring"],
                    imports=imports,
                    classes=[
                        ClassInfoFromSymbol(symbol)
                        for symbol in symbols
                        if symbol.symbol_type == "class"
                    ],
                    functions=[
                        FunctionInfoFromSymbol(symbol)
                        for symbol in symbols
                        if symbol.symbol_type == "function"
                    ],
                    symbols=symbols,
                    parse_error=row["parse_error"],
                )
            )
        return files

    def _load_symbols(
        self, connection: sqlite3.Connection, file_id: int
    ) -> list[SymbolInfo]:
        rows = connection.execute(
            """
            SELECT name, qualified_name, symbol_type, line_start, line_end,
                   parent_symbol, metadata_json
            FROM symbols WHERE file_id = ?
            ORDER BY line_start
            """,
            (file_id,),
        ).fetchall()
        return [
            SymbolInfo(
                name=row["name"],
                qualified_name=row["qualified_name"],
                symbol_type=row["symbol_type"],
                line_start=row["line_start"],
                line_end=row["line_end"],
                parent_symbol=row["parent_symbol"],
                metadata=json.loads(row["metadata_json"]),
            )
            for row in rows
        ]

    def _load_imports(
        self, connection: sqlite3.Connection, file_id: int
    ) -> list[ImportInfo]:
        rows = connection.execute(
            """
            SELECT module, imported_symbols_json, alias, relative_level, line,
                   resolved_path, kind
            FROM imports WHERE file_id = ?
            ORDER BY line
            """,
            (file_id,),
        ).fetchall()
        return [
            ImportInfo(
                module=row["module"],
                imported=json.loads(row["imported_symbols_json"]),
                alias=row["alias"],
                relative_level=row["relative_level"],
                line=row["line"],
                resolved_path=row["resolved_path"],
                kind=row["kind"],
            )
            for row in rows
        ]

    def _load_dependencies(
        self, connection: sqlite3.Connection, project_id: int
    ) -> list[DependencyEdge]:
        rows = connection.execute(
            """
            SELECT source_path, target_path, relationship, import_type, line, resolved
            FROM dependencies WHERE project_id = ?
            """,
            (project_id,),
        ).fetchall()
        return [
            DependencyEdge(
                source=row["source_path"],
                target=row["target_path"],
                relationship=row["relationship"],
                import_type=row["import_type"],
                line=row["line"],
                resolved=bool(row["resolved"]),
            )
            for row in rows
        ]


def ClassInfoFromSymbol(symbol: SymbolInfo):
    from engines.indexer.models import ClassInfo

    return ClassInfo(
        name=symbol.name,
        qualified_name=symbol.qualified_name,
        line=symbol.line_start,
        end_line=symbol.line_end,
        bases=symbol.metadata.get("bases", []),
        decorators=symbol.metadata.get("decorators", []),
    )


def FunctionInfoFromSymbol(symbol: SymbolInfo):
    from engines.indexer.models import FunctionInfo

    return FunctionInfo(
        name=symbol.name,
        qualified_name=symbol.qualified_name,
        line=symbol.line_start,
        end_line=symbol.line_end,
        is_async=symbol.metadata.get("async", False),
        decorators=symbol.metadata.get("decorators", []),
    )


index_repository = IndexRepository()
