"""Unit tests for SQLite persistent vector storage and project isolation."""

from pathlib import Path

from engines.rag.models import ChunkMetadata, KnowledgeChunk
from engines.rag.storage.vector_store import SQLiteVectorStore


def test_sqlite_vector_store_crud(tmp_path: Path):
    db_path = tmp_path / "test_vec.db"
    store = SQLiteVectorStore(db_path)
    proj1 = "/path/project1"
    proj2 = "/path/project2"

    chunk1 = KnowledgeChunk(
        chunk_id="file1.py#chunk-0",
        content="def function_a(): return 1",
        vector=[0.1, 0.2, 0.3, 0.4],
        metadata=ChunkMetadata(
            project_path=proj1,
            file_path="/path/project1/file1.py",
            relative_path="file1.py",
            language="Python",
            document_type="python",
            symbol_name="function_a",
            symbol_type="function",
            line_start=1,
            line_end=2,
            content_hash="ch1",
            chunk_hash="ck1",
            chunk_index=0,
            created_at="2026-08-10T00:00:00Z",
            updated_at="2026-08-10T00:00:00Z",
        ),
    )

    chunk2 = KnowledgeChunk(
        chunk_id="file2.py#chunk-0",
        content="class ClassB: pass",
        vector=[0.8, 0.7, 0.6, 0.5],
        metadata=ChunkMetadata(
            project_path=proj2,
            file_path="/path/project2/file2.py",
            relative_path="file2.py",
            language="Python",
            document_type="python",
            symbol_name="ClassB",
            symbol_type="class",
            line_start=1,
            line_end=2,
            content_hash="ch2",
            chunk_hash="ck2",
            chunk_index=0,
            created_at="2026-08-10T00:00:00Z",
            updated_at="2026-08-10T00:00:00Z",
        ),
    )

    # 1. Upsert
    inserted = store.upsert_chunks([chunk1, chunk2])
    assert inserted == 2
    assert store.count() == 2
    assert store.count(proj1) == 1
    assert store.count(proj2) == 1

    # 2. Similarity Search & Project Isolation
    results = store.similarity_search([0.1, 0.2, 0.3, 0.4], project_path=proj1)
    assert len(results) == 1
    assert results[0][0].metadata.symbol_name == "function_a"

    # Search project2 should NOT return chunk1
    results_p2 = store.similarity_search([0.1, 0.2, 0.3, 0.4], project_path=proj2)
    assert len(results_p2) == 1
    assert results_p2[0][0].metadata.symbol_name == "ClassB"

    # 3. Delete file chunks
    deleted_cnt = store.delete_file_chunks(proj1, "file1.py")
    assert deleted_cnt == 1
    assert store.count(proj1) == 0
    assert store.count(proj2) == 1

    # 4. Delete project
    del_proj = store.delete_project(proj2)
    assert del_proj == 1
    assert store.count() == 0
