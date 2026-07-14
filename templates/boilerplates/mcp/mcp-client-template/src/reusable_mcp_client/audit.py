from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .security import mask_secrets


@dataclass
class AuditLog:
    records: list[dict[str, Any]] = field(default_factory=list)

    def record(self, server_id: str, operation: str, arguments: dict[str, Any] | None = None) -> None:
        self.records.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "server_id": server_id,
                "operation": operation,
                "arguments": mask_secrets(arguments or {}),
            }
        )

