from __future__ import annotations

import json
import logging
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.constants.runtime_values import (
    DEFAULT_RUNTIME_EVENT_BACKUP_COUNT,
    DEFAULT_RUNTIME_EVENT_MAX_BYTES,
    DEFAULT_RUNTIME_TRACE_ID_BYTES,
    LOG_SANITIZE_LIST_ITEMS_MAX_DEFAULT,
    LOG_SANITIZE_STRING_MAX_CHARS_DEFAULT,
    NON_NEGATIVE_INT_DEFAULT,
    RUNTIME_EVENT_INITIAL_SEQUENCE,
    RUNTIME_EVENT_SEQUENCE_WIDTH,
    SCHEMA_VERSION,
)


LOGGER = logging.getLogger(__name__)
DEFAULT_RUNTIME_EVENT_LOG_DIR = Path("logs") / "runtime"
DEFAULT_RUNTIME_EVENT_LOG_FILE = "runtime-events.log"
DEFAULT_ACTIVE_RUNTIME_TRACE_FILE = "active-trace.json"
DEFAULT_RUNTIME_EVENT_SCHEMA_VERSION = SCHEMA_VERSION
AIWF_TRACE_ID_ENV = "AIWF_TRACE_ID"
SENSITIVE_KEYS = ("secret", "token", "password", "credential", "apikey", "api_key", "private_key")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def monthly_log_path(
    log_dir: Path,
    *,
    stem: str = "runtime-metrics",
    suffix: str = ".jsonl",
    now: datetime | None = None,
) -> Path:
    current = now or _now_utc()
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    return log_dir / f"{stem}-{current.strftime('%Y%m')}{suffix}"


def resolve_log_path(
    *,
    log_dir: Path | None = None,
    base_path: Path | None = None,
    rotate_monthly: bool = True,
    now: datetime | None = None,
) -> Path:
    if base_path is not None:
        path = base_path
        if not rotate_monthly:
            return path
        suffix = path.suffix or ".jsonl"
        stem = path.stem or "runtime-metrics"
        return path.with_name(f"{stem}-{(now or _now_utc()).strftime('%Y%m')}{suffix}")
    directory = log_dir or Path("logs")
    if rotate_monthly:
        return monthly_log_path(directory, now=now)
    return directory / "runtime-metrics.jsonl"


