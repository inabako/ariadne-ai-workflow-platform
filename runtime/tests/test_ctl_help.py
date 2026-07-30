from __future__ import annotations

import json
import runpy
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

from runtime.common import registry_store
from runtime.ctl import ctl
from runtime.observability import command_event
from runtime.rag import duckdb_store


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_ctl_parser_uses_aiwfctl_program_name() -> None:
    parser = ctl.build_parser()

    assert parser.prog == "aiwfctl"
    args = parser.parse_args(["github-knowledge", "rebase-review-intake", "--work-id", "w", "--human-check", "approved"])
    assert args.github_knowledge_command == "rebase-review-intake"
    assert args.human_check == "approved"
    status_args = parser.parse_args(["github-knowledge", "status", "--work-id", "w"])
    assert status_args.github_knowledge_command == "status"
    assert parser.parse_args(["github-knowledge", "next-action", "--work-id", "w"]).github_knowledge_command == "next-action"
    assert parser.parse_args(["github-knowledge", "resume", "--work-id", "w"]).github_knowledge_command == "resume"
    verify_args = parser.parse_args(
        ["github-knowledge", "verify-remote", "--work-id", "w", "--expected-remote-sha", "abc123"]
    )
    assert verify_args.github_knowledge_command == "verify-remote"
    assert verify_args.expected_remote_sha == "abc123"
    cleanup_args = parser.parse_args(["github-knowledge", "cleanup-worktree", "--work-id", "w", "--force"])
    assert cleanup_args.github_knowledge_command == "cleanup-worktree"
    work_args = parser.parse_args(["work", "cleanup-check", "--work-id", "github/original", "--recursive"])
    assert work_args.work_command == "cleanup-check"
    assert work_args.recursive is True
    assert cleanup_args.force is True
    preflight_args = parser.parse_args(["preflight", "--profile", "github-cli", "--work-id", "w"])
    assert preflight_args.command == "preflight"
    assert preflight_args.profile == "github-cli"
    assert preflight_args.work_id == "w"
    tools_args = parser.parse_args(["tools", "bom-scan", "--paths", "docs", "--fail-on-finding"])
    assert tools_args.command == "tools"
    assert tools_args.tools_command == "bom-scan"
    assert tools_args.paths == ["docs"]
    assert tools_args.fail_on_finding is True
    release_validate_args = parser.parse_args(["release", "validate", "--expected-license", "AGPL-3.0-or-later", "--json"])
    assert release_validate_args.command == "release"
    assert release_validate_args.release_command == "validate"
    assert release_validate_args.expected_license == "AGPL-3.0-or-later"
    assert release_validate_args.json is True
    release_manifest_args = parser.parse_args(["release", "manifest", "--artifact", "LICENSE"])
    assert release_manifest_args.command == "release"
    assert release_manifest_args.release_command == "manifest"
    assert release_manifest_args.artifact == ["LICENSE"]
    publish_args = parser.parse_args(
        [
            "github-knowledge",
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
    assert publish_args.github_knowledge_command == "publish-verified-replay"
    assert publish_args.expected_remote_sha == "abc123"
    namespace = runpy.run_path(str(Path(ctl.__file__)))
    assert namespace["build_parser"]


def test_windows_script_runtime_contract() -> None:
    script = repo_root() / "runtime" / "windows-script" / "aiwf.ps1"
    wrapper = repo_root() / "runtime" / "windows-script" / "aiwf.cmd"
    tools_cmd_files = list((repo_root() / "runtime" / "tools").glob("*.cmd"))
    raw = script.read_bytes()
    text = raw.decode("utf-8")
    wrapper_text = wrapper.read_text(encoding="utf-8")
    bash_script = repo_root() / "runtime" / "posix-bash" / "aiwf.sh"
    bash_raw = bash_script.read_bytes()
    bash_text = bash_raw.decode("utf-8")

    assert not raw.startswith(b"\xef\xbb\xbf")
    assert "Set-StrictMode -Version Latest" in text
    assert "[System.Text.UTF8Encoding]::new($false)" in text
    assert "$OutputEncoding = $Utf8NoBom" in text
    assert '$env:PYTHONUTF8 = "1"' in text
    assert '$env:PYTHONIOENCODING = "utf-8"' in text
    assert "[Parameter(ValueFromRemainingArguments = $true)]" in text
    assert "Invoke-AiwfNative" in text
    assert '"ctl/ctl.py"' in text
    assert '"--project", $RuntimeRoot, "python", $CtlPath, "--repo-root", $RepoRoot' in text
    assert "powershell -NoProfile -ExecutionPolicy Bypass -File" in wrapper_text
    assert "%~dp0aiwf.ps1" in wrapper_text
    assert tools_cmd_files == []
    assert '"--project", $RuntimeRoot, "python", $CtlPath, "--repo-root", $RepoRoot, "preflight"' in text
    assert '"run", "--project", $RuntimeRoot, "pytest", "-c", $PytestConfig' in text
    assert '"tools", "spec-check"' in text
    assert '"tools", "bom-scan"' in text
    assert '"tools", "bom-strip"' in text
    assert "pytest_ut_spec_sync.py" not in text
    assert "utf8_bom.py" not in text
    assert "runtime/workflow" not in text
    assert not bash_raw.startswith(b"\xef\xbb\xbf")
    assert bash_text.startswith("#!/usr/bin/env bash")
    assert "set -Eeuo pipefail" in bash_text
    assert "Ariadne POSIX bash runtime" in bash_text
    assert "PYTHONUTF8=1" in bash_text
    assert "PYTHONIOENCODING=utf-8" in bash_text
    assert 'ctl_path="$runtime_root/ctl/ctl.py"' in bash_text
    assert 'run --project "$runtime_root" python "$ctl_path" --repo-root "$repo_root"' in bash_text
    assert 'run --project "$runtime_root" python "$ctl_path" --repo-root "$repo_root" preflight "$@"' in bash_text
    assert 'run --project "$runtime_root" pytest -c "$runtime_root/pytest.ini" "$@"' in bash_text
    assert 'tools spec-check "$@"' in bash_text
    assert 'tools bom-scan "$@"' in bash_text
    assert 'tools bom-strip "$@"' in bash_text
    assert "pytest_ut_spec_sync.py" not in bash_text
    assert "utf8_bom.py" not in bash_text
    assert "runtime/workflow" not in bash_text


def test_pytest_config_and_cache_are_runtime_scoped() -> None:
    root_config = repo_root() / "pytest.ini"
    runtime_config = repo_root() / "runtime" / "pytest.ini"
    gitignore = (repo_root() / ".gitignore").read_text(encoding="utf-8")
    text = runtime_config.read_text(encoding="utf-8")

    assert not root_config.exists()
    assert "testpaths = tests" in text
    assert "cache_dir = .pytest_cache" in text
    assert "pythonpath = .." in text
    assert "runtime/.pytest_cache/" in gitignore
    assert "\n.pytest_cache/" not in gitignore


def test_ctl_without_modifier_warns_and_does_not_show_list() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root())])

    code, output = ctl.run(args)

    assert code == 1
    assert "警告" in output
    assert "aiwfctl help list" in output
    assert "aiwfctl path shell" in output
    assert "aiwfctl knowledge search" in output
    assert "## Workflow Commands" not in output


def test_ctl_run_writes_runtime_event_log_for_each_command(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    registry = tmp_path / "runtime" / "registries"
    registry.mkdir(parents=True)
    (registry / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")

    args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "help", "list"])
    code, output = ctl.run(args)

    assert code == 0
    assert "## Workflow Commands" in output
    log_path = tmp_path / "logs" / "runtime" / "runtime-events.log"
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    started_prefix = lines[0].split(" | ", 3)
    completed_prefix = lines[1].split(" | ", 3)
    assert started_prefix[1] == completed_prefix[1]
    assert started_prefix[2] == "00001"
    assert completed_prefix[2] == "00002"
    started = json.loads(started_prefix[3])
    completed = json.loads(completed_prefix[3])
    assert started["component"] == "ctl"
    assert started["event"] == "runtime_command_started"
    assert started["command"] == "help list"
    assert started["schema_version"] == "1.0"
    assert started["level"] == "info"
    assert started["workflow"] == "help"
    assert started["phase"] == "execute"
    assert started["operation_id"] == "help:list"
    assert started["attempt"] == 1
    assert started["diagnostics"] == {
        "recoverable": False,
        "next_action": "",
        "resume_command": "",
    }
    assert "command" not in started["input"]
    assert started["input"] == {
        "json": False,
        "repo_root": str(tmp_path),
        "work_id": "",
    }
    assert completed["event"] == "runtime_command_completed"
    assert completed["level"] == "info"
    assert completed["workflow"] == "help"
    assert completed["phase"] == "execute"
    assert completed["operation_id"] == "help:list"
    assert completed["diagnostics"] == {
        "recoverable": False,
        "next_action": "",
        "resume_command": "",
    }
    assert "command" not in completed["input"]
    assert completed["output"]["exit_code"] == 0
    assert completed["output"]["reason"] == "completed"
    assert isinstance(completed["output"]["duration_ms"], int)
    assert completed["output"]["duration_ms"] >= 0


