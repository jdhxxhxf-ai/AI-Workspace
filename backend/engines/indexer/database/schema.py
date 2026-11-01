"""SQLite schema initialization for the Project Intelligence engine."""

import sqlite3
from pathlib import Path

from shared.utils import ensure_directory

SCHEMA_VERSION = 1

CREATE_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        languages_json TEXT NOT NULL DEFAULT '{}',
        entry_points_json TEXT NOT NULL DEFAULT '[]',
        manifest_files_json TEXT NOT NULL DEFAULT '[]',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        last_indexed_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        relative_path TEXT NOT NULL,
        absolute_path TEXT NOT NULL,
        extension TEXT NOT NULL,
        language TEXT NOT NULL,
        size INTEGER NOT NULL DEFAULT 0,
        modified_at REAL NOT NULL DEFAULT 0,
        content_hash TEXT,
        indexable INTEGER NOT NULL DEFAULT 1,
        skip_reason TEXT,
        module_path TEXT,
        module_docstring TEXT,
        parse_error TEXT,
        UNIQUE(project_id, relative_path),
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS symbols (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        file_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        qualified_name TEXT NOT NULL,
        symbol_type TEXT NOT NULL,
        line_start INTEGER NOT NULL,
        line_end INTEGER,
        parent_symbol TEXT,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS imports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        file_id INTEGER NOT NULL,
        module TEXT NOT NULL,
        imported_symbols_json TEXT NOT NULL DEFAULT '[]',
        alias TEXT,
        relative_level INTEGER NOT NULL DEFAULT 0,
        line INTEGER NOT NULL DEFAULT 0,
        resolved_path TEXT,
        kind TEXT NOT NULL DEFAULT 'unresolved',
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS dependencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        source_path TEXT NOT NULL,
        target_path TEXT NOT NULL,
        relationship TEXT NOT NULL,
        import_type TEXT NOT NULL DEFAULT 'direct',
        line INTEGER NOT NULL DEFAULT 0,
        resolved INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS index_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        scanned INTEGER NOT NULL DEFAULT 0,
        indexed INTEGER NOT NULL DEFAULT 0,
        unchanged INTEGER NOT NULL DEFAULT 0,
        changed INTEGER NOT NULL DEFAULT 0,
        new_count INTEGER NOT NULL DEFAULT 0,
        deleted INTEGER NOT NULL DEFAULT 0,
        failed INTEGER NOT NULL DEFAULT 0,
        duration_ms INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_files_project ON files(project_id)",
    "CREATE INDEX IF NOT EXISTS idx_files_hash ON files(project_id, content_hash)",
    "CREATE INDEX IF NOT EXISTS idx_symbols_project ON symbols(project_id)",
    "CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(project_id, name)",
    "CREATE INDEX IF NOT EXISTS idx_symbols_qualified ON symbols(project_id, qualified_name)",
    "CREATE INDEX IF NOT EXISTS idx_imports_file ON imports(file_id)",
    "CREATE INDEX IF NOT EXISTS idx_dependencies_source ON dependencies(project_id, source_path)",
    "CREATE INDEX IF NOT EXISTS idx_dependencies_target ON dependencies(project_id, target_path)",
]


def initialize_schema(db_path: Path) -> None:
    """Create the SQLite schema if it does not exist."""
    ensure_directory(db_path.parent)
    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for statement in CREATE_STATEMENTS:
            connection.execute(statement)
        row = connection.execute(
            "SELECT version FROM schema_version LIMIT 1"
        ).fetchone()
        if row is None:
            connection.execute(
                "INSERT INTO schema_version(version) VALUES (?)",
                (SCHEMA_VERSION,),
            )
        connection.commit()
