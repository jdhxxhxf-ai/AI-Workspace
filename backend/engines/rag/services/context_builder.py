"""Structured Knowledge Context Builder for future AI Agent stages."""

from engines.rag.models import ContextPayload, RetrievalResult


class KnowledgeContextBuilder:
    """Transforms retrieved RAG results into formatted structured context payloads."""

    def build_context(self, query: str, project_path: str, results: list[RetrievalResult]) -> ContextPayload:
        if not results:
            return ContextPayload(
                query=query,
                project_path=project_path,
                total_chunks_retrieved=0,
                context_text="No relevant knowledge chunks found.",
                sources=[],
            )

        context_blocks: list[str] = []
        sources: list[dict] = []

        for i, res in enumerate(results, start=1):
            source_info = {
                "rank": i,
                "file_path": res.file_path,
                "relative_path": res.relative_path,
                "symbol_name": res.symbol_name,
                "symbol_type": res.symbol_type,
                "qualified_name": res.qualified_name,
                "line_start": res.line_start,
                "line_end": res.line_end,
                "score": res.score,
                "vector_score": res.vector_score,
                "lexical_score": res.lexical_score,
            }
            sources.append(source_info)

            header = f"### [Source {i}] {res.relative_path}"
            if res.symbol_name:
                header += f" ({res.symbol_type}: {res.symbol_name})"
            header += f" (Lines {res.line_start}-{res.line_end or res.line_start}, Score: {res.score:.3f})"

            block = f"{header}\n```\n{res.content}\n```"
            context_blocks.append(block)

        full_context = "\n\n".join(context_blocks)

        return ContextPayload(
            query=query,
            project_path=project_path,
            total_chunks_retrieved=len(results),
            context_text=full_context,
            sources=sources,
        )
