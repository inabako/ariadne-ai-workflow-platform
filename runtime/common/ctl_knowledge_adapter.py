from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.common.ctl_adapter_utils import workflow_args
from runtime.rag import duckdb_store


def run_knowledge(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    return duckdb_store.run(workflow_args(args, repo_root, command))
