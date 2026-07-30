from __future__ import annotations

from .....application.ports.inbound import LocalModelCapabilityPort
from ..context import map_request_context
from ..mappers import (
    map_exception,
    map_invoke_local_model_request,
    map_read_workspace_file_request,
    map_tool_response,
    map_write_output_artifact_request,
)


def call_health_check(use_case: LocalModelCapabilityPort, raw_context=None) -> dict[str, object]:
    try:
        return map_tool_response(use_case.health_check(map_request_context(raw_context)))
    except Exception as exc:
        return map_exception(exc)


def call_read_workspace_file(use_case: LocalModelCapabilityPort, relative_path: str, raw_context=None) -> dict[str, object]:
    try:
        request = map_read_workspace_file_request(relative_path)
        return map_tool_response(use_case.read_workspace_file(request, map_request_context(raw_context)))
    except Exception as exc:
        return map_exception(exc)


def call_invoke_local_model(
    use_case: LocalModelCapabilityPort,
    prompt: str,
    *,
    model_id: str | None = None,
    max_tokens: int = 512,
    raw_context=None,
) -> dict[str, object]:
    try:
        request = map_invoke_local_model_request(prompt, model_id=model_id, max_tokens=max_tokens)
        return map_tool_response(use_case.invoke_local_model(request, map_request_context(raw_context)))
    except Exception as exc:
        return map_exception(exc)


def call_write_output_artifact(
    use_case: LocalModelCapabilityPort,
    relative_path: str,
    content: str,
    *,
    overwrite: bool = False,
    raw_context=None,
) -> dict[str, object]:
    try:
        request = map_write_output_artifact_request(relative_path, content, overwrite=overwrite)
        return map_tool_response(use_case.write_output_artifact(request, map_request_context(raw_context)))
    except Exception as exc:
        return map_exception(exc)
