from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EventBus:
    events: list[dict[str, Any]] = field(default_factory=list)

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        self.events.append({"event_type": event_type, "payload": payload})

