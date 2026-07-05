from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from runtime.github import api, issue_manager, pull_request_manager


def make_work_repo(tmp_path: Path, work_id: str = "issue-1") -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    work_dir = repo / "work" / work_id
    (repo / ".git").mkdir(parents=True)
    (work_dir / "context").mkdir(parents=True)
    (work_dir / "process-report").mkdir(parents=True)
    return repo, work_dir


def test_github_api_urls_support_dotcom_and_enterprise_hosts() -> None:
    assert api.github_api_base_url({}) == "https://api.github.com"
    assert api.github_graphql_url({}) == "https://api.github.com/graphql"
    assert api.github_api_base_url({"GH_HOST": "https://github.example.local/"}) == "https://github.example.local/api/v3"
    assert api.github_graphql_url({"GH_HOST": "github.example.local"}) == "https://github.example.local/api/graphql"


def test_github_token_is_required() -> None:
    with pytest.raises(ValueError, match="GitHub API token is required"):
        api.github_token({})


def test_get_branch_sha_requires_commit_sha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api, "github_api_json", lambda settings, method, path, payload=None: {"commit": {}})

    with pytest.raises(RuntimeError, match="did not include commit sha"):
        api.get_branch_sha({"GITHUB_TOKEN": "token"}, "inabako/example", "develop")


def test_normalize_issue_title_applies_prefix_once() -> None:
    title, prefix = issue_manager.normalize_issue_title("ログを整理する", flow_label="improvement")

    assert title == "[改善フロー] ログを整理する"
    assert prefix == "改善フロー"
    assert issue_manager.normalize_issue_title(title, flow_label="improvement")[0] == title


def test_manage_issue_draft_writes_body_record_and_artifact_index(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "agent-context.json").write_text(
        json.dumps({"intent": {"summary": "Intent summary"}, "project": {"name": "demo"}, "workflow": {"name": "docs-sync"}}),
        encoding="utf-8",
    )
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"repository": "https://github.com/inabako/example.git", "target_branch": "develop", "current_commit": "abc123"}),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo=None,
        title="docsを同期する",
        flow_label=None,
        title_prefix=None,
        body_file=None,
        label=[],
        assignee=[],
        repo_root=str(repo),
        create=False,
    )

    record = issue_manager.manage_issue(args)

    assert record["status"] == "draft"
    assert record["github_repo"] == "inabako/example"
    assert record["title"] == "[改善フロー] docsを同期する"
    assert record["body_source"] == "runtime-default"
    assert (repo / record["body_path"]).exists()
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    assert {artifact["id"].split("-github-issue-")[0] for artifact in artifact_index["artifacts"]} == {
        "GITHUB-ISSUE-MD",
        "GITHUB-ISSUE-JSON",
    }


def test_create_issue_with_api_extracts_number_from_url_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        issue_manager,
        "github_api_json",
        lambda settings, method, path, payload: {"html_url": "https://github.com/inabako/example/issues/123"},
    )

    issue_url, issue_number = issue_manager.create_issue_with_api(
        "inabako/example",
        "title",
        "body",
        ["bug"],
        [],
        {"GITHUB_TOKEN": "token"},
    )

    assert issue_url.endswith("/issues/123")
    assert issue_number == "123"


def test_pull_request_create_requires_human_approval(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"github_repo": "inabako/example", "working_branch": "feature/issue-1"}),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo=None,
        base="develop",
        head=None,
        title_file=None,
        body_file=None,
        repo_root=str(repo),
        create=True,
        human_check=None,
    )

    with pytest.raises(ValueError, match="--create requires --human-check approved"):
        pull_request_manager.manage_pull_request(args)


def test_pull_request_draft_writes_record_and_updates_scm_state(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"github_repo": "inabako/example", "working_branch": "feature/issue-1"}),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo=None,
        base="develop",
        head=None,
        title_file=None,
        body_file=None,
        repo_root=str(repo),
        create=False,
        human_check=None,
    )

    record = pull_request_manager.manage_pull_request(args)

    assert record["status"] == "draft"
    assert record["head"] == "feature/issue-1"
    assert record["base"] == "develop"
    state = json.loads((work_dir / "context" / "scm-state.json").read_text(encoding="utf-8"))
    assert state["pull_request_record"].startswith("work/issue-1/process-report/pull-request-")
