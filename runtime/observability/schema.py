from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from runtime.constants.runtime_values import (
    COST_AMOUNT_DEFAULT,
    NON_NEGATIVE_FLOAT_DEFAULT,
    NON_NEGATIVE_INT_DEFAULT,
    SCHEMA_VERSION,
)


ARTIFACT_TYPE = "runtime-metrics"
EVENT_NAMES = {
    "workflow_started",
    "workflow_completed",
    "workflow_failed",
    "agent_started",
    "agent_completed",
    "human_check_required",
    "evidence_generated",
    "runtime_error",
    "token_usage_recorded",
    "context_usage_recorded",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _non_negative_int(value: Any, default: int = NON_NEGATIVE_INT_DEFAULT) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(parsed, NON_NEGATIVE_INT_DEFAULT)


def _non_negative_float(value: Any, default: float = NON_NEGATIVE_FLOAT_DEFAULT) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(parsed, NON_NEGATIVE_FLOAT_DEFAULT)


def token_usage(
    *,
    input_tokens: Any = NON_NEGATIVE_INT_DEFAULT,
    output_tokens: Any = NON_NEGATIVE_INT_DEFAULT,
    total_tokens: Any | None = None,
    estimated: bool = True,
) -> dict[str, Any]:
    input_count = _non_negative_int(input_tokens)
    output_count = _non_negative_int(output_tokens)
    total_count = _non_negative_int(total_tokens, input_count + output_count) if total_tokens is not None else input_count + output_count
    return {
        "input": input_count,
        "output": output_count,
        "total": total_count,
        "estimated": bool(estimated),
    }


def cost_usage(
    *,
    input_cost: Any = COST_AMOUNT_DEFAULT,
    output_cost: Any = COST_AMOUNT_DEFAULT,
    total_cost: Any | None = None,
    currency: str = "USD",
    estimated: bool = True,
) -> dict[str, Any]:
    input_amount = _non_negative_float(input_cost)
    output_amount = _non_negative_float(output_cost)
    total_amount = _non_negative_float(total_cost, input_amount + output_amount) if total_cost is not None else input_amount + output_amount
    return {
        "input_cost": input_amount,
        "output_cost": output_amount,
        "total_cost": total_amount,
        "currency": currency or "USD",
        "estimated": bool(estimated),
    }


def context_usage(
    *,
    selected_context_count: Any = NON_NEGATIVE_INT_DEFAULT,
    estimated_context_tokens: Any = NON_NEGATIVE_INT_DEFAULT,
    rag_reference_count: Any = NON_NEGATIVE_INT_DEFAULT,
    dispatcher_route: str = "",
) -> dict[str, Any]:
    return {
        "selected_context_count": _non_negative_int(selected_context_count),
        "estimated_context_tokens": _non_negative_int(estimated_context_tokens),
        "rag_reference_count": _non_negative_int(rag_reference_count),
        "dispatcher_route": dispatcher_route,
    }


def runtime_status(
    *,
    retry_count: Any = NON_NEGATIVE_INT_DEFAULT,
    human_check_required: bool = False,
    evidence_generated: bool = False,
    error_count: Any = NON_NEGATIVE_INT_DEFAULT,
) -> dict[str, Any]:
    return {
        "retry_count": _non_negative_int(retry_count),
        "human_check_required": bool(human_check_required),
        "evidence_generated": bool(evidence_generated),
        "error_count": _non_negative_int(error_count),
    }


def runtime_metric_record(
    *,
    event: str,
    workflow_id: str = "",
    workflow_name: str = "",
    agent_name: str = "",
    started_at: str = "",
    ended_at: str = "",
    duration_ms: Any = NON_NEGATIVE_INT_DEFAULT,
    token: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    runtime: dict[str, Any] | None = None,
    model: dict[str, Any] | None = None,
    cost: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    normalized_event = event if event in EVENT_NAMES else "runtime_error"
    record = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "event": normalized_event,
        "timestamp": timestamp or utc_now_iso(),
        "workflow_id": workflow_id,
        "workflow_name": workflow_name,
        "agent_name": agent_name,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_ms": _non_negative_int(duration_ms),
        "token_usage": token or token_usage(),
        "context": context or context_usage(),
        "runtime": runtime or runtime_status(),
        "model": model or {
            "provider": "",
            "name": "",
            "pricing_estimated": True,
        },
        "cost": cost or cost_usage(),
        "metadata": metadata or {},
    }
    return record
