from __future__ import annotations


class MockVideoService:
    def __init__(self) -> None:
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    def current_frame_label(self) -> str:
        return "mock frame"
