from __future__ import annotations

from models.telemetry import Telemetry


class MockTelemetryService:
    def __init__(self) -> None:
        self.started = False
        self.telemetry = Telemetry(battery_percent=88.0, signal_quality=0.95, connected=True)

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    def current(self) -> Telemetry:
        return self.telemetry
