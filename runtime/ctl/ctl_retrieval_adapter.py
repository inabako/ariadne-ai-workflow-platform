from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.retrieval import task_runner


def run_retrieval(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    if command != "run":
        raise KeyError(command)
    task_file = Path(args.task_file)
    if not task_file.is_absolute():
        task_file = repo_root / task_file
    return task_runner.run(
        argparse.Namespace(
            work_id=args.work_id,
            task_file=str(task_file),
            repo_root=str(repo_root),
            mode=args.mode,
            max_workers=args.max_workers,
            dry_run=args.dry_run,
            stop_on_failure=args.stop_on_failure,
        )
    )
