from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.workflow import iac_template


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
