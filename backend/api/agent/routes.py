"""Agent API routes — planner and executor."""

from fastapi import APIRouter, HTTPException

from engines.agent.executor import executor
from engines.agent.models import ExecutorRequest, PlannerRequest
from engines.agent.planner import planner
from shared.exceptions import PlannerError

router = APIRouter(tags=["Agent"])


@router.post("/planner/plan")
def create_plan(request: PlannerRequest):
    """Create an execution plan from a prompt."""
    try:
        return planner.create_plan(request.prompt)
    except PlannerError as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.post("/executor/run")
def run_executor(request: ExecutorRequest):
    """Execute a plan from a prompt."""
    try:
        return executor.execute(request.prompt)
    except PlannerError as e:
        raise HTTPException(status_code=400, detail=e.message) from e
