"""Unit tests for full and incremental RAG indexing."""

from pathlib import Path

from engines.rag.config import RAGConfig
from engines.rag.embeddings.mock_provider import MockEmbeddingProvider
from engines.rag.indexing.manager import RAGIndexManager
from engines.rag.storage.vector_store import SQLiteVectorStore


def test_rag_full_and_incremental_indexing(sample_project: Path, tmp_path: Path):
    db_path = tmp_path / "rag_incremental.db"
    store = SQLiteVectorStore(db_path)
    embedder = MockEmbeddingProvider()
    config = RAGConfig(vector_db_path=db_path)

    manager = RAGIndexManager(embedder=embedder, vector_store=store, config=config)
    project_str = str(sample_project)

    # 1. Full Indexing
    stats1 = manager.index_project(project_str)
    assert stats1.indexed_documents > 0
    assert stats1.total_chunks > 0
    initial_chunks = stats1.total_chunks

    # 2. Immediate Refresh (all unchanged)
    stats2 = manager.refresh_project(project_str)
    assert stats2.unchanged_files == stats1.scanned_files
    assert stats2.changed_files == 0
    assert stats2.new_files == 0

    # 3. Add new file
    new_doc = sample_project / "extra_doc.md"
    new_doc.write_text("# Extra Knowledge\nThis is an added markdown document.\n", encoding="utf-8")

    stats3 = manager.refresh_project(project_str)
    assert stats3.new_files == 1
    assert stats3.total_chunks > 0

    # 4. Modify existing file
    main_py = sample_project / "main.py"
    main_py.write_text("def updated_create_app(): return 'v2'\n", encoding="utf-8")

    stats4 = manager.refresh_project(project_str)
    assert stats4.changed_files == 1

    # 5. Delete file
    new_doc.unlink()

    stats5 = manager.refresh_project(project_str)
    assert stats5.deleted_files == 1
