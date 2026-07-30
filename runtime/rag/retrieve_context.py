from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.constants.runtime_values import SCHEMA_VERSION  # noqa: E402
from runtime.common import find_repo_root, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.rag import duckdb_store  # noqa: E402
from runtime.constants.cli_defaults import RAG_RETRIEVE_MAX_CHARS_DEFAULT, RAG_RETRIEVE_TOP_K_DEFAULT  # noqa: E402
from runtime.constants.paths import CHUNKS_INDEX, EMBEDDINGS_INDEX, GENERATED_RETRIEVAL, RAG_EMBED_SCRIPT  # noqa: E402
from runtime.rag.scoring_constants import (  # noqa: E402
    FALLBACK_SELECTED_UNIT_COUNT,
    HEADING_MATCH_BONUS,
    HYBRID_SEMANTIC_WEIGHT,
    KEYWORD_CONTAINS_BONUS,
    LONG_TEXT_BLOCK_CHARS,
    MIN_CONTEXT_REMAINING_CHARS,
    MIN_PER_CHUNK_CONTEXT_BUDGET,
    SCORE_MIN,
    SECTION_SEPARATOR_CHARS,
    SEMANTIC_SCORE_SCALE,
    SPARSE_EMBEDDING_HASH_BYTES,
    TOKEN_ESTIMATE_CHARS_PER_TOKEN,
    TRUNCATION_RESERVED_CHARS,
)


WORD_RE = re.compile(r"[A-Za-z0-9_.:-]+|[\u3040-\u30ff\u3400-\u9fff]+")
SPLIT_RE = re.compile(r"(?<=[。.!?])\s+|\n\s*\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retrieve file-based RAG chunks and create a compressed context pack."
    )
    parser.add_argument("query", help="Search query used to retrieve RAG chunks.")
    parser.add_argument("--chunks-index", default=str(CHUNKS_INDEX))
    parser.add_argument("--embeddings-index", default=str(EMBEDDINGS_INDEX))
    parser.add_argument("--output-dir", default=str(GENERATED_RETRIEVAL))
    parser.add_argument("--top-k", type=int, default=RAG_RETRIEVE_TOP_K_DEFAULT)
    parser.add_argument("--max-chars", type=int, default=RAG_RETRIEVE_MAX_CHARS_DEFAULT)
    parser.add_argument("--search-mode", default="hybrid", choices=["keyword", "semantic", "hybrid"])
    parser.add_argument("--backend", default="file", choices=["file", "duckdb"])
    parser.add_argument("--duckdb-path", default=str(duckdb_store.DEFAULT_DB_PATH))
    parser.add_argument("--semantic-hint", default="")
    parser.add_argument("--document-type", default="")
    parser.add_argument("--environment", default="")
    parser.add_argument("--workflow", default="")
    parser.add_argument("--min-reliability", type=float, default=None)
    parser.add_argument("--min-freshness", type=float, default=None)
    parser.add_argument("--project", default="")
    parser.add_argument("--repository", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--source-type", default="", help="Optional source_type filter, e.g. external-web or internal-work.")
    parser.add_argument("--category", default="", help="Optional external-web category filter.")
    parser.add_argument("--trust-level", default="", help="Optional trust_level filter.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--write-markdown", action="store_true")
    return parser


def arg_value(args: argparse.Namespace, name: str, default: Any = "") -> Any:
    return getattr(args, name, default)


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
    if args.source_type and row.get("source_type") != args.source_type:
        return False
    if args.category and row.get("category") != args.category:
        return False
    if args.trust_level and row.get("trust_level") != args.trust_level:
        return False
    return True


def duckdb_filters_from_args(args: argparse.Namespace) -> duckdb_store.SearchFilters:
    return duckdb_store.SearchFilters(
        query=str(args.query),
        semantic_hint=str(arg_value(args, "semantic_hint", "")),
        category=str(arg_value(args, "category", "")),
        tags=[str(tag) for tag in arg_value(args, "tag", [])],
        source=str(arg_value(args, "source_type", "")),
        document_type=str(arg_value(args, "document_type", "")),
        environment=str(arg_value(args, "environment", "")),
        workflow=str(arg_value(args, "workflow", "")),
        min_reliability=arg_value(args, "min_reliability", None),
        min_freshness=arg_value(args, "min_freshness", None),
        limit=int(arg_value(args, "top_k", RAG_RETRIEVE_TOP_K_DEFAULT)),
    )


def duckdb_result_to_chunk(row: dict[str, Any]) -> dict[str, Any]:
    knowledge_id = str(row.get("knowledge_id", ""))
    return {
        "chunk_id": knowledge_id,
        "document_id": knowledge_id,
        "source_path": row.get("source_path", ""),
        "chunk_path": row.get("source_file", ""),
        "chunk_index": 0,
        "title": row.get("title", ""),
        "heading_path": [row.get("title", "")] if row.get("title") else [],
        "content": row.get("content", ""),
        "tags": row.get("tags", []),
        "source_type": row.get("source", ""),
        "category": row.get("category", ""),
        "topic": row.get("semantic_hint", ""),
        "trust_level": row.get("optimization_decision", ""),
        "retrieved_at": row.get("updated_at", ""),
        "verify_before_use": False,
        "sources": [],
        "_score": row.get("final_score", SCORE_MIN),
        "_keyword_score": row.get("keyword_match_score", SCORE_MIN),
        "_semantic_score": row.get("semantic_hint_score", SCORE_MIN),
        "_rerank_method": "duckdb",
        "_duckdb_scores": row.get("scores", {}),
    }


def retrieve_duckdb(repo_root: Path, args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], Path]:
    duckdb_path = Path(str(arg_value(args, "duckdb_path", duckdb_store.DEFAULT_DB_PATH)))
    duckdb_path = duckdb_path if duckdb_path.is_absolute() else repo_root / duckdb_path
    search_result = duckdb_store.search_knowledge(duckdb_path.resolve(), duckdb_filters_from_args(args))
    selected = [duckdb_result_to_chunk(row) for row in search_result.get("results", [])]
    dropped: list[dict[str, Any]] = []
    if not selected:
        dropped.append({"chunk_id": "", "score": SCORE_MIN, "reason": "no-duckdb-query-match"})
    return selected, dropped, search_result, duckdb_path.resolve()


