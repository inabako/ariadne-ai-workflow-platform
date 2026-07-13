from __future__ import annotations

import argparse
import io
import json
import runpy
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
    assert api.github_api_base_url({"GITHUB_API_URL": "https://api.example.test/"}) == "https://api.example.test"
    assert api.github_graphql_url({"GITHUB_GRAPHQL_URL": "https://graphql.example.test/"}) == "https://graphql.example.test"
    assert api.github_graphql_url({"GITHUB_API_URL": "https://api.github.com"}) == "https://api.github.com/graphql"
    assert api.github_graphql_url({"GITHUB_API_URL": "https://github.example.local/api/v3"}) == "https://github.example.local/api/graphql"
    assert api.github_graphql_url({"GITHUB_API_URL": "https://api.example.test/root"}) == "https://api.example.test/root/graphql"
    assert api.github_api_base_url({"GH_HOST": "https://github.example.local/"}) == "https://github.example.local/api/v3"
    assert api.github_graphql_url({"GH_HOST": "github.example.local"}) == "https://github.example.local/api/graphql"


def test_defensive_specimen_issue_body_report_path_returns_empty_without_car_artifact() -> None:
    assert issue_manager.corrective_action_report_path(["work/issue-1/context/state.json", "docs/report.md"]) == ""


class FakeResponse:
    def __init__(self, body: str) -> None:
        self.body = body.encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self.body


def test_github_token_is_required() -> None:
    with pytest.raises(ValueError, match="GitHub API token is required"):
        api.github_token({})


def test_github_api_json_sends_request_and_parses_response(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["method"] = request.get_method()
        seen["body"] = request.data
        seen["auth"] = request.headers["Authorization"]
        seen["timeout"] = timeout
        return FakeResponse('{"ok": true}')

    monkeypatch.setattr(api.request, "urlopen", fake_urlopen)

    result = api.github_api_json({"GITHUB_TOKEN": "token"}, "POST", "/repos/o/r/issues", {"title": "demo"})

    assert result == {"ok": True}
    assert seen["url"] == "https://api.github.com/repos/o/r/issues"
    assert seen["method"] == "POST"
    assert seen["body"] == b'{"title": "demo"}'
    assert seen["auth"] == "Bearer token"
    assert seen["timeout"] == 30


def test_github_api_json_reports_http_and_url_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_http_error(request, timeout):
        raise api.error.HTTPError(
            request.full_url,
            422,
            "unprocessable",
            hdrs=None,
            fp=io.BytesIO(b'{"message": "Validation failed"}'),
        )

    monkeypatch.setattr(api.request, "urlopen", raise_http_error)
    with pytest.raises(RuntimeError, match=r"GitHub API request failed \(422\): Validation failed"):
        api.github_api_json({"GITHUB_TOKEN": "token"}, "GET", "/bad")

    def raise_plain_http_error(request, timeout):
        raise api.error.HTTPError(
            request.full_url,
            500,
            "server error",
            hdrs=None,
            fp=io.BytesIO(b"not-json"),
        )

    monkeypatch.setattr(api.request, "urlopen", raise_plain_http_error)
    with pytest.raises(RuntimeError, match=r"GitHub API request failed \(500\): not-json"):
        api.github_api_json({"GITHUB_TOKEN": "token"}, "GET", "/bad")

    def raise_url_error(request, timeout):
        raise api.error.URLError("network down")

    monkeypatch.setattr(api.request, "urlopen", raise_url_error)
    with pytest.raises(RuntimeError, match="network down"):
        api.github_api_json({"GITHUB_TOKEN": "token"}, "GET", "/bad")


def test_github_graphql_json_returns_data_and_reports_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api.request, "urlopen", lambda request, timeout: FakeResponse('{"data": {"viewer": {"login": "ariadne"}}}'))

    assert api.github_graphql_json({"GITHUB_TOKEN": "token"}, "query { viewer { login } }") == {"viewer": {"login": "ariadne"}}

    monkeypatch.setattr(api.request, "urlopen", lambda request, timeout: FakeResponse('{"errors": [{"message": "bad query"}]}'))
    with pytest.raises(RuntimeError, match="bad query"):
        api.github_graphql_json({"GITHUB_TOKEN": "token"}, "bad")


