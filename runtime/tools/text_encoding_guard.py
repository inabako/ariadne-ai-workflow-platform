from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso  # noqa: E402


TEXT_EXTENSIONS = {
    ".cfg",
    ".cmd",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
LOSSY_MARKER_RE = re.compile(r"\ufffd|\?{3,}")


@dataclass(frozen=True)
class TextFile:
    path: Path
    text: str
    decode_error: str | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect UTF-8 decode errors and irreversible text loss markers."
    )
    parser.add_argument("--repo-root", default="", help="Repository root. Defaults to auto-detection.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan text files for mojibake-like damage.")
    add_path_arguments(scan)
    scan.add_argument("--fail-on-finding", action="store_true", help="Return exit code 1 when findings exist.")
    return parser


def add_path_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["docs"],
        help="Files or directories to scan, relative to repo root unless absolute. Defaults to docs.",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=sorted(TEXT_EXTENSIONS),
        help="Text file extensions to include when scanning directories.",
    )


def resolve_repo_root(value: str | Path | None) -> Path:
    if value:
        return Path(value).resolve()
    return find_repo_root()


def resolve_path(repo_root: Path, value: str | Path) -> Path:
    raw = Path(value)
    return raw.resolve() if raw.is_absolute() else (repo_root / raw).resolve()


def should_skip_path(path: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts)


def iter_target_files(repo_root: Path, paths: Sequence[str], extensions: set[str]) -> list[Path]:
    files: list[Path] = []
    for value in paths:
        path = resolve_path(repo_root, value)
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix.lower() in extensions and not should_skip_path(path):
                files.append(path)
            continue
        for child in path.rglob("*"):
            if child.is_file() and child.suffix.lower() in extensions and not should_skip_path(child):
                files.append(child)
    return sorted(set(files))


def read_text_file(path: Path) -> TextFile | None:
    raw = path.read_bytes()
    if b"\x00" in raw:
        return None
    try:
        return TextFile(path=path, text=raw.decode("utf-8-sig"))
    except UnicodeDecodeError as exc:
        return TextFile(path=path, text=raw.decode("utf-8", errors="replace"), decode_error=str(exc))


def line_snippet(line: str, marker: str, width: int = 90) -> str:
    index = line.find(marker)
    if index < 0:
        return line[:width]
    start = max(0, index - width // 2)
    return line[start : start + width]


def findings_for_text(repo_root: Path, path: Path, text: str, decode_error: str | None = None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    rel_path = relative_to_repo(repo_root, path)
    if decode_error:
        findings.append(
            {
                "path": rel_path,
                "line": 1,
                "kind": "decode-error",
                "marker": "utf-8",
                "snippet": decode_error,
                "repairable": False,
            }
        )
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in LOSSY_MARKER_RE.finditer(line):
            findings.append(
                {
                    "path": rel_path,
                    "line": line_no,
                    "kind": "lossy-marker",
                    "marker": match.group(0),
                    "snippet": line_snippet(line, match.group(0)),
                    "repairable": False,
                }
            )
    return findings


def scan_files(repo_root: Path, paths: Sequence[str], extensions: set[str]) -> dict[str, Any]:
    files = iter_target_files(repo_root, paths, extensions)
    findings: list[dict[str, Any]] = []
    skipped_binary: list[str] = []

    for path in files:
        text_file = read_text_file(path)
        if text_file is None:
            skipped_binary.append(relative_to_repo(repo_root, path))
            continue
        file_findings = findings_for_text(repo_root, path, text_file.text, text_file.decode_error)
        findings.extend(file_findings)

    return {
        "schema_version": "1.0",
        "artifact_type": "text-encoding-guard",
        "generated_at": utc_now_iso(),
        "status": "finding" if findings else "ok",
        "repo_root": str(repo_root),
        "paths": list(paths),
        "extensions": sorted(extensions),
        "files_scanned": len(files) - len(skipped_binary),
        "files_skipped_binary": skipped_binary,
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        repo_root = resolve_repo_root(args.repo_root)
        extensions = {value if value.startswith(".") else f".{value}" for value in args.extensions}
        payload = scan_files(repo_root, args.paths, extensions)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1 if args.fail_on_finding and payload["status"] == "finding" else 0
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
