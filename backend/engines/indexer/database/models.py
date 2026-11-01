"""Indexer database models."""

from pydantic import BaseModel, Field

from engines.indexer.models import ProjectIndex


class IndexRecord(BaseModel):
    """A stored project index record."""

    project_path: str
    index: ProjectIndex
    created_at: str = ""
    file_count: int = 0


class IndexMetadata(BaseModel):
    """Metadata about a stored index."""

    project_path: str
    file_count: int = 0
    dependency_count: int = 0
    created_at: str = ""
