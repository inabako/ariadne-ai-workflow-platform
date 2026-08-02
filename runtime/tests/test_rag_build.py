from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

from runtime.rag import rag_build


def make_args(tmp_path: Path, **overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "repo_root": str(tmp_path),
        "work_id": "",
        "work_dir": "",
        "source_dir": "work/db/ariadne-knowledge-platform/rag/corrective-action-report",
        "document_type": "corrective-action-report",
        "normalized_dir": "work/db/ariadne-knowledge-platform/rag/normalized",
        "chunks_dir": "work/db/ariadne-knowledge-platform/rag/chunks",
        "optimized_chunks_dir": "work/db/ariadne-knowledge-platform/rag/optimized-chunks",
        "indexes_dir": "work/db/ariadne-knowledge-platform/rag/indexes",
        "embeddings_output": "work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl",
        "output": "work/db/ariadne-knowledge-platform/rag/retrieval/rag-build-run-latest.json",
        "ingestion_evidence_dir": "db/rag/evidence/ingestion",
        "ingestion_policy": "runtime/rag/policies/knowledge-ingestion-policy.json",
        "skip_optimization": False,
        "duckdb_migrate": False,
        "duckdb_path": "db/rag/ariadne-knowledge.duckdb",
        "duckdb_source_dir": "",
        "duckdb_error_log": "db/rag/migration-errors.jsonl",
        "duckdb_evidence_output": "db/rag/evidence/migration-summary.json",
        "duckdb_policy": "",
        "project": "ariadne",
        "repository": "ariadne-ai-workflow-platform",
        "branch": "main",
        "commit": "abc123",
        "status": "draft",
        "chunk_size": 500,
        "chunk_overlap": 50,
        "embedding_dimensions": 64,
        "clean_output": False,
        "standardize_filenames": False,
        "skip_standardize": False,
        "replace_references": False,
        "random_length": 8,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_rag_build_small_helpers(tmp_path: Path) -> None:
    absolute = tmp_path / "absolute"

    assert rag_build.resolve_repo_path(tmp_path, "rag/chunks") == tmp_path / "rag" / "chunks"
    assert rag_build.resolve_repo_path(tmp_path, str(absolute)) == absolute
    assert rag_build.resolve_work_dir(tmp_path, "", "") is None
    assert rag_build.resolve_work_dir(tmp_path, "issue-1", "") == tmp_path / "work" / "issue-1"
    assert rag_build.resolve_work_dir(tmp_path, "", "custom-work") == tmp_path / "custom-work"
    assert rag_build.resolve_work_dir(tmp_path, "", str(absolute)) == absolute

    assert rag_build.stage_record("stage", {"ok": True}) == {
        "name": "stage",
        "status": "completed",
        "result": {"ok": True},
    }

    assert rag_build.should_standardize(make_args(tmp_path))
    assert not rag_build.should_standardize(make_args(tmp_path, skip_standardize=True))
    assert rag_build.should_standardize(
        make_args(tmp_path, source_dir="docs", document_type="design-note", standardize_filenames=True)
    )
    assert not rag_build.should_standardize(
        make_args(tmp_path, source_dir="docs", document_type="design-note", standardize_filenames=False)
    )


def test_rag_build_artifact_defaults_and_human_check_reasons(tmp_path: Path) -> None:
    args = make_args(
        tmp_path,
        work_id="issue-7",
        clean_output=True,
        source_dir=str(tmp_path / "rag" / "corrective-action-report"),
        normalized_dir=str(tmp_path / "rag" / "normalized"),
        chunks_dir=str(tmp_path / "rag" / "chunks"),
        indexes_dir=str(tmp_path / "rag" / "indexes"),
        embeddings_output=str(tmp_path / "rag" / "embeddings" / "chunks-embeddings.jsonl"),
        duckdb_migrate=True,
    )
    stages = [
        rag_build.stage_record("normalize-documents", {"document_count": 2}),
        rag_build.stage_record("chunk-documents", {"chunk_count": 5}),
        rag_build.stage_record(
            "optimize-ingestion",
            {
                "candidate_chunk_count": 5,
                "accepted_chunk_count": 4,
                "rewritten_chunk_count": 1,
                "human_check_required_count": 1,
                "rejected_chunk_count": 0,
                "average_optimization_score": 0.86,
                "evidence_dir": "db/rag/evidence/ingestion",
                "ingestion_summary": "db/rag/evidence/ingestion/ingestion-summary.json",
            },
        ),
        rag_build.stage_record(
            "build-index",
            {
                "documents_index": "work/db/ariadne-knowledge-platform/rag/indexes/documents.jsonl",
                "chunks_index": "work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl",
                "chunk_count": 4,
            },
        ),
        rag_build.stage_record("embed-chunks", {"embedding_count": 5}),
        rag_build.stage_record(
            "duckdb-migrate",
            {
                "db": "db/rag/ariadne-knowledge.duckdb",
                "evidence_output": "db/rag/evidence/migration-summary.json",
                "registered_count": 4,
                "updated_count": 1,
                "skipped_count": 2,
                "failed_count": 0,
            },
        ),
    ]

    artifact = rag_build.build_run_artifact(tmp_path, args, stages)

    assert artifact["artifact_type"] == "rag-build-run"
    assert artifact["work_id"] == "issue-7"
    assert artifact["inputs"]["standardize_filenames"] is True
    assert artifact["inputs"]["clean_output"] is True
    assert artifact["outputs"]["document_count"] == 2
    assert artifact["outputs"]["raw_chunk_count"] == 5
    assert artifact["outputs"]["chunk_count"] == 4
    assert artifact["outputs"]["candidate_chunk_count"] == 5
    assert artifact["outputs"]["accepted_chunk_count"] == 4
    assert artifact["outputs"]["human_check_required_count"] == 1
    assert artifact["outputs"]["ingestion_summary"] == "db/rag/evidence/ingestion/ingestion-summary.json"
    assert artifact["outputs"]["embedding_count"] == 5
    assert artifact["outputs"]["duckdb_enabled"] is True
    assert artifact["outputs"]["duckdb_registered_count"] == 4
    assert artifact["outputs"]["duckdb_updated_count"] == 1
    assert artifact["outputs"]["duckdb_skipped_count"] == 2
    assert artifact["outputs"]["duckdb_failed_count"] == 0
    assert artifact["human_check_required"] is True
    assert "clean-output was used" in artifact["human_check_reasons"][0]
    assert "source report filenames" in artifact["human_check_reasons"][1]
    repair_command = artifact["gate_restart"]["repair_command"]
    assert "runtime/ctl/ctl.py --repo-root . rag build" in repair_command
    assert "runtime/rag/rag_build.py --repo-root" not in repair_command

    minimal = rag_build.build_run_artifact(
        tmp_path,
        make_args(tmp_path, source_dir="docs", document_type="design-note"),
        [rag_build.stage_record("normalize-documents", {})],
    )
    assert minimal["outputs"]["chunk_count"] == 0
    assert minimal["outputs"]["embedding_count"] == 0
    assert minimal["human_check_required"] is False


def test_register_rag_build_context_uses_work_dir_name(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    def fake_register_context(repo_root: Path, work_dir: Path, **kwargs: object) -> dict[str, object]:
        calls.append({"repo_root": repo_root, "work_dir": work_dir, **kwargs})
        return {"contexts": []}

    monkeypatch.setattr(rag_build, "register_context", fake_register_context)
    artifact = tmp_path / "rag" / "retrieval" / "rag-build-run-latest.json"

    rag_build.register_rag_build_context(tmp_path, make_args(tmp_path), artifact)
    assert calls == []

    rag_build.register_rag_build_context(
        tmp_path,
        make_args(tmp_path, work_id="", work_dir="work/custom-issue"),
        artifact,
    )

    assert len(calls) == 1
    assert calls[0]["work_dir"] == tmp_path / "work" / "custom-issue"
    assert calls[0]["work_id"] == "custom-issue"
    assert calls[0]["context_type"] == "rag-build-run"
    assert calls[0]["schema"] == ".ariadne/schemas/rag-build-run.schema.json"


def test_rag_build_run_with_standardize_and_context_registration(monkeypatch, tmp_path: Path) -> None:
    stage_calls: list[tuple[str, argparse.Namespace]] = []

    def record_stage(name: str, result: dict[str, object]):
        def inner(args: argparse.Namespace) -> dict[str, object]:
            stage_calls.append((name, args))
            return result

        return inner

    monkeypatch.setattr(
        rag_build.standardize_corrective_report_names,
        "run",
        record_stage("standardize", {"renamed_count": 1}),
    )
    monkeypatch.setattr(
        rag_build.normalize_documents,
        "run",
        record_stage("normalize", {"document_count": 3}),
    )
    monkeypatch.setattr(
        rag_build.chunk_documents,
        "run",
        record_stage("chunk", {"chunk_count": 9}),
    )
    monkeypatch.setattr(
        rag_build.ingestion_optimizer,
        "run",
        record_stage("optimize", {"candidate_chunk_count": 9, "accepted_chunk_count": 8}),
    )
    monkeypatch.setattr(
        rag_build.build_index,
        "run",
        record_stage(
            "index",
            {
                "documents_index": "work/db/ariadne-knowledge-platform/rag/indexes/documents.jsonl",
                "chunks_index": "work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl",
                "chunk_count": 8,
            },
        ),
    )
    monkeypatch.setattr(
        rag_build.embed_chunks,
        "run",
        record_stage("embed", {"embedding_count": 9}),
    )

    args = make_args(
        tmp_path,
        work_id="issue-22",
        clean_output=True,
        replace_references=True,
        random_length=7,
    )

    result = rag_build.run(args)

    assert result["status"] == "completed"
    assert result["document_count"] == 3
    assert result["chunk_count"] == 8
    assert result["embedding_count"] == 9
    assert result["stages"] == [
        "standardize-corrective-report-filenames",
        "normalize-documents",
        "chunk-documents",
        "optimize-ingestion",
        "build-index",
        "embed-chunks",
    ]
    assert [name for name, _ in stage_calls] == ["standardize", "normalize", "chunk", "optimize", "index", "embed"]
    assert stage_calls[0][1].replace_references is True
    assert stage_calls[0][1].random_length == 7
    assert stage_calls[1][1].clean_output is True
    assert stage_calls[2][1].chunk_size == 500
    assert stage_calls[3][1].output_dir == "work/db/ariadne-knowledge-platform/rag/optimized-chunks"
    assert stage_calls[4][1].chunks_dir == "work/db/ariadne-knowledge-platform/rag/optimized-chunks"
    assert stage_calls[5][1].chunks_index.endswith(str(Path("work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl")))
    assert stage_calls[5][1].dimensions == 64

    artifact_path = tmp_path / result["rag_build_run"]
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["human_check_required"] is True
    assert artifact["outputs"]["documents_index"] == "work/db/ariadne-knowledge-platform/rag/indexes/documents.jsonl"
    manifest = json.loads((tmp_path / "work" / "issue-22" / "context" / "context-manifest.json").read_text(encoding="utf-8"))
    assert manifest["contexts"][0]["type"] == "rag-build-run"


def test_rag_build_run_skip_standardize_and_explicit_work_dir(monkeypatch, tmp_path: Path) -> None:
    stage_names: list[str] = []

    def fake_standardize(args: argparse.Namespace) -> dict[str, object]:
        raise AssertionError("standardize should be skipped")

    monkeypatch.setattr(rag_build.standardize_corrective_report_names, "run", fake_standardize)
    monkeypatch.setattr(
        rag_build.normalize_documents,
        "run",
        lambda args: stage_names.append("normalize") or {"document_count": 1},
    )
    monkeypatch.setattr(
        rag_build.chunk_documents,
        "run",
        lambda args: stage_names.append("chunk") or {"chunk_count": 2},
    )
    monkeypatch.setattr(
        rag_build.ingestion_optimizer,
        "run",
        lambda args: stage_names.append("optimize") or {"candidate_chunk_count": 2, "accepted_chunk_count": 2},
    )
    monkeypatch.setattr(
        rag_build.build_index,
        "run",
        lambda args: stage_names.append("index") or {"documents_index": "", "chunks_index": ""},
    )
    monkeypatch.setattr(
        rag_build.embed_chunks,
        "run",
        lambda args: stage_names.append("embed") or {"embedding_count": 2},
    )

    work_dir = tmp_path / "external-work"
    args = make_args(
        tmp_path,
        work_id="",
        work_dir=str(work_dir),
        source_dir="docs",
        document_type="design-note",
        skip_standardize=True,
    )

    result = rag_build.run(args)

    assert result["stages"] == ["normalize-documents", "chunk-documents", "optimize-ingestion", "build-index", "embed-chunks"]
    assert stage_names == ["normalize", "chunk", "optimize", "index", "embed"]
    manifest = json.loads((work_dir / "context" / "context-manifest.json").read_text(encoding="utf-8"))
    assert manifest["work_id"] == "external-work"


def test_rag_build_run_can_skip_ingestion_optimization(monkeypatch, tmp_path: Path) -> None:
    stage_names: list[str] = []

    monkeypatch.setattr(
        rag_build.normalize_documents,
        "run",
        lambda args: stage_names.append("normalize") or {"document_count": 1},
    )
    monkeypatch.setattr(
        rag_build.chunk_documents,
        "run",
        lambda args: stage_names.append("chunk") or {"chunk_count": 2},
    )
    monkeypatch.setattr(
        rag_build.ingestion_optimizer,
        "run",
        lambda args: (_ for _ in ()).throw(AssertionError("optimization should be skipped")),
    )
    monkeypatch.setattr(
        rag_build.build_index,
        "run",
        lambda args: stage_names.append(f"index:{args.chunks_dir}") or {"documents_index": "", "chunks_index": "", "chunk_count": 2},
    )
    monkeypatch.setattr(
        rag_build.embed_chunks,
        "run",
        lambda args: stage_names.append("embed") or {"embedding_count": 2},
    )

    result = rag_build.run(
        make_args(
            tmp_path,
            source_dir="docs",
            document_type="design-note",
            skip_standardize=True,
            skip_optimization=True,
        )
    )

    assert result["stages"] == ["normalize-documents", "chunk-documents", "build-index", "embed-chunks"]
    assert stage_names == ["normalize", "chunk", "index:work/db/ariadne-knowledge-platform/rag/chunks", "embed"]
    artifact = json.loads((tmp_path / result["rag_build_run"]).read_text(encoding="utf-8"))
    assert artifact["outputs"]["chunk_count"] == 2
    assert artifact["outputs"]["accepted_chunk_count"] == 0


def test_rag_build_run_can_register_duckdb_migration_context(monkeypatch, tmp_path: Path) -> None:
    stage_names: list[str] = []
    migration_calls: list[dict[str, object]] = []

    monkeypatch.setattr(
        rag_build.normalize_documents,
        "run",
        lambda args: stage_names.append("normalize") or {"document_count": 1},
    )
    monkeypatch.setattr(
        rag_build.chunk_documents,
        "run",
        lambda args: stage_names.append("chunk") or {"chunk_count": 2},
    )
    monkeypatch.setattr(
        rag_build.ingestion_optimizer,
        "run",
        lambda args: stage_names.append("optimize") or {"candidate_chunk_count": 2, "accepted_chunk_count": 2},
    )
    monkeypatch.setattr(
        rag_build.build_index,
        "run",
        lambda args: stage_names.append(f"index:{args.chunks_dir}") or {"documents_index": "", "chunks_index": "", "chunk_count": 2},
    )
    monkeypatch.setattr(
        rag_build.embed_chunks,
        "run",
        lambda args: stage_names.append("embed") or {"embedding_count": 2},
    )

    def fake_migrate(repo_root: Path, db_path: Path, source: Path, policy: dict[str, object], error_log: Path) -> dict[str, object]:
        migration_calls.append(
            {
                "repo_root": repo_root,
                "db_path": db_path,
                "source": source,
                "policy": policy,
                "error_log": error_log,
            }
        )
        return {
            "status": "completed",
            "artifact_type": "rag-duckdb-migration-summary",
            "db": "db/rag/test.duckdb",
            "source": "work/db/ariadne-knowledge-platform/rag/optimized-chunks",
            "target_file_count": 2,
            "registered_count": 2,
            "updated_count": 0,
            "skipped_count": 0,
            "failed_count": 0,
            "error_log": "",
            "errors": [],
        }

    monkeypatch.setattr(rag_build.duckdb_store, "migrate_directory", fake_migrate)

    result = rag_build.run(
        make_args(
            tmp_path,
            work_id="issue-duckdb",
            source_dir="docs",
            document_type="design-note",
            skip_standardize=True,
            duckdb_migrate=True,
            duckdb_path="db/rag/test.duckdb",
        )
    )

    assert result["stages"] == ["normalize-documents", "chunk-documents", "optimize-ingestion", "build-index", "embed-chunks", "duckdb-migrate"]
    assert result["duckdb_enabled"] is True
    assert result["duckdb_migration_summary"] == "db/rag/evidence/migration-summary.json"
    assert migration_calls[0]["db_path"] == tmp_path / "db" / "rag" / "test.duckdb"
    assert migration_calls[0]["source"] == (
        tmp_path / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "optimized-chunks"
    )
    evidence = json.loads((tmp_path / "db" / "rag" / "evidence" / "migration-summary.json").read_text(encoding="utf-8"))
    assert evidence["artifact_type"] == "rag-duckdb-migration"
    assert evidence["migration"]["registered_count"] == 2
    artifact = json.loads((tmp_path / result["rag_build_run"]).read_text(encoding="utf-8"))
    assert artifact["outputs"]["duckdb_registered_count"] == 2
    manifest = json.loads((tmp_path / "work" / "issue-duckdb" / "context" / "context-manifest.json").read_text(encoding="utf-8"))
    context_types = {item["type"] for item in manifest["contexts"]}
    assert {"rag-build-run", "rag-duckdb-migration"} <= context_types


def test_rag_build_parser_and_main_paths(monkeypatch, tmp_path: Path, capsys) -> None:
    parser = rag_build.build_parser()
    args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "--work-id",
            "issue-1",
            "--source-dir",
            "docs",
            "--document-type",
            "design-note",
            "--standardize-filenames",
            "--replace-references",
            "--random-length",
            "5",
            "--duckdb-migrate",
            "--duckdb-path",
            "db/rag/test.duckdb",
        ]
    )
    assert args.work_id == "issue-1"
    assert args.standardize_filenames is True
    assert args.replace_references is True
    assert args.random_length == 5
    assert args.duckdb_migrate is True
    assert args.duckdb_path == "db/rag/test.duckdb"

    monkeypatch.setattr(
        rag_build,
        "run",
        lambda args: {"status": "completed", "rag_build_run": "work/db/ariadne-knowledge-platform/rag/retrieval/run.json"},
    )
    assert rag_build.main(["--repo-root", str(tmp_path)]) == 0
    assert '"status": "completed"' in capsys.readouterr().out

    monkeypatch.setattr(rag_build, "run", lambda args: {"status": "failed"})
    assert rag_build.main(["--repo-root", str(tmp_path)]) == 1
    assert '"status": "failed"' in capsys.readouterr().out

    def fail(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(rag_build, "run", fail)
    assert rag_build.main(["--repo-root", str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "ERROR: boom" in captured.err

    namespace = runpy.run_path(str(Path(rag_build.__file__)))
    assert namespace["build_parser"]
