from __future__ import annotations

from typing import Protocol

from .models import RuntimeCommand, RuntimeResponse


class RuntimeClient(Protocol):
    def send_command(self, command: RuntimeCommand) -> RuntimeResponse:
        ...


class MockRuntimeClient:
    def __init__(self) -> None:
        self.commands: list[RuntimeCommand] = []

    def send_command(self, command: RuntimeCommand) -> RuntimeResponse:
        self.commands.append(command)
        if command.command_type == "runtime.health":
            return RuntimeResponse(status="ok", payload={"runtime": "ready"})
        if command.command_type == "job.submit":
            return RuntimeResponse(status="accepted", payload={"job_id": "job-mock-001"})
        return RuntimeResponse(status="ok", payload=command.payload)

