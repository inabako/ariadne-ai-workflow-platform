from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build JSONL indexes for normalized RAG documents and chunks.")
    parser.add_argument("--normalized-dir", default="rag/normalized")
    parser.add_argument("--chunks-dir", default="rag/chunks")
    parser.add_argument("--output-dir", default="rag/indexes")
    parser.add_argument("--repo-root", default=None)
    return parser


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def document_index_row(repo_root: Path, path: Path) -> dict[str, Any]:
    document = read_json(path)
    if not isinstance(document, dict):
        raise ValueError(f"Invalid normalized document: {path}")
    metadata = document.get("metadata", {})
    return {
        "schema_version": "1.0",
        "document_id": document.get("document_id", ""),
        "document_type": document.get("document_type", ""),
        "title": document.get("title", ""),
        "source_path": document.get("source_path", ""),
        "normalized_path": relative_to_repo(repo_root, path),
        "project": metadata.get("project", ""),
        "repository": metadata.get("repository", ""),
        "branch": metadata.get("branch", ""),
        "commit": metadata.get("commit", ""),
        "status": metadata.get("status", ""),
        "tags": metadata.get("tags", []),
        "source_type": metadata.get("source_type", ""),
        "category": metadata.get("category", ""),
        "topic": metadata.get("topic", ""),
        "trust_level": metadata.get("trust_level", ""),
        "retrieved_at": metadata.get("retrieved_at", ""),
        "verify_before_use": metadata.get("verify_before_use", False),
        "sources": metadata.get("sources", []),
        "headings": document.get("headings", []),
        "metadata": metadata,
    }


def chunk_index_row(repo_root: Path, path: Path) -> dict[str, Any]:
    chunk = read_json(path)
    if not isinstance(chunk, dict):
        raise ValueError(f"Invalid chunk document: {path}")
    metadata = chunk.get("metadata", {})
    return {
        "schema_version": "1.0",
        "chunk_id": chunk.get("chunk_id", ""),
        "document_id": chunk.get("document_id", ""),
        "document_type": metadata.get("document_type", ""),
        "title": metadata.get("title", ""),
        "source_path": chunk.get("source_path", ""),
        "chunk_path": relative_to_repo(repo_root, path),
        "chunk_index": chunk.get("chunk_index", 0),
        "heading_path": chunk.get("heading_path", []),
        "project": metadata.get("project", ""),
        "repository": metadata.get("repository", ""),
        "branch": metadata.get("branch", ""),
        "commit": metadata.get("commit", ""),
        "status": metadata.get("status", ""),
        "tags": metadata.get("tags", []),
        "source_type": metadata.get("source_type", ""),
        "category": metadata.get("category", ""),
        "topic": metadata.get("topic", ""),
        "trust_level": metadata.get("trust_level", ""),
        "retrieved_at": metadata.get("retrieved_at", ""),
        "verify_before_use": metadata.get("verify_before_use", False),
        "sources": metadata.get("sources", []),
        "content": chunk.get("content", ""),
        "metadata": metadata,
    }


def discover_json(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(path for path in directory.rglob("*.json") if path.is_file())


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    normalized_dir = (
        repo_root / args.normalized_dir if not Path(args.normalized_dir).is_absolute() else Path(args.normalized_dir)
    ).resolve()
    chunks_dir = (repo_root / args.chunks_dir if not Path(args.chunks_dir).is_absolute() else Path(args.chunks_dir)).resolve()
    output_dir = (repo_root / args.output_dir if not Path(args.output_dir).is_absolute() else Path(args.output_dir)).resolve()

    document_rows = [document_index_row(repo_root, path) for path in discover_json(normalized_dir)]
    chunk_rows = [chunk_index_row(repo_root, path) for path in discover_json(chunks_dir)]
    write_jsonl(output_dir / "documents.jsonl", document_rows)
    write_jsonl(output_dir / "chunks.jsonl", chunk_rows)
    return {
        "output_dir": relative_to_repo(repo_root, output_dir),
        "documents_index": relative_to_repo(repo_root, output_dir / "documents.jsonl"),
        "chunks_index": relative_to_repo(repo_root, output_dir / "chunks.jsonl"),
        "document_count": len(document_rows),
        "chunk_count": len(chunk_rows),
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
