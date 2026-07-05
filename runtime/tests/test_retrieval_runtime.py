from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pytest

from runtime.retrieval import task_runner


def make_repo(tmp_path: Path, work_id: str = "issue-1") -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    work_dir = repo / "work" / work_id
    (repo / ".git").mkdir(parents=True)
    (work_dir / "context").mkdir(parents=True)
    (work_dir / "process-report").mkdir(parents=True)
    return repo, work_dir


def test_task_plan_rejects_duplicate_task_ids(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps({"tasks": [{"id": "a", "command": []}, {"id": "a", "command": []}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate task id"):
        task_runner.load_task_plan(path)


def test_task_plan_rejects_unknown_dependencies(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps({"tasks": [{"id": "a", "depends_on": ["missing"], "command": []}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown task dependencies"):
        task_runner.load_task_plan(path)


def test_task_runner_dry_run_writes_reports_and_artifact_index(tmp_path: Path) -> None:
    repo, work_dir = make_repo(tmp_path)
    task_file = repo / "work" / "issue-1" / "context" / "tasks.json"
    task_file.write_text(
        json.dumps(
            {
                "execution": {"mode": "sequential"},
                "tasks": [
                    {"id": "plan", "name": "Plan only", "outputs": ["docs/plan.md"]},
                    {"id": "test", "name": "Test only", "depends_on": ["plan"], "command": ["pytest"]},
                ],
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        work_id="issue-1",
        task_file=str(task_file),
        repo_root=str(repo),
        mode="auto",
        max_workers=2,
        dry_run=True,
        stop_on_failure=False,
    )

    result = task_runner.run(args)

    assert result["execution_mode"] == "sequential"
    assert result["summary"] == {"total": 2, "failed": 0, "blocked": 0}
    assert (repo / result["json_report"]).exists()
    assert (repo / result["markdown_report"]).exists()
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    assert {artifact["id"].split("-task-run-")[0] for artifact in artifact_index["artifacts"]} == {
        "TASK-RUN-JSON",
        "TASK-RUN-MD",
    }


def test_run_one_task_records_failure_logs(tmp_path: Path) -> None:
    repo, work_dir = make_repo(tmp_path)
    report_dir = work_dir / "process-report"
    task = {"id": "bad", "name": "Bad command", "command": ["definitely-missing-command"], "cwd": str(work_dir)}

    result = task_runner.run_one_task(task, repo, work_dir, report_dir, dry_run=False)

    assert result.status == "failed"
    assert result.stderr_path is not None
    assert (repo / result.stderr_path).exists()


def test_sequential_stop_on_failure_blocks_remaining(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo, work_dir = make_repo(tmp_path)

    def fake_run_one_task(task, repo_root, work_dir_arg, report_dir, dry_run):
        return task_runner.TaskResult(
            id=task["id"],
            name=task["id"],
            status="failed",
            started_at="now",
            ended_at="now",
            duration_seconds=0,
            returncode=1,
        )

    monkeypatch.setattr(task_runner, "run_one_task", fake_run_one_task)
    results = task_runner.run_sequential(
        [{"id": "a"}, {"id": "b"}],
        repo,
        work_dir,
        work_dir / "process-report",
        dry_run=False,
        stop_on_failure=True,
    )

    assert [result.status for result in results] == ["failed", "blocked"]


def test_normalize_command_accepts_string_and_array() -> None:
    assert task_runner.normalize_command(["python", "-m", "pytest"]) == ["python", "-m", "pytest"]
    assert task_runner.normalize_command("python -m pytest") == ["python", "-m", "pytest"]

    with pytest.raises(ValueError, match="task.command"):
        task_runner.normalize_command({"command": "pytest"})
