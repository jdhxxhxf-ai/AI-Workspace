"""Memory engine interfaces."""

from abc import ABC, abstractmethod
from typing import Any


class MemoryStore(ABC):
    """Abstract interface for memory storage backends."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Retrieve a value by key."""

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Store a value by key."""

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value by key."""

    @abstractmethod
    def clear(self) -> None:
        """Clear all stored values."""
