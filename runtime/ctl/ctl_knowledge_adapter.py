from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import save_plan_output_if_requested
from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.rag import duckdb_store


def _display_path(value: object) -> str:
    return str(value).replace("\\", "/") if value not in {None, ""} else ""


def duckdb_dry_run_plan(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    parent_command = "rag duckdb" if getattr(args, "rag_command", "") == "duckdb" else "knowledge"
    dry_args = workflow_args(args, repo_root, command)
    reads: list[dict[str, str]] = []
    writes: list[dict[str, str]] = []
    for source in getattr(dry_args, "source", []) or []:
        reads.append({"role": "source", "path": _display_path(source)})
    for attr in ["source_repo", "policy"]:
        value = _display_path(getattr(dry_args, attr, ""))
        if value:
            reads.append({"role": attr.replace("_", "-"), "path": value})
    for attr in ["db", "error_log", "output"]:
        value = _display_path(getattr(dry_args, attr, ""))
        if value:
            writes.append({"role": attr.replace("_", "-"), "path": value})
    if getattr(dry_args, "reset", False):
        writes.append({"role": "reset-generated-read-model", "path": _display_path(getattr(dry_args, "db", ""))})

    result = {
        "schema_version": "1.0",
        "artifact_type": "rag-dry-run-plan",
        "status": "dry-run",
        "command": f"{parent_command} {command}",
        "repo_root": str(repo_root),
        "would_run": False,
        "reads": [item for item in reads if item.get("path")],
        "writes": [item for item in writes if item.get("path")],
        "options": {
            "reset": bool(getattr(dry_args, "reset", False)),
        },
        "next_action": "内容を確認し、問題なければ --dry-run を外して同じコマンドを実行してください。",
    }
    return save_plan_output_if_requested(args, repo_root, result)


def run_knowledge(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    if getattr(args, "dry_run", False):
        return duckdb_dry_run_plan(args, repo_root, command)
    return duckdb_store.run(workflow_args(args, repo_root, command))
