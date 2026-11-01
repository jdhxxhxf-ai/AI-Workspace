"""Application startup validation."""

from shared.logger import get_logger

logger = get_logger("core.startup")


def validate_imports() -> list[str]:
    """Validate that all core modules can be imported."""
    errors: list[str] = []
    modules = [
        "config.settings",
        "shared.logger",
        "engines.tools.registry",
        "engines.workspace.manager",
        "engines.indexer.parser",
        "engines.rag.services.retrieval_service",
        "engines.llm.pipeline",
        "engines.memory.conversation",
        "engines.agent.planner",
        "engines.agent.executor",
        "api.router",
    ]

    for module in modules:
        try:
            __import__(module)
            logger.info("Import OK: %s", module)
        except ImportError as e:
            errors.append(f"{module}: {e}")
            logger.error("Import FAILED: %s — %s", module, e)

    return errors


def validate_tools() -> list[str]:
    """Validate tool registration."""
    errors: list[str] = []

    try:
        from engines.tools.registry import registry

        tools = registry.list_tools()
        if len(tools) < 3:
            errors.append(f"Expected at least 3 tools, found {len(tools)}")

        expected = {"file", "terminal", "write"}
        registered = {t.name for t in tools}
        missing = expected - registered
        if missing:
            errors.append(f"Missing tools: {missing}")

        logger.info("Tools validated: %s", registered)
    except Exception as e:
        errors.append(f"Tool validation failed: {e}")

    return errors


def _collect_route_paths(app) -> list[str]:
    """Collect registered route paths from the OpenAPI schema."""
    return list(app.openapi().get("paths", {}).keys())


def validate_routes(app) -> list[str]:
    """Validate that expected routes are registered."""
    errors: list[str] = []
    route_paths = _collect_route_paths(app)

    expected = ["/", "/health", "/workspace/scan", "/files/read",
                "/tools/execute", "/planner/plan", "/indexer/scan", "/rag/status"]

    for path in expected:
        if path not in route_paths:
            errors.append(f"Missing route: {path}")
        else:
            logger.info("Route OK: %s", path)

    return errors


def run_startup_validation(app) -> bool:
    """Run all startup validations. Returns True if all pass."""
    logger.info("Running startup validation...")

    all_errors: list[str] = []
    all_errors.extend(validate_imports())
    all_errors.extend(validate_tools())
    all_errors.extend(validate_routes(app))

    if all_errors:
        for error in all_errors:
            logger.error("Validation error: %s", error)
        logger.error("Startup validation FAILED with %d error(s)", len(all_errors))
        return False

    logger.info("Startup validation PASSED")
    return True
