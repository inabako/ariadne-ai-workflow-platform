from __future__ import annotations

import argparse
import json
import runpy
import subprocess
from pathlib import Path

import pytest

from runtime.scm import (
    bootstrap_repository,
    commit_changes,
    create_issue_branch,
    prepare_repository,
    prepare_support_repository,
    push_branch,
    scm_utils,
)


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


def test_scm_utils_dry_run_posix_askpass_and_git_helpers(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    dry = scm_utils.run_git(["status"], tmp_path, dry_run=True)

    assert dry.returncode == 0
    assert dry.stdout == "DRY-RUN: git status"

    calls: list[list[str]] = []
    original_run_git = scm_utils.run_git

    def fake_run_git(args, cwd):
        calls.append(list(args))
        if args == ["show-ref", "--verify", "--quiet", "refs/heads/missing"]:
            return subprocess.CompletedProcess(["git", *args], 1, stdout="", stderr="")
        return subprocess.CompletedProcess(["git", *args], 0, stdout="value\n", stderr="")

    monkeypatch.setattr(scm_utils, "run_git", fake_run_git)

    assert scm_utils.git_output(["rev-parse", "HEAD"], tmp_path) == "value"
    assert scm_utils.current_branch(tmp_path) == "value"
    assert scm_utils.current_commit(tmp_path) == "value"
    assert scm_utils.local_branch_exists(tmp_path, "feature/issue-1") is True
    assert scm_utils.local_branch_exists(tmp_path, "missing") is False
    assert ["rev-parse", "--abbrev-ref", "HEAD"] in calls
    assert ["rev-parse", "HEAD"] in calls

    def fake_subprocess_run(command, **kwargs):
        assert command == ["git", "status"]
        assert kwargs["cwd"] == str(tmp_path)
        assert kwargs["env"] == {"A": "B"}
        assert kwargs["shell"] is False
        return subprocess.CompletedProcess(command, 0, stdout="clean\n", stderr="")

    monkeypatch.setattr(scm_utils.subprocess, "run", fake_subprocess_run)
    assert original_run_git(["status"], tmp_path, env={"A": "B"}).stdout == "clean\n"


def test_scm_utils_posix_askpass_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    writes: list[tuple[str, str]] = []
    chmods: list[int] = []

    class DummyTempDirectory:
        def __enter__(self) -> str:
            return "dummy-temp"

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

    class FakePath:
        def __init__(self, value: str) -> None:
            self.value = value

        def __truediv__(self, child: str) -> "FakePath":
            return FakePath(f"{self.value}/{child}")

        def write_text(self, text: str, encoding: str) -> None:
            writes.append((text, encoding))

        def chmod(self, mode: int) -> None:
            chmods.append(mode)

        def __str__(self) -> str:
            return self.value

    monkeypatch.setattr(scm_utils.os, "name", "posix")
    monkeypatch.setattr(scm_utils.tempfile, "TemporaryDirectory", DummyTempDirectory)
    monkeypatch.setattr(scm_utils, "Path", FakePath)

    with scm_utils.github_token_git_env("secret-token") as env:
        assert env is not None
        assert env["GIT_ASKPASS"] == "dummy-temp/git-askpass.sh"

    assert writes and writes[0][1] == "utf-8"
    assert chmods == [0o700]


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


def test_prepare_repository_parser_main_script_and_missing_work(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parser = prepare_repository.build_parser()
    parsed = parser.parse_args(
        [
            "--work-id",
            "issue-1",
            "--repository",
            "inabako/example",
            "--target-branch",
            "develop",
            "--remote",
            "upstream",
            "--requirements",
            str(tmp_path / "req.md"),
            "--repo-root",
            str(tmp_path),
            "--source-dir",
            str(tmp_path / "source"),
            "--no-pull",
            "--dry-run",
        ]
    )

    assert parsed.work_id == "issue-1"
    assert parsed.repository == "inabako/example"
    assert parsed.target_branch == "develop"
    assert parsed.remote == "upstream"
    assert parsed.requirements == [str(tmp_path / "req.md")]
    assert parsed.no_pull is True
    assert parsed.dry_run is True

    repo, _work_dir = make_work_repo(tmp_path)

    assert prepare_repository.main(
        [
            "--work-id",
            "issue-1",
            "--repository",
            "inabako/example",
            "--repo-root",
            str(repo),
            "--dry-run",
        ]
    ) == 0
    assert '"repository": "inabako/example"' in capsys.readouterr().out

    namespace = runpy.run_path(str(Path(prepare_repository.__file__)))
    assert namespace["build_parser"]

    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        prepare_repository.prepare_repository(
            argparse.Namespace(
                work_id="missing",
                repository="inabako/example",
                target_branch=None,
                remote=None,
                requirements=[],
                repo_root=str(repo),
                source_dir=None,
                no_pull=False,
                dry_run=True,
            )
        )

    def fail_prepare(_args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(prepare_repository, "prepare_repository", fail_prepare)

    assert prepare_repository.main(["--work-id", "issue-1", "--repository", "inabako/example"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err


def test_prepare_repository_uses_requirement_config_when_cli_repository_is_missing(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    requirement = repo / "work" / "requirements" / "req.md"
    requirement.parent.mkdir(parents=True)
    requirement.write_text(
        "\n".join(
            [
                "# Requirement",
                "",
                "Repository: inabako/from-requirement",
                "Target branch: release",
                "Remote: upstream",
            ]
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        repository=None,
        target_branch=None,
        remote=None,
        requirements=[str(requirement)],
        repo_root=str(repo),
        source_dir=None,
        no_pull=False,
        dry_run=True,
    )

    state = prepare_repository.prepare_repository(args)

    assert state["repository"] == "inabako/from-requirement"
    assert state["repository_source"] == "requirements"
    assert state["target_branch"] == "release"
    assert state["remote"] == "upstream"
    assert state["requirement_files"] == ["work/requirements/req.md"]
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    assert any(artifact["id"] == "SCM-STATE" for artifact in artifact_index["artifacts"])


def test_prepare_repository_requires_repository_when_cli_and_requirements_are_empty(tmp_path: Path) -> None:
    repo, _ = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="issue-1",
        repository=None,
        target_branch=None,
        remote=None,
        requirements=[],
        repo_root=str(repo),
        source_dir=None,
        no_pull=False,
        dry_run=True,
    )

    with pytest.raises(ValueError, match="Repository is required"):
        prepare_repository.prepare_repository(args)


def test_prepare_repository_rejects_existing_non_git_source_dir(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    args = argparse.Namespace(
        work_id="issue-1",
        repository="inabako/example",
        target_branch="main",
        remote="origin",
        requirements=None,
        repo_root=str(repo),
        source_dir=str(source),
        no_pull=False,
        dry_run=True,
    )

    with pytest.raises(RuntimeError, match="not a git repository"):
        prepare_repository.prepare_repository(args)


def test_prepare_repository_existing_git_repo_fetch_checkout_and_pull(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    (source / ".git").mkdir(parents=True)
    calls: list[list[str]] = []

    def fake_run_git(args, cwd):
        calls.append(list(args))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(prepare_repository, "run_git", fake_run_git)
    monkeypatch.setattr(prepare_repository, "current_branch", lambda path: "develop")
    monkeypatch.setattr(prepare_repository, "current_commit", lambda path: "abc123")
    args = argparse.Namespace(
        work_id="issue-1",
        repository="inabako/example",
        target_branch="develop",
        remote="origin",
        requirements=None,
        repo_root=str(repo),
        source_dir=str(source),
        no_pull=False,
        dry_run=False,
    )

    state = prepare_repository.prepare_repository(args)

    assert state["current_branch"] == "develop"
    assert state["current_commit"] == "abc123"
    assert calls == [
        ["fetch", "origin", "develop"],
        ["checkout", "develop"],
        ["pull", "--ff-only", "origin", "develop"],
    ]


def test_prepare_repository_clone_repository_invokes_git_with_token_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "source" / "repository"
    calls: list[tuple[list[str], Path, dict[str, str] | None]] = []

    def fake_run_git(args, cwd, env=None):
        calls.append((list(args), cwd, env))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(prepare_repository, "run_git", fake_run_git)

    prepare_repository.clone_repository("https://github.com/inabako/example.git", "main", source, "token", dry_run=False)

    assert calls[0][0] == [
        "clone",
        "--branch",
        "main",
        "--single-branch",
        "https://github.com/inabako/example.git",
        str(source),
    ]
    assert calls[0][1] == source.parent
    assert calls[0][2] is not None
    assert calls[0][2]["GITHUB_TOKEN"] == "token"

    dry_source = tmp_path / "dry-source" / "repository"
    create_issue_branch.clone_issue_branch("inabako/example", "feature/issue-43", dry_source, "token", "inabako", dry_run=True)
    assert dry_source.parent.exists()
    assert not dry_source.exists()


def test_prepare_repository_clone_dry_run_and_no_pull_branch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "source" / "repository"
    prepare_repository.clone_repository("https://github.com/inabako/example.git", "main", source, "token", dry_run=True)
    assert source.parent.exists()
    assert not source.exists()

    repo, work_dir = make_work_repo(tmp_path)
    source.mkdir(parents=True)
    calls: list[list[str]] = []

    def fake_run_git(args, cwd):
        calls.append(list(args))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(prepare_repository, "run_git", fake_run_git)
    monkeypatch.setattr(prepare_repository, "is_git_repository", lambda path: True)
    monkeypatch.setattr(prepare_repository, "current_branch", lambda path: "develop")
    monkeypatch.setattr(prepare_repository, "current_commit", lambda path: "abc123")
    args = argparse.Namespace(
        work_id=work_dir.name,
        repository="inabako/example",
        target_branch="develop",
        remote="upstream",
        requirements=[],
        repo_root=str(repo),
        source_dir=str(source),
        no_pull=True,
        dry_run=False,
    )

    state = prepare_repository.prepare_repository(args)

    assert state["current_branch"] == "develop"
    assert ["fetch", "upstream", "develop"] in calls
    assert ["checkout", "develop"] in calls
    assert ["pull", "--ff-only", "upstream", "develop"] not in calls


def test_prepare_support_repository_dry_run_writes_state_report_and_artifacts(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="issue-1",
        name="protocol",
        repository="localty-system-protocol",
        branch="main",
        remote="origin",
        repo_root=str(repo),
        source_dir=None,
        no_pull=False,
        dry_run=True,
    )

    result = prepare_support_repository.prepare_support_repository(args)

    assert result["action"] == "dry-run"
    assert result["branch"] == "main"
    assert result["commit"] == "dry-run"
    assert result["source_dir"] == "work/issue-1/source/protocol"

    support_state = json.loads((work_dir / "context" / "support-repositories.json").read_text(encoding="utf-8"))
    assert support_state["repositories"][0]["name"] == "protocol"
    assert (work_dir / "process-report" / "support-repository-protocol.json").exists()

    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    artifact_ids = {artifact["id"] for artifact in artifact_index["artifacts"]}
    assert {"SUPPORT-REPOSITORY-PROTOCOL", "SUPPORT-REPOSITORIES"} <= artifact_ids


def test_prepare_support_repository_replaces_existing_state_entry(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "support-repositories.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "repositories": [
                    {
                        "name": "protocol",
                        "branch": "old",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        name="protocol",
        repository="inabako/localty-system-protocol",
        branch="develop",
        remote=None,
        repo_root=str(repo),
        source_dir=None,
        no_pull=False,
        dry_run=True,
    )

    prepare_support_repository.prepare_support_repository(args)

    support_state = json.loads((work_dir / "context" / "support-repositories.json").read_text(encoding="utf-8"))
    assert len(support_state["repositories"]) == 1
    assert support_state["repositories"][0]["branch"] == "develop"


def test_prepare_support_repository_rejects_existing_non_git_source_dir(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "protocol"
    source.mkdir(parents=True)
    args = argparse.Namespace(
        work_id="issue-1",
        name="protocol",
        repository="inabako/localty-system-protocol",
        branch="main",
        remote=None,
        repo_root=str(repo),
        source_dir=str(source),
        no_pull=False,
        dry_run=True,
    )

    with pytest.raises(RuntimeError, match="not a git repository"):
        prepare_support_repository.prepare_support_repository(args)


def test_prepare_support_repository_updates_existing_git_repo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "protocol"
    (source / ".git").mkdir(parents=True)
    calls: list[list[str]] = []

    def fake_run_git(args, cwd):
        calls.append(list(args))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(prepare_support_repository, "run_git", fake_run_git)
    monkeypatch.setattr(prepare_support_repository, "current_branch", lambda path: "develop")
    monkeypatch.setattr(prepare_support_repository, "current_commit", lambda path: "abc123")
    args = argparse.Namespace(
        work_id="issue-1",
        name="protocol",
        repository="inabako/localty-system-protocol",
        branch="develop",
        remote="upstream",
        repo_root=str(repo),
        source_dir=str(source),
        no_pull=True,
        dry_run=False,
    )

    result = prepare_support_repository.prepare_support_repository(args)

    assert result["action"] == "updated"
    assert result["branch"] == "develop"
    assert result["commit"] == "abc123"
    assert calls == [
        ["fetch", "upstream", "develop"],
        ["checkout", "develop"],
    ]


def test_prepare_support_repository_parser_clone_pull_main_and_script_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    parser = prepare_support_repository.build_parser()
    parsed = parser.parse_args(
        [
            "--work-id",
            "issue-1",
            "--name",
            "protocol",
            "--repository",
            "inabako/localty-system-protocol",
            "--branch",
            "develop",
            "--remote",
            "upstream",
            "--repo-root",
            str(repo),
            "--source-dir",
            str(work_dir / "source" / "protocol"),
            "--no-pull",
            "--dry-run",
        ]
    )
    assert parsed.work_id == "issue-1"
    assert parsed.name == "protocol"
    assert parsed.no_pull is True
    assert parsed.dry_run is True

    clone_calls: list[tuple[list[str], Path, dict[str, str] | None]] = []

    def fake_run_git(args, cwd, env=None):
        clone_calls.append((list(args), cwd, env))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(prepare_support_repository, "run_git", fake_run_git)
    prepare_support_repository.clone_repository(
        "https://github.com/inabako/example.git",
        "main",
        work_dir / "source" / "example",
        "token",
        dry_run=False,
    )
    assert clone_calls[0][0][:4] == ["clone", "--branch", "main", "--single-branch"]
    assert clone_calls[0][2] is not None

    source = work_dir / "source" / "protocol"
    (source / ".git").mkdir(parents=True)
    update_calls: list[list[str]] = []

    def fake_update_git(args, cwd):
        update_calls.append(list(args))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(prepare_support_repository, "run_git", fake_update_git)
    monkeypatch.setattr(prepare_support_repository, "current_branch", lambda path: "develop")
    monkeypatch.setattr(prepare_support_repository, "current_commit", lambda path: "abc123")
    update_args = argparse.Namespace(
        work_id="issue-1",
        name="protocol",
        repository="inabako/localty-system-protocol",
        branch="develop",
        remote="origin",
        repo_root=str(repo),
        source_dir=str(source),
        no_pull=False,
        dry_run=False,
    )

    result = prepare_support_repository.prepare_support_repository(update_args)

    assert result["action"] == "updated"
    assert ["pull", "--ff-only", "origin", "develop"] in update_calls

    dry_existing_args = argparse.Namespace(**{**vars(update_args), "dry_run": True})
    dry_existing = prepare_support_repository.prepare_support_repository(dry_existing_args)
    assert dry_existing["action"] == "dry-run"

    missing_args = argparse.Namespace(**{**vars(update_args), "work_id": "missing"})
    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        prepare_support_repository.prepare_support_repository(missing_args)

    monkeypatch.setattr(
        prepare_support_repository,
        "prepare_support_repository",
        lambda args: {"status": "ok", "work_id": args.work_id},
    )
    assert prepare_support_repository.main(
        [
            "--work-id",
            "issue-1",
            "--name",
            "protocol",
            "--repository",
            "inabako/localty-system-protocol",
            "--repo-root",
            str(repo),
        ]
    ) == 0
    assert '"work_id": "issue-1"' in capsys.readouterr().out

    def raise_error(args):
        raise RuntimeError("boom")

    monkeypatch.setattr(prepare_support_repository, "prepare_support_repository", raise_error)
    assert prepare_support_repository.main(
        [
            "--work-id",
            "issue-1",
            "--name",
            "protocol",
            "--repository",
            "inabako/localty-system-protocol",
            "--repo-root",
            str(repo),
        ]
    ) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(prepare_support_repository.__file__)))
    assert namespace["build_parser"]


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


def test_create_issue_branch_clone_issue_branch_uses_token_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "source" / "repository"
    calls: list[tuple[list[str], Path, dict[str, str] | None]] = []

    def fake_run_git(args, cwd, env=None):
        calls.append((list(args), cwd, env))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(create_issue_branch, "run_git", fake_run_git)

    create_issue_branch.clone_issue_branch("inabako/example", "feature/issue-42", source, "token", "inabako", dry_run=False)

    assert calls[0][0] == [
        "clone",
        "--branch",
        "feature/issue-42",
        "--single-branch",
        "https://github.com/inabako/example.git",
        str(source),
    ]
    assert calls[0][1] == source.parent
    assert calls[0][2] is not None
    assert calls[0][2]["GITHUB_TOKEN"] == "token"


def test_create_issue_branch_checkout_existing_repository_switches_existing_or_tracks_remote(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "repository"
    source.mkdir()
    calls: list[list[str]] = []

    def fake_run_git(args, cwd):
        calls.append(list(args))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(create_issue_branch, "run_git", fake_run_git)
    monkeypatch.setattr(create_issue_branch, "local_branch_exists", lambda path, branch: True)

    create_issue_branch.checkout_existing_repository(source, "origin", "feature/issue-42", dry_run=False)

    assert calls == [
        ["fetch", "origin", "feature/issue-42"],
        ["switch", "feature/issue-42"],
    ]

    calls.clear()
    monkeypatch.setattr(create_issue_branch, "local_branch_exists", lambda path, branch: False)

    create_issue_branch.checkout_existing_repository(source, "upstream", "feature/issue-43", dry_run=False)

    assert calls == [
        ["fetch", "upstream", "feature/issue-43"],
        ["switch", "--track", "-c", "feature/issue-43", "upstream/feature/issue-43"],
    ]

    calls.clear()
    create_issue_branch.checkout_existing_repository(source, "origin", "feature/issue-44", dry_run=True)
    assert calls == []


def test_create_issue_branch_local_only_requires_source_repository(tmp_path: Path) -> None:
    repo, _ = make_work_repo(tmp_path)
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
        local_only=True,
        link_to_issue=False,
        dry_run=True,
    )

    with pytest.raises(FileNotFoundError, match="Source repository does not exist"):
        create_issue_branch.create_branch(args)


def test_create_issue_branch_local_only_switches_existing_branch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    calls: list[list[str]] = []

    def fake_run_git(args, cwd):
        calls.append(list(args))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(create_issue_branch, "run_git", fake_run_git)
    monkeypatch.setattr(create_issue_branch, "local_branch_exists", lambda path, branch: True)
    monkeypatch.setattr(create_issue_branch, "current_branch", lambda path: "feature/issue-42")
    monkeypatch.setattr(create_issue_branch, "current_commit", lambda path: "abc123")
    args = argparse.Namespace(
        work_id="issue-1",
        issue_number="42",
        repository="inabako/example",
        github_repo=None,
        base_branch="develop",
        branch_prefix=None,
        remote="origin",
        repo_root=str(repo),
        source_dir=str(source),
        local_only=True,
        link_to_issue=True,
        dry_run=False,
    )

    result = create_issue_branch.create_branch(args)

    assert result["linked_branch_status"] == "skipped_local_only"
    assert calls == [["switch", "feature/issue-42"]]
    state = json.loads((work_dir / "context" / "scm-state.json").read_text(encoding="utf-8"))
    assert state["current_commit"] == "abc123"


def test_create_issue_branch_local_only_creates_missing_branch_and_script_load(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    calls: list[list[str]] = []

    def fake_run_git(args, cwd):
        calls.append(list(args))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(create_issue_branch, "run_git", fake_run_git)
    monkeypatch.setattr(create_issue_branch, "local_branch_exists", lambda path, branch: False)
    monkeypatch.setattr(create_issue_branch, "current_branch", lambda path: "feature/issue-99")
    monkeypatch.setattr(create_issue_branch, "current_commit", lambda path: "commit99")

    result = create_issue_branch.create_branch(
        argparse.Namespace(
            work_id="issue-1",
            issue_number="99",
            repository=None,
            github_repo=None,
            base_branch=None,
            branch_prefix=None,
            remote=None,
            repo_root=str(repo),
            source_dir=str(source),
            local_only=True,
            link_to_issue=True,
            dry_run=False,
        )
    )

    assert result["linked_branch_status"] == "skipped_local_only"
    assert ["switch", "-c", "feature/issue-99"] in calls

    namespace = runpy.run_path(str(Path(create_issue_branch.__file__)))
    assert namespace["build_parser"]


def test_create_issue_branch_remote_branch_ref_then_clone(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    clone_calls: list[tuple[str, str, Path, str, str, bool]] = []
    monkeypatch.setattr(create_issue_branch, "load_env", lambda repo_root: {"GITHUB_TOKEN": "token"})
    monkeypatch.setattr(create_issue_branch, "get_branch_sha", lambda settings, github_repo, base_branch: "base-sha")
    monkeypatch.setattr(
        create_issue_branch,
        "create_branch_ref",
        lambda settings, github_repo, branch, sha: f"refs/heads/{branch}",
    )
    monkeypatch.setattr(
        create_issue_branch,
        "clone_issue_branch",
        lambda repository, branch_name, source_dir, token, default_owner, dry_run: clone_calls.append(
            (repository, branch_name, source_dir, token, default_owner, dry_run)
        ),
    )
    monkeypatch.setattr(create_issue_branch, "current_branch", lambda path: "feature/issue-42")
    monkeypatch.setattr(create_issue_branch, "current_commit", lambda path: "commit-sha")
    args = argparse.Namespace(
        work_id="issue-1",
        issue_number="42",
        repository="inabako/example",
        github_repo=None,
        base_branch="develop",
        branch_prefix="feat/issue",
        remote="upstream",
        repo_root=str(repo),
        source_dir=None,
        local_only=False,
        link_to_issue=False,
        dry_run=False,
    )

    result = create_issue_branch.create_branch(args)

    assert result["branch"] == "feat/issue-42"
    assert result["remote_branch_ref"] == "refs/heads/feat/issue-42"
    assert result["linked_branch_status"] == "not_requested"
    assert clone_calls == [
        ("inabako/example", "feat/issue-42", work_dir / "source" / "repository", "token", "", False)
    ]
    state = json.loads((work_dir / "context" / "scm-state.json").read_text(encoding="utf-8"))
    assert state["remote_branch_base_sha"] == "base-sha"
    assert state["current_branch"] == "feature/issue-42"


def test_create_issue_branch_remote_dry_run_fills_repository_from_github_repo(tmp_path: Path) -> None:
    repo, _work_dir = make_work_repo(tmp_path)
    result = create_issue_branch.create_branch(
        argparse.Namespace(
            work_id="issue-1",
            issue_number="55",
            repository=None,
            github_repo="inabako/example",
            base_branch="main",
            branch_prefix="feature/issue",
            remote="origin",
            repo_root=str(repo),
            source_dir=None,
            local_only=False,
            link_to_issue=False,
            dry_run=True,
        )
    )

    assert result["remote_branch_ref"] == "refs/heads/feature/issue-55"
    state = json.loads((repo / "work" / "issue-1" / "context" / "scm-state.json").read_text(encoding="utf-8"))
    assert state["repository"] == "https://github.com/inabako/example.git"


def test_create_issue_branch_remote_linked_branch_checks_out_existing_source(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    checkout_calls: list[tuple[Path, str, str, bool]] = []
    monkeypatch.setattr(
        create_issue_branch,
        "create_linked_branch",
        lambda settings, github_repo, issue_number, branch, base_branch: {
            "status": "created",
            "linked_branch_id": "linked-id",
            "linked_branch_name": branch,
            "issue_id": "issue-id",
            "repository_id": "repo-id",
            "base_oid": "base-oid",
        },
    )
    monkeypatch.setattr(
        create_issue_branch,
        "checkout_existing_repository",
        lambda source_dir, remote, branch_name, dry_run: checkout_calls.append((source_dir, remote, branch_name, dry_run)),
    )
    monkeypatch.setattr(create_issue_branch, "current_branch", lambda path: "feature/issue-42")
    monkeypatch.setattr(create_issue_branch, "current_commit", lambda path: "commit-sha")
    args = argparse.Namespace(
        work_id="issue-1",
        issue_number="42",
        repository="https://github.com/inabako/example.git",
        github_repo=None,
        base_branch="develop",
        branch_prefix=None,
        remote="origin",
        repo_root=str(repo),
        source_dir=str(source),
        local_only=False,
        link_to_issue=True,
        dry_run=False,
    )

    result = create_issue_branch.create_branch(args)

    assert result["linked_branch_status"] == "created"
    assert result["linked_branch_id"] == "linked-id"
    assert checkout_calls == [(source, "origin", "feature/issue-42", False)]
    state = json.loads((work_dir / "context" / "scm-state.json").read_text(encoding="utf-8"))
    assert state["linked_branch_issue_id"] == "issue-id"
    assert state["linked_branch_repository_id"] == "repo-id"


def test_create_issue_branch_requires_github_repo_for_remote_creation(tmp_path: Path) -> None:
    repo, _ = make_work_repo(tmp_path)
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
        link_to_issue=False,
        dry_run=True,
    )

    with pytest.raises(ValueError, match="GitHub repository is required"):
        create_issue_branch.create_branch(args)


def test_create_issue_branch_main_prints_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"repository": "https://github.com/inabako/example.git", "target_branch": "develop"}),
        encoding="utf-8",
    )

    code = create_issue_branch.main(
        [
            "--repo-root",
            str(repo),
            "--work-id",
            "issue-1",
            "--issue-number",
            "42",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    assert '"branch": "feature/issue-42"' in captured.out

    namespace = runpy.run_path(str(Path(push_branch.__file__)))
    assert namespace["build_parser"]


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


def test_push_branch_requires_existing_source_repository(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="issue-1",
        repo_root=str(repo),
        source_dir=str(work_dir / "source" / "repository"),
        remote=None,
        branch="feature/issue-42",
        set_upstream=False,
        human_check="approved",
        dry_run=True,
    )

    with pytest.raises(FileNotFoundError, match="Source repository does not exist"):
        push_branch.push_branch(args)


def test_push_branch_refuses_workflow_repository_itself(tmp_path: Path) -> None:
    repo, _ = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="issue-1",
        repo_root=str(repo),
        source_dir=str(repo),
        remote=None,
        branch="feature/issue-42",
        set_upstream=False,
        human_check="approved",
        dry_run=True,
    )

    with pytest.raises(ValueError, match="workflow repository itself"):
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


def test_push_branch_uses_current_branch_when_state_has_no_working_branch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    (work_dir / "context" / "scm-state.json").write_text(json.dumps({"remote": "upstream"}), encoding="utf-8")
    monkeypatch.setattr(push_branch, "current_branch", lambda path: "feature/issue-99")
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

    result = push_branch.push_branch(args)

    assert result["remote"] == "upstream"
    assert result["branch"] == "feature/issue-99"


def test_push_branch_non_dry_run_uses_token_env_and_set_upstream(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    calls: list[tuple[list[str], Path, dict[str, str] | None]] = []
    monkeypatch.setattr(push_branch, "load_env", lambda repo_root: {"GITHUB_TOKEN": "token"})

    def fake_run_git(args, cwd, env=None):
        calls.append((list(args), cwd, env))
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(push_branch, "run_git", fake_run_git)
    args = argparse.Namespace(
        work_id="issue-1",
        repo_root=str(repo),
        source_dir=str(source),
        remote="origin",
        branch="feature/issue-42",
        set_upstream=True,
        human_check="approved",
        dry_run=False,
    )

    result = push_branch.push_branch(args)

    assert result["dry_run"] is False
    assert calls[0][0] == ["push", "-u", "origin", "feature/issue-42"]
    assert calls[0][1] == source
    assert calls[0][2] is not None
    assert calls[0][2]["GITHUB_TOKEN"] == "token"


def test_push_branch_main_prints_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"remote": "origin", "working_branch": "feature/issue-42"}),
        encoding="utf-8",
    )

    code = push_branch.main(
        [
            "--repo-root",
            str(repo),
            "--work-id",
            "issue-1",
            "--source-dir",
            str(source),
            "--human-check",
            "approved",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    assert '"branch": "feature/issue-42"' in captured.out


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


def test_commit_changes_parser_main_script_and_plain_commit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parser = commit_changes.build_parser()
    parsed = parser.parse_args(
        [
            "--work-id",
            "issue-1",
            "--message",
            "fix: commit change",
            "--repo-root",
            str(tmp_path),
            "--source-dir",
            str(tmp_path / "repo"),
            "--all",
            "--allow-empty",
            "--dry-run",
        ]
    )

    assert parsed.work_id == "issue-1"
    assert parsed.message == "fix: commit change"
    assert parsed.all is True
    assert parsed.allow_empty is True
    assert parsed.dry_run is True

    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    calls: list[list[str]] = []

    def fake_run_git(args, cwd):
        calls.append(list(args))
        if args == ["status", "--short"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout=" M app.py\n", stderr="")
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(commit_changes, "load_env", lambda repo_root: {})
    monkeypatch.setattr(commit_changes, "run_git", fake_run_git)
    monkeypatch.setattr(commit_changes, "current_branch", lambda path: "feature/issue-1")
    monkeypatch.setattr(commit_changes, "current_commit", lambda path: "commit123")

    result = commit_changes.commit_changes(
        argparse.Namespace(
            work_id="issue-1",
            message="fix: commit change",
            repo_root=str(repo),
            source_dir=str(source),
            all=False,
            allow_empty=False,
            dry_run=False,
        )
    )

    assert result["commit"] == "commit123"
    assert ["commit", "-m", "fix: commit change"] in calls
    assert not any(call[:2] == ["config", "user.name"] for call in calls)
    assert ["add", "-A"] not in calls

    assert commit_changes.main(
        [
            "--work-id",
            "issue-1",
            "--message",
            "fix: commit change",
            "--repo-root",
            str(repo),
            "--source-dir",
            str(source),
            "--dry-run",
        ]
    ) == 0
    assert '"message": "fix: commit change"' in capsys.readouterr().out

    monkeypatch.setattr(commit_changes, "commit_changes", lambda args: (_ for _ in ()).throw(RuntimeError("boom")))
    assert commit_changes.main(["--work-id", "issue-1", "--message", "fix: commit change"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(commit_changes.__file__)))
    assert namespace["build_parser"]


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


def test_commit_changes_missing_source_dir_is_reported(tmp_path: Path) -> None:
    repo, _ = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="issue-1",
        message="test: harden missing source handling",
        repo_root=str(repo),
        source_dir=str(repo / "work" / "issue-1" / "source" / "repository"),
        all=False,
        allow_empty=False,
        dry_run=True,
    )

    with pytest.raises(FileNotFoundError, match="Source repository does not exist"):
        commit_changes.commit_changes(args)


def test_commit_changes_requires_changes_unless_allow_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    monkeypatch.setattr(
        commit_changes,
        "run_git",
        lambda args, cwd: subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr=""),
    )
    args = argparse.Namespace(
        work_id="issue-1",
        message="test: require non empty commit",
        repo_root=str(repo),
        source_dir=str(source),
        all=False,
        allow_empty=False,
        dry_run=True,
    )

    with pytest.raises(RuntimeError, match="No changes to commit"):
        commit_changes.commit_changes(args)


def test_commit_changes_non_dry_run_allows_empty_and_configures_user(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    calls: list[list[str]] = []

    def fake_run_git(args, cwd):
        calls.append(list(args))
        if args == ["status", "--short"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(commit_changes, "load_env", lambda repo_root: {"GIT_USER_NAME": "Ariadne", "GIT_USER_EMAIL": "ariadne@example.test"})
    monkeypatch.setattr(commit_changes, "run_git", fake_run_git)
    monkeypatch.setattr(commit_changes, "current_branch", lambda path: "feature/issue-1")
    monkeypatch.setattr(commit_changes, "current_commit", lambda path: "commit123")
    args = argparse.Namespace(
        work_id="issue-1",
        message="test: allow empty semantic commit",
        repo_root=str(repo),
        source_dir=str(source),
        all=True,
        allow_empty=True,
        dry_run=False,
    )

    result = commit_changes.commit_changes(args)

    assert result["commit"] == "commit123"
    assert result["dry_run"] is False
    assert ["config", "user.name", "Ariadne"] in calls
    assert ["config", "user.email", "ariadne@example.test"] in calls
    assert ["add", "-A"] in calls
    assert ["commit", "--allow-empty", "-m", "test: allow empty semantic commit"] in calls


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


def test_bootstrap_repository_rejects_non_semantic_message(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo="inabako/example",
        initial_branch="main",
        remote="origin",
        message="bootstrap please",
        repo_root=str(repo),
        source_dir=str(work_dir / "source" / "repository"),
        push=False,
        human_check=None,
        dry_run=True,
    )

    with pytest.raises(ValueError, match="semantic commit format"):
        bootstrap_repository.bootstrap_repository(args)


def test_bootstrap_repository_parser_main_and_script_load(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parser = bootstrap_repository.build_parser()
    parsed = parser.parse_args(
        [
            "--work-id",
            "issue-1",
            "--github-repo",
            "inabako/example",
            "--initial-branch",
            "develop",
            "--remote",
            "upstream",
            "--message",
            "chore: bootstrap repository",
            "--repo-root",
            str(tmp_path),
            "--source-dir",
            str(tmp_path / "source"),
            "--push",
            "--human-check",
            "approved",
            "--dry-run",
        ]
    )

    assert parsed.work_id == "issue-1"
    assert parsed.github_repo == "inabako/example"
    assert parsed.initial_branch == "develop"
    assert parsed.remote == "upstream"
    assert parsed.message == "chore: bootstrap repository"
    assert parsed.repo_root == str(tmp_path)
    assert parsed.source_dir == str(tmp_path / "source")
    assert parsed.push is True
    assert parsed.human_check == "approved"
    assert parsed.dry_run is True

    repo, _work_dir = make_work_repo(tmp_path)

    assert bootstrap_repository.main(
        [
            "--work-id",
            "issue-1",
            "--repo-root",
            str(repo),
            "--github-repo",
            "inabako/example",
            "--dry-run",
        ]
    ) == 0
    assert '"github_repo": "inabako/example"' in capsys.readouterr().out

    def fail_bootstrap(_args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(bootstrap_repository, "bootstrap_repository", fail_bootstrap)

    assert bootstrap_repository.main(["--work-id", "issue-1", "--dry-run"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(bootstrap_repository.__file__)))
    assert namespace["build_parser"]


def test_bootstrap_repository_requires_existing_work_directory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    args = argparse.Namespace(
        work_id="missing-work",
        github_repo="inabako/example",
        initial_branch="main",
        remote="origin",
        message="chore: bootstrap realtime iac repository",
        repo_root=str(repo),
        source_dir=None,
        push=False,
        human_check=None,
        dry_run=True,
    )

    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        bootstrap_repository.bootstrap_repository(args)


def test_bootstrap_repository_dry_run_uses_scm_state_repository_and_writes_record(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    (work_dir / "context" / "scm-state.json").write_text(
        json.dumps({"repository": "https://github.com/inabako/example.git", "target_branch": "develop"}),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo=None,
        initial_branch=None,
        remote=None,
        message="chore: bootstrap realtime iac repository",
        repo_root=str(repo),
        source_dir=None,
        push=False,
        human_check=None,
        dry_run=True,
    )

    result = bootstrap_repository.bootstrap_repository(args)

    assert result["github_repo"] == "inabako/example"
    assert result["repository"] == "https://github.com/inabako/example.git"
    assert result["current_branch"] == "develop"
    assert result["current_commit"] == "dry-run"
    assert result["pushed"] is False
    state = json.loads((work_dir / "context" / "scm-state.json").read_text(encoding="utf-8"))
    assert state["repository_mode"] == "precreated-new"
    assert state["bootstrap_record"].startswith("work/issue-1/process-report/bootstrap-repository-")
    assert (repo / result["record_path"]).exists()


def test_bootstrap_repository_rejects_workflow_repo_as_source(tmp_path: Path) -> None:
    repo, _ = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo="inabako/example",
        initial_branch="main",
        remote="origin",
        message="chore: bootstrap realtime iac repository",
        repo_root=str(repo),
        source_dir=str(repo),
        push=False,
        human_check=None,
        dry_run=True,
    )

    with pytest.raises(ValueError, match="workflow repository itself"):
        bootstrap_repository.bootstrap_repository(args)


def test_bootstrap_repository_requires_github_repo_when_state_is_empty(tmp_path: Path) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo=None,
        initial_branch="main",
        remote="origin",
        message="chore: bootstrap realtime iac repository",
        repo_root=str(repo),
        source_dir=str(work_dir / "source" / "repository"),
        push=False,
        human_check=None,
        dry_run=True,
    )

    with pytest.raises(ValueError, match="GitHub repository is required"):
        bootstrap_repository.bootstrap_repository(args)


def test_bootstrap_repository_set_remote_adds_or_updates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    calls: list[list[str]] = []
    get_url_returncode = 1

    def fake_run_git(args, cwd):
        calls.append(list(args))
        if args == ["remote", "get-url", "origin"]:
            return subprocess.CompletedProcess(["git", *args], get_url_returncode, stdout="", stderr="")
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(bootstrap_repository, "run_git", fake_run_git)

    bootstrap_repository.set_remote(source, "origin", "https://github.com/inabako/example.git", dry_run=False)
    assert calls == [
        ["remote", "get-url", "origin"],
        ["remote", "add", "origin", "https://github.com/inabako/example.git"],
    ]

    calls.clear()
    get_url_returncode = 0
    bootstrap_repository.set_remote(source, "origin", "https://github.com/inabako/example.git", dry_run=False)
    assert calls == [
        ["remote", "get-url", "origin"],
        ["remote", "set-url", "origin", "https://github.com/inabako/example.git"],
    ]


def test_bootstrap_repository_non_dry_run_commits_and_pushes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    calls: list[list[str]] = []

    def fake_run_git(args, cwd, env=None):
        calls.append(list(args))
        if args == ["remote", "get-url", "origin"]:
            return subprocess.CompletedProcess(["git", *args], 1, stdout="", stderr="")
        if args == ["status", "--short"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout="A docker-compose.yml\n", stderr="")
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(
        bootstrap_repository,
        "load_env",
        lambda repo_root: {
            "GITHUB_TOKEN": "token",
            "GIT_USER_NAME": "Ariadne",
            "GIT_USER_EMAIL": "ariadne@example.test",
        },
    )
    monkeypatch.setattr(bootstrap_repository, "run_git", fake_run_git)
    monkeypatch.setattr(bootstrap_repository, "is_git_repository", lambda path: False)
    monkeypatch.setattr(bootstrap_repository, "current_branch", lambda path: "main")
    monkeypatch.setattr(bootstrap_repository, "current_commit", lambda path: "commit123")
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo="inabako/example",
        initial_branch="main",
        remote="origin",
        message="chore: bootstrap realtime iac repository",
        repo_root=str(repo),
        source_dir=str(source),
        push=True,
        human_check="approved",
        dry_run=False,
    )

    result = bootstrap_repository.bootstrap_repository(args)

    assert result["pushed"] is True
    assert result["current_commit"] == "commit123"
    assert ["ls-remote", "https://github.com/inabako/example.git"] in calls
    assert ["init"] in calls
    assert ["checkout", "-B", "main"] in calls
    assert ["config", "user.name", "Ariadne"] in calls
    assert ["config", "user.email", "ariadne@example.test"] in calls
    assert ["add", "-A"] in calls
    assert ["commit", "-m", "chore: bootstrap realtime iac repository"] in calls
    assert ["remote", "add", "origin", "https://github.com/inabako/example.git"] in calls
    assert ["push", "-u", "origin", "main"] in calls


def test_bootstrap_repository_non_dry_run_skips_commit_when_head_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"
    calls: list[list[str]] = []

    def fake_run_git(args, cwd, env=None):
        calls.append(list(args))
        if args == ["status", "--short"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")
        if args == ["rev-parse", "--verify", "HEAD"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout="abc123\n", stderr="")
        if args == ["remote", "get-url", "origin"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout="https://github.com/inabako/example.git\n", stderr="")
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(bootstrap_repository, "run_git", fake_run_git)
    monkeypatch.setattr(bootstrap_repository, "load_env", lambda repo_root: {"GITHUB_TOKEN": "token"})
    monkeypatch.setattr(bootstrap_repository, "is_git_repository", lambda path: True)
    monkeypatch.setattr(bootstrap_repository, "current_branch", lambda path: "main")
    monkeypatch.setattr(bootstrap_repository, "current_commit", lambda path: "abc123")
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo="inabako/example",
        initial_branch="main",
        remote="origin",
        message="chore: bootstrap realtime iac repository",
        repo_root=str(repo),
        source_dir=str(source),
        push=False,
        human_check=None,
        dry_run=False,
    )

    result = bootstrap_repository.bootstrap_repository(args)

    assert result["current_commit"] == "abc123"
    assert ["rev-parse", "--verify", "HEAD"] in calls
    assert ["commit", "-m", "chore: bootstrap realtime iac repository"] not in calls
    assert ["remote", "set-url", "origin", "https://github.com/inabako/example.git"] in calls


def test_bootstrap_repository_non_dry_run_requires_files_when_no_head(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_work_repo(tmp_path)
    source = work_dir / "source" / "repository"

    def fake_run_git(args, cwd, env=None):
        if args == ["status", "--short"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")
        if args == ["rev-parse", "--verify", "HEAD"]:
            return subprocess.CompletedProcess(["git", *args], 1, stdout="", stderr="")
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    monkeypatch.setattr(bootstrap_repository, "run_git", fake_run_git)
    monkeypatch.setattr(bootstrap_repository, "load_env", lambda repo_root: {})
    monkeypatch.setattr(bootstrap_repository, "is_git_repository", lambda path: True)
    args = argparse.Namespace(
        work_id="issue-1",
        github_repo="inabako/example",
        initial_branch="main",
        remote="origin",
        message="chore: bootstrap realtime iac repository",
        repo_root=str(repo),
        source_dir=str(source),
        push=False,
        human_check=None,
        dry_run=False,
    )

    with pytest.raises(RuntimeError, match="No files to bootstrap"):
        bootstrap_repository.bootstrap_repository(args)
