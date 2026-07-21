from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolResponse:
    status: str
    data: dict[str, Any] = field(default_factory=dict)
    error_code: str = ""
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"status": self.status, **self.data}
        if self.error_code:
            payload["error_code"] = self.error_code
        if self.message:
            payload["message"] = self.message
        return payload

    @classmethod
    def ok(cls, **data: Any) -> "ToolResponse":
        return cls(status="ok", data=data)

    @classmethod
    def error(cls, *, error_code: str, message: str) -> "ToolResponse":
        return cls(status="error", error_code=error_code, message=message)
