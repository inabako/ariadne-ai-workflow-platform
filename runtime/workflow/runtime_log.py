from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo  # noqa: E402
from runtime.constants.runtime_values import SCHEMA_VERSION  # noqa: E402
from runtime.constants.workflow_limits import (  # noqa: E402
    RUNTIME_LOG_COMMAND_PREVIEW_LIMIT,
    RUNTIME_LOG_DEFAULT_KEEP_LAST,
    RUNTIME_LOG_EVENT_PREVIEW_LIMIT,
    RUNTIME_LOG_MAINTENANCE_GRACE_EVENTS,
    RUNTIME_LOG_TAIL_DEFAULT_LIMIT,
)
from runtime.observability import logger as runtime_event_logger  # noqa: E402
from runtime.workflow import runtime_trace  # noqa: E402


DEFAULT_RUNTIME_LOG_ARCHIVE_DIR = Path("logs") / "runtime" / "archive"
DEFAULT_PROBLEM_ACKNOWLEDGEMENT_PATH = Path("logs") / "runtime" / "problem-acknowledgements.json"


def resolve_runtime_log_path(repo_root: Path, runtime_log: str = "") -> Path:
    return runtime_trace.resolve_runtime_log_path(repo_root, runtime_log).resolve()


def resolve_archive_dir(repo_root: Path, archive_dir: str = "") -> Path:
    raw = Path(archive_dir) if archive_dir else repo_root / DEFAULT_RUNTIME_LOG_ARCHIVE_DIR
    return (raw if raw.is_absolute() else repo_root / raw).resolve()


def _require_under_repo(repo_root: Path, path: Path) -> None:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"path must stay under repository root: {path}") from exc


