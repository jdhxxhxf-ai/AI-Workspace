"""Workspace data models."""

from pydantic import BaseModel


class FileNode(BaseModel):
    """A file or directory node in the workspace."""

    name: str
    path: str
    is_dir: bool


class WorkspaceInfo(BaseModel):
    """Summary information about a scanned workspace."""

    root: str
    total_files: int
    total_directories: int
    items: list[FileNode]


class WorkspaceConfig(BaseModel):
    """Workspace configuration."""

    root_path: str
    name: str = ""
    watch_enabled: bool = False
