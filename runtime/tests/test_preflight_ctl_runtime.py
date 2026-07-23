from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.ctl import ctl
from runtime.environment import preflight


def latest_runtime_event(repo: Path) -> dict[str, object]:
    line = (repo / "logs" / "runtime" / "runtime-events.log").read_text(encoding="utf-8").splitlines()[-1]
    return json.loads(line.split(" | ", 3)[3])


def test_ctl_preflight_runs_environment_preflight_and_writes_runtime_log(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(
        preflight,
        "build_checks",
        lambda args, repo_root: [
            preflight.Check(
                id="exe:git",
                label="git",
                kind="executable",
                required=True,
                ok=True,
                detected="C:/tools/git.exe",
                install_hint="install git",
            )
        ],
    )
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "preflight",
            "--profile",
            "github-cli",
            "--work-id",
            "issue-1",
        ]
    )

    code, output = ctl.run(args)

    result = json.loads(output)
    assert code == 0
    assert result["profile"] == "github-cli"
    assert result["status"] == "ready"
    assert result["record_path"].startswith("work/issue-1/process-report/")
    completed = latest_runtime_event(repo)
    assert completed["command"] == "preflight"
    assert completed["operation_id"] == "preflight"
    assert completed["input"]["work_id"] == "issue-1"


def test_ctl_preflight_returns_blocked_when_required_tool_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(
        preflight,
        "build_checks",
        lambda args, repo_root: [
            preflight.Check(
                id="exe:uv",
                label="uv",
                kind="executable",
                required=True,
                ok=False,
                detected="",
                install_hint="install uv",
                install_command="install uv",
            )
        ],
    )
    args = ctl.build_parser().parse_args(["--repo-root", str(repo), "preflight", "--profile", "runtime-dev"])

    code, output = ctl.run(args)

    result = json.loads(output)
    assert code == 2
    assert result["status"] == "install-list-required"
    assert result["gate_restart"]["restart_from"] == "environment-preflight-gate"
    completed = latest_runtime_event(repo)
    assert completed["command"] == "preflight"
    assert completed["output"]["status"] == "blocked"