def append_jsonl(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as file:
            file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    except OSError as exc:
        warning = f"runtime metrics write failed: {exc}"
        LOGGER.warning(warning)
        return {
            "status": "warning",
            "path": str(path),
            "warning": warning,
        }
    return {
        "status": "ok",
        "path": str(path),
        "warning": "",
    }


def _now_local() -> datetime:
    return datetime.now().astimezone()


def runtime_event_log_path(repo_root: Path, log_dir: Path | None = None) -> Path:
    directory = log_dir or repo_root / DEFAULT_RUNTIME_EVENT_LOG_DIR
    return directory / DEFAULT_RUNTIME_EVENT_LOG_FILE


def active_runtime_trace_path(repo_root: Path, log_dir: Path | None = None) -> Path:
    directory = log_dir or repo_root / DEFAULT_RUNTIME_EVENT_LOG_DIR
    return directory / DEFAULT_ACTIVE_RUNTIME_TRACE_FILE


def generate_trace_id() -> str:
    return secrets.token_hex(DEFAULT_RUNTIME_TRACE_ID_BYTES)


def load_active_runtime_trace(repo_root: Path, log_dir: Path | None = None) -> dict[str, Any]:
    path = active_runtime_trace_path(repo_root, log_dir=log_dir)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    trace_id = str(payload.get("trace_id", "") or "")
    if not trace_id:
        return {}
    return payload


def active_runtime_trace_id(repo_root: Path, log_dir: Path | None = None) -> str:
    return str(load_active_runtime_trace(repo_root, log_dir=log_dir).get("trace_id", "") or "")


def _coerce_runtime_event_sequence(value: Any) -> int:
    try:
        sequence = int(value)
    except (TypeError, ValueError):
        return RUNTIME_EVENT_INITIAL_SEQUENCE
    return max(sequence, RUNTIME_EVENT_INITIAL_SEQUENCE)


def active_runtime_trace_last_sequence(repo_root: Path, log_dir: Path | None = None) -> int:
    trace = load_active_runtime_trace(repo_root, log_dir=log_dir)
    return _coerce_runtime_event_sequence(trace.get("last_sequence", RUNTIME_EVENT_INITIAL_SEQUENCE))


def begin_active_runtime_trace(
    repo_root: Path,
    *,
    workflow: str,
    work_id: str = "",
    trace_id: str = "",
    force: bool = False,
    initial_sequence: int = RUNTIME_EVENT_INITIAL_SEQUENCE,
    log_dir: Path | None = None,
) -> dict[str, Any]:
    path = active_runtime_trace_path(repo_root, log_dir=log_dir)
    existing = load_active_runtime_trace(repo_root, log_dir=log_dir)
    if existing and not force:
        return {
            "status": "blocked",
            "reason": "active-trace-exists",
            "trace_id": existing.get("trace_id", ""),
            "workflow": existing.get("workflow", ""),
            "work_id": existing.get("work_id", ""),
            "last_sequence": _coerce_runtime_event_sequence(
                existing.get("last_sequence", RUNTIME_EVENT_INITIAL_SEQUENCE)
            ),
            "path": str(path),
        }
    payload = {
        "schema_version": DEFAULT_RUNTIME_EVENT_SCHEMA_VERSION,
        "artifact_type": "active-runtime-trace",
        "status": "active",
        "trace_id": trace_id or generate_trace_id(),
        "workflow": workflow,
        "work_id": work_id,
        "started_at": _now_local().isoformat(timespec="milliseconds"),
        "updated_at": _now_local().isoformat(timespec="milliseconds"),
        "last_sequence": _coerce_runtime_event_sequence(initial_sequence),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        **payload,
        "path": str(path),
    }


def advance_active_runtime_trace_sequence(
    repo_root: Path,
    *,
    trace_id: str,
    minimum_sequence: int,
    log_dir: Path | None = None,
) -> int:
    path = active_runtime_trace_path(repo_root, log_dir=log_dir)
    payload = load_active_runtime_trace(repo_root, log_dir=log_dir)
    if str(payload.get("trace_id", "") or "") != trace_id:
        return minimum_sequence

    last_sequence = _coerce_runtime_event_sequence(payload.get("last_sequence", RUNTIME_EVENT_INITIAL_SEQUENCE))
    next_sequence = max(last_sequence + 1, _coerce_runtime_event_sequence(minimum_sequence))
    payload["last_sequence"] = next_sequence
    payload["updated_at"] = _now_local().isoformat(timespec="milliseconds")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        LOGGER.warning("active runtime trace sequence update failed: %s", exc)
        return minimum_sequence
    return next_sequence


def end_active_runtime_trace(repo_root: Path, log_dir: Path | None = None) -> dict[str, Any]:
    path = active_runtime_trace_path(repo_root, log_dir=log_dir)
    existing = load_active_runtime_trace(repo_root, log_dir=log_dir)
    if not existing:
        return {
            "status": "not-active",
            "reason": "active-trace-missing",
            "trace_id": "",
            "workflow": "",
            "path": str(path),
        }
    path.unlink(missing_ok=True)
    return {
        **existing,
        "status": "ended",
        "ended_at": _now_local().isoformat(timespec="milliseconds"),
        "path": str(path),
    }


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower().replace("-", "_")
    return any(marker in lowered for marker in SENSITIVE_KEYS)


def sanitize_for_log(
    value: Any,
    *,
    max_string_length: int = LOG_SANITIZE_STRING_MAX_CHARS_DEFAULT,
    max_list_items: int = LOG_SANITIZE_LIST_ITEMS_MAX_DEFAULT,
) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            text_key = str(key)
            if _is_sensitive_key(text_key):
                sanitized[text_key] = "***"
            else:
                sanitized[text_key] = sanitize_for_log(
                    item,
                    max_string_length=max_string_length,
                    max_list_items=max_list_items,
                )
        return sanitized
    if isinstance(value, (list, tuple)):
        items = [
            sanitize_for_log(item, max_string_length=max_string_length, max_list_items=max_list_items)
            for item in list(value)[:max_list_items]
        ]
        if len(value) > max_list_items:
            items.append({"_truncated": len(value) - max_list_items})
        return items
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, str):
        normalized = value.replace("\r", "\\r").replace("\n", "\\n")
        if len(normalized) > max_string_length:
            return f"{normalized[:max_string_length]}...<truncated>"
        return normalized
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return str(value)


def format_runtime_event_line(
    *,
    timestamp: datetime,
    trace_id: str,
    sequence: int,
    payload: dict[str, Any],
) -> str:
    timestamp_text = timestamp.astimezone().isoformat(timespec="milliseconds")
    json_payload = json.dumps(sanitize_for_log(payload), ensure_ascii=False, separators=(",", ":"))
    return f"{timestamp_text} | {trace_id} | {sequence:0{RUNTIME_EVENT_SEQUENCE_WIDTH}d} | {json_payload}"


