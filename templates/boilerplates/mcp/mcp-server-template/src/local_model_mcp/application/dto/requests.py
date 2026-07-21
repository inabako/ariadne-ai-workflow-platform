from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class RequestContext:
    request_id: str = ""
    trace_id: str = ""
    actor_id: str | None = None
    client_name: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReadWorkspaceFileRequest:
    relative_path: str


@dataclass(frozen=True)
class InvokeLocalModelRequest:
    prompt: str
    model_id: str | None = None
    max_tokens: int = 512


@dataclass(frozen=True)
class WriteOutputArtifactRequest:
    relative_path: str
    content: str
    overwrite: bool = False