def test_github_graphql_json_reports_http_and_url_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_http_error(request, timeout):
        raise api.error.HTTPError(
            request.full_url,
            401,
            "unauthorized",
            hdrs=None,
            fp=io.BytesIO(b'{"message": "Bad credentials"}'),
        )

    monkeypatch.setattr(api.request, "urlopen", raise_http_error)
    with pytest.raises(RuntimeError, match=r"GitHub GraphQL request failed \(401\): Bad credentials"):
        api.github_graphql_json({"GITHUB_TOKEN": "token"}, "query")

    def raise_plain_http_error(request, timeout):
        raise api.error.HTTPError(
            request.full_url,
            502,
            "bad gateway",
            hdrs=None,
            fp=io.BytesIO(b"plain failure"),
        )

    monkeypatch.setattr(api.request, "urlopen", raise_plain_http_error)
    with pytest.raises(RuntimeError, match=r"GitHub GraphQL request failed \(502\): plain failure"):
        api.github_graphql_json({"GITHUB_TOKEN": "token"}, "query")

    def raise_url_error(request, timeout):
        raise api.error.URLError("dns failed")

    monkeypatch.setattr(api.request, "urlopen", raise_url_error)
    with pytest.raises(RuntimeError, match="dns failed"):
        api.github_graphql_json({"GITHUB_TOKEN": "token"}, "query")


def test_get_branch_sha_requires_commit_sha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api, "github_api_json", lambda settings, method, path, payload=None: {"commit": {}})

    with pytest.raises(RuntimeError, match="did not include commit sha"):
        api.get_branch_sha({"GITHUB_TOKEN": "token"}, "inabako/example", "develop")


def test_get_branch_sha_returns_commit_sha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api, "github_api_json", lambda settings, method, path, payload=None: {"commit": {"sha": "abc123"}})

    assert api.get_branch_sha({"GITHUB_TOKEN": "token"}, "inabako/example", "develop") == "abc123"


def test_get_repository_issue_graphql_context_returns_ids_and_validates_required_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        api,
        "github_graphql_json",
        lambda settings, query, variables: {
            "repository": {
                "id": "repo-id",
                "issue": {"id": "issue-id"},
                "ref": {"target": {"oid": "base-oid"}},
            }
        },
    )

    assert api.get_repository_issue_graphql_context({"GITHUB_TOKEN": "token"}, "inabako/example", "42", "develop") == {
        "repository_id": "repo-id",
        "issue_id": "issue-id",
        "base_oid": "base-oid",
    }

    monkeypatch.setattr(api, "github_graphql_json", lambda settings, query, variables: {"repository": {}})
    with pytest.raises(RuntimeError, match="repository id"):
        api.get_repository_issue_graphql_context({"GITHUB_TOKEN": "token"}, "inabako/example", "42", "develop")

    monkeypatch.setattr(api, "github_graphql_json", lambda settings, query, variables: {"repository": {"id": "repo-id"}})
    with pytest.raises(RuntimeError, match="issue id"):
        api.get_repository_issue_graphql_context({"GITHUB_TOKEN": "token"}, "inabako/example", "42", "develop")

    monkeypatch.setattr(
        api,
        "github_graphql_json",
        lambda settings, query, variables: {"repository": {"id": "repo-id", "issue": {"id": "issue-id"}}},
    )
    with pytest.raises(RuntimeError, match="base oid"):
        api.get_repository_issue_graphql_context({"GITHUB_TOKEN": "token"}, "inabako/example", "42", "develop")


