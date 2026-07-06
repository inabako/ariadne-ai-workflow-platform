from __future__ import annotations

import argparse
import json
import re
import runpy
from pathlib import Path

import pytest

from runtime.workflow import github_knowledge_maintenance


def make_work_dir(tmp_path: Path, work_id: str = "github-knowledge-repo-recent") -> tuple[Path, Path]:
    repo_root = tmp_path
    work_dir = repo_root / "work" / work_id
    (work_dir / "context").mkdir(parents=True)
    return repo_root, work_dir


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def write_ready_gate(repo_root: Path, work_dir: Path, *, mutation: bool = False, rag: bool = False) -> None:
    gate_path = work_dir / "context" / "github-operation-gate.json"
    tool_path = work_dir / "context" / "tool-selection.json"
    write_json(
        gate_path,
        {
            "mutation_allowed": mutation,
            "human_check_required": rag or mutation,
        },
    )
    write_json(
        tool_path,
        {
            "human_check_required": mutation,
        },
    )
    write_json(
        work_dir / "context" / "context-manifest.json",
        {
            "schema_version": "1.0",
            "contexts": [
                {
                    "type": "github-operation-gate",
                    "path": github_knowledge_maintenance.relative_to_repo(repo_root, gate_path),
                },
                {
                    "type": "tool-selection",
                    "path": github_knowledge_maintenance.relative_to_repo(repo_root, tool_path),
                },
            ],
        },
    )


def sample_analysis() -> dict[str, object]:
    return {
        "repository": "owner/repo",
        "target_branch": "main",
        "repair_mode": "proposal",
        "summary": "Repository knowledge summary.",
        "guardrails": ["Do not mutate source."],
        "knowledge_assets": [
            {
                "title": "README",
                "asset_type": "docs",
                "source_ref": "README.md",
                "intent": "entrypoint",
                "reuse_value": "high",
            }
        ],
        "narrative_gaps": [
            {
                "id": "GAP-1",
                "asset_ref": "README",
                "gap_type": "missing intent",
                "severity": "medium",
                "evidence": ["Issue #1", "PR #2"],
                "why_it_matters": "handoff risk",
            }
        ],
        "repair_proposals": [
            {
                "id": "FIX-1",
                "target": "README",
                "proposal_type": "docs",
                "reason": "clarify intent",
                "before_summary": "unclear",
                "after_summary": "clear",
                "draft_body": "Add intent section.",
                "approval_required": True,
            }
        ],
        "github_sync_actions": [
            {
                "id": "SYNC-1",
                "title": "Update issue body",
                "target_type": "issue",
                "target_id": "1",
                "operation": "comment",
                "approval_status": "pending",
                "reason": "preserve knowledge",
                "draft_command": "gh issue comment 1 --body-file note.md",
            }
        ],
        "rag_candidates": [
            {
                "id": "RAG-1",
                "candidate_type": "workflow",
                "source_ref": "README",
                "knowledge_value": "reusable",
                "limits": "repo-specific",
            }
        ],
        "open_questions": [
            {
                "id": "Q-1",
                "question": "Can mutation proceed?",
                "reason": "human gate",
                "blocks": True,
            }
        ],
    }


def test_build_parser_parses_every_subcommand() -> None:
    parser = github_knowledge_maintenance.build_parser()

    assert parser.parse_args(["init", "--repository", "owner/repo"]).command == "init"
    assert parser.parse_args(["analysis-template", "--work-id", "w"]).command == "analysis-template"
    assert parser.parse_args(["repair-plan", "--work-id", "w"]).command == "repair-plan"
    assert parser.parse_args(["github-sync-plan", "--work-id", "w"]).command == "github-sync-plan"
    assert parser.parse_args(["rag-candidate", "--work-id", "w", "--human-check", "approved"]).command == "rag-candidate"


def test_repository_name_and_default_work_id_variants() -> None:
    assert github_knowledge_maintenance.repository_name("https://github.com/owner/Repo.Name.git") == "Repo.Name"
    assert github_knowledge_maintenance.repository_name("C:/src/Robot App.git") == "Robot-App"
    assert (
        github_knowledge_maintenance.default_work_id("owner/repo", ["issue", "full"], default_owner="")
        == "github-knowledge-repo-full"
    )
    assert (
        github_knowledge_maintenance.default_work_id("repo", ["pull-request"], default_owner="owner")
        == "github-knowledge-repo-pull-request"
    )
    report_name = github_knowledge_maintenance.rag_source_report_name("Repo Topic!")
    assert re.fullmatch(r"\d{14}_[A-Z0-9]{6}_Repo-Topic\.md", report_name)


def test_init_work_rejects_existing_without_reuse_and_script_load(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path, "github-knowledge-repo-recent")

    with pytest.raises(FileExistsError, match="Work directory already exists"):
        github_knowledge_maintenance.init_work(
            argparse.Namespace(
                command="init",
                repository="owner/repo",
                target_branch="main",
                scan_mode=["recent"],
                repair_mode="proposal",
                rag_output=False,
                work_id=work_dir.name,
                repo_root=str(repo_root),
                reuse_existing=False,
            )
        )

    namespace = runpy.run_path(str(Path(github_knowledge_maintenance.__file__)))
    assert namespace["build_parser"]