def test_runtime_diagnostics_for_blocked_command_include_next_action() -> None:
    diagnostics = command_event.runtime_diagnostics_for_result(
        "self-improvement create-feedback",
        "blocked",
        "required_argument_missing",
    )

    assert diagnostics == {
        "recoverable": True,
        "next_action": "review_command_usage",
        "resume_command": "aiwfctl self-improvement create-feedback",
    }


def test_ctl_help_without_modifier_warns_and_does_not_show_list() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help"])

    code, output = ctl.run(args)

    assert code == 1
    assert "警告" in output
    assert "list / show / search / open / markdown" in output
    assert "aiwfctl path shell" in output
    assert "## Workflow Commands" not in output


def test_ctl_warning_can_be_colored_yellow() -> None:
    output = ctl.format_root_usage_warning(color=True)

    assert "\033[33m" in output
    assert "\033[0m" in output
    assert "aiwfctl help list" in output
    assert "aiwfctl path shell" in output
    assert "aiwfctl env select web-svg" in output
    assert "aiwfctl knowledge search" in output


def test_ctl_knowledge_usage_and_search_export_context(tmp_path: Path) -> None:
    root = tmp_path
    (root / ".git").mkdir()
    (root / "runtime" / "registries").mkdir(parents=True)
    (root / "runtime" / "registries" / "workflow_help.json").write_text(
        '{"commands": [], "extensions": []}',
        encoding="utf-8",
    )
    db = root / "db" / "rag" / "knowledge.duckdb"
    source = root / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "optimized-chunks" / "knowledge.json"
    source.parent.mkdir(parents=True)
    source.write_text(
        json.dumps(
            {
                "knowledge_id": "ctl-knowledge",
                "title": "CTL Knowledge",
                "content": "aiwfctl knowledge search can find DuckDB context records.",
                "semantic_hint": "aiwfctl duckdb context",
                "metadata": {"status": "approved", "trust_level": "high", "tags": ["ctl"]},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    policy = duckdb_store.ingestion_optimizer.load_policy(
        repo_root(), "runtime/rag/policies/knowledge-ingestion-policy.json"
    )
    duckdb_store.ingest_file(root, db, source, policy)

    args = ctl.build_parser().parse_args(["--repo-root", str(root), "knowledge"])
    code, output = ctl.run(args)
    assert code == 1
    assert "Knowledge Management" in output
    assert "aiwfctl knowledge source clone" in output

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "knowledge",
            "source",
            "--path",
            "work/db/ariadne-knowledge-platform",
            "status",
        ]
    )
    code, output = ctl.run(args)
    assert code == 0
    assert "Knowledge Source Repository" in output
    assert "Action : status" in output
    assert "work/db/ariadne-knowledge-platform" in output

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "knowledge",
            "--db",
            str(db),
            "search",
            "--query",
            "DuckDB context",
            "--tag",
            "ctl",
        ]
    )
    code, output = ctl.run(args)
    assert code == 0
    assert "Knowledge Search" in output
    assert "ctl-knowledge" in output

    output_path = root / "work" / "issue-1" / "context" / "knowledge.json"
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "knowledge",
            "--db",
            str(db),
            "export-context",
            "--query",
            "DuckDB context",
            "--tag",
            "ctl",
            "--output",
            str(output_path),
            "--json",
        ]
    )
    code, output = ctl.run(args)
    assert code == 0
    assert '"artifact_type": "rag-duckdb-context-export"' in output
    assert output_path.exists()

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "knowledge",
            "--db",
            str(db),
            "rebuild",
            "--source",
            "work/db/ariadne-knowledge-platform/rag/optimized-chunks",
            "--source-repo",
            "work/db/ariadne-knowledge-platform",
            "--reset",
        ]
    )
    code, output = ctl.run(args)
    assert code == 1
    assert "Knowledge source repository is not available" in output

    (root / "work" / "db" / "ariadne-knowledge-platform" / ".git").mkdir(parents=True)
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "knowledge",
            "source",
            "--path",
            "work/db/ariadne-knowledge-platform",
            "import-local",
            "--clean",
        ]
    )
    code, output = ctl.run(args)
    assert code == 0
    assert "Action : import-local" in output
    assert (root / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "optimized-chunks" / "knowledge.json").exists()

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "knowledge",
            "--db",
            str(db),
            "rebuild",
            "--source-repo",
            "work/db/ariadne-knowledge-platform",
            "--reset",
        ]
    )
    code, output = ctl.run(args)
    assert code == 0
    assert "Knowledge Rebuild" in output
    assert "Source Repo     : work/db/ariadne-knowledge-platform" in output
    assert "Registered" in output

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "knowledge",
            "--db",
            str(db),
            "verify",
            "--query",
            "DuckDB context",
            "--output",
            "db/rag/evidence/reference-check.json",
        ]
    )
    code, output = ctl.run(args)
    assert code == 0
    assert "Knowledge Reference Check" in output
    assert "Status       : completed" in output
    assert "Manifest     : db/rag/evidence/context/context-manifest.json" in output
    assert (root / "db" / "rag" / "evidence" / "reference-check.json").exists()
    manifest = json.loads((root / "db" / "rag" / "evidence" / "context" / "context-manifest.json").read_text(encoding="utf-8"))
    assert manifest["work_id"] == "duckdb-reference-check"
    assert "rag-duckdb-reference-check" in {item["type"] for item in manifest["contexts"]}


def test_ctl_github_knowledge_sync_apply_dry_run_updates_analysis(tmp_path: Path) -> None:
    root = tmp_path
    (root / ".git").mkdir()
    work_id = "github/main/recent"
    context_dir = root / "work" / "github" / "main" / "recent" / "context"
    context_dir.mkdir(parents=True)
    gate_path = context_dir / "github-operation-gate.json"
    tool_path = context_dir / "tool-selection.json"
    analysis_path = context_dir / "github-knowledge-analysis.json"
    gate_path.write_text(json.dumps({"mutation_allowed": True, "human_check_required": True}), encoding="utf-8")
    tool_path.write_text(json.dumps({"human_check_required": True}), encoding="utf-8")
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "workflow": "github-knowledge-maintenance",
                "work_id": work_id,
                "repository": "owner/repo",
                "target_branch": "main",
                "scan_mode": ["recent"],
                "repair_mode": "apply",
                "summary": "",
                "guardrails": [],
                "metadata_sources": [],
                "knowledge_assets": [],
                "narrative_gaps": [],
                "repair_proposals": [],
                "history_rewrite_candidates": [],
                "github_sync_actions": [
                        {
                            "id": "SYNC-1",
                            "target_type": "issue",
                            "target_id": "1",
                            "operation": "comment",
                            "draft_command": "gh issue comment 1 --body-file note.md",
                            "approval_status": "approved",
                            "human_review_decision": "OK",
                            "human_review_source": "work/github/main/recent/process-report/sync-review.md",
                        }
                ],
                "knowledge_db_candidates": [],
                "rag_candidates": [],
                "open_questions": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (context_dir / "context-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "contexts": [
                    {
                        "type": "github-operation-gate",
                        "path": "work/github/main/recent/context/github-operation-gate.json",
                    },
                    {"type": "tool-selection", "path": "work/github/main/recent/context/tool-selection.json"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "github-knowledge",
            "sync-apply",
            "--work-id",
            work_id,
            "--action-id",
            "SYNC-1",
            "--human-check",
            "approved",
            "--dry-run",
            "--json",
        ]
    )
    code, output = ctl.run(args)

    assert code == 0
    assert '"action_id": "SYNC-1"' in output
    updated = json.loads(analysis_path.read_text(encoding="utf-8"))
    assert updated["github_sync_actions"][0]["execution_status"] == "dry-run"


