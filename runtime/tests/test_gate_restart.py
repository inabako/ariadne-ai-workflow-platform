from __future__ import annotations

import pytest

from runtime.common import gate_restart


def test_build_gate_restart_defaults_restart_from_to_gate() -> None:
    result = gate_restart.build_gate_restart(
        "doctor-gate",
        restart_reason="failed-doctor-gate",
        repair_available=True,
        repair_command="aiwfctl doctor --repair-encoding --fail-on-warning",
        status_after_restart="pass",
    )

    assert result == {
        "schema_version": "1.0",
        "artifact_type": "gate-restart",
        "gate": "doctor-gate",
        "restart_from": "doctor-gate",
        "restart_reason": "failed-doctor-gate",
        "repair_available": True,
        "repair_command": "aiwfctl doctor --repair-encoding --fail-on-warning",
        "status_after_restart": "pass",
        "next_on_pass": "return-to-calling-workflow-after-gate",
        "next_on_fail": "stay-at-gate",
    }


def test_build_gate_restart_rejects_missing_gate() -> None:
    with pytest.raises(ValueError, match="gate is required"):
        gate_restart.build_gate_restart("")


def test_build_gate_restart_requires_repair_command_when_repair_is_available() -> None:
    with pytest.raises(ValueError, match="repair_command is required"):
        gate_restart.build_gate_restart("doctor-gate", repair_available=True)


def test_build_gate_restart_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="status_after_restart"):
        gate_restart.build_gate_restart("doctor-gate", status_after_restart="done")


def test_build_status_gate_restart_enables_repair_for_non_pass_status() -> None:
    result = gate_restart.build_status_gate_restart(
        "workflow-selection-gate",
        status="human-check-required",
        restart_reason="workflow-selection",
        repair_command="aiwfctl context init --workflow /x --work-id <work-id>",
    )

    assert result["restart_from"] == "workflow-selection-gate"
    assert result["repair_available"] is True
    assert result["status_after_restart"] == "pass"


def test_build_status_gate_restart_disables_repair_for_pass_status() -> None:
    result = gate_restart.build_status_gate_restart(
        "workflow-selection-gate",
        status="ready",
        restart_reason="workflow-selection",
        repair_command="aiwfctl context init --workflow /x --work-id <work-id>",
    )

    assert result["repair_available"] is False
    assert result["repair_command"] == ""
    assert result["status_after_restart"] == "pass"
