"""FastAPI REST routes for RAG & Knowledge Engine."""

from fastapi import APIRouter, HTTPException, Query

from api.rag.schemas import (
    RAGContextRequest,
    RAGContextResponse,
    RAGDeleteResponse,
    RAGIndexRequest,
    RAGIndexResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGStatsResponse,
    RAGStatusResponse,
)
from engines.rag.services.retrieval_service import knowledge_retrieval_service
from shared.exceptions import AIWorkspaceError, ProjectNotFoundError, WorkspaceNotFoundError

router = APIRouter(prefix="/rag", tags=["RAG & Knowledge Engine"])


@router.post("/index", response_model=RAGIndexResponse)
def index_project(req: RAGIndexRequest):
    """Perform a full RAG indexing run over a project workspace."""
    try:
        stats = knowledge_retrieval_service.index_project(req.project_path)
        return RAGIndexResponse(stats=stats)
    except WorkspaceNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
    except AIWorkspaceError as error:
        raise HTTPException(status_code=400, detail=error.message) from error


@router.post("/refresh", response_model=RAGIndexResponse)
def refresh_project(req: RAGIndexRequest):
    """Perform incremental RAG indexing based on Stage 2 content hashes."""
    try:
        stats = knowledge_retrieval_service.refresh_project(req.project_path)
        return RAGIndexResponse(stats=stats)
    except WorkspaceNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
    except AIWorkspaceError as error:
        raise HTTPException(status_code=400, detail=error.message) from error


@router.get("/status", response_model=RAGStatusResponse)
def get_rag_status():
    """Return status of RAG engine, embedding provider, and vector store."""
    return RAGStatusResponse(**knowledge_retrieval_service.get_status_info())


@router.get("/stats", response_model=RAGStatsResponse)
def get_project_rag_stats(project_path: str = Query(...)):
    """Return total chunk counts and metadata for a project in RAG vector store."""
    try:
        return RAGStatsResponse(**knowledge_retrieval_service.get_stats(project_path))
    except WorkspaceNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error


@router.post("/search", response_model=RAGSearchResponse)
def search_knowledge(req: RAGSearchRequest):
    """Perform hybrid semantic and lexical search over indexed project knowledge."""
    try:
        results = knowledge_retrieval_service.search(
            project_path=req.project_path,
            query=req.query,
            limit=req.limit,
            metadata_filter=req.metadata_filter,
        )
        return RAGSearchResponse(
            query=req.query,
            project_path=req.project_path,
            total_results=len(results),
            results=[r.model_dump() for r in results],
        )
    except WorkspaceNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
    except AIWorkspaceError as error:
        raise HTTPException(status_code=400, detail=error.message) from error


@router.post("/context", response_model=RAGContextResponse)
def build_knowledge_context(req: RAGContextRequest):
    """Retrieve and format structured context payload for AI Agents."""
    try:
        payload = knowledge_retrieval_service.build_context(
            project_path=req.project_path,
            query=req.query,
            limit=req.limit,
            metadata_filter=req.metadata_filter,
        )
        return RAGContextResponse(**payload.model_dump())
    except WorkspaceNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
    except AIWorkspaceError as error:
        raise HTTPException(status_code=400, detail=error.message) from error


@router.delete("/project", response_model=RAGDeleteResponse)
def delete_project_rag(project_path: str = Query(...)):
    """Delete all indexed RAG vectors and chunks for a project."""
    try:
        return RAGDeleteResponse(**knowledge_retrieval_service.delete_project(project_path))
    except WorkspaceNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.message) from error
