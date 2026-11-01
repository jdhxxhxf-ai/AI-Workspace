"""RAG Engine configuration."""

from dataclasses import dataclass, field
from pathlib import Path

from config.settings import settings


@dataclass
class RAGConfig:
    """Configurable RAG parameters."""

    enabled: bool = field(default_factory=lambda: settings.rag_enabled)
    embedding_provider: str = field(default_factory=lambda: settings.rag_embedding_provider)
    embedding_model: str = field(default_factory=lambda: settings.rag_embedding_model)
    vector_db_path: Path = field(default_factory=lambda: settings.rag_vector_db_path)
    top_k: int = field(default_factory=lambda: settings.rag_top_k)
    chunk_size: int = field(default_factory=lambda: settings.rag_chunk_size)
    chunk_overlap: int = field(default_factory=lambda: settings.rag_chunk_overlap)
    batch_size: int = field(default_factory=lambda: settings.rag_batch_size)
