from __future__ import annotations

import argparse
import json
import runpy
import subprocess
from pathlib import Path
from typing import Any

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


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "Task plan must be a JSON object"),
        ({}, "non-empty tasks array"),
        ({"tasks": []}, "non-empty tasks array"),
        ({"tasks": ["not-object"]}, "Each task must be a JSON object"),
        ({"tasks": [{"id": ""}]}, "non-empty id"),
        ({"tasks": [{"id": 123}]}, "non-empty id"),
        ({"tasks": [{"id": "a", "depends_on": "b"}]}, "depends_on must be a string array"),
        ({"tasks": [{"id": "a", "depends_on": [1]}]}, "depends_on must be a string array"),
    ],
)
def test_task_plan_rejects_invalid_shapes(tmp_path: Path, payload: Any, message: str) -> None:
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        task_runner.load_task_plan(path)


def test_task_plan_rejects_unknown_dependencies(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps({"tasks": [{"id": "a", "depends_on": ["missing"], "command": []}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown task dependencies"):
        task_runner.load_task_plan(path)


def test_task_plan_accepts_valid_dependencies_and_parser_options(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps(
            {
                "execution": {"mode": "parallel"},
                "tasks": [
                    {"id": "prepare"},
                    {"id": "verify", "depends_on": ["prepare"]},
                ],
            }
        ),
        encoding="utf-8",
    )

    assert task_runner.load_task_plan(path)["tasks"][1]["depends_on"] == ["prepare"]
    parsed = task_runner.build_parser().parse_args(
        [
            "--work-id",
            "issue-1",
            "--task-file",
            str(path),
            "--repo-root",
            str(tmp_path),
            "--mode",
            "sequential",
            "--max-workers",
            "1",
            "--dry-run",
            "--stop-on-failure",
        ]
    )

    assert parsed.mode == "sequential"
    assert parsed.max_workers == 1
    assert parsed.dry_run is True
    assert parsed.stop_on_failure is True


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


def test_run_defaults_auto_to_parallel_and_uses_agent_context(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo, work_dir = make_repo(tmp_path)
    (work_dir / "context" / "agent-context.json").write_text(
        json.dumps({"project": {"name": "Ariadne"}, "workflow": {"name": "retrieval"}}),
        encoding="utf-8",
    )
    task_file = work_dir / "context" / "tasks.json"
    task_file.write_text(json.dumps({"tasks": [{"id": "a"}]}), encoding="utf-8")
    calls: list[tuple[str, int]] = []

    def fake_run_parallel(
        tasks: list[dict[str, Any]],
        repo_root: Path,
        work_dir_arg: Path,
        report_dir: Path,
        dry_run: bool,
        max_workers: int,
        stop_on_failure: bool,
    ) -> list[task_runner.TaskResult]:
        calls.append((tasks[0]["id"], max_workers))
        return [
            task_runner.TaskResult(
                id="a",
                name="a",
                status="skipped",
                started_at="start",
                ended_at="end",
                duration_seconds=0.0,
                error="No command defined; task was treated as documentation/planning only.",
            )
        ]

    monkeypatch.setattr(task_runner, "run_parallel", fake_run_parallel)

    result = task_runner.run(
        argparse.Namespace(
            work_id="issue-1",
            task_file=str(task_file),
            repo_root=str(repo),
            mode="auto",
            max_workers=3,
            dry_run=False,
            stop_on_failure=False,
        )
    )

    assert result["execution_mode"] == "parallel"
    assert result["summary"] == {"total": 1, "failed": 0, "blocked": 0}
    assert calls == [("a", 3)]
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    assert artifact_index["project"] == "Ariadne"
    assert artifact_index["workflow"] == "retrieval"


def test_run_rejects_missing_work_dir_and_unsupported_mode(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    task_file = repo / "tasks.json"
    task_file.write_text(json.dumps({"tasks": [{"id": "a"}]}), encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        task_runner.run(
            argparse.Namespace(
                work_id="missing",
                task_file=str(task_file),
                repo_root=str(repo),
                mode="parallel",
                max_workers=1,
                dry_run=True,
                stop_on_failure=False,
            )
        )

    _, work_dir = make_repo(tmp_path / "repo2", work_id="issue-2")
    invalid_task_file = work_dir / "context" / "tasks.json"
    invalid_task_file.write_text(json.dumps({"tasks": [{"id": "a"}]}), encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported execution mode"):
        task_runner.run(
            argparse.Namespace(
                work_id="issue-2",
                task_file=str(invalid_task_file),
                repo_root=str(work_dir.parents[1]),
                mode="serial",
                max_workers=1,
                dry_run=True,
                stop_on_failure=False,
            )
        )


def test_run_one_task_records_failure_logs(tmp_path: Path) -> None:
    repo, work_dir = make_repo(tmp_path)
    report_dir = work_dir / "process-report"
    task = {"id": "bad", "name": "Bad command", "command": ["definitely-missing-command"], "cwd": str(work_dir)}

    result = task_runner.run_one_task(task, repo, work_dir, report_dir, dry_run=False)

    assert result.status == "failed"
    assert result.stderr_path is not None
    assert (repo / result.stderr_path).exists()


def test_run_one_task_skips_missing_command_and_rejects_missing_cwd(tmp_path: Path) -> None:
    repo, work_dir = make_repo(tmp_path)
    skipped = task_runner.run_one_task(
        {"id": "doc", "outputs": ["docs/out.md"]},
        repo,
        work_dir,
        work_dir / "process-report",
        dry_run=False,
    )

    assert skipped.status == "skipped"
    assert skipped.error and "No command defined" in skipped.error
    assert skipped.outputs == ["docs/out.md"]

    with pytest.raises(FileNotFoundError, match="cwd does not exist"):
        task_runner.run_one_task(
            {"id": "bad-cwd", "command": ["tool"], "cwd": str(work_dir / "missing")},
            repo,
            work_dir,
            work_dir / "process-report",
            dry_run=False,
        )


def test_run_one_task_records_success_and_returncode_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_repo(tmp_path)
    calls: list[dict[str, Any]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append({"command": command, **kwargs})
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(task_runner.subprocess, "run", fake_run)
    result = task_runner.run_one_task(
        {
            "id": "good",
            "name": "Good task",
            "command": "tool --flag",
            "cwd": str(work_dir),
            "timeout_seconds": 12,
            "outputs": ["build/out.txt"],
        },
        repo,
        work_dir,
        work_dir / "process-report",
        dry_run=False,
    )

    assert result.status == "success"
    assert result.returncode == 0
    assert result.error is None
    assert result.stdout_path and (repo / result.stdout_path).read_text(encoding="utf-8-sig") == "ok"
    assert calls[0]["command"] == ["tool", "--flag"]
    assert calls[0]["timeout"] == 12

    def fake_failed(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 7, stdout="", stderr="bad")

    monkeypatch.setattr(task_runner.subprocess, "run", fake_failed)
    failed = task_runner.run_one_task(
        {"id": "exit7", "command": ["tool"], "cwd": str(work_dir), "timeout_seconds": "invalid"},
        repo,
        work_dir,
        work_dir / "process-report",
        dry_run=False,
    )

    assert failed.status == "failed"
    assert failed.returncode == 7
    assert failed.error == "Command exited with 7."


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


def test_sequential_blocks_failed_dependency_and_detects_cycle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_repo(tmp_path)

    def fake_run_one_task(task, repo_root, work_dir_arg, report_dir, dry_run):
        status = "failed" if task["id"] == "a" else "success"
        return task_runner.TaskResult(
            id=task["id"],
            name=task_runner.task_name(task),
            status=status,
            started_at="now",
            ended_at="now",
            duration_seconds=0,
        )

    monkeypatch.setattr(task_runner, "run_one_task", fake_run_one_task)
    results = task_runner.run_sequential(
        [{"id": "a"}, {"id": "b", "depends_on": ["a"]}],
        repo,
        work_dir,
        work_dir / "process-report",
        dry_run=False,
        stop_on_failure=False,
    )

    assert [(result.id, result.status) for result in results] == [("a", "failed"), ("b", "blocked")]
    assert results[1].error == "Blocked by failed dependencies: a"

    with pytest.raises(ValueError, match="dependency cycle"):
        task_runner.run_sequential(
            [{"id": "a", "depends_on": ["b"]}, {"id": "b", "depends_on": ["a"]}],
            repo,
            work_dir,
            work_dir / "process-report",
            dry_run=False,
            stop_on_failure=False,
        )


def test_parallel_blocks_failed_dependency_and_stop_on_failure_pending(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo, work_dir = make_repo(tmp_path)

    def fake_run_one_task(task, repo_root, work_dir_arg, report_dir, dry_run):
        return task_runner.TaskResult(
            id=task["id"],
            name=task["id"],
            status="failed" if task["id"] == "a" else "success",
            started_at="now",
            ended_at="now",
            duration_seconds=0,
        )

    monkeypatch.setattr(task_runner, "run_one_task", fake_run_one_task)

    dependency_results = task_runner.run_parallel(
        [{"id": "a"}, {"id": "b", "depends_on": ["a"]}],
        repo,
        work_dir,
        work_dir / "process-report",
        dry_run=False,
        max_workers=0,
        stop_on_failure=False,
    )
    assert [(result.id, result.status) for result in dependency_results] == [("a", "failed"), ("b", "blocked")]
    assert dependency_results[1].error == "Blocked by failed dependencies: a"

    stopped_results = task_runner.run_parallel(
        [{"id": "a"}, {"id": "b", "depends_on": ["a"]}],
        repo,
        work_dir,
        work_dir / "process-report",
        dry_run=False,
        max_workers=1,
        stop_on_failure=True,
    )
    assert [(result.id, result.status) for result in stopped_results] == [("a", "failed"), ("b", "blocked")]
    assert stopped_results[1].error == "Stopped after previous task failure."

    with pytest.raises(ValueError, match="dependency cycle"):
        task_runner.run_parallel(
            [{"id": "a", "depends_on": ["b"]}, {"id": "b", "depends_on": ["a"]}],
            repo,
            work_dir,
            work_dir / "process-report",
            dry_run=False,
            max_workers=1,
            stop_on_failure=False,
        )


def test_result_to_dict_and_write_reports_include_optional_fields(tmp_path: Path) -> None:
    repo, work_dir = make_repo(tmp_path)
    task_file = work_dir / "context" / "tasks.json"
    task_file.write_text(json.dumps({"tasks": [{"id": "a"}]}), encoding="utf-8")
    result = task_runner.TaskResult(
        id="a",
        name="Named | task",
        status="failed",
        started_at="start",
        ended_at="end",
        duration_seconds=1.25,
        returncode=9,
        stdout_path="work/issue-1/process-report/logs/a.stdout.txt",
        stderr_path="work/issue-1/process-report/logs/a.stderr.txt",
        error="pipe | escaped",
        outputs=["out.txt"],
    )

    data = task_runner.result_to_dict(result)
    assert data["returncode"] == 9
    assert data["stdout_path"].endswith("a.stdout.txt")
    assert data["stderr_path"].endswith("a.stderr.txt")
    assert data["error"] == "pipe | escaped"

    _, md_path = task_runner.write_reports(repo, work_dir, task_file, "parallel", [result])
    markdown = md_path.read_text(encoding="utf-8-sig")
    assert "| failed | 1 |" in markdown
    assert "pipe \\| escaped" in markdown


def test_main_prints_json_and_reports_errors(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(
        task_runner,
        "run",
        lambda args: {
            "work_id": args.work_id,
            "execution_mode": "parallel",
            "json_report": "work/issue-1/process-report/run.json",
            "markdown_report": "work/issue-1/process-report/run.md",
            "summary": {"total": 0, "failed": 0, "blocked": 0},
        },
    )

    assert task_runner.main(["--work-id", "issue-1", "--task-file", "tasks.json"]) == 0
    stdout = capsys.readouterr().out
    assert '"work_id": "issue-1"' in stdout

    def raise_error(args):
        raise RuntimeError("boom")

    monkeypatch.setattr(task_runner, "run", raise_error)

    assert task_runner.main(["--work-id", "issue-1", "--task-file", "tasks.json"]) == 1
    stderr = capsys.readouterr().err
    assert "ERROR: boom" in stderr

    namespace = runpy.run_path(str(Path(task_runner.__file__)))
    assert namespace["build_parser"]


def test_normalize_command_accepts_string_and_array() -> None:
    assert task_runner.normalize_command(["python", "-m", "pytest"]) == ["python", "-m", "pytest"]
    assert task_runner.normalize_command("python -m pytest") == ["python", "-m", "pytest"]

    with pytest.raises(ValueError, match="task.command"):
        task_runner.normalize_command({"command": "pytest"})
