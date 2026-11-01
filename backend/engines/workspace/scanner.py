"""Workspace directory scanner."""

from pathlib import Path

from engines.workspace.models import FileNode, WorkspaceInfo
from shared.exceptions import WorkspaceNotFoundError


def scan_workspace(path: str) -> WorkspaceInfo:
    """Scan a workspace directory and return its structure."""
    root = Path(path)

    if not root.exists():
        raise WorkspaceNotFoundError(path)

    items: list[FileNode] = []
    files = 0
    directories = 0

    for item in root.iterdir():
        if item.is_dir():
            directories += 1
        else:
            files += 1

        items.append(
            FileNode(
                name=item.name,
                path=str(item),
                is_dir=item.is_dir(),
            )
        )

    return WorkspaceInfo(
        root=str(root),
        total_files=files,
        total_directories=directories,
        items=items,
    )
