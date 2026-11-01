"""Structure-aware Markdown document chunker."""

import hashlib
import re
from datetime import datetime, timezone

from engines.rag.config import RAGConfig
from engines.rag.models import ChunkMetadata, KnowledgeChunk, KnowledgeDocument


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MarkdownChunker:
    """Chunks Markdown documentation files by section headings (#, ##, ###)."""

    HEADING_REGEX = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)

    def __init__(self, config: RAGConfig | None = None) -> None:
        self.config = config or RAGConfig()

    def chunk_document(self, doc: KnowledgeDocument, project_path: str) -> list[KnowledgeChunk]:
        lines = doc.content.splitlines(keepends=True)
        total_lines = len(lines)
        if total_lines == 0:
            return []

        # Find heading lines and their line numbers
        heading_matches = [
            (match.start(), match.group(1), match.group(2).strip(), doc.content[:match.start()].count("\n") + 1)
            for match in self.HEADING_REGEX.finditer(doc.content)
        ]

        if not heading_matches:
            return self._generic_text_chunk(doc, project_path, lines)

        sections: list[dict] = []
        for i, (_, level_hashes, title, line_no) in enumerate(heading_matches):
            next_line_no = heading_matches[i + 1][3] - 1 if i + 1 < len(heading_matches) else total_lines
            sections.append({
                "heading_level": len(level_hashes),
                "title": title,
                "line_start": line_no,
                "line_end": next_line_no,
            })

        # Include preamble before first heading if any
        first_heading_line = heading_matches[0][3]
        chunks: list[KnowledgeChunk] = []
        now = _utc_now()
        chunk_idx = 0

        if first_heading_line > 1:
            preamble_lines = lines[:first_heading_line - 1]
            preamble_text = "".join(preamble_lines).strip()
            if preamble_text:
                c_hash = hashlib.sha256(f"{doc.relative_path}:preamble:{preamble_text}".encode("utf-8")).hexdigest()
                chunks.append(
                    KnowledgeChunk(
                        chunk_id=f"{doc.relative_path}#chunk-{chunk_idx}",
                        content=preamble_text,
                        metadata=ChunkMetadata(
                            project_path=project_path,
                            file_path=doc.file_path,
                            relative_path=doc.relative_path,
                            language="Markdown",
                            document_type="markdown",
                            symbol_name="Preamble",
                            symbol_type="section",
                            line_start=1,
                            line_end=first_heading_line - 1,
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

        for sec in sections:
            start = sec["line_start"]
            end = sec["line_end"]
            section_text = "".join(lines[start - 1:end]).strip()
            if not section_text:
                continue

            if len(section_text) > self.config.chunk_size:
                sub_chunks = self._split_text(section_text, self.config.chunk_size, self.config.chunk_overlap)
                for sub_i, sub_t in enumerate(sub_chunks):
                    c_hash = hashlib.sha256(
                        f"{doc.relative_path}:{start}:{sec['title']}:{sub_i}:{sub_t}".encode("utf-8")
                    ).hexdigest()
                    chunks.append(
                        KnowledgeChunk(
                            chunk_id=f"{doc.relative_path}#chunk-{chunk_idx}",
                            content=sub_t,
                            metadata=ChunkMetadata(
                                project_path=project_path,
                                file_path=doc.file_path,
                                relative_path=doc.relative_path,
                                language="Markdown",
                                document_type="markdown",
                                symbol_name=sec["title"],
                                symbol_type="section",
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
                    f"{doc.relative_path}:{start}:{sec['title']}:{section_text}".encode("utf-8")
                ).hexdigest()
                chunks.append(
                    KnowledgeChunk(
                        chunk_id=f"{doc.relative_path}#chunk-{chunk_idx}",
                        content=section_text,
                        metadata=ChunkMetadata(
                            project_path=project_path,
                            file_path=doc.file_path,
                            relative_path=doc.relative_path,
                            language="Markdown",
                            document_type="markdown",
                            symbol_name=sec["title"],
                            symbol_type="section",
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

        return chunks

    def _generic_text_chunk(
        self, doc: KnowledgeDocument, project_path: str, lines: list[str]
    ) -> list[KnowledgeChunk]:
        now = _utc_now()
        full_text = "".join(lines)
        sub_chunks = self._split_text(full_text, self.config.chunk_size, self.config.chunk_overlap)
        chunks: list[KnowledgeChunk] = []

        curr_l = 1
        for i, sub_t in enumerate(sub_chunks):
            line_cnt = len(sub_t.splitlines())
            start_l = curr_l
            end_l = min(len(lines), curr_l + max(1, line_cnt) - 1)
            curr_l = end_l + 1
            c_hash = hashlib.sha256(f"{doc.relative_path}:{i}:{sub_t}".encode("utf-8")).hexdigest()

            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{doc.relative_path}#chunk-{i}",
                    content=sub_t,
                    metadata=ChunkMetadata(
                        project_path=project_path,
                        file_path=doc.file_path,
                        relative_path=doc.relative_path,
                        language="Markdown",
                        document_type="markdown",
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

    @staticmethod
    def _split_text(text: str, max_size: int, overlap: int) -> list[str]:
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
