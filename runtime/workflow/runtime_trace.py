from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo  # noqa: E402
from runtime.constants.runtime_values import SCHEMA_VERSION  # noqa: E402
from runtime.constants.workflow_limits import RUNTIME_TRACE_EVENT_PREVIEW_LIMIT  # noqa: E402
from runtime.observability import logger as runtime_event_logger  # noqa: E402


def parse_runtime_event_log_line(line: str) -> dict[str, Any] | None:
    parts = line.rstrip("\n").split(" | ", 3)
    if len(parts) != 4:
        return None
    timestamp, trace_id, sequence_text, payload_text = parts
    try:
        sequence = int(sequence_text)
        payload = json.loads(payload_text)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return {
        "timestamp": timestamp,
        "trace_id": trace_id,
        "sequence": sequence,
        "payload": payload,
    }


def resolve_runtime_log_path(repo_root: Path, runtime_log: str = "") -> Path:
    if runtime_log:
        raw = Path(runtime_log)
        return raw if raw.is_absolute() else repo_root / raw
    return runtime_event_logger.runtime_event_log_path(repo_root)


def _latest_trace_id(events: list[dict[str, Any]], *, exclude_trace_id: str = "") -> str:
    for event in reversed(events):
        trace_id = str(event.get("trace_id", "") or "")
        if trace_id and trace_id != exclude_trace_id:
            return trace_id
    return ""


def load_trace_events(
    repo_root: Path,
    *,
    trace_id: str = "",
    runtime_log: str = "",
    exclude_trace_id: str = "",
) -> dict[str, Any]:
    log_path = resolve_runtime_log_path(repo_root, runtime_log)
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-trace-report",
        "status": "ok",
        "log_path": relative_to_repo(repo_root, log_path),
        "trace_id": trace_id.strip(),
        "selected_latest_trace": False,
        "events": [],
        "total_events": 0,
        "malformed_lines": 0,
    }
    if not log_path.exists():
        result["status"] = "missing-log"
        return result

    events: list[dict[str, Any]] = []
    malformed = 0
    for line in log_path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        parsed = parse_runtime_event_log_line(line)
        if parsed is None:
            malformed += 1
            continue
        events.append(parsed)

    selected_trace_id = result["trace_id"]
    if not selected_trace_id:
        selected_trace_id = _latest_trace_id(events, exclude_trace_id=exclude_trace_id)
        result["trace_id"] = selected_trace_id
        result["selected_latest_trace"] = bool(selected_trace_id)

    matched = [event for event in events if event.get("trace_id") == selected_trace_id] if selected_trace_id else []
    result["events"] = matched
    result["total_events"] = len(events)
    result["malformed_lines"] = malformed
    if selected_trace_id and not matched:
        result["status"] = "missing-trace"
    elif not matched:
        result["status"] = "empty-log"
    return result


