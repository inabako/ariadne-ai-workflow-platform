from __future__ import annotations

from typing import Protocol


class ModelAdapter(Protocol):
    def decide(self, prompt: str) -> dict[str, object]:
        ...


class MCPClientAdapter(Protocol):
    def call_tool(self, server_id: str, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
        ...


class MockModelAdapter:
    def decide(self, prompt: str) -> dict[str, object]:
        return {"action": "continue", "reasoning_summary": prompt[:120]}

