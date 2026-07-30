from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.workflow import self_improvement


SELF_IMPROVEMENT_HANDLERS: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "init-feedback": self_improvement.run_init_feedback,
    "create-feedback": self_improvement.run_create_feedback,
    "review-feedback": self_improvement.run_review_feedback,
    "issue-body": self_improvement.run_issue_body,
    "branch-name": self_improvement.run_branch_name,
    "evidence-scaffold": self_improvement.run_evidence_scaffold,
}


def run_self_improvement(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    handler = SELF_IMPROVEMENT_HANDLERS.get(command)
    if handler is None:
        raise KeyError(f"Unknown self-improvement command: {command}")
    return handler(workflow_args(args, repo_root, command))
