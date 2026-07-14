from __future__ import annotations

import socket


class UDPControlClient:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._socket: socket.socket | None = None

    @property
    def started(self) -> bool:
        return self._socket is not None

    def start(self) -> None:
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data: bytes) -> None:
        if self._socket is None:
            raise RuntimeError("UDPControlClient is not started")
        self._socket.sendto(data, (self._host, self._port))

    def stop(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
