from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo  # noqa: E402
from runtime.constants.runtime_values import FILE_HASH_CHUNK_BYTES  # noqa: E402
from runtime.constants.paths import LEGACY_ROOT_RAG_PREFIX, KNOWLEDGE_SOURCE_REPO, KNOWLEDGE_SOURCE_RAG  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"Move legacy root rag backups into {KNOWLEDGE_SOURCE_RAG.as_posix()}."
    )
    parser.add_argument(
        "--legacy-dir",
        default="",
        help=f"Legacy directory. Default: newest {LEGACY_ROOT_RAG_PREFIX}* under knowledge repo.",
    )
    parser.add_argument("--target-rag-dir", default=str(KNOWLEDGE_SOURCE_RAG))
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--keep-legacy-dir", action="store_true")
    return parser


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(FILE_HASH_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def newest_legacy_dir(repo_root: Path) -> Path:
    base = repo_root / KNOWLEDGE_SOURCE_REPO
    candidates = sorted(
        (path for path in base.glob(f"{LEGACY_ROOT_RAG_PREFIX}*") if path.is_dir()),
        key=lambda path: path.name,
    )
    if not candidates:
        raise FileNotFoundError(f"Legacy root RAG directory was not found under {base}")
    return candidates[-1]


def remove_empty_dirs(path: Path, stop_at: Path) -> int:
    removed = 0
    for directory in sorted((item for item in path.rglob("*") if item.is_dir()), key=lambda item: len(item.parts), reverse=True):
        if directory == stop_at:
            continue
        try:
            directory.rmdir()
            removed += 1
        except OSError:
            pass
    return removed


def assert_migration_paths(repo_root: Path, legacy_dir: Path, target_rag_dir: Path) -> None:
    resolved_repo = repo_root.resolve()
    resolved_knowledge = (resolved_repo / KNOWLEDGE_SOURCE_REPO).resolve()
    resolved_legacy = legacy_dir.resolve()
    resolved_target = target_rag_dir.resolve()
    try:
        resolved_legacy.relative_to(resolved_knowledge)
        resolved_target.relative_to(resolved_knowledge)
    except ValueError as exc:
        raise ValueError(f"Legacy RAG migration paths must stay under {KNOWLEDGE_SOURCE_REPO.as_posix()}.") from exc
    if resolved_legacy == resolved_target:
        raise ValueError("Legacy RAG directory and target RAG directory must be different.")


def migrate_legacy_root_rag(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    legacy_dir = resolve_repo_path(repo_root, args.legacy_dir).resolve() if args.legacy_dir else newest_legacy_dir(repo_root)
    target_rag_dir = resolve_repo_path(repo_root, args.target_rag_dir).resolve()
    assert_migration_paths(repo_root, legacy_dir, target_rag_dir)
    if not legacy_dir.exists():
        raise FileNotFoundError(f"Legacy RAG directory not found: {legacy_dir}")
    target_rag_dir.mkdir(parents=True, exist_ok=True)

    moved: list[str] = []
    duplicate_removed: list[str] = []
    conflicts: list[str] = []

    for source in sorted(path for path in legacy_dir.rglob("*") if path.is_file()):
        relative = source.relative_to(legacy_dir)
        target = target_rag_dir / relative
        if target.exists():
            if sha256(source) == sha256(target):
                source.unlink()
                duplicate_removed.append(relative.as_posix())
                continue
            conflicts.append(relative.as_posix())
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        source.replace(target)
        moved.append(relative.as_posix())

    if conflicts:
        raise FileExistsError("Legacy RAG migration has conflicting files: " + ", ".join(conflicts))

    removed_dirs = remove_empty_dirs(legacy_dir, legacy_dir)
    legacy_removed = False
    if not args.keep_legacy_dir:
        try:
            legacy_dir.rmdir()
            legacy_removed = True
        except OSError:
            legacy_removed = False

    return {
        "status": "completed",
        "legacy_dir": relative_to_repo(repo_root, legacy_dir),
        "target_rag_dir": relative_to_repo(repo_root, target_rag_dir),
        "moved_count": len(moved),
        "duplicate_removed_count": len(duplicate_removed),
        "removed_empty_dir_count": removed_dirs,
        "legacy_dir_removed": legacy_removed,
        "moved": moved,
        "duplicate_removed": duplicate_removed,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = migrate_legacy_root_rag(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
