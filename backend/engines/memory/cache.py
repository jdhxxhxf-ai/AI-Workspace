"""Temporary cache — in-memory cache for Stage 1."""

from typing import Any


class TemporaryCache:
    """Simple in-memory cache with TTL support (infrastructure only)."""

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        """Get a cached value."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set a cached value."""
        self._cache[key] = value

    def delete(self, key: str) -> bool:
        """Delete a cached value."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    @property
    def size(self) -> int:
        """Number of cached entries."""
        return len(self._cache)
