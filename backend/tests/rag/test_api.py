"""Integration tests for RAG API endpoints."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from main import app
from engines.rag.services.retrieval_service import knowledge_retrieval_service
from engines.rag.embeddings.mock_provider import MockEmbeddingProvider
from engines.rag.storage.vector_store import SQLiteVectorStore

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_rag_service(tmp_path: Path):
    """Override retrieval service dependencies to use isolated temp DB and Mock embedder."""
    temp_db = tmp_path / "rag_api_test.db"
    knowledge_retrieval_service._embedder = MockEmbeddingProvider()
    knowledge_retrieval_service._vector_store = SQLiteVectorStore(temp_db)
    yield


def test_rag_api_full_flow(sample_project: Path):
    proj_str = str(sample_project)

    # 1. GET /rag/status
    res_status = client.get("/rag/status")
    assert res_status.status_code == 200
    assert "enabled" in res_status.json()

    # 2. POST /rag/index
    res_index = client.post("/rag/index", json={"project_path": proj_str})
    if res_index.status_code != 200:
        print("RES INDEX FAIL:", res_index.status_code, res_index.json())
    assert res_index.status_code == 200
    assert res_index.json()["stats"]["indexed_documents"] > 0

    # 3. POST /rag/refresh
    res_refresh = client.post("/rag/refresh", json={"project_path": proj_str})
    assert res_refresh.status_code == 200
    assert res_refresh.json()["stats"]["unchanged_files"] > 0

    # 4. GET /rag/stats
    res_stats = client.get(f"/rag/stats?project_path={proj_str}")
    assert res_stats.status_code == 200
    assert res_stats.json()["total_chunks"] > 0

    # 5. POST /rag/search
    res_search = client.post(
        "/rag/search",
        json={"project_path": proj_str, "query": "ToolRegistry execute", "limit": 5},
    )
    assert res_search.status_code == 200
    assert res_search.json()["total_results"] > 0

    # 6. POST /rag/context
    res_ctx = client.post(
        "/rag/context",
        json={"project_path": proj_str, "query": "ToolRegistry", "limit": 3},
    )
    assert res_ctx.status_code == 200
    assert res_ctx.json()["total_chunks_retrieved"] > 0
    assert "ToolRegistry" in res_ctx.json()["context_text"]

    # 7. DELETE /rag/project
    res_del = client.delete(f"/rag/project?project_path={proj_str}")
    assert res_del.status_code == 200
    assert res_del.json()["deleted_chunks"] > 0
