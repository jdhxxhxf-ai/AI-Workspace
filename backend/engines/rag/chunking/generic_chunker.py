"""Generic sliding window text and configuration chunker."""

import hashlib
from datetime import datetime, timezone

from engines.rag.config import RAGConfig
from engines.rag.models import ChunkMetadata, KnowledgeChunk, KnowledgeDocument


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GenericChunker:
    """Sliding-window line-aware text chunker for text, JSON, YAML, and configuration files."""

    def __init__(self, config: RAGConfig | None = None) -> None:
        self.config = config or RAGConfig()

    def chunk_document(self, doc: KnowledgeDocument, project_path: str) -> list[KnowledgeChunk]:
        lines = doc.content.splitlines(keepends=True)
        total_lines = len(lines)
        if total_lines == 0:
            return []

        chunks: list[KnowledgeChunk] = []
        now = _utc_now()
        full_text = doc.content

        if len(full_text) <= self.config.chunk_size:
            c_hash = hashlib.sha256(f"{doc.relative_path}:0:{full_text}".encode("utf-8")).hexdigest()
            return [
                KnowledgeChunk(
                    chunk_id=f"{doc.relative_path}#chunk-0",
                    content=full_text,
                    metadata=ChunkMetadata(
                        project_path=project_path,
                        file_path=doc.file_path,
                        relative_path=doc.relative_path,
                        language=doc.language,
                        document_type=doc.language.lower(),
                        line_start=1,
                        line_end=total_lines,
                        content_hash=doc.content_hash,
                        chunk_hash=c_hash,
                        chunk_index=0,
                        source_type=doc.source_type,
                        created_at=now,
                        updated_at=now,
                    ),
                )
            ]

        # Bounded sliding window
        start = 0
        text_len = len(full_text)
        step = max(1, self.config.chunk_size - self.config.chunk_overlap)
        chunk_idx = 0

        while start < text_len:
            end = min(text_len, start + self.config.chunk_size)
            chunk_text = full_text[start:end]
            if chunk_text.strip():
                line_start = full_text[:start].count("\n") + 1
                line_end = line_start + chunk_text.count("\n")
                c_hash = hashlib.sha256(
                    f"{doc.relative_path}:{chunk_idx}:{chunk_text}".encode("utf-8")
                ).hexdigest()
                chunks.append(
                    KnowledgeChunk(
                        chunk_id=f"{doc.relative_path}#chunk-{chunk_idx}",
                        content=chunk_text,
                        metadata=ChunkMetadata(
                            project_path=project_path,
                            file_path=doc.file_path,
                            relative_path=doc.relative_path,
                            language=doc.language,
                            document_type=doc.language.lower(),
                            line_start=line_start,
                            line_end=line_end,
                            content_hash=doc.content_hash,
                            chunk_hash=c_hash,
                            chunk_index=chunk_idx,
                            source_type=doc.source_type,
                            created_at=now,
                            updated_at=now,
                        ),
                    )
                )
                chunk_idx += 1
            if end == text_len:
                break
            start += step

        return chunks
