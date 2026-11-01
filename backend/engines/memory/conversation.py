"""Conversation memory — interface for Stage 1."""

from typing import Any

from engines.memory.interfaces import MemoryStore


class ConversationMemory:
    """Stores conversation history for a session."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._messages: list[dict[str, Any]] = []
        self._store = store

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self._messages.append({"role": role, "content": content})

    def get_messages(self) -> list[dict[str, Any]]:
        """Get all conversation messages."""
        return list(self._messages)

    def clear(self) -> None:
        """Clear conversation history."""
        self._messages.clear()

    @property
    def count(self) -> int:
        """Number of messages in conversation."""
        return len(self._messages)
