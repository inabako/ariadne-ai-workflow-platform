from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.observability.metrics import RuntimeMetricsCollector
from runtime.workflow import github_knowledge_maintenance


GITHUB_KNOWLEDGE_COMMAND_MAP = {
    "init": "init",
    "analysis-template": "analysis-template",
    "artifact-integrity": "artifact-integrity",
    "status": "status",
    "next-action": "next-action",
    "resume": "resume",
    "verify-remote": "verify-remote",
    "cleanup-worktree": "cleanup-worktree",
    "repair-plan": "repair-plan",
    "detect-rebase": "detect-rebase-candidates",
    "rebase-plan": "rebase-plan",
    "rebase-review-intake": "rebase-review-intake",
    "message-repair-plan": "message-repair-plan",
    "message-review-intake": "message-review-intake",
    "sync-plan": "github-sync-plan",
    "sync-review-plan": "github-sync-review-plan",
    "sync-review-intake": "github-sync-review-intake",
    "sync-apply": "github-sync-apply",
    "rebase-package": "rebase-replay-package",
    "message-repair-package": "message-repair-package",
    "rebase-apply": "rebase-replay-apply",
    "publish-verified-replay": "publish-verified-replay",
    "rag-candidate": "rag-candidate",
}


MetricsFactory = Callable[[Path, str], RuntimeMetricsCollector]
MetricsRecorder = Callable[..., None]


def resolve_runtime_command(command: str) -> str:
    try:
        return GITHUB_KNOWLEDGE_COMMAND_MAP[command]
    except KeyError as exc:
        raise KeyError(f"Unknown GitHub knowledge command: {command}") from exc


def run_github_knowledge(
    args: argparse.Namespace,
    repo_root: Path,
    command: str,
    *,
    metrics_factory: MetricsFactory,
    metrics_recorder: MetricsRecorder,
) -> dict[str, Any]:
    runtime_command = resolve_runtime_command(command)
    metrics = metrics_factory(repo_root, work_id=str(getattr(args, "work_id", "") or ""))
    metrics.workflow_started(metadata={"ctl_command": f"github-knowledge {command}"})
    try:
        result = github_knowledge_maintenance.run(workflow_args(args, repo_root, runtime_command))
        metrics_recorder(metrics, repo_root, command_name=command, result=result)
        return result
    except Exception as exc:
        metrics.runtime_error(error=str(exc))
        metrics.workflow_failed(error=str(exc))
        raise
