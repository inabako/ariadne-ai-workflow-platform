from __future__ import annotations

from runtime.constants.runtime_values import SCHEMA_VERSION


from typing import Any

NEXT_ON_PASS_RETURN_TO_WORKFLOW = "return-to-calling-workflow-after-gate"
NEXT_ON_FAIL_STAY_AT_GATE = "stay-at-gate"
PASS_LIKE_STATUS = {
    "applied",
    "approved",
    "build_available",
    "completed",
    "dry-run",
    "not-required",
    "ok",
    "pass",
    "ready",
    "selected",
    "updated",
    "verified",
}


def build_gate_restart(
    gate: str,
    *,
    restart_from: str | None = None,
    restart_reason: str = "",
    repair_available: bool = False,
    repair_command: str = "",
    status_after_restart: str = "unknown",
) -> dict[str, Any]:
    if not gate:
        raise ValueError("gate is required.")
    if status_after_restart not in {"pass", "warning", "fail", "unknown"}:
        raise ValueError("status_after_restart must be pass, warning, fail, or unknown.")
    if repair_available and not repair_command:
        raise ValueError("repair_command is required when repair_available is true.")
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "gate-restart",
        "gate": gate,
        "restart_from": restart_from or gate,
        "restart_reason": restart_reason,
        "repair_available": repair_available,
        "repair_command": repair_command,
        "status_after_restart": status_after_restart,
        "next_on_pass": NEXT_ON_PASS_RETURN_TO_WORKFLOW,
        "next_on_fail": NEXT_ON_FAIL_STAY_AT_GATE,
    }


def build_status_gate_restart(
    gate: str,
    *,
    status: str,
    restart_reason: str = "",
    repair_command: str = "",
    pass_like_statuses: set[str] | None = None,
) -> dict[str, Any]:
    normalized_status = str(status).strip()
    passing_statuses = pass_like_statuses or PASS_LIKE_STATUS
    is_pass_like = normalized_status in passing_statuses
    repair_available = bool(repair_command) and not is_pass_like
    return build_gate_restart(
        gate,
        restart_reason=restart_reason or normalized_status,
        repair_available=repair_available,
        repair_command=repair_command if repair_available else "",
        status_after_restart="pass" if is_pass_like or repair_available else "fail",
    )
