from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.review import council


REVIEW_HANDLERS: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "plan": council.plan_review,
    "start": council.start_review,
    "handoff": council.handoff_review,
    "orchestrate": council.orchestrate_review,
    "next-action": council.next_action_review,
    "summary": council.summary_review,
    "human-gate": council.human_gate_review,
    "run-specialist": council.run_specialist_review,
    "execute-specialist": council.execute_specialist_review,
    "draft-findings": council.draft_findings_review,
    "capture-knowledge": council.capture_review_knowledge,
    "rag-build": council.rag_build_review,
    "add-finding": council.add_finding,
    "challenge": council.challenge_review,
    "evidence-gate": council.evidence_gate,
    "reinspect": council.reinspect_review,
    "status": council.status_review,
    "issues": council.list_issues,
    "inspect": council.inspect_review,
    "verdict": council.decide_verdict,
}


def run_review(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    handler = REVIEW_HANDLERS.get(command)
    if handler is None:
        raise KeyError(f"Unknown review command: {command}")
    return handler(workflow_args(args, repo_root, command))