def score_row(row: dict[str, Any], query_terms: list[str]) -> float:
    text_parts = [
        row.get("title", ""),
        row.get("source_path", ""),
        row.get("repository", ""),
        row.get("branch", ""),
        " ".join(str(item) for item in row.get("heading_path", [])),
        " ".join(str(tag) for tag in row.get("tags", [])),
        json.dumps(row.get("metadata", {}), ensure_ascii=False, sort_keys=True),
        row.get("content", ""),
    ]
    text = "\n".join(text_parts).lower()
    token_counts = Counter(tokenize(text))
    score = SCORE_MIN
    for term in query_terms:
        if not term:
            continue
        score += token_counts.get(term, 0)
        if term in text:
            score += KEYWORD_CONTAINS_BONUS
    if row.get("heading_path"):
        heading_text = " ".join(row.get("heading_path", [])).lower()
        score += sum(HEADING_MATCH_BONUS for term in query_terms if term in heading_text)
    return score


def stable_dimension(token: str, dimensions: int) -> int:
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:SPARSE_EMBEDDING_HASH_BYTES], "big") % dimensions


def sparse_embedding(text: str, dimensions: int) -> dict[str, float]:
    counts = Counter(tokenize(text))
    values: dict[int, float] = {}
    for token, count in counts.items():
        index = stable_dimension(token, dimensions)
        values[index] = values.get(index, SCORE_MIN) + float(count)
    norm = math.sqrt(sum(value * value for value in values.values()))
    if norm == 0:
        return {}
    return {str(index): value / norm for index, value in values.items()}


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return SCORE_MIN
    if len(left) > len(right):
        left, right = right, left
    return sum(float(value) * float(right.get(index, SCORE_MIN)) for index, value in left.items())


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
            dropped.append({"chunk_id": row.get("chunk_id", ""), "score": SCORE_MIN, "reason": "filtered"})
            continue
        keyword_score = score_row(row, query_terms)
        embedding_row = embeddings.get(str(row.get("chunk_id", "")), {})
        semantic_score = cosine_similarity(query_embedding, embedding_row.get("embedding", {}))
        if args.search_mode == "keyword":
            score = keyword_score
        elif args.search_mode == "semantic":
            score = semantic_score * SEMANTIC_SCORE_SCALE
        else:
            score = keyword_score + (semantic_score * HYBRID_SEMANTIC_WEIGHT)
        if score <= SCORE_MIN:
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

    scored.sort(key=lambda row: (-float(row.get("_score", SCORE_MIN)), int(row.get("chunk_index", 0))))
    selected = scored[: args.top_k]
    for row in scored[args.top_k :]:
        dropped.append({"chunk_id": row.get("chunk_id", ""), "score": row.get("_score", SCORE_MIN), "reason": "below-top-k"})
    return selected, dropped


