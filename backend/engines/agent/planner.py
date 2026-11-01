"""Rule-based planner — creates execution plans from prompts."""

from engines.agent.models import ExecutionPlan, PlanStep
from shared.exceptions import PlannerError
from shared.logger import get_logger

logger = get_logger("agent.planner")


class Planner:
    """Creates tool execution plans from natural language prompts."""

    def create_plan(self, prompt: str) -> ExecutionPlan:
        """Parse a prompt and create an execution plan."""
        prompt = prompt.strip()
        steps: list[PlanStep] = []
        lower_prompt = prompt.lower()

        if lower_prompt.startswith("read "):
            path = prompt[5:].strip()
            steps.append(PlanStep(tool="file", arguments={"path": path}))

        elif lower_prompt.startswith("terminal "):
            command = prompt[9:].strip()
            steps.append(PlanStep(tool="terminal", arguments={"command": command}))

        elif lower_prompt.startswith("write "):
            try:
                _, path, content = prompt.split("|", 2)
                steps.append(
                    PlanStep(
                        tool="write",
                        arguments={"path": path.strip(), "content": content},
                    )
                )
            except ValueError as e:
                raise PlannerError("Write format: write | path | content") from e

        if not steps:
            raise PlannerError("No suitable tool found for the given prompt.")

        logger.info("Created plan with %d step(s)", len(steps))
        return ExecutionPlan(steps=steps)


planner = Planner()
