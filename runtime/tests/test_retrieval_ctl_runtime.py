from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl


def latest_runtime_event(repo: Path) -> dict[str, object]:
    line = (repo / "logs" / "runtime" / "runtime-events.log").read_text(encoding="utf-8").splitlines()[-1]
    return json.loads(line.split(" | ", 3)[3])


def test_ctl_retrieval_run_writes_task_reports_and_runtime_log(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    work_dir = repo / "work" / "issue-1"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    task_file = context_dir / "task-plan.json"
    task_file.write_text(
        json.dumps(
            {
                "execution": {"mode": "sequential"},
                "tasks": [{"id": "plan", "name": "Plan task"}],
            }
        ),
        encoding="utf-8",
    )
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "retrieval",
            "run",
            "--work-id",
            "issue-1",
            "--task-file",
            "work/issue-1/context/task-plan.json",
            "--dry-run",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    result = json.loads(output)
    assert code == 0
    assert result["work_id"] == "issue-1"
    assert result["execution_mode"] == "sequential"
    assert result["summary"]["total"] == 1
    assert (repo / result["json_report"]).exists()
    assert (repo / result["markdown_report"]).exists()
    completed = latest_runtime_event(repo)
    assert completed["command"] == "retrieval run"
    assert completed["operation_id"] == "retrieval:run"


def test_ctl_retrieval_run_reports_missing_work_directory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_file = repo / "task-plan.json"
    task_file.write_text(json.dumps({"tasks": [{"id": "plan"}]}), encoding="utf-8")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "retrieval",
            "run",
            "--work-id",
            "missing",
            "--task-file",
            str(task_file),
        ]
    )

    code, output = ctl.run(args)

    assert code == 1
    assert "Retrieval runtime failed" in output
    completed = latest_runtime_event(repo)
    assert completed["command"] == "retrieval run"
    assert completed["output"]["status"] == "failed"
