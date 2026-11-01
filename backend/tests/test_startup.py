"""Startup validation tests."""

import importlib


def test_main_import():
    """Verify main module imports without error."""
    module = importlib.import_module("main")
    assert module.app is not None


def test_app_routes():
    """Verify expected routes are registered."""
    from main import app

    paths = list(app.openapi()["paths"].keys())
    assert "/" in paths
    assert "/health" in paths
    assert "/tools/execute" in paths


def test_tool_registry():
    """Verify all default tools are registered."""
    from engines.tools.registry import registry

    tools = {t.name for t in registry.list_tools()}
    assert "file" in tools
    assert "terminal" in tools
    assert "write" in tools
