from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AuditRecorder:
    records: list[dict[str, Any]] = field(default_factory=list)

    def record(self, action: str, target: str, *, status: str, metadata: dict[str, Any] | None = None) -> None:
        self.records.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": action,
                "target": target,
                "status": status,
                "metadata": metadata or {},
            }
        )

