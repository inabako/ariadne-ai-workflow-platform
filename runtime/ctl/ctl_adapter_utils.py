from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class StoreWithExplicitFlag(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        setattr(namespace, self.dest, values)
        setattr(namespace, f"{self.dest}_explicit", True)


def add_output_argument(
    command: argparse.ArgumentParser,
    *,
    default: str = "",
    required: bool = False,
    help: str = "",
) -> None:
    command.add_argument(
        "--output",
        default=default,
        required=required,
        action=StoreWithExplicitFlag,
        help=help,
    )


def workflow_args(args: argparse.Namespace, repo_root: Path, command: str, **overrides: Any) -> argparse.Namespace:
    values = vars(args).copy()
    values["command"] = command
    values["repo_root"] = str(repo_root)
    values.update(overrides)
    return argparse.Namespace(**values)


def output_was_explicit(args: argparse.Namespace, name: str = "output") -> bool:
    return bool(getattr(args, f"{name}_explicit", False))


def write_json_output(repo_root: Path, output: str, payload: dict[str, Any]) -> str:
    raw = Path(output)
    path = raw if raw.is_absolute() else repo_root / raw
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def save_plan_output_if_requested(
    args: argparse.Namespace,
    repo_root: Path,
    result: dict[str, Any],
    *,
    require_explicit: bool = True,
) -> dict[str, Any]:
    output = str(getattr(args, "output", "") or "").strip()
    if not output:
        return result
    if require_explicit and not output_was_explicit(args):
        return result
    saved = dict(result)
    raw = Path(output)
    path = raw if raw.is_absolute() else repo_root / raw
    try:
        plan_output = str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        plan_output = str(path)
    saved["plan_output"] = plan_output
    saved["written"] = False
    write_json_output(repo_root, output, {**saved, "written": True})
    saved["written"] = True
    return saved
