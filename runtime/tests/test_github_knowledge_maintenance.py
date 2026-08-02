from __future__ import annotations

import argparse
import json
import re
import runpy
import subprocess
from pathlib import Path

import pytest

from runtime.workflow import github_knowledge_maintenance


DEFAULT_GITHUB_WORK_ID = "github/original/recent"
BRANCH_GITHUB_WORK_ID = "github/dev-bk/recent"


def work_id_for_path(work_dir: Path) -> str:
    return github_knowledge_maintenance.work_id_from_work_dir(work_dir)


def make_work_dir(tmp_path: Path, work_id: str = DEFAULT_GITHUB_WORK_ID) -> tuple[Path, Path]:
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
    assert parser.parse_args(["artifact-integrity", "--work-id", "w"]).command == "artifact-integrity"
    assert parser.parse_args(["status", "--work-id", "w"]).command == "status"
    assert parser.parse_args(["next-action", "--work-id", "w"]).command == "next-action"
    assert parser.parse_args(["resume", "--work-id", "w"]).command == "resume"
    assert parser.parse_args(["verify-remote", "--work-id", "w", "--expected-remote-sha", "abc"]).command == "verify-remote"
    assert parser.parse_args(["cleanup-worktree", "--work-id", "w", "--force"]).command == "cleanup-worktree"
    assert parser.parse_args(["repair-plan", "--work-id", "w"]).command == "repair-plan"
    assert parser.parse_args(["detect-rebase-candidates", "--work-id", "w"]).command == "detect-rebase-candidates"
    assert parser.parse_args(["detect-rebase-candidates", "--work-id", "w", "--all-history"]).all_history is True
    assert parser.parse_args(["rebase-plan", "--work-id", "w"]).command == "rebase-plan"
    assert parser.parse_args(["rebase-review-intake", "--work-id", "w"]).command == "rebase-review-intake"
    assert parser.parse_args(["message-repair-plan", "--work-id", "w"]).command == "message-repair-plan"
    assert parser.parse_args(["message-review-intake", "--work-id", "w"]).command == "message-review-intake"
    assert parser.parse_args(["rebase-apply", "--work-id", "w", "--candidate-id", "HISTORY-1"]).command == "rebase-apply"
    assert parser.parse_args(["rebase-replay-package", "--work-id", "w"]).command == "rebase-replay-package"
    assert parser.parse_args(["rebase-replay-package", "--work-id", "w", "--push-allowed"]).allow_push is True
    assert parser.parse_args(["message-repair-package", "--work-id", "w"]).command == "message-repair-package"
    assert parser.parse_args(["message-repair-package", "--work-id", "w", "--push-allowed"]).allow_push is True
    assert parser.parse_args(["rebase-replay-apply", "--work-id", "w"]).command == "rebase-replay-apply"
    assert (
        parser.parse_args(["rebase-replay-apply", "--work-id", "w", "--apply-mode", "git-3way"]).apply_mode
        == "git-3way"
    )
    publish_args = parser.parse_args(
        [
            "publish-verified-replay",
            "--work-id",
            "w",
            "--target-branch",
            "dev-bk",
            "--expected-remote-sha",
            "abc123",
            "--human-check",
            "approved",
        ]
    )
    assert publish_args.command == "publish-verified-replay"
    assert publish_args.expected_remote_sha == "abc123"
    assert parser.parse_args(["github-sync-plan", "--work-id", "w"]).command == "github-sync-plan"
    assert parser.parse_args(["github-sync-review-plan", "--work-id", "w"]).command == "github-sync-review-plan"
    assert parser.parse_args(["github-sync-review-intake", "--work-id", "w"]).command == "github-sync-review-intake"
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
    assert github_knowledge_maintenance.work_id_from_work_dir(
        Path("C:/repo/work/github/original/recent")
    ) == "github/original/recent"
    report_name = github_knowledge_maintenance.rag_source_report_name("Repo Topic!")
    assert re.fullmatch(r"\d{14}_[A-Z0-9]{6}_Repo-Topic\.md", report_name)


