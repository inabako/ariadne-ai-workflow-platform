from __future__ import annotations

from typing import Protocol

from models.telemetry import Telemetry


class StartStopService(Protocol):
    def start(self) -> None: ...

    def stop(self) -> None: ...


class RobotControllerInterface(StartStopService, Protocol):
    def send_command(self, command: str, payload: dict | None = None) -> None: ...


class TelemetryServiceInterface(StartStopService, Protocol):
    def current(self) -> Telemetry: ...


class VideoServiceInterface(StartStopService, Protocol):
    def current_frame_label(self) -> str: ...
