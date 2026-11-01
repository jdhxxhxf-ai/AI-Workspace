"""Central API router — aggregates all route modules."""

from fastapi import APIRouter

from api.agent.routes import router as agent_router
from api.files.routes import router as files_router
from api.health import router as health_router
from api.indexer.routes import router as indexer_router
from api.rag.routes import router as rag_router
from api.tools.routes import router as tools_router
from api.workspace.routes import router as workspace_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(workspace_router)
api_router.include_router(files_router)
api_router.include_router(tools_router)
api_router.include_router(agent_router)
api_router.include_router(indexer_router)
api_router.include_router(rag_router)