def test_ctl_github_knowledge_rebase_package_and_apply_dry_run(tmp_path: Path) -> None:
    root = tmp_path
    (root / ".git").mkdir()
    work_id = "github/dev-bk/recent"
    context_dir = root / "work" / "github" / "dev-bk" / "recent" / "context"
    context_dir.mkdir(parents=True)
    gate_path = context_dir / "github-operation-gate.json"
    tool_path = context_dir / "tool-selection.json"
    analysis_path = context_dir / "github-knowledge-analysis.json"
    gate_path.write_text(json.dumps({"mutation_allowed": True, "human_check_required": True}), encoding="utf-8")
    tool_path.write_text(json.dumps({"human_check_required": True}), encoding="utf-8")
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "workflow": "github-knowledge-maintenance",
                "work_id": work_id,
                "repository": "owner/repo",
                "target_branch": "dev-bk",
                "scan_mode": ["recent"],
                "repair_mode": "apply",
                "summary": "",
                "guardrails": [],
                "metadata_sources": [],
                "knowledge_assets": [],
                "narrative_gaps": [],
                "repair_proposals": [],
                "history_rewrite_candidates": [
                    {
                        "id": "HISTORY-1",
                        "file_paths": ["runtime/tests/test_example.py"],
                        "suspect_commits": ["abc1234 update: test follow-up"],
                        "expected_commit": "def5678 feat(runtime): add example workflow",
                        "repair_goal": "absorb-into-existing-commit",
                        "recommended_action": "non-interactive-git-cli-rewrite",
                        "reason": "test commit leaked from semantic runtime commit",
                        "approval_status": "approved",
                        "completion_criteria": ["absorb the leaked test into the runtime commit"],
                        "rollback_plan": "git reset --hard def5678",
                        "draft_commands": [],
                        "verification_commands": ["git diff --quiet dev-bk..HEAD"],
                    }
                ],
                "github_sync_actions": [],
                "knowledge_db_candidates": [],
                "rag_candidates": [],
                "open_questions": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (context_dir / "context-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "contexts": [
                    {
                        "type": "github-operation-gate",
                        "path": "work/github/dev-bk/recent/context/github-operation-gate.json",
                    },
                    {"type": "tool-selection", "path": "work/github/dev-bk/recent/context/tool-selection.json"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    package_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "github-knowledge",
            "rebase-package",
            "--work-id",
            work_id,
            "--candidate-id",
            "HISTORY-1",
            "--apply-mode",
            "git-3way",
            "--json",
        ]
    )
    package_code, package_output = ctl.run(package_args)

    assert package_code == 0
    package_result = json.loads(package_output)
    assert package_result["rebase_replay_package"] == "work/github/dev-bk/recent/context/rebase-replay-package.json"
    package = json.loads((context_dir / "rebase-replay-package.json").read_text(encoding="utf-8"))
    assert package["absorb"] == [{"target": "def5678", "sources": ["abc1234"]}]
    assert package["apply_mode"] == "git-3way"

    apply_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "github-knowledge",
            "rebase-apply",
            "--work-id",
            work_id,
            "--human-check",
            "approved",
            "--dry-run",
            "--json",
        ]
    )
    apply_code, apply_output = ctl.run(apply_args)

    assert apply_code == 0
    apply_result = json.loads(apply_output)
    assert apply_result["dry_run"] is True
    assert apply_result["apply_mode"] == "git-3way"
    assert apply_result["worktree_path"] == "work/github/dev-bk/recent/git-worktree/dev-bk"
    updated = json.loads(analysis_path.read_text(encoding="utf-8"))
    assert updated["history_rewrite_candidates"][0]["replay_package_ref"] == (
        "work/github/dev-bk/recent/context/rebase-replay-package.json"
    )
    metrics_context_path = context_dir / "runtime-metrics.json"
    metrics_evidence_path = root / "work" / "github" / "dev-bk" / "recent" / "test-evidence" / "runtime-metrics.json"
    assert metrics_context_path.exists()
    assert metrics_evidence_path.exists()
    metrics = json.loads(metrics_context_path.read_text(encoding="utf-8"))
    assert metrics["workflow_id"] == work_id
    assert metrics["workflow_name"] == "/github-knowledge-maintenance"
    assert metrics["events"][0]["event"] == "workflow_started"
    assert metrics["events"][-1]["event"] == "workflow_completed"
    assert metrics["events"][-1]["metadata"]["ctl_command"] == "github-knowledge rebase-apply"
    manifest = json.loads((context_dir / "context-manifest.json").read_text(encoding="utf-8"))
    runtime_metrics_contexts = [item for item in manifest["contexts"] if item["type"] == "runtime-metrics"]
    assert runtime_metrics_contexts == [
        {
            "type": "runtime-metrics",
            "path": "work/github/dev-bk/recent/context/runtime-metrics.json",
            "required": False,
            "generated_by": "runtime-observability",
            "owner": "workflow",
            "schema": ".ariadne/schemas/runtime-metrics.schema.json",
            "status": "available",
            "updated_at": runtime_metrics_contexts[0]["updated_at"],
        }
    ]


def test_ctl_human_gate_check_blocks_until_approved(tmp_path: Path) -> None:
    root = tmp_path
    (root / ".git").mkdir()
    registry_dir = root / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "human_gates.json").write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "gates": [
                    {
                        "id": "close-prune",
                        "requires_human_check": True,
                        "approved_value": "approved",
                        "reason": "cleanup requires approval",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    pending_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "human-gate",
            "check",
            "--gate",
            "close-prune",
            "--human-check",
            "pending",
            "--json",
        ]
    )
    pending_code, pending_output = ctl.run(pending_args)

    assert pending_code == 2
    assert json.loads(pending_output)["status"] == "blocked"

    approved_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "human-gate",
            "check",
            "--gate",
            "close-prune",
            "--human-check",
            "approved",
            "--json",
        ]
    )
    approved_code, approved_output = ctl.run(approved_args)

    assert approved_code == 0
    assert json.loads(approved_output)["status"] == "approved"


def test_ctl_self_improvement_review_flow_uses_official_entrypoint(tmp_path: Path) -> None:
    root = tmp_path
    (root / ".git").mkdir()
    feedback_path = root / "work" / "feedback" / "docs-sync-feedback.md"
    create_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "self-improvement",
            "create-feedback",
            "--target-workflow",
            "/docs-sync",
            "--situation",
            "docs review",
            "--friction",
            "approval path unclear",
            "--output",
            str(feedback_path),
            "--json",
        ]
    )
    create_code, create_output = ctl.run(create_args)

    assert create_code == 0
    create_result = json.loads(create_output)
    assert create_result["status"] == "proposed"
    assert feedback_path.exists()

    review_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "self-improvement",
            "review-feedback",
            "--feedback",
            str(feedback_path),
            "--decision",
            "accepted",
            "--reviewer",
            "Human",
            "--reason",
            "approved for issue conversion",
            "--json",
        ]
    )
    review_code, review_output = ctl.run(review_args)

    assert review_code == 0
    review_result = json.loads(review_output)
    assert review_result["decision"] == "accepted"
    assert "## Human Check" in feedback_path.read_text(encoding="utf-8-sig")


def test_ctl_close_archive_prepare_and_prune_dry_run(tmp_path: Path) -> None:
    root = tmp_path
    (root / ".git").mkdir()
    source = root / "work" / "issue-123"
    (source / "process-report").mkdir(parents=True)
    (source / "process-report" / "summary.md").write_text("# Summary\n\nDone.\n", encoding="utf-8")

    prepare_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "close-archive",
            "prepare",
            "--work-id",
            "issue-123",
            "--no-auto-rag",
            "--json",
        ]
    )
    prepare_code, prepare_output = ctl.run(prepare_args)

    assert prepare_code == 0
    prepare_result = json.loads(prepare_output)
    assert prepare_result["status"] == "prepared"
    archive_dir = root / prepare_result["archive_dir"]
    (archive_dir / "source" / "repository").mkdir(parents=True)
    (archive_dir / "source" / "repository" / "tmp.txt").write_text("temporary\n", encoding="utf-8")

    prune_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "close-archive",
            "prune",
            "--work-id",
            "issue-123",
            "--json",
        ]
    )
    prune_code, prune_output = ctl.run(prune_args)

    assert prune_code == 0
    prune_result = json.loads(prune_output)
    assert prune_result["status"] == "dry-run"
    assert prune_result["target_count"] >= 1
    assert (archive_dir / "source" / "repository" / "tmp.txt").exists()