def test_create_linked_branch_uses_context_and_defaults_missing_linked_ref(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        api,
        "get_repository_issue_graphql_context",
        lambda settings, github_repo, issue_number, base_branch: {
            "repository_id": "repo-id",
            "issue_id": "issue-id",
            "base_oid": "base-oid",
        },
    )
    monkeypatch.setattr(api, "github_graphql_json", lambda settings, query, variables: {"createLinkedBranch": {}})

    result = api.create_linked_branch({"GITHUB_TOKEN": "token"}, "inabako/example", "42", "feature/issue-42", "develop")

    assert result["status"] == "created"
    assert result["linked_branch_name"] == "feature/issue-42"
    assert result["linked_branch_oid"] == "base-oid"
    assert result["issue_id"] == "issue-id"


def test_create_branch_ref_returns_ref_and_validates_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api, "github_api_json", lambda settings, method, path, payload: {"ref": "refs/heads/feature/issue-1"})

    assert api.create_branch_ref({"GITHUB_TOKEN": "token"}, "inabako/example", "feature/issue-1", "abc123") == "refs/heads/feature/issue-1"

    monkeypatch.setattr(api, "github_api_json", lambda settings, method, path, payload: {})
    with pytest.raises(RuntimeError, match="created ref"):
        api.create_branch_ref({"GITHUB_TOKEN": "token"}, "inabako/example", "feature/issue-1", "abc123")


def test_normalize_issue_title_applies_prefix_once() -> None:
    title, prefix = issue_manager.normalize_issue_title("ログを整理する", flow_label="improvement")

    assert title == "[改善フロー] ログを整理する"
    assert prefix == "改善フロー"
    assert issue_manager.normalize_issue_title(title, flow_label="improvement")[0] == title
    assert issue_manager.normalize_issue_title("plain title") == ("plain title", "")


@pytest.mark.parametrize(
    ("workflow_name", "expected"),
    [
        ("ariadne-new-system", "初期開発"),
        ("ariadne-feature-maintenance", "新規機能フロー"),
        ("corrective-action-fix", "改善フロー"),
        ("docs-sync", "改善フロー"),
        ("unknown", ""),
    ],
)
def test_infer_flow_label_from_agent_context(tmp_path: Path, workflow_name: str, expected: str) -> None:
    _, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "agent-context.json").write_text(
        json.dumps({"workflow": {"name": workflow_name}}),
        encoding="utf-8",
    )

    assert issue_manager.infer_flow_label(work_dir) == expected


