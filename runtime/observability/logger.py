from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)


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