def _read_log_lines(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return log_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()


def _parse_events(lines: list[str]) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    malformed = 0
    for line in lines:
        parsed = runtime_trace.parse_runtime_event_log_line(line)
        if parsed is None:
            malformed += 1
        else:
            events.append(parsed)
    return events, malformed


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload", {})
    return payload if isinstance(payload, dict) else {}


def _event_view(event: dict[str, Any]) -> dict[str, Any]:
    payload = _payload(event)
    output = payload.get("output", {}) if isinstance(payload.get("output"), dict) else {}
    diagnostics = payload.get("diagnostics", {}) if isinstance(payload.get("diagnostics"), dict) else {}
    return {
        "timestamp": event.get("timestamp", ""),
        "trace_id": event.get("trace_id", ""),
        "sequence": event.get("sequence", 0),
        "event": payload.get("event", ""),
        "command": payload.get("command", ""),
        "workflow": payload.get("workflow", ""),
        "level": payload.get("level", ""),
        "status": output.get("status", ""),
        "reason": output.get("reason", ""),
        "exit_code": output.get("exit_code", ""),
        "duration_ms": output.get("duration_ms", ""),
        "next_action": diagnostics.get("next_action", ""),
        "resume_command": diagnostics.get("resume_command", ""),
    }


def _is_problem_event(event: dict[str, Any]) -> bool:
    status = str(event.get("status", "") or "")
    level = str(event.get("level", "") or "")
    event_name = str(event.get("event", "") or "")
    exit_code = event.get("exit_code", "")
    if event_name == "runtime_command_failed":
        return True
    if status and status != "completed":
        return True
    if isinstance(exit_code, int) and exit_code != 0:
        return True
    return level in {"error", "warning"} and event_name != "runtime_command_started"


def _parsed_records(lines: list[str]) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    malformed = 0
    for line in lines:
        parsed = runtime_trace.parse_runtime_event_log_line(line)
        if parsed is None:
            malformed += 1
            continue
        records.append({**_event_view(parsed), "raw_line": line})
    return records, malformed


def _filter_records(records: list[dict[str, Any]], *, trace_id: str = "", problems: bool = False) -> list[dict[str, Any]]:
    filtered = records
    if trace_id:
        filtered = [record for record in filtered if str(record.get("trace_id", "") or "") == trace_id]
    if problems:
        filtered = [record for record in filtered if _is_problem_event(record)]
    return filtered


def problem_acknowledgement_path(repo_root: Path) -> Path:
    return (repo_root / DEFAULT_PROBLEM_ACKNOWLEDGEMENT_PATH).resolve()


def load_problem_acknowledgements(repo_root: Path) -> dict[str, Any]:
    path = problem_acknowledgement_path(repo_root)
    if not path.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": "runtime-problem-acknowledgements",
            "acknowledged_events": [],
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("artifact_type", "runtime-problem-acknowledgements")
    data.setdefault("acknowledged_events", [])
    return data


def _event_ack_key(event: dict[str, Any]) -> str:
    sequence = event.get("sequence", "")
    sequence = _normalize_sequence(sequence)
    return "|".join(
        [
            str(event.get("trace_id", "") or ""),
            str(sequence or ""),
            str(event.get("event", "") or ""),
            str(event.get("command", "") or ""),
            str(event.get("status", "") or ""),
            str(event.get("reason", "") or ""),
        ]
    )


def _normalize_sequence(value: object) -> str:
    if isinstance(value, int):
        return f"{value:05d}"
    text = str(value or "")
    return f"{int(text):05d}" if text.isdigit() else text


def problem_ack_key(event: dict[str, Any]) -> str:
    return _event_ack_key(event)


def acknowledged_problem_keys(repo_root: Path) -> set[str]:
    data = load_problem_acknowledgements(repo_root)
    items = data.get("acknowledged_events", [])
    if not isinstance(items, list):
        return set()
    return {
        str(item.get("ack_key", "") or "")
        for item in items
        if isinstance(item, dict) and item.get("ack_key")
    }


def is_problem_acknowledged(repo_root: Path, event: dict[str, Any]) -> bool:
    return _event_ack_key(event) in acknowledged_problem_keys(repo_root)


def acknowledge_runtime_problem(
    repo_root: Path,
    *,
    trace_id: str = "",
    sequence: str = "",
    command: str = "",
    all_matching: bool = False,
    reason: str = "",
) -> dict[str, Any]:
    log_path = resolve_runtime_log_path(repo_root)
    lines = _read_log_lines(log_path)
    records, malformed = _parsed_records(lines)
    problems = [record for record in records if _is_problem_event(record)]
    if trace_id:
        problems = [record for record in problems if str(record.get("trace_id", "") or "") == trace_id]
    if sequence:
        normalized_sequence = _normalize_sequence(sequence)
        problems = [record for record in problems if _normalize_sequence(record.get("sequence", "")) == normalized_sequence]
    if command:
        problems = [record for record in problems if str(record.get("command", "") or "") == command]
    targets = problems if all_matching else problems[-1:] if problems else []
    status = "ok" if targets else "empty-match" if log_path.exists() else "missing-log"
    path = problem_acknowledgement_path(repo_root)
    data = load_problem_acknowledgements(repo_root)
    entries = data.get("acknowledged_events", [])
    if not isinstance(entries, list):
        entries = []
    written = False
    for target in targets:
        ack_key = _event_ack_key(target)
        if ack_key not in {
            str(item.get("ack_key", "") or "")
            for item in entries
            if isinstance(item, dict)
        }:
            entries.append(
                {
                    "ack_key": ack_key,
                    "trace_id": target.get("trace_id", ""),
                    "sequence": target.get("sequence", ""),
                    "event": target.get("event", ""),
                    "command": target.get("command", ""),
                    "status": target.get("status", ""),
                    "reason": target.get("reason", ""),
                    "acknowledged_reason": reason,
                }
            )
            data["acknowledged_events"] = entries
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            written = True
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-problem-acknowledgement",
        "status": status,
        "log_path": relative_to_repo(repo_root, log_path),
        "acknowledgement_path": relative_to_repo(repo_root, path),
        "trace_id": trace_id,
        "sequence": sequence,
        "command": command,
        "all_matching": all_matching,
        "malformed_lines": malformed,
        "acknowledged_event": targets[-1] if targets else {},
        "acknowledged_count": len(targets),
        "written": written,
    }


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: value for key, value in sorted(counter.items(), key=lambda item: (-item[1], item[0]))}


