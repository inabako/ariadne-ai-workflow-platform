from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from runtime.rag import retrieve_context


def test_read_jsonl_reports_line_number_for_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "chunks.jsonl"
    path.write_text('{"ok": true}\n{bad}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSONL"):
        retrieve_context.read_jsonl(path)


def test_retrieve_filters_rows_and_selects_keyword_matches() -> None:
    rows = [
        {
            "chunk_id": "a",
            "content": "Docker Compose validation and health check",
            "heading_path": ["Docker"],
            "repository": "repo-a",
            "branch": "develop",
            "tags": ["iac"],
        },
        {
            "chunk_id": "b",
            "content": "GUI layout",
            "heading_path": ["GUI"],
            "repository": "repo-b",
            "branch": "main",
            "tags": ["gui"],
        },
    ]
    args = argparse.Namespace(
        query="docker health",
        top_k=1,
        search_mode="keyword",
        project="",
        repository="repo-a",
        branch="develop",
        tag=["iac"],
        source_type="",
        category="",
        trust_level="",
    )

    selected, dropped = retrieve_context.retrieve(rows, {}, 0, args)

    assert [row["chunk_id"] for row in selected] == ["a"]
    assert dropped == [{"chunk_id": "b", "score": 0, "reason": "filtered"}]


def test_retrieve_requires_positive_top_k() -> None:
    args = argparse.Namespace(
        query="docker",
        top_k=0,
        search_mode="keyword",
        project="",
        repository="",
        branch="",
        tag=[],
        source_type="",
        category="",
        trust_level="",
    )

    with pytest.raises(ValueError, match="--top-k must be positive"):
        retrieve_context.retrieve([], {}, 0, args)


def test_run_keyword_retrieval_writes_context_pack_and_markdown(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    chunks_index = repo / "rag" / "indexes" / "chunks.jsonl"
    chunks_index.parent.mkdir(parents=True)
    row = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "source_path": "rag/source/report.md",
        "chunk_path": "rag/chunks/chunk-1.json",
        "title": "Docker report",
        "heading_path": ["Docker Desktop validation"],
        "content": "Docker Desktop validation uses docker compose config and health check.",
        "chunk_index": 0,
        "repository": "inabako/example",
        "branch": "develop",
        "tags": ["iac"],
    }
    chunks_index.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    args = argparse.Namespace(
        query="docker compose health",
        chunks_index=str(chunks_index),
        embeddings_index=str(repo / "rag" / "embeddings" / "missing.jsonl"),
        output_dir="rag/retrieval",
        top_k=3,
        max_chars=1000,
        search_mode="keyword",
        project="",
        repository="inabako/example",
        branch="develop",
        tag=["iac"],
        source_type="",
        category="",
        trust_level="",
        repo_root=str(repo),
        write_markdown=True,
    )

    result = retrieve_context.run(args)

    assert result["candidate_count"] == 1
    assert result["selected_chunk_count"] == 1
    assert (repo / result["retrieval_result"]).exists()
    assert (repo / result["context_pack"]).exists()
    assert (repo / result["context_markdown"]).exists()
    context_pack = json.loads((repo / result["context_pack"]).read_text(encoding="utf-8"))
    assert context_pack["compression"]["retrieval_method"] == "keyword"
    assert "docker compose config" in context_pack["context"]


def test_semantic_search_requires_embeddings_index(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    chunks_index = repo / "rag" / "indexes" / "chunks.jsonl"
    chunks_index.parent.mkdir(parents=True)
    chunks_index.write_text(json.dumps({"chunk_id": "chunk-1", "content": "docker"}) + "\n", encoding="utf-8")
    args = argparse.Namespace(
        query="docker",
        chunks_index=str(chunks_index),
        embeddings_index=str(repo / "rag" / "embeddings" / "missing.jsonl"),
        output_dir="rag/retrieval",
        top_k=1,
        max_chars=1000,
        search_mode="semantic",
        project="",
        repository="",
        branch="",
        tag=[],
        source_type="",
        category="",
        trust_level="",
        repo_root=str(repo),
        write_markdown=False,
    )

    with pytest.raises(FileNotFoundError, match="Semantic search requires embeddings index"):
        retrieve_context.run(args)
