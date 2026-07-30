from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from runtime.constants.runtime_values import SCHEMA_VERSION
from runtime.common.common import relative_to_repo, utc_now_iso
from runtime.constants.encoding import MOJIBAKE_MARKERS, SOURCE_ENCODINGS

TEXT_EXTENSIONS = {
    ".cfg",
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
DEFAULT_PATHS = [".github", "docs", "runtime", "skills", "templates"]
ALLOW_MOJIBAKE_EXAMPLE = "text-boundary: allow-mojibake-example"


def normalize_extensions(values: Sequence[str] | None = None) -> set[str]:
    source = values or sorted(TEXT_EXTENSIONS)
    return {value if value.startswith(".") else f".{value}" for value in source}


def should_skip_path(path: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts)


def resolve_path(repo_root: Path, value: str | Path) -> Path:
    raw = Path(value)
    return raw.resolve() if raw.is_absolute() else (repo_root / raw).resolve()


def iter_text_files(repo_root: Path, paths: Sequence[str], extensions: set[str]) -> list[Path]:
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


def marker_count(text: str) -> int:
    return sum(text.count(marker) for marker in MOJIBAKE_MARKERS)


def line_snippet(line: str, width: int = 100) -> str:
    return line[:width]


def recover_mojibake_line(line: str) -> str | None:
    if marker_count(line) == 0:
        return None
    for encoding in SOURCE_ENCODINGS:
        try:
            recovered = line.encode(encoding).decode("utf-8")
        except UnicodeError:
            continue
        if recovered != line and marker_count(recovered) < marker_count(line):
            return recovered
    return None


def decode_non_utf8(raw: bytes) -> tuple[str, str] | None:
    for encoding in SOURCE_ENCODINGS:
        try:
            return encoding, raw.decode(encoding)
        except UnicodeError:
            continue
    return None


def file_findings(repo_root: Path, path: Path) -> tuple[list[dict[str, Any]], str | None]:
    raw = path.read_bytes()
    rel_path = relative_to_repo(repo_root, path)
    findings: list[dict[str, Any]] = []
    if b"\x00" in raw:
        return findings, None
    if raw.startswith(b"\xef\xbb\xbf"):
        findings.append(
            {
                "path": rel_path,
                "line": 1,
                "kind": "utf8-bom",
                "repairable": True,
                "snippet": "UTF-8 BOM",
            }
        )
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        decoded = decode_non_utf8(raw)
        findings.append(
            {
                "path": rel_path,
                "line": 1,
                "kind": "utf8-decode-failed",
                "repairable": decoded is not None,
                "snippet": str(exc),
            }
        )
        return findings, decoded[1] if decoded else None

    for line_number, line in enumerate(text.splitlines(), start=1):
        if ALLOW_MOJIBAKE_EXAMPLE in line:
            continue
        if marker_count(line) == 0:
            continue
        findings.append(
            {
                "path": rel_path,
                "line": line_number,
                "kind": "semantic-mojibake-marker",
                "repairable": recover_mojibake_line(line) is not None,
                "snippet": line_snippet(line),
            }
        )
    return findings, text


def scan_text_boundary(repo_root: Path, paths: Sequence[str], extensions: set[str]) -> dict[str, Any]:
    files = iter_text_files(repo_root, paths, extensions)
    findings: list[dict[str, Any]] = []
    skipped_binary: list[str] = []
    for path in files:
        raw = path.read_bytes()
        if b"\x00" in raw:
            skipped_binary.append(relative_to_repo(repo_root, path))
            continue
        file_result, _text = file_findings(repo_root, path)
        findings.extend(file_result)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "text-boundary-scan",
        "generated_at": utc_now_iso(),
        "status": "finding" if findings else "ok",
        "paths": list(paths),
        "extensions": sorted(extensions),
        "files_scanned": len(files) - len(skipped_binary),
        "files_skipped_binary": skipped_binary,
        "findings": findings,
    }


def repair_text_boundary(
    repo_root: Path,
    paths: Sequence[str],
    extensions: set[str],
    *,
    backup_suffix: str = ".encoding-bak",
    write: bool = True,
) -> dict[str, Any]:
    files = iter_text_files(repo_root, paths, extensions)
    repairs: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for path in files:
        raw = path.read_bytes()
        rel_path = relative_to_repo(repo_root, path)
        if b"\x00" in raw:
            continue
        findings, text = file_findings(repo_root, path)
        if not findings:
            continue
        if text is None:
            blocked.append({"path": rel_path, "reason": "no-safe-decode"})
            continue

        changed_kinds: list[str] = []
        new_text = text
        if raw.startswith(b"\xef\xbb\xbf"):
            changed_kinds.append("utf8-bom")
        if any(item["kind"] == "utf8-decode-failed" and item["repairable"] for item in findings):
            changed_kinds.append("decode-to-utf8")
        recovered_lines: list[str] = []
        line_changed = False
        for line in new_text.splitlines():
            recovered = recover_mojibake_line(line)
            if recovered is None:
                recovered_lines.append(line)
                continue
            recovered_lines.append(recovered)
            line_changed = True
        if line_changed:
            new_text = "\n".join(recovered_lines)
            if text.endswith("\n"):
                new_text += "\n"
            changed_kinds.append("semantic-mojibake")

        encoded = new_text.encode("utf-8")
        if encoded == raw:
            continue
        record = {
            "path": rel_path,
            "kinds": sorted(set(changed_kinds)),
            "written": False,
            "backup": "",
        }
        if write:
            if backup_suffix:
                backup_path = path.with_name(path.name + backup_suffix)
                if not backup_path.exists():
                    backup_path.write_bytes(raw)
                record["backup"] = relative_to_repo(repo_root, backup_path)
            path.write_bytes(encoded)
            record["written"] = True
        repairs.append(record)

    post_scan = scan_text_boundary(repo_root, paths, extensions)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "text-boundary-repair",
        "generated_at": utc_now_iso(),
        "status": "repaired" if repairs and not post_scan["findings"] else "remaining-findings" if post_scan["findings"] else "ok",
        "paths": list(paths),
        "extensions": sorted(extensions),
        "repairs": repairs,
        "blocked": blocked,
        "remaining_findings": post_scan["findings"],
    }
