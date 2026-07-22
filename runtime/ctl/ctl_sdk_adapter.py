from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.workflow import sdk_analysis


def run_sdk(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    return sdk_analysis.run(workflow_args(args, repo_root, command))


def format_result(result: dict[str, Any]) -> str:
    return sdk_analysis.format_result(result)