def test_ctl_env_select_gui_mode_returns_windows_msys2_profile() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "select", "gui-mode"])

    code, output = ctl.run(args)

    assert code == 0
    assert "Selected Environment : gui-mode" in output
    assert "Backend              : windows-msys2-gui" in output
    assert "windows-msys2-gui" in output
    assert "Workflow Context     : 未登録" in output
    assert "Initialization" in output


def test_ctl_env_select_web_svg_returns_wsl_web_profile() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "select", "web-svg", "--json"])

    code, output = ctl.run(args)

    assert code == 0
    assert '"name": "web-svg"' in output
    assert '"backend": "wsl-ubuntu-web"' in output
    assert '"id": "wsl-ubuntu-web"' in output
    assert "Node.js" in output
    assert "Playwright" in output


def test_ctl_env_select_unknown_requires_human_check() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "select", "unknown-runtime"])

    code, output = ctl.run(args)

    assert code == 2
    assert "Unknown environment : unknown-runtime" in output
    assert "Available Environments" in output
    assert "実行環境を特定できません" in output

    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "show", "unknown-runtime"])
    code, output = ctl.run(args)

    assert code == 1
    assert "Unknown environment : unknown-runtime" in output


def test_ctl_env_without_subcommand_shows_environment_management() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env"])

    code, output = ctl.run(args)

    assert code == 0
    assert "Environment Management" in output
    assert "Commands" in output
    assert "aiwfctl env list" in output
    assert "aiwfctl env show gui-mode" in output
    assert "Backend名は表示情報" in output


def test_ctl_env_list_shows_public_environments_not_raw_profile_list() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "list"])

    code, output = ctl.run(args)

    assert code == 0
    assert "Available Environments" in output
    assert "gui-mode" in output
    assert "Backend : windows-msys2-gui" in output
    assert "web-svg" in output
    assert "docker" in output


def test_ctl_env_show_uses_public_environment_name() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "show", "gui-mode"])

    code, output = ctl.run(args)

    assert code == 0
    assert "Environment : gui-mode" in output
    assert "Backend" in output
    assert "windows-msys2-gui" in output
    assert "Recommended for" in output
    assert "Required Tools" in output
    assert "Example Commands" in output
    assert "Context Output" in output
    assert "work/<work-id>/context/environment-selection.json" in output
    assert '"schema_version": "1.0"' in output


def test_ctl_env_select_tool_name_requires_human_check_with_candidate() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "select", "pyqt"])

    code, output = ctl.run(args)

    assert code == 2
    assert "Unknown environment : pyqt" in output
    assert "利用者向けEnvironment名を指定してください" in output
    assert "Available Environments" in output
    assert "gui-mode" in output


def test_ctl_env_select_writes_workflow_context(tmp_path: Path) -> None:
    root = tmp_path
    source = repo_root()
    runtime_dir = root / "runtime" / "registries"
    schema_runtime = root / "runtime" / "tools"
    windows_script_dir = root / "runtime" / "windows-script"
    runtime_dir.mkdir(parents=True)
    schema_runtime.mkdir(parents=True)
    windows_script_dir.mkdir(parents=True)
    (runtime_dir / "workflow_environment_profiles.json").write_text(
        json.dumps(ctl.load_environment_registry(source), ensure_ascii=False),
        encoding="utf-8",
    )
    (root / "runtime" / "workflow").mkdir(parents=True)
    (root / "runtime" / "workflow" / "workflow_doctor.py").write_text("", encoding="utf-8")
    (windows_script_dir / "aiwfctl.cmd").write_text("", encoding="utf-8")
    (root / "runtime" / "registries" / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")
    args = ctl.build_parser().parse_args(
        ["--repo-root", str(root), "env", "select", "gui-mode", "--work-id", "issue-123"]
    )

    code, output = ctl.run(args)

    assert code == 0
    context_path = root / "work" / "issue-123" / "context" / "environment-selection.json"
    manifest_path = root / "work" / "issue-123" / "context" / "context-manifest.json"
    assert context_path.exists()
    assert manifest_path.exists()
    assert "work/issue-123/context/environment-selection.json" in output
    assert "work/issue-123/context/context-manifest.json" in output
    data = json.loads(context_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.0"
    assert data["artifact_type"] == "environment-selection-context"
    datetime.fromisoformat(data["selected_at"])
    assert data["selected_by"] in {"dispatcher", "human", "workflow"}
    assert data["selection_mode"] in {"manual", "auto", "human-check"}
    assert data["selected_by"] == "dispatcher"
    assert data["selection_mode"] == "manual"
    assert data["environment"] == "gui-mode"
    assert data["backend"] == "windows-msys2-gui"
    assert data["work_id"] == "issue-123"
    assert data["source"]["schema"] == ".ariadne/schemas/environment-selection.schema.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["artifact_type"] == "context-manifest"
    assert manifest["architecture"] == "context-first"
    assert manifest["contexts"][0]["type"] == "environment-selection"
    assert manifest["contexts"][0]["owner"] == "dispatcher"


def test_ctl_env_select_warns_before_overwriting_different_context(tmp_path: Path) -> None:
    root = tmp_path
    source = repo_root()
    runtime_dir = root / "runtime" / "registries"
    runtime_tools = root / "runtime" / "tools"
    windows_script_dir = root / "runtime" / "windows-script"
    runtime_dir.mkdir(parents=True)
    runtime_tools.mkdir(parents=True)
    windows_script_dir.mkdir(parents=True)
    (runtime_dir / "workflow_environment_profiles.json").write_text(
        json.dumps(ctl.load_environment_registry(source), ensure_ascii=False),
        encoding="utf-8",
    )
    (root / "runtime" / "workflow").mkdir(parents=True)
    (root / "runtime" / "workflow" / "workflow_doctor.py").write_text("", encoding="utf-8")
    (windows_script_dir / "aiwfctl.cmd").write_text("", encoding="utf-8")
    (root / "runtime" / "registries" / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")
    context_path = root / "work" / "issue-123" / "context" / "environment-selection.json"
    context_path.parent.mkdir(parents=True)
    context_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "artifact_type": "environment-selection-context",
                "selected_at": "2026-07-05T00:00:00+00:00",
                "selected_by": "dispatcher",
                "selection_mode": "manual",
                "environment": "web-svg",
                "backend": "wsl-ubuntu-web",
                "reason": "previous",
                "work_id": "issue-123",
                "status": "selected",
                "human_check_required": False,
                "context_path": "work/issue-123/context/environment-selection.json",
                "source": {
                    "registry": "db/registries/registry.duckdb",
                    "schema": ".ariadne/schemas/environment-selection.schema.json",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    args = ctl.build_parser().parse_args(
        ["--repo-root", str(root), "env", "select", "gui-mode", "--work-id", "issue-123"]
    )

    code, output = ctl.run(args)

    assert code == 0
    assert "Warnings" in output
    assert "既存contextのenvironment `web-svg`" in output
    data = json.loads(context_path.read_text(encoding="utf-8"))
    assert data["environment"] == "gui-mode"
    assert data["backend"] == "windows-msys2-gui"
    assert data["warnings"]


def test_ctl_help_list_contains_workflow_commands() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "list"])

    code, output = ctl.run(args)

    assert code == 0
    assert "/requirement-discovery" in output
    assert "/corrective-action-fix" in output
    assert "必須" in output
    assert " / 必須:" not in output
    assert "\n  概要:" in output
    assert "\n  前提:\n    - " in output
    assert all(" / " not in line for line in output.splitlines() if line.startswith("  前提:"))
    assert "\n  必須:" in output
    assert "\n  docs:\n    - docs/workflows/requirement-discovery.md" in output
    assert "docs/workflows/corrective-action-fix.md" in output
    assert "## Workflow Extensions" in output
    assert "gac-uac-gui-mode" in output
    assert "web-svg-layout-mode" in output
    assert "mcp-server-group-implementation" in output
    assert "docs/workflows/gui-mode.md" in output
    assert "docs/workflows/mcp-server-group-implementation.md" in output


def test_ctl_help_show_includes_arguments_and_details() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/docs-sync"])

    code, output = ctl.run(args)

    assert code == 0
    assert "## /docs-sync" in output
    assert "`repository`" in output
    assert "`branch`" in output
    assert "前提条件" in output
    assert "処理の詳細" in output


def test_corrective_action_fix_help_declares_report_source() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/corrective-action-fix"])

    code, output = ctl.run(args)

    assert code == 0
    assert "/corrective-action-report" in output
    assert "`report`" in output
    assert "| `report` | no |" in output
    assert "未指定の場合、このflow内でCorrective Action Reportを作成する" in output


def test_vscode_environment_help_declares_repo_local_tools_path() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/vscode-environment"])

    code, output = ctl.run(args)

    assert code == 0
    assert "self-provision mode" in output
    assert "target-workspace mode" in output
    assert "custom-design mode" in output
    assert "runtime/windows-script" in output
    assert "terminal.integrated.env.windows.Path" in output
    assert "runtime-context.json" in output


def test_realtime_iac_help_declares_docker_context_gate() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/realtime-iac"])

    code, output = ctl.run(args)

    assert code == 0
    assert "aiwfctl env select docker" in output
    assert "environment-selection.environment" in output


def test_ariadne_new_system_iac_help_declares_execution_plan_handoff() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/ariadne-new-system-iac"])

    code, output = ctl.run(args)

    assert code == 0
    assert "execution-plan.json" in output
    assert "realtime-iac-handoff.json" in output
    assert "iac_handoff_context.py" in output


def test_ctl_context_init_creates_phase3_contexts(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "/docs-sync",
                        "workflow": "docs-sync",
                        "overview": "docs only sync",
                        "aliases": [],
                    }
                ],
                "extensions": [],
            }
        ),
        encoding="utf-8",
    )
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "context",
            "init",
            "--work-id",
            "issue-9001",
            "--workflow",
            "/docs-sync",
            "--tool",
            "gh:read-only:GitHub metadata collection",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    assert "workflow-selection" in output
    assert "tool-selection" in output
    assert (tmp_path / "work" / "issue-9001" / "context" / "workflow-selection.json").exists()
    assert (tmp_path / "work" / "issue-9001" / "context" / "tool-selection.json").exists()


