"""Tests for ProjectIntelligenceService and incremental indexing."""

from pathlib import Path
import pytest

from engines.indexer.database.repository import IndexRepository
from engines.indexer.service import ProjectIntelligenceService
from engines.indexer.context import ProjectContextBuilder
from shared.exceptions import WorkspaceNotFoundError, IndexerError


def test_service_index_project(sample_project: Path, temp_db: Path):
    repo = IndexRepository(temp_db)
    service = ProjectIntelligenceService(repo)

    result = service.index_project(str(sample_project))
    assert "files" in result
    assert "stats" in result
    assert result["stats"]["indexed"] > 0
    assert result["stats"]["new"] > 0


def test_service_incremental_indexing(sample_project: Path, temp_db: Path):
    repo = IndexRepository(temp_db)
    service = ProjectIntelligenceService(repo)

    # Initial index
    initial_res = service.index_project(str(sample_project))
    initial_indexed = initial_res["stats"]["indexed"]

    # 1. Immediate refresh without changes -> all unchanged
    refresh1 = service.refresh_project(str(sample_project))
    assert refresh1["stats"]["unchanged"] == initial_indexed
    assert refresh1["stats"]["changed"] == 0
    assert refresh1["stats"]["new"] == 0
    assert refresh1["stats"]["deleted"] == 0

    # 2. Add a new file
    new_file = sample_project / "new_module.py"
    new_file.write_text("def new_func(): pass\n", encoding="utf-8")

    refresh2 = service.refresh_project(str(sample_project))
    assert refresh2["stats"]["new"] == 1

    # 3. Modify an existing file
    main_file = sample_project / "main.py"
    main_file.write_text("def create_app(): return 42\n", encoding="utf-8")

    refresh3 = service.refresh_project(str(sample_project))
    assert refresh3["stats"]["changed"] == 1

    # 4. Delete a file
    new_file.unlink()

    refresh4 = service.refresh_project(str(sample_project))
    assert refresh4["stats"]["deleted"] == 1


def test_service_queries(sample_project: Path, temp_db: Path):
    repo = IndexRepository(temp_db)
    service = ProjectIntelligenceService(repo)
    service.index_project(str(sample_project))

    summary = service.get_project_summary(str(sample_project))
    assert summary["name"] == "sample_project"
    assert summary["file_count"] > 0

    file_list = service.list_files(str(sample_project))
    assert len(file_list["files"]) > 0

    file_intel = service.get_file_intelligence(str(sample_project), "main.py")
    assert file_intel["relative_path"] == "main.py"
    assert len(file_intel["symbols"]) > 0

    symbol_res = service.search_symbols(str(sample_project), "create_app")
    assert len(symbol_res["symbols"]) >= 1

    graph = service.get_graph(str(sample_project))
    assert "nodes" in graph
    assert "edges" in graph


def test_service_context_builder(sample_project: Path, temp_db: Path):
    repo = IndexRepository(temp_db)
    service = ProjectIntelligenceService(repo)
    service.index_project(str(sample_project))

    builder = ProjectContextBuilder(repo)
    context = builder.build(str(sample_project), focus_path="main.py")

    assert "project" in context
    assert "counts" in context
    assert "focus_file" in context
    assert context["focus_file"]["relative_path"] == "main.py"


def test_service_non_existent_workspace(temp_db: Path):
    repo = IndexRepository(temp_db)
    service = ProjectIntelligenceService(repo)
    with pytest.raises(WorkspaceNotFoundError):
        service.index_project("/non/existent/path/for/sure/12345")
