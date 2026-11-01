"""Agent executor — runs plans through the tool registry."""

from typing import Any

from engines.agent.models import ExecutionPlan
from engines.agent.planner import planner
from engines.tools.registry import registry
from shared.logger import get_logger

logger = get_logger("agent.executor")


class Executor:
    """Executes plans by delegating to registered tools."""

    def execute(self, prompt: str) -> dict[str, Any]:
        """Create a plan from a prompt and execute all steps."""
        plan = planner.create_plan(prompt)
        return self.execute_plan(plan)

    def execute_plan(self, plan: ExecutionPlan) -> dict[str, Any]:
        """Execute a pre-built plan."""
        results: list[dict[str, Any]] = []

        for step in plan.steps:
            logger.info("Executing step: tool=%s", step.tool)
            result = registry.execute(step.tool, **step.arguments)
            results.append({"tool": step.tool, "result": result})

        return {
            "plan": plan.model_dump(),
            "results": results,
        }


executor = Executor()