def test_ctl_context_show_and_require_use_context_first_runtime(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    work_dir = tmp_path / "work" / "issue-9002"
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "context",
            "show",
            "--work-dir",
            "work/issue-9002",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    show_result = json.loads(output)
    assert show_result["status"] == "missing"
    assert show_result["manifest_path"] == "work/issue-9002/context/context-manifest.json"

    require_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "context",
            "require",
            "--work-dir",
            str(work_dir),
            "--context",
            "environment-selection",
            "--json",
        ]
    )
    require_code, require_output = ctl.run(require_args)

    assert require_code == 2
    require_result = json.loads(require_output)
    assert require_result["status"] == "human-check-required"
    assert require_result["missing"] == ["environment-selection"]


def test_ctl_doctor_runs_workflow_doctor(monkeypatch, tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")
    (registry_dir / "workflow_environment_profiles.json").write_text(
        '{"environments": [], "profiles": [], "mappings": []}',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        ctl.workflow_doctor,
        "run",
        lambda args: {"status": "pass", "warning_count": 0, "warnings": []},
    )

    args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "doctor"])
    code, output = ctl.run(args)

    assert code == 0
    assert "Workflow Doctor" in output
    assert "Warning Count : 0" in output

    args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "doctor", "--json"])
    code, output = ctl.run(args)

    assert code == 0
    assert '"status": "pass"' in output


def test_defensive_specimen_ctl_doctor_formats_warning_paths(monkeypatch, tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")
    (registry_dir / "workflow_environment_profiles.json").write_text(
        '{"environments": [], "profiles": [], "mappings": []}',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        ctl.workflow_doctor,
        "run",
        lambda args: {
            "status": "warning",
            "warning_count": 1,
            "warnings": [
                {
                    "id": "defensive-specimen",
                    "message": "rare warning specimen",
                    "paths": [f"path-{index}" for index in range(12)],
                }
            ],
        },
    )

    args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "doctor"])
    code, output = ctl.run(args)

    assert code == 0
    assert "Warnings" in output
    assert "defensive-specimen" in output
    assert "rare warning specimen" in output
    assert "path-0" in output
    assert "path-9" in output
    assert "path-10" not in output


def test_ctl_help_search_finds_svg_gui_workflows() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "search", "svg", "gui"])

    code, output = ctl.run(args)

    assert code == 0
    assert "Workflow Help Search Candidates" in output
    assert "/ariadne-new-system" in output
    assert "/corrective-action-fix" in output
    assert "gac-uac-gui-mode" in output
    assert "show: aiwfctl help show /ariadne-new-system" in output
    assert "show: aiwfctl help show gac-uac-gui-mode" in output
    assert "## Details" not in output


def test_ctl_help_show_includes_svg_extension_details() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "gui-mode"])

    code, output = ctl.run(args)

    assert code == 0
    assert "## gac-uac-gui-mode" in output
    assert "workflow extension" in output
    assert "前提条件" in output
    assert "SYS_" in output
    assert "FEAT_" in output
    assert "FIX_" in output
    assert "standalone command: `false`" in output


def test_ctl_help_show_includes_mcp_group_extension_details() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "mcp-group"])

    code, output = ctl.run(args)

    assert code == 0
    assert "## mcp-server-group-implementation" in output
    assert "workflow extension" in output
    assert "standalone command: `true`" in output
    assert "aiwfctl mcp-group analyze --work-id <work-id>" in output
    assert "runtime/workflow/mcp_server_group.py" in output


def test_ctl_help_markdown_writes_searchable_file(tmp_path: Path) -> None:
    output_path = tmp_path / "help.md"
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root()),
            "help",
            "markdown",
            "--output",
            str(output_path),
            "--query",
            "rag",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    assert "wrote:" in output
    text = output_path.read_text(encoding="utf-8")
    assert "# AI Workflow Help" in text
    assert "/rag-load" in text


def test_workflow_help_registry_referenced_files_exist() -> None:
    root = repo_root()
    registry = ctl.load_registry(root)

    for command in registry["commands"]:
        assert command.get("prerequisites"), f"{command['command']} missing prerequisites"
        for key in ["skill_path", "prompt_path"]:
            value = command.get(key, "")
            assert value, f"{command['command']} missing {key}"
            assert (root / value).exists(), f"{command['command']} references missing {value}"
        for value in command.get("docs", []):
            assert (root / value).exists(), f"{command['command']} references missing {value}"
        for value in command.get("related_runtime", []):
            assert (root / value).exists(), f"{command['command']} references missing {value}"
    for extension in registry["extensions"]:
        assert extension.get("prerequisites"), f"{extension['name']} missing prerequisites"
        for value in extension.get("docs", []):
            assert (root / value).exists(), f"{extension['name']} references missing {value}"
        for value in extension.get("related_runtime", []):
            assert (root / value).exists(), f"{extension['name']} references missing {value}"


def test_workflow_help_search_uses_intent_terms() -> None:
    root = repo_root()
    registry = ctl.load_registry(root)

    commands = ctl.search_commands(registry, ["新しく作る"])

    assert commands
    assert commands[0]["command"] == "/ariadne-new-system"

    args = ctl.build_parser().parse_args(["--repo-root", str(root), "help", "search", "新しく作る"])
    code, output = ctl.run(args)

    assert code == 0
    assert "Workflow Help Search Candidates" in output
    assert "1. /ariadne-new-system" in output
    assert "show: aiwfctl help show /ariadne-new-system" in output
    assert "## Details" not in output


