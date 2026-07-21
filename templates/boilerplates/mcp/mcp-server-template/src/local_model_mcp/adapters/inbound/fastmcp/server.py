from __future__ import annotations

from typing import Any

from ....bootstrap import ApplicationContainer
from .resources.example_resource import read_model_information
from .tools import call_health_check, call_invoke_local_model, call_read_workspace_file, call_write_output_artifact


class FastMCPServerAdapter:
    def __init__(self, container: ApplicationContainer, *, name: str = "local-model-mcp") -> None:
        self.container = container
        self.name = name
        self.mcp = self._create_fastmcp_instance()
        if self.mcp is not None:
            self.register()

    def _create_fastmcp_instance(self) -> Any | None:
        try:
            from fastmcp import FastMCP
        except ImportError:
            return None
        return FastMCP(self.name)

    def register(self) -> None:
        if self.mcp is None:
            return

        @self.mcp.tool()
        def health_check() -> dict[str, object]:
            return call_health_check(self.container.capability_use_case)

        @self.mcp.tool()
        def read_workspace_file(relative_path: str) -> dict[str, object]:
            return call_read_workspace_file(self.container.capability_use_case, relative_path)

        @self.mcp.tool()
        def invoke_local_model(prompt: str, model_id: str | None = None, max_tokens: int = 512) -> dict[str, object]:
            return call_invoke_local_model(
                self.container.capability_use_case,
                prompt,
                model_id=model_id,
                max_tokens=max_tokens,
            )

        @self.mcp.tool()
        def write_output_artifact(relative_path: str, content: str, overwrite: bool = False) -> dict[str, object]:
            return call_write_output_artifact(
                self.container.capability_use_case,
                relative_path,
                content,
                overwrite=overwrite,
            )

        @self.mcp.resource("model://information")
        def model_information() -> dict[str, object]:
            return read_model_information(self.container)

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, object]:
        args = arguments or {}
        use_case = self.container.capability_use_case
        if name == "health_check":
            return call_health_check(use_case)
        if name == "read_workspace_file":
            return call_read_workspace_file(use_case, str(args["relative_path"]))
        if name == "invoke_local_model":
            return call_invoke_local_model(
                use_case,
                str(args["prompt"]),
                model_id=args.get("model_id"),
                max_tokens=int(args.get("max_tokens", 512)),
            )
        if name == "write_output_artifact":
            return call_write_output_artifact(
                use_case,
                str(args["relative_path"]),
                str(args["content"]),
                overwrite=bool(args.get("overwrite", False)),
            )
        return {"status": "error", "error_code": "capability_not_found", "message": f"unknown tool: {name}"}


def create_fastmcp_server(container: ApplicationContainer) -> FastMCPServerAdapter:
    return FastMCPServerAdapter(container)
