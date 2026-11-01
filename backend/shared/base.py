"""Shared base classes."""

from abc import ABC, abstractmethod
from typing import Any


class BaseEngine(ABC):
    """Base class for all engines."""

    name: str = "base"

    @abstractmethod
    def initialize(self) -> None:
        """Initialize engine resources."""

    def shutdown(self) -> None:
        """Release engine resources."""


class BaseManager(ABC):
    """Base class for resource managers."""

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Return manager status information."""
