from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl


def write_tiny_indexes(repo: Path) -> tuple[Path, Path]:
    indexes = repo / "rag" / "indexes"
    embeddings_dir = repo / "rag" / "embeddings"
    indexes.mkdir(parents=True)
    embeddings_dir.mkdir(parents=True)
    chunks = indexes / "chunks.jsonl"
    embeddings = embeddings_dir / "chunks-embeddings.jsonl"
    row = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "source_path": "rag/doc.md",
        "chunk_path": "rag/chunks/chunk-1.json",
        "chunk_index": 0,
        "title": "Runtime RAG",
        "heading_path": ["RAG"],
        "content": "RAG runtime retrieve context pack for workflow review and knowledge reuse.",
    }
    chunks.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    embeddings.write_text("", encoding="utf-8")
    return chunks, embeddings


def test_ctl_rag_retrieve_writes_context_pack_and_runtime_log(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    chunks, embeddings = write_tiny_indexes(repo)
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "rag",
            "retrieve",
            "rag runtime",
            "--chunks-index",
            str(chunks.relative_to(repo)),
            "--embeddings-index",
            str(embeddings.relative_to(repo)),
            "--output-dir",
            "rag/retrieval",
            "--search-mode",
            "keyword",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["selected_chunk_count"] == 1
    assert (repo / result["context_pack"]).exists()
    completed = json.loads((repo / "logs" / "runtime" / "runtime-events.log").read_text(encoding="utf-8").splitlines()[-1].split(" | ", 3)[3])
    assert completed["command"] == "rag retrieve"
    assert completed["operation_id"] == "rag:retrieve"


def test_ctl_rag_jsonize_converts_sources(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    rag = repo / "rag"
    rag.mkdir(parents=True)
    (rag / "note.md").write_text("# Note\n\nRAG source for CTL jsonize.\n", encoding="utf-8")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "rag",
            "jsonize",
            "--rag-dir",
            "rag",
            "--output-dir",
            "rag/jsonized",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["converted_count"] == 1
    assert (repo / result["artifacts"][0]["json_path"]).exists()


def test_ctl_rag_migrate_legacy_root_moves_backup(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    legacy = repo / "work" / "db" / "ariadne-knowledge-platform" / "legacy-root-rag-20260723010101"
    (legacy / "chunks").mkdir(parents=True)
    (legacy / "chunks" / "one.json").write_text('{"chunk": 1}', encoding="utf-8")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "rag",
            "migrate-legacy-root",
            "--legacy-dir",
            str(legacy.relative_to(repo)),
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["moved"] == ["chunks/one.json"]
    assert (repo / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "chunks" / "one.json").exists()


def test_ctl_rag_build_dry_run_reports_plan_without_writing_outputs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    source = repo / "rag" / "source"
    source.mkdir(parents=True)
    (source / "note.md").write_text("# Note\n\nRAG source.\n", encoding="utf-8")
    output = repo / "rag" / "retrieval" / "build.json"
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "rag",
            "build",
            "--source-dir",
            "rag/source",
            "--normalized-dir",
            "rag/normalized",
            "--chunks-dir",
            "rag/chunks",
            "--indexes-dir",
            "rag/indexes",
            "--embeddings-output",
            "rag/embeddings/chunks.jsonl",
            "--output",
            str(output.relative_to(repo)),
            "--skip-optimization",
            "--dry-run",
            "--json",
        ]
    )

    code, output_text = ctl.run(args)

    assert code == 0
    result = json.loads(output_text)
    assert result["artifact_type"] == "rag-dry-run-plan"
    assert result["status"] == "dry-run"
    assert result["plan_output"] == "rag/retrieval/build.json"
    assert result["written"] is True
    assert result["command"] == "rag build"
    assert result["would_run"] is False
    assert any(item["path"] == "rag/source" for item in result["reads"])
    assert any(item["path"] == "rag/retrieval/build.json" for item in result["writes"])
    assert output.exists()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["artifact_type"] == "rag-dry-run-plan"
    assert saved["plan_output"] == "rag/retrieval/build.json"
    assert not (repo / "rag" / "normalized").exists()


def test_ctl_rag_duckdb_rebuild_dry_run_reports_plan_without_creating_db(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    db = repo / "db" / "rag" / "knowledge.duckdb"
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "rag",
            "duckdb",
            "--db",
            str(db.relative_to(repo)),
            "rebuild",
            "--source-repo",
            "work/db/ariadne-knowledge-platform",
            "--reset",
            "--dry-run",
            "--output",
            "work/evidence/duckdb-rebuild-dry-run.json",
            "--json",
        ]
    )

    code, output_text = ctl.run(args)

    assert code == 0
    result = json.loads(output_text)
    assert result["artifact_type"] == "rag-dry-run-plan"
    assert result["command"] == "rag duckdb rebuild"
    assert result["plan_output"] == "work/evidence/duckdb-rebuild-dry-run.json"
    assert result["written"] is True
    assert result["options"]["reset"] is True
    assert any(item["path"] == "work/db/ariadne-knowledge-platform" for item in result["reads"])
    assert any(item["path"] == "db/rag/knowledge.duckdb" for item in result["writes"])
    assert not db.exists()
    assert (repo / "work" / "evidence" / "duckdb-rebuild-dry-run.json").exists()


def test_ctl_rag_semantic_hints_build_dry_run_reports_generation_and_build_outputs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "rag",
            "semantic-hints",
            "build",
            "--source-dir",
            "work/db/ariadne-knowledge-platform/semantic-hints",
            "--rag-source-dir",
            "work/db/ariadne-knowledge-platform/rag/semantic-hints",
            "--output",
            "work/db/ariadne-knowledge-platform/rag/retrieval/semantic-hints-build-latest.json",
            "--dry-run",
            "--json",
        ]
    )

    code, output_text = ctl.run(args)

    assert code == 0
    result = json.loads(output_text)
    assert result["artifact_type"] == "rag-dry-run-plan"
    assert result["plan_output"] == "work/db/ariadne-knowledge-platform/rag/retrieval/semantic-hints-build-latest.json"
    assert result["written"] is True
    assert result["command"] == "rag semantic-hints build"
    assert any(item["path"] == "work/db/ariadne-knowledge-platform/semantic-hints" for item in result["reads"])
    assert any(item["role"] == "generated-semantic-hint-source" for item in result["writes"])
    assert not (repo / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "semantic-hints").exists()
