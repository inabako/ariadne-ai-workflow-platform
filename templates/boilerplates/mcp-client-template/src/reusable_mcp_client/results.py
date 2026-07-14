from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OperationResult:
    status: str
    server_id: str
    operation: str
    data: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "server_id": self.server_id,
            "operation": self.operation,
            **self.data,
        }
        if self.error_code:
            payload["error_code"] = self.error_code
        if self.message:
            payload["message"] = self.message
        return payload