def _event_view(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload", {}) if isinstance(event.get("payload"), dict) else {}
    output = payload.get("output", {}) if isinstance(payload.get("output"), dict) else {}
    diagnostics = payload.get("diagnostics", {}) if isinstance(payload.get("diagnostics"), dict) else {}
    return {
        "timestamp": event.get("timestamp", ""),
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


def summarize_trace(log_data: dict[str, Any]) -> dict[str, Any]:
    events = list(log_data.get("events", []))
    viewed_events = [_event_view(event) for event in events]
    statuses: Counter[str] = Counter(str(event.get("status", "") or "") for event in viewed_events if event.get("status"))
    reasons: Counter[str] = Counter(str(event.get("reason", "") or "") for event in viewed_events if event.get("reason"))
    commands: list[str] = []
    durations: list[int] = []
    problem_events: list[dict[str, Any]] = []
    last_successful_command = ""

    for event in viewed_events:
        command = str(event.get("command", "") or "")
        if command and command not in commands:
            commands.append(command)
        duration = event.get("duration_ms")
        if isinstance(duration, int):
            durations.append(duration)
        status = str(event.get("status", "") or "")
        exit_code = event.get("exit_code")
        if status == "completed":
            last_successful_command = command
        if (
            status and status != "completed"
        ) or event.get("event") == "runtime_command_failed" or (
            isinstance(exit_code, int) and exit_code != 0
        ):
            problem_events.append(event)

    started_count = sum(1 for event in viewed_events if event.get("event") == "runtime_command_started")
    terminal_count = sum(
        1
        for event in viewed_events
        if event.get("event") in {"runtime_command_completed", "runtime_command_failed"}
    )
    if "failed" in statuses or any(event.get("event") == "runtime_command_failed" for event in viewed_events):
        outcome = "failed"
    elif "blocked" in statuses:
        outcome = "blocked"
    elif events and started_count > terminal_count:
        outcome = "in-progress"
    elif events:
        outcome = "completed"
    else:
        outcome = log_data.get("status", "empty-log")

    last_event = viewed_events[-1] if viewed_events else {}
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-trace-report",
        "status": log_data.get("status", "ok"),
        "trace_id": log_data.get("trace_id", ""),
        "log_path": log_data.get("log_path", ""),
        "selected_latest_trace": bool(log_data.get("selected_latest_trace")),
        "event_count": len(events),
        "total_events": log_data.get("total_events", len(events)),
        "malformed_lines": log_data.get("malformed_lines", 0),
        "first_timestamp": events[0]["timestamp"] if events else "",
        "last_timestamp": events[-1]["timestamp"] if events else "",
        "commands": commands,
        "statuses": dict(statuses),
        "reasons": dict(reasons),
        "duration_total_ms": sum(durations),
        "duration_max_ms": max(durations) if durations else 0,
        "started_count": started_count,
        "terminal_count": terminal_count,
        "last_successful_command": last_successful_command,
        "last_event": last_event,
        "problem_events": problem_events,
        "timeline": viewed_events,
        "outcome": outcome,
        "next_actions": trace_next_actions(outcome, problem_events),
    }


def trace_next_actions(outcome: str, problem_events: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for event in reversed(problem_events):
        resume = str(event.get("resume_command", "") or "")
        if resume:
            actions.append(resume)
            break
    if outcome == "in-progress":
        actions.append("aiwfctl trace status")
    elif outcome == "blocked":
        actions.append("review_human_check_or_block_reason")
    elif outcome == "failed":
        actions.append("inspect_runtime_error")
    if not actions:
        actions.append("aiwfctl status")
    return actions


def build_trace_report(
    repo_root: Path,
    *,
    trace_id: str = "",
    runtime_log: str = "",
    exclude_trace_id: str = "",
) -> dict[str, Any]:
    return summarize_trace(
        load_trace_events(
            repo_root,
            trace_id=trace_id,
            runtime_log=runtime_log,
            exclude_trace_id=exclude_trace_id,
        )
    )


def _counter_text(values: dict[str, int]) -> str:
    if not values:
        return "none"
    return ", ".join(f"{key}: {value}" for key, value in values.items())


def _format_event_line(event: dict[str, Any]) -> str:
    status = str(event.get("status", "") or "-")
    reason = str(event.get("reason", "") or "-")
    command = str(event.get("command", "") or "-")
    return (
        f"  - seq={int(event.get('sequence', 0)):05d} "
        f"event={event.get('event', '')} command={command} status={status} reason={reason}"
    )


def format_trace_report(result: dict[str, Any]) -> str:
    window = (
        f"{result.get('first_timestamp', '')} -> {result.get('last_timestamp', '')}"
        if result.get("first_timestamp") and result.get("last_timestamp")
        else "-"
    )
    lines = [
        "Runtime Trace Report",
        "",
        f"Status       : {result.get('status', '')}",
        f"Outcome      : {result.get('outcome', '')}",
        f"Trace ID     : {result.get('trace_id', '') or '-'}",
        f"Log          : {result.get('log_path', '')}",
        f"Events       : {result.get('event_count', 0)} / {result.get('total_events', 0)}",
        f"Malformed    : {result.get('malformed_lines', 0)}",
        f"Window       : {window}",
        f"Started      : {result.get('started_count', 0)}",
        f"Terminal     : {result.get('terminal_count', 0)}",
        f"Last Success : {result.get('last_successful_command', '') or '-'}",
        f"Statuses     : {_counter_text(result.get('statuses', {}))}",
        f"Reasons      : {_counter_text(result.get('reasons', {}))}",
        f"Duration     : total={result.get('duration_total_ms', 0)}ms max={result.get('duration_max_ms', 0)}ms",
        "",
        "Commands",
    ]
    commands = result.get("commands", [])
    lines.extend(f"  - {command}" for command in commands) if commands else lines.append("  - none")
    lines.append("")
    lines.append("Problems")
    problems = result.get("problem_events", [])
    if problems:
        lines.extend(_format_event_line(event) for event in problems[:RUNTIME_TRACE_EVENT_PREVIEW_LIMIT])
        if len(problems) > RUNTIME_TRACE_EVENT_PREVIEW_LIMIT:
            lines.append(f"  - ... truncated: {len(problems) - RUNTIME_TRACE_EVENT_PREVIEW_LIMIT} event(s)")
    else:
        lines.append("  - none")
    lines.append("")
    lines.append("Timeline")
    timeline = result.get("timeline", [])
    if timeline:
        lines.extend(_format_event_line(event) for event in timeline[:RUNTIME_TRACE_EVENT_PREVIEW_LIMIT])
        if len(timeline) > RUNTIME_TRACE_EVENT_PREVIEW_LIMIT:
            lines.append(f"  - ... truncated: {len(timeline) - RUNTIME_TRACE_EVENT_PREVIEW_LIMIT} event(s)")
    else:
        lines.append("  - none")
    lines.append("")
    lines.append("Next Actions")
    lines.extend(f"  - {action}" for action in result.get("next_actions", []))
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show runtime events for one trace id.")
    parser.add_argument("trace_id", nargs="?", default="")
    parser.add_argument("--runtime-log", default="")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    result = build_trace_report(repo_root, trace_id=args.trace_id, runtime_log=args.runtime_log)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_trace_report(result), end="")
    return 0 if result.get("status") == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
