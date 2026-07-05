from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from runtime.rag import build_index, chunk_documents, embed_chunks, normalize_documents


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    return repo


def test_normalize_document_preserves_front_matter_and_headings(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    source = repo / "rag" / "corrective-action-report" / "report.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "---\n"
        "title: Docker検証レポート\n"
        "repository: inabako/example\n"
        "branch: develop\n"
        "tags:\n"
        "- iac\n"
        "- docker\n"
        "---\n"
        "# Docker検証レポート\n\n"
        "Docker Composeの検証内容です。\n\n"
        "## Health Check\n\n"
        "health checkを確認します。\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(
        document_type="corrective-action-report",
        project="",
        repository="",
        branch="",
        commit="",
        status="draft",
    )

    document = normalize_documents.normalize_document(repo, source, repo / "rag" / "normalized", args)

    assert document["schema_version"] == "1.0"
    assert document["title"] == "Docker検証レポート"
    assert document["metadata"]["repository"] == "inabako/example"
    assert document["metadata"]["tags"] == ["iac", "docker"]
    assert document["headings"] == ["Docker検証レポート", "Health Check"]
    assert (repo / document["normalized_path"]).exists()


def test_discover_sources_ignores_readme(tmp_path: Path) -> None:
    source_dir = tmp_path / "rag-source"
    source_dir.mkdir()
    (source_dir / "README.md").write_text("# readme\n", encoding="utf-8")
    report = source_dir / "report.md"
    report.write_text("# report\n", encoding="utf-8")

    assert normalize_documents.discover_sources(source_dir) == [report]


def test_split_content_validates_chunk_settings() -> None:
    with pytest.raises(ValueError, match="--chunk-size"):
        chunk_documents.split_content("text", 0, 0)

    with pytest.raises(ValueError, match="--chunk-overlap"):
        chunk_documents.split_content("text", 10, 10)


def test_chunk_document_writes_chunk_with_heading_path(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    normalized = repo / "rag" / "normalized" / "doc.json"
    normalized.parent.mkdir(parents=True)
    normalized.write_text(
        json.dumps(
            {
                "document_id": "doc-1",
                "source_path": "rag/source/report.md",
                "document_type": "corrective-action-report",
                "title": "Report",
                "content": "# Section\n\nDocker Compose validation paragraph.",
                "metadata": {"repository": "inabako/example", "tags": ["docker"]},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(chunk_size=200, chunk_overlap=0)

    chunks = chunk_documents.chunk_document(repo, normalized, repo / "rag" / "chunks", args)

    assert len(chunks) == 1
    assert chunks[0]["document_id"] == "doc-1"
    assert chunks[0]["heading_path"] == ["Section"]
    assert chunks[0]["metadata"]["title"] == "Report"
    assert (repo / "rag" / "chunks" / f"{chunks[0]['chunk_id']}.json").exists()


def test_build_index_writes_document_and_chunk_jsonl(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    normalized = repo / "rag" / "normalized" / "doc.json"
    chunk = repo / "rag" / "chunks" / "chunk.json"
    normalized.parent.mkdir(parents=True)
    chunk.parent.mkdir(parents=True)
    normalized.write_text(
        json.dumps(
            {
                "document_id": "doc-1",
                "document_type": "corrective-action-report",
                "title": "Report",
                "source_path": "rag/source/report.md",
                "headings": ["Report"],
                "metadata": {"repository": "inabako/example", "branch": "develop", "tags": ["docker"]},
            }
        ),
        encoding="utf-8",
    )
    chunk.write_text(
        json.dumps(
            {
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "source_path": "rag/source/report.md",
                "chunk_index": 0,
                "heading_path": ["Report"],
                "content": "Docker content",
                "metadata": {"repository": "inabako/example", "branch": "develop", "tags": ["docker"]},
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(repo),
        normalized_dir="rag/normalized",
        chunks_dir="rag/chunks",
        output_dir="rag/indexes",
    )

    result = build_index.run(args)

    assert result["document_count"] == 1
    assert result["chunk_count"] == 1
    documents = (repo / result["documents_index"]).read_text(encoding="utf-8")
    chunks = (repo / result["chunks_index"]).read_text(encoding="utf-8")
    assert '"document_id": "doc-1"' in documents
    assert '"chunk_id": "chunk-1"' in chunks


def test_embed_chunks_is_deterministic_and_validates_dimensions(tmp_path: Path) -> None:
    row = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "title": "Docker",
        "content": "Docker Compose health check",
        "heading_path": ["Docker"],
        "tags": ["iac"],
    }

    first = embed_chunks.build_embedding(row, 32)
    second = embed_chunks.build_embedding(row, 32)

    assert first == second
    assert first["embedding_model"] == "local-hash-embedding-v1"
    assert first["dimensions"] == 32
    assert first["embedding"]
    with pytest.raises(ValueError, match="--dimensions"):
        embed_chunks.sparse_embedding("Docker", 0)


def test_embed_chunks_run_writes_jsonl(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    chunks_index = repo / "rag" / "indexes" / "chunks.jsonl"
    chunks_index.parent.mkdir(parents=True)
    chunks_index.write_text(
        json.dumps({"chunk_id": "chunk-1", "document_id": "doc-1", "content": "Docker"}) + "\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(repo),
        chunks_index="rag/indexes/chunks.jsonl",
        output="rag/embeddings/chunks-embeddings.jsonl",
        dimensions=16,
    )

    result = embed_chunks.run(args)

    assert result["embedding_count"] == 1
    output = repo / result["embeddings_index"]
    assert output.exists()
    assert '"embedding_model": "local-hash-embedding-v1"' in output.read_text(encoding="utf-8")
