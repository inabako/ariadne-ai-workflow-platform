from __future__ import annotations

from typing import Any


class MockMCPServer:
    def __init__(self) -> None:
        self.prompts = {"summary": "Summarize {topic}"}
        self.resources = {"mock://status": {"status": "ready"}}
        self.tools = {"health_check": self._health_check}

    async def list_prompts(self) -> list[str]:
        return sorted(self.prompts)

    async def get_prompt(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        return self.prompts[name].format(**(arguments or {}))

    async def list_resources(self) -> list[str]:
        return sorted(self.resources)

    async def read_resource(self, uri: str) -> dict[str, Any]:
        return dict(self.resources[uri])

    async def list_tools(self) -> list[str]:
        return sorted(self.tools)

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.tools[name](arguments or {})

    def _health_check(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"status": "ok", "arguments": arguments}

