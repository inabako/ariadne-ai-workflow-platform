from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NotificationRouter:
    events: list[dict[str, Any]] = field(default_factory=list)

    def handle(self, server_id: str, event_type: str, payload: dict[str, Any]) -> None:
        self.events.append({"server_id": server_id, "event_type": event_type, "payload": payload})