def _top_counter_items(counter: Counter[str], *, limit: int = RUNTIME_LOG_COMMAND_PREVIEW_LIMIT) -> list[dict[str, Any]]:
    return [
        {"value": key, "count": value}
        for key, value in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def build_log_summary(repo_root: Path, *, runtime_log: str = "") -> dict[str, Any]:
    log_path = resolve_runtime_log_path(repo_root, runtime_log)
    lines = _read_log_lines(log_path)
    events, malformed = _parse_events(lines)
    payloads = [_payload(event) for event in events]
    command_counts: Counter[str] = Counter(
        str(payload.get("command", "") or "") for payload in payloads if payload.get("command")
    )
    event_counts: Counter[str] = Counter(str(payload.get("event", "") or "") for payload in payloads if payload.get("event"))
    level_counts: Counter[str] = Counter(str(payload.get("level", "") or "") for payload in payloads if payload.get("level"))
    trace_ids = sorted({str(event.get("trace_id", "") or "") for event in events if event.get("trace_id")})
    size_bytes = log_path.stat().st_size if log_path.exists() else 0
    status = "ok" if log_path.exists() and events else "empty-log" if log_path.exists() else "missing-log"
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-log-summary",
        "status": status,
        "log_path": relative_to_repo(repo_root, log_path),
        "exists": log_path.exists(),
        "size_bytes": size_bytes,
        "line_count": len(lines),
        "event_count": len(events),
        "malformed_lines": malformed,
        "trace_count": len(trace_ids),
        "first_timestamp": events[0].get("timestamp", "") if events else "",
        "last_timestamp": events[-1].get("timestamp", "") if events else "",
        "event_counts": _counter_dict(event_counts),
        "level_counts": _counter_dict(level_counts),
        "top_commands": _top_counter_items(command_counts),
        "maintenance": log_maintenance_status(len(lines)),
        "next_actions": log_next_actions(len(lines)),
    }


def log_maintenance_status(line_count: int, *, keep_last: int = RUNTIME_LOG_DEFAULT_KEEP_LAST) -> dict[str, Any]:
    threshold = int(keep_last) + RUNTIME_LOG_MAINTENANCE_GRACE_EVENTS
    over_threshold = int(line_count) > threshold
    return {
        "status": "attention" if over_threshold else "ok",
        "line_count": int(line_count),
        "keep_last": int(keep_last),
        "grace_events": RUNTIME_LOG_MAINTENANCE_GRACE_EVENTS,
        "threshold": threshold,
        "archive_candidate_count": max(int(line_count) - int(keep_last), 0) if over_threshold else 0,
        "recommended_commands": log_next_actions(int(line_count), keep_last=keep_last),
    }


def log_next_actions(line_count: int, *, keep_last: int = RUNTIME_LOG_DEFAULT_KEEP_LAST) -> list[str]:
    if line_count <= int(keep_last) + RUNTIME_LOG_MAINTENANCE_GRACE_EVENTS:
        return ["aiwfctl log summary"]
    return [
        f"aiwfctl log archive --keep-last {int(keep_last)} --dry-run",
        f"aiwfctl log prune --keep-last {int(keep_last)} --dry-run",
    ]


def _split_keep_last(lines: list[str], keep_last: int) -> tuple[list[str], list[str]]:
    normalized_keep = max(int(keep_last), 0)
    if normalized_keep == 0:
        return lines, []
    if len(lines) <= normalized_keep:
        return [], lines
    return lines[:-normalized_keep], lines[-normalized_keep:]


def _write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines)
    path.write_text(f"{text}\n" if text else "", encoding="utf-8", newline="\n")


