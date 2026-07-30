from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.github import issue_manager, pull_request_manager


def run_github(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    command_args = workflow_args(args, repo_root, command)
    if command == "issue":
        return issue_manager.manage_issue(command_args)
    if command == "pr":
        return pull_request_manager.manage_pull_request(command_args)
    raise KeyError(command)
