from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProgressEvent:
    server_id: str
    operation: str
    current: int
    total: int | None = None

    @property
    def ratio(self) -> float | None:
        if self.total in (None, 0):
            return None
        return self.current / self.total

