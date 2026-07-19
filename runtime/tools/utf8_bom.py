from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso  # noqa: E402


UTF8_BOM = b"\xef\xbb\xbf"
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan for and remove UTF-8 BOM from text files.")
    parser.add_argument("--repo-root", default="", help="Repository root. Defaults to auto-detection.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Find text files that start with a UTF-8 BOM.")
    add_path_arguments(scan)
    scan.add_argument("--fail-on-finding", action="store_true", help="Return exit code 1 when BOM files exist.")

    strip = subparsers.add_parser("strip", help="Remove UTF-8 BOM from matching text files.")
    add_path_arguments(strip)
    strip.add_argument("--write", action="store_true", help="Apply changes in place. Without this, only report candidates.")
    strip.add_argument(
        "--backup-suffix",
        default=".bom-bak",
        help="Suffix for backup files when --write is used. Empty value disables backups.",
    )
    strip.add_argument("--fail-on-finding", action="store_true", help="Return exit code 1 when BOM files exist.")
    return parser


def add_path_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["."],
        help="Files or directories to scan, relative to repo root unless absolute. Defaults to repository root.",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=sorted(TEXT_EXTENSIONS),
        help="Text file extensions to include when scanning directories.",
    )


def print_json(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    try:
        print(text, end="")
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8"))


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


def has_utf8_bom(raw: bytes) -> bool:
    return raw.startswith(UTF8_BOM)


def is_binary(raw: bytes) -> bool:
    return b"\x00" in raw


def scan_files(repo_root: Path, paths: Sequence[str], extensions: set[str]) -> dict[str, Any]:
    files = iter_target_files(repo_root, paths, extensions)
    bom_files: list[dict[str, Any]] = []
    skipped_binary: list[str] = []

    for path in files:
        raw = path.read_bytes()
        rel_path = relative_to_repo(repo_root, path)
        if is_binary(raw):
            skipped_binary.append(rel_path)
            continue
        if has_utf8_bom(raw):
            bom_files.append({"path": rel_path, "size_bytes": len(raw)})

    return {
        "schema_version": "1.0",
        "artifact_type": "utf8-bom-scan",
        "generated_at": utc_now_iso(),
        "status": "finding" if bom_files else "ok",
        "repo_root": str(repo_root),
        "paths": list(paths),
        "extensions": sorted(extensions),
        "files_scanned": len(files) - len(skipped_binary),
        "files_skipped_binary": skipped_binary,
        "bom_files": bom_files,
    }


def strip_files(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args.repo_root)
    extensions = {value if value.startswith(".") else f".{value}" for value in args.extensions}
    files = iter_target_files(repo_root, args.paths, extensions)
    stripped: list[dict[str, Any]] = []
    unchanged: list[str] = []
    skipped_binary: list[str] = []

    for path in files:
        raw = path.read_bytes()
        rel_path = relative_to_repo(repo_root, path)
        if is_binary(raw):
            skipped_binary.append(rel_path)
            continue
        if not has_utf8_bom(raw):
            unchanged.append(rel_path)
            continue

        record = {
            "path": rel_path,
            "written": False,
            "backup": "",
            "bytes_removed": len(UTF8_BOM),
        }
        if args.write:
            backup_path: Path | None = None
            if args.backup_suffix:
                backup_path = path.with_name(path.name + args.backup_suffix)
                if not backup_path.exists():
                    backup_path.write_bytes(raw)
            path.write_bytes(raw[len(UTF8_BOM) :])
            record["written"] = True
            record["backup"] = relative_to_repo(repo_root, backup_path) if backup_path is not None else ""
        stripped.append(record)

    return {
        "schema_version": "1.0",
        "artifact_type": "utf8-bom-strip",
        "generated_at": utc_now_iso(),
        "status": "stripped" if args.write and stripped else ("candidate" if stripped else "ok"),
        "repo_root": str(repo_root),
        "paths": list(args.paths),
        "extensions": sorted(extensions),
        "files_scanned": len(files) - len(skipped_binary),
        "files_skipped_binary": skipped_binary,
        "stripped": stripped,
        "unchanged": unchanged,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        repo_root = resolve_repo_root(args.repo_root)
        extensions = {value if value.startswith(".") else f".{value}" for value in args.extensions}
        payload = scan_files(repo_root, args.paths, extensions)
        print_json(payload)
        return 1 if args.fail_on_finding and payload["bom_files"] else 0
    if args.command == "strip":
        payload = strip_files(args)
        print_json(payload)
        return 1 if args.fail_on_finding and payload["stripped"] else 0
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
