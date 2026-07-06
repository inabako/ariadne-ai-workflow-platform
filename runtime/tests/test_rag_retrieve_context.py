from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from runtime.rag import retrieve_context


def make_args(**overrides):
    values = {
        "query": "docker health",
        "chunks_index": "rag/indexes/chunks.jsonl",
        "embeddings_index": "rag/embeddings/chunks-embeddings.jsonl",
        "output_dir": "rag/retrieval",
        "top_k": 2,
        "max_chars": 1000,
        "search_mode": "hybrid",
        "project": "",
        "repository": "",
        "branch": "",
        "tag": [],
        "source_type": "",
        "category": "",
        "trust_level": "",
        "repo_root": "",
        "write_markdown": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_read_jsonl_reports_line_number_for_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "chunks.jsonl"
    path.write_text('{"ok": true}\n{bad}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSONL"):
        retrieve_context.read_jsonl(path)


def test_read_jsonl_requires_existing_file_and_ignores_non_object_rows(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    with pytest.raises(FileNotFoundError, match="RAG chunk index not found"):
        retrieve_context.read_jsonl(missing)

    path = tmp_path / "chunks.jsonl"
    path.write_text('\n{"chunk_id": "ok"}\n["ignored"]\n', encoding="utf-8")

    assert retrieve_context.read_jsonl(path) == [{"chunk_id": "ok"}]


def test_tokenize_sparse_embedding_and_cosine_cover_cjk_and_empty_values() -> None:
    tokens = retrieve_context.tokenize("Docker 検証 テスト")
    embedding = retrieve_context.sparse_embedding("docker docker compose", dimensions=16)

    assert "docker" in tokens
    assert "検証" in tokens
    assert retrieve_context.cjk_bigrams("検証") == ["検証"]
    assert retrieve_context.sparse_embedding("", dimensions=16) == {}
    assert retrieve_context.cosine_similarity({}, embedding) == 0.0
    assert retrieve_context.cosine_similarity(embedding, embedding) == pytest.approx(1.0)


def test_filter_row_applies_all_optional_filters() -> None:
    row = {
        "project": "ariadne",
        "repository": "owner/repo",
        "branch": "main",
        "tags": ["rag", "workflow"],
        "source_type": "external-web",
        "category": "docs",
        "trust_level": "official",
    }

    assert retrieve_context.filter_row(
        row,
        make_args(project="ariadne", repository="owner/repo", branch="main", tag=["rag"], source_type="external-web", category="docs", trust_level="official"),
    )
    assert not retrieve_context.filter_row(row, make_args(project="other"))
    assert not retrieve_context.filter_row(row, make_args(repository="other/repo"))
    assert not retrieve_context.filter_row(row, make_args(branch="develop"))
    assert not retrieve_context.filter_row(row, make_args(tag=["missing"]))
    assert not retrieve_context.filter_row(row, make_args(source_type="internal-work"))
    assert not retrieve_context.filter_row(row, make_args(category="blog"))
    assert not retrieve_context.filter_row(row, make_args(trust_level="community"))


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


def test_retrieve_scores_semantic_hybrid_no_match_and_below_top_k() -> None:
    rows = [
        {"chunk_id": "a", "content": "docker compose health", "heading_path": [], "chunk_index": 0},
        {"chunk_id": "b", "content": "compose health gateway", "heading_path": [], "chunk_index": 1},
        {"chunk_id": "c", "content": "unrelated gui", "heading_path": [], "chunk_index": 2},
    ]
    embeddings = {
        "a": {"chunk_id": "a", "dimensions": 32, "embedding": retrieve_context.sparse_embedding("docker health", 32)},
        "b": {"chunk_id": "b", "dimensions": 32, "embedding": retrieve_context.sparse_embedding("health", 32)},
    }

    semantic, dropped = retrieve_context.retrieve(rows, embeddings, 32, make_args(query="docker health", top_k=1, search_mode="semantic"))
    hybrid, hybrid_dropped = retrieve_context.retrieve(rows, embeddings, 32, make_args(query="docker health", top_k=2, search_mode="hybrid"))

    assert semantic[0]["chunk_id"] == "a"
    assert any(item["reason"] == "below-top-k" for item in dropped)
    assert [row["chunk_id"] for row in hybrid] == ["a", "b"]
    assert any(item["chunk_id"] == "c" and item["reason"] == "no-query-match" for item in hybrid_dropped)


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


def test_split_units_and_compress_chunk_cover_matching_fallback_and_truncation() -> None:
    long_line = "x" * 720
    units = retrieve_context.split_units(f"first paragraph\n\n{long_line}\nsecond line")

    assert units[0] == "first paragraph"
    assert long_line in units
    assert "second line" in units

    content = "alpha first sentence.\n\nDocker compose health details are important.\n\nother notes"
    matched = retrieve_context.compress_chunk({"content": content}, ["docker"], max_chars=200)
    fallback = retrieve_context.compress_chunk({"content": content}, ["missing"], max_chars=200)
    truncated = retrieve_context.compress_chunk({"content": "docker " * 200}, ["docker"], max_chars=80)

    assert "Docker compose health" in matched
    assert "alpha first sentence" in fallback
    assert truncated.endswith("[truncated]")
    assert retrieve_context.estimate_tokens("abcde") == 2


def test_build_context_respects_budget_and_preserves_source_metadata() -> None:
    selected = [
        {
            "chunk_id": "a",
            "document_id": "doc-a",
            "source_path": "rag/source/a.md",
            "chunk_path": "rag/chunks/a.json",
            "heading_path": ["A", "Docker"],
            "content": "docker health " * 100,
            "_score": 9,
            "source_type": "external-web",
            "category": "docs",
            "topic": "docker",
            "trust_level": "official",
            "retrieved_at": "2026-07-06T00:00:00Z",
            "verify_before_use": True,
            "sources": [{"url": "https://example.com"}],
        },
        {"chunk_id": "b", "content": "health gateway", "_score": 1},
    ]

    context, sources = retrieve_context.build_context(selected, make_args(query="docker health", max_chars=360, top_k=2))

    assert "## a" in context
    assert len(context) <= 380
    assert sources[0]["chunk_id"] == "a"
    assert sources[0]["verify_before_use"] is True
    assert sources[0]["sources"] == [{"url": "https://example.com"}]


def test_write_context_markdown_lists_sources(tmp_path: Path) -> None:
    path = tmp_path / "context.md"
    retrieve_context.write_context_markdown(
        path,
        {
            "query": "docker",
            "created_at": "2026-07-06T00:00:00Z",
            "compression": {"estimated_tokens": 10},
            "sources": [{"chunk_id": "chunk-1", "source_path": "rag/source/report.md"}],
            "context": "compressed context",
        },
    )

    text = path.read_text(encoding="utf-8")
    assert "RAG Context Pack" in text
    assert "`chunk-1`" in text
    assert "compressed context" in text


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


def test_run_hybrid_retrieval_uses_embeddings_and_absolute_output_dir(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    chunks_index = repo / "rag" / "indexes" / "chunks.jsonl"
    embeddings_index = repo / "rag" / "embeddings" / "chunks-embeddings.jsonl"
    output_dir = tmp_path / "retrieval-output"
    chunks_index.parent.mkdir(parents=True)
    embeddings_index.parent.mkdir(parents=True)
    row = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "source_path": "rag/source/report.md",
        "content": "gateway health",
        "chunk_index": 0,
        "source_type": "internal-work",
        "category": "ops",
        "trust_level": "local",
    }
    chunks_index.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    embeddings_index.write_text(
        json.dumps(
            {
                "chunk_id": "chunk-1",
                "dimensions": 32,
                "embedding": retrieve_context.sparse_embedding("docker health gateway", 32),
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    result = retrieve_context.run(
        make_args(
            query="docker health",
            chunks_index=str(chunks_index),
            embeddings_index=str(embeddings_index),
            output_dir=str(output_dir),
            search_mode="hybrid",
            source_type="internal-work",
            category="ops",
            trust_level="local",
            repo_root=str(repo),
        )
    )

    retrieval = json.loads((repo / result["retrieval_result"]).read_text(encoding="utf-8-sig"))
    context_pack = json.loads((repo / result["context_pack"]).read_text(encoding="utf-8-sig"))
    assert result["selected_chunk_count"] == 1
    assert retrieval["embeddings_index_path"] == "rag/embeddings/chunks-embeddings.jsonl"
    assert context_pack["compression"]["embedding_model"] == "local-hash-embedding-v1"
    assert output_dir.exists()


def test_run_rejects_non_positive_max_chars(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="--max-chars must be positive"):
        retrieve_context.run(make_args(max_chars=0, repo_root=str(tmp_path)))


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


def test_main_prints_json(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(
        retrieve_context,
        "run",
        lambda args: {
            "retrieval_result": "rag/retrieval/result.json",
            "context_pack": "rag/retrieval/context.json",
            "context_markdown": "",
            "candidate_count": 1,
            "selected_chunk_count": 1,
            "estimated_tokens": 3,
        },
    )

    code = retrieve_context.main(["docker health"])

    captured = capsys.readouterr()
    assert code == 0
    assert '"selected_chunk_count": 1' in captured.out
