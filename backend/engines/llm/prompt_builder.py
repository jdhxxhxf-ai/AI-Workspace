"""Prompt builder — infrastructure for constructing LLM prompts."""

from dataclasses import dataclass, field


@dataclass
class PromptTemplate:
    """A reusable prompt template."""

    system: str = ""
    user: str = ""
    context: str = ""


class PromptBuilder:
    """Builds structured prompts for LLM requests."""

    def __init__(self) -> None:
        self._parts: list[str] = []

    def add_system(self, text: str) -> "PromptBuilder":
        """Add a system instruction."""
        self._parts.append(f"[System]\n{text}")
        return self

    def add_context(self, text: str) -> "PromptBuilder":
        """Add context information."""
        self._parts.append(f"[Context]\n{text}")
        return self

    def add_user(self, text: str) -> "PromptBuilder":
        """Add a user message."""
        self._parts.append(f"[User]\n{text}")
        return self

    def build(self) -> str:
        """Build the final prompt string."""
        return "\n\n".join(self._parts)

    @staticmethod
    def from_template(template: PromptTemplate) -> str:
        """Build a prompt from a template."""
        builder = PromptBuilder()
        if template.system:
            builder.add_system(template.system)
        if template.context:
            builder.add_context(template.context)
        if template.user:
            builder.add_user(template.user)
        return builder.build()
