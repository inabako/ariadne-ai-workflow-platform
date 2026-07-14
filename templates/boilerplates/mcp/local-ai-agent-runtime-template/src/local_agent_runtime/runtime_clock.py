from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class RuntimeClock:
    max_runtime_seconds: int = 28_800

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def deadline_from(self, started_at: datetime) -> datetime:
        return started_at + timedelta(seconds=self.max_runtime_seconds)

    def is_expired(self, started_at: datetime, current: datetime | None = None) -> bool:
        return (current or self.now()) >= self.deadline_from(started_at)

