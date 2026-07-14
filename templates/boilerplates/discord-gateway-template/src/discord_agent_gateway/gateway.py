from __future__ import annotations

from pathlib import Path

from .authorization import AuthorizationPolicy
from .commands import CommandRegistry
from .errors import GatewayError
from .human_check import HumanCheckTokenManager
from .mapping import CommandMapper, RuntimeEventMapper
from .mock_discord import MockDiscordAdapter
from .models import DiscordInteraction, RuntimeEvent, RuntimeResponse
from .rate_limit import InMemoryRateLimiter
from .runtime_client import MockRuntimeClient, RuntimeClient
from .state import SQLiteGatewayStateStore


class DiscordGateway:
    def __init__(
        self,
        runtime_client: RuntimeClient | None = None,
        authorization_policy: AuthorizationPolicy | None = None,
        state_path: Path | None = None,
    ) -> None:
        self.registry = CommandRegistry()
        self.authorization = authorization_policy or AuthorizationPolicy()
        self.command_mapper = CommandMapper()
        self.event_mapper = RuntimeEventMapper()
        self.runtime_client = runtime_client or MockRuntimeClient()
        self.rate_limiter = InMemoryRateLimiter()
        self.discord = MockDiscordAdapter()
        self.human_checks = HumanCheckTokenManager(secret="template-secret")
        self.state = SQLiteGatewayStateStore(state_path or Path("workspace/state/gateway.db"))

    def handle_interaction(self, interaction: DiscordInteraction) -> RuntimeResponse:
        try:
            self.authorization.assert_allowed(interaction.subject)
            self.rate_limiter.assert_allowed(f"{interaction.subject.user_id}:{interaction.command_name}")
            self.registry.get(interaction.command_name)
            command = self.command_mapper.map_interaction(interaction)
            return self.runtime_client.send_command(command)
        except GatewayError as exc:
            return RuntimeResponse(status="error", payload={"error_code": exc.code}, message=str(exc))

    def deliver_event(self, event: RuntimeEvent, channel_id: str) -> str | None:
        if not self.state.mark_event_seen(event.event_id):
            return None
        message = self.event_mapper.to_discord_message(event, channel_id)
        message_id = self.discord.send_message(message)
        self.state.save_message_reference(event.job_id, channel_id, message_id)
        return message_id

