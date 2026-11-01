"""Project Intelligence API request/response models."""

from typing import Any

from pydantic import BaseModel, Field

from engines.indexer.models import IndexStats


class IndexResponse(BaseModel):
    files: list[dict[str, Any]]
    dependencies: list[dict[str, Any]]
    stats: IndexStats | None = None


class RefreshResponse(BaseModel):
    stats: IndexStats
    files: list[dict[str, Any]]
    dependencies: list[dict[str, Any]]


class SymbolSearchResponse(BaseModel):
    symbols: list[dict[str, Any]]


class FileListResponse(BaseModel):
    files: list[dict[str, Any]]


class DependencyListResponse(BaseModel):
    dependencies: list[dict[str, Any]] = Field(default_factory=list)
    dependents: list[dict[str, Any]] = Field(default_factory=list)
