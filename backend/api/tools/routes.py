"""Tools API routes."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from engines.tools.registry import registry
from shared.exceptions import AIWorkspaceError

router = APIRouter(prefix="/tools", tags=["Tools"])


class ToolRequest(BaseModel):
    """Request to execute a tool."""

    tool: str
    arguments: dict[str, Any]


@router.post("/execute")
def execute_tool(request: ToolRequest):
    """Execute a registered tool."""
    try:
        return registry.execute(request.tool, **request.arguments)
    except AIWorkspaceError as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.get("/list")
def list_tools():
    """List all registered tools."""
    tools = [
        {
            "name": t.name,
            "description": t.description,
            "version": t.version,
        }
        for t in registry.list_tools()
    ]
    return {"tools": tools}
