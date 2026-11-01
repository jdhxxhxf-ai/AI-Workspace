"""Tests for persistent SQLite repository and database schema."""

from pathlib import Path
from engines.indexer.database.repository import IndexRepository
from engines.indexer.database.schema import initialize_schema
from engines.indexer.models import DependencyEdge, IndexStats, PythonFileInfo, SymbolInfo, ImportInfo


def test_db_schema_initialization(tmp_path: Path):
    db_path = tmp_path / "test_schema.db"
    initialize_schema(db_path)
    assert db_path.is_file()


def test_repository_index_and_get_summary(tmp_path: Path):
    db_path = tmp_path / "test_repo.db"
    repo = IndexRepository(db_path)
    project_path = str(tmp_path / "sample")

    parsed_file = PythonFileInfo(
        path=str(tmp_path / "sample" / "main.py"),
        relative_path="main.py",
        module_path="main",
        symbols=[
            SymbolInfo(
                name="main",
                qualified_name="main",
                symbol_type="module",
                line_start=1,
            ),
            SymbolInfo(
                name="run",
                qualified_name="main.run",
                symbol_type="function",
                line_start=3,
            ),
        ],
        imports=[ImportInfo(module="os", line=1)],
    )

    stats = repo.index_project(
        project_path=project_path,
        parsed_files=[parsed_file],
        dependencies=[],
        discovery={"name": "sample", "languages": {"Python": 1}, "entry_points": ["main.py"]},
    )

    assert stats.indexed == 1
    summary = repo.get_summary(project_path)
    assert summary.name == "sample"
    assert summary.file_count == 1
    assert summary.symbol_count == 2
    assert summary.function_count == 1


def test_repository_search_symbols_and_dependencies(tmp_path: Path):
    db_path = tmp_path / "test_search.db"
    repo = IndexRepository(db_path)
    project_path = str(tmp_path / "sample")

    file1 = PythonFileInfo(
        path=str(tmp_path / "sample" / "app.py"),
        relative_path="app.py",
        module_path="app",
        symbols=[
            SymbolInfo(name="AppRegistry", qualified_name="app.AppRegistry", symbol_type="class", line_start=5),
        ],
    )
    file2 = PythonFileInfo(
        path=str(tmp_path / "sample" / "utils.py"),
        relative_path="utils.py",
        module_path="utils",
        symbols=[
            SymbolInfo(name="helper", qualified_name="utils.helper", symbol_type="function", line_start=2),
        ],
    )
    dep = DependencyEdge(
        source="app.py",
        target="utils.py",
        relationship="IMPORTS",
        import_type="direct",
        line=1,
        resolved=True,
    )

    repo.index_project(project_path, [file1, file2], [dep])

    symbols = repo.search_symbols(project_path, "AppReg")
    assert len(symbols) == 1
    assert symbols[0]["name"] == "AppRegistry"

    deps = repo.get_dependencies(project_path, "app.py")
    assert len(deps) == 1
    assert deps[0]["target_path"] == "utils.py"

    dependents = repo.get_dependents(project_path, "utils.py")
    assert len(dependents) == 1
    assert dependents[0]["source_path"] == "app.py"

    graph = repo.get_graph(project_path)
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1


def test_repository_foreign_key_cascade(tmp_path: Path):
    db_path = tmp_path / "test_cascade.db"
    repo = IndexRepository(db_path)
    project_path = str(tmp_path / "sample")

    file1 = PythonFileInfo(
        path=str(tmp_path / "sample" / "main.py"),
        relative_path="main.py",
        module_path="main",
        symbols=[SymbolInfo(name="main", qualified_name="main", symbol_type="module", line_start=1)],
    )

    repo.index_project(project_path, [file1], [])

    # Delete project
    deleted = repo.delete(project_path)
    assert deleted is True

    assert repo.list_all() == []
