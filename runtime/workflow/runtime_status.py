from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo  # noqa: E402
from runtime.constants.paths import (  # noqa: E402
    DUCKDB_DEFAULT_PATH,
    GENERATED_CHUNKS,
    GENERATED_INDEXES,
    GENERATED_NORMALIZED,
    GENERATED_OPTIMIZED_CHUNKS,
    GENERATED_RETRIEVAL,
    KNOWLEDGE_SOURCE_REPO,
    KNOWLEDGE_SOURCE_REPO_NAME,
    REGISTRY_DB_PATH,
    SEMANTIC_HINT_BACKUPS,
    SOURCE_SEMANTIC_HINTS,
)
from runtime.constants.runtime_values import SCHEMA_VERSION  # noqa: E402
from runtime.constants.workflow_limits import (  # noqa: E402
    RUNTIME_LOG_DEFAULT_KEEP_LAST,
    RUNTIME_LOG_MAINTENANCE_GRACE_EVENTS,
    RUNTIME_STATUS_EVENT_READ_LIMIT,
    RUNTIME_STATUS_WORK_PREVIEW_LIMIT,
)
from runtime.constants.workspace import WORK_ROOT, work_dir_for_id, work_root_for_repo  # noqa: E402
from runtime.environment import preflight  # noqa: E402
from runtime.observability import logger as runtime_event_logger  # noqa: E402
from runtime.workflow import runtime_log  # noqa: E402
from runtime.workflow import runtime_trace  # noqa: E402
from runtime.workflow import workflow_doctor  # noqa: E402
from runtime.workflow import workflow_state  # noqa: E402


RUNTIME_STATUS_NOISE_COMMANDS = (
    "status",
    "help",
    "trace status",
    "trace show",
)


def _path_status(repo_root: Path, path: Path) -> dict[str, Any]:
    absolute = path if path.is_absolute() else repo_root / path
    return {
        "path": relative_to_repo(repo_root, absolute),
        "exists": absolute.exists(),
        "is_dir": absolute.is_dir(),
        "is_file": absolute.is_file(),
    }


