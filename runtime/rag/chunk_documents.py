from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo, write_json  # noqa: E402
from runtime.rag.cleanup_guard import assert_safe_clean_output_target  # noqa: E402
from runtime.constants.paths import GENERATED_CHUNKS, GENERATED_NORMALIZED  # noqa: E402


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Split normalized RAG documents into JSON chunks.")
    parser.add_argument("--input-dir", default=str(GENERATED_NORMALIZED))
    parser.add_argument("--output-dir", default=str(GENERATED_CHUNKS))
    parser.add_argument("--chunk-size", type=int, default=1800)
    parser.add_argument("--chunk-overlap", type=int, default=180)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--clean-output", action="store_true")
    return parser


def heading_path_for_text(text: str) -> list[str]:
    heading_path: list[str] = []
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        heading_path = heading_path[: level - 1]
        heading_path.append(title)
    return heading_path


def split_content(content: str, chunk_size: int, chunk_overlap: int) -> list[tuple[int, int, str]]:
    if chunk_size <= 0:
        raise ValueError("--chunk-size must be positive.")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("--chunk-overlap must be greater than or equal to 0 and smaller than --chunk-size.")

    paragraphs = re.split(r"(\n\s*\n)", content.strip())
    chunks: list[tuple[int, int, str]] = []
    current = ""
    current_start = 0
    cursor = 0

    for part in paragraphs:
        if not part:
            continue
        part_start = cursor
        cursor += len(part)
        candidate = current + part
        if current and len(candidate) > chunk_size:
            previous_end = current_start + len(current)
            chunks.append((current_start, previous_end, current.strip()))
            overlap_text = current[-chunk_overlap:] if chunk_overlap else ""
            current = overlap_text + part
            current_start = max(0, previous_end - len(overlap_text))
            continue
        if not current:
            current_start = part_start
        current = candidate

    if current.strip():
        chunks.append((current_start, current_start + len(current), current.strip()))

    if not chunks and content.strip():
        chunks.append((0, len(content), content.strip()))
    return chunks


def chunk_document(repo_root: Path, document_path: Path, output_dir: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    document = read_json(document_path)
    if not isinstance(document, dict):
        raise ValueError(f"Invalid normalized document: {document_path}")

    document_id = document["document_id"]
    content = document.get("content", "")
    split_chunks = split_content(content, args.chunk_size, args.chunk_overlap)
    chunks: list[dict[str, Any]] = []
    for index, (start, end, text) in enumerate(split_chunks):
        legacy_chunk_id = f"{document_id}-chunk-{index + 1:04d}"
        chunk_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"rag-chunk:{document_id}:{index}:{start}:{end}"))
        metadata = {
            **document.get("metadata", {}),
            "document_type": document.get("document_type", ""),
            "title": document.get("title", ""),
        }
        chunk = {
            "schema_version": "1.0",
            "chunk_id": chunk_id,
            "legacy_chunk_id": legacy_chunk_id,
            "document_id": document_id,
            "source_path": document.get("source_path", ""),
            "normalized_path": relative_to_repo(repo_root, document_path),
            "chunk_index": index,
            "chunk_sequence": index + 1,
            "heading_path": heading_path_for_text(text),
            "content": text,
            "char_start": start,
            "char_end": end,
            "metadata": metadata,
        }
        write_json(output_dir / f"{chunk_id}.json", chunk)
        chunks.append(chunk)
    return chunks


def discover_documents(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"RAG normalized directory not found: {input_dir}")
    return sorted(path for path in input_dir.rglob("*.json") if path.is_file())


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    input_dir = (repo_root / args.input_dir).resolve() if not Path(args.input_dir).is_absolute() else Path(args.input_dir)
    output_dir = (repo_root / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    if args.clean_output:
        assert_safe_clean_output_target(repo_root, output_dir)
    if args.clean_output and output_dir.exists():
        for path in output_dir.glob("*.json"):
            path.unlink()
    documents = discover_documents(input_dir)
    all_chunks: list[dict[str, Any]] = []
    for document_path in documents:
        all_chunks.extend(chunk_document(repo_root, document_path, output_dir, args))
    return {
        "input_dir": relative_to_repo(repo_root, input_dir),
        "output_dir": relative_to_repo(repo_root, output_dir),
        "document_count": len(documents),
        "chunk_count": len(all_chunks),
        "chunks": [relative_to_repo(repo_root, output_dir / f"{chunk['chunk_id']}.json") for chunk in all_chunks],
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
