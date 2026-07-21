from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.common.ctl_adapter_utils import workflow_args
from runtime.workflow import human_gate_policy


def run_human_gate(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    gate_args = workflow_args(args, repo_root, command)
    if command == "list":
        return human_gate_policy.run_list(gate_args)
    if command == "check":
        return human_gate_policy.run_check(gate_args)
    raise KeyError(f"Unknown human-gate command: {command}")