def test_workflow_help_uses_terms_from_separated_json(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "commands": [
                    {
                        "id": "alpha",
                        "command": "/alpha",
                        "workflow": "alpha",
                        "skill": "alpha",
                        "overview": "alpha overview",
                        "prerequisites": [],
                        "arguments": [],
                        "details": [],
                        "examples": [],
                    }
                ],
                "extensions": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (registry_dir / "search_terms.json").write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "terms": [
                    {
                        "id": "11111111-1111-4111-8111-111111111111",
                        "owner_registry": "workflow_help",
                        "owner_type": "command",
                        "owner_id": "alpha",
                        "term": "入口整理",
                        "locale": "ja",
                        "kind": "intent",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    registry = ctl.load_registry(tmp_path)
    matches = ctl.search_commands(registry, ["入口整理"])

    assert matches[0]["command"] == "/alpha"
    UUID(matches[0]["_search_terms"][0]["id"])
    assert matches[0]["_search_terms"][0]["owner_id"] == "alpha"


def write_registry_source(source_dir: Path) -> None:
    source_dir.mkdir(parents=True)
    (source_dir / "workflow_help.json").write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "commands": [
                    {
                        "id": "alpha",
                        "command": "/alpha",
                        "workflow": "alpha",
                        "skill": "alpha",
                        "overview": "alpha overview",
                        "prerequisites": [],
                        "arguments": [],
                        "details": [],
                        "examples": [],
                    }
                ],
                "extensions": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (source_dir / "search_terms.json").write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "terms": [
                    {
                        "id": "11111111-1111-4111-8111-111111111111",
                        "owner_registry": "workflow_help",
                        "owner_type": "command",
                        "owner_id": "alpha",
                        "term": "entrypoint maintenance",
                        "locale": "en",
                        "kind": "intent",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    for name, payload in {
        "tool_candidates.json": {"registry_version": "1.0", "tools": []},
        "human_gates.json": {"registry_version": "1.0", "gates": []},
        "workflow_environment_profiles.json": {
            "registry_version": "1.0",
            "environments": [{"name": "local", "backend": "windows-powershell", "purpose": "local runtime"}],
            "profiles": [{"id": "windows-powershell", "environment": "local"}],
            "mappings": [],
        },
    }.items():
        (source_dir / name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_registry_store_builds_search_terms_table_with_owner_id(tmp_path: Path) -> None:
    source_dir = tmp_path / "work" / "db" / "ariadne-knowledge-platform" / "registries"
    source_dir.mkdir(parents=True)
    (source_dir / "workflow_help.json").write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "commands": [
                    {
                        "id": "alpha",
                        "command": "/alpha",
                        "workflow": "alpha",
                        "skill": "alpha",
                        "overview": "alpha overview",
                        "prerequisites": [],
                        "arguments": [],
                        "details": [],
                        "examples": [],
                    }
                ],
                "extensions": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (source_dir / "search_terms.json").write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "terms": [
                    {
                        "id": "11111111-1111-4111-8111-111111111111",
                        "owner_registry": "workflow_help",
                        "owner_type": "command",
                        "owner_id": "alpha",
                        "term": "入口整理",
                        "locale": "ja",
                        "kind": "intent",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    for name, payload in {
        "tool_candidates.json": {"registry_version": "1.0", "tools": []},
        "human_gates.json": {"registry_version": "1.0", "gates": []},
        "workflow_environment_profiles.json": {
            "registry_version": "1.0",
            "environments": [],
            "profiles": [],
            "mappings": [],
        },
    }.items():
        (source_dir / name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    db_path = tmp_path / "db" / "registries" / "registry.duckdb"
    result = registry_store.build_registry_read_model(tmp_path, source_dir, db_path)

    assert "search_terms" in result["tables"]
    assert result["counts"]["search_terms"] == 1
    with registry_store.connect(db_path, read_only=True) as conn:
        command_id = conn.execute("SELECT id FROM workflow_help_commands").fetchone()[0]
        term_id, owner_id = conn.execute("SELECT id, owner_id FROM search_terms").fetchone()
    assert command_id == "alpha"
    UUID(term_id)
    assert owner_id == command_id

    registry = registry_store.load_workflow_help(tmp_path)
    matches = ctl.search_commands(registry, ["入口整理"])
    assert matches[0]["command"] == "/alpha"


def test_registry_store_ensure_builds_missing_duckdb_from_source_backup(tmp_path: Path) -> None:
    source_dir = tmp_path / "work" / "db" / "ariadne-knowledge-platform" / "registries"
    db_path = tmp_path / "db" / "registries" / "registry.duckdb"
    write_registry_source(source_dir)

    result = registry_store.ensure_registry_read_model(tmp_path, source_dir, db_path)

    assert result["action"] == "built"
    assert db_path.exists()
    assert result["counts"]["workflow_help_commands"] == 1
    assert result["counts"]["workflow_environments"] == 1

    existing = registry_store.ensure_registry_read_model(tmp_path, source_dir, db_path)

    assert existing["action"] == "existing"
    assert existing["counts"]["workflow_help_commands"] == 1


def test_registry_load_auto_builds_missing_duckdb_from_default_source_backup(tmp_path: Path) -> None:
    source_dir = tmp_path / "work" / "db" / "ariadne-knowledge-platform" / "registries"
    db_path = tmp_path / "db" / "registries" / "registry.duckdb"
    write_registry_source(source_dir)

    registry = registry_store.load_workflow_help(tmp_path)
    environment_registry = registry_store.load_environment_profiles(tmp_path)

    assert db_path.exists()
    assert registry["commands"][0]["command"] == "/alpha"
    assert registry["commands"][0]["_search_terms"][0]["term"] == "entrypoint maintenance"
    assert environment_registry["environments"][0]["name"] == "local"


def test_registry_store_ensure_skips_when_source_backup_is_incomplete(tmp_path: Path) -> None:
    source_dir = tmp_path / "work" / "db" / "ariadne-knowledge-platform" / "registries"
    source_dir.mkdir(parents=True)
    (source_dir / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")

    result = registry_store.ensure_registry_read_model(tmp_path)

    assert result["action"] == "missing-source"
    assert result["status"] == "skipped"
    assert "tool_candidates.json" in result["missing_sources"][0]
    assert not (tmp_path / "db" / "registries" / "registry.duckdb").exists()


def test_workflow_help_search_terms_cover_all_prompt_commands() -> None:
    root = repo_root()
    registry = ctl.load_registry(root)
    missing: list[str] = []

    for command in registry["commands"]:
        terms = command.get("_search_terms", [])
        if not terms:
            missing.append(command["command"])
            continue
        for term in terms:
            UUID(term["id"])
            assert term["owner_id"] == command["id"]
            assert term["owner_type"] == "command"

    assert not missing


def test_environment_profile_registry_referenced_docs_exist() -> None:
    root = repo_root()
    registry = ctl.load_environment_registry(root)

    assert registry["environments"], "public environment registry is empty"
    for environment in registry["environments"]:
        assert environment.get("name"), "environment missing name"
        assert environment.get("backend"), f"{environment['name']} missing backend"
        ctl.profile_by_id(registry, environment["backend"])
    assert registry["profiles"], "environment profile registry is empty"
    for profile in registry["profiles"]:
        assert profile.get("id"), "environment profile missing id"
        for value in profile.get("docs", []):
            assert (root / value).exists(), f"{profile['id']} references missing {value}"
    for mapping in registry["mappings"]:
        assert mapping.get("profiles"), f"{mapping['subject']} missing profiles"
        for profile_id in mapping["profiles"]:
            ctl.profile_by_id(registry, profile_id)
        for value in mapping.get("docs", []):
            assert (root / value).exists(), f"{mapping['subject']} references missing {value}"


def test_ctl_registry_and_search_helper_edge_cases(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text("[]", encoding="utf-8")
    (registry_dir / "workflow_environment_profiles.json").write_text("[]", encoding="utf-8")

    try:
        ctl.load_registry(tmp_path)
    except ValueError as exc:
        assert "workflow help registry" in str(exc)
    else:
        raise AssertionError("non-object workflow help registry should fail")

    try:
        ctl.load_environment_registry(tmp_path)
    except ValueError as exc:
        assert "environment profiles registry" in str(exc)
    else:
        raise AssertionError("non-object environment profile registry should fail")

    registry = {
        "commands": [{"command": "/b"}, {"command": "/a", "aliases": ["/alias-a"], "overview": "alpha"}],
        "extensions": [{"name": "z-ext"}, {"name": "a-ext", "aliases": ["alias-ext"], "overview": "alpha"}],
    }

    assert ctl.normalize_command("docs-sync") == "/docs-sync"
    assert ctl.normalize_command(" /already ") == "/already"
    assert ctl.find_command(registry, "alias-a")["command"] == "/a"
    assert ctl.find_help_item(registry, "alias-ext")[0] == "extension"
    assert [item["command"] for item in ctl.search_commands(registry, [" "])] == ["/a", "/b"]
    assert [item["name"] for item in ctl.search_extensions(registry, [" "])] == ["a-ext", "z-ext"]
    assert ctl.profile_key({"id": "B"}) == "b"

    try:
        ctl.find_extension(registry, "missing")
    except KeyError as exc:
        assert "Unknown workflow extension" in str(exc)
    else:
        raise AssertionError("unknown extension should fail")


def test_ctl_environment_selection_mapping_branches() -> None:
    registry = {
        "environments": [
            {"name": "env-a", "backend": "p1", "purpose": "A"},
            {"name": "env-b", "backend": "p2", "purpose": "B"},
        ],
        "profiles": [
            {"id": "p1", "aliases": ["profile-a"], "docs": ["docs/a.md"], "primary_tools": ["Git"]},
            {"id": "p2", "aliases": [], "docs": ["docs/b.md"], "primary_tools": ["Docker"]},
        ],
        "mappings": [
            {"subject_type": "command", "subject": "/mapped", "profiles": ["p1"], "selection_reason": "mapped"},
            {"subject_type": "keyword", "subject": "gui pyqt", "profiles": ["p1"], "selection_reason": "keyword-a"},
            {"subject_type": "keyword", "subject": "gui web", "profiles": ["p2"], "selection_reason": "keyword-b"},
            {"subject_type": "unknown", "subject": "never", "profiles": ["p1"]},
        ],
    }

    assert ctl.find_public_environment_by_backend(registry, "missing") is None
    assert ctl.find_environment_profile(registry, "profile-a")["id"] == "p1"
    assert not ctl.environment_mapping_matches({"subject_type": "unknown", "subject": "x"}, "x")

    mapped = ctl.select_environment(registry, "/mapped")
    assert mapped["status"] == "selected"
    assert mapped["environment"]["name"] == "env-a"
    assert mapped["profiles"][0]["id"] == "p1"

    keyword = ctl.select_environment(registry, "please use gui")
    assert keyword["status"] == "human-check-required"
    assert {item["name"] for item in keyword["candidate_environments"]} == {"env-a", "env-b"}

    try:
        ctl.profile_by_id(registry, "missing")
    except KeyError as exc:
        assert "Unknown environment profile id" in str(exc)
    else:
        raise AssertionError("unknown profile id should fail")


def test_ctl_environment_formatting_and_context_warning_helpers(tmp_path: Path) -> None:
    profile = {
        "id": "p1",
        "title": "Profile One",
        "environment": "Windows",
        "shell": "PowerShell",
        "os": "Windows",
        "summary": "summary",
        "primary_tools": ["Git", "Python"],
        "run_command": "run",
        "preflight_profile": "",
        "applies_when": [],
        "verification": [],
        "human_check_required_when": [],
        "docs": [],
    }
    formatted_profile = ctl.format_environment_profile(profile)
    assert "Profile One" in formatted_profile
    assert "Git, Python" in formatted_profile

    human_check = ctl.format_environment_human_check(
        {
            "target": "gui",
            "status": "human-check-required",
            "human_check_reasons": ["choose explicitly"],
            "candidate_environments": [{"name": "gui-mode", "backend": "windows", "purpose": "GUI"}],
        }
    )
    assert "Environment Human Check Required" in human_check
    assert "gui-mode" in human_check
    assert "Candidate Environments" not in ctl.format_environment_human_check(
        {
            "target": "unknown",
            "status": "human-check-required",
            "human_check_reasons": ["choose explicitly"],
            "candidate_environments": [],
        }
    )

    context = {
        "work_id": "issue-2",
        "environment": "gui-mode",
        "backend": "windows-msys2-gui",
    }
    assert not ctl.environment_context_warnings({}, context)
    assert ctl.environment_context_warnings({"work_id": "issue-2"}, context) == []
    assert ctl.environment_context_warnings("broken", context)
    warnings = ctl.environment_context_warnings(
        {"work_id": "issue-1", "environment": "web-svg", "backend": "wsl-ubuntu-web"},
        context,
    )
    assert len(warnings) == 3

    record = {
        "status": "selected",
        "target": "gui-mode",
        "environment": {"name": "gui-mode", "backend": "windows-msys2-gui", "recommended_for": []},
        "mapping": {"selection_reason": "manual"},
        "profiles": [profile],
        "human_check_required": False,
        "created_at": "2026-07-07T00:00:00+00:00",
    }
    context_record = ctl.environment_context_record(
        record,
        work_id="issue-7",
        selected_by="human",
        selection_mode="auto",
    )
    assert context_record["selected_by"] == "human"
    assert context_record["selection_mode"] == "auto"
    assert context_record["context_path"] == "work/issue-7/context/environment-selection.json"

    output_json = tmp_path / "environment-selection.json"
    output_md = tmp_path / "environment-selection.md"
    assert ctl.write_environment_selection(tmp_path, record.copy(), output=str(output_json)) == [
        "environment-selection.json"
    ]
    assert json.loads(output_json.read_text(encoding="utf-8"))["target"] == "gui-mode"
    assert ctl.write_environment_selection(tmp_path, record.copy(), output=str(output_md)) == [
        "environment-selection.md"
    ]
    assert "Selected Environment" in output_md.read_text(encoding="utf-8")

    registry = {
        "profiles": [
            {"id": "p1", "primary_tools": []},
            {"id": "p2", "primary_tools": []},
        ],
        "environments": [
            {"name": "env-one", "backend": "p1", "purpose": "one"},
            {"name": "env-two", "backend": "p2", "purpose": "two"},
        ],
        "mappings": [
            {"subject_type": "command", "subject": "build", "profiles": ["p1"], "selection_reason": "one"},
            {"subject_type": "command", "subject": "build", "profiles": ["p2"], "selection_reason": "two"},
        ],
    }
    try:
        ctl.find_environment_profile(registry, "missing")
    except KeyError as exc:
        assert "Unknown environment profile" in str(exc)
    else:
        raise AssertionError("unknown profile should fail")

    ambiguous = ctl.select_environment(registry, "build")
    assert ambiguous["status"] == "human-check-required"
    assert len(ambiguous["candidate_environments"]) == 2
    assert "Candidate Environments" in ctl.format_environment_human_check(ambiguous)
    assert "Human Check" in ctl.format_unknown_environment(registry, "build", ambiguous)

    profile_backend = ctl.format_environment_selection(
        {
            "status": "selected",
            "target": "manual",
            "environment": {},
            "mapping": {},
            "profiles": [{"id": "p1"}],
            "human_check_required": False,
            "workflow_context": {},
            "initialization": {},
        }
    )
    assert "Backend              : p1" in profile_backend
    assert "Environment Human Check Required" in ctl.format_environment_selection(
        {
            "status": "human-check-required",
            "target": "manual",
            "human_check_required": True,
            "human_check_reasons": ["needs human"],
            "candidate_environments": [],
        }
    )


def test_ctl_help_formatting_empty_lists_and_open_search_paths(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    registry = {
        "description": "minimal help",
        "commands": [
            {
                "command": "/alpha",
                "workflow": "alpha",
                "overview": "alpha overview",
                "arguments": [],
                "docs": [],
                "examples": [],
                "details": [],
                "prerequisites": [],
                "related_runtime": [],
            }
        ],
        "extensions": [],
    }
    (registry_dir / "workflow_help.json").write_text(json.dumps(registry), encoding="utf-8")

    assert "なし" in ctl.format_arg_table("empty", [])
    assert ctl.format_prerequisites_for_list([])
    assert ctl.format_docs_for_list([])

    open_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "help", "open", "--query", "alpha"])
    code, output = ctl.run(open_args)
    assert code == 0
    assert "# AI Workflow Help" in output
    assert "/alpha" in output

    markdown_args = ctl.build_parser().parse_args(
        ["--repo-root", str(tmp_path), "help", "markdown", "--output", "work/help/out.md"]
    )
    code, output = ctl.run(markdown_args)
    assert code == 0
    assert "wrote: work/help/out.md" in output
    assert (tmp_path / "work" / "help" / "out.md").exists()

    search_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "help", "search", "missing"])
    code, output = ctl.run(search_args)
    assert code == 1
    assert "workflow help" in output


def test_ctl_color_mode_and_main_output(monkeypatch, capsys) -> None:
    class TtyStream:
        def isatty(self) -> bool:
            return True

    class NonTtyStream:
        def isatty(self) -> bool:
            return False

    monkeypatch.setenv("AIWFCTL_COLOR", "always")
    assert ctl.should_use_color(NonTtyStream())
    monkeypatch.setenv("AIWFCTL_COLOR", "never")
    assert not ctl.should_use_color(TtyStream())
    monkeypatch.delenv("AIWFCTL_COLOR", raising=False)
    monkeypatch.setenv("NO_COLOR", "1")
    assert not ctl.should_use_color(TtyStream())
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert ctl.should_use_color(TtyStream())
    assert not ctl.should_use_color(NonTtyStream())

    code = ctl.main(["--repo-root", str(repo_root()), "help", "search", "svg"])
    captured = capsys.readouterr()
    assert code == 0
    assert "Workflow Help Search Candidates" in captured.out


def test_ctl_run_manual_error_and_json_branches(monkeypatch, tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(
        json.dumps({"commands": [], "extensions": []}),
        encoding="utf-8",
    )
    (registry_dir / "workflow_environment_profiles.json").write_text(
        json.dumps({"environments": [], "profiles": [], "mappings": []}),
        encoding="utf-8",
    )

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="unknown"))
    assert code == 1
    assert "Unknown command: unknown" in output

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="env", env_command="unknown"))
    assert code == 1
    assert "Unknown env command: unknown" in output

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="context", context_command=None))
    assert code == 1
    assert "Context Management" in output

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="context", context_command="unknown"))
    assert code == 1
    assert "Unknown context command: unknown" in output

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="help", help_command="unknown"))
    assert code == 1
    assert "Unknown help command: unknown" in output

    monkeypatch.setattr(
        ctl.dispatcher_context,
        "run_init",
        lambda args: {
            "status": "human-check-required",
            "work_id": "issue-1",
            "workflow": "/docs-sync",
            "manifest_path": "work/issue-1/context/context-manifest.json",
            "contexts": ["workflow-selection"],
            "written": ["work/issue-1/context/workflow-selection.json"],
        },
    )
    code, output = ctl.run(
        SimpleNamespace(repo_root=str(tmp_path), command="context", context_command="init", json=True)
    )
    assert code == 2
    assert '"status": "human-check-required"' in output

    monkeypatch.setattr(
        ctl.dispatcher_context,
        "run_init",
        lambda args: {
            "status": "ready",
            "work_id": "issue-2",
            "workflow": "/docs-sync",
            "manifest_path": "work/issue-2/context/context-manifest.json",
            "contexts": ["workflow-selection"],
            "written": [],
        },
    )
    code, output = ctl.run(
        SimpleNamespace(repo_root=str(tmp_path), command="context", context_command="init", json=False)
    )
    assert code == 0
    assert "Written Artifacts" not in output

    code, output = ctl.run(
        SimpleNamespace(repo_root=str(tmp_path), command="help", help_command="list")
    )
    assert code == 0
    assert "## Workflow Extensions" not in output