def _archive_file_path(archive_dir: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return archive_dir / f"runtime-events-{timestamp}.log"


def archive_runtime_log(
    repo_root: Path,
    *,
    runtime_log: str = "",
    archive_dir: str = "",
    keep_last: int = RUNTIME_LOG_DEFAULT_KEEP_LAST,
    dry_run: bool = False,
    human_check: str | None = None,
) -> dict[str, Any]:
    log_path = resolve_runtime_log_path(repo_root, runtime_log)
    target_archive_dir = resolve_archive_dir(repo_root, archive_dir)
    _require_under_repo(repo_root, log_path)
    _require_under_repo(repo_root, target_archive_dir)
    lines = _read_log_lines(log_path)
    archived_lines, remaining_lines = _split_keep_last(lines, keep_last)
    archive_path = _archive_file_path(target_archive_dir)
    approved = human_check == "approved"
    status = "dry-run" if dry_run else "human-check-required" if not approved else "ok"
    if not log_path.exists():
        status = "missing-log"
    elif not archived_lines:
        status = "no-op" if approved and not dry_run else status
    if approved and not dry_run and archived_lines:
        _write_lines(archive_path, archived_lines)
        _write_lines(log_path, remaining_lines)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-log-archive",
        "status": status,
        "dry_run": dry_run,
        "log_path": relative_to_repo(repo_root, log_path),
        "archive_path": relative_to_repo(repo_root, archive_path),
        "keep_last": max(int(keep_last), 0),
        "line_count": len(lines),
        "archive_count": len(archived_lines),
        "kept_count": len(remaining_lines),
        "would_write": approved and not dry_run and bool(archived_lines),
        "human_check_required": not dry_run and not approved and log_path.exists(),
        "next_action": "add --human-check approved to archive and shrink the runtime log"
        if not dry_run and not approved and log_path.exists()
        else "",
    }


def prune_runtime_log(
    repo_root: Path,
    *,
    runtime_log: str = "",
    keep_last: int = RUNTIME_LOG_DEFAULT_KEEP_LAST,
    dry_run: bool = False,
    human_check: str | None = None,
) -> dict[str, Any]:
    log_path = resolve_runtime_log_path(repo_root, runtime_log)
    _require_under_repo(repo_root, log_path)
    lines = _read_log_lines(log_path)
    pruned_lines, remaining_lines = _split_keep_last(lines, keep_last)
    approved = human_check == "approved"
    status = "dry-run" if dry_run else "human-check-required" if not approved else "ok"
    if not log_path.exists():
        status = "missing-log"
    elif not pruned_lines:
        status = "no-op" if approved and not dry_run else status
    if approved and not dry_run and pruned_lines:
        _write_lines(log_path, remaining_lines)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-log-prune",
        "status": status,
        "dry_run": dry_run,
        "log_path": relative_to_repo(repo_root, log_path),
        "keep_last": max(int(keep_last), 0),
        "line_count": len(lines),
        "prune_count": len(pruned_lines),
        "kept_count": len(remaining_lines),
        "would_write": approved and not dry_run and bool(pruned_lines),
        "human_check_required": not dry_run and not approved and log_path.exists(),
        "next_action": "add --human-check approved to prune the runtime log"
        if not dry_run and not approved and log_path.exists()
        else "",
    }


def tail_runtime_log(
    repo_root: Path,
    *,
    runtime_log: str = "",
    limit: int = RUNTIME_LOG_TAIL_DEFAULT_LIMIT,
    trace_id: str = "",
    problems: bool = False,
) -> dict[str, Any]:
    log_path = resolve_runtime_log_path(repo_root, runtime_log)
    lines = _read_log_lines(log_path)
    records, malformed = _parsed_records(lines)
    filtered = _filter_records(records, trace_id=trace_id.strip(), problems=problems)
    selected = filtered[-max(int(limit), 0) :] if limit else filtered
    status = "ok" if log_path.exists() and selected else "empty-match" if log_path.exists() else "missing-log"
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-log-tail",
        "status": status,
        "log_path": relative_to_repo(repo_root, log_path),
        "trace_id": trace_id.strip(),
        "problems_only": problems,
        "limit": max(int(limit), 0),
        "line_count": len(lines),
        "total_event_count": len(records),
        "selected_event_count": len(selected),
        "malformed_lines": malformed,
        "events": selected,
    }


