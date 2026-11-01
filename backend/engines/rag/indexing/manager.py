"""Full and incremental RAG index manager."""

import time
from pathlib import Path

from engines.indexer.database.repository import IndexRepository
from engines.indexer.scanner import ProjectScanner
from engines.rag.chunking.generic_chunker import GenericChunker
from engines.rag.chunking.markdown_chunker import MarkdownChunker
from engines.rag.chunking.python_chunker import PythonCodeChunker
from engines.rag.config import RAGConfig
from engines.rag.domain.extractor import DocumentExtractor
from engines.rag.embeddings.provider import EmbeddingProvider
from engines.rag.models import KnowledgeChunk, KnowledgeDocument, RAGStats
from engines.rag.storage.vector_store import VectorStore
from shared.exceptions import WorkspaceNotFoundError
from shared.logger import get_logger

logger = get_logger("rag.indexing")


class RAGIndexManager:
    """Manages document extraction, code-aware chunking, batch embeddings, and vector storage."""

    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
        repository: IndexRepository | None = None,
        config: RAGConfig | None = None,
    ) -> None:
        self.embedder = embedder
        self.vector_store = vector_store
        self.repository = repository
        self.config = config or RAGConfig()
        self.extractor = DocumentExtractor(repository=repository)
        self.python_chunker = PythonCodeChunker(self.config)
        self.markdown_chunker = MarkdownChunker(self.config)
        self.generic_chunker = GenericChunker(self.config)

    def index_project(self, project_path: str) -> RAGStats:
        """Perform a full RAG indexing run over a project workspace."""
        started = time.perf_counter()
        root = self._resolve_path(project_path)

        scanner = ProjectScanner(str(root))
        scanned_files = scanner.scan_files()

        # Delete existing vector storage records for full reindex
        self.vector_store.delete_project(str(root))

        all_chunks: list[KnowledgeChunk] = []
        indexed_docs = 0

        for file_info in scanned_files:
            if not file_info.indexable:
                continue
            doc = self.extractor.extract_document(str(root), file_info)
            if doc is None:
                continue
            chunks = self._chunk_document(doc, str(root))
            if chunks:
                all_chunks.extend(chunks)
                indexed_docs += 1

        total_embedded = self._embed_and_store_batch(all_chunks)
        self.vector_store.save_file_hashes(
            str(root), {f.relative_path: f.content_hash for f in scanned_files if f.indexable and f.content_hash}
        )

        duration_ms = int((time.perf_counter() - started) * 1000)
        stats = RAGStats(
            scanned_files=len(scanned_files),
            indexed_documents=indexed_docs,
            total_chunks=total_embedded,
            new_files=indexed_docs,
            duration_ms=duration_ms,
            embedding_provider=self.embedder.name,
            embedding_model=self.config.embedding_model,
        )
        logger.info("Indexed RAG project %s: %d chunks across %d docs in %dms", str(root), total_embedded, indexed_docs, duration_ms)
        return stats

    def refresh_project(self, project_path: str) -> RAGStats:
        """Perform incremental RAG indexing based on Stage 2 content hashes."""
        started = time.perf_counter()
        root = self._resolve_path(project_path)

        scanner = ProjectScanner(str(root))
        scanned_files = scanner.scan_files()

        existing_hashes = self.vector_store.get_file_hashes(str(root))
        scanned_map = {f.relative_path: f for f in scanned_files if f.indexable}
        scanned_paths = set(scanned_map.keys())

        deleted_paths = set(existing_hashes.keys()) - scanned_paths
        deleted_count = 0
        for del_path in deleted_paths:
            deleted_count += self.vector_store.delete_file_chunks(str(root), del_path)

        unchanged_count = 0
        changed_count = 0
        new_count = 0
        indexed_docs = 0
        chunks_to_embed: list[KnowledgeChunk] = []

        for rel_path, file_info in scanned_map.items():
            prev_hash = existing_hashes.get(rel_path)
            curr_hash = file_info.content_hash

            if prev_hash is not None and prev_hash == curr_hash:
                unchanged_count += 1
                continue

            if prev_hash is None:
                new_count += 1
            else:
                changed_count += 1
                self.vector_store.delete_file_chunks(str(root), rel_path)

            doc = self.extractor.extract_document(str(root), file_info)
            if doc is None:
                continue

            chunks = self._chunk_document(doc, str(root))
            if chunks:
                chunks_to_embed.extend(chunks)
                indexed_docs += 1

        total_embedded = self._embed_and_store_batch(chunks_to_embed)
        self.vector_store.save_file_hashes(
            str(root), {f.relative_path: f.content_hash for f in scanned_files if f.indexable and f.content_hash}
        )

        duration_ms = int((time.perf_counter() - started) * 1000)
        stats = RAGStats(
            scanned_files=len(scanned_files),
            indexed_documents=indexed_docs,
            total_chunks=total_embedded,
            unchanged_files=unchanged_count,
            changed_files=changed_count,
            new_files=new_count,
            deleted_files=len(deleted_paths),
            duration_ms=duration_ms,
            embedding_provider=self.embedder.name,
            embedding_model=self.config.embedding_model,
        )
        logger.info(
            "Refreshed RAG project %s: %d new/updated chunks, %d unchanged in %dms",
            str(root), total_embedded, unchanged_count, duration_ms
        )
        return stats

    def _chunk_document(self, doc: KnowledgeDocument, project_path: str) -> list[KnowledgeChunk]:
        if doc.language == "Python":
            return self.python_chunker.chunk_document(doc, project_path)
        if doc.language == "Markdown":
            return self.markdown_chunker.chunk_document(doc, project_path)
        return self.generic_chunker.chunk_document(doc, project_path)

    def _embed_and_store_batch(self, chunks: list[KnowledgeChunk]) -> int:
        if not chunks:
            return 0

        batch_size = self.config.batch_size
        total_chunks = len(chunks)

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c.content for c in batch]
            vectors = self.embedder.embed_documents(texts)
            for chunk, vector in zip(batch, vectors):
                chunk.vector = vector
            self.vector_store.upsert_chunks(batch)

        return total_chunks

    @staticmethod
    def _resolve_path(project_path: str) -> Path:
        root = Path(project_path).resolve()
        if not root.is_dir():
            raise WorkspaceNotFoundError(project_path)
        return root
