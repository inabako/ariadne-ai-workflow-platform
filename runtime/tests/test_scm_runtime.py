from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pytest

from runtime.scm import bootstrap_repository, commit_changes, create_issue_branch, prepare_repository, push_branch, scm_utils


def make_work_repo(tmp_path: Path, work_id: str = "issue-1") -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    work_dir = repo / "work" / work_id
    (repo / ".git").mkdir(parents=True)
    (work_dir / "context").mkdir(parents=True)
    (work_dir / "process-report").mkdir(parents=True)
    return repo, work_dir


def test_require_success_raises_with_stderr_detail() -> None:
    result = subprocess.CompletedProcess(["git", "status"], 128, stdout="", stderr="fatal: not a git repo")

    with pytest.raises(RuntimeError, match="git status failed: fatal: not a git repo"):
        scm_utils.require_success(result, "git status")


def test_github_token_git_env_sets_non_interactive_auth() -> None:
    with scm_utils.github_token_git_env("secret-token") as env:
        assert env is not None
        assert env["GITHUB_TOKEN"] == "secret-token"
        assert env["GIT_TERMINAL_PROMPT"] == "0"
        assert env["GCM_INTERACTIVE"] == "Never"
        assert "GIT_ASKPASS" in env


def test_prepare_repository_dry_run_writes_scm_state_and_manifest(tmp_path: Path) -> None:
    repo, _ = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="issue-1",
        repository="inabako/example.git",
        target_branch="develop",
        remote="origin",
        requirements=None,
        repo_root=str(repo),
        source_dir=None,
        no_pull=False,
        dry_run=True,
    )

    state = prepare_repository.prepare_repository(args)

    assert state["repository"] == "inabako/example.git"
    assert state["target_branch"] == "develop"
    assert state["current_branch"] == "develop"
    assert state["current_commit"] == "dry-run"
    assert (repo / "work" / "issue-1" / "context" / "scm-state.json").exists()
    manifest = json.loads((repo / "work" / "issue-1" / "context" / "context-manifest.json").read_text(encoding="utf-8"))
    assert any(context["type"] == "scm-state" for context in manifest["contexts"])


def test_create_issue_branch_dry_run_records_remote_branch_without_api(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"repository": "https://github.com/inabako/example.git", "target_branch": "develop"}),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        issue_number="42",
        repository=None,
        github_repo=None,
        base_branch=None,
        branch_prefix=None,
        remote=None,
        repo_root=str(repo),
        source_dir=None,
        local_only=False,
        link_to_issue=True,
        dry_run=True,
    )

    result = create_issue_branch.create_branch(args)

    assert result["branch"] == "feature/issue-42"
    assert result["remote_branch_ref"] == "refs/heads/feature/issue-42"
    assert result["linked_branch_status"] == "dry-run"
    state = json.loads((work_dir / "context" / "scm-state.json").read_text(encoding="utf-8"))
    assert state["working_branch"] == "feature/issue-42"
    assert state["current_commit"] == "dry-run"


def test_push_branch_dry_run_refuses_non_issue_branch(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"remote": "origin", "working_branch": "develop"}),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        repo_root=str(repo),
        source_dir=str(source),
        remote=None,
        branch=None,
        set_upstream=False,
        human_check="approved",
        dry_run=True,
    )

    with pytest.raises(ValueError, match="Refusing to push non-issue branch"):
        push_branch.push_branch(args)


def test_push_branch_dry_run_writes_push_record_for_issue_branch(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"remote": "origin", "working_branch": "feature/issue-42"}),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        repo_root=str(repo),
        source_dir=str(source),
        remote=None,
        branch=None,
        set_upstream=True,
        human_check="approved",
        dry_run=True,
    )

    result = push_branch.push_branch(args)

    assert result["branch"] == "feature/issue-42"
    assert result["dry_run"] is True
    state = json.loads((work_dir / "context" / "scm-state.json").read_text(encoding="utf-8"))
    assert state["pushed_branch"] == "feature/issue-42"
    assert state["push_record"].startswith("work/issue-1/process-report/push-record-")


def test_commit_changes_rejects_non_semantic_message(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    args = argparse.Namespace(
        work_id="issue-1",
        message="update stuff",
        repo_root=str(repo),
        source_dir=str(source),
        all=False,
        allow_empty=False,
        dry_run=True,
    )

    with pytest.raises(ValueError, match="semantic commit format"):
        commit_changes.commit_changes(args)


def test_commit_changes_dry_run_records_status_without_commit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)

    def fake_run_git(args, cwd):
        if args == ["status", "--short"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout=" M runtime/ctl.py\n", stderr="")
        raise AssertionError(args)

    monkeypatch.setattr(commit_changes, "run_git", fake_run_git)
    monkeypatch.setattr(commit_changes, "current_branch", lambda path: "feature/issue-1")
    args = argparse.Namespace(
        work_id="issue-1",
        message="test: harden scm runtime",
        repo_root=str(repo),
        source_dir=str(source),
        all=False,
        allow_empty=False,
        dry_run=True,
    )

    result = commit_changes.commit_changes(args)

    assert result["commit"] == "dry-run"
    assert result["branch"] == "feature/issue-1"
    assert result["status_before"] == "M runtime/ctl.py"


def test_bootstrap_repository_requires_human_approval_for_initial_push(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo="inabako/example",
        initial_branch="main",
        remote="origin",
        message="chore: bootstrap realtime iac repository",
        repo_root=str(repo),
        source_dir=str(source),
        push=True,
        human_check=None,
        dry_run=True,
    )

    with pytest.raises(ValueError, match="Initial repository push requires --human-check approved"):
        bootstrap_repository.bootstrap_repository(args)
