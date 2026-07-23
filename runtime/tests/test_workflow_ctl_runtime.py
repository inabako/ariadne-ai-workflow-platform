from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl


def latest_runtime_event(repo: Path) -> dict[str, object]:
    line = (repo / "logs" / "runtime" / "runtime-events.log").read_text(encoding="utf-8").splitlines()[-1]
    return json.loads(line.split(" | ", 3)[3])


def test_ctl_workflow_state_set_writes_state_and_runtime_log(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "workflow",
            "state",
            "--work-dir",
            "work/issue-1",
            "set",
            "--workflow",
            "docs-sync",
            "--work-id",
            "issue-1",
            "--phase",
            "analysis",
            "--status",
            "in-progress",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["state"]["phase"] == "analysis"
    assert (repo / result["state_path"]).exists()
    completed = latest_runtime_event(repo)
    assert completed["command"] == "workflow state set"
    assert completed["operation_id"] == "workflow:state:set"


def test_ctl_workflow_docs_sync_init_creates_contexts(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "workflow",
            "docs-sync",
            "init",
            "--repository",
            "owner/repo",
            "--target-branch",
            "feature/docs",
            "--work-id",
            "docs-feature",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["work_id"] == "docs-feature"
    assert (repo / "work" / "docs-feature" / "context" / "agent-context.json").exists()


def test_ctl_workflow_iac_handoff_creates_execution_plan(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "workflow",
            "iac-handoff",
            "create",
            "--work-id",
            "issue-iac",
            "--validator-judgment",
            "pass",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["status"] == "ready-for-human-check"
    assert (repo / result["execution_plan"]).exists()
    assert "execution-plan" in result["manifest_contexts"]


def test_ctl_workflow_validate_vscode_workspace_checks_json(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    vscode = repo / ".vscode"
    vscode.mkdir(parents=True)
    for name in ["settings.json", "tasks.json", "launch.json", "extensions.json"]:
        (vscode / name).write_text("{}", encoding="utf-8")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "workflow",
            "validate-vscode-workspace",
            "check",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["status"] == "ok"
    assert result["validated_files"] == [
        ".vscode/settings.json",
        ".vscode/tasks.json",
        ".vscode/launch.json",
        ".vscode/extensions.json",
    ]