def test_ctl_work_cleanup_check_and_apply_requires_absorbed_knowledge(tmp_path: Path) -> None:
    root = tmp_path
    work_dir = root / "work" / "github" / "original" / "recent"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    (context_dir / "github-knowledge-analysis.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "workflow": "github-knowledge-maintenance",
                "work_id": "github/original/recent",
                "repository": "owner/repo",
            }
        ),
        encoding="utf-8",
    )

    blocked_args = ctl.build_parser().parse_args(
        ["--repo-root", str(root), "work", "cleanup-check", "--work-id", "github/original", "--recursive", "--json"]
    )
    blocked_code, blocked_output = ctl.run(blocked_args)

    assert blocked_code == 0
    blocked = json.loads(blocked_output)
    assert blocked["status"] == "blocked"
    assert "long-lived knowledge artifact is not confirmed" in blocked["blockers"]

    metrics_work = root / "work" / "github" / "metrics-only" / "recent"
    (metrics_work / "context").mkdir(parents=True)
    (metrics_work / "test-evidence").mkdir(parents=True)
    (metrics_work / "context" / "runtime-metrics.json").write_text(
        json.dumps({"artifact_type": "runtime-metrics", "workflow_id": "github/metrics-only/recent"}),
        encoding="utf-8",
    )
    (metrics_work / "test-evidence" / "runtime-metrics.json").write_text(
        json.dumps({"artifact_type": "runtime-metrics", "workflow_id": "github/metrics-only/recent"}),
        encoding="utf-8",
    )
    (metrics_work / "context" / "context-manifest.json").write_text(
        json.dumps(
            {
                "contexts": [
                    {
                        "type": "runtime-metrics",
                        "path": "work/github/metrics-only/recent/context/runtime-metrics.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    metrics_args = ctl.build_parser().parse_args(
        ["--repo-root", str(root), "work", "cleanup-check", "--work-id", "github/metrics-only", "--recursive", "--json"]
    )
    metrics_code, metrics_output = ctl.run(metrics_args)

    assert metrics_code == 0
    metrics = json.loads(metrics_output)
    assert metrics["status"] == "ready"
    assert metrics["checks"][0]["workflow"] == "metrics-only-empty-work"
    assert metrics["checks"][0]["empty_runtime_metrics_only"] is True

    protected_args = ctl.build_parser().parse_args(
        ["--repo-root", str(root), "work", "cleanup-check", "--work-id", "github", "--recursive", "--json"]
    )
    protected_code, protected_output = ctl.run(protected_args)

    assert protected_code == 1
    assert "protected work scope" in protected_output

    rag_source = root / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "github-knowledge" / "source.md"
    rag_source.parent.mkdir(parents=True)
    rag_source.write_text("# absorbed\n", encoding="utf-8")
    (context_dir / "artifact-index.json").write_text(
        json.dumps(
            {
                "artifacts": [
                    {
                        "id": "GITHUB-KNOWLEDGE-RAG-CANDIDATE",
                        "path": "work/db/ariadne-knowledge-platform/rag/github-knowledge/source.md",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    ready_args = ctl.build_parser().parse_args(
        ["--repo-root", str(root), "work", "cleanup-check", "--work-id", "github/original", "--recursive", "--json"]
    )
    ready_code, ready_output = ctl.run(ready_args)

    assert ready_code == 0
    ready = json.loads(ready_output)
    assert ready["status"] == "ready"
    assert ready["apply_command"].endswith("--human-check approved")

    required_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "work",
            "cleanup-check",
            "--work-id",
            "github/original",
            "--recursive",
            "--required-artifact",
            "work/db/ariadne-knowledge-platform/rag/github-knowledge/source.md",
            "--json",
        ]
    )
    required_code, required_output = ctl.run(required_args)

    assert required_code == 0
    required = json.loads(required_output)
    assert (
        "--required-artifact work/db/ariadne-knowledge-platform/rag/github-knowledge/source.md"
        in required["apply_command"]
    )

    pending_args = ctl.build_parser().parse_args(
        ["--repo-root", str(root), "work", "cleanup-apply", "--work-id", "github/original", "--recursive", "--json"]
    )
    pending_code, pending_output = ctl.run(pending_args)

    assert pending_code == 1
    assert "requires --human-check approved" in pending_output

    apply_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(root),
            "work",
            "cleanup-apply",
            "--work-id",
            "github/original",
            "--recursive",
            "--human-check",
            "approved",
            "--json",
        ]
    )
    apply_code, apply_output = ctl.run(apply_args)

    assert apply_code == 0
    applied = json.loads(apply_output)
    assert applied["status"] == "removed"
    assert applied["exists_after"] is False
    assert not (root / "work" / "github" / "original").exists()