def test_default_issue_body_uses_project_template_and_corrective_report(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    template = source / ".github" / "ISSUE_TEMPLATE.md"
    template.parent.mkdir(parents=True)
    template.write_text(
        "\n".join(
            [
                "# Issue",
                "- Report:",
                "- Target branch:",
                "- Target commit:",
            ]
        ),
        encoding="utf-8",
    )
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps(
            {
                "source_dir": "work/issue-1/source/repository",
                "target_branch": "develop",
                "current_commit": "abc123",
            }
        ),
        encoding="utf-8",
    )
    (work_dir / "context" / "artifact-index.json").write_text(
        json.dumps(
            {
                "artifacts": [
                    {
                        "path": "work/issue-1/process-report/corrective-action-report.md",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    body = issue_manager.default_issue_body(repo, work_dir)

    assert "- Report: `work/issue-1/process-report/corrective-action-report.md`" in body
    assert "- Target branch: `develop`" in body
    assert "- Target commit: `abc123`" in body


def test_issue_body_from_args_reads_body_file(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    body_file = tmp_path / "body.md"
    body_file.write_text("# Custom body\n", encoding="utf-8")
    args = argparse.Namespace(body_file=str(body_file))

    body, source, template_path = issue_manager.issue_body_from_args(repo, work_dir, args)

    assert body == "# Custom body\n"
    assert source == "body-file"
    assert template_path == str(body_file.resolve())


def test_issue_manager_template_default_and_package_guard_edges(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    template = source / ".github" / "ISSUE_TEMPLATE.md"
    template.parent.mkdir(parents=True)
    template.write_text("- Report:\n- Target branch:\n- Target commit:\n", encoding="utf-8")
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"source_dir": str(source), "target_branch": "", "current_commit": ""}),
        encoding="utf-8",
    )

    body, source_name, template_path = issue_manager.issue_body_from_args(
        repo,
        work_dir,
        argparse.Namespace(body_file=None),
    )

    assert source_name == "project-template"
    assert template_path == "work/issue-1/source/repository/.github/ISSUE_TEMPLATE.md"
    assert "- Report:" in body
    assert "`" not in body

    template.unlink()
    (work_dir / "context" / "artifact-index.json").write_text(
        json.dumps({"artifacts": [{"path": "work/issue-1/design-document/design.md"}]}),
        encoding="utf-8",
    )
    runtime_default = issue_manager.default_issue_body(repo, work_dir)
    assert "`work/issue-1/design-document/design.md`" in runtime_default

    namespace = runpy.run_path(str(Path(issue_manager.__file__)))
    assert namespace["build_parser"]


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


def test_manage_issue_create_uses_defaults_and_updates_artifact_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"repository": "inabako/example", "target_branch": "develop", "current_commit": "abc123"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        issue_manager,
        "load_env",
        lambda repo_root: {
            "DEFAULT_GITHUB_ISSUE_LABELS": "bug, workflow",
            "DEFAULT_GITHUB_ISSUE_ASSIGNEES": "alice,bob",
            "GITHUB_TOKEN": "token",
        },
    )
    monkeypatch.setattr(
        issue_manager,
        "create_issue_with_api",
        lambda github_repo, title, body_text, labels, assignees, settings: ("https://github.com/inabako/example/issues/77", "77"),
    )
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo=None,
        title="修正する",
        flow_label="improvement",
        title_prefix=None,
        body_file=None,
        label=[],
        assignee=[],
        repo_root=str(repo),
        create=True,
    )

    record = issue_manager.manage_issue(args)

    assert record["status"] == "created"
    assert record["issue_number"] == "77"
    assert record["labels"] == ["bug", "workflow"]
    assert record["assignees"] == ["alice", "bob"]
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    assert {artifact["status"] for artifact in artifact_index["artifacts"]} == {"approved"}
    assert all(artifact["unresolved_items"] == [] for artifact in artifact_index["artifacts"])


def test_manage_issue_requires_work_dir_and_github_repo(tmp_path: Path) -> None:
    repo, _ = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="missing",
        github_repo=None,
        title="missing",
        flow_label=None,
        title_prefix=None,
        body_file=None,
        label=[],
        assignee=[],
        repo_root=str(repo),
        create=False,
    )

    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        issue_manager.manage_issue(args)

    args.work_id = "issue-1"
    with pytest.raises(ValueError, match="GitHub repository is required"):
        issue_manager.manage_issue(args)


def test_manage_issue_rejects_repo_without_owner(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"github_repo": "example"}),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo=None,
        title="missing owner",
        flow_label=None,
        title_prefix=None,
        body_file=None,
        label=[],
        assignee=[],
        repo_root=str(repo),
        create=False,
    )

    with pytest.raises(ValueError, match="GitHub repository is required"):
        issue_manager.manage_issue(args)


def test_manage_issue_rejects_slug_without_owner_after_resolution(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, _work_dir = make_work_repo(tmp_path)
    monkeypatch.setattr(issue_manager, "repository_to_github_slug", lambda repository, owner=None: "example")
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo="example",
        title="missing owner",
        flow_label=None,
        title_prefix=None,
        body_file=None,
        label=[],
        assignee=[],
        repo_root=str(repo),
        create=False,
    )

    with pytest.raises(ValueError, match="owner/name"):
        issue_manager.manage_issue(args)


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

    monkeypatch.setattr(
        issue_manager,
        "github_api_json",
        lambda settings, method, path, payload: {"html_url": "https://github.com/inabako/example/issues/not-a-number"},
    )
    issue_url, issue_number = issue_manager.create_issue_with_api(
        "inabako/example",
        "title",
        "body",
        [],
        [],
        {"GITHUB_TOKEN": "token"},
    )
    assert issue_url.endswith("/not-a-number")
    assert issue_number is None


