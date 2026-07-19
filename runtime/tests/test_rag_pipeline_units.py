from __future__ import annotations

import argparse
import json
import runpy
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


def test_normalize_documents_parser_and_scalar_helpers(tmp_path: Path) -> None:
    parser = normalize_documents.build_parser()
    args = parser.parse_args(
        [
            "--source-dir",
            "custom/source",
            "--output-dir",
            "custom/normalized",
            "--document-type",
            "external-web-knowledge",
            "--repo-root",
            str(tmp_path),
            "--project",
            "ariadne",
            "--repository",
            "inabako/ariadne",
            "--branch",
            "main",
            "--commit",
            "abc123",
            "--status",
            "approved",
            "--clean-output",
        ]
    )

    assert args.source_dir == "custom/source"
    assert args.output_dir == "custom/normalized"
    assert args.document_type == "external-web-knowledge"
    assert args.repo_root == str(tmp_path)
    assert args.clean_output is True
    assert normalize_documents.parse_scalar("   ") == ""
    assert normalize_documents.parse_scalar("[alpha, 'beta', \"gamma\", ]") == ["alpha", "beta", "gamma"]
    assert normalize_documents.parse_scalar("'quoted value'") == "quoted value"
    assert normalize_documents.parse_bool(True) is True
    assert normalize_documents.parse_bool("YES") is True
    assert normalize_documents.parse_bool("off") is False
    assert normalize_documents.parse_bool(1) is True


def test_normalize_documents_front_matter_helper_edges(tmp_path: Path) -> None:
    list_value, next_index = normalize_documents.parse_front_matter_value(
        ["tags:", "- alpha", "- 'beta'", "summary: done"],
        0,
    )
    empty_value, empty_next = normalize_documents.parse_front_matter_value(["tags:", "summary: done"], 0)
    metadata, content = normalize_documents.parse_front_matter(
        "---\n"
        "\n"
        "# comment\n"
        "ignored line\n"
        "title: Example\n"
        "claims:\n"
        "- safe\n"
        "---\n"
        "# Body\n"
    )

    assert list_value == ["alpha", "beta"]
    assert next_index == 3
    assert empty_value == ""
    assert empty_next == 1
    assert metadata == {"title": "Example", "claims": ["safe"]}
    assert content == "# Body\n"
    assert normalize_documents.title_from_content("plain body", tmp_path / "fallback-name.md") == "fallback-name"
    assert normalize_documents.ensure_list("single") == ["single"]
    assert normalize_documents.first_string(["", "alpha", "beta"]) == "alpha, beta"


def test_normalize_document_includes_external_web_metadata_and_defaults(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    source = repo / "rag" / "external" / "web.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "---\n"
        "type: external-web-knowledge\n"
        "artifact_type: source-note\n"
        "source_type: web\n"
        "source_kind: official-docs\n"
        "source_owner: vendor\n"
        "category: runtime\n"
        "topic: docker\n"
        "trust_level: high\n"
        "retrieved_at: 2026-07-07T00:00:00Z\n"
        "freshness_policy: verify-before-use\n"
        "sources: [official docs, changelog]\n"
        "urls:\n"
        "- https://example.test/docs\n"
        "claims:\n"
        "- current behavior\n"
        "verification_notes:\n"
        "- cite before use\n"
        "verify_before_use: yes\n"
        "areas: api\n"
        "severity_focus:\n"
        "- medium\n"
        "owner_agent: web-rag\n"
        "---\n"
        "No heading body.\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(
        document_type="corrective-action-report",
        project="ariadne",
        repository="",
        branch="main",
        commit="",
        status="draft",
    )

    document = normalize_documents.normalize_document(repo, source, repo / "rag" / "normalized", args)

    assert document["document_type"] == "external-web-knowledge"
    assert document["title"] == "web"
    assert document["metadata"]["commit"] == "unknown"
    assert document["metadata"]["agent"] == "web-rag"
    assert document["metadata"]["tags"] == ["external-web-knowledge"]
    assert document["metadata"]["areas"] == ["api"]
    assert document["metadata"]["severity_focus"] == ["medium"]
    assert document["metadata"]["artifact_type"] == "source-note"
    assert document["metadata"]["sources"] == ["official docs", "changelog"]
    assert document["metadata"]["urls"] == ["https://example.test/docs"]
    assert document["metadata"]["claims"] == ["current behavior"]
    assert document["metadata"]["verify_before_use"] is True


