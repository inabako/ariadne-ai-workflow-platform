from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl


def latest_runtime_event(repo: Path) -> dict[str, object]:
    line = (repo / "logs" / "runtime" / "runtime-events.log").read_text(encoding="utf-8").splitlines()[-1]
    return json.loads(line.split(" | ", 3)[3])


def test_ctl_gui_init_input_writes_inbox_readme_and_runtime_log(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "gui",
            "init-input",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["status"] == "ready"
    assert (repo / result["readme"]).exists()
    completed = latest_runtime_event(repo)
    assert completed["command"] == "gui init-input"
    assert completed["operation_id"] == "gui:init-input"


def test_ctl_gui_self_test_runs_runtime_checks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "gui",
            "self-test",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["status"] == "pass"
    assert "generate-and-validate" in result["checks"]


def test_ctl_web_svg_run_skips_without_matching_svg(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    work_dir = repo / "work" / "SYS-101"
    work_dir.mkdir(parents=True)
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "web-svg",
            "run",
            "--issue-id",
            "SYS-101",
            "--skip-context-check",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["status"] == "skipped"
    assert result["input_prefix"] == "WEB_SYS"
    assert (work_dir / "context" / "web-svg-layout-state.json").exists()
    completed = latest_runtime_event(repo)
    assert completed["command"] == "web-svg run"
    assert completed["operation_id"] == "web-svg:run"
