"""Unit tests for HybridRetriever, ranking, and KnowledgeContextBuilder."""

from pathlib import Path

from engines.rag.embeddings.mock_provider import MockEmbeddingProvider
from engines.rag.models import ChunkMetadata, KnowledgeChunk
from engines.rag.retrieval.hybrid_retriever import HybridRetriever
from engines.rag.services.context_builder import KnowledgeContextBuilder
from engines.rag.storage.vector_store import SQLiteVectorStore


def test_hybrid_retriever_and_context_builder(tmp_path: Path):
    db_path = tmp_path / "test_retrieval.db"
    store = SQLiteVectorStore(db_path)
    embedder = MockEmbeddingProvider()
    proj = str(tmp_path / "proj")

    # Generate vectors via mock embedder
    v1 = embedder.embed_text("def execute_terminal_command(): pass")
    v2 = embedder.embed_text("def calculate_total(): return 100")

    chunk1 = KnowledgeChunk(
        chunk_id="terminal.py#chunk-0",
        content="def execute_terminal_command(): pass",
        vector=v1,
        metadata=ChunkMetadata(
            project_path=proj,
            file_path=f"{proj}/terminal.py",
            relative_path="terminal.py",
            language="Python",
            document_type="python",
            symbol_name="execute_terminal_command",
            symbol_type="function",
            qualified_name="terminal.execute_terminal_command",
            line_start=1,
            line_end=2,
            chunk_hash="ch1",
        ),
    )

    chunk2 = KnowledgeChunk(
        chunk_id="math.py#chunk-0",
        content="def calculate_total(): return 100",
        vector=v2,
        metadata=ChunkMetadata(
            project_path=proj,
            file_path=f"{proj}/math.py",
            relative_path="math.py",
            language="Python",
            document_type="python",
            symbol_name="calculate_total",
            symbol_type="function",
            qualified_name="math.calculate_total",
            line_start=1,
            line_end=2,
            chunk_hash="ch2",
        ),
    )

    store.upsert_chunks([chunk1, chunk2])

    retriever = HybridRetriever(embedder, store)
    results = retriever.search(query="execute terminal command", project_path=proj, limit=5)

    assert len(results) >= 1
    assert results[0].symbol_name == "execute_terminal_command"
    assert results[0].score > 0.0

    # Build Context
    builder = KnowledgeContextBuilder()
    context = builder.build_context("execute terminal command", proj, results)

    assert context.total_chunks_retrieved == len(results)
    assert "execute_terminal_command" in context.context_text
    assert len(context.sources) == len(results)
