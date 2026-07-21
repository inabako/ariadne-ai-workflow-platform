from __future__ import annotations

from ...config import ServerConfig
from ...errors import MCPServerError
from ..dto.requests import InvokeLocalModelRequest, ReadWorkspaceFileRequest, RequestContext, WriteOutputArtifactRequest
from ..dto.responses import ToolResponse
from ..ports.outbound.model_port import ModelPort
from ..ports.outbound.workspace_port import WorkspacePort


class LocalModelCapabilityUseCase:
    def __init__(self, *, config: ServerConfig, workspace: WorkspacePort, model: ModelPort) -> None:
        self.config = config
        self.workspace = workspace
        self.model = model

    def health_check(self, context: RequestContext) -> ToolResponse:
        return ToolResponse.ok(protocol_version=self.config.protocol_version)

    def list_workspace_files(self, relative_path: str, context: RequestContext) -> ToolResponse:
        return ToolResponse.ok(files=self.workspace.list_input_files(relative_path))

    def read_workspace_file(self, request: ReadWorkspaceFileRequest, context: RequestContext) -> ToolResponse:
        return self._guard(lambda: ToolResponse.ok(relative_path=request.relative_path, content=self.workspace.read_input_text(request.relative_path, max_file_bytes=self.config.max_file_bytes)))

    def invoke_local_model(self, request: InvokeLocalModelRequest, context: RequestContext) -> ToolResponse:
        response = self.model.invoke(
            request.prompt,
            model_id=request.model_id or self.config.model_id,
            max_tokens=request.max_tokens,
        )
        return ToolResponse.ok(model_id=response.model_id, text=response.text, tokens_used=response.tokens_used)

    def write_output_artifact(self, request: WriteOutputArtifactRequest, context: RequestContext) -> ToolResponse:
        return self._guard(
            lambda: ToolResponse.ok(
                relative_path=self.workspace.write_output_text(
                    request.relative_path,
                    request.content,
                    overwrite=request.overwrite,
                    max_file_bytes=self.config.max_file_bytes,
                )
            )
        )

    def _guard(self, action) -> ToolResponse:
        try:
            return action()
        except MCPServerError as exc:
            return ToolResponse.error(error_code=exc.code, message=str(exc))
