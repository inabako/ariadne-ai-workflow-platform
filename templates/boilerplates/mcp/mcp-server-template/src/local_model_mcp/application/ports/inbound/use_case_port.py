from __future__ import annotations

from typing import Protocol

from ...dto.requests import InvokeLocalModelRequest, ReadWorkspaceFileRequest, RequestContext, WriteOutputArtifactRequest
from ...dto.responses import ToolResponse


class LocalModelCapabilityPort(Protocol):
    def health_check(self, context: RequestContext) -> ToolResponse:
        ...

    def list_workspace_files(self, relative_path: str, context: RequestContext) -> ToolResponse:
        ...

    def read_workspace_file(self, request: ReadWorkspaceFileRequest, context: RequestContext) -> ToolResponse:
        ...

    def invoke_local_model(self, request: InvokeLocalModelRequest, context: RequestContext) -> ToolResponse:
        ...

    def write_output_artifact(self, request: WriteOutputArtifactRequest, context: RequestContext) -> ToolResponse:
        ...
