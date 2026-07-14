from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic

from .errors import RateLimitError


@dataclass
class InMemoryRateLimiter:
    max_requests: int = 5
    window_seconds: float = 60.0
    _hits: dict[str, list[float]] = field(default_factory=dict)

    def assert_allowed(self, key: str) -> None:
        now = monotonic()
        hits = [hit for hit in self._hits.get(key, []) if now - hit <= self.window_seconds]
        if len(hits) >= self.max_requests:
            raise RateLimitError("rate limit exceeded")
        hits.append(now)
        self._hits[key] = hits

