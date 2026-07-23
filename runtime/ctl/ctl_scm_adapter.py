from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.scm import (
    bootstrap_repository,
    commit_changes,
    compare_requirements,
    create_issue_branch,
    prepare_repository,
    prepare_support_repository,
    push_branch,
)


def run_scm(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    command_args = workflow_args(args, repo_root, command)
    if command == "prepare":
        return prepare_repository.prepare_repository(command_args)
    if command == "support":
        return prepare_support_repository.prepare_support_repository(command_args)
    if command == "compare":
        return compare_requirements.compare_requirements(command_args)
    if command == "branch":
        return create_issue_branch.create_branch(command_args)
    if command == "commit":
        return commit_changes.commit_changes(command_args)
    if command == "push":
        return push_branch.push_branch(command_args)
    if command == "bootstrap":
        return bootstrap_repository.bootstrap_repository(command_args)
    raise KeyError(command)
