"""Persistent local vector and metadata store using SQLite."""

import json
import math
import sqlite3
import struct
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from config.settings import settings
from engines.rag.models import ChunkMetadata, KnowledgeChunk
from shared.logger import get_logger
from shared.utils import ensure_directory

logger = get_logger("rag.storage")


class VectorStore(ABC):
    """Abstract interface for local vector storage."""

    @abstractmethod
    def upsert_chunks(self, chunks: list[KnowledgeChunk]) -> int:
        pass

    @abstractmethod
    def delete_project(self, project_path: str) -> int:
        pass

    @abstractmethod
    def delete_file_chunks(self, project_path: str, relative_path: str) -> int:
        pass

    @abstractmethod
    def similarity_search(
        self,
        query_vector: list[float],
        project_path: str,
        top_k: int = 10,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[tuple[KnowledgeChunk, float]]:
        pass

    @abstractmethod
    def get_file_hashes(self, project_path: str) -> dict[str, str]:
        pass

    @abstractmethod
    def count(self, project_path: str | None = None) -> int:
        pass


class SQLiteVectorStore(VectorStore):
    """Local SQLite-backed persistent vector store."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.rag_vector_db_path
        self._initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize_schema(self) -> None:
        ensure_directory(self.db_path.parent)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    project_path TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    relative_path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    symbol_name TEXT,
                    symbol_type TEXT,
                    qualified_name TEXT,
                    parent_symbol TEXT,
                    line_start INTEGER NOT NULL,
                    line_end INTEGER,
                    content TEXT NOT NULL,
                    content_hash TEXT,
                    chunk_hash TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    vector_blob BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vec_proj ON vector_chunks(project_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vec_rel ON vector_chunks(project_path, relative_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vec_sym ON vector_chunks(project_path, symbol_name)")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS file_hashes (
                    project_path TEXT NOT NULL,
                    relative_path TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    PRIMARY KEY (project_path, relative_path)
                )
                """
            )
            conn.commit()

    @staticmethod
    def _pack_vector(vec: list[float]) -> bytes:
        return struct.pack(f"{len(vec)}f", *vec)

    @staticmethod
    def _unpack_vector(blob: bytes) -> list[float]:
        count = len(blob) // 4
        return list(struct.unpack(f"{count}f", blob))

    def upsert_chunks(self, chunks: list[KnowledgeChunk]) -> int:
        if not chunks:
            return 0
        with self._connect() as conn:
            for chunk in chunks:
                m = chunk.metadata
                blob = self._pack_vector(chunk.vector)
                conn.execute(
                    """
                    INSERT INTO vector_chunks (
                        chunk_id, project_path, file_path, relative_path, language,
                        document_type, source_type, symbol_name, symbol_type,
                        qualified_name, parent_symbol, line_start, line_end,
                        content, content_hash, chunk_hash, chunk_index,
                        vector_blob, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(chunk_id) DO UPDATE SET
                        content = excluded.content,
                        content_hash = excluded.content_hash,
                        chunk_hash = excluded.chunk_hash,
                        symbol_name = excluded.symbol_name,
                        symbol_type = excluded.symbol_type,
                        qualified_name = excluded.qualified_name,
                        parent_symbol = excluded.parent_symbol,
                        line_start = excluded.line_start,
                        line_end = excluded.line_end,
                        vector_blob = excluded.vector_blob,
                        updated_at = excluded.updated_at
                    """,
                    (
                        chunk.chunk_id,
                        m.project_path,
                        m.file_path,
                        m.relative_path,
                        m.language,
                        m.document_type,
                        m.source_type,
                        m.symbol_name,
                        m.symbol_type,
                        m.qualified_name,
                        m.parent_symbol,
                        m.line_start,
                        m.line_end,
                        chunk.content,
                        m.content_hash,
                        m.chunk_hash,
                        m.chunk_index,
                        blob,
                        m.created_at,
                        m.updated_at,
                    ),
                )
            conn.commit()
        return len(chunks)

    def save_file_hashes(self, project_path: str, file_hashes: dict[str, str]) -> None:
        if not file_hashes:
            return
        with self._connect() as conn:
            for rel_path, content_hash in file_hashes.items():
                if content_hash:
                    conn.execute(
                        """
                        INSERT INTO file_hashes (project_path, relative_path, content_hash)
                        VALUES (?, ?, ?)
                        ON CONFLICT(project_path, relative_path) DO UPDATE SET
                            content_hash = excluded.content_hash
                        """,
                        (project_path, rel_path, content_hash),
                    )
            conn.commit()

    def delete_project(self, project_path: str) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM vector_chunks WHERE project_path = ?", (project_path,)
            )
            conn.execute(
                "DELETE FROM file_hashes WHERE project_path = ?", (project_path,)
            )
            conn.commit()
            return cursor.rowcount

    def delete_file_chunks(self, project_path: str, relative_path: str) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM vector_chunks WHERE project_path = ? AND relative_path = ?",
                (project_path, relative_path),
            )
            conn.execute(
                "DELETE FROM file_hashes WHERE project_path = ? AND relative_path = ?",
                (project_path, relative_path),
            )
            conn.commit()
            return cursor.rowcount

    def get_file_hashes(self, project_path: str) -> dict[str, str]:
        """Return dict mapping relative_path -> content_hash for project."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT relative_path, content_hash
                FROM file_hashes
                WHERE project_path = ?
                """,
                (project_path,),
            ).fetchall()
        return {row["relative_path"]: row["content_hash"] for row in rows}

    def count(self, project_path: str | None = None) -> int:
        with self._connect() as conn:
            if project_path:
                row = conn.execute(
                    "SELECT COUNT(*) FROM vector_chunks WHERE project_path = ?",
                    (project_path,),
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) FROM vector_chunks").fetchone()
            return row[0] if row else 0

    def similarity_search(
        self,
        query_vector: list[float],
        project_path: str,
        top_k: int = 10,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[tuple[KnowledgeChunk, float]]:
        if not query_vector:
            return []

        sql = "SELECT * FROM vector_chunks WHERE project_path = ?"
        params: list[Any] = [project_path]

        if metadata_filter:
            if "language" in metadata_filter:
                sql += " AND language = ?"
                params.append(metadata_filter["language"])
            if "source_type" in metadata_filter:
                sql += " AND source_type = ?"
                params.append(metadata_filter["source_type"])
            if "symbol_type" in metadata_filter:
                sql += " AND symbol_type = ?"
                params.append(metadata_filter["symbol_type"])
            if "relative_path" in metadata_filter:
                sql += " AND relative_path = ?"
                params.append(metadata_filter["relative_path"])

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        scored: list[tuple[KnowledgeChunk, float]] = []
        for row in rows:
            vec = self._unpack_vector(row["vector_blob"])
            score = self._cosine_similarity(query_vector, vec)
            chunk = KnowledgeChunk(
                chunk_id=row["chunk_id"],
                content=row["content"],
                vector=vec,
                metadata=ChunkMetadata(
                    project_path=row["project_path"],
                    file_path=row["file_path"],
                    relative_path=row["relative_path"],
                    language=row["language"],
                    document_type=row["document_type"],
                    source_type=row["source_type"],
                    symbol_name=row["symbol_name"],
                    symbol_type=row["symbol_type"],
                    qualified_name=row["qualified_name"],
                    parent_symbol=row["parent_symbol"],
                    line_start=row["line_start"],
                    line_end=row["line_end"],
                    content_hash=row["content_hash"],
                    chunk_hash=row["chunk_hash"],
                    chunk_index=row["chunk_index"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                ),
            )
            scored.append((chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    @staticmethod
    def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
