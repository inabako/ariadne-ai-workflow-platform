from __future__ import annotations


class VideoService:
    def __init__(self) -> None:
        self._started = False

    def start(self) -> None:
        self._started = True

    def stop(self) -> None:
        self._started = False

    def current_frame_label(self) -> str:
        return "video stopped" if not self._started else "video running"
