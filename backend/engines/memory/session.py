"""Session storage — interface for Stage 1."""

from typing import Any
from uuid import uuid4


class SessionStorage:
    """Manages user sessions with associated data."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid4())
        self._sessions[session_id] = {}
        return session_id

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get session data."""
        return self._sessions.get(session_id)

    def set_data(self, session_id: str, key: str, value: Any) -> None:
        """Set data in a session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = {}
        self._sessions[session_id][key] = value

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    @property
    def active_sessions(self) -> int:
        """Number of active sessions."""
        return len(self._sessions)
