from __future__ import annotations

from .....application.dto.requests import InvokeLocalModelRequest, ReadWorkspaceFileRequest, WriteOutputArtifactRequest


def map_read_workspace_file_request(relative_path: str) -> ReadWorkspaceFileRequest:
    return ReadWorkspaceFileRequest(relative_path=relative_path)


def map_invoke_local_model_request(
    prompt: str,
    *,
    model_id: str | None = None,
    max_tokens: int = 512,
) -> InvokeLocalModelRequest:
    return InvokeLocalModelRequest(prompt=prompt, model_id=model_id, max_tokens=max_tokens)


def map_write_output_artifact_request(
    relative_path: str,
    content: str,
    *,
    overwrite: bool = False,
) -> WriteOutputArtifactRequest:
    return WriteOutputArtifactRequest(relative_path=relative_path, content=content, overwrite=overwrite)