def test_create_issue_with_api_builds_url_from_number_and_rejects_missing_url(monkeypatch: pytest.MonkeyPatch) -> None:
    payloads = []

    def fake_github_api_json(settings, method, path, payload):
        payloads.append(payload)
        return {"number": 88}

    monkeypatch.setattr(issue_manager, "github_api_json", fake_github_api_json)

    issue_url, issue_number = issue_manager.create_issue_with_api(
        "inabako/example",
        "title",
        "body",
        [],
        ["alice"],
        {"GITHUB_TOKEN": "token"},
    )

    assert issue_url == "https://github.com/inabako/example/issues/88"
    assert issue_number == "88"
    assert "labels" not in payloads[0]
    assert payloads[0]["assignees"] == ["alice"]

    monkeypatch.setattr(issue_manager, "github_api_json", lambda settings, method, path, payload: {})
    with pytest.raises(RuntimeError, match="response did not include issue URL"):
        issue_manager.create_issue_with_api("inabako/example", "title", "body", [], [], {"GITHUB_TOKEN": "token"})


def test_issue_manager_main_prints_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"repository": "inabako/example", "target_branch": "develop"}),
        encoding="utf-8",
    )

    code = issue_manager.main(
        [
            "--repo-root",
            str(repo),
            "--work-id",
            "issue-1",
            "--title",
            "docsを同期する",
            "--flow-label",
            "improvement",
            "--github-repo",
            "inabako/example",
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    assert '"status": "draft"' in captured.out

    code = issue_manager.main(["--work-id", "missing", "--title", "x", "--repo-root", str(repo)])
    assert code == 1
    assert "ERROR:" in capsys.readouterr().err


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


def test_pull_request_defaults_use_latest_issue_title_and_base_work_id(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path, work_id="issue-2")
    base_work_dir = repo / "work" / "issue-1"
    (base_work_dir / "context").mkdir(parents=True)
    (base_work_dir / "process-report").mkdir(parents=True)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"base_work_id": "issue-1", "github_repo": "inabako/example", "working_branch": "feature/issue-2"}),
        encoding="utf-8",
    )
    (base_work_dir / "process-report" / "github-issue-old.json").write_text(
        json.dumps({"title": "[改善フロー] 古いIssue"}),
        encoding="utf-8",
    )
    (work_dir / "process-report" / "github-issue-new.json").write_text(
        json.dumps({"title": "[改善フロー] 新しいIssue"}),
        encoding="utf-8",
    )

    assert pull_request_manager.latest_issue_title(repo, work_dir) == "[改善フロー] 古いIssue"
    assert pull_request_manager.default_pr_title(repo, work_dir) == "[改善フロー] 古いIssue"
    assert "sequenceDiagram" in pull_request_manager.default_pr_body(work_dir)


def test_pull_request_uses_title_and_body_files_and_create_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    title_file = tmp_path / "title.md"
    body_file = tmp_path / "body.md"
    title_file.write_text("Custom PR title\n", encoding="utf-8")
    body_file.write_text("Custom PR body\n", encoding="utf-8")
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"repository": "inabako/example", "pushed_branch": "feature/issue-1"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(pull_request_manager, "load_env", lambda repo_root: {"GITHUB_TOKEN": "token"})
    monkeypatch.setattr(
        pull_request_manager,
        "create_pull_request_with_api",
        lambda settings, github_repo, title, body, head, base: {
            "html_url": "https://github.com/inabako/example/pull/5",
            "number": 5,
        },
    )
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo=None,
        base="develop",
        head=None,
        title_file=str(title_file),
        body_file=str(body_file),
        repo_root=str(repo),
        create=True,
        human_check="approved",
    )

    record = pull_request_manager.manage_pull_request(args)

    assert record["status"] == "created"
    assert record["title"] == "Custom PR title"
    assert record["pull_request_number"] == "5"
    assert record["body_file"] == str(body_file.resolve())
    state = json.loads((work_dir / "context" / "scm-state.json").read_text(encoding="utf-8"))
    assert state["pull_request_url"].endswith("/pull/5")


