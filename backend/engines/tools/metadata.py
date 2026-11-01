"""Tool metadata models."""

from dataclasses import dataclass, field


@dataclass
class ToolMetadata:
    """Metadata describing a registered tool."""

    name: str
    description: str
    version: str = "1.0.0"
    parameters: dict[str, str] = field(default_factory=dict)
