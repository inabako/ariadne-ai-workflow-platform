from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.workflow import iac_deployment_runtime
from runtime.workflow import iac_prepare_runtime
from runtime.workflow import iac_template
from runtime.workflow import kubernetes_runtime


def run_iac_template(args: argparse.Namespace, repo_root: Path, command: str | None) -> dict[str, Any]:
    if command == "list":
        return iac_template.list_templates(repo_root)
    if command == "prepare":
        return iac_template.prepare_template(
            repo_root,
            template=args.template,
            work_id=args.work_id,
            work_dir=args.work_dir,
            force=args.force,
        )
    if command == "health":
        return iac_template.health_template(
            repo_root,
            template=args.template,
            work_id=args.work_id,
            work_dir=args.work_dir,
            probe_tools=args.probe_tools,
        )
    raise KeyError(f"Unknown IaC template command: {command}")


def run_iac_kubernetes(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    return kubernetes_runtime.run(args, repo_root)


def format_kubernetes_result(result: dict[str, Any]) -> str:
    return kubernetes_runtime.format_result(result)


def run_iac_deployment(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    return iac_deployment_runtime.run(args, repo_root)


def format_deployment_result(result: dict[str, Any]) -> str:
    return iac_deployment_runtime.format_result(result)


def run_iac_prepare(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    return iac_prepare_runtime.run(args, repo_root)


def format_prepare_result(result: dict[str, Any]) -> str:
    return iac_prepare_runtime.format_result(result)
