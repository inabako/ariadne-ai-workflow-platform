from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.workflow import work_cleanup


def run_work_cleanup(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    return work_cleanup.run(workflow_args(args, repo_root, command))
