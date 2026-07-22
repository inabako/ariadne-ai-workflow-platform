from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def workflow_args(args: argparse.Namespace, repo_root: Path, command: str, **overrides: Any) -> argparse.Namespace:
    values = vars(args).copy()
    values["command"] = command
    values["repo_root"] = str(repo_root)
    values.update(overrides)
    return argparse.Namespace(**values)
