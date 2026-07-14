from __future__ import annotations

from dataclasses import dataclass

from .errors import ServerNotFoundError


@dataclass(frozen=True)
class ServerDescriptor:
    server_id: str
    transport: str = "in_memory"
    command: str = ""
    url: str = ""
    enabled: bool = True


class ServerRegistry:
    def __init__(self) -> None:
        self._servers: dict[str, ServerDescriptor] = {}

    def register(self, descriptor: ServerDescriptor) -> None:
        self._servers[descriptor.server_id] = descriptor

    def get(self, server_id: str) -> ServerDescriptor:
        try:
            return self._servers[server_id]
        except KeyError as exc:
            raise ServerNotFoundError(f"unknown server: {server_id}") from exc

    def list_servers(self) -> list[ServerDescriptor]:
        return [self._servers[key] for key in sorted(self._servers)]

