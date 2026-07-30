from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.constants.runtime_values import SCHEMA_VERSION  # noqa: E402
from runtime.common import gate_restart, find_repo_root, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.workspace import context_file  # noqa: E402


STATE_FILE_NAME = "workflow-state.json"
VALID_STATUS = {"not-started", "in-progress", "blocked", "review-ready", "complete", "failed"}


def default_state(workflow: str, work_id: str, phase: str, status: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workflow": workflow,
        "work_id": work_id,
        "phase": phase,
        "status": status,
        "blocking_reason": "",
        "next_human_action": "",
        "artifacts": {},
        "updated_at": utc_now_iso(),
        "history": [],
        "gate_restart": workflow_state_gate_restart(status, workflow, work_id, phase),
    }


def workflow_state_gate_restart(status: str, workflow: str, work_id: str, phase: str) -> dict[str, Any]:
    repair_command = ""
    if status in {"blocked", "failed"}:
        repair_command = (
            "uv run --project runtime python runtime/ctl/ctl.py --repo-root . "
            f"workflow state set --work-dir work/{work_id} --workflow {workflow} --work-id {work_id} --phase {phase} --status in-progress"
        )
    return gate_restart.build_status_gate_restart(
        "workflow-state-gate",
        status=status,
        restart_reason="workflow-state",
        repair_command=repair_command,
    )


def state_path_for_work_dir(work_dir: Path) -> Path:
    return context_file(work_dir, STATE_FILE_NAME)


def load_state(work_dir: Path, workflow: str = "", work_id: str = "", phase: str = "", status: str = "not-started") -> dict[str, Any]:
    path = state_path_for_work_dir(work_dir)
    data = read_json(path, default=None)
    if isinstance(data, dict):
        data.setdefault("schema_version", SCHEMA_VERSION)
        data.setdefault("workflow", workflow)
        data.setdefault("work_id", work_id)
        data.setdefault("phase", phase)
        data.setdefault("status", status)
        data.setdefault("blocking_reason", "")
        data.setdefault("next_human_action", "")
        data.setdefault("artifacts", {})
        data.setdefault("history", [])
        data.setdefault(
            "gate_restart",
            workflow_state_gate_restart(
                str(data.get("status", status)),
                str(data.get("workflow", workflow)),
                str(data.get("work_id", work_id)),
                str(data.get("phase", phase)),
            ),
        )
        return data
    return default_state(workflow, work_id, phase, status)


def update_state(
    work_dir: Path,
    *,
    workflow: str,
    work_id: str,
    phase: str,
    status: str,
    blocking_reason: str = "",
    next_human_action: str = "",
    artifacts: dict[str, str] | None = None,
) -> dict[str, Any]:
    if status not in VALID_STATUS:
        raise ValueError(f"Invalid workflow status: {status}")
    state = load_state(work_dir, workflow=workflow, work_id=work_id, phase=phase, status=status)
    previous = {
        "phase": state.get("phase", ""),
        "status": state.get("status", ""),
        "updated_at": state.get("updated_at", ""),
    }
    state.update(
        {
            "workflow": workflow,
            "work_id": work_id,
            "phase": phase,
            "status": status,
            "blocking_reason": blocking_reason,
            "next_human_action": next_human_action,
            "updated_at": utc_now_iso(),
            "gate_restart": workflow_state_gate_restart(status, workflow, work_id, phase),
        }
    )
    if artifacts:
        state.setdefault("artifacts", {}).update(artifacts)
    if previous["phase"] or previous["status"]:
        state.setdefault("history", []).append(previous)
    write_json(state_path_for_work_dir(work_dir), state)
    return state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read or update workflow-state.json.")
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show")
    show.set_defaults(handler=run_show)

    set_state = sub.add_parser("set")
    set_state.add_argument("--workflow", required=True)
    set_state.add_argument("--work-id", required=True)
    set_state.add_argument("--phase", required=True)
    set_state.add_argument("--status", required=True, choices=sorted(VALID_STATUS))
    set_state.add_argument("--blocking-reason", default="")
    set_state.add_argument("--next-human-action", default="")
    set_state.set_defaults(handler=run_set)
    return parser


def resolve_work_dir(args: argparse.Namespace) -> tuple[Path, Path]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    raw = Path(args.work_dir)
    work_dir = raw if raw.is_absolute() else repo_root / raw
    return repo_root, work_dir


def run_show(args: argparse.Namespace) -> dict[str, Any]:
    repo_root, work_dir = resolve_work_dir(args)
    path = state_path_for_work_dir(work_dir)
    return {
        "status": "ok" if path.exists() else "missing",
        "state_path": relative_to_repo(repo_root, path),
        "state": read_json(path, default={}) or {},
    }


def run_set(args: argparse.Namespace) -> dict[str, Any]:
    repo_root, work_dir = resolve_work_dir(args)
    state = update_state(
        work_dir,
        workflow=args.workflow,
        work_id=args.work_id,
        phase=args.phase,
        status=args.status,
        blocking_reason=args.blocking_reason,
        next_human_action=args.next_human_action,
    )
    return {
        "status": "updated",
        "state_path": relative_to_repo(repo_root, state_path_for_work_dir(work_dir)),
        "state": state,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") not in {"failed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