def test_gate_and_tool_selection_proposal_mode_do_not_require_human_check() -> None:
    gate = github_knowledge_maintenance.github_operation_gate(
        work_id="w",
        repository="owner/repo",
        repair_mode="proposal",
        rag_output=False,
    )
    tools = github_knowledge_maintenance.github_tool_selection(work_id="w", repair_mode="proposal")

    assert gate["mutation_allowed"] is False
    assert gate["human_check_required"] is False
    assert tools["human_check_required"] is False
    assert [tool["mode"] for tool in tools["tools"]] == ["read-only", "read-only"]


def test_register_github_knowledge_contexts_skips_missing_files_and_registers_existing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(work_dir / "context" / "tool-selection.json", {})
    calls: list[dict[str, object]] = []

    def fake_register_context(repo_root_arg, work_dir_arg, **kwargs):
        calls.append({"repo_root": repo_root_arg, "work_dir": work_dir_arg, **kwargs})

    monkeypatch.setattr(github_knowledge_maintenance, "register_context", fake_register_context)

    github_knowledge_maintenance.register_github_knowledge_contexts(repo_root, work_dir, "w")

    assert len(calls) == 1
    assert calls[0]["context_type"] == "tool-selection"
    assert calls[0]["owner"] == "dispatcher"


def test_markdown_helpers_render_empty_values_booleans_lists_and_titles() -> None:
    assert github_knowledge_maintenance.markdown_list([]).startswith("- ")
    assert github_knowledge_maintenance.markdown_list(["a", "b"]) == "- a\n- b"
    assert github_knowledge_maintenance.markdown_value(True) != github_knowledge_maintenance.markdown_value(False)
    assert github_knowledge_maintenance.field_list([], ["id"]) == "- なし"

    rendered = github_knowledge_maintenance.field_list(
        [{"id": "ITEM-1", "evidence": ["Issue #1", "PR #2"], "approval_required": True}],
        ["evidence", "approval_required", "unknown_field"],
    )

    assert "### ITEM-1" in rendered
    assert "- Issue #1" in rendered
    assert "unknown_field" in rendered


def test_load_analysis_reports_missing_work_missing_file_and_non_object(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)

    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        github_knowledge_maintenance.load_analysis(repo_root, "missing", "")

    with pytest.raises(FileNotFoundError, match="GitHub knowledge analysis does not exist"):
        github_knowledge_maintenance.load_analysis(repo_root, work_dir.name, "")

    write_json(work_dir / "context" / "github-knowledge-analysis.json", [])

    with pytest.raises(ValueError, match="must be a JSON object"):
        github_knowledge_maintenance.load_analysis(repo_root, work_dir.name, "")


