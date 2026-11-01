"""Workspace API routes."""

from fastapi import APIRouter, HTTPException

from engines.workspace.manager import workspace_manager
from shared.exceptions import WorkspaceNotFoundError

router = APIRouter(prefix="/workspace", tags=["Workspace"])


@router.get("/scan")
def scan(path: str):
    """Scan a workspace directory."""
    try:
        return workspace_manager.discover(path)
    except WorkspaceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message) from e
