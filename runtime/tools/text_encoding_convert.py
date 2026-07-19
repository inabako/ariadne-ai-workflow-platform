from __future__ import annotations

import argparse
import json
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
DEFAULT_INSPECT_ENCODINGS = (
    "cp932",
    "shift_jis",
    "utf-8-sig",
    "utf-8",
    "euc_jp",
    "iso2022_jp",
    "latin1",
    "cp1252",
)
EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}


@dataclass(frozen=True)
class DecodeCandidate:
    encoding: str
    ok: bool
    error: str = ""
    text: str = ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect text encodings and safely convert files to UTF-8.")
    parser.add_argument("--repo-root", default="", help="Repository root. Defaults to auto-detection.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect = subparsers.add_parser("inspect", help="Try candidate encodings with strict decoding.")
    add_path_arguments(inspect)
    inspect.add_argument(
        "--encodings",
        nargs="+",
        default=list(DEFAULT_INSPECT_ENCODINGS),
        help="Candidate source encodings to try with strict decoding.",
    )
    inspect.add_argument("--fail-on-warning", action="store_true", help="Return exit code 1 when warnings exist.")

    preview = subparsers.add_parser("preview", help="Show hex bytes and short decode previews for candidate encodings.")
    add_path_arguments(preview)
    preview.add_argument(
        "--encodings",
        nargs="+",
        default=list(DEFAULT_INSPECT_ENCODINGS),
        help="Candidate source encodings to try with strict decoding.",
    )
    preview.add_argument("--bytes", type=int, default=160, help="Maximum bytes to include in the hex preview.")
    preview.add_argument("--chars", type=int, default=120, help="Maximum decoded characters per encoding preview.")
    preview.add_argument("--fail-on-warning", action="store_true", help="Return exit code 1 when warnings exist.")

    convert = subparsers.add_parser("convert", help="Safely convert text files from a source encoding to UTF-8.")
    add_path_arguments(convert)
    convert.add_argument("--from-encoding", default="cp932", help="Source encoding. Defaults to cp932.")
    convert.add_argument("--to-encoding", default="utf-8", help="Target encoding. Defaults to utf-8.")
    convert.add_argument("--write", action="store_true", help="Apply conversion in place.")
    convert.add_argument(
        "--backup-suffix",
        default=".encoding-bak",
        help="Suffix for backup files when --write is used. Empty value disables backups.",
    )
    convert.add_argument(
        "--force",
        action="store_true",
        help="Convert even when the file already decodes as UTF-8.",
    )
    convert.add_argument("--fail-on-blocked", action="store_true", help="Return exit code 1 when conversion is blocked.")
    return parser


def print_json(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    try:
        print(text, end="")
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8"))


def add_path_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["docs"],
        help="Files or directories to inspect, relative to repo root unless absolute. Defaults to docs.",
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


def try_decode(raw: bytes, encoding: str) -> DecodeCandidate:
    try:
        text = raw.decode(encoding)
    except UnicodeError as exc:
        return DecodeCandidate(encoding=encoding, ok=False, error=str(exc))
    return DecodeCandidate(encoding=encoding, ok=True, text=text)


def decode_candidates(raw: bytes, encodings: Sequence[str]) -> list[DecodeCandidate]:
    seen: set[str] = set()
    candidates: list[DecodeCandidate] = []
    for encoding in encodings:
        normalized = encoding.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(try_decode(raw, encoding))
    return candidates


def candidate_payload(candidate: DecodeCandidate) -> dict[str, Any]:
    payload = {
        "encoding": candidate.encoding,
        "ok": candidate.ok,
    }
    if not candidate.ok:
        payload["error"] = candidate.error
    return payload


def preview_payload(candidate: DecodeCandidate, max_chars: int) -> dict[str, Any]:
    payload = candidate_payload(candidate)
    if candidate.ok:
        payload["text"] = candidate.text[:max_chars]
        payload["truncated"] = len(candidate.text) > max_chars
    return payload


def classify_decodes(ok_encodings: Sequence[str]) -> str:
    normalized = {encoding.lower() for encoding in ok_encodings}
    utf8_names = {"utf-8", "utf-8-sig"}
    if not ok_encodings:
        return "undecodable"
    if normalized & utf8_names:
        if len(normalized - utf8_names) > 0:
            return "utf8-compatible-with-other-decoders"
        return "utf8"
    return "non-utf8-candidate"


def inspect_files(repo_root: Path, paths: Sequence[str], extensions: set[str], encodings: Sequence[str]) -> dict[str, Any]:
    files = iter_target_files(repo_root, paths, extensions)
    inspected: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    skipped_binary: list[str] = []

    for path in files:
        raw = path.read_bytes()
        rel_path = relative_to_repo(repo_root, path)
        if b"\x00" in raw:
            skipped_binary.append(rel_path)
            continue
        candidates = decode_candidates(raw, encodings)
        ok_encodings = [candidate.encoding for candidate in candidates if candidate.ok]
        if not ok_encodings:
            warnings.append({"path": rel_path, "kind": "decode-failed", "message": "No candidate encoding decoded cleanly."})
        inspected.append(
            {
                "path": rel_path,
                "preferred_encoding": ok_encodings[0] if ok_encodings else "",
                "ok_encodings": ok_encodings,
                "classification": classify_decodes(ok_encodings),
                "candidates": [candidate_payload(candidate) for candidate in candidates],
            }
        )

    return {
        "schema_version": "1.0",
        "artifact_type": "text-encoding-inspect",
        "generated_at": utc_now_iso(),
        "status": "warning" if warnings else "ok",
        "repo_root": str(repo_root),
        "paths": list(paths),
        "extensions": sorted(extensions),
        "encodings": list(encodings),
        "files_inspected": len(files) - len(skipped_binary),
        "files_skipped_binary": skipped_binary,
        "files": inspected,
        "warnings": warnings,
    }


def preview_files(
    repo_root: Path,
    paths: Sequence[str],
    extensions: set[str],
    encodings: Sequence[str],
    *,
    max_bytes: int,
    max_chars: int,
) -> dict[str, Any]:
    files = iter_target_files(repo_root, paths, extensions)
    previews: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    skipped_binary: list[str] = []

    for path in files:
        raw = path.read_bytes()
        rel_path = relative_to_repo(repo_root, path)
        if b"\x00" in raw:
            skipped_binary.append(rel_path)
            continue
        candidates = decode_candidates(raw, encodings)
        ok_encodings = [candidate.encoding for candidate in candidates if candidate.ok]
        classification = classify_decodes(ok_encodings)
        if classification == "undecodable":
            warnings.append({"path": rel_path, "kind": "decode-failed", "message": "No candidate encoding decoded cleanly."})
        previews.append(
            {
                "path": rel_path,
                "size_bytes": len(raw),
                "hex_bytes": raw[:max_bytes].hex(" "),
                "hex_truncated": len(raw) > max_bytes,
                "preferred_encoding": ok_encodings[0] if ok_encodings else "",
                "ok_encodings": ok_encodings,
                "classification": classification,
                "previews": [preview_payload(candidate, max_chars) for candidate in candidates],
            }
        )

    return {
        "schema_version": "1.0",
        "artifact_type": "text-encoding-preview",
        "generated_at": utc_now_iso(),
        "status": "warning" if warnings else "ok",
        "repo_root": str(repo_root),
        "paths": list(paths),
        "extensions": sorted(extensions),
        "encodings": list(encodings),
        "max_bytes": max_bytes,
        "max_chars": max_chars,
        "files_previewed": len(files) - len(skipped_binary),
        "files_skipped_binary": skipped_binary,
        "files": previews,
        "warnings": warnings,
    }


def convert_files(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args.repo_root)
    extensions = {value if value.startswith(".") else f".{value}" for value in args.extensions}
    files = iter_target_files(repo_root, args.paths, extensions)
    converted: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    unchanged: list[dict[str, Any]] = []
    skipped_binary: list[str] = []

    for path in files:
        raw = path.read_bytes()
        rel_path = relative_to_repo(repo_root, path)
        if b"\x00" in raw:
            skipped_binary.append(rel_path)
            continue

        try:
            source_text = raw.decode(args.from_encoding)
        except UnicodeError as exc:
            blocked.append({"path": rel_path, "reason": "source-decode-failed", "error": str(exc)})
            continue

        if not args.force and args.from_encoding.lower() not in {"utf-8", "utf-8-sig"}:
            try:
                raw.decode("utf-8-sig")
            except UnicodeError:
                pass
            else:
                blocked.append({"path": rel_path, "reason": "already-decodes-as-utf8"})
                continue

        try:
            converted_raw = source_text.encode(args.to_encoding)
            verified_text = converted_raw.decode(args.to_encoding)
        except UnicodeError as exc:
            blocked.append({"path": rel_path, "reason": "target-encode-verify-failed", "error": str(exc)})
            continue
        if verified_text != source_text:
            blocked.append({"path": rel_path, "reason": "target-roundtrip-changed-text"})
            continue
        if converted_raw == raw:
            unchanged.append({"path": rel_path, "from_encoding": args.from_encoding, "to_encoding": args.to_encoding})
            continue

        record = {
            "path": rel_path,
            "from_encoding": args.from_encoding,
            "to_encoding": args.to_encoding,
            "written": False,
            "backup": "",
        }
        if args.write:
            backup_path = Path()
            if args.backup_suffix:
                backup_path = path.with_name(path.name + args.backup_suffix)
                if not backup_path.exists():
                    backup_path.write_bytes(raw)
            path.write_bytes(converted_raw)
            record["written"] = True
            record["backup"] = relative_to_repo(repo_root, backup_path) if backup_path else ""
        converted.append(record)

    return {
        "schema_version": "1.0",
        "artifact_type": "text-encoding-convert",
        "generated_at": utc_now_iso(),
        "status": "blocked" if blocked else ("converted" if converted and args.write else ("candidate" if converted else "ok")),
        "repo_root": str(repo_root),
        "paths": list(args.paths),
        "files_skipped_binary": skipped_binary,
        "converted": converted,
        "unchanged": unchanged,
        "blocked": blocked,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inspect":
        repo_root = resolve_repo_root(args.repo_root)
        extensions = {value if value.startswith(".") else f".{value}" for value in args.extensions}
        payload = inspect_files(repo_root, args.paths, extensions, args.encodings)
        print_json(payload)
        return 1 if args.fail_on_warning and payload["warnings"] else 0
    if args.command == "preview":
        repo_root = resolve_repo_root(args.repo_root)
        extensions = {value if value.startswith(".") else f".{value}" for value in args.extensions}
        payload = preview_files(
            repo_root,
            args.paths,
            extensions,
            args.encodings,
            max_bytes=max(0, args.bytes),
            max_chars=max(0, args.chars),
        )
        print_json(payload)
        return 1 if args.fail_on_warning and payload["warnings"] else 0

    payload = convert_files(args)
    print_json(payload)
    return 1 if args.fail_on_blocked and payload["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
