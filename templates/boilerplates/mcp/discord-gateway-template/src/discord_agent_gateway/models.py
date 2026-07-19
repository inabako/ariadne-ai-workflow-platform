from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DiscordSubject:
    user_id: str
    guild_id: str | None
    channel_id: str | None
    role_ids: tuple[str, ...] = ()
    is_dm: bool = False


@dataclass(frozen=True)
class DiscordInteraction:
    interaction_id: str
    interaction_type: str
    command_name: str
    subject: DiscordSubject
    options: dict[str, Any] = field(default_factory=dict)
    custom_id: str | None = None


@dataclass(frozen=True)
class RuntimeCommand:
    command_type: str
    requested_by: str
    payload: dict[str, Any]
    idempotency_key: str


@dataclass(frozen=True)
class RuntimeResponse:
    status: str
    payload: dict[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass(frozen=True)
class RuntimeEvent:
    event_id: str
    event_type: str
    job_id: str
    summary: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiscordMessage:
    channel_id: str
    content: str
    components: list[dict[str, Any]] = field(default_factory=list)

