from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


SCHEMA_VERSION = "1.0"
TRACE_ID_HEX_LENGTH = 24


class WorkflowStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_human"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class EvidenceStatus(StrEnum):
    AVAILABLE = "available"
    MISSING = "missing"
    BLOCKED = "blocked"


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def generate_trace_id() -> str:
    return secrets.token_hex(TRACE_ID_HEX_LENGTH // 2)


def validate_trace_id(trace_id: str) -> None:
    if len(trace_id) != TRACE_ID_HEX_LENGTH:
        raise ValueError("trace_id must be 24 lowercase hexadecimal characters.")
    try:
        int(trace_id, 16)
    except ValueError as exc:
        raise ValueError("trace_id must be 24 lowercase hexadecimal characters.") from exc
    if trace_id != trace_id.lower():
        raise ValueError("trace_id must be lowercase.")


def reject_secret_keys(payload: dict[str, Any]) -> None:
    forbidden_markers = ("secret", "token", "password", "api_key", "credential")
    for key in payload:
        normalized = key.lower().replace("-", "_")
        if any(marker in normalized for marker in forbidden_markers):
            raise ValueError(f"Secret-like field is not allowed in runtime contract: {key}")


@dataclass(frozen=True)
class WorkflowRequest:
    workflow_id: str
    workflow_type: str
    input: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    trace_id: str = field(default_factory=generate_trace_id)
    requested_at: str = field(default_factory=utc_timestamp)

    def to_contract(self) -> dict[str, Any]:
        validate_trace_id(self.trace_id)
        reject_secret_keys(self.input)
        reject_secret_keys(self.context)
        return {
            "schema_version": SCHEMA_VERSION,
            "workflow_id": self.workflow_id,
            "trace_id": self.trace_id,
            "workflow_type": self.workflow_type,
            "input": self.input,
            "context": self.context,
            "constraints": self.constraints,
            "requested_at": self.requested_at,
        }


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    workflow_id: str
    trace_id: str
    source: str
    type: str
    path: str
    status: EvidenceStatus = EvidenceStatus.AVAILABLE
    created_at: str = field(default_factory=utc_timestamp)

    def to_contract(self) -> dict[str, Any]:
        validate_trace_id(self.trace_id)
        return {
            "schema_version": SCHEMA_VERSION,
            "evidence_id": self.evidence_id,
            "trace_id": self.trace_id,
            "workflow_id": self.workflow_id,
            "source": self.source,
            "type": self.type,
            "path": self.path,
            "status": self.status.value,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class RuntimeErrorRecord:
    error_id: str
    workflow_id: str
    trace_id: str
    code: str
    message: str
    retryable: bool = False
    framework_metadata: dict[str, Any] = field(default_factory=dict)

    def to_contract(self) -> dict[str, Any]:
        validate_trace_id(self.trace_id)
        return {
            "schema_version": SCHEMA_VERSION,
            "error_id": self.error_id,
            "trace_id": self.trace_id,
            "workflow_id": self.workflow_id,
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
            "framework_metadata": self.framework_metadata,
        }


@dataclass(frozen=True)
class WorkflowResult:
    workflow_id: str
    trace_id: str
    status: WorkflowStatus
    outputs: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    next_action: str | None = None
    completed_at: str | None = None

    def to_contract(self) -> dict[str, Any]:
        validate_trace_id(self.trace_id)
        return {
            "schema_version": SCHEMA_VERSION,
            "workflow_id": self.workflow_id,
            "trace_id": self.trace_id,
            "status": self.status.value,
            "outputs": self.outputs,
            "evidence": self.evidence,
            "errors": self.errors,
            "next_action": self.next_action,
            "completed_at": self.completed_at,
        }
