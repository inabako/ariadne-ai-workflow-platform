from __future__ import annotations

from dataclasses import dataclass

from .errors import AuthorizationError
from .models import DiscordSubject


@dataclass(frozen=True)
class AuthorizationPolicy:
    allowed_guild_ids: tuple[str, ...] = ()
    allowed_channel_ids: tuple[str, ...] = ()
    allowed_role_ids: tuple[str, ...] = ()
    deny_dm_by_default: bool = True

    def assert_allowed(self, subject: DiscordSubject) -> None:
        if self.deny_dm_by_default and subject.is_dm:
            raise AuthorizationError("direct messages are denied")
        if self.allowed_guild_ids and subject.guild_id not in self.allowed_guild_ids:
            raise AuthorizationError("guild is not allowed")
        if self.allowed_channel_ids and subject.channel_id not in self.allowed_channel_ids:
            raise AuthorizationError("channel is not allowed")
        if self.allowed_role_ids and not set(subject.role_ids).intersection(self.allowed_role_ids):
            raise AuthorizationError("required role is missing")

