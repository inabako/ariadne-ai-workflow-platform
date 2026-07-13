from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.rag import duckdb_store


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    return repo


def write_record(repo: Path, relative: str, content: str, **overrides: object) -> Path:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "knowledge_id": "knowledge-1",
        "title": "DuckDB read model",
        "content": content,
        "source_path": "rag/source/report.md",
        "document_type": "runtime-knowledge",
        "metadata": {
            "status": "approved",
            "trust_level": "high",
            "tags": ["rag", "duckdb"],
            "repository": "inabako/ariadne-ai-workflow-platform",
            "commit": "abc123",
        },
    }
    payload.update(overrides)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def load_policy(repo: Path) -> dict[str, object]:
    return duckdb_store.ingestion_optimizer.load_policy(
        repo, "runtime/rag/policies/knowledge-ingestion-policy.json"
    )


def test_duckdb_store_init_creates_generated_schema(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "ariadne-knowledge.duckdb"

    result = duckdb_store.init_schema(db)

    assert result["status"] == "completed"
    assert db.exists()
    with duckdb_store.connect(db) as conn:
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
    assert {"knowledge_documents", "knowledge_tags", "knowledge_scores"} <= tables


def test_duckdb_store_ingests_skips_duplicate_and_updates_same_id(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "test.duckdb"
    policy = load_policy(repo)
    first = write_record(
        repo,
        "rag/optimized-chunks/knowledge-1.json",
        "DuckDB is a generated read model. File-based RAG artifacts remain the source of truth.",
    )
    record = duckdb_store.normalize_record(repo, first, json.loads(first.read_text(encoding="utf-8")))

    registered = duckdb_store.register_record(db, record, policy)
    skipped = duckdb_store.register_record(db, record, policy)
    updated_path = write_record(
        repo,
        "rag/optimized-chunks/knowledge-1-updated.json",
        "DuckDB is regenerated from JSON artifacts and now contains updated runtime knowledge.",
    )
    updated_record = duckdb_store.normalize_record(
        repo, updated_path, json.loads(updated_path.read_text(encoding="utf-8"))
    )
    updated = duckdb_store.register_record(db, updated_record, policy)

    assert registered["action"] == "registered"
    assert skipped["action"] == "skipped"
    assert updated["action"] == "updated"
    with duckdb_store.connect(db) as conn:
        row_count = conn.execute("SELECT count(*) FROM knowledge_documents").fetchone()[0]
        content = conn.execute(
            "SELECT content FROM knowledge_documents WHERE knowledge_id = ?",
            ["knowledge-1"],
        ).fetchone()[0]
        tags = {row[0] for row in conn.execute("SELECT tag FROM knowledge_tags").fetchall()}
        score = conn.execute(
            "SELECT optimization_decision FROM knowledge_scores WHERE knowledge_id = ?",
            ["knowledge-1"],
        ).fetchone()[0]
    assert row_count == 1
    assert "updated runtime knowledge" in content
    assert {"rag", "duckdb"} <= tags
    assert score in duckdb_store.ingestion_optimizer.DECISIONS


def test_duckdb_store_skips_same_content_with_different_id(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "test.duckdb"
    policy = load_policy(repo)
    content = "A generated DuckDB index must not duplicate identical RAG content."
    first = write_record(repo, "rag/chunks/one.json", content, knowledge_id="knowledge-1")
    second = write_record(repo, "rag/chunks/two.json", content, knowledge_id="knowledge-2")

    first_result = duckdb_store.ingest_file(repo, db, first, policy)
    second_result = duckdb_store.ingest_file(repo, db, second, policy)

    assert first_result["action"] == "registered"
    assert second_result["action"] == "skipped"
    with duckdb_store.connect(db) as conn:
        assert conn.execute("SELECT count(*) FROM knowledge_documents").fetchone()[0] == 1


def test_duckdb_store_migrate_continues_after_invalid_records(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    source = repo / "rag" / "optimized-chunks"
    write_record(
        repo,
        "rag/optimized-chunks/valid.json",
        "A valid RAG JSON record should be registered into the generated DuckDB read model.",
    )
    (source / "missing-content.json").write_text(
        json.dumps({"knowledge_id": "missing-content"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (source / "invalid.json").write_text("{", encoding="utf-8")
    db = repo / "rag" / "duckdb" / "test.duckdb"
    error_log = repo / "rag" / "duckdb" / "migration-errors.jsonl"

    result = duckdb_store.migrate_directory(repo, db, source, load_policy(repo), error_log)

    assert result["status"] == "completed_with_errors"
    assert result["target_file_count"] == 3
    assert result["registered_count"] == 1
    assert result["failed_count"] == 2
    errors = error_log.read_text(encoding="utf-8")
    assert "missing-content.json" in errors
    assert "invalid.json" in errors


def test_duckdb_store_cli_and_fallback_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    record = write_record(
        repo,
        "rag/optimized-chunks/knowledge-1.json",
        "CLI ingest registers generated DuckDB read model rows from JSON RAG artifacts.",
    )
    db = repo / "rag" / "duckdb" / "cli.duckdb"

    assert duckdb_store.main(["--repo-root", str(repo), "--db", str(db), "init"]) == 0
    assert '"rag-duckdb-schema"' in capsys.readouterr().out
    assert (
        duckdb_store.main(["--repo-root", str(repo), "--db", str(db), "ingest", "--file", str(record)])
        == 0
    )
    assert '"knowledge_id": "knowledge-1"' in capsys.readouterr().out

    parser = duckdb_store.build_parser()
    args = parser.parse_args(["--repo-root", str(repo), "migrate", "--source", "rag/optimized-chunks"])
    assert isinstance(args, argparse.Namespace)
    assert duckdb_store.resolve_repo_path(repo, "rag/duckdb/x.duckdb") == repo / "rag" / "duckdb" / "x.duckdb"
    assert duckdb_store.source_kind_from_path(repo / "rag" / "jsonized" / "a.json") == "jsonized-artifact"
    assert duckdb_store.deterministic_id("a.json", "content") == duckdb_store.deterministic_id(
        "a.json", "content"
    )

    def fail(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(duckdb_store, "run", fail)
    assert duckdb_store.main(["--repo-root", str(repo), "init"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(duckdb_store.__file__)))
    assert namespace["build_parser"]


def test_duckdb_store_requires_content_and_source_directory(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    bad = repo / "rag" / "normalized" / "bad.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text(json.dumps({"knowledge_id": "bad"}, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="requires non-empty content"):
        duckdb_store.normalize_record(repo, bad, json.loads(bad.read_text(encoding="utf-8")))
    with pytest.raises(FileNotFoundError, match="RAG source directory not found"):
        duckdb_store.discover_json_files(repo / "missing")


def test_duckdb_store_helper_fallbacks_and_generated_ids(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    path = repo / "rag" / "normalized" / "auto.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "body": "A normalized document can omit IDs because DuckDB is only a generated read model.",
        "content_hash": "known-hash",
        "tags": "single-tag",
        "metadata": {"keywords": ["generated", "duckdb"], "status": "draft"},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    record = duckdb_store.normalize_record(repo, path, payload)

    assert duckdb_store.metadata_from_payload({"metadata": []}) == {}
    assert duckdb_store.first_text(None, 42) == "42"
    assert duckdb_store.first_text("", "fallback") == "fallback"
    assert duckdb_store.list_text(" x ") == ["x"]
    assert duckdb_store.list_text(["a", "", "b"]) == ["a", "b"]
    assert duckdb_store.list_text({"a": "b"}) == []
    assert duckdb_store.source_kind_from_path(path) == "normalized-document"
    assert duckdb_store.source_kind_from_path(repo / "rag" / "other" / "a.json") == "knowledge-json"
    assert record.knowledge_id == duckdb_store.deterministic_id("rag/normalized/auto.json", record.content)
    assert record.content_hash == "known-hash"
    assert {"single-tag", "generated", "duckdb"} <= set(record.tags)


def test_duckdb_store_run_migrate_and_empty_error_log(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_record(
        repo,
        "rag/optimized-chunks/run.json",
        "Run migrate projects file-based RAG JSON into a generated DuckDB read model.",
    )
    args = argparse.Namespace(
        repo_root=str(repo),
        db="rag/duckdb/run.duckdb",
        command="migrate",
        source="rag/optimized-chunks",
        policy="runtime/rag/policies/knowledge-ingestion-policy.json",
        error_log="rag/duckdb/migration-errors.jsonl",
    )

    result = duckdb_store.run(args)

    assert result["status"] == "completed"
    assert result["registered_count"] == 1
    assert result["error_log"] == ""
    assert not (repo / "rag" / "duckdb" / "migration-errors.jsonl").exists()


def test_duckdb_store_defensive_error_paths(tmp_path: Path, monkeypatch) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "test.duckdb"
    source = repo / "rag" / "optimized-chunks"
    source.mkdir(parents=True)
    list_payload = source / "list.json"
    list_payload.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="must be a JSON object"):
        duckdb_store.ingest_file(repo, db, list_payload, load_policy(repo))

    def unknown_action(repo_root: Path, db_path: Path, file_path: Path, policy: dict[str, object]) -> dict[str, object]:
        return {"action": "mystery"}

    monkeypatch.setattr(duckdb_store, "ingest_file", unknown_action)
    result = duckdb_store.migrate_directory(repo, db, source, load_policy(repo), repo / "rag" / "duckdb" / "e.jsonl")
    assert result["failed_count"] == 1

    unsupported = argparse.Namespace(
        repo_root=str(repo),
        db=str(db),
        command="unknown",
        policy="runtime/rag/policies/knowledge-ingestion-policy.json",
    )
    with pytest.raises(ValueError, match="Unsupported command"):
        duckdb_store.run(unsupported)


def test_duckdb_store_search_ranks_keyword_and_metadata_filters(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "search.duckdb"
    policy = load_policy(repo)
    gui = write_record(
        repo,
        "rag/optimized-chunks/gui.json",
        "PyQt GUI smoke test uses QTest and validates window startup behavior.",
        knowledge_id="gui",
        semantic_hint="pyqt gui smoke-test",
        category="test",
        document_type="gui-knowledge",
        environment="windows-msys2-gui",
        workflow="/ariadne-feature-maintenance",
        metadata={"status": "approved", "trust_level": "high", "tags": ["gui", "pyqt"], "repository": "repo"},
    )
    web = write_record(
        repo,
        "rag/optimized-chunks/web.json",
        "React SVG layout test uses Playwright and browser rendering checks.",
        knowledge_id="web",
        semantic_hint="react svg layout",
        category="test",
        document_type="web-knowledge",
        environment="wsl-ubuntu-web",
        workflow="/ariadne-feature-maintenance",
        metadata={"status": "approved", "trust_level": "medium", "tags": ["web", "svg"], "repository": "repo"},
    )
    duckdb_store.ingest_file(repo, db, gui, policy)
    duckdb_store.ingest_file(repo, db, web, policy)

    result = duckdb_store.search_knowledge(
        db,
        duckdb_store.SearchFilters(
            query="PyQt GUI",
            semantic_hint="smoke-test",
            category="test",
            tags=["pyqt"],
            source="",
            document_type="gui-knowledge",
            environment="windows-msys2-gui",
            workflow="/ariadne-feature-maintenance",
            min_reliability=0.5,
            min_freshness=0.5,
            limit=5,
        ),
    )

    assert result["status"] == "completed"
    assert result["candidate_count"] == 1
    assert result["result_count"] == 1
    assert result["results"][0]["knowledge_id"] == "gui"
    assert result["results"][0]["keyword_match_score"] > 0
    assert result["results"][0]["semantic_hint_score"] > 0
    assert "pyqt" in result["results"][0]["tags"]


def test_duckdb_store_search_returns_zero_results_without_error(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "search.duckdb"
    policy = load_policy(repo)
    record = write_record(
        repo,
        "rag/optimized-chunks/one.json",
        "Runtime knowledge about DuckDB generated read model registration.",
    )
    duckdb_store.ingest_file(repo, db, record, policy)

    result = duckdb_store.search_knowledge(
        db,
        duckdb_store.SearchFilters(
            query="nonexistent-token",
            semantic_hint="",
            category="",
            tags=[],
            source="",
            document_type="",
            environment="",
            workflow="",
            min_reliability=None,
            min_freshness=None,
            limit=10,
        ),
    )

    assert result["status"] == "completed"
    assert result["candidate_count"] == 0
    assert result["result_count"] == 0
    assert result["results"] == []


def test_duckdb_store_export_context_writes_agent_json(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "context.duckdb"
    record = write_record(
        repo,
        "rag/optimized-chunks/context.json",
        "Context export should trim long content before passing knowledge to an Agent.",
        knowledge_id="context",
        semantic_hint="agent context export",
        metadata={"status": "approved", "trust_level": "high", "tags": ["context"]},
    )
    duckdb_store.ingest_file(repo, db, record, load_policy(repo))
    output = repo / "work" / "issue-1" / "context" / "knowledge.json"

    result = duckdb_store.export_context(
        repo,
        db,
        duckdb_store.SearchFilters(
            query="Context export",
            semantic_hint="agent",
            category="",
            tags=["context"],
            source="",
            document_type="",
            environment="",
            workflow="",
            min_reliability=None,
            min_freshness=None,
            limit=3,
        ),
        output,
        max_chars=20,
    )

    assert result["status"] == "completed"
    assert result["output"] == "work/issue-1/context/knowledge.json"
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "rag-duckdb-context"
    assert data["result_count"] == 1
    assert len(data["results"][0]["content"]) == 20
    assert data["results"][0]["score"] > 0


def test_duckdb_store_cli_search_and_export_context(tmp_path: Path, capsys) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "cli-search.duckdb"
    record = write_record(
        repo,
        "rag/optimized-chunks/cli-search.json",
        "CLI search finds DuckDB knowledge and exports context JSON.",
        knowledge_id="cli-search",
        semantic_hint="duckdb cli search",
        metadata={"status": "approved", "trust_level": "high", "tags": ["cli"]},
    )
    duckdb_store.ingest_file(repo, db, record, load_policy(repo))
    output = repo / "work" / "knowledge.json"

    assert (
        duckdb_store.main(
            [
                "--repo-root",
                str(repo),
                "--db",
                str(db),
                "search",
                "--query",
                "DuckDB knowledge",
                "--tag",
                "cli",
            ]
        )
        == 0
    )
    assert '"artifact_type": "rag-duckdb-search-result"' in capsys.readouterr().out
    assert (
        duckdb_store.main(
            [
                "--repo-root",
                str(repo),
                "--db",
                str(db),
                "export-context",
                "--query",
                "DuckDB knowledge",
                "--tag",
                "cli",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert '"artifact_type": "rag-duckdb-context-export"' in capsys.readouterr().out
    assert output.exists()


def test_duckdb_store_rebuild_standard_sources_records_history(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "standard.duckdb"
    error_log = repo / "rag" / "duckdb" / "standard-errors.jsonl"
    source_repo = repo / "work" / "db" / "ariadne-knowledge-platform"
    (source_repo / ".git").mkdir(parents=True)
    write_record(
        repo,
        "work/db/ariadne-knowledge-platform/rag/chunks/runtime.json",
        "Runtime workflow knowledge is loaded into DuckDB during a standard rebuild.",
        knowledge_id="runtime-knowledge",
        metadata={"status": "approved", "trust_level": "high", "tags": ["runtime"]},
    )
    write_record(
        repo,
        "work/db/ariadne-knowledge-platform/rag/jsonized/duckdb.json",
        "DuckDB reference checks confirm that migrated knowledge can be searched.",
        knowledge_id="duckdb-knowledge",
        metadata={"status": "approved", "trust_level": "medium", "tags": ["duckdb"]},
    )

    source_metadata = {
        "url": duckdb_store.DEFAULT_SOURCE_REPO_URL,
        "path": "work/db/ariadne-knowledge-platform",
        "exists": True,
        "is_git_repo": True,
        "branch": "main",
        "commit": "abc123",
        "dirty": False,
        "status": "clean",
    }
    result = duckdb_store.rebuild_standard_sources(
        repo,
        db,
        duckdb_store.source_repo_standard_sources(repo, source_repo),
        load_policy(repo),
        error_log,
        reset=True,
        source_repository=source_metadata,
    )

    assert result["artifact_type"] == "rag-duckdb-rebuild-summary"
    assert result["reset_performed"] is False
    assert result["target_file_count"] == 2
    assert result["registered_count"] == 2
    assert result["failed_count"] == 0
    assert set(result["sources"]) == {
        "work/db/ariadne-knowledge-platform/rag/chunks",
        "work/db/ariadne-knowledge-platform/rag/jsonized",
    }
    assert result["source_repository"]["commit"] == "abc123"
    with duckdb_store.connect(db) as conn:
        schema_version = conn.execute(
            "SELECT value FROM rag_store_metadata WHERE key = 'schema_version'"
        ).fetchone()[0]
        history = conn.execute("SELECT status, registered_count FROM rag_migration_runs").fetchone()
    assert schema_version == duckdb_store.SCHEMA_VERSION
    assert history == ("completed", 2)


def test_duckdb_store_verify_references_writes_evidence(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    db = repo / "rag" / "duckdb" / "verify.duckdb"
    record = write_record(
        repo,
        "rag/optimized-chunks/reference.json",
        "Reference verification searches DuckDB and writes human readable evidence.",
        knowledge_id="reference-knowledge",
        semantic_hint="reference check",
        metadata={"status": "approved", "trust_level": "high", "tags": ["reference"]},
    )
    duckdb_store.ingest_file(repo, db, record, load_policy(repo))
    output = repo / "rag" / "evidence" / "duckdb" / "reference-check.json"

    result = duckdb_store.verify_references(
        repo,
        db,
        ["Reference verification", "missing-token"],
        output,
        min_results=1,
        limit=3,
        work_dir=repo / "work" / "issue-duckdb",
        work_id="issue-duckdb",
        source_repository={"path": "work/db/ariadne-knowledge-platform", "commit": "abc123"},
    )

    assert result["artifact_type"] == "rag-duckdb-reference-check"
    assert result["status"] == "human-check-required"
    assert result["passed_count"] == 1
    assert result["failed_count"] == 1
    assert result["context_manifest"] == "work/issue-duckdb/context/context-manifest.json"
    assert output.exists()
    evidence = json.loads(output.read_text(encoding="utf-8"))
    manifest = json.loads(
        (repo / "work" / "issue-duckdb" / "context" / "context-manifest.json").read_text(encoding="utf-8")
    )
    assert evidence["checks"][0]["top_results"][0]["knowledge_id"] == "reference-knowledge"
    assert evidence["checks"][1]["status"] == "failed"
    assert evidence["context_manifest"] == "work/issue-duckdb/context/context-manifest.json"
    assert evidence["source_repository"]["commit"] == "abc123"
    entry = manifest["contexts"][0]
    assert entry["type"] == "rag-duckdb-reference-check"
    assert entry["status"] == "human-check-required"
    assert entry["schema"] == ".github/schemas/rag-duckdb-reference-check.schema.json"

    default_result = duckdb_store.run(
        argparse.Namespace(
            repo_root=str(repo),
            db=str(db),
            command="verify",
            query=["Reference verification"],
            output="rag/evidence/duckdb/default-reference-check.json",
            min_results=1,
            limit=3,
            work_id="",
            work_dir="",
            source_repo="",
        )
    )

    assert default_result["context_manifest"] == "rag/evidence/duckdb/context/context-manifest.json"
    default_manifest = json.loads(
        (repo / "rag" / "evidence" / "duckdb" / "context" / "context-manifest.json").read_text(encoding="utf-8")
    )
    assert default_manifest["work_id"] == "duckdb-reference-check"
