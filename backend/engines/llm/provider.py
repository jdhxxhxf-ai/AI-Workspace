"""LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    name: str = "base"

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a text completion from a prompt."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is reachable."""

    @abstractmethod
    def list_models(self) -> list[str]:
        """List available models."""
