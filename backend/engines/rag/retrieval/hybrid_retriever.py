"""Hybrid semantic and lexical retrieval engine with deterministic ranking."""

import re
from typing import Any

from engines.rag.config import RAGConfig
from engines.rag.embeddings.provider import EmbeddingProvider
from engines.rag.models import RetrievalResult
from engines.rag.storage.vector_store import VectorStore


class HybridRetriever:
    """Combines vector similarity search with lexical symbol and path matching."""

    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
        config: RAGConfig | None = None,
    ) -> None:
        self.embedder = embedder
        self.vector_store = vector_store
        self.config = config or RAGConfig()

    def search(
        self,
        query: str,
        project_path: str,
        limit: int | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        top_k = limit or self.config.top_k
        query_text = query.strip()
        if not query_text:
            return []

        # 1. Generate query vector
        query_vector = self.embedder.embed_text(query_text)

        # 2. Query vector store for candidate chunks (retrieve candidate pool)
        candidate_k = max(top_k * 3, 30)
        candidates = self.vector_store.similarity_search(
            query_vector=query_vector,
            project_path=project_path,
            top_k=candidate_k,
            metadata_filter=metadata_filter,
        )

        # 3. Compute hybrid scores (vector + lexical + symbol match)
        results: list[RetrievalResult] = []
        tokens = [t.lower() for t in re.findall(r"\w+", query_text) if len(t) > 1]

        for chunk, v_score in candidates:
            m = chunk.metadata
            l_score = self._compute_lexical_score(query_text, tokens, chunk.content, m)
            combined_score = 0.6 * max(0.0, v_score) + 0.4 * l_score

            results.append(
                RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    score=round(combined_score, 4),
                    content=chunk.content,
                    file_path=m.file_path,
                    relative_path=m.relative_path,
                    language=m.language,
                    source_type=m.source_type,
                    symbol_name=m.symbol_name,
                    symbol_type=m.symbol_type,
                    qualified_name=m.qualified_name,
                    line_start=m.line_start,
                    line_end=m.line_end,
                    vector_score=round(v_score, 4),
                    lexical_score=round(l_score, 4),
                )
            )

        # 4. Sort by combined score descending and deduplicate
        results.sort(key=lambda r: r.score, reverse=True)
        deduped = self._deduplicate(results)

        return deduped[:top_k]

    def _compute_lexical_score(self, query: str, tokens: list[str], content: str, m: Any) -> float:
        score = 0.0
        content_lower = content.lower()
        query_lower = query.lower()

        # Exact symbol or qualified name match
        if m.symbol_name and m.symbol_name.lower() in query_lower:
            score += 0.5
        if m.qualified_name and m.qualified_name.lower() in query_lower:
            score += 0.5

        # Path match
        if m.relative_path and any(t in m.relative_path.lower() for t in tokens):
            score += 0.3

        # Token match frequency in content
        if tokens:
            matches = sum(1 for t in tokens if t in content_lower)
            score += min(0.5, (matches / len(tokens)) * 0.5)

        return min(1.0, score)

    @staticmethod
    def _deduplicate(results: list[RetrievalResult]) -> list[RetrievalResult]:
        seen_keys = set()
        deduped: list[RetrievalResult] = []

        for item in results:
            key = (item.relative_path, item.line_start, item.line_end)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped.append(item)

        return deduped
