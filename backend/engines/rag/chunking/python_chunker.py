"""Code-aware Python AST chunker."""

import hashlib
from datetime import datetime, timezone

from engines.rag.config import RAGConfig
from engines.rag.models import ChunkMetadata, KnowledgeChunk, KnowledgeDocument


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PythonCodeChunker:
    """Chunks Python source files by AST symbol boundaries (functions, classes, methods)."""

    def __init__(self, config: RAGConfig | None = None) -> None:
        self.config = config or RAGConfig()

    def chunk_document(self, doc: KnowledgeDocument, project_path: str) -> list[KnowledgeChunk]:
        lines = doc.content.splitlines(keepends=True)
        total_lines = len(lines)
        if total_lines == 0:
            return []

        chunks: list[KnowledgeChunk] = []

        # Filter out module symbol to avoid duplicating entire file as a single module chunk if symbols exist
        symbol_candidates = [
            s for s in doc.ast_symbols
            if s.get("symbol_type") in {"function", "method", "class", "constant", "variable"}
        ]

        if not symbol_candidates:
            # Fallback to bounded block chunking
            return self._fallback_line_chunks(doc, project_path, lines)

        # Sort symbols by line_start
        symbol_candidates.sort(key=lambda s: s.get("line_start", 1))

        # Track processed line ranges to cover top-level uncaptured module code
        covered_lines = set()
        chunk_idx = 0
        now = _utc_now()

        for sym in symbol_candidates:
            start = max(1, sym.get("line_start", 1))
            end = min(total_lines, sym.get("line_end") or start)
            covered_lines.update(range(start, end + 1))

            chunk_text = "".join(lines[start - 1:end]).strip()
            if not chunk_text:
                continue

            # Sub-chunk if chunk exceeds max_chunk_size
            if len(chunk_text) > self.config.chunk_size:
                sub_chunks = self._split_large_text(chunk_text, self.config.chunk_size, self.config.chunk_overlap)
                for sub_i, sub_text in enumerate(sub_chunks):
                    c_hash = hashlib.sha256(
                        f"{doc.relative_path}:{start}:{sym.get('name')}:{sub_i}:{sub_text}".encode("utf-8")
                    ).hexdigest()
                    chunks.append(
                        KnowledgeChunk(
                            chunk_id=f"{doc.relative_path}#chunk-{chunk_idx}",
                            content=sub_text,
                            metadata=ChunkMetadata(
                                project_path=project_path,
                                file_path=doc.file_path,
                                relative_path=doc.relative_path,
                                language="Python",
                                document_type="python",
                                symbol_name=sym.get("name"),
                                symbol_type=sym.get("symbol_type"),
                                qualified_name=sym.get("qualified_name"),
                                parent_symbol=sym.get("parent_symbol"),
                                line_start=start,
                                line_end=end,
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
            else:
                c_hash = hashlib.sha256(
                    f"{doc.relative_path}:{start}:{sym.get('name')}:{chunk_text}".encode("utf-8")
                ).hexdigest()
                chunks.append(
                    KnowledgeChunk(
                        chunk_id=f"{doc.relative_path}#chunk-{chunk_idx}",
                        content=chunk_text,
                        metadata=ChunkMetadata(
                            project_path=project_path,
                            file_path=doc.file_path,
                            relative_path=doc.relative_path,
                            language="Python",
                            document_type="python",
                            symbol_name=sym.get("name"),
                            symbol_type=sym.get("symbol_type"),
                            qualified_name=sym.get("qualified_name"),
                            parent_symbol=sym.get("parent_symbol"),
                            line_start=start,
                            line_end=end,
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

        # Process uncovered lines (e.g. imports, top-level setup statements)
        uncovered = sorted(set(range(1, total_lines + 1)) - covered_lines)
        if uncovered:
            uncovered_chunks = self._chunk_line_ranges(uncovered, lines, doc, project_path, chunk_idx, now)
            chunks.extend(uncovered_chunks)

        return chunks

    def _fallback_line_chunks(
        self, doc: KnowledgeDocument, project_path: str, lines: list[str]
    ) -> list[KnowledgeChunk]:
        now = _utc_now()
        full_text = "".join(lines)
        text_sub_chunks = self._split_large_text(full_text, self.config.chunk_size, self.config.chunk_overlap)
        chunks: list[KnowledgeChunk] = []

        curr_line = 1
        for i, sub_text in enumerate(text_sub_chunks):
            sub_line_count = len(sub_text.splitlines())
            start_l = curr_line
            end_l = min(len(lines), curr_line + max(1, sub_line_count) - 1)
            curr_line = end_l + 1

            c_hash = hashlib.sha256(
                f"{doc.relative_path}:{i}:{sub_text}".encode("utf-8")
            ).hexdigest()

            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{doc.relative_path}#chunk-{i}",
                    content=sub_text,
                    metadata=ChunkMetadata(
                        project_path=project_path,
                        file_path=doc.file_path,
                        relative_path=doc.relative_path,
                        language="Python",
                        document_type="python",
                        line_start=start_l,
                        line_end=end_l,
                        content_hash=doc.content_hash,
                        chunk_hash=c_hash,
                        chunk_index=i,
                        source_type=doc.source_type,
                        created_at=now,
                        updated_at=now,
                    ),
                )
            )
        return chunks

    def _chunk_line_ranges(
        self,
        uncovered_lines: list[int],
        all_lines: list[str],
        doc: KnowledgeDocument,
        project_path: str,
        start_idx: int,
        now: str,
    ) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        if not uncovered_lines:
            return chunks

        # Group contiguous line ranges
        ranges: list[tuple[int, int]] = []
        range_start = uncovered_lines[0]
        range_end = range_start

        for l in uncovered_lines[1:]:
            if l == range_end + 1:
                range_end = l
            else:
                ranges.append((range_start, range_end))
                range_start = l
                range_end = l
        ranges.append((range_start, range_end))

        curr_idx = start_idx
        for r_start, r_end in ranges:
            text = "".join(all_lines[r_start - 1:r_end]).strip()
            if not text:
                continue
            c_hash = hashlib.sha256(
                f"{doc.relative_path}:{r_start}:{r_end}:{text}".encode("utf-8")
            ).hexdigest()
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{doc.relative_path}#chunk-{curr_idx}",
                    content=text,
                    metadata=ChunkMetadata(
                        project_path=project_path,
                        file_path=doc.file_path,
                        relative_path=doc.relative_path,
                        language="Python",
                        document_type="python",
                        line_start=r_start,
                        line_end=r_end,
                        content_hash=doc.content_hash,
                        chunk_hash=c_hash,
                        chunk_index=curr_idx,
                        source_type=doc.source_type,
                        created_at=now,
                        updated_at=now,
                    ),
                )
            )
            curr_idx += 1
        return chunks

    @staticmethod
    def _split_large_text(text: str, max_size: int, overlap: int) -> list[str]:
        if len(text) <= max_size:
            return [text]
        result: list[str] = []
        start = 0
        text_len = len(text)
        step = max(1, max_size - overlap)

        while start < text_len:
            end = min(text_len, start + max_size)
            chunk = text[start:end]
            if chunk.strip():
                result.append(chunk)
            if end == text_len:
                break
            start += step
        return result
