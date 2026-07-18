from __future__ import annotations

import argparse
import json
import re
import runpy
import subprocess
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
        "history_rewrite_candidates": [
            {
                "id": "HISTORY-1",
                "file_paths": ["runtime/workflow/example.py", "runtime/tests/test_example.py"],
                "suspect_commits": ["abc1234 docs-only subject"],
                "expected_commit": "def5678 feat(runtime): add example workflow",
                "repair_goal": "absorb-into-existing-commit",
                "independent_responsibility": "",
                "evidence_refs": ["PR #12 diff", "git show abc1234"],
                "completion_criteria": [
                    "The leaked files are absorbed into the semantic implementation commit.",
                    "No new issue or commit message is invented solely to justify the leaked commit.",
                ],
                "recommended_action": "non-interactive-git-cli-rewrite",
                "reason": "two files were committed separately from their natural workflow change",
                "before_summary": "implementation and tests are split into an unrelated later commit",
                "after_summary": "implementation and tests are grouped in one semantic commit",
                "approval_status": "pending",
                "before_after_sha_mapping": [],
                "rollback_plan": "",
                "draft_commands": ["git status --short"],
                "verification_commands": ["git log --format=\"%H %s\" -5"],
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
    assert parser.parse_args(["detect-rebase-candidates", "--work-id", "w"]).command == "detect-rebase-candidates"
    assert parser.parse_args(["rebase-plan", "--work-id", "w"]).command == "rebase-plan"
    assert parser.parse_args(["rebase-review-intake", "--work-id", "w"]).command == "rebase-review-intake"
    assert parser.parse_args(["rebase-apply", "--work-id", "w", "--candidate-id", "HISTORY-1"]).command == "rebase-apply"
    assert parser.parse_args(["rebase-replay-package", "--work-id", "w"]).command == "rebase-replay-package"
    assert parser.parse_args(["rebase-replay-apply", "--work-id", "w"]).command == "rebase-replay-apply"
    assert (
        parser.parse_args(["rebase-replay-apply", "--work-id", "w", "--apply-mode", "git-3way"]).apply_mode
        == "git-3way"
    )
    assert parser.parse_args(["github-sync-plan", "--work-id", "w"]).command == "github-sync-plan"
    assert parser.parse_args(["github-sync-apply", "--work-id", "w", "--action-id", "SYNC-1"]).command == "github-sync-apply"
    assert parser.parse_args(["rag-candidate", "--work-id", "w", "--human-check", "approved"]).command == "rag-candidate"


def test_repository_name_and_default_work_id_variants() -> None:
    assert github_knowledge_maintenance.repository_name("https://github.com/owner/Repo.Name.git") == "Repo.Name"
    assert github_knowledge_maintenance.repository_name("C:/src/Robot App.git") == "Robot-App"
    assert (
        github_knowledge_maintenance.default_work_id("owner/repo", ["issue", "full"], default_owner="")
        == "github/original/full"
    )
    assert (
        github_knowledge_maintenance.default_work_id("repo", ["pull-request"], default_owner="owner", target_branch="dev/bk-01")
        == "github/dev-bk-01/pull-request"
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

    result = github_knowledge_maintenance.init_work(
        argparse.Namespace(
            command="init",
            repository="owner/repo",
            target_branch="dev-bk-01",
            scan_mode=["recent"],
            repair_mode="proposal",
            rag_output=False,
            work_id=None,
            repo_root=str(repo_root),
            reuse_existing=False,
            intent_summary="",
        )
    )
    assert result["work_id"] == "github/dev-bk-01/recent"
    assert result["work_dir"] == "work/github/dev-bk-01/recent"
    analysis = github_knowledge_maintenance.default_analysis(repo_root / "work" / "github" / "dev-bk-01" / "recent")
    assert analysis["work_id"] == "github/dev-bk-01/recent"


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
    assert [tool["mode"] for tool in tools["tools"]] == ["read-only", "read-only", "local-history-read"]
    assert gate["responsibility_boundary"]["github_api"]["not_allowed"]
    assert gate["responsibility_boundary"]["git_cli_local"]["authentication_required"] is False
    assert gate["responsibility_boundary"]["git_cli_remote"]["authentication_required"] is True
    assert gate["git_cli_preflight"]["install_command"] == "winget install --id Git.Git -e"
    assert next(tool for tool in tools["tools"] if tool["mode"] == "local-history-read")["authentication_required"] is False


def test_tool_selection_apply_mode_splits_local_and_remote_git_auth() -> None:
    tools = github_knowledge_maintenance.github_tool_selection(work_id="w", repair_mode="apply")

    by_mode = {tool["mode"]: tool for tool in tools["tools"]}
    assert by_mode["local-history-mutation"]["authentication_required"] is False
    assert by_mode["remote-history-mutation"]["authentication_required"] is True
    assert by_mode["remote-history-mutation"]["human_check_required"] is True


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
    assert analysis["history_rewrite_candidates"] == []

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
    rebase_plan = github_knowledge_maintenance.build_rebase_plan(analysis)
    sync_plan = github_knowledge_maintenance.build_sync_plan(analysis)
    rag_candidate = github_knowledge_maintenance.build_rag_candidate(analysis, "repo knowledge")

    assert "Repository knowledge summary." in repair_plan
    assert "FIX-1" in repair_plan
    assert "HISTORY-1" in repair_plan
    assert "Git Commit 履歴 Rebase レビュー計画" in rebase_plan
    assert "レビュー凡例" in rebase_plan
    assert "候補別 OK / NG チェックリスト" in rebase_plan
    assert "| 候補ID | OK欄 | NG欄 | 疑わしいコミット | 対象ファイル | 現在の推奨 | メモ |" in rebase_plan
    assert "| HISTORY-1 | [ ] OK | [ ] NG |" in rebase_plan
    assert "- [ ] OK: rebase整備対象として次段のitem-level計画に進める" in rebase_plan
    assert "- [ ] NG: rebaseしない / 候補から外す" in rebase_plan
    assert "keep-with-evidence" in rebase_plan
    assert "検出された差分が正当でそのまま残すべき場合" in rebase_plan
    assert "GitHub API / Git CLI 責務境界" in rebase_plan
    assert "Git CLI local" in rebase_plan
    assert "認証は不要" in rebase_plan
    assert "Git CLI remote" in rebase_plan
    assert "認証が必要" in rebase_plan
    assert "non-interactive-git-cli-rewrite" in rebase_plan
    assert "SYNC-1" in sync_plan
    assert "gh issue comment 1" in sync_plan
    assert "# repo knowledge" in rag_candidate
    assert "RAG-1" in rag_candidate


def test_build_sync_plan_renders_empty_action_placeholder() -> None:
    rendered = github_knowledge_maintenance.build_sync_plan({"repository": "owner/repo", "target_branch": "main"})

    assert "owner/repo" in rendered
    assert "SYNC-1" not in rendered


def test_history_rewrite_candidate_validation_edges() -> None:
    assert github_knowledge_maintenance.validate_history_rewrite_candidates(
        [
            {
                "id": "HISTORY-BAD",
                "file_paths": ["a.py", "b.py", "c.py", "d.py"],
                "approval_status": "approved",
            }
        ]
    ) == [
        "HISTORY-BAD: file_paths must contain 1 to 3 files.",
        "HISTORY-BAD: approved rebase repair requires repair_goal.",
        "HISTORY-BAD: approved rebase repair requires completion_criteria.",
        "HISTORY-BAD: approved rebase repair requires rollback_plan.",
        "HISTORY-BAD: approved rebase repair requires draft_commands or replay_package_ref.",
        "HISTORY-BAD: approved rebase repair requires verification_commands.",
    ]
    assert github_knowledge_maintenance.validate_history_rewrite_candidates(
        [{"id": "HISTORY-STATUS", "file_paths": ["a.py"], "approval_status": "unknown"}]
    ) == ["HISTORY-STATUS: approval_status must be pending, approved, or rejected."]
    assert github_knowledge_maintenance.validate_history_rewrite_candidates(
        [
            {
                "id": "HISTORY-KEEP",
                "file_paths": ["a.py"],
                "repair_goal": "keep-with-evidence",
                "approval_status": "approved",
                "completion_criteria": ["Keep only with evidence."],
                "before_after_sha_mapping": ["abc -> def"],
                "rollback_plan": "git reset --hard abc",
                "draft_commands": ["git status --short"],
                "verification_commands": ["git log --format=\"%H %s\" -5"],
            }
        ]
    ) == [
        "HISTORY-KEEP: keep repair requires independent_responsibility.",
        "HISTORY-KEEP: keep repair requires evidence_refs.",
    ]


def test_detect_history_rewrite_candidates_from_commit_log(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    commits = github_knowledge_maintenance.parse_commit_log(
        "\n".join(
            [
                "222222222222\x1fupdate",
                "runtime/workflow/example.py",
                "",
                "111111111111\x1ffeat(runtime): add example workflow",
                "runtime/workflow/main.py",
            ]
        )
    )
    calls: list[list[str]] = []

    def fake_git_output(_repo_path: Path, args: list[str]) -> str:
        calls.append(args)
        if len(calls) == 1:
            raise github_knowledge_maintenance.subprocess.CalledProcessError(128, args)
        return "222222222222\x1fupdate\nruntime/workflow/example.py\n"

    monkeypatch.setattr(github_knowledge_maintenance, "git_output", fake_git_output)
    assert github_knowledge_maintenance.collect_commit_summaries(tmp_path, "HEAD~30", "HEAD", 20)[0]["hash"] == "222222222222"
    assert calls[1][-1] == "HEAD"

    monkeypatch.setattr(github_knowledge_maintenance, "collect_commit_summaries", lambda *args, **kwargs: commits)

    candidates = github_knowledge_maintenance.detect_history_rewrite_candidates(
        repo_path=tmp_path,
        base="HEAD~2",
        head="HEAD",
        max_commits=20,
        max_files=3,
    )

    assert candidates[0]["id"] == "HISTORY-DETECT-001"
    assert candidates[0]["expected_commit"] == "1111111 feat(runtime): add example workflow"
    assert candidates[0]["approval_status"] == "pending"
    assert candidates[0]["repair_goal"] == "absorb-into-existing-commit"
    assert candidates[0]["recommended_action"] == "non-interactive-git-cli-rewrite"
    assert candidates[0]["content_review_evidence"]["related_commit_score"] > 0


def test_detect_history_rewrite_candidates_requires_manual_review_when_subjects_are_thin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    commits = github_knowledge_maintenance.parse_commit_log(
        "\n".join(
            [
                "333333333333\x1fupdate: guard follow-up",
                "runtime/workflow/github_knowledge_maintenance.py",
                "",
                "222222222222\x1fupdate: guard",
                "runtime/workflow/github_knowledge_maintenance.py",
                "runtime/tests/test_github_knowledge_maintenance.py",
            ]
        )
    )
    monkeypatch.setattr(github_knowledge_maintenance, "collect_commit_summaries", lambda *args, **kwargs: commits)

    candidates = github_knowledge_maintenance.detect_history_rewrite_candidates(
        repo_path=tmp_path,
        base="HEAD~2",
        head="HEAD",
        max_commits=20,
        max_files=3,
    )

    assert candidates[0]["expected_commit"] == "2222222 update: guard"
    assert candidates[0]["repair_goal"] == "manual-review-required"
    assert candidates[0]["recommended_action"] == "manual-review-required"
    assert candidates[0]["approval_status"] == "pending"
    assert candidates[0]["content_review_evidence"]["related_commit_subject_is_weak"] is True
    assert "runtime" in candidates[0]["content_review_evidence"]["candidate_domains"]


def test_create_detect_rebase_candidates_writes_analysis(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis_path = work_dir / "context" / "github-knowledge-analysis.json"
    write_json(analysis_path, sample_analysis())
    detected = [
        {
            "id": "HISTORY-DETECT-001",
            "file_paths": ["runtime/workflow/example.py"],
            "suspect_commits": ["2222222 update"],
            "expected_commit": "1111111 feat(runtime): add example workflow",
            "repair_goal": "absorb-into-existing-commit",
            "recommended_action": "non-interactive-git-cli-rewrite",
            "reason": "detected",
            "approval_status": "pending",
        }
    ]
    monkeypatch.setattr(github_knowledge_maintenance, "detect_history_rewrite_candidates", lambda **kwargs: detected)

    result = github_knowledge_maintenance.create_detect_rebase_candidates(
        argparse.Namespace(
            command="detect-rebase-candidates",
            work_id=work_dir.name,
            analysis_path="",
            git_repo=str(repo_root),
            base="HEAD~30",
            head="HEAD",
            max_commits=80,
            max_files=3,
            append=False,
            repo_root=str(repo_root),
        )
    )

    updated = json.loads(analysis_path.read_text(encoding="utf-8"))
    assert result["candidate_count"] == 1
    assert updated["history_rewrite_candidates"] == detected


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


def test_create_rebase_plan_writes_output_and_registers_artifact(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis_path = work_dir / "context" / "github-knowledge-analysis.json"
    output_path = tmp_path / "rebase.md"
    write_json(analysis_path, sample_analysis())

    result = github_knowledge_maintenance.create_rebase_plan(
        argparse.Namespace(
            command="rebase-plan",
            work_id=work_dir.name,
            analysis_path="",
            output=str(output_path),
            repo_root=str(repo_root),
        )
    )

    assert result["candidate_count"] == 1
    assert result["rebase_plan"] == "rebase.md"
    assert result["validation_errors"] == []
    rebase_plan = output_path.read_text(encoding="utf-8-sig")
    assert "HISTORY-1" in rebase_plan
    assert "追加の承認依頼ではない" in rebase_plan
    assert "再承認を求めません" in rebase_plan
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8-sig"))
    assert any(item["id"] == "GITHUB-HISTORY-REBASE-PLAN" for item in artifact_index["artifacts"])


def test_create_rebase_review_intake_reads_ok_ng_checklist(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    process_dir = work_dir / "process-report"
    process_dir.mkdir()
    analysis = sample_analysis()
    first = analysis["history_rewrite_candidates"][0]
    first.update(
        {
            "id": "HISTORY-DETECT-001",
            "repair_goal": "manual-review-required",
            "recommended_action": "manual-review-required",
            "rollback_plan": "git reset --hard def5678",
            "draft_commands": ["# replay approved commits", "git diff --quiet <old-head>..<new-head>"],
        }
    )
    analysis["history_rewrite_candidates"].append(
        {
            "id": "HISTORY-DETECT-002",
            "file_paths": ["docs/example.md"],
            "suspect_commits": ["1111111 update: docs"],
            "expected_commit": "2222222 docs(workflow): add example",
            "repair_goal": "manual-review-required",
            "recommended_action": "manual-review-required",
            "reason": "thin subject",
            "approval_status": "pending",
            "completion_criteria": ["The candidate is resolved by human review."],
            "rollback_plan": "git reset --hard 2222222",
            "draft_commands": [],
            "verification_commands": ["git log --format=\"%H %s\" -5"],
        }
    )
    analysis_path = work_dir / "context" / "github-knowledge-analysis.json"
    write_json(analysis_path, analysis)
    plan_path = process_dir / "github-history-rebase-plan-20260718_000000.md"
    plan_path.write_text(
        "\n".join(
            [
                "| 候補ID | OK欄 | NG欄 | 疑わしいコミット | 対象ファイル | 現在の推奨 | メモ |",
                "| --- | --- | --- | --- | --- | --- | --- |",
                "| HISTORY-DETECT-001 | [x] OK | [ ] NG | abc1234 docs-only subject | runtime/workflow/example.py | `manual-review-required` |  |",
                "| HISTORY-DETECT-002 | [ ] OK | [x] NG | 1111111 update: docs | docs/example.md | `manual-review-required` |  |",
            ]
        ),
        encoding="utf-8",
    )

    result = github_knowledge_maintenance.create_rebase_review_intake(
        argparse.Namespace(
            command="rebase-review-intake",
            work_id=work_dir.name,
            analysis_path="",
            plan_path=str(plan_path),
            human_check="approved",
            ok_repair_goal="auto",
            allow_partial=False,
            repo_root=str(repo_root),
        )
    )

    assert result["candidate_count"] == 2
    assert result["approved_count"] == 1
    assert result["rejected_count"] == 1
    updated = json.loads(analysis_path.read_text(encoding="utf-8"))
    approved = updated["history_rewrite_candidates"][0]
    rejected = updated["history_rewrite_candidates"][1]
    assert approved["approval_status"] == "approved"
    assert approved["repair_goal"] == "absorb-into-existing-commit"
    assert approved["recommended_action"] == "non-interactive-git-cli-rewrite"
    assert approved["draft_commands"] == []
    assert approved["replay_package_ref"] == f"work/{work_dir.name}/context/rebase-replay-package.json"
    assert approved["human_review_decision"] == "OK"
    assert rejected["approval_status"] == "rejected"
    assert rejected["repair_goal"] == "no-rewrite"
    assert rejected["human_review_decision"] == "NG"
    assert updated["rebase_review_intakes"][0]["approved_count"] == 1


def test_create_rebase_apply_requires_human_and_candidate_approval(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    candidate = analysis["history_rewrite_candidates"][0]
    candidate.update(
        {
            "approval_status": "approved",
            "before_after_sha_mapping": ["abc1234 -> def5678"],
            "rollback_plan": "git reset --hard abc1234",
            "draft_commands": ["git status --short"],
            "verification_commands": ["git log --format=\"%H %s\" -5"],
        }
    )
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_ready_gate(repo_root, work_dir, mutation=True)

    with pytest.raises(PermissionError, match="human-check approved"):
        github_knowledge_maintenance.create_rebase_apply(
            argparse.Namespace(
                command="rebase-apply",
                work_id=work_dir.name,
                candidate_id="HISTORY-1",
                analysis_path="",
                git_repo=str(repo_root),
                human_check="pending",
                allow_interactive=False,
                dry_run=True,
                repo_root=str(repo_root),
            )
        )

    result = github_knowledge_maintenance.create_rebase_apply(
        argparse.Namespace(
            command="rebase-apply",
            work_id=work_dir.name,
            candidate_id="HISTORY-1",
            analysis_path="",
            git_repo=str(repo_root),
            human_check="approved",
            allow_interactive=False,
            dry_run=True,
            repo_root=str(repo_root),
        )
    )

    assert result["dry_run"] is True
    assert result["planned_count"] == 1
    assert result["executed_count"] == 0
    assert result["verification_count"] == 1
    updated = json.loads((work_dir / "context" / "github-knowledge-analysis.json").read_text(encoding="utf-8"))
    assert updated["history_rewrite_candidates"][0]["execution_status"] == "dry-run"


def run_git(repo: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return result.stdout


def commit_file(repo: Path, path: str, text: str, message: str) -> str:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    run_git(repo, ["add", path])
    run_git(repo, ["commit", "-m", message])
    return run_git(repo, ["rev-parse", "HEAD"]).strip()


def test_apply_commit_patch_auto_3way_falls_back(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []

    monkeypatch.setattr(github_knowledge_maintenance, "commit_patch", lambda _repo, _commit: b"diff --git a/a b/a\n")

    def fail_direct(_repo: Path, _patch: bytes) -> None:
        calls.append("direct")
        raise RuntimeError("direct failed")

    def pass_3way(_repo: Path, _patch: bytes) -> None:
        calls.append("git-3way")

    monkeypatch.setattr(github_knowledge_maintenance, "apply_patch_direct", fail_direct)
    monkeypatch.setattr(github_knowledge_maintenance, "apply_patch_git_3way", pass_3way)

    mode = github_knowledge_maintenance.apply_commit_patch(tmp_path, "abc1234", "auto-3way")

    assert mode == "git-3way"
    assert calls == ["direct", "git-3way"]


def test_rebase_replay_package_generates_from_approved_candidate(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path, "github-knowledge-owner-repo-recent")
    analysis = sample_analysis()
    analysis["target_branch"] = "dev-bk"
    candidate = analysis["history_rewrite_candidates"][0]
    candidate.update(
        {
            "id": "HISTORY-REPLAY-1",
            "approval_status": "approved",
            "repair_goal": "absorb-into-existing-commit",
            "suspect_commits": ["abc1234 update: test follow-up"],
            "expected_commit": "def5678 feat(runtime): add example workflow",
            "rollback_plan": "git reset --hard def5678",
            "draft_commands": [],
            "replay_package_ref": "",
            "verification_commands": ["git diff --quiet dev-bk..HEAD"],
        }
    )
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)

    result = github_knowledge_maintenance.create_rebase_replay_package(
        argparse.Namespace(
            command="rebase-replay-package",
            work_id=work_dir.name,
            candidate_id=["HISTORY-REPLAY-1"],
            analysis_path="",
            output="",
            target_branch="",
            source_ref="",
            remote="origin",
            expected_remote_sha="",
            allow_push=False,
            apply_mode="auto-3way",
            repo_root=str(repo_root),
        )
    )

    package_path = work_dir / "context" / "rebase-replay-package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    assert result["rebase_replay_package"] == f"work/{work_dir.name}/context/rebase-replay-package.json"
    assert package["target_branch"] == "dev-bk"
    assert package["source_ref"] == "dev-bk"
    assert package["apply_mode"] == "auto-3way"
    assert package["candidate_ids"] == ["HISTORY-REPLAY-1"]
    assert package["absorb"] == [{"target": "def5678", "sources": ["abc1234"]}]
    assert package["drop"] == []
    assert package["verification_commands"] == ["git diff --quiet dev-bk..HEAD"]
    assert not list((work_dir / "context").glob("*rebase*.py"))
    updated = json.loads((work_dir / "context" / "github-knowledge-analysis.json").read_text(encoding="utf-8"))
    updated_candidate = updated["history_rewrite_candidates"][0]
    assert updated_candidate["replay_package_ref"] == f"work/{work_dir.name}/context/rebase-replay-package.json"
    assert updated["rebase_replay_packages"][0]["apply_mode"] == "auto-3way"
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    assert any(item["id"] == "GITHUB-HISTORY-REBASE-REPLAY-PACKAGE" for item in artifact_index["artifacts"])


def test_rebase_replay_package_rejects_unapproved_candidate(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    analysis["target_branch"] = "dev-bk"
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)

    with pytest.raises(PermissionError, match="HISTORY-1 is not approved"):
        github_knowledge_maintenance.create_rebase_replay_package(
            argparse.Namespace(
                command="rebase-replay-package",
                work_id=work_dir.name,
                candidate_id=["HISTORY-1"],
                analysis_path="",
                output="",
                target_branch="",
                source_ref="",
                remote="origin",
                expected_remote_sha="",
                allow_push=False,
                apply_mode="direct",
                repo_root=str(repo_root),
            )
        )


def test_rebase_replay_package_requires_split_message(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    analysis["target_branch"] = "dev-bk"
    candidate = analysis["history_rewrite_candidates"][0]
    candidate.update(
        {
            "approval_status": "approved",
            "repair_goal": "split-into-independent-commit",
            "suspect_commits": ["abc1234 update: split target"],
            "rollback_plan": "git reset --hard abc1234",
            "draft_commands": [],
            "replay_package_ref": "",
            "verification_commands": ["git diff --quiet dev-bk..HEAD"],
        }
    )
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)

    with pytest.raises(ValueError, match="split repair requires message_override"):
        github_knowledge_maintenance.create_rebase_replay_package(
            argparse.Namespace(
                command="rebase-replay-package",
                work_id=work_dir.name,
                candidate_id=["HISTORY-1"],
                analysis_path="",
                output="",
                target_branch="",
                source_ref="",
                remote="origin",
                expected_remote_sha="",
                allow_push=False,
                apply_mode="direct",
                repo_root=str(repo_root),
            )
        )


def test_rebase_replay_apply_uses_worktree_and_builtin_runtime(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path, "github-knowledge-owner-repo-recent")
    run_git(repo_root, ["init"])
    run_git(repo_root, ["config", "user.name", "Tester"])
    run_git(repo_root, ["config", "user.email", "tester@example.com"])
    run_git(repo_root, ["config", "core.autocrlf", "false"])
    run_git(repo_root, ["checkout", "-b", "dev-bk"])
    root_commit = commit_file(repo_root, "README.md", "# repo\n", "add: initial")
    target_commit = commit_file(repo_root, "runtime/workflow/example.py", "print('runtime')\n", "update: runtime")
    source_commit = commit_file(repo_root, "runtime/tests/test_example.py", "def test_example():\n    assert True\n", "update: test")
    source_tip = run_git(repo_root, ["rev-parse", "HEAD"]).strip()
    analysis = sample_analysis()
    analysis["target_branch"] = "dev-bk"
    candidate = analysis["history_rewrite_candidates"][0]
    candidate.update(
        {
            "id": "HISTORY-REPLAY-1",
            "approval_status": "approved",
            "repair_goal": "absorb-into-existing-commit",
            "expected_commit": target_commit,
            "rollback_plan": f"git reset --hard {source_tip}",
            "draft_commands": [],
            "replay_package_ref": "work/github-knowledge-owner-repo-recent/context/rebase-replay-package.json",
            "verification_commands": ["git diff --quiet dev-bk..HEAD"],
        }
    )
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_ready_gate(repo_root, work_dir, mutation=True)
    write_json(
        work_dir / "context" / "rebase-replay-package.json",
        {
            "schema_version": "1.0",
            "target_branch": "dev-bk",
            "source_ref": "dev-bk",
            "apply_mode": "git-3way",
            "candidate_ids": ["HISTORY-REPLAY-1"],
            "absorb": [{"target": target_commit, "sources": [source_commit]}],
            "message_overrides": [
                {
                    "commit": target_commit,
                    "message": "feat(runtime): add example workflow\n\nAbsorb the immediate test follow-up into the same semantic runtime change.",
                }
            ],
            "verification_commands": ["git diff --quiet dev-bk..HEAD"],
        },
    )

    result = github_knowledge_maintenance.create_rebase_replay_apply(
        argparse.Namespace(
            command="rebase-replay-apply",
            work_id=work_dir.name,
            package_path="",
            analysis_path="",
            human_check="approved",
            remote="",
            push=False,
            reuse_worktree=False,
            dry_run=False,
            repo_root=str(repo_root),
        )
    )

    assert result["tree_equal"] is True
    assert result["apply_mode"] == "git-3way"
    assert {item["mode"] for item in result["apply_results"]} == {"git-3way"}
    assert result["before_count"] == 3
    assert result["after_count"] == 2
    assert result["worktree_path"] == f"work/{work_dir.name}/git-worktree/dev-bk"
    replay_log = run_git(repo_root / result["worktree_path"], ["log", "--format=%s"])
    assert "feat(runtime): add example workflow" in replay_log
    assert "update: test" not in replay_log
    assert not list((work_dir / "context").glob("*rebase*.py"))
    updated = json.loads((work_dir / "context" / "github-knowledge-analysis.json").read_text(encoding="utf-8"))
    updated_candidate = updated["history_rewrite_candidates"][0]
    assert updated_candidate["execution_status"] == "verified"
    assert updated_candidate["execution_result"]["runtime"] == "built-in-rebase-replay"
    assert updated_candidate["execution_result"]["apply_mode"] == "git-3way"
    assert updated_candidate["before_after_sha_mapping"][0].endswith(".tsv")


def test_rebase_replay_apply_dry_run_does_not_create_worktree(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(work_dir / "context" / "github-knowledge-analysis.json", sample_analysis())
    write_ready_gate(repo_root, work_dir, mutation=True)
    write_json(
        work_dir / "context" / "rebase-replay-package.json",
        {
            "target_branch": "dev-bk",
            "source_ref": "origin/dev-bk",
            "drop": ["abc1234"],
            "candidate_ids": [],
        },
    )

    result = github_knowledge_maintenance.create_rebase_replay_apply(
        argparse.Namespace(
            command="rebase-replay-apply",
            work_id=work_dir.name,
            package_path="",
            analysis_path="",
            human_check="approved",
            remote="",
            push=False,
            reuse_worktree=False,
            dry_run=True,
            repo_root=str(repo_root),
        )
    )

    assert result["dry_run"] is True
    assert result["worktree_path"] == f"work/{work_dir.name}/git-worktree/dev-bk"
    assert not (work_dir / "git-worktree" / "dev-bk").exists()


def test_rebase_apply_rejects_interactive_rebase_even_when_allowed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Interactive rebase is not supported"):
        github_knowledge_maintenance.run_rebase_command(
            tmp_path,
            "git rebase -i abc1234^",
            allow_interactive=False,
            dry_run=True,
        )

    with pytest.raises(ValueError, match="Interactive rebase is not supported"):
        github_knowledge_maintenance.run_rebase_command(
            tmp_path,
            "git rebase --interactive abc1234^",
            allow_interactive=True,
            dry_run=True,
        )

    with pytest.raises(ValueError, match="single command"):
        github_knowledge_maintenance.run_rebase_command(
            tmp_path,
            "git status && git log",
            allow_interactive=False,
            dry_run=True,
        )


def test_github_sync_command_validation_edges() -> None:
    action = {
        "id": "SYNC-1",
        "target_type": "issue",
        "operation": "comment",
        "draft_command": "gh issue comment 1 --body-file note.md",
    }

    parts = github_knowledge_maintenance.parse_github_sync_command(action["draft_command"])
    github_knowledge_maintenance.validate_github_sync_command(action, parts)

    with pytest.raises(ValueError, match="single gh command"):
        github_knowledge_maintenance.parse_github_sync_command("gh issue comment 1 && gh pr comment 2")
    with pytest.raises(ValueError, match="must start with gh"):
        github_knowledge_maintenance.parse_github_sync_command("git status")
    with pytest.raises(ValueError, match="target does not match"):
        github_knowledge_maintenance.validate_github_sync_command(
            {"id": "SYNC-BAD", "target_type": "pull-request", "operation": "comment"},
            parts,
        )
    with pytest.raises(ValueError, match="scoped under repos"):
        github_knowledge_maintenance.validate_github_sync_command(
            {"id": "SYNC-API", "target_type": "api", "operation": "api"},
            ["gh", "api", "user"],
        )


def test_create_sync_apply_requires_approval_and_records_result(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    action = analysis["github_sync_actions"][0]
    action["approval_status"] = "approved"
    analysis["history_rewrite_candidates"] = [
        {
            "id": "HISTORY-KEEP",
            "file_paths": ["runtime/workflow/example.py"],
            "suspect_commits": ["abc1234 docs-only subject"],
            "repair_goal": "keep-with-evidence",
            "independent_responsibility": "This is a legitimate documentation-only follow-up.",
            "evidence_refs": ["PR #12 review comment"],
            "recommended_action": "no-rewrite",
            "reason": "human reviewed as independent",
            "approval_status": "approved",
        }
    ]
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_ready_gate(repo_root, work_dir, mutation=True)

    with pytest.raises(PermissionError, match="human-check approved"):
        github_knowledge_maintenance.create_sync_apply(
            argparse.Namespace(
                command="github-sync-apply",
                work_id=work_dir.name,
                action_id="SYNC-1",
                analysis_path="",
                human_check="pending",
                dry_run=True,
                repo_root=str(repo_root),
            )
        )

    result = github_knowledge_maintenance.create_sync_apply(
        argparse.Namespace(
            command="github-sync-apply",
            work_id=work_dir.name,
            action_id="SYNC-1",
            analysis_path="",
            human_check="approved",
            dry_run=True,
            repo_root=str(repo_root),
        )
    )

    updated = json.loads((work_dir / "context" / "github-knowledge-analysis.json").read_text(encoding="utf-8"))
    updated_action = updated["github_sync_actions"][0]
    assert result["executed"] is False
    assert updated_action["execution_status"] == "dry-run"
    assert updated_action["execution_result"]["skipped"] is True


def test_create_sync_apply_blocks_unresolved_rebase_candidates(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    analysis["github_sync_actions"][0]["approval_status"] = "approved"
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_ready_gate(repo_root, work_dir, mutation=True)

    with pytest.raises(RuntimeError, match="blocked until rebase candidates are resolved: HISTORY-1"):
        github_knowledge_maintenance.create_sync_apply(
            argparse.Namespace(
                command="github-sync-apply",
                work_id=work_dir.name,
                action_id="SYNC-1",
                analysis_path="",
                human_check="approved",
                dry_run=True,
                repo_root=str(repo_root),
            )
        )


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
    assert publish_result["rag_candidate"].startswith("work/db/ariadne-knowledge-platform/rag/github-knowledge/")


def test_run_dispatches_commands_and_rejects_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(github_knowledge_maintenance, "init_work", lambda args: {"command": "init"})
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_analysis_template",
        lambda args: {"command": "analysis-template"},
    )
    monkeypatch.setattr(github_knowledge_maintenance, "create_repair_plan", lambda args: {"command": "repair-plan"})
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_detect_rebase_candidates",
        lambda args: {"command": "detect-rebase-candidates"},
    )
    monkeypatch.setattr(github_knowledge_maintenance, "create_rebase_plan", lambda args: {"command": "rebase-plan"})
    monkeypatch.setattr(github_knowledge_maintenance, "create_rebase_apply", lambda args: {"command": "rebase-apply"})
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_rebase_replay_package",
        lambda args: {"command": "rebase-replay-package"},
    )
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_rebase_replay_apply",
        lambda args: {"command": "rebase-replay-apply"},
    )
    monkeypatch.setattr(github_knowledge_maintenance, "create_sync_plan", lambda args: {"command": "github-sync-plan"})
    monkeypatch.setattr(github_knowledge_maintenance, "create_sync_apply", lambda args: {"command": "github-sync-apply"})
    monkeypatch.setattr(github_knowledge_maintenance, "create_rag_candidate", lambda args: {"command": "rag-candidate"})

    for command in [
        "init",
        "analysis-template",
        "repair-plan",
        "detect-rebase-candidates",
        "rebase-plan",
        "rebase-apply",
        "rebase-replay-package",
        "rebase-replay-apply",
        "github-sync-plan",
        "github-sync-apply",
        "rag-candidate",
    ]:
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
