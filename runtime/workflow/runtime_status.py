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
    RUNTIME_STATUS_EVENT_READ_LIMIT,
    RUNTIME_STATUS_WORK_PREVIEW_LIMIT,
)
from runtime.constants.workspace import WORK_ROOT, work_dir_for_id, work_root_for_repo  # noqa: E402
from runtime.observability import logger as runtime_event_logger  # noqa: E402
from runtime.workflow import workflow_state  # noqa: E402


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


def runtime_log_status(repo_root: Path) -> dict[str, Any]:
    path = runtime_event_logger.runtime_event_log_path(repo_root)
    if not path.exists():
        return {
            "path": relative_to_repo(repo_root, path),
            "exists": False,
            "event_count": 0,
            "last_event": {},
        }
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    recent = lines[-RUNTIME_STATUS_EVENT_READ_LIMIT:]
    last_event: dict[str, Any] = {}
    if recent:
        timestamp, trace_id, sequence, payload = _runtime_event_parts(recent[-1])
        last_event = {
            "timestamp": timestamp,
            "trace_id": trace_id,
            "sequence": sequence,
            "event": payload.get("event", ""),
            "command": payload.get("command", ""),
            "workflow": payload.get("workflow", ""),
            "level": payload.get("level", ""),
        }
    return {
        "path": relative_to_repo(repo_root, path),
        "exists": True,
        "event_count": len(lines),
        "last_event": last_event,
    }


def active_trace_status(repo_root: Path) -> dict[str, Any]:
    path = runtime_event_logger.active_runtime_trace_path(repo_root)
    active = runtime_event_logger.load_active_runtime_trace(repo_root)
    if not active:
        return {
            "status": "not-active",
            "path": relative_to_repo(repo_root, path),
            "trace_id": "",
            "workflow": "",
            "last_sequence": 0,
        }
    return {
        "status": active.get("status", "active"),
        "path": relative_to_repo(repo_root, path),
        "trace_id": active.get("trace_id", ""),
        "workflow": active.get("workflow", ""),
        "last_sequence": active.get("last_sequence", 0),
    }


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


def next_actions(status: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    if status["trace"].get("status") == "active":
        actions.append("aiwfctl trace status")
    else:
        actions.append("aiwfctl trace begin --workflow <workflow>")
    if not status["knowledge"]["paths"]["duckdb"]["exists"]:
        actions.append("aiwfctl rag duckdb rebuild --reset")
    if not status["runtime"]["event_log"]["exists"]:
        actions.append("aiwfctl help list")
    actions.append("aiwfctl doctor")
    return actions


def collect_status(repo_root: Path, work_id: str = "") -> dict[str, Any]:
    resolved = repo_root.resolve()
    status = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "runtime-status",
        "status": "ok",
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
    }
    status["next_actions"] = next_actions(status)
    if status["repo"]["git"]["dirty_count"] or status["trace"]["status"] == "active":
        status["status"] = "attention"
    return status


def format_status(result: dict[str, Any]) -> str:
    git = result["repo"]["git"]
    trace = result["trace"]
    work = result["work"]
    knowledge = result["knowledge"]["paths"]
    event_log = result["runtime"]["event_log"]
    lines = [
        "Ariadne Runtime Status",
        "",
        f"Status      : {result.get('status', '')}",
        f"Repo Root   : {result['repo'].get('root', '')}",
        f"Git         : branch={git.get('branch', '') or '-'} head={git.get('head', '') or '-'} dirty={git.get('dirty_count', 0)}",
        "",
        "Trace",
        f"  Status    : {trace.get('status', '')}",
        f"  Trace ID  : {trace.get('trace_id', '') or '-'}",
        f"  Workflow  : {trace.get('workflow', '') or '-'}",
        f"  Last Seq  : {trace.get('last_sequence', 0)}",
        "",
        "Runtime Log",
        f"  Path      : {event_log.get('path', '')}",
        f"  Events    : {event_log.get('event_count', 0)}",
    ]
    last_event = event_log.get("last_event", {})
    if last_event:
        lines.append(
            f"  Last      : {last_event.get('trace_id', '')} {last_event.get('sequence', '')} {last_event.get('event', '')}"
        )
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
            "Next Actions",
        ]
    )
    lines.extend(f"  - {item}" for item in result.get("next_actions", []))
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show Ariadne runtime status.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--work-id", default="")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    result = collect_status(repo_root, work_id=args.work_id)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_status(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
