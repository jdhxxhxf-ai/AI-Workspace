"""Agent engine data models."""

from typing import Any

from pydantic import BaseModel


class PlannerRequest(BaseModel):
    """Request to create an execution plan."""

    prompt: str


class ExecutorRequest(BaseModel):
    """Request to execute a plan from a prompt."""

    prompt: str


class PlanStep(BaseModel):
    """A single step in an execution plan."""

    tool: str
    arguments: dict[str, Any]


class ExecutionPlan(BaseModel):
    """A complete execution plan."""

    steps: list[PlanStep]
