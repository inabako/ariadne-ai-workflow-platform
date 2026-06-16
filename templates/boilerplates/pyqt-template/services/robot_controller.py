from __future__ import annotations

from network.protocol import encode_message
from network.udp_client import UDPControlClient


class RobotControllerService:
    def __init__(self, client: UDPControlClient) -> None:
        self._client = client

    def start(self) -> None:
        self._client.start()

    def stop(self) -> None:
        self._client.stop()

    def send_command(self, command: str, payload: dict | None = None) -> None:
        self._client.send(encode_message(command, payload))
