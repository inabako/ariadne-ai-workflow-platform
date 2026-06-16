from __future__ import annotations


class GStreamerReceiver:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled
        self.started = False

    def start(self) -> None:
        if self.enabled:
            self.started = True

    def stop(self) -> None:
        self.started = False
