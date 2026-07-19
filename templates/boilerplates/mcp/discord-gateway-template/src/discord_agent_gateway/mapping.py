from __future__ import annotations

from .errors import ValidationError
from .models import DiscordInteraction, RuntimeCommand, RuntimeEvent, DiscordMessage
from .security import escape_mentions


class CommandMapper:
    def map_interaction(self, interaction: DiscordInteraction) -> RuntimeCommand:
        name = interaction.command_name
        options = interaction.options
        if name == "submit":
            goal = str(options.get("goal", "")).strip()
            if not goal:
                raise ValidationError("goal is required")
            payload = {"goal": goal, "workflow_name": options.get("workflow_name", "repository-analysis")}
            command_type = "job.submit"
        elif name in {"status", "pause", "resume", "cancel", "artifacts"}:
            job_id = str(options.get("job_id", "")).strip()
            if not job_id:
                raise ValidationError("job_id is required")
            payload = {"job_id": job_id}
            command_type = f"job.{name}"
        elif name == "health":
            payload = {}
            command_type = "runtime.health"
        else:
            raise ValidationError(f"unknown command: {name}")
        return RuntimeCommand(
            command_type=command_type,
            requested_by=interaction.subject.user_id,
            payload=payload,
            idempotency_key=interaction.interaction_id,
        )


class RuntimeEventMapper:
    def to_discord_message(self, event: RuntimeEvent, channel_id: str) -> DiscordMessage:
        content = f"[{event.event_type}] {event.job_id}: {escape_mentions(event.summary)}"
        components: list[dict[str, str]] = []
        if event.event_type == "job.waiting_for_input":
            components = [
                {"type": "button", "label": "Approve", "action": "human_check.approve"},
                {"type": "button", "label": "Reject", "action": "human_check.reject"},
            ]
        return DiscordMessage(channel_id=channel_id, content=content, components=components)

