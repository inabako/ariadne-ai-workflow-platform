from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Telemetry:
    battery_percent: float = 0.0
    signal_quality: float = 0.0
    last_command: str = ""
    connected: bool = False
