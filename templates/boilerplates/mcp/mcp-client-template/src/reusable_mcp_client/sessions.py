from __future__ import annotations

from dataclasses import dataclass, field

from .errors import SessionNotConnectedError


@dataclass
class CapabilityCache:
    prompts: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


@dataclass
class ClientSession:
    server_id: str
    connected: bool = False
    capabilities: CapabilityCache = field(default_factory=CapabilityCache)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, ClientSession] = {}

    def mark_connected(self, server_id: str, capabilities: CapabilityCache) -> ClientSession:
        session = ClientSession(server_id=server_id, connected=True, capabilities=capabilities)
        self._sessions[server_id] = session
        return session

    def get_connected(self, server_id: str) -> ClientSession:
        session = self._sessions.get(server_id)
        if session is None or not session.connected:
            raise SessionNotConnectedError(f"server is not connected: {server_id}")
        return session

    def disconnect(self, server_id: str) -> None:
        if server_id in self._sessions:
            self._sessions[server_id].connected = False

    def disconnect_all(self) -> None:
        for session in self._sessions.values():
            session.connected = False

