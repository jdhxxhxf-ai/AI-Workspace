"""Project Intelligence API routes."""

from fastapi import APIRouter, HTTPException, Query

from api.indexer.schemas import (
    DependencyListResponse,
    FileListResponse,
    IndexResponse,
    RefreshResponse,
    SymbolSearchResponse,
)
from engines.indexer.context import project_context_builder
from engines.indexer.service import project_intelligence
from shared.exceptions import AIWorkspaceError, ProjectNotFoundError, WorkspaceNotFoundError

router = APIRouter(prefix="/indexer", tags=["Project Intelligence"])


@router.post("/scan", response_model=IndexResponse)
def scan_project(project_path: str):
    """Scan and fully index a project directory."""
    try:
        result = project_intelligence.index_project(project_path)
        return IndexResponse(**result)
    except WorkspaceNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
    except AIWorkspaceError as error:
        raise HTTPException(status_code=400, detail=error.message) from error


@router.post("/refresh", response_model=RefreshResponse)
def refresh_project(project_path: str):
    """Incrementally refresh a project index using content hashes."""
    try:
        result = project_intelligence.refresh_project(project_path)
        return RefreshResponse(**result)
    except WorkspaceNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
    except AIWorkspaceError as error:
        raise HTTPException(status_code=400, detail=error.message) from error


@router.get("/indexes")
def list_indexes():
    """List all stored project indexes."""
    return project_intelligence.list_indexes()


@router.get("/project")
def get_project_summary(project_path: str):
    """Return deterministic project summary."""
    try:
        return project_intelligence.get_project_summary(project_path)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error


@router.get("/files", response_model=FileListResponse)
def list_project_files(
    project_path: str,
    language: str | None = None,
    limit: int = Query(default=200, le=1000),
):
    """List indexed files for a project."""
    try:
        return FileListResponse(**project_intelligence.list_files(project_path, language, limit))
    except WorkspaceNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error


@router.get("/file")
def get_file_intelligence(project_path: str, path: str):
    """Return structural intelligence for a single indexed file."""
    try:
        return project_intelligence.get_file_intelligence(project_path, path)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
    except AIWorkspaceError as error:
        raise HTTPException(status_code=404, detail=error.message) from error


@router.get("/symbols/search", response_model=SymbolSearchResponse)
def search_symbols(
    project_path: str,
    q: str,
    symbol_type: str | None = None,
    limit: int = Query(default=50, le=200),
):
    """Search symbols by name within an indexed project."""
    try:
        return SymbolSearchResponse(
            **project_intelligence.search_symbols(project_path, q, symbol_type, limit)
        )
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error


@router.get("/dependencies", response_model=DependencyListResponse)
def get_dependencies(project_path: str, path: str):
    """Return direct dependencies for a file/module."""
    try:
        return DependencyListResponse(
            dependencies=project_intelligence.get_dependencies(project_path, path)["dependencies"]
        )
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error


@router.get("/dependents", response_model=DependencyListResponse)
def get_dependents(project_path: str, path: str):
    """Return reverse dependencies for a file/module."""
    try:
        return DependencyListResponse(
            dependents=project_intelligence.get_dependents(project_path, path)["dependents"]
        )
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error


@router.get("/graph")
def get_project_graph(project_path: str):
    """Return the structural dependency graph for a project."""
    try:
        return project_intelligence.get_graph(project_path)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error


@router.get("/context")
def get_project_context(project_path: str, focus_path: str | None = None):
    """Return compact structural project context."""
    try:
        return project_context_builder.build(project_path, focus_path)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