def test_normalize_documents_run_cleans_json_output_and_accepts_absolute_paths(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    source_dir = tmp_path / "absolute-source"
    output_dir = tmp_path / "absolute-output"
    source_dir.mkdir()
    output_dir.mkdir()
    (source_dir / "README.md").write_text("# ignored\n", encoding="utf-8")
    (source_dir / "report.md").write_text("# Report\n\nBody\n", encoding="utf-8")
    old_json = output_dir / "old.json"
    old_text = output_dir / "old.txt"
    old_json.write_text("{}", encoding="utf-8")
    old_text.write_text("keep", encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        source_dir=str(source_dir),
        output_dir=str(output_dir),
        document_type="note",
        project="ariadne",
        repository="repo",
        branch="main",
        commit="abc123",
        status="approved",
        clean_output=True,
    )

    result = normalize_documents.run(args)

    assert result["source_dir"] == str(source_dir.resolve())
    assert result["output_dir"] == str(output_dir.resolve())
    assert result["document_count"] == 1
    assert len(result["documents"]) == 1
    assert not old_json.exists()
    assert old_text.exists()

    protected = repo / "db" / "rag"
    protected.mkdir(parents=True)
    with pytest.raises(ValueError, match="Refusing to clean protected RAG path"):
        normalize_documents.run(
            argparse.Namespace(
                repo_root=str(repo),
                source_dir=str(source_dir),
                output_dir="db/rag",
                document_type="note",
                project="ariadne",
                repository="repo",
                branch="main",
                commit="abc123",
                status="approved",
                clean_output=True,
            )
        )


def test_normalize_documents_missing_source_and_main_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    with pytest.raises(FileNotFoundError, match="RAG source directory not found"):
        normalize_documents.discover_sources(tmp_path / "missing")

    repo = make_repo(tmp_path)
    source_dir = repo / "rag" / "source"
    source_dir.mkdir(parents=True)
    (source_dir / "report.md").write_text("# Report\n\nBody\n", encoding="utf-8")
    assert normalize_documents.main(
        [
            "--repo-root",
            str(repo),
            "--source-dir",
            "rag/source",
            "--output-dir",
            "rag/normalized",
            "--document-type",
            "note",
        ]
    ) == 0
    assert '"document_count": 1' in capsys.readouterr().out

    def raise_error(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(normalize_documents, "run", raise_error)
    assert normalize_documents.main(["--repo-root", str(repo)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err


def test_normalize_documents_module_can_be_loaded_as_script_path() -> None:
    namespace = runpy.run_path(str(Path(normalize_documents.__file__)))

    assert namespace["build_parser"]


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
    assert chunk_documents.split_content("single", 3, 0) == [(0, 6, "single")]

    chunks = chunk_documents.split_content("alpha\n\nbeta beta beta\n\ngamma gamma gamma", 18, 4)

    assert len(chunks) >= 2
    assert chunks[0][2].startswith("alpha")
    assert chunks[1][0] <= chunks[0][1]
    assert "beta" in chunks[1][2]
    assert chunks[-1][2].endswith("gamma gamma gamma")

    with pytest.raises(ValueError, match="--chunk-overlap"):
        chunk_documents.split_content("text", 10, -1)


def test_split_content_defensive_fallback_preserves_text_when_splitter_yields_no_parts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_split(pattern: str, text: str) -> list[str]:
        assert pattern == r"(\n\s*\n)"
        assert text == "runtime rescue thread"
        return [""]

    monkeypatch.setattr(chunk_documents.re, "split", fake_split)

    assert chunk_documents.split_content("runtime rescue thread", 100, 0) == [
        (0, len("runtime rescue thread"), "runtime rescue thread")
    ]


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

    protected = repo / "db" / "rag"
    with pytest.raises(ValueError, match="Refusing to clean protected RAG path"):
        chunk_documents.run(
            argparse.Namespace(
                repo_root=str(repo),
                input_dir=str(input_dir),
                output_dir=str(protected),
                chunk_size=100,
                chunk_overlap=0,
                clean_output=True,
            )
        )


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

    namespace = runpy.run_path(str(Path(chunk_documents.__file__)))
    assert namespace["build_parser"]


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


def test_build_index_parser_invalid_rows_empty_discovery_main_and_script(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parser = build_index.build_parser()
    parsed = parser.parse_args(
        [
            "--normalized-dir",
            "custom/normalized",
            "--chunks-dir",
            "custom/chunks",
            "--output-dir",
            "custom/indexes",
            "--repo-root",
            str(tmp_path),
        ]
    )

    assert parsed.normalized_dir == "custom/normalized"
    assert parsed.chunks_dir == "custom/chunks"
    assert parsed.output_dir == "custom/indexes"
    assert parsed.repo_root == str(tmp_path)
    assert build_index.discover_json(tmp_path / "missing") == []

    invalid_document = tmp_path / "doc.json"
    invalid_chunk = tmp_path / "chunk.json"
    invalid_document.write_text("[]", encoding="utf-8")
    invalid_chunk.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid normalized document"):
        build_index.document_index_row(tmp_path, invalid_document)
    with pytest.raises(ValueError, match="Invalid chunk document"):
        build_index.chunk_index_row(tmp_path, invalid_chunk)

    repo = make_repo(tmp_path)
    assert build_index.main(
        [
            "--repo-root",
            str(repo),
            "--normalized-dir",
            "rag/missing-normalized",
            "--chunks-dir",
            "rag/missing-chunks",
            "--output-dir",
            "rag/indexes",
        ]
    ) == 0
    assert '"document_count": 0' in capsys.readouterr().out

    monkeypatch.setattr(build_index, "run", lambda args: (_ for _ in ()).throw(RuntimeError("boom")))
    assert build_index.main(["--repo-root", str(repo)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(build_index.__file__)))
    assert namespace["build_parser"]


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


def test_embed_chunks_parser_jsonl_edges_and_empty_embedding(tmp_path: Path) -> None:
    parser = embed_chunks.build_parser()

    args = parser.parse_args(
        [
            "--chunks-index",
            "custom/chunks.jsonl",
            "--output",
            "custom/embeddings.jsonl",
            "--dimensions",
            "16",
            "--repo-root",
            str(tmp_path),
        ]
    )

    assert args.chunks_index == "custom/chunks.jsonl"
    assert args.output == "custom/embeddings.jsonl"
    assert args.dimensions == 16
    assert args.repo_root == str(tmp_path)

    with pytest.raises(FileNotFoundError, match="RAG chunk index not found"):
        embed_chunks.read_jsonl(tmp_path / "missing.jsonl")

    mixed_jsonl = tmp_path / "mixed.jsonl"
    mixed_jsonl.write_text('{"ok": true}\n\n["ignored"]\n', encoding="utf-8")

    assert embed_chunks.read_jsonl(mixed_jsonl) == [{"ok": True}]

    invalid_jsonl = tmp_path / "invalid.jsonl"
    invalid_jsonl.write_text('{"ok": true}\n\n{bad}\n', encoding="utf-8")

    with pytest.raises(ValueError, match=r"Invalid JSONL .*:3"):
        embed_chunks.read_jsonl(invalid_jsonl)

    assert embed_chunks.sparse_embedding("", 8) == {}


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


def test_embed_chunks_main_success_error_and_script_load(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = make_repo(tmp_path)
    chunks_index = repo / "rag" / "indexes" / "chunks.jsonl"
    chunks_index.parent.mkdir(parents=True)
    chunks_index.write_text(
        json.dumps({"chunk_id": "chunk-1", "document_id": "doc-1", "content": "Docker"}) + "\n",
        encoding="utf-8",
    )

    exit_code = embed_chunks.main(
        [
            "--repo-root",
            str(repo),
            "--chunks-index",
            "rag/indexes/chunks.jsonl",
            "--output",
            "rag/embeddings/chunks-embeddings.jsonl",
            "--dimensions",
            "16",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"embedding_count": 1' in captured.out

    def fail_run(_args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(embed_chunks, "run", fail_run)

    assert embed_chunks.main(["--repo-root", str(repo)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(embed_chunks.__file__)))
    assert namespace["build_parser"]
