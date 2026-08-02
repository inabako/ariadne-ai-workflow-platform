from __future__ import annotations

import argparse
import json
import runpy
import subprocess
from pathlib import Path

import pytest

from runtime.rag import rag_dispatcher


def write_tiny_indexes(tmp_path: Path) -> tuple[Path, Path]:
    chunks = tmp_path / "chunks.jsonl"
    embeddings = tmp_path / "chunks-embeddings.jsonl"
    row = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "source_path": "rag/normalized/doc-1.json",
        "chunk_path": "rag/chunks/chunk-1.json",
        "chunk_index": 0,
        "title": "Workflow doctor and human gate registry",
        "repository": "test-repo",
        "branch": "main",
        "project": "",
        "tags": ["workflow"],
        "heading_path": ["Workflow"],
        "metadata": {},
        "content": "workflow doctor human gate registry close archive pytest regression safety STOP communication loss",
    }
    chunks.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    embeddings.write_text("", encoding="utf-8")
    return chunks, embeddings


def make_args(**overrides) -> argparse.Namespace:
    defaults = {
        "query": [],
        "task": "",
        "workflow": "",
        "work_id": "",
        "context_file": [],
        "work_dir": "",
        "dispatch_plan": "",
        "repository": "",
        "branch": "",
        "project": "",
        "tag": [],
        "source_type": "",
        "category": "",
        "trust_level": "",
        "chunks_index": "rag/indexes/chunks.jsonl",
        "embeddings_index": "rag/embeddings/chunks-embeddings.jsonl",
        "retrieval_backend": "file",
        "duckdb_path": "db/rag/ariadne-knowledge.duckdb",
        "semantic_hint": "",
        "document_type": "",
        "environment": "",
        "knowledge_workflow": "",
        "min_reliability": None,
        "min_freshness": None,
        "output_dir": "rag/retrieval",
        "search_mode": "hybrid",
        "top_k": 5,
        "max_chars": 4000,
        "max_queries": 5,
        "jobs": 4,
        "aggregate_max_chars": 12000,
        "build_if_missing": False,
        "write_markdown": False,
        "repo_root": "",
        "python": "python",
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_dispatcher_planning_helpers_cover_context_and_explicit_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    work_dir = repo / "work" / "issue-1"
    (work_dir / "design-document").mkdir(parents=True)
    (work_dir / "process-report").mkdir()
    (work_dir / "context").mkdir()
    (work_dir / "design-document" / "design.md").write_text(
        "MainWindow TelemetryService watchdog STOP rollback pytest README docs\n",
        encoding="utf-8",
    )
    (work_dir / "process-report" / "report.md").write_text("video-control telemetry_receiver.py\n", encoding="utf-8")
    (work_dir / "context" / "state.json").write_text('{"component":"ControlSession"}\n', encoding="utf-8")
    context_file = repo / "context.md"
    context_file.write_text("DiscoveryService communication loss CI documentation\n", encoding="utf-8")

    args = make_args(
        task="startup shutdown operator observability",
        context_file=["context.md"],
        work_dir=str(work_dir),
        repository="target-system",
        branch="main",
        project="ariadne",
        tag=["robot", "safety"],
        source_type="internal-work",
        category="corrective-action",
        trust_level="verified",
        max_queries=10,
    )

    assert rag_dispatcher.resolve_path(repo, "context.md") == context_file.resolve()
    assert rag_dispatcher.resolve_path(repo, str(context_file.resolve())) == context_file.resolve()
    assert rag_dispatcher.read_text_file(repo / "missing.md") == ""
    collected = rag_dispatcher.collect_work_context(work_dir)
    assert "# design.md" in collected
    assert "# report.md" in collected
    assert "# state.json" in collected
    (work_dir / "process-report" / "empty.md").write_text("", encoding="utf-8")
    assert "# empty.md" not in rag_dispatcher.collect_work_context(work_dir)
    assert rag_dispatcher.collect_work_context(repo / "missing") == ""
    assert rag_dispatcher.default_work_dir(repo, make_args(work_id="issue-2")) == repo / "work" / "issue-2"
    assert rag_dispatcher.default_work_dir(repo, make_args()) is None
    assert rag_dispatcher.unique_keep_order([" A  B ", "a b", "", "C"]) == ["A B", "C"]

    terms = rag_dispatcher.extract_component_terms(
        "MainWindow TelemetryService telemetry_receiver.py video-control watchdog_service DiscoveryService"
    )
    assert "MainWindow" in terms
    assert "TelemetryService" in terms
    assert "telemetry_receiver.py" in terms
    planning_context = rag_dispatcher.collect_planning_context(args, repo)
    assert "DiscoveryService" in planning_context
    assert "MainWindow" in planning_context
    assert "startup shutdown operator observability" in planning_context
    assert rag_dispatcher.base_filters_from_args(args) == {
        "project": "ariadne",
        "repository": "target-system",
        "branch": "main",
        "tags": ["robot", "safety"],
        "source_type": "internal-work",
        "category": "corrective-action",
        "trust_level": "verified",
    }

    query_items, semantic_hints = rag_dispatcher.derive_query_items(args, repo)
    queries = [item["query"] for item in query_items]
    assert queries[0] == "target-system main corrective action report"
    assert any("architecture responsibility boundary" in query for query in queries)
    assert any("safety risk corrective action" in query for query in queries)
    assert any("documentation gap operations README corrective action" == query for query in queries)
    assert "TelemetryService" in semantic_hints
    assert "STOP" in semantic_hints
    assert query_items[0]["filters"]["repository"] == "target-system"

    explicit_args = make_args(query=[" duplicate query ", "DUPLICATE QUERY", "other"], max_queries=2)
    explicit_items, explicit_hints = rag_dispatcher.derive_query_items(explicit_args, repo)
    assert [item["query"] for item in explicit_items] == ["duplicate query", "other"]
    assert explicit_hints == ["duplicate query", "other"]

    deduped = rag_dispatcher.dedupe_query_items(
        [{"query": "  A  B "}, {"query": "a b"}, {"query": ""}, {"query": "C"}]
    )
    assert [item["query"] for item in deduped] == ["A B", "C"]
    query_items_for_append: list[dict] = []
    rag_dispatcher.append_query(query_items_for_append, "   ", "skip", args)
    assert query_items_for_append == []

    no_optional_context = rag_dispatcher.collect_planning_context(make_args(task="", context_file=[], work_dir=""), repo)
    assert no_optional_context == ""


def test_dispatcher_duckdb_backend_command_and_index_gate(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    args = make_args(
        retrieval_backend="duckdb",
        duckdb_path="db/rag/knowledge.duckdb",
        semantic_hint="dispatcher context",
        document_type="rag-knowledge",
        environment="windows",
        knowledge_workflow="/rag-build",
        min_reliability=0.6,
        min_freshness=0.5,
        tag=["duckdb"],
        category="runtime",
        python="python",
    )
    query_item = {
        "query": "DuckDB dispatcher",
        "purpose": "duckdb retrieval",
        "search_mode": "keyword",
        "filters": {
            "tags": ["duckdb"],
            "category": "runtime",
            "semantic_hint": "dispatcher context",
            "document_type": "rag-knowledge",
            "environment": "windows",
            "workflow": "/rag-build",
            "min_reliability": 0.6,
            "min_freshness": 0.5,
        },
    }

    rag_dispatcher.ensure_indexes(args, repo)
    command = rag_dispatcher.retrieval_command(args, query_item)

    assert "--backend" in command
    assert command[command.index("--backend") + 1] == "duckdb"
    assert command[command.index("--duckdb-path") + 1] == "db/rag/knowledge.duckdb"
    assert "--semantic-hint" in command
    assert "--document-type" in command
    assert "--environment" in command
    assert "--workflow" in command
    assert "--min-reliability" in command
    assert "--min-freshness" in command


def test_dispatcher_execution_plan_and_plan_normalization_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    work_dir = repo / "work" / "issue-2"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)

    no_work_args = make_args()
    assert rag_dispatcher.execution_plan_reference(repo, None) == ""
    assert rag_dispatcher.execution_plan_gate(repo, no_work_args, None)["status"] == "not-required"

    fallback_plan = context_dir / "execution-plan.json"
    fallback_plan.write_text("{}\n", encoding="utf-8")
    args = make_args(work_id="issue-2", work_dir=str(work_dir))
    assert rag_dispatcher.execution_plan_reference(repo, work_dir) == "work/issue-2/context/execution-plan.json"
    assert rag_dispatcher.execution_plan_gate(repo, args, work_dir)["status"] == "ready"

    fallback_plan.unlink()
    gate = rag_dispatcher.execution_plan_gate(repo, args, work_dir)
    assert gate["status"] == "human-check-required"
    assert gate["human_check_required"] is True

    manifest = {
        "schema_version": "1.0",
        "contexts": [
            {
                "type": "execution-plan",
                "path": "work/issue-2/context/registered-plan.json",
            }
        ],
    }
    (context_dir / "context-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (context_dir / "registered-plan.json").write_text("{}\n", encoding="utf-8")
    assert rag_dispatcher.execution_plan_reference(repo, work_dir) == "work/issue-2/context/registered-plan.json"
    manifest["contexts"] = [{"type": "other", "path": "work/issue-2/context/other.json"}]
    (context_dir / "context-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    fallback_plan.write_text("{}\n", encoding="utf-8")
    assert rag_dispatcher.execution_plan_reference(repo, work_dir) == "work/issue-2/context/execution-plan.json"

    plan_args = make_args(max_queries=3, search_mode="semantic")
    plan = {
        "metadata": {
            "project": "ariadne",
            "repository": "repo",
            "branch": "main",
            "tags": ["base"],
            "source_type": "internal",
            "category": "ops",
            "trust_level": "verified",
        },
        "search_mode": "keyword",
        "queries": [
            "legacy query",
            123,
            {
                "query": "dict query",
                "purpose": "purpose",
                "filters": {"branch": "feature", "tags": ["override"], "category": ""},
            },
            {"query": "legacy query"},
        ],
    }
    normalized = rag_dispatcher.normalize_plan_query_items(plan, plan_args)

    assert [item["query"] for item in normalized] == ["legacy query", "dict query"]
    assert normalized[0]["purpose"] == "legacy string query from dispatch plan"
    assert normalized[0]["search_mode"] == "semantic"
    assert normalized[1]["search_mode"] == "keyword"
    assert normalized[1]["filters"]["branch"] == "feature"
    assert normalized[1]["filters"]["tags"] == ["override"]
    assert normalized[1]["filters"]["category"] == "ops"


def test_dispatcher_existing_plan_validation_and_execution_plan_override(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    invalid_json = repo / "invalid.json"
    invalid_json.write_text("[]", encoding="utf-8")
    wrong_type = repo / "wrong.json"
    wrong_type.write_text(json.dumps({"artifact_type": "other"}), encoding="utf-8")
    valid = repo / "plan.json"
    valid.write_text(
        json.dumps(
            {
                "artifact_type": "rag-dispatch-plan",
                "execution_plan": "work/issue-3/context/from-plan.json",
                "queries": ["q"],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid dispatch plan"):
        rag_dispatcher.build_dispatch_plan(make_args(dispatch_plan=str(invalid_json)), repo)
    with pytest.raises(ValueError, match="artifact_type must be rag-dispatch-plan"):
        rag_dispatcher.build_dispatch_plan(make_args(dispatch_plan=str(wrong_type)), repo)

    plan = rag_dispatcher.build_dispatch_plan(
        make_args(dispatch_plan=str(valid), work_id="issue-3", work_dir=str(repo / "work" / "issue-3")),
        repo,
    )

    assert plan["schema_version"] == "1.0"
    assert plan["plan_id"]
    assert plan["execution_plan_gate"]["status"] == "ready"
    assert plan["execution_plan"] == "work/issue-3/context/from-plan.json"
    assert plan["human_check_required"] is False

    plan_without_gate = repo / "plan-without-gate.json"
    plan_without_gate.write_text(
        json.dumps(
            {
                "artifact_type": "rag-dispatch-plan",
                "execution_plan": "work/issue-3/context/from-plan.json",
                "queries": ["q"],
            }
        ),
        encoding="utf-8",
    )
    inferred = rag_dispatcher.build_dispatch_plan(make_args(dispatch_plan=str(plan_without_gate), work_id="issue-3"), repo)
    assert inferred["execution_plan_gate"]["execution_plan"] == "work/issue-3/context/from-plan.json"

    work_context = repo / "work" / "issue-3" / "context"
    work_context.mkdir(parents=True)
    (work_context / "execution-plan.json").write_text("{}\n", encoding="utf-8")
    plan_with_existing_gate_path = repo / "plan-with-existing-gate-path.json"
    plan_with_existing_gate_path.write_text(
        json.dumps(
            {
                "artifact_type": "rag-dispatch-plan",
                "execution_plan": "work/issue-3/context/from-plan.json",
                "queries": ["q"],
            }
        ),
        encoding="utf-8",
    )
    gated = rag_dispatcher.build_dispatch_plan(
        make_args(dispatch_plan=str(plan_with_existing_gate_path), work_id="issue-3", work_dir=str(repo / "work" / "issue-3")),
        repo,
    )
    assert gated["execution_plan_gate"]["execution_plan"] == "work/issue-3/context/execution-plan.json"

    namespace = runpy.run_path(str(Path(rag_dispatcher.__file__)))
    assert namespace["build_parser"]


def test_dispatcher_command_index_build_and_aggregation_helpers(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    args = make_args(
        python="py",
        chunks_index="rag/indexes/chunks.jsonl",
        embeddings_index="rag/embeddings/chunks-embeddings.jsonl",
        output_dir="rag/retrieval",
        project="proj",
        repository="repo",
        branch="main",
        tag=["base"],
        source_type="internal_work",
        category="ops",
        trust_level="trusted",
        write_markdown=True,
        top_k=3,
        max_chars=123,
    )
    query_item = {
        "query": "safety query",
        "search_mode": "keyword",
        "filters": {
            "project": "override-project",
            "repository": "override-repo",
            "branch": "feature",
            "tags": "urgent",
            "source_type": "external-web",
            "category": "docs",
            "trust_level": "official",
        },
    }

    command = rag_dispatcher.retrieval_command(args, query_item)

    assert command[:7] == ["py", "runtime/ctl/ctl.py", "--repo-root", ".", "rag", "retrieve", "safety query"]
    assert ["--project", "override-project"] == command[command.index("--project") : command.index("--project") + 2]
    assert ["--source-type", "external-web"] == command[command.index("--source-type") : command.index("--source-type") + 2]
    assert command[-4:] == ["--tag", "urgent", "--write-markdown", "--json"]

    with pytest.raises(FileNotFoundError, match="RAG index files are missing"):
        rag_dispatcher.ensure_indexes(args, repo)

    calls: list[list[str]] = []

    def fake_run_command(command: list[str], cwd: Path) -> dict:
        calls.append(command)
        return {"returncode": 0, "stderr": ""}

    monkeypatch.setattr(rag_dispatcher, "run_command", fake_run_command)
    rag_dispatcher.ensure_indexes(make_args(build_if_missing=True, python="py"), repo)
    assert [call[1:6] for call in calls] == [
        ["runtime/ctl/ctl.py", "--repo-root", ".", "rag", "normalize"],
        ["runtime/ctl/ctl.py", "--repo-root", ".", "rag", "chunk"],
        ["runtime/ctl/ctl.py", "--repo-root", ".", "rag", "index"],
        ["runtime/ctl/ctl.py", "--repo-root", ".", "rag", "embed"],
    ]
    assert all(call[-1] == "--json" for call in calls)

    def fake_failed_command(command: list[str], cwd: Path) -> dict:
        return {"returncode": 1, "stderr": "failed"}

    monkeypatch.setattr(rag_dispatcher, "run_command", fake_failed_command)
    with pytest.raises(RuntimeError, match="RAG build stage failed"):
        rag_dispatcher.ensure_indexes(make_args(build_if_missing=True, python="py"), repo)

    pack1 = repo / "pack1.json"
    pack2 = repo / "pack2.json"
    empty_pack = repo / "empty-pack.json"
    empty_pack.write_text(json.dumps({"context": "", "sources": [{"chunk_id": "ignored"}]}), encoding="utf-8")
    pack1.write_text(
        json.dumps(
            {
                "context": "A" * 500,
                "sources": [{"chunk_id": "c1"}, {"source_path": "same"}],
            }
        ),
        encoding="utf-8",
    )
    pack2.write_text(
        json.dumps(
            {
                "context": "B" * 200,
                "sources": [{"chunk_id": "c1"}, {"source_path": "c2"}],
            }
        ),
        encoding="utf-8",
    )
    aggregate, sources = rag_dispatcher.aggregate_context_packs(
        repo,
        [
            {"json": None, "query": "ignored"},
            {"json": {"context_pack": str(empty_pack)}, "query": "empty"},
            {"json": {"context_pack": str(pack1)}, "query": "q1"},
            {"json": {"context_pack": str(pack2)}, "query": "q2"},
        ],
        max_chars=220,
    )

    assert "[truncated]" in aggregate
    assert "## Query: q1" in aggregate
    assert sources == [{"chunk_id": "c1"}, {"source_path": "same"}]
    assert rag_dispatcher.load_context_pack(repo, str(repo / "missing.json")) == {}

    tiny_pack = repo / "tiny-pack.json"
    tiny_pack.write_text(json.dumps({"context": "abc", "sources": [{"chunk_id": "tiny"}]}), encoding="utf-8")
    aggregate, tiny_sources = rag_dispatcher.aggregate_context_packs(
        repo,
        [{"json": {"context_pack": str(tiny_pack)}, "query": "tiny"}],
        max_chars=0,
    )
    assert aggregate == "[truncated]"
    assert tiny_sources == [{"chunk_id": "tiny"}]


def test_dispatcher_run_failure_paths_and_markdown_main(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    chunks, embeddings = write_tiny_indexes(tmp_path)
    output_dir = repo / "rag" / "retrieval"

    with pytest.raises(ValueError, match="max-queries"):
        rag_dispatcher.run(make_args(repo_root=str(repo), max_queries=0))
    with pytest.raises(ValueError, match="jobs"):
        rag_dispatcher.run(make_args(repo_root=str(repo), jobs=0))
    empty_plan = repo / "empty-plan.json"
    empty_plan.write_text(
        json.dumps({"artifact_type": "rag-dispatch-plan", "queries": []}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="No RAG queries"):
        rag_dispatcher.run(
            make_args(
                repo_root=str(repo),
                dispatch_plan=str(empty_plan),
                chunks_index=str(chunks),
                embeddings_index=str(embeddings),
                output_dir=str(output_dir),
            )
        )

    retrieval_calls: list[str] = []

    def fake_retrievals(args: argparse.Namespace, repo_root: Path, query_items: list[dict]) -> list[dict]:
        retrieval_calls.extend(item["query"] for item in query_items)
        return [{"returncode": 2, "stderr": "bad retrieval", "query": query_items[0]["query"]}]

    monkeypatch.setattr(rag_dispatcher, "run_retrievals", fake_retrievals)
    with pytest.raises(RuntimeError, match="RAG retrieval failed"):
        rag_dispatcher.run(
            make_args(
                repo_root=str(repo),
                query=["q"],
                chunks_index=str(chunks),
                embeddings_index=str(embeddings),
                output_dir=str(output_dir),
            )
        )
    assert retrieval_calls == ["q"]

    pack = repo / "pack.json"
    pack.write_text(json.dumps({"context": "context body", "sources": [{"chunk_id": "chunk"}]}), encoding="utf-8")

    def fake_success_retrievals(args: argparse.Namespace, repo_root: Path, query_items: list[dict]) -> list[dict]:
        return [
            {
                "returncode": 0,
                "query": query_items[0]["query"],
                "purpose": query_items[0].get("purpose", ""),
                "search_mode": query_items[0].get("search_mode", args.search_mode),
                "filters": query_items[0].get("filters", {}),
                "json": {
                    "retrieval_result": "result.json",
                    "context_pack": str(pack),
                    "context_markdown": "pack.md",
                    "candidate_count": 2,
                    "selected_chunk_count": 1,
                    "estimated_tokens": 10,
                },
            }
        ]

    monkeypatch.setattr(rag_dispatcher, "run_retrievals", fake_success_retrievals)
    result = rag_dispatcher.run(
        make_args(
            repo_root=str(repo),
            query=["q"],
            chunks_index=str(chunks),
            embeddings_index=str(embeddings),
            output_dir=str(output_dir),
            write_markdown=True,
        )
    )

    assert result["context_pack_count"] == 1
    assert result["source_count"] == 1
    assert result["dispatch_markdown"].endswith(".md")
    assert (repo / result["dispatch_markdown"]).read_text(encoding="utf-8").startswith("# RAG Load Dispatch Summary")

    monkeypatch.setattr(
        rag_dispatcher,
        "run",
        lambda args: {
            "dispatch_plan": "plan.json",
            "dispatch_result": "result.json",
            "dispatch_markdown": "",
            "execution_plan": "",
            "execution_plan_gate": {},
            "human_check_required": False,
            "query_count": 1,
            "context_pack_count": 1,
            "source_count": 0,
        },
    )
    assert rag_dispatcher.main(["--query", "q"]) == 0
    assert '"query_count": 1' in capsys.readouterr().out

    def raise_error(args):
        raise RuntimeError("boom")

    monkeypatch.setattr(rag_dispatcher, "run", raise_error)
    assert rag_dispatcher.main(["--query", "q"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err


def test_dispatcher_run_command_json_boundaries(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[dict] = []

    def fake_run(command, **kwargs):
        calls.append({"command": command, **kwargs})
        return subprocess.CompletedProcess(command, 0, stdout='{"ok": true}', stderr="")

    monkeypatch.setattr(rag_dispatcher.subprocess, "run", fake_run)

    result = rag_dispatcher.run_command(["tool"], tmp_path)

    assert result["json"] == {"ok": True}
    assert calls[0]["cwd"] == str(tmp_path)
    assert calls[0]["stdout"] is subprocess.PIPE

    monkeypatch.setattr(
        rag_dispatcher.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, stdout="not-json", stderr=""),
    )
    assert rag_dispatcher.run_command(["tool"], tmp_path)["json"] is None

    monkeypatch.setattr(
        rag_dispatcher.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, stdout="", stderr=""),
    )
    assert "json" not in rag_dispatcher.run_command(["tool"], tmp_path)


def test_dispatcher_writes_query_plan_before_dispatch(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    chunks, embeddings = write_tiny_indexes(tmp_path)
    output_dir = tmp_path / "retrieval"
    work_dir = tmp_path / "work" / "issue-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    execution_plan = context_dir / "execution-plan.json"
    execution_plan.write_text(
        json.dumps({"schema_version": "1.0", "artifact_type": "execution-plan"}),
        encoding="utf-8",
    )
    args = rag_dispatcher.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "--work-id",
            "issue-9001",
            "--work-dir",
            str(work_dir),
            "--task",
            "workflow doctor human gate registry",
            "--repository",
            "test-repo",
            "--branch",
            "main",
            "--chunks-index",
            str(chunks),
            "--embeddings-index",
            str(embeddings),
            "--output-dir",
            str(output_dir),
            "--max-queries",
            "2",
            "--jobs",
            "1",
            "--top-k",
            "1",
        ]
    )

    result = rag_dispatcher.run(args)

    plan = json.loads(Path(result["dispatch_plan"]).read_text(encoding="utf-8"))
    dispatch = json.loads(Path(result["dispatch_result"]).read_text(encoding="utf-8"))
    assert plan["artifact_type"] == "rag-dispatch-plan"
    assert plan["queries"]
    assert plan["queries"][0]["purpose"]
    assert plan["metadata"]["repository"] == "test-repo"
    assert plan["execution_plan"] == str(execution_plan)
    assert plan["execution_plan_gate"]["status"] == "ready"
    assert dispatch["dispatch_plan"] == result["dispatch_plan"]
    assert dispatch["dispatch_plan_id"] == plan["plan_id"]
    assert dispatch["execution_plan"] == str(execution_plan)
    assert dispatch["human_check_required"] is False
    assert result["context_pack_count"] == 2
    manifest = json.loads((context_dir / "context-manifest.json").read_text(encoding="utf-8"))
    assert {"rag-dispatch-plan", "rag-load-dispatch"} <= {item["type"] for item in manifest["contexts"]}


def test_dispatcher_can_reuse_existing_query_plan(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    chunks, embeddings = write_tiny_indexes(tmp_path)
    output_dir = tmp_path / "retrieval"
    plan = {
        "schema_version": "1.0",
        "artifact_type": "rag-dispatch-plan",
        "plan_id": "plan-test",
        "created_at": "2026-07-04T00:00:00+00:00",
        "intent": "reuse plan",
        "metadata": {
            "repository": "test-repo",
            "branch": "main",
            "tags": [],
        },
        "semantic_hints": ["workflow doctor"],
        "queries": [
            {
                "query": "workflow doctor human gate registry",
                "purpose": "reuse shared query plan",
                "search_mode": "hybrid",
                "filters": {
                    "repository": "test-repo",
                    "branch": "main",
                },
            }
        ],
        "stop_conditions": ["RAG indexes are missing"],
    }
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    args = rag_dispatcher.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "--dispatch-plan",
            str(plan_path),
            "--chunks-index",
            str(chunks),
            "--embeddings-index",
            str(embeddings),
            "--output-dir",
            str(output_dir),
            "--jobs",
            "1",
            "--top-k",
            "1",
        ]
    )

    result = rag_dispatcher.run(args)
    dispatch = json.loads(Path(result["dispatch_result"]).read_text(encoding="utf-8"))

    assert result["dispatch_plan"] == str(plan_path)
    assert dispatch["dispatch_plan_id"] == "plan-test"
    assert dispatch["context_packs"][0]["purpose"] == "reuse shared query plan"


def test_dispatcher_warns_when_work_id_has_no_execution_plan(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    chunks, embeddings = write_tiny_indexes(tmp_path)
    output_dir = tmp_path / "retrieval"
    work_dir = tmp_path / "work" / "issue-9002"
    work_dir.mkdir(parents=True)
    args = rag_dispatcher.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "--work-id",
            "issue-9002",
            "--work-dir",
            str(work_dir),
            "--task",
            "workflow doctor human gate registry",
            "--chunks-index",
            str(chunks),
            "--embeddings-index",
            str(embeddings),
            "--output-dir",
            str(output_dir),
            "--max-queries",
            "1",
            "--jobs",
            "1",
            "--top-k",
            "1",
        ]
    )

    result = rag_dispatcher.run(args)

    plan = json.loads(Path(result["dispatch_plan"]).read_text(encoding="utf-8"))
    dispatch = json.loads(Path(result["dispatch_result"]).read_text(encoding="utf-8"))
    assert plan["execution_plan_gate"]["status"] == "human-check-required"
    assert plan["human_check_required"] is True
    assert dispatch["human_check_required"] is True
    assert result["human_check_required"] is True