def _git_value(repo_root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def git_status(repo_root: Path) -> dict[str, Any]:
    git_dir = repo_root / ".git"
    present = git_dir.exists()
    if not present:
        return {
            "present": False,
            "branch": "",
            "head": "",
            "dirty_count": 0,
        }
    porcelain = _git_value(repo_root, "status", "--porcelain")
    return {
        "present": True,
        "branch": _git_value(repo_root, "branch", "--show-current"),
        "head": _git_value(repo_root, "rev-parse", "--short", "HEAD"),
        "dirty_count": len([line for line in porcelain.splitlines() if line.strip()]),
    }


def _runtime_event_parts(line: str) -> tuple[str, str, str, dict[str, Any]]:
    timestamp, trace_id, sequence, payload = (line.split(" | ", 3) + ["", "", "", ""])[:4]
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        data = {}
    return timestamp, trace_id, sequence, data if isinstance(data, dict) else {}


def _runtime_event_view(line: str) -> dict[str, Any]:
    timestamp, trace_id, sequence, payload = _runtime_event_parts(line)
    output = payload.get("output", {}) if isinstance(payload.get("output"), dict) else {}
    diagnostics = payload.get("diagnostics", {}) if isinstance(payload.get("diagnostics"), dict) else {}
    input_payload = payload.get("input", {}) if isinstance(payload.get("input"), dict) else {}
    return {
        "timestamp": timestamp,
        "trace_id": trace_id,
        "sequence": sequence,
        "event": payload.get("event", ""),
        "command": payload.get("command", ""),
        "workflow": payload.get("workflow", ""),
        "level": payload.get("level", ""),
        "status": output.get("status", ""),
        "reason": output.get("reason", ""),
        "exit_code": output.get("exit_code", ""),
        "next_action": diagnostics.get("next_action", ""),
        "resume_command": diagnostics.get("resume_command", ""),
        "work_id": input_payload.get("work_id", "") or payload.get("work_id", ""),
    }


def _is_status_noise_event(event: dict[str, Any]) -> bool:
    command = str(event.get("command", "") or "").strip()
    if command in RUNTIME_STATUS_NOISE_COMMANDS:
        return True
    return command.startswith("help ") or command.startswith("log ") or command.startswith("trace show ")


def _is_problem_event(event: dict[str, Any]) -> bool:
    status = str(event.get("status", "") or "")
    event_name = str(event.get("event", "") or "")
    level = str(event.get("level", "") or "")
    exit_code = event.get("exit_code", "")
    if event_name == "runtime_command_failed":
        return True
    if status and status != "completed":
        return True
    if isinstance(exit_code, int) and exit_code != 0:
        return True
    return level in {"error", "warning"} and event_name != "runtime_command_started"


def _latest_matching_event(lines: list[str], predicate: Any) -> dict[str, Any]:
    for line in reversed(lines):
        event = _runtime_event_view(line)
        if event.get("event") and predicate(event):
            return event
    return {}


def runtime_log_status(repo_root: Path) -> dict[str, Any]:
    path = runtime_event_logger.runtime_event_log_path(repo_root)
    if not path.exists():
        return {
            "path": relative_to_repo(repo_root, path),
            "exists": False,
            "event_count": 0,
            "maintenance": runtime_log.log_maintenance_status(0, keep_last=RUNTIME_LOG_DEFAULT_KEEP_LAST),
            "acknowledgement_candidates": [],
            "last_event": {},
        }
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    recent = lines[-RUNTIME_STATUS_EVENT_READ_LIMIT:]
    last_event: dict[str, Any] = {}
    if recent:
        last_event = _runtime_event_view(recent[-1])
    acknowledged_keys = runtime_log.acknowledged_problem_keys(repo_root)
    candidates = acknowledgement_candidates(recent, acknowledged_keys)
    return {
        "path": relative_to_repo(repo_root, path),
        "exists": True,
        "event_count": len(lines),
        "maintenance": runtime_log.log_maintenance_status(len(lines), keep_last=RUNTIME_LOG_DEFAULT_KEEP_LAST),
        "last_event": last_event,
        "last_relevant_event": _latest_matching_event(recent, lambda event: not _is_status_noise_event(event)),
        "last_problem_event": _latest_matching_event(
            recent,
            lambda event: not _is_status_noise_event(event)
            and _is_problem_event(event)
            and runtime_log.problem_ack_key(event) not in acknowledged_keys,
        ),
        "acknowledgement_candidates": candidates,
        "acknowledged_problem_count": len(acknowledged_keys),
    }


def active_trace_status(repo_root: Path) -> dict[str, Any]:
    return runtime_trace.inspect_active_trace(repo_root)


def related_trace_status(repo_root: Path, work_id: str) -> dict[str, Any]:
    path = runtime_event_logger.runtime_event_log_path(repo_root)
    result: dict[str, Any] = {
        "work_id": work_id,
        "trace_count": 0,
        "latest_trace_id": "",
        "traces": [],
    }
    if not work_id or not path.exists():
        return result
    grouped: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        event = _runtime_event_view(line)
        trace_id = str(event.get("trace_id", "") or "")
        if not trace_id or str(event.get("work_id", "") or "") != work_id:
            continue
        item = grouped.setdefault(
            trace_id,
            {
                "trace_id": trace_id,
                "work_id": work_id,
                "event_count": 0,
                "problem_count": 0,
                "last_event": {},
                "last_problem_event": {},
            },
        )
        item["event_count"] += 1
        item["last_event"] = event
        if _is_problem_event(event):
            item["problem_count"] += 1
            item["last_problem_event"] = event
    traces = sorted(grouped.values(), key=lambda item: str(item.get("last_event", {}).get("timestamp", "")), reverse=True)
    result["trace_count"] = len(traces)
    result["latest_trace_id"] = str(traces[0].get("trace_id", "") or "") if traces else ""
    result["traces"] = traces[:RUNTIME_STATUS_WORK_PREVIEW_LIMIT]
    return result


def _work_dirs(repo_root: Path) -> list[Path]:
    work_root = work_root_for_repo(repo_root)
    if not work_root.exists():
        return []
    return [
        path
        for path in work_root.iterdir()
        if path.is_dir() and path.name not in {"db", "requirements"}
    ]


def _work_state(repo_root: Path, work_dir: Path) -> dict[str, Any]:
    state_path = workflow_state.state_path_for_work_dir(work_dir)
    state = read_json(state_path, default={}) if state_path.exists() else {}
    return {
        "work_id": work_dir.name,
        "path": relative_to_repo(repo_root, work_dir),
        "state_path": relative_to_repo(repo_root, state_path),
        "state_exists": state_path.exists(),
        "workflow": state.get("workflow", "") if isinstance(state, dict) else "",
        "phase": state.get("phase", "") if isinstance(state, dict) else "",
        "status": state.get("status", "unknown") if isinstance(state, dict) else "unknown",
        "updated_at": state.get("updated_at", "") if isinstance(state, dict) else "",
    }


def work_status(repo_root: Path, work_id: str = "") -> dict[str, Any]:
    if work_id:
        target = work_dir_for_id(repo_root, work_id)
        items = [_work_state(repo_root, target)] if target.exists() else []
        return {
            "root": _path_status(repo_root, WORK_ROOT),
            "work_id": work_id,
            "work_area_count": len(_work_dirs(repo_root)),
            "selected": items[0] if items else {
                "work_id": work_id,
                "path": f"work/{work_id}",
                "state_exists": False,
                "status": "missing",
            },
            "recent": [],
        }

    dirs = sorted(_work_dirs(repo_root), key=lambda path: path.stat().st_mtime, reverse=True)
    recent = [_work_state(repo_root, path) for path in dirs[:RUNTIME_STATUS_WORK_PREVIEW_LIMIT]]
    active = [
        item
        for item in recent
        if item.get("status") not in {"complete", "missing", "unknown"}
    ]
    return {
        "root": _path_status(repo_root, WORK_ROOT),
        "work_id": "",
        "work_area_count": len(dirs),
        "active_recent_count": len(active),
        "selected": {},
        "recent": recent,
    }


def knowledge_status(repo_root: Path) -> dict[str, Any]:
    paths = {
        "source_repo": KNOWLEDGE_SOURCE_REPO,
        "rag": KNOWLEDGE_SOURCE_REPO / "rag",
        "semantic_hints_source": SOURCE_SEMANTIC_HINTS,
        "semantic_hints_backup": SEMANTIC_HINT_BACKUPS,
        "normalized": GENERATED_NORMALIZED,
        "chunks": GENERATED_CHUNKS,
        "optimized_chunks": GENERATED_OPTIMIZED_CHUNKS,
        "indexes": GENERATED_INDEXES,
        "retrieval": GENERATED_RETRIEVAL,
        "duckdb": DUCKDB_DEFAULT_PATH,
        "registry_db": REGISTRY_DB_PATH,
    }
    return {
        "source_repo_name": KNOWLEDGE_SOURCE_REPO_NAME,
        "paths": {key: _path_status(repo_root, path) for key, path in paths.items()},
    }


def _check_status(check: Any) -> dict[str, Any]:
    data = check.to_dict() if hasattr(check, "to_dict") else dict(check)
    required = bool(data.get("required", False))
    ok = bool(data.get("ok", False))
    data["status"] = "ready" if ok else "missing-required" if required else "missing-optional"
    return data


def dependency_readiness(repo_root: Path) -> dict[str, Any]:
    checks = [
        preflight.which_check("git", required=True, install_hint="Install Git, then verify with git --version."),
        preflight.uv_runtime_check(repo_root, required=True),
        preflight.which_check("docker", required=False, install_hint="Install Docker Desktop when local container rehearsal is required."),
        preflight.docker_daemon_check(required=False),
        preflight.github_cli_version_check(required=False),
        preflight.github_cli_auth_check(repo_root, required=False),
        preflight.which_check("reuse", required=False, install_hint="Install REUSE for local license lint rehearsal."),
        preflight.act_cli_check(required=False),
        preflight.path_check(
            repo_root / ".github" / "workflows" / "scancode.yml",
            check_id="path:scancode-workflow",
            label="ScanCode workflow",
            required=False,
            install_hint="Add .github/workflows/scancode.yml before ScanCode GitHub Actions rehearsal.",
        ),
        preflight.path_check(
            repo_root / DUCKDB_DEFAULT_PATH,
            check_id="path:duckdb-read-model",
            label="DuckDB read model",
            required=False,
            install_hint="Run aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset.",
        ),
    ]
    entries = [_check_status(check) for check in checks]
    required_missing = [item for item in entries if item.get("required") and not item.get("ok")]
    optional_missing = [item for item in entries if not item.get("required") and not item.get("ok")]
    return {
        "artifact_type": "runtime-dependency-readiness",
        "status": "ready" if not required_missing else "attention",
        "check_count": len(entries),
        "ready_count": len([item for item in entries if item.get("ok")]),
        "required_missing_count": len(required_missing),
        "optional_missing_count": len(optional_missing),
        "checks": entries,
    }


def doctor_status(repo_root: Path) -> dict[str, Any]:
    try:
        result = workflow_doctor.run(
            argparse.Namespace(
                repo_root=str(repo_root),
                fail_on_warning=False,
                skip_ut_spec_sync=False,
                repair_encoding=False,
                repair_spec_index=False,
                dry_run=False,
                encoding_paths=None,
                encoding_extensions=None,
            )
        )
    except Exception as exc:
        return {
            "status": "unavailable",
            "warning_count": 0,
            "warning_summary": {},
            "warnings": [],
            "error": str(exc),
        }
    return {
        "status": result.get("status", ""),
        "warning_count": int(result.get("warning_count", 0) or 0),
        "warning_summary": result.get("warning_summary", {}),
        "warnings": result.get("warnings", []),
    }


def _duckdb_rebuild_next_action(repo_root: Path) -> str:
    findings = workflow_doctor.duckdb_read_model_findings(repo_root)
    if not findings:
        return ""
    return workflow_doctor.warning_guidance("rag-duckdb-read-model-missing", findings).get("repair_command", "")


def acknowledge_problem_command(event: dict[str, Any]) -> str:
    trace_id = str(event.get("trace_id", "") or "")
    sequence = str(event.get("sequence", "") or "")
    if not trace_id or not sequence:
        return ""
    return (
        "aiwfctl log acknowledge-problem "
        f"--trace-id {trace_id} --sequence {sequence} "
        '--reason "known and reviewed"'
    )


def acknowledgement_candidates(
    recent_lines: list[str],
    acknowledged_keys: set[str],
    *,
    limit: int = RUNTIME_STATUS_WORK_PREVIEW_LIMIT,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in reversed(recent_lines):
        event = _runtime_event_view(line)
        if not event.get("event"):
            continue
        if _is_status_noise_event(event) or not _is_problem_event(event):
            continue
        ack_key = runtime_log.problem_ack_key(event)
        if ack_key in acknowledged_keys or ack_key in seen:
            continue
        seen.add(ack_key)
        candidates.append(
            {
                **event,
                "acknowledge_command": acknowledge_problem_command(event),
            }
        )
        if len(candidates) >= limit:
            break
    return candidates


def next_actions(repo_root: Path, status: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    trace_status = status["trace"].get("status")
    if trace_status == "active":
        actions.append("aiwfctl trace status")
    elif trace_status == "invalid":
        actions.append("aiwfctl trace recover --dry-run")
    else:
        actions.append("aiwfctl trace begin --workflow <workflow>")
    related_traces = status.get("related_traces", {})
    latest_trace_id = str(related_traces.get("latest_trace_id", "") or "") if isinstance(related_traces, dict) else ""
    if latest_trace_id:
        actions.append(f"aiwfctl trace show {latest_trace_id}")
    duckdb_rebuild = _duckdb_rebuild_next_action(repo_root)
    if duckdb_rebuild:
        actions.append(duckdb_rebuild)
    if not status["runtime"]["event_log"]["exists"]:
        actions.append("aiwfctl help list")
    else:
        last_problem = status["runtime"]["event_log"].get("last_problem_event", {})
        if isinstance(last_problem, dict):
            acknowledge_command = acknowledge_problem_command(last_problem)
            if acknowledge_command:
                actions.append(acknowledge_command)
        candidates = status["runtime"]["event_log"].get("acknowledgement_candidates", [])
        if isinstance(candidates, list) and len(candidates) > 1:
            actions.append("aiwfctl log tail --problems -n 20")
        maintenance = status["runtime"]["event_log"].get("maintenance", {})
        if isinstance(maintenance, dict) and maintenance.get("status") == "attention":
            actions.append("aiwfctl log summary")
            actions.append(f"aiwfctl log archive --keep-last {maintenance.get('keep_last', RUNTIME_LOG_DEFAULT_KEEP_LAST)} --dry-run")
    doctor = status.get("doctor", {})
    if isinstance(doctor, dict) and int(doctor.get("warning_count", 0) or 0) > 0:
        actions.append("aiwfctl doctor --json")
    actions.append("aiwfctl doctor")
    return actions


def attention_reason_summary(reasons: list[dict[str, Any]]) -> dict[str, Any]:
    severity_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for reason in reasons:
        severity = str(reason.get("severity", "") or "info")
        category = str(reason.get("category", "") or "runtime")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1
    return {
        "attention_reason_count": len(reasons),
        "severity_counts": severity_counts,
        "category_counts": category_counts,
    }


def collect_status(repo_root: Path, work_id: str = "", view_mode: str = "full") -> dict[str, Any]:
    resolved = repo_root.resolve()
    status = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-status",
        "status": "ok",
        "view_mode": view_mode,
        "repo": {
            "root": str(resolved),
            "git": git_status(resolved),
        },
        "runtime": {
            "aiwfctl": _path_status(resolved, Path("runtime/windows-script/aiwfctl.cmd")),
            "event_log": runtime_log_status(resolved),
        },
        "trace": active_trace_status(resolved),
        "work": work_status(resolved, work_id),
        "knowledge": knowledge_status(resolved),
        "environment": {
            "dependency_readiness": dependency_readiness(resolved),
        },
        "doctor": doctor_status(resolved),
    }
    if work_id:
        status["related_traces"] = related_trace_status(resolved, work_id)
    status["next_actions"] = next_actions(resolved, status)
    status["attention_reasons"] = attention_reasons(status)
    status["attention_summary"] = attention_reason_summary(status["attention_reasons"])
    if status["attention_reasons"]:
        status["status"] = "attention"
    return status


def attention_reasons(result: dict[str, Any]) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    git = result.get("repo", {}).get("git", {})
    dirty_count = int(git.get("dirty_count", 0) or 0)
    if dirty_count:
        reasons.append(
            {
                "id": "git-dirty",
                "severity": "info",
                "category": "repository",
                "message": "Working tree has uncommitted changes.",
                "count": dirty_count,
                "next_action": "Review git status and commit or split changes when ready.",
            }
        )

    trace = result.get("trace", {})
    trace_status = trace.get("status", "")
    if trace_status in {"active", "invalid"}:
        reasons.append(
            {
                "id": f"trace-{trace_status}",
                "severity": "warning" if trace_status == "invalid" else "info",
                "category": "trace",
                "message": f"Active trace state is {trace_status}.",
                "trace_id": trace.get("trace_id", ""),
                "next_action": trace.get("recovery_command", "") or "Review trace status.",
            }
        )
    if trace.get("stale"):
        reasons.append(
            {
                "id": "trace-stale",
                "severity": "warning",
                "category": "trace",
                "message": "Active trace looks stale.",
                "trace_id": trace.get("trace_id", ""),
                "next_action": trace.get("recovery_command", "") or "Run aiwfctl trace recover --dry-run.",
            }
        )

    event_log = result.get("runtime", {}).get("event_log", {})
    last_problem = event_log.get("last_problem_event", {})
    if isinstance(last_problem, dict) and last_problem:
        acknowledge_command = acknowledge_problem_command(last_problem)
        reasons.append(
            {
                "id": "runtime-last-problem-event",
                "severity": "warning",
                "category": "runtime-log",
                "message": "Runtime log contains an unacknowledged problem event.",
                "trace_id": last_problem.get("trace_id", ""),
                "sequence": last_problem.get("sequence", ""),
                "command": last_problem.get("command", ""),
                "next_action": acknowledge_command or last_problem.get("resume_command", "") or "Run aiwfctl trace show --problems.",
                "resume_command": last_problem.get("resume_command", ""),
                "acknowledge_command": acknowledge_command,
            }
        )

    doctor = result.get("doctor", {})
    doctor_warnings = int(doctor.get("warning_count", 0) or 0)
    if doctor_warnings:
        reasons.append(
            {
                "id": "doctor-warnings",
                "severity": "warning",
                "category": "repository-health",
                "message": "Workflow doctor reported warnings.",
                "count": doctor_warnings,
                "next_action": "Run aiwfctl doctor --json.",
            }
        )

    readiness = result.get("environment", {}).get("dependency_readiness", {})
    if readiness.get("status") == "attention":
        reasons.append(
            {
                "id": "dependency-readiness",
                "severity": "warning"
                if int(readiness.get("required_missing_count", 0) or 0)
                else "info",
                "category": "environment",
                "message": "Runtime dependency readiness needs attention.",
                "required_missing_count": int(readiness.get("required_missing_count", 0) or 0),
                "optional_missing_count": int(readiness.get("optional_missing_count", 0) or 0),
                "next_action": "Run aiwfctl preflight --profile runtime-dev.",
            }
        )

    return reasons


def summarize_status(result: dict[str, Any]) -> dict[str, Any]:
    event_log = result.get("runtime", {}).get("event_log", {})
    knowledge = result.get("knowledge", {}).get("paths", {})
    readiness = result.get("environment", {}).get("dependency_readiness", {})
    warning_summary = result.get("doctor", {}).get("warning_summary", {})
    compact_warning_summary = {
        "severity_counts": warning_summary.get("severity_counts", {}) if isinstance(warning_summary, dict) else {},
        "category_counts": warning_summary.get("category_counts", {}) if isinstance(warning_summary, dict) else {},
        "repairable_count": warning_summary.get("repairable_count", 0) if isinstance(warning_summary, dict) else 0,
        "human_review_count": warning_summary.get("human_review_count", 0) if isinstance(warning_summary, dict) else 0,
    }
    return {
        "schema_version": result.get("schema_version", SCHEMA_VERSION),
        "artifact_type": result.get("artifact_type", "runtime-status"),
        "status": result.get("status", ""),
        "view_mode": "summary",
        "attention_reasons": result.get("attention_reasons", []),
        "attention_summary": result.get("attention_summary", attention_reason_summary(result.get("attention_reasons", []))),
        "repo": {
            "root": result.get("repo", {}).get("root", ""),
            "git": result.get("repo", {}).get("git", {}),
        },
        "trace": {
            key: result.get("trace", {}).get(key, "")
            for key in ("status", "trace_id", "workflow", "work_id", "last_sequence", "reason", "recovery_command")
        },
        "runtime": {
            "event_log": {
                "exists": event_log.get("exists", False),
                "event_count": event_log.get("event_count", 0),
                "maintenance": event_log.get("maintenance", {}),
                "last_problem_event": event_log.get("last_problem_event", {}),
                "acknowledgement_candidate_count": len(event_log.get("acknowledgement_candidates", []))
                if isinstance(event_log.get("acknowledgement_candidates", []), list)
                else 0,
            }
        },
        "work": {
            "work_id": result.get("work", {}).get("work_id", ""),
            "work_area_count": result.get("work", {}).get("work_area_count", 0),
            "selected": result.get("work", {}).get("selected", {}),
        },
        "knowledge": {
            "source_repo_name": result.get("knowledge", {}).get("source_repo_name", ""),
            "source_exists": knowledge.get("source_repo", {}).get("exists", False),
            "duckdb_exists": knowledge.get("duckdb", {}).get("exists", False),
        },
        "doctor": {
            "status": result.get("doctor", {}).get("status", ""),
            "warning_count": result.get("doctor", {}).get("warning_count", 0),
            "warning_summary": compact_warning_summary,
        },
        "environment": {
            "dependency_readiness": {
                "status": readiness.get("status", ""),
                "check_count": readiness.get("check_count", 0),
                "ready_count": readiness.get("ready_count", 0),
                "required_missing_count": readiness.get("required_missing_count", 0),
                "optional_missing_count": readiness.get("optional_missing_count", 0),
            }
        },
        "next_actions": result.get("next_actions", []),
    }


def problem_status(result: dict[str, Any]) -> dict[str, Any]:
    event_log = result.get("runtime", {}).get("event_log", {})
    readiness = result.get("environment", {}).get("dependency_readiness", {})
    failed_checks = [item for item in readiness.get("checks", []) if isinstance(item, dict) and not item.get("ok")]
    related = result.get("related_traces", {})
    problem_traces = [
        item
        for item in related.get("traces", [])
        if isinstance(item, dict) and int(item.get("problem_count", 0) or 0) > 0
    ] if isinstance(related, dict) else []
    payload = {
        "schema_version": result.get("schema_version", SCHEMA_VERSION),
        "artifact_type": result.get("artifact_type", "runtime-status"),
        "status": result.get("status", ""),
        "view_mode": "problems",
        "attention_reasons": result.get("attention_reasons", []),
        "attention_summary": result.get("attention_summary", attention_reason_summary(result.get("attention_reasons", []))),
        "next_actions": result.get("next_actions", []),
    }
    trace = result.get("trace", {})
    if trace.get("status") in {"active", "invalid"} or trace.get("stale"):
        payload["trace"] = trace
    last_problem = event_log.get("last_problem_event", {})
    if isinstance(last_problem, dict) and last_problem:
        payload["runtime"] = {
            "last_problem_event": last_problem,
            "acknowledgement_candidates": event_log.get("acknowledgement_candidates", []),
        }
    if problem_traces:
        payload["related_traces"] = {
            "work_id": related.get("work_id", "") if isinstance(related, dict) else "",
            "problem_traces": problem_traces,
        }
    doctor = result.get("doctor", {})
    if int(doctor.get("warning_count", 0) or 0) > 0 or doctor.get("status") in {"warning", "fail", "unavailable"}:
        payload["doctor"] = doctor
    if failed_checks or readiness.get("status") == "attention":
        payload["environment"] = {
            "dependency_readiness": {
                "status": readiness.get("status", ""),
                "required_missing_count": readiness.get("required_missing_count", 0),
                "optional_missing_count": readiness.get("optional_missing_count", 0),
                "failed_checks": failed_checks,
            }
        }
    return payload


def apply_status_view(result: dict[str, Any], view_mode: str) -> dict[str, Any]:
    if view_mode == "summary":
        return summarize_status(result)
    if view_mode == "problems":
        return problem_status(result)
    return {**result, "view_mode": "verbose" if view_mode == "verbose" else "full"}


def format_status(result: dict[str, Any]) -> str:
    git = result["repo"]["git"]
    trace = result["trace"]
    work = result["work"]
    knowledge = result["knowledge"]["paths"]
    event_log = result["runtime"]["event_log"]
    doctor = result.get("doctor", {})
    readiness = result.get("environment", {}).get("dependency_readiness", {})
    lines = [
        "Ariadne Runtime Status",
        "",
        f"Status      : {result.get('status', '')}",
        f"Repo Root   : {result['repo'].get('root', '')}",
        f"Git         : branch={git.get('branch', '') or '-'} head={git.get('head', '') or '-'} dirty={git.get('dirty_count', 0)}",
        f"Doctor      : status={doctor.get('status', '-') or '-'} warnings={doctor.get('warning_count', 0)}",
        f"Readiness   : status={readiness.get('status', '-') or '-'} ready={readiness.get('ready_count', 0)}/{readiness.get('check_count', 0)} required_missing={readiness.get('required_missing_count', 0)} optional_missing={readiness.get('optional_missing_count', 0)}",
        "",
        "Trace",
        f"  Status    : {trace.get('status', '')}",
        f"  Trace ID  : {trace.get('trace_id', '') or '-'}",
        f"  Workflow  : {trace.get('workflow', '') or '-'}",
        f"  Work ID   : {trace.get('work_id', '') or '-'}",
        f"  Last Seq  : {trace.get('last_sequence', 0)}",
    ]
    if trace.get("reason"):
        lines.append(f"  Reason    : {trace.get('reason', '')}")
    if trace.get("recovery_command"):
        lines.append(f"  Recovery  : {trace.get('recovery_command', '')}")
    reasons = result.get("attention_reasons", [])
    if reasons:
        lines.extend(["", "Attention Reasons"])
        for item in reasons:
            message = item.get("message", "")
            reason_id = item.get("id", "")
            next_action = item.get("next_action", "")
            lines.append(f"  - {reason_id}: {message}".rstrip())
            if next_action:
                lines.append(f"    next: {next_action}")
    related_traces = result.get("related_traces", {})
    if isinstance(related_traces, dict) and related_traces.get("traces"):
        lines.extend(["", "Related Traces"])
        for item in related_traces.get("traces", []):
            lines.append(
                f"  - {item.get('trace_id', '')}: events={item.get('event_count', 0)} problems={item.get('problem_count', 0)}"
            )
            problem = item.get("last_problem_event", {})
            if isinstance(problem, dict) and problem:
                lines.append(
                    f"    problem: {problem.get('command', '')} status={problem.get('status', '') or '-'} reason={problem.get('reason', '') or '-'}"
                )
    lines.extend(
        [
            "",
            "Runtime Log",
            f"  Path      : {event_log.get('path', '')}",
            f"  Events    : {event_log.get('event_count', 0)}",
        ]
    )
    maintenance = event_log.get("maintenance", {})
    if isinstance(maintenance, dict):
        lines.extend(
            [
                f"  Maint     : status={maintenance.get('status', '')} threshold={maintenance.get('threshold', 0)} keep_last={maintenance.get('keep_last', 0)}",
                f"  Archive C : {maintenance.get('archive_candidate_count', 0)}",
            ]
        )
    last_event = event_log.get("last_event", {})
    if last_event:
        lines.append(
            f"  Last      : {last_event.get('trace_id', '')} {last_event.get('sequence', '')} {last_event.get('event', '')}"
        )
    last_relevant = event_log.get("last_relevant_event", {})
    if last_relevant:
        lines.append(
            f"  Relevant  : {last_relevant.get('trace_id', '')} {last_relevant.get('sequence', '')} "
            f"{last_relevant.get('event', '')} {last_relevant.get('command', '')}".rstrip()
        )
    last_problem = event_log.get("last_problem_event", {})
    if last_problem:
        lines.append(
            f"  Problem   : {last_problem.get('trace_id', '')} {last_problem.get('sequence', '')} "
            f"{last_problem.get('event', '')} {last_problem.get('command', '')} "
            f"status={last_problem.get('status', '') or '-'} reason={last_problem.get('reason', '') or '-'}".rstrip()
        )
    candidates = event_log.get("acknowledgement_candidates", [])
    if isinstance(candidates, list) and candidates:
        lines.append(f"  Ack Cand  : {len(candidates)}")
        for item in candidates[:RUNTIME_STATUS_WORK_PREVIEW_LIMIT]:
            lines.append(
                f"    - {item.get('trace_id', '')} {item.get('sequence', '')} {item.get('command', '')}".rstrip()
            )
            if item.get("acknowledge_command"):
                lines.append(f"      ack: {item.get('acknowledge_command', '')}")
    lines.extend(
        [
            "",
            "Work",
            f"  Root      : {work['root'].get('path', '')} exists={str(work['root'].get('exists', False)).lower()}",
            f"  Count     : {work.get('work_area_count', 0)}",
        ]
    )
    selected = work.get("selected", {})
    if selected:
        lines.append(f"  Selected  : {selected.get('path', '')} status={selected.get('status', '')}")
    recent = work.get("recent", [])
    if recent:
        lines.append("  Recent")
        for item in recent:
            lines.append(
                f"    - {item.get('path', '')}: {item.get('status', '')} {item.get('workflow', '')}".rstrip()
            )
    lines.extend(
        [
            "",
            "Knowledge",
            f"  Source    : {knowledge['source_repo'].get('path', '')} exists={str(knowledge['source_repo'].get('exists', False)).lower()}",
            f"  RAG       : {knowledge['rag'].get('path', '')} exists={str(knowledge['rag'].get('exists', False)).lower()}",
            f"  DuckDB    : {knowledge['duckdb'].get('path', '')} exists={str(knowledge['duckdb'].get('exists', False)).lower()}",
            "",
            "Dependency Readiness",
        ]
    )
    for item in readiness.get("checks", []):
        if isinstance(item, dict):
            lines.append(
                f"  - {item.get('id', '')}: {item.get('status', '')} required={str(item.get('required', False)).lower()}"
            )
    lines.extend(
        [
            "",
            "Next Actions",
        ]
    )
    lines.extend(f"  - {item}" for item in result.get("next_actions", []))
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show Ariadne runtime status.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--work-id", default="")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--summary", action="store_true")
    mode.add_argument("--verbose", action="store_true")
    mode.add_argument("--problems", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    view_mode = "summary" if args.summary else "problems" if args.problems else "verbose" if args.verbose else "full"
    result = collect_status(repo_root, work_id=args.work_id, view_mode=view_mode)
    if args.json:
        print(json.dumps(apply_status_view(result, view_mode), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_status(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
