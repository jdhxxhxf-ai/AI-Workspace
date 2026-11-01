"""Shared fixtures for Stage 2 indexer tests."""

import textwrap
from pathlib import Path

import pytest

from engines.indexer.database.repository import IndexRepository
from engines.indexer.service import ProjectIntelligenceService


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    return tmp_path / "test_intelligence.db"


@pytest.fixture
def repository(temp_db: Path) -> IndexRepository:
    return IndexRepository(temp_db)


@pytest.fixture
def service(repository: IndexRepository) -> ProjectIntelligenceService:
    return ProjectIntelligenceService(repository)


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    root = tmp_path / "sample_project"
    pkg = root / "sample_pkg"
    pkg.mkdir(parents=True)

    (root / "requirements.txt").write_text("fastapi>=0.110.0\n", encoding="utf-8")
    (root / "main.py").write_text(
        textwrap.dedent(
            """
            from sample_pkg.registry import ToolRegistry

            def create_app():
                return ToolRegistry()
            """
        ).strip(),
        encoding="utf-8",
    )
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "registry.py").write_text(
        textwrap.dedent(
            """
            import asyncio
            from sample_pkg.base import BaseTool

            class ToolRegistry(BaseTool):
                \"\"\"Registry for tools.\"\"\"

                VERSION = "1.0"

                async def execute(self):
                    return True
            """
        ).strip(),
        encoding="utf-8",
    )
    (pkg / "base.py").write_text(
        textwrap.dedent(
            """
            class BaseTool:
                pass
            """
        ).strip(),
        encoding="utf-8",
    )
    (root / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (root / "readme.md").write_text("# Sample\n", encoding="utf-8")
    (root / "node_modules").mkdir()
    (root / "node_modules" / "ignored.js").write_text("console.log('skip');\n", encoding="utf-8")
    return root