def _rotate_log_file(path: Path, *, max_bytes: int, backup_count: int) -> None:
    if max_bytes <= NON_NEGATIVE_INT_DEFAULT or backup_count <= NON_NEGATIVE_INT_DEFAULT or not path.exists():
        return
    oldest = path.with_name(f"{path.name}.{backup_count}")
    if oldest.exists():
        oldest.unlink()
    for index in range(backup_count - 1, 0, -1):
        source = path.with_name(f"{path.name}.{index}")
        if source.exists():
            source.rename(path.with_name(f"{path.name}.{index + 1}"))
    path.rename(path.with_name(f"{path.name}.1"))


def append_runtime_event_line(
    path: Path,
    line: str,
    *,
    max_bytes: int = DEFAULT_RUNTIME_EVENT_MAX_BYTES,
    backup_count: int = DEFAULT_RUNTIME_EVENT_BACKUP_COUNT,
) -> dict[str, Any]:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        projected_size = (path.stat().st_size if path.exists() else NON_NEGATIVE_INT_DEFAULT) + len((line + "\n").encode("utf-8"))
        if path.exists() and projected_size > max_bytes:
            _rotate_log_file(path, max_bytes=max_bytes, backup_count=backup_count)
        with path.open("a", encoding="utf-8", newline="\n") as file:
            file.write(line + "\n")
    except OSError as exc:
        warning = f"runtime event log write failed: {exc}"
        LOGGER.warning(warning)
        return {
            "status": "warning",
            "path": str(path),
            "warning": warning,
        }
    return {
        "status": "ok",
        "path": str(path),
        "warning": "",
    }


class RuntimeEventLogger:
    def __init__(
        self,
        *,
        repo_root: Path,
        component: str,
        workflow: str = "",
        trace_id: str | None = None,
        log_dir: Path | None = None,
        use_active_trace: bool = True,
        max_bytes: int = DEFAULT_RUNTIME_EVENT_MAX_BYTES,
        backup_count: int = DEFAULT_RUNTIME_EVENT_BACKUP_COUNT,
    ) -> None:
        self.repo_root = repo_root
        self.component = component
        self.workflow = workflow
        self.log_dir = log_dir
        self.use_active_trace = use_active_trace
        env_trace_id = os.environ.get(AIWF_TRACE_ID_ENV)
        active_trace = load_active_runtime_trace(repo_root, log_dir=log_dir) if use_active_trace else {}
        state_trace_id = str(active_trace.get("trace_id", "") or "")
        self.trace_id = trace_id or env_trace_id or state_trace_id or generate_trace_id()
        self.log_path = runtime_event_log_path(repo_root, log_dir=log_dir)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.sequence = (
            _coerce_runtime_event_sequence(active_trace.get("last_sequence", RUNTIME_EVENT_INITIAL_SEQUENCE))
            if state_trace_id == self.trace_id
            else RUNTIME_EVENT_INITIAL_SEQUENCE
        )
        self.write_warnings: list[dict[str, Any]] = []

    def emit(
        self,
        event: str,
        *,
        level: str = "info",
        workflow: str | None = None,
        phase: str = "",
        operation_id: str = "",
        attempt: int = 1,
        diagnostics: dict[str, Any] | None = None,
        input: dict[str, Any] | None = None,
        output: dict[str, Any] | None = None,
        **metadata: Any,
    ) -> dict[str, Any]:
        minimum_sequence = self.sequence + 1
        self.sequence = (
            advance_active_runtime_trace_sequence(
                self.repo_root,
                trace_id=self.trace_id,
                minimum_sequence=minimum_sequence,
                log_dir=self.log_dir,
            )
            if self.use_active_trace
            else minimum_sequence
        )
        payload = {
            **metadata,
            "schema_version": DEFAULT_RUNTIME_EVENT_SCHEMA_VERSION,
            "level": level or "info",
            "component": self.component,
            "event": event,
            "workflow": self.workflow if workflow is None else workflow,
            "phase": phase,
            "operation_id": operation_id,
            "attempt": attempt if isinstance(attempt, int) and attempt > 0 else 1,
            "diagnostics": diagnostics or {},
            "input": input or {},
            "output": output or {},
        }
        line = format_runtime_event_line(
            timestamp=_now_local(),
            trace_id=self.trace_id,
            sequence=self.sequence,
            payload=payload,
        )
        write_result = append_runtime_event_line(
            self.log_path,
            line,
            max_bytes=self.max_bytes,
            backup_count=self.backup_count,
        )
        if write_result["status"] != "ok":
            self.write_warnings.append(write_result)
        return {
            "status": write_result["status"],
            "path": write_result["path"],
            "trace_id": self.trace_id,
            "sequence": self.sequence,
            "warning": write_result["warning"],
        }
