"""API endpoint integration tests for Stage 2 Project Intelligence."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from main import app
from engines.indexer.service import project_intelligence
from engines.indexer.database.repository import IndexRepository

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_db(tmp_path: Path):
    """Override repository database path to use isolated temp DB during tests."""
    temp_db = tmp_path / "api_test.db"
    project_intelligence.repository = IndexRepository(temp_db)
    yield


def test_api_scan_and_queries(sample_project: Path):
    path_str = str(sample_project)

    # 1. POST /indexer/scan
    res = client.post(f"/indexer/scan?project_path={path_str}")
    assert res.status_code == 200
    data = res.json()
    assert "files" in data
    assert "stats" in data

    # 2. POST /indexer/refresh
    res_refresh = client.post(f"/indexer/refresh?project_path={path_str}")
    assert res_refresh.status_code == 200
    refresh_data = res_refresh.json()
    assert refresh_data["stats"]["unchanged"] > 0

    # 3. GET /indexer/indexes
    res_indexes = client.get("/indexer/indexes")
    assert res_indexes.status_code == 200
    assert len(res_indexes.json()["indexes"]) >= 1

    # 4. GET /indexer/project
    res_proj = client.get(f"/indexer/project?project_path={path_str}")
    assert res_proj.status_code == 200
    assert res_proj.json()["name"] == "sample_project"

    # 5. GET /indexer/files
    res_files = client.get(f"/indexer/files?project_path={path_str}")
    assert res_files.status_code == 200
    assert len(res_files.json()["files"]) > 0

    # 6. GET /indexer/file
    res_file = client.get(f"/indexer/file?project_path={path_str}&path=main.py")
    assert res_file.status_code == 200
    assert res_file.json()["relative_path"] == "main.py"

    # 7. GET /indexer/symbols/search
    res_sym = client.get(f"/indexer/symbols/search?project_path={path_str}&q=create_app")
    assert res_sym.status_code == 200
    assert len(res_sym.json()["symbols"]) >= 1

    # 8. GET /indexer/dependencies
    res_dep = client.get(f"/indexer/dependencies?project_path={path_str}&path=main.py")
    assert res_dep.status_code == 200
    assert "dependencies" in res_dep.json()

    # 9. GET /indexer/dependents
    res_rev = client.get(f"/indexer/dependents?project_path={path_str}&path=sample_pkg/registry.py")
    assert res_rev.status_code == 200
    assert "dependents" in res_rev.json()

    # 10. GET /indexer/graph
    res_graph = client.get(f"/indexer/graph?project_path={path_str}")
    assert res_graph.status_code == 200
    assert "nodes" in res_graph.json()

    # 11. GET /indexer/context
    res_ctx = client.get(f"/indexer/context?project_path={path_str}&focus_path=main.py")
    assert res_ctx.status_code == 200
    assert "project" in res_ctx.json()


def test_api_invalid_workspace():
    res = client.post("/indexer/scan?project_path=/invalid/non_existent_folder_xyz")
    assert res.status_code == 404