def test_status_reports_package_execution_and_next_action(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    analysis["target_branch"] = "feature/issue-2-v0.0.2"
    analysis["message_repair_candidates"] = [
        {
            "id": "MESSAGE-REPAIR-001",
            "approval_status": "approved",
            "execution_status": "pending",
            "commit": "abc123",
            "proposed_commit_message": "test(runtime): improve resume command\n",
        }
    ]
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_json(
        work_dir / "context" / "message-repair-package.json",
        {
            "target_branch": "feature/issue-2-v0.0.2",
            "source_ref": "origin/feature/issue-2-v0.0.2",
            "remote": "origin",
            "apply_mode": "auto-3way",
            "allow_push": True,
            "expected_remote_sha": "abc123",
            "candidate_ids": ["MESSAGE-REPAIR-001"],
            "message_overrides": [{"commit": "abc123", "message": "test(runtime): improve resume command\n"}],
        },
    )

    result = github_knowledge_maintenance.run(
        argparse.Namespace(
            command="status",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            repo_root=str(repo_root),
        )
    )

    assert result["latest_package"]["allow_push"] is True
    assert result["latest_package"]["expected_remote_sha"] == "abc123"
    assert result["message_repair_candidates"]["unresolved"] == 1
    assert result["next_action"]["action"] == "verify-remote-then-rebase-apply"
    assert "--push" in result["next_action"]["command"]


def test_next_action_prefers_reuse_worktree_when_replay_worktree_exists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    analysis["target_branch"] = "feature/issue-2-v0.0.2"
    analysis["history_rewrite_candidates"][0]["approval_status"] = "approved"
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_json(
        work_dir / "context" / "rebase-replay-package.json",
        {
            "target_branch": "feature/issue-2-v0.0.2",
            "source_ref": "origin/feature/issue-2-v0.0.2",
            "remote": "origin",
            "apply_mode": "direct",
            "allow_push": False,
            "expected_remote_sha": "",
            "candidate_ids": ["HISTORY-1"],
            "absorb": [{"target": "def5678", "sources": ["abc1234"]}],
        },
    )
    replay_dir = work_dir / "git-worktree" / "feature-issue-2-v0.0.2"
    replay_dir.mkdir(parents=True)
    monkeypatch.setattr(github_knowledge_maintenance, "git_text", lambda *_args, **_kwargs: "## replay\n")

    result = github_knowledge_maintenance.run(
        argparse.Namespace(
            command="next-action",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            repo_root=str(repo_root),
        )
    )

    assert result["next_action"]["action"] == "resume-rebase-apply-with-reuse-worktree"
    assert "--reuse-worktree" in result["next_action"]["command"]
    assert "cleanup-worktree" in result["next_action"]["cleanup_command"]


def test_resume_blocks_when_analysis_json_is_corrupt(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis_path = work_dir / "context" / "github-knowledge-analysis.json"
    analysis_path.write_text("{invalid", encoding="utf-8")

    result = github_knowledge_maintenance.run(
        argparse.Namespace(
            command="resume",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            repo_root=str(repo_root),
        )
    )

    assert result["encoding_gate"]["status"] == "block"
    assert result["next_action"]["state"] == "encoding-gate-blocked"
    assert result["next_action"]["action"] == "repair-artifact-integrity-before-resume"
    assert any("json-parse-failed" in finding["message"] for finding in result["encoding_gate"]["findings"])


def test_resume_blocks_push_package_without_expected_remote_sha(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    mojibake_marker = "こんにちは".encode("utf-8").decode("cp932")[:1]
    analysis["summary"] = f"{mojibake_marker} marker should block resume artifacts."
    analysis["history_rewrite_candidates"][0]["approval_status"] = "approved"
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_json(
        work_dir / "context" / "rebase-replay-package.json",
        {
            "target_branch": "main",
            "source_ref": "origin/main",
            "remote": "origin",
            "apply_mode": "direct",
            "allow_push": True,
            "expected_remote_sha": "",
            "candidate_ids": ["HISTORY-1"],
            "absorb": [{"target": "def5678", "sources": ["abc1234"]}],
        },
    )

    result = github_knowledge_maintenance.run(
        argparse.Namespace(
            command="next-action",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            repo_root=str(repo_root),
        )
    )

    assert result["encoding_gate"]["status"] == "block"
    assert result["next_action"]["state"] == "encoding-gate-blocked"
    assert any("mojibake-marker-present" in finding["message"] for finding in result["encoding_gate"]["findings"])
    assert any("expected-remote-sha" in finding["message"] for finding in result["encoding_gate"]["findings"])


def test_verify_remote_compares_expected_sha_from_package(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    analysis["target_branch"] = "feature/issue-2-v0.0.2"
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_json(
        work_dir / "context" / "rebase-replay-package.json",
        {
            "target_branch": "feature/issue-2-v0.0.2",
            "source_ref": "origin/feature/issue-2-v0.0.2",
            "remote": "origin",
            "apply_mode": "direct",
            "allow_push": True,
            "expected_remote_sha": "abc123",
            "candidate_ids": [],
        },
    )
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "git_text",
        lambda *_args, **_kwargs: "abc123\trefs/heads/feature/issue-2-v0.0.2\n",
    )

    result = github_knowledge_maintenance.run(
        argparse.Namespace(
            command="verify-remote",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            package_path="",
            target_branch="",
            remote="",
            expected_remote_sha="",
            repo_root=str(repo_root),
        )
    )

    assert result["matches"] is True
    assert result["next_action"] == "safe-to-push"


def test_cleanup_worktree_requires_force_before_removal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    analysis["target_branch"] = "feature/issue-2-v0.0.2"
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    replay_dir = work_dir / "git-worktree" / "feature-issue-2-v0.0.2"
    replay_dir.mkdir(parents=True)
    calls: list[list[str]] = []

    def fake_git_text(_repo: Path, args: list[str], **_kwargs: object) -> str:
        calls.append(args)
        if args[:3] == ["worktree", "remove", "--force"]:
            replay_dir.rmdir()
        return ""

    monkeypatch.setattr(github_knowledge_maintenance, "git_text", fake_git_text)
    dry_result = github_knowledge_maintenance.run(
        argparse.Namespace(
            command="cleanup-worktree",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            target_branch="",
            force=False,
            prune=False,
            repo_root=str(repo_root),
        )
    )
    assert dry_result["force_required"] is True
    assert dry_result["exists_after"] is True

    remove_result = github_knowledge_maintenance.run(
        argparse.Namespace(
            command="cleanup-worktree",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            target_branch="",
            force=True,
            prune=False,
            repo_root=str(repo_root),
        )
    )
    assert remove_result["removed"] is True
    assert remove_result["exists_after"] is False
    assert any(args[:3] == ["worktree", "remove", "--force"] for args in calls)


def test_init_work_rejects_existing_without_reuse_and_script_load(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path, "github/original/recent")

    with pytest.raises(FileExistsError, match="Work directory already exists"):
        github_knowledge_maintenance.init_work(
            argparse.Namespace(
                command="init",
                repository="owner/repo",
                target_branch="main",
                scan_mode=["recent"],
                repair_mode="proposal",
                rag_output=False,
                work_id=work_id_for_path(work_dir),
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
        github_knowledge_maintenance.load_analysis(repo_root, work_id_for_path(work_dir), "")

    write_json(work_dir / "context" / "github-knowledge-analysis.json", [])

    with pytest.raises(ValueError, match="must be a JSON object"):
        github_knowledge_maintenance.load_analysis(repo_root, work_id_for_path(work_dir), "")


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
    assert "### 詳細事項" in rebase_plan
    detail_section = rebase_plan.split("### 詳細事項", 1)[1]
    assert "OK / NG のチェックは上の「候補別 OK / NG チェックリスト」にのみ記入してください。" in detail_section
    assert "- [ ] OK:" not in detail_section
    assert "- [ ] NG:" not in detail_section
    assert "- 想定吸収先 / 期待commit: def5678 feat(runtime): add example workflow" in detail_section
    assert "- 判断理由: two files were committed separately from their natural workflow change" in detail_section
    assert "- 証跡refs: PR #12 diff, git show abc1234" in detail_section
    assert "- Verification commands: git log --format=\"%H %s\" -5" in detail_section
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
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            git_repo=str(repo_root),
            base="HEAD~30",
            head="HEAD",
            max_commits=80,
            max_files=3,
            all_history=False,
            append=False,
            repo_root=str(repo_root),
        )
    )

    updated = json.loads(analysis_path.read_text(encoding="utf-8"))
    assert result["candidate_count"] == 1
    assert result["base"] == "HEAD~30"
    assert result["all_history"] is False
    assert updated["history_rewrite_candidates"] == detected

    result = github_knowledge_maintenance.create_detect_rebase_candidates(
        argparse.Namespace(
            command="detect-rebase-candidates",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            git_repo=str(repo_root),
            base="HEAD~30",
            head="HEAD",
            max_commits=200,
            max_files=3,
            all_history=True,
            append=False,
            repo_root=str(repo_root),
        )
    )

    assert result["base"] == ""
    assert result["all_history"] is True


def test_create_repair_plan_writes_output_and_registers_artifact(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis_path = work_dir / "context" / "github-knowledge-analysis.json"
    output_path = tmp_path / "repair.md"
    write_json(analysis_path, sample_analysis())

    result = github_knowledge_maintenance.create_repair_plan(
        argparse.Namespace(
            command="repair-plan",
            work_id=work_id_for_path(work_dir),
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
            work_id=work_id_for_path(work_dir),
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


def test_create_artifact_integrity_report_passes_for_valid_analysis_and_rebase_plan(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis_path = work_dir / "context" / "github-knowledge-analysis.json"
    write_json(analysis_path, sample_analysis())
    plan_path = work_dir / "process-report" / "github-history-rebase-plan-20260718_000000.md"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text("# Plan\n\n## 候補別 OK / NG チェックリスト\n", encoding="utf-8")

    result = github_knowledge_maintenance.create_artifact_integrity_report(
        argparse.Namespace(
            command="artifact-integrity",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            output="",
            fail_on_finding=False,
            repo_root=str(repo_root),
        )
    )

    assert result["status"] == "pass"
    assert result["findings"] == []
    assert result["report_path"].endswith(".md")
    assert result["report_json"].endswith(".json")
    assert result["gate_restart"]["gate"] == "github-knowledge-artifact-integrity-gate"
    assert result["gate_restart"]["next_on_pass"] == "return-to-calling-workflow-after-gate"
    assert any("ok-ng-checklist-present" in item["content_signals"] for item in result["artifacts"])


def test_create_artifact_integrity_report_fails_for_invalid_analysis_json(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis_path = work_dir / "context" / "github-knowledge-analysis.json"
    analysis_path.write_text("{invalid", encoding="utf-8")

    result = github_knowledge_maintenance.create_artifact_integrity_report(
        argparse.Namespace(
            command="artifact-integrity",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            output="",
            fail_on_finding=False,
            repo_root=str(repo_root),
        )
    )

    assert result["status"] == "fail"
    assert any("json-parse-failed" in finding for finding in result["findings"])
    assert result["gate_restart"]["repair_available"] is True
    assert result["gate_restart"]["next_on_fail"] == "stay-at-gate"

    with pytest.raises(RuntimeError, match="artifact integrity failed"):
        github_knowledge_maintenance.create_artifact_integrity_report(
            argparse.Namespace(
                command="artifact-integrity",
                work_id=work_id_for_path(work_dir),
                analysis_path="",
                output="",
                fail_on_finding=True,
                repo_root=str(repo_root),
            )
        )


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
            work_id=work_id_for_path(work_dir),
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
    assert approved["replay_package_ref"] == f"work/{work_id_for_path(work_dir)}/context/rebase-replay-package.json"
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
                work_id=work_id_for_path(work_dir),
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
            work_id=work_id_for_path(work_dir),
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
    repo_root, work_dir = make_work_dir(tmp_path, "github/dev-bk/recent")
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
            work_id=work_id_for_path(work_dir),
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
    assert result["rebase_replay_package"] == f"work/{work_id_for_path(work_dir)}/context/rebase-replay-package.json"
    assert package["target_branch"] == "dev-bk"
    assert package["source_ref"] == "dev-bk"
    assert package["apply_mode"] == "auto-3way"
    assert package["replay_strategy"] == "tree-preserving"
    assert package["candidate_ids"] == ["HISTORY-REPLAY-1"]
    assert package["absorb"] == [{"target": "def5678", "sources": ["abc1234"]}]
    assert package["drop"] == []
    assert package["verification_commands"] == ["git diff --quiet dev-bk..HEAD"]
    assert not list((work_dir / "context").glob("*rebase*.py"))
    updated = json.loads((work_dir / "context" / "github-knowledge-analysis.json").read_text(encoding="utf-8"))
    updated_candidate = updated["history_rewrite_candidates"][0]
    assert updated_candidate["replay_package_ref"] == f"work/{work_id_for_path(work_dir)}/context/rebase-replay-package.json"
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
                work_id=work_id_for_path(work_dir),
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
                work_id=work_id_for_path(work_dir),
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
    repo_root, work_dir = make_work_dir(tmp_path, "github/dev-bk/recent")
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
            "replay_package_ref": "work/github/dev-bk/recent/context/rebase-replay-package.json",
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
            "absorb": [{"target": target_commit[:7], "sources": [source_commit[:7]]}],
            "message_overrides": [
                {
                    "commit": target_commit[:7],
                    "message": "feat(runtime): add example workflow\n\nAbsorb the immediate test follow-up into the same semantic runtime change.",
                }
            ],
            "verification_commands": [
                'git log --format="%H %s" --max-count=20',
                "git diff --quiet dev-bk..HEAD",
            ],
        },
    )

    result = github_knowledge_maintenance.create_rebase_replay_apply(
        argparse.Namespace(
            command="rebase-replay-apply",
            work_id=work_id_for_path(work_dir),
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
    assert {item["mode"] for item in result["apply_results"]} == {"tree-replay", "tree-overlay"}
    assert result["before_count"] == 3
    assert result["after_count"] == 2
    assert all(item["returncode"] == 0 for item in result["verification_results"])
    assert result["worktree_path"] == f"work/{work_id_for_path(work_dir)}/git-worktree/dev-bk"
    replay_log = run_git(repo_root / result["worktree_path"], ["log", "--format=%s"])
    assert "feat(runtime): add example workflow" in replay_log
    assert "update: test" not in replay_log
    mapping = (repo_root / result["mapping_path"]).read_text(encoding="utf-8")
    assert f"{source_commit}\tDROPPED" in mapping
    assert not list((work_dir / "context").glob("*rebase*.py"))
    updated = json.loads((work_dir / "context" / "github-knowledge-analysis.json").read_text(encoding="utf-8"))
    updated_candidate = updated["history_rewrite_candidates"][0]
    assert updated_candidate["execution_status"] == "verified"
    assert updated_candidate["execution_result"]["runtime"] == "built-in-rebase-replay"
    assert updated_candidate["execution_result"]["apply_mode"] == "git-3way"
    assert updated_candidate["before_after_sha_mapping"][0].endswith(".tsv")


def test_rebase_replay_apply_preserves_final_tree_when_absorbed_patch_context_moved(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path, "github/dev-bk/recent")
    run_git(repo_root, ["init"])
    run_git(repo_root, ["config", "user.name", "Tester"])
    run_git(repo_root, ["config", "user.email", "tester@example.com"])
    run_git(repo_root, ["config", "core.autocrlf", "false"])
    run_git(repo_root, ["checkout", "-b", "dev-bk"])
    commit_file(repo_root, "README.md", "# repo\n", "add: initial")
    target_commit = commit_file(repo_root, "docs/guide.md", "alpha\n", "docs: add guide")
    middle_commit = commit_file(repo_root, "docs/guide.md", "alpha\nbeta\n", "docs: expand guide")
    source_commit = commit_file(repo_root, "docs/guide.md", "alpha\nbeta\ngamma\n", "update: guide follow-up")
    source_tip = run_git(repo_root, ["rev-parse", "HEAD"]).strip()
    source_tree = run_git(repo_root, ["rev-parse", f"{source_tip}^{{tree}}"]).strip()
    analysis = sample_analysis()
    analysis["target_branch"] = "dev-bk"
    candidate = analysis["history_rewrite_candidates"][0]
    candidate.update(
        {
            "id": "HISTORY-REPLAY-CONTEXT",
            "approval_status": "approved",
            "repair_goal": "absorb-into-existing-commit",
            "expected_commit": target_commit,
            "suspect_commits": [source_commit],
            "rollback_plan": f"git reset --hard {source_tip}",
            "draft_commands": [],
            "replay_package_ref": "work/github/dev-bk/recent/context/rebase-replay-package.json",
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
            "apply_mode": "auto-3way",
            "candidate_ids": ["HISTORY-REPLAY-CONTEXT"],
            "absorb": [{"target": target_commit[:7], "sources": [source_commit[:7]]}],
            "verification_commands": ["git diff --quiet dev-bk..HEAD"],
        },
    )

    result = github_knowledge_maintenance.create_rebase_replay_apply(
        argparse.Namespace(
            command="rebase-replay-apply",
            work_id=work_id_for_path(work_dir),
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

    replay_repo = repo_root / result["worktree_path"]
    replay_tree = run_git(replay_repo, ["rev-parse", "HEAD^{tree}"]).strip()
    replay_log = run_git(replay_repo, ["log", "--format=%s"])
    mapping = (repo_root / result["mapping_path"]).read_text(encoding="utf-8")
    assert result["tree_equal"] is True
    assert replay_tree == source_tree
    assert result["before_count"] == 4
    assert result["after_count"] == 3
    assert "docs: add guide" in replay_log
    assert "docs: expand guide" in replay_log
    assert "update: guide follow-up" not in replay_log
    assert f"{source_commit}\tDROPPED" in mapping
    assert f"{middle_commit}\tDROPPED" not in mapping


def test_rebase_replay_apply_resolves_absorb_cycle_to_earliest_anchor(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path, "github/dev-bk/recent")
    run_git(repo_root, ["init"])
    run_git(repo_root, ["config", "user.name", "Tester"])
    run_git(repo_root, ["config", "user.email", "tester@example.com"])
    run_git(repo_root, ["config", "core.autocrlf", "false"])
    run_git(repo_root, ["checkout", "-b", "dev-bk"])
    commit_file(repo_root, "README.md", "# repo\n", "add: initial")
    target_commit = commit_file(repo_root, "runtime/workflow/example.py", "print('runtime')\n", "update: runtime")
    source_commit = commit_file(repo_root, "runtime/tests/test_example.py", "def test_example():\n    assert True\n", "update: test")
    analysis = sample_analysis()
    analysis["target_branch"] = "dev-bk"
    for candidate_id, expected, suspect in [
        ("HISTORY-REPLAY-1", target_commit, source_commit),
        ("HISTORY-REPLAY-2", source_commit, target_commit),
    ]:
        candidate = dict(analysis["history_rewrite_candidates"][0])
        candidate.update(
            {
                "id": candidate_id,
                "approval_status": "approved",
                "repair_goal": "absorb-into-existing-commit",
                "expected_commit": expected,
                "suspect_commits": [suspect],
                "rollback_plan": "git reset --hard HEAD",
                "verification_commands": ["git diff --quiet dev-bk..HEAD"],
            }
        )
        analysis.setdefault("history_rewrite_candidates", []).append(candidate)
    analysis["history_rewrite_candidates"] = analysis["history_rewrite_candidates"][1:]
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_ready_gate(repo_root, work_dir, mutation=True)
    write_json(
        work_dir / "context" / "rebase-replay-package.json",
        {
            "target_branch": "dev-bk",
            "source_ref": "dev-bk",
            "apply_mode": "git-3way",
            "candidate_ids": ["HISTORY-REPLAY-1", "HISTORY-REPLAY-2"],
            "absorb": [
                {"target": target_commit[:7], "sources": [source_commit[:7]]},
                {"target": source_commit[:7], "sources": [target_commit[:7]]},
            ],
            "verification_commands": ["git diff --quiet dev-bk..HEAD"],
        },
    )

    result = github_knowledge_maintenance.create_rebase_replay_apply(
        argparse.Namespace(
            command="rebase-replay-apply",
            work_id=work_id_for_path(work_dir),
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

    replay_repo = repo_root / result["worktree_path"]
    replay_log = run_git(replay_repo, ["log", "--format=%s"])
    mapping = (repo_root / result["mapping_path"]).read_text(encoding="utf-8")
    report = (repo_root / result["report_path"]).read_text(encoding="utf-8")
    assert result["tree_equal"] is True
    assert result["before_count"] == 3
    assert result["after_count"] == 2
    assert "update: runtime" in replay_log
    assert "update: test" not in replay_log
    assert f"{target_commit}\tDROPPED" not in mapping
    assert f"{source_commit}\tDROPPED" in mapping
    assert "Semantic Anchor Resolution" in report
    assert "cycle resolved to earliest responsibility anchor" in report


def test_message_repair_plan_intake_package_and_replay_apply(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path, "github/dev-bk/recent")
    run_git(repo_root, ["init"])
    run_git(repo_root, ["config", "user.name", "Tester"])
    run_git(repo_root, ["config", "user.email", "tester@example.com"])
    run_git(repo_root, ["config", "core.autocrlf", "false"])
    run_git(repo_root, ["checkout", "-b", "dev-bk"])
    commit_file(repo_root, "README.md", "# repo\n", "feat(runtime): add baseline\n\nIntent: baseline")
    weak_commit = commit_file(repo_root, "runtime/workflow/example.py", "print('runtime')\n", "update: runtime")
    source_tip = run_git(repo_root, ["rev-parse", "HEAD"]).strip()
    source_tree = run_git(repo_root, ["rev-parse", f"{source_tip}^{{tree}}"]).strip()
    analysis = sample_analysis()
    analysis["target_branch"] = "dev-bk"
    analysis["history_rewrite_candidates"] = []
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_ready_gate(repo_root, work_dir, mutation=True)

    plan = github_knowledge_maintenance.create_message_repair_plan(
        argparse.Namespace(
            command="message-repair-plan",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            git_repo=str(repo_root),
            source_ref="dev-bk",
            max_commits=10,
            output="",
            repo_root=str(repo_root),
        )
    )

    plan_path = repo_root / plan["message_repair_plan"]
    text = plan_path.read_text(encoding="utf-8")
    assert "MESSAGE-REPAIR-001" in text
    assert "fix(runtime): runtime" in text or "feat(runtime): runtime" in text
    plan_path.write_text(text.replace("| MESSAGE-REPAIR-001 | [ ] OK | [ ] NG |", "| MESSAGE-REPAIR-001 | [x] OK | [ ] NG |"), encoding="utf-8")

    intake = github_knowledge_maintenance.create_message_review_intake(
        argparse.Namespace(
            command="message-review-intake",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            plan_path=str(plan_path),
            human_check="approved",
            allow_partial=False,
            repo_root=str(repo_root),
        )
    )
    assert intake["approved_count"] == 1

    package = github_knowledge_maintenance.create_message_repair_package(
        argparse.Namespace(
            command="message-repair-package",
            work_id=work_id_for_path(work_dir),
            candidate_id=[],
            analysis_path="",
            output="",
            target_branch="dev-bk",
            source_ref="dev-bk",
            remote="origin",
            expected_remote_sha="",
            allow_push=False,
            apply_mode="auto-3way",
            repo_root=str(repo_root),
        )
    )
    package_data = json.loads((repo_root / package["message_repair_package"]).read_text(encoding="utf-8"))
    assert package_data["message_overrides"][0]["commit"] == weak_commit

    result = github_knowledge_maintenance.create_rebase_replay_apply(
        argparse.Namespace(
            command="rebase-replay-apply",
            work_id=work_id_for_path(work_dir),
            package_path=str(repo_root / package["message_repair_package"]),
            analysis_path="",
            human_check="approved",
            remote="",
            push=False,
            reuse_worktree=False,
            dry_run=False,
            repo_root=str(repo_root),
        )
    )

    replay_repo = repo_root / result["worktree_path"]
    replay_tree = run_git(replay_repo, ["rev-parse", "HEAD^{tree}"]).strip()
    replay_log = run_git(replay_repo, ["log", "--format=%s", "--max-count=1"])
    updated = json.loads((work_dir / "context" / "github-knowledge-analysis.json").read_text(encoding="utf-8"))
    assert result["tree_equal"] is True
    assert replay_tree == source_tree
    assert "update: runtime" not in replay_log
    assert updated["message_repair_candidates"][0]["execution_status"] == "verified"
    assert updated["message_repair_candidates"][0]["before_after_sha_mapping"][0].endswith(".tsv")


def test_publish_verified_replay_pushes_existing_verified_tip(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path, "github/dev-bk/recent")
    remote_repo = tmp_path / "remote.git"
    run_git(repo_root, ["init"])
    run_git(repo_root, ["config", "user.name", "Tester"])
    run_git(repo_root, ["config", "user.email", "tester@example.com"])
    run_git(repo_root, ["config", "core.autocrlf", "false"])
    run_git(repo_root, ["checkout", "-b", "dev-bk"])
    root_commit = commit_file(repo_root, "README.md", "# repo\n", "feat(runtime): add baseline\n\nIntent: baseline")
    source_tip = commit_file(repo_root, "runtime/workflow/example.py", "print('runtime')\n", "update: runtime")
    run_git(repo_root, ["init", "--bare", str(remote_repo)])
    run_git(repo_root, ["remote", "add", "origin", str(remote_repo)])
    run_git(repo_root, ["push", "origin", "dev-bk"])
    source_tree = run_git(repo_root, ["rev-parse", f"{source_tip}^{{tree}}"]).strip()
    new_tip = run_git(
        repo_root,
        [
            "commit-tree",
            source_tree,
            "-p",
            root_commit,
            "-m",
            "feat(runtime): runtime\n\nIntent: verified replay publication test.",
        ],
    ).strip()
    analysis = sample_analysis()
    analysis["target_branch"] = "dev-bk"
    analysis["history_rewrite_candidates"] = []
    analysis["message_repair_candidates"] = [
        {
            "id": "MESSAGE-REPAIR-001",
            "commit": source_tip,
            "approval_status": "approved",
            "proposed_commit_message": "feat(runtime): runtime\n",
            "execution_status": "verified",
            "execution_result": {
                "runtime": "built-in-rebase-replay",
                "new_tip": new_tip,
                "pushed": False,
            },
        }
    ]
    analysis["rebase_replay_executions"] = [
        {
            "dry_run": False,
            "source_tip": source_tip,
            "new_tip": new_tip,
            "before_count": 2,
            "after_count": 2,
            "tree_equal": True,
            "pushed": False,
            "remote_before": "",
            "remote_after": "",
            "worktree_path": f"work/{work_id_for_path(work_dir)}/git-worktree/dev-bk",
            "report_path": f"work/{work_id_for_path(work_dir)}/process-report/github-history-rebase-replay-execution.md",
            "mapping_path": f"work/{work_id_for_path(work_dir)}/context/github-history-rebase-replay-sha-map.tsv",
            "apply_mode": "auto-3way",
            "apply_results": [],
        }
    ]
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_ready_gate(repo_root, work_dir, mutation=True)

    result = github_knowledge_maintenance.create_publish_verified_replay(
        argparse.Namespace(
            command="publish-verified-replay",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            target_branch="dev-bk",
            remote="origin",
            expected_remote_sha=source_tip,
            new_tip="",
            execution_index=-1,
            human_check="approved",
            dry_run=False,
            repo_root=str(repo_root),
        )
    )

    remote_tip = run_git(repo_root, ["ls-remote", "--heads", "origin", "dev-bk"]).split()[0]
    updated = json.loads((work_dir / "context" / "github-knowledge-analysis.json").read_text(encoding="utf-8"))
    assert result["pushed"] is True
    assert result["remote_before"] == source_tip
    assert result["remote_after"] == new_tip
    assert remote_tip == new_tip
    assert updated["rebase_replay_executions"][0]["pushed"] is True
    assert updated["message_repair_candidates"][0]["execution_status"] == "pushed"
    assert updated["rebase_replay_publications"][0]["new_tip"] == new_tip
    assert (repo_root / result["report_path"]).exists()


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
            work_id=work_id_for_path(work_dir),
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
    assert result["worktree_path"] == f"work/{work_id_for_path(work_dir)}/git-worktree/dev-bk"
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


def test_create_sync_review_plan_and_intake_reads_ok_ng_checklist(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    analysis["history_rewrite_candidates"] = []
    analysis["github_sync_actions"].append(
        {
            "id": "SYNC-2",
            "title": "Reject stale PR comment",
            "target_type": "pr-comment",
            "target_id": "2",
            "operation": "comment",
            "approval_status": "pending",
            "reason": "stale proposal",
            "draft_command": "gh pr comment 2 --body-file stale.md",
        }
    )
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_ready_gate(repo_root, work_dir)

    result = github_knowledge_maintenance.create_sync_review_plan(
        argparse.Namespace(
            command="github-sync-review-plan",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            output="",
            repo_root=str(repo_root),
        )
    )
    plan_path = repo_root / result["sync_review_plan"]
    text = plan_path.read_text(encoding="utf-8")
    assert "| SYNC-1 | [ ] OK | [ ] NG |" in text
    assert "| SYNC-2 | [ ] OK | [ ] NG |" in text

    plan_path.write_text(
        text.replace("| SYNC-1 | [ ] OK | [ ] NG |", "| SYNC-1 | [x] OK | [ ] NG |").replace(
            "| SYNC-2 | [ ] OK | [ ] NG |",
            "| SYNC-2 | [ ] OK | [x] NG |",
        ),
        encoding="utf-8",
    )

    intake = github_knowledge_maintenance.create_sync_review_intake(
        argparse.Namespace(
            command="github-sync-review-intake",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            plan_path="",
            human_check="approved",
            allow_partial=False,
            repo_root=str(repo_root),
        )
    )

    updated = json.loads((work_dir / "context" / "github-knowledge-analysis.json").read_text(encoding="utf-8"))
    assert intake["approved_count"] == 1
    assert intake["rejected_count"] == 1
    assert updated["github_sync_actions"][0]["approval_status"] == "approved"
    assert updated["github_sync_actions"][0]["human_review_decision"] == "OK"
    assert updated["github_sync_actions"][0]["human_review_source"].endswith(".md")
    assert updated["github_sync_actions"][1]["approval_status"] == "rejected"
    assert updated["github_sync_actions"][1]["human_review_decision"] == "NG"


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
                work_id=work_id_for_path(work_dir),
                action_id="SYNC-1",
                analysis_path="",
                human_check="pending",
                dry_run=True,
                repo_root=str(repo_root),
            )
        )

    with pytest.raises(PermissionError, match="approved through github-sync-review-intake"):
        github_knowledge_maintenance.create_sync_apply(
            argparse.Namespace(
                command="github-sync-apply",
                work_id=work_id_for_path(work_dir),
                action_id="SYNC-1",
                analysis_path="",
                human_check="approved",
                dry_run=True,
                repo_root=str(repo_root),
            )
        )

    analysis["github_sync_actions"][0]["human_review_decision"] = "OK"
    analysis["github_sync_actions"][0]["human_review_source"] = "work/github/original/recent/process-report/sync-review.md"
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)

    result = github_knowledge_maintenance.create_sync_apply(
        argparse.Namespace(
            command="github-sync-apply",
            work_id=work_id_for_path(work_dir),
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
    assert result["gate_restart"]["gate"] == "github-knowledge-sync-apply-gate"
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
                work_id=work_id_for_path(work_dir),
                action_id="SYNC-1",
                analysis_path="",
                human_check="approved",
                dry_run=True,
                repo_root=str(repo_root),
            )
        )


def test_create_sync_apply_blocks_unresolved_message_repair_candidates(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis = sample_analysis()
    analysis["history_rewrite_candidates"][0]["approval_status"] = "rejected"
    analysis["github_sync_actions"][0]["approval_status"] = "approved"
    analysis["message_repair_candidates"] = [
        {
            "id": "MESSAGE-REPAIR-001",
            "commit": "abc1234",
            "current_subject": "update: runtime",
            "proposed_subject": "fix(runtime): connect message repair gate before sync",
            "proposed_commit_message": "fix(runtime): connect message repair gate before sync\n\nVerify message repair before GitHub sync.",
            "file_paths": ["runtime/workflow/github_knowledge_maintenance.py"],
            "reason": "weak semantic subject remains before GitHub sync",
            "approval_status": "approved",
            "execution_status": "pending",
        }
    ]
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    write_ready_gate(repo_root, work_dir, mutation=True)

    with pytest.raises(RuntimeError, match="blocked until message repair candidates are verified: MESSAGE-REPAIR-001"):
        github_knowledge_maintenance.create_sync_apply(
            argparse.Namespace(
                command="github-sync-apply",
                work_id=work_id_for_path(work_dir),
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
                work_id=work_id_for_path(work_dir),
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
            work_id=work_id_for_path(work_dir),
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
    assert result["gate_restart"]["gate"] == "github-knowledge-rag-candidate-gate"
    assert output_path.exists()


def test_create_rag_candidate_default_and_publish_outputs(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(work_dir / "context" / "github-knowledge-analysis.json", sample_analysis())
    write_ready_gate(repo_root, work_dir, rag=True)

    default_result = github_knowledge_maintenance.create_rag_candidate(
        argparse.Namespace(
            command="rag-candidate",
            work_id=work_id_for_path(work_dir),
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
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            topic="repo topic",
            output="",
            publish_rag=True,
            human_check="approved",
            repo_root=str(repo_root),
        )
    )

    assert default_result["published"] is False
    assert default_result["rag_candidate"].startswith(f"work/{work_id_for_path(work_dir)}/process-report/github-knowledge-rag-candidate-")
    assert default_result["work_cleanup"]["ready_for_check"] is False
    assert default_result["next_action"] == {}
    assert publish_result["published"] is True
    assert publish_result["rag_candidate"].startswith("work/db/ariadne-knowledge-platform/rag/github-knowledge/")
    assert publish_result["work_cleanup"]["ready_for_check"] is True
    assert publish_result["next_action"]["action"] == "check-work-cleanup"
    assert "work cleanup-check --work-id github/original --recursive" in publish_result["next_action"]["command"]
    assert "work cleanup-apply --work-id github/original --recursive --human-check approved" in publish_result["next_action"]["cleanup_command"]

    analysis = sample_analysis()
    analysis["history_rewrite_candidates"] = []
    analysis["message_repair_candidates"] = []
    write_json(work_dir / "context" / "github-knowledge-analysis.json", analysis)
    status_result = github_knowledge_maintenance.create_next_action(
        argparse.Namespace(
            command="next-action",
            work_id=work_id_for_path(work_dir),
            analysis_path="",
            repo_root=str(repo_root),
        )
    )

    assert status_result["next_action"]["action"] == "check-work-cleanup"
    assert status_result["status_summary"]["work_cleanup"]["ready_for_check"] is True


def test_run_dispatches_commands_and_rejects_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(github_knowledge_maintenance, "init_work", lambda args: {"command": "init"})
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_analysis_template",
        lambda args: {"command": "analysis-template"},
    )
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_artifact_integrity_report",
        lambda args: {"command": "artifact-integrity"},
    )
    monkeypatch.setattr(github_knowledge_maintenance, "create_status", lambda args: {"command": "status"})
    monkeypatch.setattr(github_knowledge_maintenance, "create_next_action", lambda args: {"command": args.command})
    monkeypatch.setattr(github_knowledge_maintenance, "create_verify_remote", lambda args: {"command": "verify-remote"})
    monkeypatch.setattr(github_knowledge_maintenance, "create_cleanup_worktree", lambda args: {"command": "cleanup-worktree"})
    monkeypatch.setattr(github_knowledge_maintenance, "create_repair_plan", lambda args: {"command": "repair-plan"})
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_detect_rebase_candidates",
        lambda args: {"command": "detect-rebase-candidates"},
    )
    monkeypatch.setattr(github_knowledge_maintenance, "create_rebase_plan", lambda args: {"command": "rebase-plan"})
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_message_repair_plan",
        lambda args: {"command": "message-repair-plan"},
    )
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_message_review_intake",
        lambda args: {"command": "message-review-intake"},
    )
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
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_publish_verified_replay",
        lambda args: {"command": "publish-verified-replay"},
    )
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_message_repair_package",
        lambda args: {"command": "message-repair-package"},
    )
    monkeypatch.setattr(github_knowledge_maintenance, "create_sync_plan", lambda args: {"command": "github-sync-plan"})
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_sync_review_plan",
        lambda args: {"command": "github-sync-review-plan"},
    )
    monkeypatch.setattr(
        github_knowledge_maintenance,
        "create_sync_review_intake",
        lambda args: {"command": "github-sync-review-intake"},
    )
    monkeypatch.setattr(github_knowledge_maintenance, "create_sync_apply", lambda args: {"command": "github-sync-apply"})
    monkeypatch.setattr(github_knowledge_maintenance, "create_rag_candidate", lambda args: {"command": "rag-candidate"})

    for command in [
        "init",
        "analysis-template",
        "artifact-integrity",
        "status",
        "next-action",
        "resume",
        "verify-remote",
        "cleanup-worktree",
        "repair-plan",
        "detect-rebase-candidates",
        "rebase-plan",
        "message-repair-plan",
        "message-review-intake",
        "rebase-apply",
        "rebase-replay-package",
        "message-repair-package",
        "rebase-replay-apply",
        "publish-verified-replay",
        "github-sync-plan",
        "github-sync-review-plan",
        "github-sync-review-intake",
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
