from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .application.dto.requests import InvokeLocalModelRequest, ReadWorkspaceFileRequest, RequestContext, WriteOutputArtifactRequest
from .bootstrap import create_application, create_application_container
from .capabilities import PROMPTS, RESOURCES, TOOLS
from .config import ServerConfig
from .errors import CapabilityNotFoundError, MCPServerError
from .model_adapter import LocalModelAdapter, MockModelAdapter


class LocalModelMCPServer:
    def __init__(self, config: ServerConfig, model_adapter: LocalModelAdapter | None = None) -> None:
        self.container = create_application_container(config, model_adapter=model_adapter or MockModelAdapter())
        self.config = self.container.config
        self.path_policy = self.container.path_policy
        self.tool_policy = self.container.tool_policy
        self.audit = self.container.audit

    def list_prompts(self) -> list[str]:
        return sorted(PROMPTS)

    def get_prompt(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        if name not in PROMPTS:
            raise CapabilityNotFoundError(f"unknown prompt: {name}")
        return PROMPTS[name].format(**(arguments or {}))

    def list_resources(self) -> list[str]:
        return sorted(RESOURCES)

    def read_resource(self, uri: str) -> dict[str, Any]:
        if uri not in RESOURCES:
            raise CapabilityNotFoundError(f"unknown resource: {uri}")
        if uri == "model://information":
            return {**RESOURCES[uri], "model_id": self.config.model_id}
        if uri == "artifact://outputs":
            return {"artifacts": self.container.capability_use_case.workspace.list_output_artifacts()}
        return dict(RESOURCES[uri])

    def list_tools(self) -> list[str]:
        return list(TOOLS)

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        try:
            self.tool_policy.assert_allowed(name)
            if name == "health_check":
                return self.container.capability_use_case.health_check(RequestContext()).to_dict()
            if name == "list_workspace_files":
                return self._list_workspace_files(args.get("relative_path", "."))
            if name == "read_workspace_file":
                return self._read_workspace_file(args["relative_path"])
            if name == "invoke_local_model":
                return self._invoke_local_model(args["prompt"], args.get("model_id"), int(args.get("max_tokens", 512)))
            if name == "write_output_artifact":
                return self._write_output_artifact(args["relative_path"], args["content"], bool(args.get("overwrite", False)))
            raise CapabilityNotFoundError(f"unknown tool: {name}")
        except MCPServerError as exc:
            self.audit.record("tool_call", name, status="error", metadata={"error_code": exc.code})
            return {"status": "error", "error_code": exc.code, "message": str(exc)}

    def _list_workspace_files(self, relative_path: str) -> dict[str, Any]:
        return self.container.capability_use_case.list_workspace_files(relative_path, RequestContext()).to_dict()

    def _read_workspace_file(self, relative_path: str) -> dict[str, Any]:
        return self.container.capability_use_case.read_workspace_file(
            ReadWorkspaceFileRequest(relative_path=relative_path),
            RequestContext(),
        ).to_dict()

    def _invoke_local_model(self, prompt: str, model_id: str | None, max_tokens: int) -> dict[str, Any]:
        return self.container.capability_use_case.invoke_local_model(
            InvokeLocalModelRequest(prompt=prompt, model_id=model_id, max_tokens=max_tokens),
            RequestContext(),
        ).to_dict()

    def _write_output_artifact(self, relative_path: str, content: str, overwrite: bool) -> dict[str, Any]:
        return self.container.capability_use_case.write_output_artifact(
            WriteOutputArtifactRequest(
                relative_path=relative_path,
                content=content,
                overwrite=overwrite,
            ),
            RequestContext(),
        ).to_dict()


def create_server(base_dir: Path | None = None) -> LocalModelMCPServer:
    container = create_application(base_dir)
    server = LocalModelMCPServer(container.config)
    server.container = container
    server.config = container.config
    server.path_policy = container.path_policy
    server.tool_policy = container.tool_policy
    server.audit = container.audit
    return server


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--health", action="store_true")
    args = parser.parse_args()
    server = create_server()
    if args.health:
        print(server.call_tool("health_check"))


if __name__ == "__main__":
    main()