def split_units(content: str) -> list[str]:
    units: list[str] = []
    for block in SPLIT_RE.split(content.strip()):
        block = block.strip()
        if not block:
            continue
        if len(block) <= LONG_TEXT_BLOCK_CHARS:
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
        selected_units = split_units(content)[:FALLBACK_SELECTED_UNIT_COUNT]

    compressed = "\n\n".join(selected_units).strip()
    if len(compressed) <= max_chars:
        return compressed
    return compressed[: max_chars - TRUNCATION_RESERVED_CHARS].rstrip() + "\n\n[truncated]"


def estimate_tokens(text: str) -> int:
    # Conservative local estimate for mixed Japanese/English text.
    return max(1, int(len(text) / TOKEN_ESTIMATE_CHARS_PER_TOKEN))


def build_context(selected: list[dict[str, Any]], args: argparse.Namespace) -> tuple[str, list[dict[str, Any]]]:
    query_terms = tokenize(args.query)
    remaining = args.max_chars
    sections: list[str] = []
    sources: list[dict[str, Any]] = []

    for row in selected:
        if remaining <= MIN_CONTEXT_REMAINING_CHARS:
            break
        heading = " > ".join(str(item) for item in row.get("heading_path", []) if str(item).strip())
        source_header = f"Source: {row.get('source_path', '')}"
        if heading:
            source_header += f"\nHeading: {heading}"
        per_chunk_budget = max(
            MIN_PER_CHUNK_CONTEXT_BUDGET,
            min(remaining, int(args.max_chars / max(1, min(len(selected), args.top_k)))),
        )
        compressed = compress_chunk(row, query_terms, per_chunk_budget)
        section = f"## {row.get('chunk_id')}\n\n{source_header}\n\n{compressed}".strip()
        if len(section) > remaining:
            section = section[: remaining - TRUNCATION_RESERVED_CHARS].rstrip() + "\n\n[truncated]"
        sections.append(section)
        remaining -= len(section) + SECTION_SEPARATOR_CHARS
        sources.append(
            {
                "chunk_id": row.get("chunk_id", ""),
                "document_id": row.get("document_id", ""),
                "source_path": row.get("source_path", ""),
                "chunk_path": row.get("chunk_path", ""),
                "heading_path": row.get("heading_path", []),
                "score": row.get("_score", row.get("score", SCORE_MIN)),
                "source_type": row.get("source_type", ""),
                "category": row.get("category", ""),
                "topic": row.get("topic", ""),
                "trust_level": row.get("trust_level", ""),
                "retrieved_at": row.get("retrieved_at", ""),
                "verify_before_use": row.get("verify_before_use", False),
                "sources": row.get("sources", []),
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

    backend = str(arg_value(args, "backend", "file"))
    duckdb_search: dict[str, Any] = {}
    duckdb_path = Path(str(arg_value(args, "duckdb_path", duckdb_store.DEFAULT_DB_PATH)))
    embeddings: dict[str, dict[str, Any]] = {}
    if backend == "duckdb":
        selected, dropped, duckdb_search, duckdb_path = retrieve_duckdb(repo_root, args)
        rows = list(duckdb_search.get("results", []))
    else:
        rows = read_jsonl(chunks_index)
        embeddings, dimensions = read_embeddings(embeddings_index)
        if args.search_mode == "semantic" and not embeddings:
            raise FileNotFoundError(
                f"Semantic search requires embeddings index. Run {RAG_EMBED_SCRIPT.as_posix()} first: {embeddings_index}"
            )
        selected, dropped = retrieve(rows, embeddings, dimensions, args)
    context, sources = build_context(selected, args)
    retrieval_id = str(uuid.uuid4())
    context_pack_id = str(uuid.uuid4())
    retrieval_path = output_dir / f"{retrieval_id}.json"
    context_path = output_dir / f"{context_pack_id}.json"
    markdown_path = output_dir / f"{context_pack_id}.md"

    selected_summary = [
        {
            "chunk_id": row.get("chunk_id", ""),
            "document_id": row.get("document_id", ""),
            "score": row.get("_score", SCORE_MIN),
            "source_path": row.get("source_path", ""),
            "chunk_path": row.get("chunk_path", ""),
            "heading_path": row.get("heading_path", []),
            "source_type": row.get("source_type", ""),
            "category": row.get("category", ""),
            "topic": row.get("topic", ""),
            "trust_level": row.get("trust_level", ""),
            "retrieved_at": row.get("retrieved_at", ""),
            "verify_before_use": row.get("verify_before_use", False),
            "sources": row.get("sources", []),
            "reason": "query-match",
            "keyword_score": row.get("_keyword_score", SCORE_MIN),
            "semantic_score": row.get("_semantic_score", SCORE_MIN),
            "rerank_method": row.get("_rerank_method", args.search_mode),
        }
        for row in selected
    ]
    retrieval_result = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "rag-retrieval-result",
        "retrieval_id": retrieval_id,
        "context_pack_id": context_pack_id,
        "query": args.query,
        "created_at": utc_now_iso(),
        "backend": backend,
        "index_path": relative_to_repo(repo_root, chunks_index),
        "embeddings_index_path": relative_to_repo(repo_root, embeddings_index) if embeddings else "",
        "duckdb_path": relative_to_repo(repo_root, duckdb_path) if backend == "duckdb" else "",
        "search_mode": args.search_mode,
        "filters": {
            "project": args.project,
            "repository": args.repository,
            "branch": args.branch,
            "tags": args.tag,
            "source_type": args.source_type,
            "category": args.category,
            "trust_level": args.trust_level,
            "semantic_hint": arg_value(args, "semantic_hint", ""),
            "document_type": arg_value(args, "document_type", ""),
            "environment": arg_value(args, "environment", ""),
            "workflow": arg_value(args, "workflow", ""),
            "min_reliability": arg_value(args, "min_reliability", None),
            "min_freshness": arg_value(args, "min_freshness", None),
        },
        "candidate_count": len(rows),
        "selected_chunks": selected_summary,
        "dropped_chunks": dropped,
        "duckdb_search": duckdb_search if backend == "duckdb" else {},
    }
    context_pack = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "rag-context-pack",
        "context_pack_id": context_pack_id,
        "retrieval_id": retrieval_id,
        "query": args.query,
        "created_at": retrieval_result["created_at"],
        "compression": {
            "method": f"{args.search_mode}-retrieval-extractive-compression",
            "backend": backend,
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
    if args.write_markdown:
        write_context_markdown(markdown_path, context_pack)
    return {
        "retrieval_result": relative_to_repo(repo_root, retrieval_path),
        "context_pack": relative_to_repo(repo_root, context_path),
        "context_markdown": relative_to_repo(repo_root, markdown_path) if args.write_markdown else "",
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
