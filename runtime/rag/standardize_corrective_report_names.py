from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo  # noqa: E402
from runtime.constants.paths import KNOWLEDGE_SOURCE_RAG, SOURCE_CORRECTIVE_ACTION_REPORTS  # noqa: E402


CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
TARGET_NAME_RE = re.compile(r"^\d{14}_[0-9A-HJKMNP-TV-Z]{5,8}_[^\\/]+\.md$")
UUID_NAME_RE = re.compile(
    r"^(?P<timestamp>\d{14})_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_(?P<repository>[^\\/]+)\.md$",
    re.IGNORECASE,
)
LEGACY_TIMESTAMP_RE = re.compile(r"(?P<date>\d{8})[_-]?(?P<time>\d{6})")
CREATED_AT_RE = re.compile(r"^created_at:\s*(?P<value>.+?)\s*$", re.MULTILINE)
REPOSITORY_RE = re.compile(r"^repository:\s*(?P<value>.+?)\s*$", re.MULTILINE)
TARGET_PROJECT_RE = re.compile(r"対象プロジェクト:\s*`(?P<value>[^`]+)`")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rename corrective action reports to timestamp_random_repository.md.")
    parser.add_argument("--source-dir", default=str(SOURCE_CORRECTIVE_ACTION_REPORTS))
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--replace-references", action="store_true")
    parser.add_argument("--random-length", type=int, default=8, choices=range(5, 9))
    return parser


def sanitize_name(value: str) -> str:
    value = value.strip().strip("`").strip("\"'")
    value = value.replace("\\", "/").rstrip("/")
    name = value.split("/")[-1] if "/" in value else value
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-._")
    return name or "unknown-repository"


def datetime_from_text(path: Path, text: str) -> datetime:
    created_match = CREATED_AT_RE.search(text)
    if created_match:
        raw_value = created_match.group("value").strip().strip("\"'")
        normalized = raw_value.replace("Z", "+00:00")
        try:
            value = datetime.fromisoformat(normalized)
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value
        except ValueError:
            pass
    filename_match = LEGACY_TIMESTAMP_RE.search(path.name)
    if filename_match:
        raw_value = f"{filename_match.group('date')}{filename_match.group('time')}"
        return datetime.strptime(raw_value, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def repository_from_text(path: Path, text: str) -> str:
    uuid_name_match = UUID_NAME_RE.match(path.name)
    if uuid_name_match:
        return sanitize_name(uuid_name_match.group("repository"))
    repository_match = REPOSITORY_RE.search(text)
    if repository_match:
        return sanitize_name(repository_match.group("value"))
    target_project_match = TARGET_PROJECT_RE.search(text)
    if target_project_match:
        return sanitize_name(target_project_match.group("value"))
    without_timestamp = LEGACY_TIMESTAMP_RE.sub("", path.stem, count=1).strip("_-")
    return sanitize_name(without_timestamp.split("_")[0])


def random_token(length: int) -> str:
    return "".join(secrets.choice(CROCKFORD_BASE32) for _ in range(length))


def replacement_name(path: Path, text: str, random_length: int) -> str:
    timestamp = datetime_from_text(path, text)
    timestamp_text = timestamp.strftime("%Y%m%d%H%M%S")
    repository = repository_from_text(path, text)
    return f"{timestamp_text}_{random_token(random_length)}_{repository}.md"


def replace_text_references(repo_root: Path, path_map: dict[str, str]) -> list[str]:
    updated: list[str] = []
    knowledge_rag_dir = repo_root / KNOWLEDGE_SOURCE_RAG
    targets = [
        *knowledge_rag_dir.glob("**/*.json"),
        *knowledge_rag_dir.glob("**/*.jsonl"),
        *knowledge_rag_dir.glob("**/*.md"),
        repo_root / "README.md",
        repo_root / "AGENT.md",
        *repo_root.glob("skills/**/*.md"),
        *repo_root.glob(".github/prompts/**/*.md"),
        *repo_root.glob("runtime/**/*.md"),
    ]
    for path in sorted(set(targets)):
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        next_text = text
        for old_rel, new_rel in path_map.items():
            next_text = next_text.replace(old_rel, new_rel)
            next_text = next_text.replace(Path(old_rel).name, Path(new_rel).name)
        if next_text != text:
            path.write_text(next_text, encoding="utf-8")
            updated.append(relative_to_repo(repo_root, path))
    return updated


def run(args: argparse.Namespace) -> dict[str, object]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    source_dir = (
        repo_root / args.source_dir if not Path(args.source_dir).is_absolute() else Path(args.source_dir)
    ).resolve()
    if not source_dir.exists():
        raise FileNotFoundError(f"Corrective report directory not found: {source_dir}")
    if not str(source_dir).lower().startswith(str(repo_root).lower()):
        raise ValueError(f"Source directory must be inside repo root: {source_dir}")

    renames: list[dict[str, str]] = []
    path_map: dict[str, str] = {}
    for path in sorted(source_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        if TARGET_NAME_RE.match(path.name):
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        new_name = replacement_name(path, text, args.random_length)
        target = path.with_name(new_name)
        if target.exists():
            raise FileExistsError(f"Target already exists: {target}")
        old_rel = relative_to_repo(repo_root, path)
        new_rel = relative_to_repo(repo_root, target)
        next_text = text.replace(path.name, new_name).replace(old_rel, new_rel)
        path.write_text(next_text, encoding="utf-8")
        path.rename(target)
        renames.append({"old": old_rel, "new": new_rel})
        path_map[old_rel] = new_rel

    updated_refs = replace_text_references(repo_root, path_map) if args.replace_references and path_map else []
    return {
        "source_dir": relative_to_repo(repo_root, source_dir),
        "renamed_count": len(renames),
        "renames": renames,
        "updated_reference_count": len(updated_refs),
        "updated_references": updated_refs,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
