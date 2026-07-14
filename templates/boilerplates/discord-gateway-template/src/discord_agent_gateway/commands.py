from __future__ import annotations

from dataclasses import dataclass

from .errors import ValidationError


@dataclass(frozen=True)
class CommandDefinition:
    name: str
    description: str
    requires_confirmation: bool = False


class CommandRegistry:
    def __init__(self) -> None:
        self._commands = {
            "submit": CommandDefinition("submit", "Submit a runtime job"),
            "status": CommandDefinition("status", "Get job status"),
            "pause": CommandDefinition("pause", "Pause a job"),
            "resume": CommandDefinition("resume", "Resume a job"),
            "cancel": CommandDefinition("cancel", "Cancel a job", requires_confirmation=True),
            "artifacts": CommandDefinition("artifacts", "List job artifacts"),
            "health": CommandDefinition("health", "Check runtime health"),
        }

    def get(self, name: str) -> CommandDefinition:
        try:
            return self._commands[name]
        except KeyError as exc:
            raise ValidationError(f"unknown command: {name}") from exc

    def list_commands(self) -> list[CommandDefinition]:
        return [self._commands[key] for key in sorted(self._commands)]

