from __future__ import annotations

from pathlib import Path

import pytest

from discord_agent_gateway import DiscordGateway, DiscordInteraction, DiscordSubject, RuntimeEvent
from discord_agent_gateway.authorization import AuthorizationPolicy
from discord_agent_gateway.errors import AuthorizationError, RateLimitError
from discord_agent_gateway.human_check import HumanCheckTokenManager
from discord_agent_gateway.mapping import CommandMapper, RuntimeEventMapper
from discord_agent_gateway.rate_limit import InMemoryRateLimiter
from discord_agent_gateway.runtime_client import MockRuntimeClient
from discord_agent_gateway.security import escape_mentions
from discord_agent_gateway.state import SQLiteGatewayStateStore


def subject() -> DiscordSubject:
    return DiscordSubject(
        user_id="user-1",
        guild_id="guild-1",
        channel_id="channel-1",
        role_ids=("role-operator",),
    )


def test_submit_command_maps_to_runtime_dto_without_discord_types(tmp_path: Path) -> None:
    runtime = MockRuntimeClient()
    gateway = DiscordGateway(
        runtime_client=runtime,
        authorization_policy=AuthorizationPolicy(allowed_guild_ids=("guild-1",), allowed_role_ids=("role-operator",)),
        state_path=tmp_path / "gateway.db",
    )
    interaction = DiscordInteraction(
        interaction_id="interaction-1",
        interaction_type="slash_command",
        command_name="submit",
        subject=subject(),
        options={"goal": "Analyze repository", "workflow_name": "repository-analysis"},
    )

    response = gateway.handle_interaction(interaction)

    assert response.status == "accepted"
    assert runtime.commands[0].command_type == "job.submit"
    assert runtime.commands[0].payload == {"goal": "Analyze repository", "workflow_name": "repository-analysis"}
    assert runtime.commands[0].requested_by == "user-1"


def test_authorization_and_rate_limit_block_before_runtime(tmp_path: Path) -> None:
    runtime = MockRuntimeClient()
    gateway = DiscordGateway(
        runtime_client=runtime,
        authorization_policy=AuthorizationPolicy(allowed_guild_ids=("guild-allowed",)),
        state_path=tmp_path / "gateway.db",
    )
    denied = DiscordInteraction(
        interaction_id="interaction-denied",
        interaction_type="slash_command",
        command_name="health",
        subject=subject(),
    )

    denied_response = gateway.handle_interaction(denied)
    limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
    limiter.assert_allowed("user-1:submit")

    assert denied_response.status == "error"
    assert denied_response.payload["error_code"] == "authorization_denied"
    assert runtime.commands == []
    with pytest.raises(RateLimitError):
        limiter.assert_allowed("user-1:submit")


def test_human_check_token_rejects_tampering() -> None:
    manager = HumanCheckTokenManager(secret="test-secret", ttl_seconds=60)
    token = manager.create("job-1", "hc-1")

    assert manager.verify(token.public_token).job_id == "job-1"
    with pytest.raises(KeyError):
        manager.verify(token.public_token + "-tampered")


def test_runtime_event_notification_is_deduped_and_mentions_are_escaped(tmp_path: Path) -> None:
    gateway = DiscordGateway(state_path=tmp_path / "gateway.db")
    event = RuntimeEvent(
        event_id="event-1",
        event_type="job.waiting_for_input",
        job_id="job-1",
        summary="@everyone approve this",
    )

    first_message_id = gateway.deliver_event(event, "channel-1")
    second_message_id = gateway.deliver_event(event, "channel-1")

    assert first_message_id == "message-1"
    assert second_message_id is None
    assert "@\u200beveryone" in gateway.discord.sent_messages[0].content
    assert gateway.discord.sent_messages[0].components[0]["action"] == "human_check.approve"


def test_sqlite_state_store_persists_event_and_message_reference(tmp_path: Path) -> None:
    store = SQLiteGatewayStateStore(tmp_path / "gateway.db")

    assert store.mark_event_seen("event-1") is True
    assert store.mark_event_seen("event-1") is False
    store.save_message_reference("job-1", "channel-1", "message-1")

    reloaded = SQLiteGatewayStateStore(tmp_path / "gateway.db")
    assert reloaded.get_message_reference("job-1") == ("channel-1", "message-1")


def test_mapper_validates_goal_and_mention_policy() -> None:
    mapper = CommandMapper()
    interaction = DiscordInteraction(
        interaction_id="interaction-empty",
        interaction_type="slash_command",
        command_name="submit",
        subject=subject(),
        options={"goal": ""},
    )

    with pytest.raises(Exception):
        mapper.map_interaction(interaction)
    assert escape_mentions("hi @here <@123>") == "hi @\u200bhere <@\u200b123>"
    message = RuntimeEventMapper().to_discord_message(
        RuntimeEvent(event_id="e2", event_type="job.completed", job_id="job-2", summary="done"),
        "channel-1",
    )
    assert message.content == "[job.completed] job-2: done"