def grep_runtime_log(
    repo_root: Path,
    *,
    trace_id: str,
    runtime_log: str = "",
    problems: bool = False,
) -> dict[str, Any]:
    log_path = resolve_runtime_log_path(repo_root, runtime_log)
    lines = _read_log_lines(log_path)
    records, malformed = _parsed_records(lines)
    filtered = _filter_records(records, trace_id=trace_id.strip(), problems=problems)
    status = "ok" if log_path.exists() and filtered else "empty-match" if log_path.exists() else "missing-log"
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-log-grep",
        "status": status,
        "log_path": relative_to_repo(repo_root, log_path),
        "trace_id": trace_id.strip(),
        "problems_only": problems,
        "line_count": len(lines),
        "total_event_count": len(records),
        "selected_event_count": len(filtered),
        "malformed_lines": malformed,
        "events": filtered,
    }


def export_runtime_log(
    repo_root: Path,
    *,
    trace_id: str,
    output: str,
    runtime_log: str = "",
    problems: bool = False,
) -> dict[str, Any]:
    result = grep_runtime_log(repo_root, trace_id=trace_id, runtime_log=runtime_log, problems=problems)
    result = {**result, "artifact_type": "runtime-log-export"}
    output_path = Path(output)
    resolved_output = output_path if output_path.is_absolute() else repo_root / output_path
    _require_under_repo(repo_root, resolved_output)
    result["output"] = relative_to_repo(repo_root, resolved_output)
    result["written"] = False
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(json.dumps({**result, "written": True}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["written"] = True
    return result


def _format_counter(values: dict[str, int]) -> str:
    if not values:
        return "none"
    return ", ".join(f"{key}: {value}" for key, value in values.items())


def format_log_summary(result: dict[str, Any]) -> str:
    window = (
        f"{result.get('first_timestamp', '')} -> {result.get('last_timestamp', '')}"
        if result.get("first_timestamp") and result.get("last_timestamp")
        else "-"
    )
    lines = [
        "Runtime Log Summary",
        "",
        f"Status    : {result.get('status', '')}",
        f"Log       : {result.get('log_path', '')}",
        f"Size      : {result.get('size_bytes', 0)} bytes",
        f"Lines     : {result.get('line_count', 0)}",
        f"Events    : {result.get('event_count', 0)}",
        f"Malformed : {result.get('malformed_lines', 0)}",
        f"Traces    : {result.get('trace_count', 0)}",
        f"Window    : {window}",
        f"Events By : {_format_counter(result.get('event_counts', {}))}",
        f"Levels    : {_format_counter(result.get('level_counts', {}))}",
        "",
        "Maintenance",
    ]
    maintenance = result.get("maintenance", {})
    if isinstance(maintenance, dict):
        lines.extend(
            [
                f"  Status    : {maintenance.get('status', '')}",
                f"  Threshold : {maintenance.get('threshold', 0)}",
                f"  Keep Last : {maintenance.get('keep_last', 0)}",
                f"  Archive C : {maintenance.get('archive_candidate_count', 0)}",
            ]
        )
    lines.extend(
        [
            "",
            "Top Commands",
        ]
    )
    commands = result.get("top_commands", [])
    lines.extend(f"  - {item.get('value', '')}: {item.get('count', 0)}" for item in commands) if commands else lines.append("  - none")
    lines.append("")
    lines.append("Next Actions")
    lines.extend(f"  - {action}" for action in result.get("next_actions", []))
    return "\n".join(lines).rstrip() + "\n"


def format_log_maintenance_result(result: dict[str, Any]) -> str:
    title = "Runtime Log Archive" if result.get("artifact_type") == "runtime-log-archive" else "Runtime Log Prune"
    lines = [
        title,
        "",
        f"Status      : {result.get('status', '')}",
        f"Dry Run     : {str(result.get('dry_run', False)).lower()}",
        f"Log         : {result.get('log_path', '')}",
        f"Keep Last   : {result.get('keep_last', 0)}",
        f"Lines       : {result.get('line_count', 0)}",
    ]
    if result.get("artifact_type") == "runtime-log-archive":
        lines.append(f"Archive     : {result.get('archive_path', '')}")
        lines.append(f"Archive Cnt : {result.get('archive_count', 0)}")
    else:
        lines.append(f"Prune Count : {result.get('prune_count', 0)}")
    lines.extend(
        [
            f"Kept Count  : {result.get('kept_count', 0)}",
            f"Would Write : {str(result.get('would_write', False)).lower()}",
        ]
    )
    plan_output = str(result.get("plan_output", "") or "")
    if plan_output:
        lines.append(f"Output      : {plan_output}")
    next_action = str(result.get("next_action", "") or "")
    if next_action:
        lines.extend(["", f"Next        : {next_action}"])
    return "\n".join(lines).rstrip() + "\n"


def _format_event_line(event: dict[str, Any]) -> str:
    status = str(event.get("status", "") or "-")
    reason = str(event.get("reason", "") or "-")
    command = str(event.get("command", "") or "-")
    return (
        f"  - {event.get('trace_id', '')} "
        f"seq={int(event.get('sequence', 0)):05d} "
        f"event={event.get('event', '')} command={command} status={status} reason={reason}"
    )


def format_log_events_result(result: dict[str, Any]) -> str:
    titles = {
        "runtime-log-tail": "Runtime Log Tail",
        "runtime-log-grep": "Runtime Log Grep",
        "runtime-log-export": "Runtime Log Export",
    }
    lines = [
        titles.get(str(result.get("artifact_type", "")), "Runtime Log Events"),
        "",
        f"Status    : {result.get('status', '')}",
        f"Log       : {result.get('log_path', '')}",
        f"Trace ID  : {result.get('trace_id', '') or '-'}",
        f"Problems  : {str(result.get('problems_only', False)).lower()}",
        f"Events    : {result.get('selected_event_count', 0)} / {result.get('total_event_count', 0)}",
        f"Malformed : {result.get('malformed_lines', 0)}",
    ]
    if "limit" in result:
        lines.append(f"Limit     : {result.get('limit', 0)}")
    if result.get("output"):
        lines.append(f"Output    : {result.get('output', '')}")
    lines.extend(["", "Events"])
    events = result.get("events", [])
    if events:
        lines.extend(_format_event_line(event) for event in events[:RUNTIME_LOG_EVENT_PREVIEW_LIMIT])
        if len(events) > RUNTIME_LOG_EVENT_PREVIEW_LIMIT:
            lines.append(f"  - ... truncated: {len(events) - RUNTIME_LOG_EVENT_PREVIEW_LIMIT} event(s)")
    else:
        lines.append("  - none")
    return "\n".join(lines).rstrip() + "\n"


def format_problem_acknowledgement(result: dict[str, Any]) -> str:
    event = result.get("acknowledged_event", {})
    lines = [
        "Runtime Problem Acknowledgement",
        "",
        f"Status : {result.get('status', '')}",
        f"Path   : {result.get('acknowledgement_path', '')}",
        f"Written: {str(result.get('written', False)).lower()}",
        f"Count  : {result.get('acknowledged_count', 0)}",
        "",
        "Event",
    ]
    if isinstance(event, dict) and event:
        lines.extend(
            [
                f"  Trace ID: {event.get('trace_id', '')}",
                f"  Sequence: {event.get('sequence', '')}",
                f"  Command : {event.get('command', '')}",
                f"  Status  : {event.get('status', '')}",
                f"  Reason  : {event.get('reason', '')}",
            ]
        )
    else:
        lines.append("  - none")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize, archive, and prune runtime event logs.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="log_command")
    summary = sub.add_parser("summary")
    summary.add_argument("--runtime-log", default="")
    summary.add_argument("--json", action="store_true")
    archive = sub.add_parser("archive")
    archive.add_argument("--runtime-log", default="")
    archive.add_argument("--archive-dir", default="")
    archive.add_argument("--keep-last", type=int, default=RUNTIME_LOG_DEFAULT_KEEP_LAST)
    archive.add_argument("--dry-run", action="store_true")
    archive.add_argument("--human-check", choices=["approved"], default=None)
    archive.add_argument("--json", action="store_true")
    prune = sub.add_parser("prune")
    prune.add_argument("--runtime-log", default="")
    prune.add_argument("--keep-last", type=int, default=RUNTIME_LOG_DEFAULT_KEEP_LAST)
    prune.add_argument("--dry-run", action="store_true")
    prune.add_argument("--human-check", choices=["approved"], default=None)
    prune.add_argument("--json", action="store_true")
    tail = sub.add_parser("tail")
    tail.add_argument("--runtime-log", default="")
    tail.add_argument("-n", "--limit", type=int, default=RUNTIME_LOG_TAIL_DEFAULT_LIMIT)
    tail.add_argument("--trace-id", default="")
    tail.add_argument("--problems", action="store_true")
    tail.add_argument("--json", action="store_true")
    grep = sub.add_parser("grep")
    grep.add_argument("--runtime-log", default="")
    grep.add_argument("--trace-id", required=True)
    grep.add_argument("--problems", action="store_true")
    grep.add_argument("--json", action="store_true")
    export = sub.add_parser("export")
    export.add_argument("--runtime-log", default="")
    export.add_argument("--trace-id", required=True)
    export.add_argument("--output", required=True)
    export.add_argument("--problems", action="store_true")
    export.add_argument("--json", action="store_true")
    acknowledge = sub.add_parser("acknowledge-problem")
    acknowledge.add_argument("--trace-id", default="")
    acknowledge.add_argument("--sequence", default="")
    acknowledge.add_argument("--command", dest="ack_command", default="")
    acknowledge.add_argument("--all", action="store_true")
    acknowledge.add_argument("--reason", default="")
    acknowledge.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    if args.log_command == "summary":
        result = build_log_summary(repo_root, runtime_log=args.runtime_log)
        output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else format_log_summary(result)
    elif args.log_command == "archive":
        result = archive_runtime_log(
            repo_root,
            runtime_log=args.runtime_log,
            archive_dir=args.archive_dir,
            keep_last=args.keep_last,
            dry_run=args.dry_run,
            human_check=args.human_check,
        )
        output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else format_log_maintenance_result(result)
    elif args.log_command == "prune":
        result = prune_runtime_log(
            repo_root,
            runtime_log=args.runtime_log,
            keep_last=args.keep_last,
            dry_run=args.dry_run,
            human_check=args.human_check,
        )
        output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else format_log_maintenance_result(result)
    elif args.log_command == "tail":
        result = tail_runtime_log(
            repo_root,
            runtime_log=args.runtime_log,
            limit=args.limit,
            trace_id=args.trace_id,
            problems=bool(args.problems),
        )
        output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else format_log_events_result(result)
    elif args.log_command == "grep":
        result = grep_runtime_log(
            repo_root,
            runtime_log=args.runtime_log,
            trace_id=args.trace_id,
            problems=bool(args.problems),
        )
        output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else format_log_events_result(result)
    elif args.log_command == "export":
        result = export_runtime_log(
            repo_root,
            runtime_log=args.runtime_log,
            trace_id=args.trace_id,
            output=args.output,
            problems=bool(args.problems),
        )
        output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else format_log_events_result(result)
    elif args.log_command == "acknowledge-problem":
        result = acknowledge_runtime_problem(
            repo_root,
            trace_id=args.trace_id,
            sequence=args.sequence,
            command=args.ack_command,
            all_matching=bool(args.all),
            reason=args.reason,
        )
        output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else format_problem_acknowledgement(result)
    else:
        parser.print_help()
        return 1
    print(output if output.endswith("\n") else f"{output}\n", end="")
    return 0 if result.get("status") in {"ok", "dry-run", "no-op", "empty-log"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
