"""RAG API request and response schemas."""

from typing import Any
from pydantic import BaseModel, Field

from engines.rag.models import RAGStats


class RAGIndexRequest(BaseModel):
    project_path: str


class RAGSearchRequest(BaseModel):
    project_path: str
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    metadata_filter: dict[str, Any] | None = None


class RAGContextRequest(BaseModel):
    project_path: str
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    metadata_filter: dict[str, Any] | None = None


class RAGIndexResponse(BaseModel):
    stats: RAGStats


class RAGSearchResponse(BaseModel):
    query: str
    project_path: str
    total_results: int
    results: list[dict[str, Any]]


class RAGContextResponse(BaseModel):
    query: str
    project_path: str
    total_chunks_retrieved: int
    context_text: str
    sources: list[dict[str, Any]]


class RAGStatusResponse(BaseModel):
    enabled: bool
    embedding_provider: str
    embedding_model: str
    provider_available: bool
    total_vectors_in_store: int


class RAGStatsResponse(BaseModel):
    project_path: str
    total_chunks: int
    embedding_provider: str
    embedding_model: str


class RAGDeleteResponse(BaseModel):
    project_path: str
    deleted_chunks: int
