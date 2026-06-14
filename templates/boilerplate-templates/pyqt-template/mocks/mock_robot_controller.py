from __future__ import annotations


class MockRobotController:
    def __init__(self) -> None:
        self.started = False
        self.commands: list[tuple[str, dict]] = []

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    def send_command(self, command: str, payload: dict | None = None) -> None:
        self.commands.append((command, payload or {}))
