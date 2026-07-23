from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import gate_restart, registry_store  # noqa: E402
from runtime.common import find_repo_root, relative_to_repo  # noqa: E402


def registry_path(repo_root: Path) -> Path:
    return registry_store.registry_db_path(repo_root)


def load_registry(repo_root: Path) -> dict[str, Any]:
    data = registry_store.load_human_gates(repo_root)
    data.setdefault("registry_version", "1.0")
    data.setdefault("gates", [])
    return data


def find_gate(registry: dict[str, Any], gate_id: str) -> dict[str, Any]:
    for gate in registry.get("gates", []):
        if gate.get("id") == gate_id:
            return gate
    raise KeyError(f"Unknown human gate: {gate_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect and enforce Human Gate Registry.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list")
    list_cmd.set_defaults(handler=run_list)

    check = sub.add_parser("check")
    check.add_argument("--gate", required=True)
    check.add_argument("--human-check", default="pending")
    check.set_defaults(handler=run_check)
    return parser


def repo_root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve() if args.repo_root else find_repo_root()


def run_list(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from_args(args)
    registry = load_registry(repo_root)
    return {
        "status": "ok",
        "registry": relative_to_repo(repo_root, registry_path(repo_root)),
        "gates": registry.get("gates", []),
        "gate_restart": gate_restart.build_status_gate_restart(
            "human-gate-registry-gate",
            status="ok",
            restart_reason="human-gate-registry",
        ),
    }


def run_check(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from_args(args)
    gate = find_gate(load_registry(repo_root), args.gate)
    approved = args.human_check == gate.get("approved_value", "approved")
    if gate.get("requires_human_check", True) and not approved:
        return {
            "status": "blocked",
            "gate": args.gate,
            "required": gate.get("approved_value", "approved"),
            "actual": args.human_check,
            "reason": gate.get("reason", ""),
            "gate_restart": gate_restart.build_status_gate_restart(
                "human-gate-check",
                status="blocked",
                restart_reason=args.gate,
                repair_command=(
                    "uv run --project runtime python runtime/ctl/ctl.py --repo-root . "
                    f"human-gate check --gate {args.gate} --human-check {gate.get('approved_value', 'approved')}"
                ),
            ),
        }
    return {
        "status": "approved",
        "gate": args.gate,
        "actual": args.human_check,
        "gate_restart": gate_restart.build_status_gate_restart(
            "human-gate-check",
            status="approved",
            restart_reason=args.gate,
        ),
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
    return 0 if result.get("status") != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
