"""Data models for the RAG & Knowledge Engine."""

from typing import Any
from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """Normalized metadata for a knowledge chunk."""

    project_id: str = ""
    project_path: str
    file_id: int | None = None
    file_path: str
    relative_path: str = ""
    language: str = ""
    document_type: str = ""
    symbol_name: str | None = None
    symbol_type: str | None = None
    qualified_name: str | None = None
    parent_symbol: str | None = None
    line_start: int = 1
    line_end: int | None = None
    content_hash: str | None = None
    chunk_hash: str = ""
    chunk_index: int = 0
    source_type: str = "source_code"
    created_at: str = ""
    updated_at: str = ""


class KnowledgeChunk(BaseModel):
    """A semantic chunk of code or documentation with vector embedding."""

    chunk_id: str = ""
    content: str
    vector: list[float] = Field(default_factory=list)
    metadata: ChunkMetadata


class KnowledgeDocument(BaseModel):
    """Raw document representation extracted from a file."""

    file_path: str
    relative_path: str
    language: str
    source_type: str
    content: str
    content_hash: str
    ast_symbols: list[dict[str, Any]] = Field(default_factory=list)
    ast_imports: list[dict[str, Any]] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    """A ranked result item from hybrid retrieval."""

    chunk_id: str
    score: float
    content: str
    file_path: str
    relative_path: str
    language: str
    source_type: str
    symbol_name: str | None = None
    symbol_type: str | None = None
    qualified_name: str | None = None
    line_start: int = 1
    line_end: int | None = None
    vector_score: float = 0.0
    lexical_score: float = 0.0


class RAGStats(BaseModel):
    """Audit statistics for a RAG indexing run."""

    scanned_files: int = 0
    indexed_documents: int = 0
    total_chunks: int = 0
    unchanged_files: int = 0
    changed_files: int = 0
    new_files: int = 0
    deleted_files: int = 0
    duration_ms: int = 0
    embedding_provider: str = ""
    embedding_model: str = ""


class ContextPayload(BaseModel):
    """Structured context payload assembled for AI Agents."""

    query: str
    project_path: str
    total_chunks_retrieved: int = 0
    context_text: str = ""
    sources: list[dict[str, Any]] = Field(default_factory=list)
