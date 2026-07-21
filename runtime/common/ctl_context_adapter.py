from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from runtime.common.ctl_adapter_utils import workflow_args
from runtime.workflow import context_first, dispatcher_context


CONTEXT_HANDLERS: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "show": context_first.run_show,
    "require": context_first.run_require,
    "require-environment": context_first.run_require_environment,
}


def run_context(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    if command == "init":
        return dispatcher_context.run_init(args)
    handler = CONTEXT_HANDLERS.get(command)
    if handler is None:
        raise KeyError(f"Unknown context command: {command}")
    return handler(workflow_args(args, repo_root, command))
