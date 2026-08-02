from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.testing import e2e_runtime


def run_e2e(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    return e2e_runtime.run(workflow_args(args, repo_root, command))


def format_result(result: dict[str, Any]) -> str:
    return e2e_runtime.format_result(result)
