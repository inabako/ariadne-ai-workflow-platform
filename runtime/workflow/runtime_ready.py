from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo  # noqa: E402
from runtime.constants.runtime_values import SCHEMA_VERSION  # noqa: E402
from runtime.tools import pytest_ut_spec_sync  # noqa: E402
from runtime.workflow import runtime_status  # noqa: E402


def _spec_check(repo_root: Path, *, skip: bool = False) -> dict[str, Any]:
    if skip:
        return {
            "status": "skipped",
            "spec_path": "docs/reference/runtime-pytest-ut/case-specification.md",
            "runtime_root": "runtime",
        }
    spec_path = repo_root / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    runtime_root = repo_root / "runtime"
    result = pytest_ut_spec_sync.check_spec(spec_path, runtime_root)
    return {
        **result,
        "spec_path": relative_to_repo(repo_root, spec_path),
        "runtime_root": relative_to_repo(repo_root, runtime_root),
    }


def _gate_statuses(status_payload: dict[str, Any], spec_result: dict[str, Any]) -> dict[str, Any]:
    trace = status_payload.get("trace", {})
    event_log = status_payload.get("runtime", {}).get("event_log", {})
    readiness = status_payload.get("environment", {}).get("dependency_readiness", {})
    doctor = status_payload.get("doctor", {})
    return {
        "git": {
            "status": "attention" if int(status_payload.get("repo", {}).get("git", {}).get("dirty_count", 0) or 0) else "pass",
            "dirty_count": int(status_payload.get("repo", {}).get("git", {}).get("dirty_count", 0) or 0),
        },
        "trace": {
            "status": "pass"
            if trace.get("status") == "not-active" and not trace.get("stale")
            else "blocked"
            if trace.get("status") == "invalid" or trace.get("stale")
            else "attention",
            "trace_status": trace.get("status", ""),
            "trace_id": trace.get("trace_id", ""),
        },
        "runtime_log": {
            "status": "attention"
            if event_log.get("last_problem_event") or event_log.get("maintenance", {}).get("status") == "attention"
            else "pass",
            "event_count": int(event_log.get("event_count", 0) or 0),
            "maintenance": event_log.get("maintenance", {}),
            "last_problem_event": event_log.get("last_problem_event", {}),
        },
        "doctor": {
            "status": "pass" if doctor.get("status") == "pass" else "blocked",
            "doctor_status": doctor.get("status", ""),
            "warning_count": int(doctor.get("warning_count", 0) or 0),
        },
        "dependency_readiness": {
            "status": "pass" if readiness.get("status") == "ready" else "blocked",
            "readiness_status": readiness.get("status", ""),
            "required_missing_count": int(readiness.get("required_missing_count", 0) or 0),
            "optional_missing_count": int(readiness.get("optional_missing_count", 0) or 0),
        },
        "ut_spec_sync": {
            "status": "skipped" if spec_result.get("status") == "skipped" else "pass" if spec_result.get("status") == "ok" else "blocked",
            "spec_status": spec_result.get("status", ""),
            "pytest_count": int(spec_result.get("pytest_count", 0) or 0),
            "spec_count": int(spec_result.get("spec_count", 0) or 0),
        },
    }


def build_ready_check(repo_root: Path, *, work_id: str = "", skip_spec_check: bool = False, strict: bool = False) -> dict[str, Any]:
    status_payload = runtime_status.collect_status(repo_root, work_id=work_id, view_mode="summary")
    spec_result = _spec_check(repo_root, skip=skip_spec_check)
    gates = _gate_statuses(status_payload, spec_result)
    gate_values = [str(item.get("status", "")) for item in gates.values() if isinstance(item, dict)]
    if "blocked" in gate_values:
        status = "blocked"
    elif "attention" in gate_values:
        status = "attention"
    else:
        status = "ready"
    non_strict_status = status
    strict_blocked = bool(strict and status == "attention")
    if strict_blocked:
        status = "blocked"
    next_actions = list(status_payload.get("next_actions", []))
    if gates["ut_spec_sync"]["status"] == "blocked":
        next_actions.insert(0, "aiwfctl tools spec-check")
        next_actions.insert(1, "aiwfctl doctor --repair-spec-index --json")
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-ready-check",
        "status": status,
        "strict": strict,
        "strict_blocked": strict_blocked,
        "non_strict_status": non_strict_status,
        "repo_root": str(repo_root.resolve()),
        "work_id": work_id,
        "gates": gates,
        "attention_summary": status_payload.get("attention_summary", {}),
        "attention_reasons": status_payload.get("attention_reasons", []),
        "spec_check": spec_result,
        "next_actions": list(dict.fromkeys(next_actions)),
    }


def format_ready_check(result: dict[str, Any]) -> str:
    lines = [
        "Runtime Ready Check",
        "",
        f"Status  : {result.get('status', '')}",
        f"Strict  : {str(result.get('strict', False)).lower()}",
        f"Repo    : {result.get('repo_root', '')}",
        f"Work ID : {result.get('work_id', '') or '-'}",
        "",
        "Gates",
    ]
    gates = result.get("gates", {})
    if isinstance(gates, dict):
        for gate_id, gate in gates.items():
            if isinstance(gate, dict):
                lines.append(f"  - {gate_id}: {gate.get('status', '')}")
    reasons = result.get("attention_reasons", [])
    if reasons:
        lines.extend(["", "Attention Reasons"])
        for reason in reasons:
            if isinstance(reason, dict):
                lines.append(f"  - {reason.get('id', '')}: {reason.get('message', '')}")
                if reason.get("next_action"):
                    lines.append(f"    next: {reason.get('next_action', '')}")
    lines.extend(["", "Next Actions"])
    lines.extend(f"  - {action}" for action in result.get("next_actions", []))
    plan_output = str(result.get("plan_output", "") or "")
    if plan_output:
        lines.extend(["", f"Output  : {plan_output}"])
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check whether Ariadne Runtime is ready for a workflow run.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--work-id", default="")
    parser.add_argument("--skip-spec-check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    result = build_ready_check(repo_root, work_id=args.work_id, skip_spec_check=args.skip_spec_check, strict=args.strict)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_ready_check(result), end="")
    return 0 if result.get("status") == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
