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


def test_chunk_documents_parser_and_heading_path_edges(tmp_path: Path) -> None:
    parser = chunk_documents.build_parser()
    args = parser.parse_args(
        [
            "--input-dir",
            "custom/normalized",
            "--output-dir",
            "custom/chunks",
            "--chunk-size",
            "120",
            "--chunk-overlap",
            "12",
            "--repo-root",
            str(tmp_path),
            "--clean-output",
        ]
    )

    assert args.input_dir == "custom/normalized"
    assert args.output_dir == "custom/chunks"
    assert args.chunk_size == 120
    assert args.chunk_overlap == 12
    assert args.repo_root == str(tmp_path)
    assert args.clean_output is True

    heading_path = chunk_documents.heading_path_for_text(
        "# Root\n\ntext\n\n### Deep\n\n## Sibling\n\n#### Leaf\n"
    )
    assert heading_path == ["Root", "Sibling", "Leaf"]
    assert chunk_documents.heading_path_for_text("plain text") == []


def test_split_content_short_empty_and_overlap_edges() -> None:
    assert chunk_documents.split_content("", 10, 0) == []
    assert chunk_documents.split_content("short text", 100, 0) == [(0, 10, "short text")]

    chunks = chunk_documents.split_content("alpha\n\nbeta beta beta\n\ngamma gamma gamma", 18, 4)

    assert len(chunks) >= 2
    assert chunks[0][2].startswith("alpha")
    assert chunks[1][0] <= chunks[0][1]
    assert "beta" in chunks[1][2]
    assert chunks[-1][2].endswith("gamma gamma gamma")

    with pytest.raises(ValueError, match="--chunk-overlap"):
        chunk_documents.split_content("text", 10, -1)


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


def test_chunk_document_rejects_non_object_json(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    normalized = repo / "rag" / "normalized" / "bad.json"
    normalized.parent.mkdir(parents=True)
    normalized.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid normalized document"):
        chunk_documents.chunk_document(
            repo,
            normalized,
            repo / "rag" / "chunks",
            argparse.Namespace(chunk_size=200, chunk_overlap=0),
        )


def test_discover_documents_errors_and_sorts_recursively(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError, match="RAG normalized directory not found"):
        chunk_documents.discover_documents(missing)

    input_dir = tmp_path / "normalized"
    nested = input_dir / "nested"
    nested.mkdir(parents=True)
    first = nested / "a.json"
    second = input_dir / "b.json"
    ignored = input_dir / "note.txt"
    first.write_text("{}", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")
    ignored.write_text("ignored", encoding="utf-8")

    assert chunk_documents.discover_documents(input_dir) == [second, first]


def test_chunk_documents_run_cleans_output_and_supports_absolute_dirs(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    input_dir = tmp_path / "absolute-normalized"
    output_dir = tmp_path / "absolute-chunks"
    input_dir.mkdir()
    output_dir.mkdir()
    stale = output_dir / "stale.json"
    stale.write_text("{}", encoding="utf-8")
    (output_dir / "keep.txt").write_text("keep", encoding="utf-8")
    (input_dir / "doc.json").write_text(
        json.dumps(
            {
                "document_id": "doc-abs",
                "source_path": "rag/source/report.md",
                "document_type": "note",
                "title": "Absolute",
                "content": "# Absolute\n\ncontent",
                "metadata": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(repo),
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        chunk_size=100,
        chunk_overlap=0,
        clean_output=True,
    )

    result = chunk_documents.run(args)

    assert result["document_count"] == 1
    assert result["chunk_count"] == 1
    assert not stale.exists()
    assert (output_dir / "keep.txt").exists()
    assert result["input_dir"] == str(input_dir)
    assert result["output_dir"] == str(output_dir)
    assert Path(result["chunks"][0]).exists()


def test_chunk_documents_main_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(
        chunk_documents,
        "run",
        lambda args: {"document_count": 1, "chunk_count": 2, "chunks": ["rag/chunks/a.json"]},
    )

    assert chunk_documents.main(["--repo-root", str(tmp_path), "--chunk-size", "50"]) == 0
    assert '"chunk_count": 2' in capsys.readouterr().out

    def fail(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(chunk_documents, "run", fail)
    assert chunk_documents.main(["--repo-root", str(tmp_path)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err


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
