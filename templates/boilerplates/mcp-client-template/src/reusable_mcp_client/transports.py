from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Protocol

from .mock_server import MockMCPServer
from .servers import ServerDescriptor


class MCPTransport(Protocol):
    async def list_prompts(self) -> list[str]:
        ...

    async def get_prompt(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        ...

    async def list_resources(self) -> list[str]:
        ...

    async def read_resource(self, uri: str) -> dict[str, Any]:
        ...

    async def list_tools(self) -> list[str]:
        ...

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        ...


class InMemoryTransport(MockMCPServer):
    pass


@dataclass
class StdioTransport:
    command: str

    def build_request(self, request_id: int, method: str, params: dict[str, Any] | None = None) -> str:
        return json.dumps({"id": request_id, "method": method, "params": params or {}}, ensure_ascii=False)

    async def _not_connected(self) -> None:
        raise NotImplementedError("Wire this boundary to the official MCP SDK stdio client or a managed subprocess.")

    async def list_prompts(self) -> list[str]:
        await self._not_connected()

    async def get_prompt(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        await self._not_connected()

    async def list_resources(self) -> list[str]:
        await self._not_connected()

    async def read_resource(self, uri: str) -> dict[str, Any]:
        await self._not_connected()

    async def list_tools(self) -> list[str]:
        await self._not_connected()

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        await self._not_connected()


class StreamableHTTPTransport(StdioTransport):
    async def _not_connected(self) -> None:
        raise NotImplementedError("Wire this boundary to the official MCP SDK Streamable HTTP client.")


class TransportFactory:
    def create(self, descriptor: ServerDescriptor) -> MCPTransport:
        if descriptor.transport == "in_memory":
            return InMemoryTransport()
        if descriptor.transport == "stdio":
            return StdioTransport(descriptor.command)
        if descriptor.transport == "streamable_http":
            return StreamableHTTPTransport(descriptor.url)
        raise ValueError(f"unsupported transport: {descriptor.transport}")


async def run_with_timeout(awaitable: Any, timeout_seconds: float) -> Any:
    return await asyncio.wait_for(awaitable, timeout=timeout_seconds)

