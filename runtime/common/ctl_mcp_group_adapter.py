from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.common.ctl_adapter_utils import workflow_args
from runtime.workflow import mcp_server_group


def run_mcp_group(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    return mcp_server_group.run(workflow_args(args, repo_root, command))


def format_result(result: dict[str, Any]) -> str:
    return mcp_server_group.format_result(result)
