from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.intake import intake_requirements


def run_intake(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    if command != "run":
        raise KeyError(command)
    return intake_requirements.run(workflow_args(args, repo_root, command))
