from __future__ import annotations

import argparse
import asyncio
from typing import Any

from .audit import AuditLog
from .notifications import NotificationRouter
from .retry import RetryPolicy
from .security import validate_resource_uri
from .servers import ServerDescriptor, ServerRegistry
from .sessions import CapabilityCache, SessionManager
from .transports import TransportFactory


class MCPClient:
    def __init__(self) -> None:
        self.registry = ServerRegistry()
        self.sessions = SessionManager()
        self._adapters: dict[str, Any] = {}
        self.transport_factory = TransportFactory()
        self.retry_policy = RetryPolicy()
        self.audit = AuditLog()
        self.notifications = NotificationRouter()

    def register_server(self, descriptor: ServerDescriptor, adapter: Any | None = None) -> None:
        self.registry.register(descriptor)
        if adapter is not None:
            self._adapters[descriptor.server_id] = adapter

    async def connect(self, server_id: str) -> dict[str, Any]:
        descriptor = self.registry.get(server_id)
        adapter = self._adapter_for(descriptor)
        self.audit.record(server_id, "connect")
        capabilities = CapabilityCache(
            prompts=await adapter.list_prompts(),
            resources=await adapter.list_resources(),
            tools=await adapter.list_tools(),
        )
        self.sessions.mark_connected(server_id, capabilities)
        return {"status": "connected", "server_id": server_id, "capabilities": capabilities}

    async def disconnect(self, server_id: str) -> None:
        self.sessions.disconnect(server_id)

    async def disconnect_all(self) -> None:
        self.sessions.disconnect_all()

    async def get_server_status(self, server_id: str) -> dict[str, Any]:
        session = self.sessions.get_connected(server_id)
        return {"server_id": server_id, "connected": session.connected, "capabilities": session.capabilities}

    async def list_prompts(self, server_id: str) -> list[str]:
        return list(self.sessions.get_connected(server_id).capabilities.prompts)

    async def get_prompt(self, server_id: str, prompt_name: str, arguments: dict[str, Any] | None = None) -> str:
        self.sessions.get_connected(server_id)
        self.audit.record(server_id, "get_prompt", {"prompt_name": prompt_name, **(arguments or {})})
        return await self._adapters[server_id].get_prompt(prompt_name, arguments or {})

    async def list_resources(self, server_id: str) -> list[str]:
        return list(self.sessions.get_connected(server_id).capabilities.resources)

    async def read_resource(self, server_id: str, uri: str) -> dict[str, Any]:
        validate_resource_uri(uri)
        self.sessions.get_connected(server_id)
        self.audit.record(server_id, "read_resource", {"uri": uri})
        return await self._adapters[server_id].read_resource(uri)

    async def list_tools(self, server_id: str) -> list[str]:
        return list(self.sessions.get_connected(server_id).capabilities.tools)

    async def call_tool(self, server_id: str, tool_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        self.sessions.get_connected(server_id)
        self.audit.record(server_id, "call_tool", {"tool_name": tool_name, **(arguments or {})})
        return await self._adapters[server_id].call_tool(tool_name, arguments or {})

    def handle_notification(self, server_id: str, event_type: str, payload: dict[str, Any]) -> None:
        self.sessions.get_connected(server_id)
        self.notifications.handle(server_id, event_type, payload)

    def _adapter_for(self, descriptor: ServerDescriptor) -> Any:
        if descriptor.server_id not in self._adapters:
            self._adapters[descriptor.server_id] = self.transport_factory.create(descriptor)
        return self._adapters[descriptor.server_id]


async def _demo() -> None:
    client = MCPClient()
    client.register_server(ServerDescriptor(server_id="local-model"))
    await client.connect("local-model")
    print([server.server_id for server in client.registry.list_servers()])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-servers", action="store_true")
    args = parser.parse_args()
    if args.list_servers:
        asyncio.run(_demo())


if __name__ == "__main__":
    main()
