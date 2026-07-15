from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.rag import ingestion_optimizer


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    return repo


def write_chunk(
    repo: Path,
    name: str,
    content: str,
    *,
    status: str = "approved",
    trust_level: str = "high",
    source_path: str = "rag/source/report.md",
) -> Path:
    path = repo / "rag" / "chunks" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "chunk_id": name.removesuffix(".json"),
        "document_id": "doc-1",
        "source_path": source_path,
        "normalized_path": "rag/normalized/doc-1.json",
        "chunk_index": 1,
        "heading_path": ["Runtime"],
        "content": content,
        "metadata": {
            "document_type": "corrective-action-report",
            "title": "Runtime report",
            "repository": "inabako/ariadne",
            "branch": "main",
            "commit": "abc123",
            "status": status,
            "trust_level": trust_level,
            "tags": ["runtime"],
            "sources": ["reviewed report"],
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def make_args(repo: Path, **overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "repo_root": str(repo),
        "chunks_dir": "rag/chunks",
        "output_dir": "rag/optimized-chunks",
        "evidence_dir": "db/rag/evidence/ingestion",
        "policy": "runtime/rag/policies/knowledge-ingestion-policy.json",
        "clean_output": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_ingestion_optimizer_accepts_complete_traceable_chunk(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_chunk(
        repo,
        "accepted.json",
        "# Knowledge Capture Report\n\nKnowledge capture is verified by workflow evidence. "
        "The evidence path, repository, branch, and commit are preserved for later workflow reuse.\n",
    )

    result = ingestion_optimizer.run(make_args(repo))

    assert result["status"] == "completed"
    assert result["candidate_chunk_count"] == 1
    assert result["accepted_chunk_count"] == 1
    assert result["embedding_allowed_chunk_count"] == 1
    optimized = json.loads((repo / "rag" / "optimized-chunks" / "accepted.json").read_text(encoding="utf-8"))
    assert optimized["optimization_decision"] == "ACCEPT"
    assert optimized["metadata"]["content_hash"] == optimized["content_hash"]


def test_ingestion_optimizer_rewrites_noise_then_accepts(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_chunk(
        repo,
        "rewrite.json",
        "# Runtime Report\n\nTODO\nTODO\nRuntime evidence keeps repository, branch, commit, and source traceability. "
        "The same traceability allows later agents to trust this knowledge.\n",
    )

    result = ingestion_optimizer.run(make_args(repo))

    assert result["accepted_chunk_count"] == 1
    assert result["rewritten_chunk_count"] == 1
    rewritten_rows = (repo / "db" / "rag" / "evidence" / "ingestion" / "rewritten-chunks.jsonl").read_text(encoding="utf-8")
    assert "removed-noise-line" in rewritten_rows


def test_ingestion_optimizer_routes_governance_conflict_to_human_check(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_chunk(
        repo,
        "human.json",
        "# Governance Conflict\n\nPlatform Governance と UTF-8 policy に矛盾があるため、Workflow Coreの判断が必要です。\n",
    )

    result = ingestion_optimizer.run(make_args(repo))

    assert result["accepted_chunk_count"] == 0
    assert result["human_check_required"] is True
    assert result["human_check_required_count"] == 1
    human_rows = (repo / "db" / "rag" / "evidence" / "ingestion" / "human-check-required.jsonl").read_text(encoding="utf-8")
    assert "high-risk-topic" in human_rows


def test_ingestion_optimizer_rejects_duplicates_and_credentials(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    content = "# Secure Report\n\nRuntime evidence is reviewed and traceable. It should be absorbed once only.\n"
    write_chunk(repo, "first.json", content)
    write_chunk(repo, "duplicate.json", content)
    write_chunk(repo, "secret.json", "password = super-secret\n")

    result = ingestion_optimizer.run(make_args(repo))

    assert result["accepted_chunk_count"] == 1
    assert result["rejected_chunk_count"] == 2
    rejected = (repo / "db" / "rag" / "evidence" / "ingestion" / "rejected-chunks.jsonl").read_text(encoding="utf-8")
    assert "duplicate-content-hash" in rejected
    assert "reject-pattern" in rejected


def test_ingestion_optimizer_helpers_and_cli_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    write_chunk(repo, "one.json", "# Report\n\nTraceable approved runtime knowledge is useful for retrieval.\n")

    parser = ingestion_optimizer.build_parser()
    parsed = parser.parse_args(["--repo-root", str(repo), "--clean-output"])
    assert parsed.clean_output is True
    assert ingestion_optimizer.clamp(2) == 1.0
    assert ingestion_optimizer.clamp(-1) == 0.0
    assert ingestion_optimizer.normalized_text(" a \r\n\r\n b ") == "a\nb"

    assert ingestion_optimizer.main(["--repo-root", str(repo)]) == 0
    assert '"status": "completed"' in capsys.readouterr().out

    def fail(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(ingestion_optimizer, "run", fail)
    assert ingestion_optimizer.main(["--repo-root", str(repo)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(ingestion_optimizer.__file__)))
    assert namespace["build_parser"]


def test_ingestion_optimizer_missing_and_invalid_policy_paths(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    with pytest.raises(FileNotFoundError, match="RAG chunks directory not found"):
        ingestion_optimizer.discover_chunks(repo / "missing")

    invalid_policy = repo / "invalid-policy.json"
    invalid_policy.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid RAG ingestion policy"):
        ingestion_optimizer.load_policy(repo, invalid_policy)

    bad_weights = repo / "bad-weights.json"
    bad_weights.write_text(json.dumps({"weights": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="weights must be an object"):
        ingestion_optimizer.load_policy(repo, bad_weights)

    zero_weights = repo / "zero-weights.json"
    zero_weights.write_text(json.dumps({"weights": {"semantic_completeness": 0}}), encoding="utf-8")
    with pytest.raises(ValueError, match="weights total must be positive"):
        ingestion_optimizer.load_policy(repo, zero_weights)


def test_ingestion_optimizer_scoring_boundary_specimens(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = ingestion_optimizer.load_policy(repo, "runtime/rag/policies/knowledge-ingestion-policy.json")
    empty_chunk = {"content": "", "metadata": {}}
    heading_chunk = {"content": "# Heading", "heading_path": [], "metadata": {"status": "draft", "trust_level": "medium"}}
    low_trust_chunk = {
        "content": "Small but traceable content for reliability scoring.",
        "source_path": "rag/source.md",
        "normalized_path": "rag/normalized/doc.json",
        "document_id": "doc",
        "metadata": {"status": "draft", "trust_level": "low", "title": "t", "source": "rag/source.md"},
    }

    assert ingestion_optimizer.score_semantic_completeness("") == 0.0
    assert ingestion_optimizer.score_semantic_completeness("# Heading") == 0.25
    assert ingestion_optimizer.score_semantic_completeness("short") == 0.45
    assert ingestion_optimizer.score_retrieval_usefulness(empty_chunk, "") == 0.0
    assert ingestion_optimizer.score_retrieval_usefulness(heading_chunk, "----") == 0.1
    assert ingestion_optimizer.score_source_reliability(heading_chunk) > 0.5
    assert ingestion_optimizer.score_source_reliability(low_trust_chunk) < 0.8
    assert ingestion_optimizer.score_context_independence("上記の内容を参照します", policy["ambiguous_terms"]) < 1.0
    assert ingestion_optimizer.noise_penalty("", policy["noise_patterns"]) == 1.0
    assert ingestion_optimizer.noise_penalty("----", policy["noise_patterns"]) > 0.0
    assert ingestion_optimizer.oversize_penalty("x" * 2500) > 0.0
    assert ingestion_optimizer.fragmentation_penalty("") == 1.0
    assert ingestion_optimizer.fragmentation_penalty("# Only Heading") == 0.9
    assert ingestion_optimizer.fragmentation_penalty("```code```") == 0.65
    assert ingestion_optimizer.fragmentation_penalty("short") == 0.75
    assert ingestion_optimizer.fragmentation_penalty("this condition is incomplete:") == 0.45
    assert ingestion_optimizer.detect_human_check_reasons({"source_path": ""}, "normal", policy, 0.0) == [
        "missing-source-traceability"
    ]
    reject_reasons = ingestion_optimizer.detect_reject_reasons("", policy, 0.0, 1.0)
    assert "empty-content" in reject_reasons
    assert "unrecoverable-fragment" in reject_reasons
    assert ingestion_optimizer.decide(0.7, [], [], policy) == "REWRITE"
    assert ingestion_optimizer.decide(0.1, [], [], policy) == "REJECT"


def test_ingestion_optimizer_rewrite_retry_limit_and_duplicate_line_specimen(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = ingestion_optimizer.load_policy(repo, "runtime/rag/policies/knowledge-ingestion-policy.json")
    duplicate_text = "# Report\nsame\nsame\nUseful traceable runtime knowledge stays readable after duplicate line cleanup.\n"

    rewritten, changes = ingestion_optimizer.rewrite_content(duplicate_text, policy)
    assert "same\nsame" not in rewritten
    assert "removed-duplicate-line" in changes
    unchanged, unchanged_changes = ingestion_optimizer.rewrite_content(
        "# Report\nUseful traceable runtime knowledge stays readable.\n",
        policy,
    )
    assert unchanged.endswith("\n")
    assert unchanged_changes == []

    rewrite_policy = {
        **policy,
        "thresholds": {"accept": 0.99, "rewrite": 0.01},
        "human_check_topics": [],
    }
    chunk = {
        "chunk_id": "retry",
        "document_id": "doc",
        "source_path": "rag/source.md",
        "normalized_path": "rag/normalized/doc.json",
        "chunk_index": 1,
        "heading_path": ["Report"],
        "content": duplicate_text,
        "metadata": {
            "document_type": "note",
            "title": "Report",
            "status": "approved",
            "trust_level": "high",
            "source": "rag/source.md",
        },
    }

    result = ingestion_optimizer.evaluate_chunk(chunk, rewrite_policy, set(), after_rewrite=True)

    assert result["decision"] == "HUMAN_CHECK"
    assert "rewrite-retry-limit-reached" in result["human_check_reasons"]


def test_ingestion_optimizer_clean_output_empty_run_and_invalid_chunk_specimens(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    chunks_dir = repo / "rag" / "chunks"
    output_dir = repo / "rag" / "optimized-chunks"
    evidence_dir = repo / "db" / "rag" / "evidence" / "ingestion"
    chunks_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)
    evidence_dir.mkdir(parents=True)
    stale_chunk = output_dir / "stale.json"
    stale_evidence = evidence_dir / "accepted-chunks.jsonl"
    stale_chunk.write_text("{}", encoding="utf-8")
    stale_evidence.write_text("stale\n", encoding="utf-8")

    result = ingestion_optimizer.run(make_args(repo, clean_output=True))

    assert result["candidate_chunk_count"] == 0
    assert result["average_optimization_score"] == 0.0
    assert not stale_chunk.exists()
    assert stale_evidence.read_text(encoding="utf-8") == ""

    protected_duckdb = repo / "db" / "rag"
    protected_duckdb.mkdir(parents=True, exist_ok=True)
    with pytest.raises(ValueError, match="Refusing to clean protected RAG path"):
        ingestion_optimizer.run(make_args(repo, output_dir="db/rag", clean_output=True))

    invalid_direct = chunks_dir / "invalid-direct.json"
    invalid_direct.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid RAG chunk document"):
        ingestion_optimizer.optimize_chunk(repo, invalid_direct, ingestion_optimizer.load_policy(repo, "runtime/rag/policies/knowledge-ingestion-policy.json"), set())

    with pytest.raises(ValueError, match="Invalid RAG chunk document"):
        ingestion_optimizer.run(make_args(repo))
