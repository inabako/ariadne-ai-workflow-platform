from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.workflow import gui_mode
from runtime.workflow import web_svg_layout_mode


def run_gui(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    command_args = workflow_args(args, repo_root, command)
    if command == "init-input":
        return gui_mode.run_init_input(command_args)
    if command == "inspect-input":
        return gui_mode.run_inspect_input(command_args)
    if command == "run":
        return gui_mode.run_generate(command_args)
    if command == "validate":
        return gui_mode.run_validate(command_args)
    if command == "self-test":
        return gui_mode.run_self_test(command_args)
    raise KeyError(command)


def run_web_svg(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    command_args = workflow_args(args, repo_root, command)
    if command == "init-input":
        return web_svg_layout_mode.run_init_input(command_args)
    if command == "run":
        return web_svg_layout_mode.run_generate(command_args)
    if command == "validate":
        return web_svg_layout_mode.run_validate(command_args)
    raise KeyError(command)
