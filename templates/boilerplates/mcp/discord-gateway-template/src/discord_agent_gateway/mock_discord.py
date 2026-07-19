from __future__ import annotations

from dataclasses import dataclass, field

from .models import DiscordMessage


@dataclass
class MockDiscordAdapter:
    sent_messages: list[DiscordMessage] = field(default_factory=list)

    def send_message(self, message: DiscordMessage) -> str:
        self.sent_messages.append(message)
        return f"message-{len(self.sent_messages)}"

