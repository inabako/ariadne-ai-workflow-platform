from __future__ import annotations


class WebSocketClient:
    def __init__(self, url: str) -> None:
        self.url = url
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False
