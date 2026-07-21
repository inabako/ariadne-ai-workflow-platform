from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from runtime.common.ctl_adapter_utils import workflow_args
from runtime.workflow import close_archive


CLOSE_ARCHIVE_HANDLERS: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "audit": close_archive.run_audit,
    "prepare": close_archive.run_prepare,
    "prune": close_archive.run_prune,
}


def run_close_archive(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    handler = CLOSE_ARCHIVE_HANDLERS.get(command)
    if handler is None:
        raise KeyError(f"Unknown close-archive command: {command}")
    return handler(workflow_args(args, repo_root, command))
