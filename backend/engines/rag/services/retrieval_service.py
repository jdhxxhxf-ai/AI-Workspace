"""High-level KnowledgeRetrievalService orchestrating indexing, search, and context assembly."""

from pathlib import Path
from typing import Any

from engines.indexer.database.repository import IndexRepository, index_repository
from engines.rag.config import RAGConfig
from engines.rag.embeddings.provider import EmbeddingProvider, get_embedding_provider
from engines.rag.indexing.manager import RAGIndexManager
from engines.rag.models import ContextPayload, RAGStats, RetrievalResult
from engines.rag.retrieval.hybrid_retriever import HybridRetriever
from engines.rag.services.context_builder import KnowledgeContextBuilder
from engines.rag.storage.vector_store import SQLiteVectorStore, VectorStore
from shared.exceptions import WorkspaceNotFoundError


class KnowledgeRetrievalService:
    """High-level RAG domain service for project indexing, hybrid retrieval, and context building."""

    def __init__(
        self,
        embedder: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
        repository: IndexRepository | None = None,
        config: RAGConfig | None = None,
    ) -> None:
        self.config = config or RAGConfig()
        self._embedder = embedder
        self._vector_store = vector_store
        self._repository = repository
        self.context_builder = KnowledgeContextBuilder()

    @property
    def embedder(self) -> EmbeddingProvider:
        if self._embedder is None:
            self._embedder = get_embedding_provider(self.config)
        return self._embedder

    @property
    def vector_store(self) -> VectorStore:
        if self._vector_store is None:
            self._vector_store = SQLiteVectorStore(self.config.vector_db_path)
        return self._vector_store

    @property
    def repository(self) -> IndexRepository:
        return self._repository or index_repository

    @property
    def index_manager(self) -> RAGIndexManager:
        return RAGIndexManager(
            embedder=self.embedder,
            vector_store=self.vector_store,
            repository=self.repository,
            config=self.config,
        )

    @property
    def retriever(self) -> HybridRetriever:
        return HybridRetriever(
            embedder=self.embedder,
            vector_store=self.vector_store,
            config=self.config,
        )

    def index_project(self, project_path: str) -> RAGStats:
        """Perform a full RAG indexing run over a project."""
        root = self._resolve_path(project_path)
        return self.index_manager.index_project(str(root))

    def refresh_project(self, project_path: str) -> RAGStats:
        """Perform incremental RAG indexing based on Stage 2 content hashes."""
        root = self._resolve_path(project_path)
        return self.index_manager.refresh_project(str(root))

    def search(
        self,
        project_path: str,
        query: str,
        limit: int | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        """Perform hybrid semantic/lexical search over project knowledge."""
        root = self._resolve_path(project_path)
        return self.retriever.search(query, str(root), limit, metadata_filter)

    def build_context(
        self,
        project_path: str,
        query: str,
        limit: int | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> ContextPayload:
        """Search and format structured context payload for downstream LLM/Agents."""
        root = self._resolve_path(project_path)
        results = self.search(str(root), query, limit, metadata_filter)
        return self.context_builder.build_context(query, str(root), results)

    def get_status(self) -> dict[str, Any]:
        return self.get_status_info()

    def get_stats(self, project_path: str) -> dict[str, Any]:
        root = self._resolve_path(project_path)
        chunk_count = self.vector_store.count(str(root))
        return {
            "project_path": str(root),
            "total_chunks": chunk_count,
            "embedding_provider": self.embedder.name,
            "embedding_model": self.config.embedding_model,
        }

    def delete_project(self, project_path: str) -> dict[str, Any]:
        root = self._resolve_path(project_path)
        deleted = self.vector_store.delete_project(str(root))
        return {"project_path": str(root), "deleted_chunks": deleted}

    def get_status_info(self) -> dict[str, Any]:
        return {
            "enabled": self.config.enabled,
            "embedding_provider": self.embedder.name,
            "embedding_model": self.config.embedding_model,
            "provider_available": self.embedder.is_available(),
            "total_vectors_in_store": self.vector_store.count(),
        }

    def _resolve_path(self, project_path: str) -> Path:
        root = Path(project_path).resolve()
        if not root.is_dir():
            raise WorkspaceNotFoundError(project_path)
        return root


knowledge_retrieval_service = KnowledgeRetrievalService()