def test_pull_request_requires_work_repo_and_head(tmp_path: Path) -> None:
    repo, _ = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="missing",
        github_repo=None,
        base="develop",
        head=None,
        title_file=None,
        body_file=None,
        repo_root=str(repo),
        create=False,
        human_check=None,
    )

    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        pull_request_manager.manage_pull_request(args)

    args.work_id = "issue-1"
    with pytest.raises(ValueError, match="GitHub repository is required"):
        pull_request_manager.manage_pull_request(args)

    (repo / "work" / "issue-1" / "context" / "scm-state.json").write_text(
        json.dumps({"github_repo": "inabako/example"}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="PR head branch is required"):
        pull_request_manager.manage_pull_request(args)


def test_create_pull_request_with_api_posts_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = {}

    def fake_github_api_json(settings, method, path, payload):
        seen.update({"settings": settings, "method": method, "path": path, "payload": payload})
        return {"html_url": "https://github.com/inabako/example/pull/9", "number": 9}

    monkeypatch.setattr(pull_request_manager, "github_api_json", fake_github_api_json)

    result = pull_request_manager.create_pull_request_with_api(
        {"GITHUB_TOKEN": "token"},
        "inabako/example",
        "title",
        "body",
        "feature/issue-1",
        "develop",
    )

    assert result["number"] == 9
    assert seen["method"] == "POST"
    assert seen["path"] == "/repos/inabako/example/pulls"
    assert seen["payload"] == {
        "title": "title",
        "body": "body",
        "head": "feature/issue-1",
        "base": "develop",
    }


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


def test_pull_request_parser_file_defaults_main_and_script_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parser = pull_request_manager.build_parser()
    parsed = parser.parse_args(
        [
            "--work-id",
            "issue-1",
            "--github-repo",
            "inabako/example",
            "--base",
            "main",
            "--head",
            "feature/issue-1",
            "--title-file",
            "title.md",
            "--body-file",
            "body.md",
            "--repo-root",
            str(tmp_path),
            "--create",
            "--human-check",
            "approved",
        ]
    )
    assert parsed.work_id == "issue-1"
    assert parsed.github_repo == "inabako/example"
    assert parsed.create is True
    assert parsed.human_check == "approved"

    repo, work_dir = make_work_repo(tmp_path)
    title_file = work_dir / "process-report" / "pull-request-title.md"
    body_file = work_dir / "process-report" / "pull-request-description.md"
    title_file.write_text("Saved PR title\n", encoding="utf-8")
    body_file.write_text("Saved PR body\n", encoding="utf-8")
    assert pull_request_manager.default_pr_title(repo, work_dir) == "Saved PR title"
    assert pull_request_manager.default_pr_body(work_dir) == "Saved PR body"

    (work_dir / "process-report" / "github-issue-empty.json").write_text(json.dumps({"title": ""}), encoding="utf-8")
    title_file.unlink()
    assert pull_request_manager.latest_issue_title(repo, work_dir) == ""

    monkeypatch.setattr(
        pull_request_manager,
        "manage_pull_request",
        lambda args: {"status": "draft", "work_id": args.work_id},
    )
    assert pull_request_manager.main(["--repo-root", str(repo), "--work-id", "issue-1", "--head", "feature/issue-1"]) == 0
    assert '"work_id": "issue-1"' in capsys.readouterr().out

    def raise_error(args):
        raise RuntimeError("boom")

    monkeypatch.setattr(pull_request_manager, "manage_pull_request", raise_error)
    assert pull_request_manager.main(["--repo-root", str(repo), "--work-id", "issue-1", "--head", "feature/issue-1"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(pull_request_manager.__file__)))
    assert namespace["build_parser"]
