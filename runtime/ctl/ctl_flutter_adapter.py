from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.workflow import flutter_multiplatform


def run_flutter(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    return flutter_multiplatform.run(workflow_args(args, repo_root, command))


def format_result(result: dict[str, Any]) -> str:
    return flutter_multiplatform.format_result(result)
