from __future__ import annotations

from models.telemetry import Telemetry


class TelemetryService:
    def __init__(self) -> None:
        self._started = False
        self._telemetry = Telemetry()

    def start(self) -> None:
        self._started = True

    def stop(self) -> None:
        self._started = False

    def current(self) -> Telemetry:
        return self._telemetry
