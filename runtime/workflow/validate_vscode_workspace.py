from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


DEFAULT_FILES = [
    ".vscode/settings.json",
    ".vscode/tasks.json",
    ".vscode/launch.json",
    ".vscode/extensions.json",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate VSCode workspace JSON files.")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root. Default: current directory.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="JSON files relative to the workspace. Defaults to this repository's VSCode files.",
    )
    return parser


def validate_file(path: Path) -> None:
    json.loads(path.read_text(encoding="utf-8-sig"))


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workspace = Path(args.workspace).resolve()
    files = args.files or DEFAULT_FILES
    validated: list[str] = []
    for raw_path in files:
        path = workspace / raw_path
        validate_file(path)
        validated.append(raw_path)
    print("VSCode JSON OK")
    for item in validated:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
