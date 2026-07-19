from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .capabilities import PROMPTS, RESOURCES, TOOLS
from .config import ServerConfig
from .config_loader import load_config_from_env
from .errors import CapabilityNotFoundError, MCPServerError
from .audit import AuditRecorder
from .input_validation import reject_binary_file, require_text_content
from .model_adapter import LocalModelAdapter, MockModelAdapter
from .security import WorkspacePathPolicy
from .tool_policy import ToolPolicy


class LocalModelMCPServer:
    def __init__(self, config: ServerConfig, model_adapter: LocalModelAdapter | None = None) -> None:
        self.config = config
        self.config.input_root.mkdir(parents=True, exist_ok=True)
        self.config.output_root.mkdir(parents=True, exist_ok=True)
        self.path_policy = WorkspacePathPolicy(config.input_root, config.output_root)
        self.model_adapter = model_adapter or MockModelAdapter()
        self.tool_policy = ToolPolicy()
        self.audit = AuditRecorder()

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
            return {"artifacts": [str(path.relative_to(self.config.output_root)) for path in self.config.output_root.rglob("*") if path.is_file()]}
        return dict(RESOURCES[uri])

    def list_tools(self) -> list[str]:
        return list(TOOLS)

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        try:
            self.tool_policy.assert_allowed(name)
            if name == "health_check":
                return {"status": "ok", "protocol_version": self.config.protocol_version}
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
        root = self.path_policy.input_path(relative_path)
        if not root.exists():
            return {"status": "ok", "files": []}
        files = [str(path.relative_to(self.config.input_root)) for path in root.rglob("*") if path.is_file()]
        return {"status": "ok", "files": sorted(files)}

    def _read_workspace_file(self, relative_path: str) -> dict[str, Any]:
        path = self.path_policy.input_path(relative_path)
        if path.stat().st_size > self.config.max_file_bytes:
            return {"status": "error", "error_code": "file_too_large", "message": "file exceeds configured max_file_bytes"}
        reject_binary_file(path)
        self.audit.record("read_workspace_file", relative_path, status="ok")
        return {"status": "ok", "relative_path": relative_path, "content": path.read_text(encoding="utf-8")}

    def _invoke_local_model(self, prompt: str, model_id: str | None, max_tokens: int) -> dict[str, Any]:
        response = self.model_adapter.invoke(prompt, model_id=model_id or self.config.model_id, max_tokens=max_tokens)
        return {"status": "ok", "model_id": response.model_id, "text": response.text, "tokens_used": response.tokens_used}

    def _write_output_artifact(self, relative_path: str, content: str, overwrite: bool) -> dict[str, Any]:
        path = self.path_policy.output_path(relative_path)
        if path.exists() and not overwrite:
            return {"status": "error", "error_code": "artifact_exists", "message": "set overwrite=true to replace existing artifact"}
        try:
            require_text_content(content, self.config.max_file_bytes)
        except MCPServerError as exc:
            return {"status": "error", "error_code": exc.code, "message": str(exc)}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.audit.record("write_output_artifact", relative_path, status="ok")
        return {"status": "ok", "relative_path": path.relative_to(self.config.output_root).as_posix()}


def create_server(base_dir: Path | None = None) -> LocalModelMCPServer:
    return LocalModelMCPServer(load_config_from_env(base_dir))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--health", action="store_true")
    args = parser.parse_args()
    server = create_server()
    if args.health:
        print(server.call_tool("health_check"))


if __name__ == "__main__":
    main()
