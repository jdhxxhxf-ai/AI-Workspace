"""Shared exception hierarchy."""


class AIWorkspaceError(Exception):
    """Base exception for AI Workspace."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ToolNotFoundError(AIWorkspaceError):
    """Raised when a requested tool is not registered."""

    def __init__(self, tool_name: str):
        super().__init__(
            f"Tool '{tool_name}' not found",
            code="TOOL_NOT_FOUND",
        )


class ToolValidationError(AIWorkspaceError):
    """Raised when tool input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, code="TOOL_VALIDATION_ERROR")


class WorkspaceNotFoundError(AIWorkspaceError):
    """Raised when a workspace path does not exist."""

    def __init__(self, path: str):
        super().__init__(
            f"Workspace not found: {path}",
            code="WORKSPACE_NOT_FOUND",
        )


class PlannerError(AIWorkspaceError):
    """Raised when the planner cannot create a valid plan."""

    def __init__(self, message: str):
        super().__init__(message, code="PLANNER_ERROR")


class LLMProviderError(AIWorkspaceError):
    """Raised when an LLM provider operation fails."""

    def __init__(self, message: str):
        super().__init__(message, code="LLM_PROVIDER_ERROR")


class IndexerError(AIWorkspaceError):
    """Raised when project indexing or intelligence queries fail."""

    def __init__(self, message: str):
        super().__init__(message, code="INDEXER_ERROR")


class ProjectNotFoundError(AIWorkspaceError):
    """Raised when a requested project index does not exist."""

    def __init__(self, path: str):
        super().__init__(
            f"Project not indexed: {path}",
            code="PROJECT_NOT_FOUND",
        )
