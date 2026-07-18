from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo  # noqa: E402
from runtime.constants.paths import CHUNKS_INDEX, EMBEDDINGS_INDEX  # noqa: E402


WORD_RE = re.compile(r"[A-Za-z0-9_.:-]+|[\u3040-\u30ff\u3400-\u9fff]+")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create local deterministic sparse embeddings for RAG chunks."
    )
    parser.add_argument("--chunks-index", default=str(CHUNKS_INDEX))
    parser.add_argument("--output", default=str(EMBEDDINGS_INDEX))
    parser.add_argument("--dimensions", type=int, default=768)
    parser.add_argument("--repo-root", default=None)
    return parser


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"RAG chunk index not found: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
        if isinstance(value, dict):
            rows.append(value)
    return rows


def cjk_ngrams(value: str, min_n: int = 2, max_n: int = 3) -> list[str]:
    compact = "".join(ch for ch in value if "\u3040" <= ch <= "\u9fff")
    tokens: list[str] = []
    for ngram_size in range(min_n, max_n + 1):
        tokens.extend(
            compact[index : index + ngram_size]
            for index in range(max(0, len(compact) - ngram_size + 1))
        )
    return tokens


def tokenize(value: str) -> list[str]:
    tokens = [match.group(0).lower() for match in WORD_RE.finditer(value)]
    tokens.extend(token.lower() for token in cjk_ngrams(value))
    return [token for token in tokens if token.strip()]


def stable_dimension(token: str, dimensions: int) -> int:
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % dimensions


def sparse_embedding(text: str, dimensions: int) -> dict[str, float]:
    if dimensions <= 0:
        raise ValueError("--dimensions must be positive.")
    counts = Counter(tokenize(text))
    values: dict[int, float] = {}
    for token, count in counts.items():
        index = stable_dimension(token, dimensions)
        values[index] = values.get(index, 0.0) + float(count)
    norm = math.sqrt(sum(value * value for value in values.values()))
    if norm == 0:
        return {}
    return {str(index): round(value / norm, 8) for index, value in sorted(values.items())}


def row_text(row: dict[str, Any]) -> str:
    return "\n".join(
        [
            str(row.get("title", "")),
            str(row.get("source_path", "")),
            str(row.get("repository", "")),
            str(row.get("branch", "")),
            " ".join(str(item) for item in row.get("heading_path", [])),
            " ".join(str(tag) for tag in row.get("tags", [])),
            json.dumps(row.get("metadata", {}), ensure_ascii=False, sort_keys=True),
            str(row.get("content", "")),
        ]
    )


def build_embedding(row: dict[str, Any], dimensions: int) -> dict[str, Any]:
    chunk_id = str(row.get("chunk_id", ""))
    return {
        "schema_version": "1.0",
        "embedding_id": f"{chunk_id}-embedding-local-hash-v1",
        "chunk_id": chunk_id,
        "document_id": row.get("document_id", ""),
        "source_path": row.get("source_path", ""),
        "chunk_path": row.get("chunk_path", ""),
        "embedding_model": "local-hash-embedding-v1",
        "dimensions": dimensions,
        "embedding": sparse_embedding(row_text(row), dimensions),
        "metadata": {
            **row.get("metadata", {}),
            "document_type": row.get("document_type", ""),
            "title": row.get("title", ""),
            "project": row.get("project", ""),
            "repository": row.get("repository", ""),
            "branch": row.get("branch", ""),
            "commit": row.get("commit", ""),
            "status": row.get("status", ""),
            "tags": row.get("tags", []),
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    chunks_index = (
        repo_root / args.chunks_index if not Path(args.chunks_index).is_absolute() else Path(args.chunks_index)
    ).resolve()
    output_path = (repo_root / args.output if not Path(args.output).is_absolute() else Path(args.output)).resolve()

    rows = read_jsonl(chunks_index)
    embeddings = [build_embedding(row, args.dimensions) for row in rows]
    write_jsonl(output_path, embeddings)
    return {
        "chunks_index": relative_to_repo(repo_root, chunks_index),
        "embeddings_index": relative_to_repo(repo_root, output_path),
        "embedding_model": "local-hash-embedding-v1",
        "dimensions": args.dimensions,
        "embedding_count": len(embeddings),
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