def test_default_analysis_ignores_non_string_assumptions_and_analysis_template_missing_work(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(
        work_dir / "context" / "agent-context.json",
        {
            "project": {"repository": "owner/repo"},
            "assumptions": [123, "target_branch=develop", "scan_mode=issue,full", "malformed"],
        },
    )

    analysis = github_knowledge_maintenance.default_analysis(work_dir)

    assert analysis["target_branch"] == "develop"
    assert analysis["scan_mode"] == ["issue", "full"]

    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        github_knowledge_maintenance.create_analysis_template(
            argparse.Namespace(command="analysis-template", work_id="missing", analysis_path="", repo_root=str(repo_root))
        )


def test_require_github_operation_gate_reports_missing_contexts(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(work_dir / "context" / "context-manifest.json", {"contexts": []})

    with pytest.raises(RuntimeError, match="github-operation-gate, tool-selection"):
        github_knowledge_maintenance.require_github_operation_gate(repo_root, work_dir, require_mutation_gate=True)


def test_require_github_operation_gate_rejects_unapproved_mutation_and_rag(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_ready_gate(repo_root, work_dir, mutation=False, rag=False)

    with pytest.raises(RuntimeError, match="does not allow mutation"):
        github_knowledge_maintenance.require_github_operation_gate(repo_root, work_dir, require_mutation_gate=True)

    with pytest.raises(RuntimeError, match="must require Human Check for RAG publication"):
        github_knowledge_maintenance.require_github_operation_gate(repo_root, work_dir, require_rag_gate=True)


def test_build_repair_sync_and_rag_markdown_include_dynamic_sections() -> None:
    analysis = sample_analysis()

    repair_plan = github_knowledge_maintenance.build_repair_plan(analysis)
    sync_plan = github_knowledge_maintenance.build_sync_plan(analysis)
    rag_candidate = github_knowledge_maintenance.build_rag_candidate(analysis, "repo knowledge")

    assert "Repository knowledge summary." in repair_plan
    assert "FIX-1" in repair_plan
    assert "SYNC-1" in sync_plan
    assert "gh issue comment 1" in sync_plan
    assert "# repo knowledge" in rag_candidate
    assert "RAG-1" in rag_candidate


def test_build_sync_plan_renders_empty_action_placeholder() -> None:
    rendered = github_knowledge_maintenance.build_sync_plan({"repository": "owner/repo", "target_branch": "main"})

    assert "owner/repo" in rendered
    assert "SYNC-1" not in rendered


def test_create_repair_plan_writes_output_and_registers_artifact(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis_path = work_dir / "context" / "github-knowledge-analysis.json"
    output_path = tmp_path / "repair.md"
    write_json(analysis_path, sample_analysis())

    result = github_knowledge_maintenance.create_repair_plan(
        argparse.Namespace(
            command="repair-plan",
            work_id=work_dir.name,
            analysis_path="",
            output=str(output_path),
            repo_root=str(repo_root),
        )
    )

    assert result["proposal_count"] == 1
    assert result["repair_plan"] == "repair.md"
    assert output_path.exists()
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8-sig"))
    assert any(item["id"] == "GITHUB-KNOWLEDGE-REPAIR-PLAN" for item in artifact_index["artifacts"])


def test_create_rag_candidate_requires_human_approval_for_publish(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(work_dir / "context" / "github-knowledge-analysis.json", sample_analysis())

    with pytest.raises(PermissionError, match="RAG publication requires"):
        github_knowledge_maintenance.create_rag_candidate(
            argparse.Namespace(
                command="rag-candidate",
                work_id=work_dir.name,
                analysis_path="",
                topic="",
                output="",
                publish_rag=True,
                human_check="pending",
                repo_root=str(repo_root),
            )
        )


def test_create_rag_candidate_writes_explicit_output_with_ready_gate(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    output_path = tmp_path / "candidate.md"
    write_json(work_dir / "context" / "github-knowledge-analysis.json", sample_analysis())
    write_ready_gate(repo_root, work_dir)

    result = github_knowledge_maintenance.create_rag_candidate(
        argparse.Namespace(
            command="rag-candidate",
            work_id=work_dir.name,
            analysis_path="",
            topic="repo topic",
            output=str(output_path),
            publish_rag=False,
            human_check="pending",
            repo_root=str(repo_root),
        )
    )

    assert result["published"] is False
    assert result["rag_candidate"] == "candidate.md"
    assert output_path.exists()


def test_create_rag_candidate_default_and_publish_outputs(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(work_dir / "context" / "github-knowledge-analysis.json", sample_analysis())
    write_ready_gate(repo_root, work_dir, rag=True)

    default_result = github_knowledge_maintenance.create_rag_candidate(
        argparse.Namespace(
            command="rag-candidate",
            work_id=work_dir.name,
            analysis_path="",
            topic="repo topic",
            output="",
            publish_rag=False,
            human_check="pending",
            repo_root=str(repo_root),
        )
    )
    publish_result = github_knowledge_maintenance.create_rag_candidate(
        argparse.Namespace(
            command="rag-candidate",
            work_id=work_dir.name,
            analysis_path="",
            topic="repo topic",
            output="",
            publish_rag=True,
            human_check="approved",
            repo_root=str(repo_root),
        )
    )

    assert default_result["published"] is False
    assert default_result["rag_candidate"].startswith(f"work/{work_dir.name}/process-report/github-knowledge-rag-candidate-")
    assert publish_result["published"] is True
    assert publish_result["rag_candidate"].startswith("rag/github-knowledge/")


def test_run_dispatches_commands_and_rejects_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(github_knowledge_maintenance, "init_work", lambda args: {"command": "init"})
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_analysis_template",
        lambda args: {"command": "analysis-template"},
    )
    monkeypatch.setattr(github_knowledge_maintenance, "create_repair_plan", lambda args: {"command": "repair-plan"})
    monkeypatch.setattr(github_knowledge_maintenance, "create_sync_plan", lambda args: {"command": "github-sync-plan"})
    monkeypatch.setattr(github_knowledge_maintenance, "create_rag_candidate", lambda args: {"command": "rag-candidate"})

    for command in ["init", "analysis-template", "repair-plan", "github-sync-plan", "rag-candidate"]:
        assert github_knowledge_maintenance.run(argparse.Namespace(command=command)) == {"command": command}

    with pytest.raises(ValueError, match="Unsupported command"):
        github_knowledge_maintenance.run(argparse.Namespace(command="unknown"))


def test_main_prints_json(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(github_knowledge_maintenance, "run", lambda args: {"status": "ok", "command": args.command})

    code = github_knowledge_maintenance.main(["analysis-template", "--work-id", "w"])

    captured = capsys.readouterr()
    assert code == 0
    assert '"status": "ok"' in captured.out

    monkeypatch.setattr(github_knowledge_maintenance, "run", lambda args: (_ for _ in ()).throw(RuntimeError("boom")))
    assert github_knowledge_maintenance.main(["analysis-template", "--work-id", "w"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err
