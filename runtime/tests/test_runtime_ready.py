from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl
from runtime.workflow import runtime_ready


def ready_status_payload(*, dirty_count: int = 0, last_problem: dict[str, object] | None = None) -> dict[str, object]:
    event_log = {
        "event_count": 5,
        "maintenance": {"status": "ok", "line_count": 5, "threshold": 1050, "keep_last": 1000},
        "last_problem_event": last_problem or {},
    }
    return {
        "repo": {"git": {"dirty_count": dirty_count}},
        "trace": {"status": "not-active", "stale": False, "trace_id": ""},
        "runtime": {"event_log": event_log},
        "doctor": {"status": "pass", "warning_count": 0},
        "environment": {
            "dependency_readiness": {
                "status": "ready",
                "required_missing_count": 0,
                "optional_missing_count": 0,
            }
        },
        "attention_summary": {"attention_reason_count": 0, "severity_counts": {}, "category_counts": {}},
        "attention_reasons": [],
        "next_actions": ["aiwfctl trace begin --workflow <workflow>", "aiwfctl doctor"],
    }


def test_runtime_ready_reports_ready_when_gates_pass(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runtime_ready.runtime_status, "collect_status", lambda repo_root, work_id="", view_mode="summary": ready_status_payload())
    monkeypatch.setattr(runtime_ready, "_spec_check", lambda repo_root, skip=False: {"status": "ok", "pytest_count": 2, "spec_count": 2})

    result = runtime_ready.build_ready_check(tmp_path)

    assert result["artifact_type"] == "runtime-ready-check"
    assert result["status"] == "ready"
    assert result["gates"]["doctor"]["status"] == "pass"
    assert result["gates"]["ut_spec_sync"]["status"] == "pass"


def test_runtime_ready_reports_attention_for_nonblocking_runtime_log_problem(monkeypatch, tmp_path: Path) -> None:
    problem = {
        "trace_id": "trace-problem",
        "sequence": "00002",
        "command": "env select",
        "status": "blocked",
    }
    payload = ready_status_payload(last_problem=problem)
    payload["attention_reasons"] = [{"id": "runtime-last-problem-event", "message": "problem", "next_action": "ack"}]
    payload["attention_summary"] = {"attention_reason_count": 1, "severity_counts": {"warning": 1}, "category_counts": {"runtime-log": 1}}
    monkeypatch.setattr(runtime_ready.runtime_status, "collect_status", lambda repo_root, work_id="", view_mode="summary": payload)
    monkeypatch.setattr(runtime_ready, "_spec_check", lambda repo_root, skip=False: {"status": "ok", "pytest_count": 2, "spec_count": 2})

    result = runtime_ready.build_ready_check(tmp_path)

    assert result["status"] == "attention"
    assert result["gates"]["runtime_log"]["status"] == "attention"
    assert result["attention_summary"]["attention_reason_count"] == 1


def test_runtime_ready_strict_promotes_attention_to_blocked(monkeypatch, tmp_path: Path) -> None:
    payload = ready_status_payload(dirty_count=2)
    payload["attention_reasons"] = [{"id": "git-dirty", "message": "dirty", "next_action": "review"}]
    payload["attention_summary"] = {"attention_reason_count": 1, "severity_counts": {"info": 1}, "category_counts": {"repository": 1}}
    monkeypatch.setattr(runtime_ready.runtime_status, "collect_status", lambda repo_root, work_id="", view_mode="summary": payload)
    monkeypatch.setattr(runtime_ready, "_spec_check", lambda repo_root, skip=False: {"status": "ok", "pytest_count": 2, "spec_count": 2})

    result = runtime_ready.build_ready_check(tmp_path, strict=True)

    assert result["status"] == "blocked"
    assert result["strict"] is True
    assert result["strict_blocked"] is True
    assert result["non_strict_status"] == "attention"


def test_ctl_ready_json_route_returns_runtime_ready_check(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        runtime_ready,
        "build_ready_check",
        lambda repo_root, work_id="", skip_spec_check=False, strict=False: {
            "schema_version": "1.0",
            "artifact_type": "runtime-ready-check",
            "status": "ready",
            "strict": strict,
            "strict_blocked": False,
            "non_strict_status": "ready",
            "repo_root": str(repo_root),
            "work_id": work_id,
            "gates": {},
            "attention_summary": {},
            "attention_reasons": [],
            "spec_check": {"status": "skipped" if skip_spec_check else "ok"},
            "next_actions": [],
        },
    )
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "ready",
            "--work-id",
            "issue-1",
            "--skip-spec-check",
            "--strict",
            "--output",
            "work/evidence/runtime-ready.json",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    payload = json.loads(output)
    assert payload["artifact_type"] == "runtime-ready-check"
    assert payload["work_id"] == "issue-1"
    assert payload["strict"] is True
    assert payload["spec_check"]["status"] == "skipped"
    assert payload["plan_output"] == "work/evidence/runtime-ready.json"
    saved = json.loads((tmp_path / "work" / "evidence" / "runtime-ready.json").read_text(encoding="utf-8"))
    assert saved["artifact_type"] == "runtime-ready-check"
    assert saved["written"] is True
