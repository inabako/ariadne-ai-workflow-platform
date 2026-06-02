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

from runtime.common import find_repo_root, local_timestamp, relative_to_repo, slugify, utc_now_iso, write_json  # noqa: E402


WORD_RE = re.compile(r"[A-Za-z0-9_.:-]+|[\u3040-\u30ff\u3400-\u9fff]+")
SPLIT_RE = re.compile(r"(?<=[。.!?])\s+|\n\s*\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retrieve file-based RAG chunks and create a compressed context pack."
    )
    parser.add_argument("query", help="Search query used to retrieve RAG chunks.")
    parser.add_argument("--chunks-index", default="rag/indexes/chunks.jsonl")
    parser.add_argument("--embeddings-index", default="rag/embeddings/chunks-embeddings.jsonl")
    parser.add_argument("--output-dir", default="rag/retrieval")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--max-chars", type=int, default=6000)
    parser.add_argument("--search-mode", default="hybrid", choices=["keyword", "semantic", "hybrid"])
    parser.add_argument("--project", default="")
    parser.add_argument("--repository", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--tag", action="append", default=[])
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


def cjk_bigrams(value: str) -> list[str]:
    compact = "".join(ch for ch in value if "\u3040" <= ch <= "\u9fff")
    return [compact[index : index + 2] for index in range(max(0, len(compact) - 1))]


def tokenize(value: str) -> list[str]:
    tokens = [match.group(0).lower() for match in WORD_RE.finditer(value)]
    tokens.extend(token.lower() for token in cjk_bigrams(value))
    return [token for token in tokens if token.strip()]


def filter_row(row: dict[str, Any], args: argparse.Namespace) -> bool:
    if args.project and row.get("project") != args.project:
        return False
    if args.repository and row.get("repository") != args.repository:
        return False
    if args.branch and row.get("branch") != args.branch:
        return False
    if args.tag:
        tags = set(str(tag) for tag in row.get("tags", []))
        if not set(args.tag).issubset(tags):
            return False
    return True


def score_row(row: dict[str, Any], query_terms: list[str]) -> float:
    text_parts = [
        row.get("title", ""),
        " ".join(str(item) for item in row.get("heading_path", [])),
        " ".join(str(tag) for tag in row.get("tags", [])),
        row.get("content", ""),
    ]
    text = "\n".join(text_parts).lower()
    token_counts = Counter(tokenize(text))
    score = 0.0
    for term in query_terms:
        if not term:
            continue
        score += token_counts.get(term, 0)
        if term in text:
            score += 2.0
    if row.get("heading_path"):
        heading_text = " ".join(row.get("heading_path", [])).lower()
        score += sum(3.0 for term in query_terms if term in heading_text)
    return score


def stable_dimension(token: str, dimensions: int) -> int:
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % dimensions


def sparse_embedding(text: str, dimensions: int) -> dict[str, float]:
    counts = Counter(tokenize(text))
    values: dict[int, float] = {}
    for token, count in counts.items():
        index = stable_dimension(token, dimensions)
        values[index] = values.get(index, 0.0) + float(count)
    norm = math.sqrt(sum(value * value for value in values.values()))
    if norm == 0:
        return {}
    return {str(index): value / norm for index, value in values.items()}


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    return sum(float(value) * float(right.get(index, 0.0)) for index, value in left.items())


def read_embeddings(path: Path) -> tuple[dict[str, dict[str, Any]], int]:
    if not path.exists():
        return {}, 0
    rows = read_jsonl(path)
    embeddings: dict[str, dict[str, Any]] = {}
    dimensions = 0
    for row in rows:
        chunk_id = str(row.get("chunk_id", ""))
        if not chunk_id:
            continue
        embeddings[chunk_id] = row
        dimensions = int(row.get("dimensions") or dimensions or 0)
    return embeddings, dimensions


def retrieve(
    rows: list[dict[str, Any]],
    embeddings: dict[str, dict[str, Any]],
    dimensions: int,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if args.top_k <= 0:
        raise ValueError("--top-k must be positive.")
    query_terms = tokenize(args.query)
    query_embedding = sparse_embedding(args.query, dimensions) if dimensions else {}
    scored: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []

    for row in rows:
        if not filter_row(row, args):
            dropped.append({"chunk_id": row.get("chunk_id", ""), "score": 0, "reason": "filtered"})
            continue
        keyword_score = score_row(row, query_terms)
        embedding_row = embeddings.get(str(row.get("chunk_id", "")), {})
        semantic_score = cosine_similarity(query_embedding, embedding_row.get("embedding", {}))
        if args.search_mode == "keyword":
            score = keyword_score
        elif args.search_mode == "semantic":
            score = semantic_score * 100.0
        else:
            score = keyword_score + (semantic_score * 35.0)
        if score <= 0:
            dropped.append({"chunk_id": row.get("chunk_id", ""), "score": score, "reason": "no-query-match"})
            continue
        scored.append(
            {
                **row,
                "_score": score,
                "_keyword_score": keyword_score,
                "_semantic_score": semantic_score,
                "_rerank_method": args.search_mode,
            }
        )

    scored.sort(key=lambda row: (-float(row.get("_score", 0)), int(row.get("chunk_index", 0))))
    selected = scored[: args.top_k]
    for row in scored[args.top_k :]:
        dropped.append({"chunk_id": row.get("chunk_id", ""), "score": row.get("_score", 0), "reason": "below-top-k"})
    return selected, dropped


def split_units(content: str) -> list[str]:
    units: list[str] = []
    for block in SPLIT_RE.split(content.strip()):
        block = block.strip()
        if not block:
            continue
        if len(block) <= 700:
            units.append(block)
            continue
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        units.extend(lines or [block])
    return units


def compress_chunk(row: dict[str, Any], query_terms: list[str], max_chars: int) -> str:
    content = str(row.get("content", "")).strip()
    if len(content) <= max_chars:
        return content

    selected_units: list[str] = []
    for unit in split_units(content):
        unit_lower = unit.lower()
        if any(term in unit_lower for term in query_terms):
            selected_units.append(unit)

    if not selected_units:
        selected_units = split_units(content)[:3]

    compressed = "\n\n".join(selected_units).strip()
    if len(compressed) <= max_chars:
        return compressed
    return compressed[: max_chars - 20].rstrip() + "\n\n[truncated]"


def estimate_tokens(text: str) -> int:
    # Conservative local estimate for mixed Japanese/English text.
    return max(1, int(len(text) / 2.5))


def build_context(selected: list[dict[str, Any]], args: argparse.Namespace) -> tuple[str, list[dict[str, Any]]]:
    query_terms = tokenize(args.query)
    remaining = args.max_chars
    sections: list[str] = []
    sources: list[dict[str, Any]] = []

    for row in selected:
        if remaining <= 200:
            break
        heading = " > ".join(str(item) for item in row.get("heading_path", []) if str(item).strip())
        source_header = f"Source: {row.get('source_path', '')}"
        if heading:
            source_header += f"\nHeading: {heading}"
        per_chunk_budget = max(300, min(remaining, int(args.max_chars / max(1, min(len(selected), args.top_k)))))
        compressed = compress_chunk(row, query_terms, per_chunk_budget)
        section = f"## {row.get('chunk_id')}\n\n{source_header}\n\n{compressed}".strip()
        if len(section) > remaining:
            section = section[: remaining - 20].rstrip() + "\n\n[truncated]"
        sections.append(section)
        remaining -= len(section) + 2
        sources.append(
            {
                "chunk_id": row.get("chunk_id", ""),
                "document_id": row.get("document_id", ""),
                "source_path": row.get("source_path", ""),
                "chunk_path": row.get("chunk_path", ""),
                "heading_path": row.get("heading_path", []),
                "score": row.get("_score", row.get("score", 0)),
            }
        )
    return "\n\n".join(sections).strip(), sources


def write_context_markdown(path: Path, context_pack: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sources = "\n".join(
        f"- `{source.get('chunk_id')}`: `{source.get('source_path')}`"
        for source in context_pack.get("sources", [])
    )
    text = f"""# RAG Context Pack

Query: `{context_pack['query']}`

Created At: `{context_pack['created_at']}`

Estimated Tokens: `{context_pack['compression']['estimated_tokens']}`

## Sources

{sources}

## Compressed Context

{context_pack['context']}
"""
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.max_chars <= 0:
        raise ValueError("--max-chars must be positive.")

    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    chunks_index = (
        repo_root / args.chunks_index if not Path(args.chunks_index).is_absolute() else Path(args.chunks_index)
    ).resolve()
    embeddings_index = (
        repo_root / args.embeddings_index if not Path(args.embeddings_index).is_absolute() else Path(args.embeddings_index)
    ).resolve()
    output_dir = (repo_root / args.output_dir if not Path(args.output_dir).is_absolute() else Path(args.output_dir)).resolve()

    rows = read_jsonl(chunks_index)
    embeddings, dimensions = read_embeddings(embeddings_index)
    if args.search_mode == "semantic" and not embeddings:
        raise FileNotFoundError(
            f"Semantic search requires embeddings index. Run runtime/rag/embed_chunks.py first: {embeddings_index}"
        )
    selected, dropped = retrieve(rows, embeddings, dimensions, args)
    context, sources = build_context(selected, args)
    timestamp = local_timestamp()
    query_slug = slugify(args.query)[:80]
    base_name = f"{timestamp}_{query_slug}"
    retrieval_path = output_dir / f"{base_name}_retrieval-result.json"
    context_path = output_dir / f"{base_name}_context-pack.json"
    markdown_path = output_dir / f"{base_name}_context-pack.md"

    selected_summary = [
        {
            "chunk_id": row.get("chunk_id", ""),
            "document_id": row.get("document_id", ""),
            "score": row.get("_score", 0),
            "source_path": row.get("source_path", ""),
            "chunk_path": row.get("chunk_path", ""),
            "heading_path": row.get("heading_path", []),
            "reason": "query-match",
            "keyword_score": row.get("_keyword_score", 0),
            "semantic_score": row.get("_semantic_score", 0),
            "rerank_method": row.get("_rerank_method", args.search_mode),
        }
        for row in selected
    ]
    retrieval_result = {
        "schema_version": "1.0",
        "query": args.query,
        "created_at": utc_now_iso(),
        "index_path": relative_to_repo(repo_root, chunks_index),
        "embeddings_index_path": relative_to_repo(repo_root, embeddings_index) if embeddings else "",
        "search_mode": args.search_mode,
        "filters": {
            "project": args.project,
            "repository": args.repository,
            "branch": args.branch,
            "tags": args.tag,
        },
        "candidate_count": len(rows),
        "selected_chunks": selected_summary,
        "dropped_chunks": dropped,
    }
    context_pack = {
        "schema_version": "1.0",
        "query": args.query,
        "created_at": retrieval_result["created_at"],
        "compression": {
            "method": f"{args.search_mode}-retrieval-extractive-compression",
            "retrieval_method": args.search_mode,
            "embedding_model": "local-hash-embedding-v1" if embeddings else "",
            "max_chars": args.max_chars,
            "input_chunk_count": len(rows),
            "selected_chunk_count": len(sources),
            "estimated_tokens": estimate_tokens(context),
            "dropped_reason_summary": sorted({str(item.get("reason", "")) for item in dropped if item.get("reason")}),
        },
        "context": context,
        "sources": sources,
        "open_questions": [],
        "risks": [],
    }
    write_json(retrieval_path, retrieval_result)
    write_json(context_path, context_pack)
    write_context_markdown(markdown_path, context_pack)
    return {
        "retrieval_result": relative_to_repo(repo_root, retrieval_path),
        "context_pack": relative_to_repo(repo_root, context_path),
        "context_markdown": relative_to_repo(repo_root, markdown_path),
        "candidate_count": len(rows),
        "selected_chunk_count": len(sources),
        "estimated_tokens": context_pack["compression"]["estimated_tokens"],
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
