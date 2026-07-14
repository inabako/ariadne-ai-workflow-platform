from __future__ import annotations

from dataclasses import dataclass

from .errors import SecurityPolicyError


@dataclass(frozen=True)
class ToolPolicy:
    denied_tools: tuple[str, ...] = ("delete_file", "run_shell_command", "git_push", "os_admin")
    mutating_tools: tuple[str, ...] = ("write_output_artifact",)

    def assert_allowed(self, tool_name: str) -> None:
        if tool_name in self.denied_tools:
            raise SecurityPolicyError(f"tool is denied by policy: {tool_name}")

    def mutates_state(self, tool_name: str) -> bool:
        return tool_name in self.mutating_tools

