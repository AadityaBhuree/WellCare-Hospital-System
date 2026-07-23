"""Thread-safe TTL caching utility for expensive queries."""

import time
from typing import Any


class TTLCache:
    """Simple in-memory TTL cache."""

    def __init__(self, ttl_seconds: float = 5.0) -> None:
        self._cache: dict[str, tuple[float, Any]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Any | None:
        """Get cached value if present and not expired."""
        if key in self._cache:
            ts, val = self._cache[key]
            if time.monotonic() - ts < self._ttl:
                return val
            del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Store value in cache with current timestamp."""
        self._cache[key] = (time.monotonic(), value)

    def invalidate(self, key: str = "") -> None:
        """Clear specific key or entire cache if key is empty."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()
