from __future__ import annotations

import argparse
import concurrent.futures
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.constants.runtime_values import DURATION_SECONDS_DEFAULT, SCHEMA_VERSION  # noqa: E402
from runtime.common import (  # noqa: E402
    find_repo_root,
    load_artifact_index,
    local_timestamp,
    read_json,
    relative_to_repo,
    upsert_artifact,
    utc_now_iso,
    write_json,
    write_markdown_bom,
)
from runtime.constants.cli_defaults import (  # noqa: E402
    TASK_RUNNER_DURATION_DECIMALS,
    TASK_RUNNER_MAX_WORKERS_DEFAULT,
    TASK_RUNNER_MIN_WORKERS,
    TASK_RUNNER_POLL_TIMEOUT_SECONDS,
)
from runtime.constants.workspace import context_dir_for_work_dir, process_report_dir_for_work_dir, work_dir_for_id, work_path_pattern  # noqa: E402


TERMINAL_FAILURE = {"failed", "blocked"}


@dataclass
class TaskResult:
    id: str
    name: str
    status: str
    started_at: str
    ended_at: str
    duration_seconds: float
    returncode: int | None = None
    stdout_path: str | None = None
    stderr_path: str | None = None
    error: str | None = None
    outputs: list[str] = field(default_factory=list)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run workflow tasks sequentially or in parallel and write process reports."
    )
    parser.add_argument("--work-id", required=True, help=f"Receipt/work ID under {work_path_pattern(work_id='<id>')}.")
    parser.add_argument("--task-file", required=True, help="JSON task plan file.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument(
        "--mode",
        default="auto",
        choices=["auto", "sequential", "parallel"],
        help="Execution mode. auto uses task plan execution.mode or parallel by default.",
    )
    parser.add_argument("--max-workers", type=int, default=TASK_RUNNER_MAX_WORKERS_DEFAULT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stop-on-failure", action="store_true")
    return parser


def normalize_command(command: Any) -> list[str]:
    if isinstance(command, list) and all(isinstance(item, str) for item in command):
        return command
    if isinstance(command, str):
        import shlex

        return shlex.split(command, posix=False)
    raise ValueError("task.command must be a string array or command string")


def load_task_plan(path: Path) -> dict[str, Any]:
    plan = read_json(path)
    if not isinstance(plan, dict):
        raise ValueError("Task plan must be a JSON object.")
    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Task plan must contain a non-empty tasks array.")
    seen: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Each task must be a JSON object.")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("Each task must have a non-empty id.")
        if task_id in seen:
            raise ValueError(f"Duplicate task id: {task_id}")
        seen.add(task_id)
        depends_on = task.get("depends_on", [])
        if not isinstance(depends_on, list) or not all(isinstance(item, str) for item in depends_on):
            raise ValueError(f"Task {task_id} depends_on must be a string array.")
    unknown_deps = {
        dep
        for task in tasks
        for dep in task.get("depends_on", [])
        if dep not in seen
    }
    if unknown_deps:
        raise ValueError(f"Unknown task dependencies: {', '.join(sorted(unknown_deps))}")
    return plan


def task_name(task: dict[str, Any]) -> str:
    return str(task.get("name") or task["id"])


def run_one_task(
    task: dict[str, Any],
    repo_root: Path,
    work_dir: Path,
    report_dir: Path,
    dry_run: bool,
) -> TaskResult:
    started_iso = utc_now_iso()
    started = time.perf_counter()
    task_id = task["id"]
    name = task_name(task)

    if dry_run or not task.get("command"):
        ended_iso = utc_now_iso()
        return TaskResult(
            id=task_id,
            name=name,
            status="planned" if dry_run else "skipped",
            started_at=started_iso,
            ended_at=ended_iso,
            duration_seconds=round(time.perf_counter() - started, TASK_RUNNER_DURATION_DECIMALS),
            outputs=list(task.get("outputs", [])),
            error=None if dry_run else "No command defined; task was treated as documentation/planning only.",
        )

    stdout_path = report_dir / "logs" / f"{task_id}.stdout.txt"
    stderr_path = report_dir / "logs" / f"{task_id}.stderr.txt"
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)

    cwd = Path(task.get("cwd") or work_dir).resolve()
    if not cwd.exists():
        raise FileNotFoundError(f"Task {task_id} cwd does not exist: {cwd}")

    command = normalize_command(task["command"])
    timeout = task.get("timeout_seconds")
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout if isinstance(timeout, (int, float)) else None,
            shell=False,
        )
        stdout_path.write_text(completed.stdout or "", encoding="utf-8-sig")
        stderr_path.write_text(completed.stderr or "", encoding="utf-8-sig")
        status = "success" if completed.returncode == 0 else "failed"
        error = None if completed.returncode == 0 else f"Command exited with {completed.returncode}."
        returncode = completed.returncode
    except Exception as exc:
        stdout_path.write_text("", encoding="utf-8-sig")
        stderr_path.write_text(str(exc), encoding="utf-8-sig")
        status = "failed"
        error = str(exc)
        returncode = None

    ended_iso = utc_now_iso()
    return TaskResult(
        id=task_id,
        name=name,
        status=status,
        started_at=started_iso,
        ended_at=ended_iso,
        duration_seconds=round(time.perf_counter() - started, TASK_RUNNER_DURATION_DECIMALS),
        returncode=returncode,
        stdout_path=relative_to_repo(repo_root, stdout_path),
        stderr_path=relative_to_repo(repo_root, stderr_path),
        error=error,
        outputs=list(task.get("outputs", [])),
    )


def blocked_result(task: dict[str, Any], reason: str) -> TaskResult:
    now = utc_now_iso()
    return TaskResult(
        id=task["id"],
        name=task_name(task),
        status="blocked",
        started_at=now,
        ended_at=now,
        duration_seconds=DURATION_SECONDS_DEFAULT,
        error=reason,
        outputs=list(task.get("outputs", [])),
    )


def run_sequential(
    tasks: list[dict[str, Any]],
    repo_root: Path,
    work_dir: Path,
    report_dir: Path,
    dry_run: bool,
    stop_on_failure: bool,
) -> list[TaskResult]:
    results: list[TaskResult] = []
    result_by_id: dict[str, TaskResult] = {}
    remaining = tasks[:]

    while remaining:
        progressed = False
        for task in remaining[:]:
            deps = task.get("depends_on", [])
            if not all(dep in result_by_id for dep in deps):
                continue
            failed_deps = [dep for dep in deps if result_by_id[dep].status in TERMINAL_FAILURE]
            if failed_deps:
                result = blocked_result(task, f"Blocked by failed dependencies: {', '.join(failed_deps)}")
            else:
                result = run_one_task(task, repo_root, work_dir, report_dir, dry_run)
            results.append(result)
            result_by_id[result.id] = result
            remaining.remove(task)
            progressed = True
            if stop_on_failure and result.status in TERMINAL_FAILURE:
                for blocked in remaining:
                    blocked_result_item = blocked_result(blocked, f"Stopped after failure in task {result.id}.")
                    results.append(blocked_result_item)
                    result_by_id[blocked_result_item.id] = blocked_result_item
                remaining.clear()
                break
        if remaining and not progressed:
            raise ValueError("Task plan has a dependency cycle or unresolved ordering.")
    return results


def run_parallel(
    tasks: list[dict[str, Any]],
    repo_root: Path,
    work_dir: Path,
    report_dir: Path,
    dry_run: bool,
    max_workers: int,
    stop_on_failure: bool,
) -> list[TaskResult]:
    task_by_id = {task["id"]: task for task in tasks}
    pending = set(task_by_id)
    running: dict[concurrent.futures.Future[TaskResult], str] = {}
    results: list[TaskResult] = []
    result_by_id: dict[str, TaskResult] = {}
    stopped = False

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(TASK_RUNNER_MIN_WORKERS, max_workers)) as executor:
        while pending or running:
            ready_ids: list[str] = []
            if not stopped:
                for task_id in sorted(pending):
                    task = task_by_id[task_id]
                    deps = task.get("depends_on", [])
                    if not all(dep in result_by_id for dep in deps):
                        continue
                    failed_deps = [dep for dep in deps if result_by_id[dep].status in TERMINAL_FAILURE]
                    if failed_deps:
                        result = blocked_result(task, f"Blocked by failed dependencies: {', '.join(failed_deps)}")
                        result_by_id[task_id] = result
                        results.append(result)
                    else:
                        future = executor.submit(run_one_task, task, repo_root, work_dir, report_dir, dry_run)
                        running[future] = task_id
                    ready_ids.append(task_id)
                for task_id in ready_ids:
                    pending.discard(task_id)

            if not running:
                if pending and stopped:
                    for task_id in sorted(pending):
                        task = task_by_id[task_id]
                        result = blocked_result(task, "Stopped after previous task failure.")
                        result_by_id[task_id] = result
                        results.append(result)
                    pending.clear()
                elif pending:
                    raise ValueError("Task plan has a dependency cycle or unresolved ordering.")
                continue

            done, _ = concurrent.futures.wait(
                running,
                timeout=TASK_RUNNER_POLL_TIMEOUT_SECONDS,
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            for future in done:
                task_id = running.pop(future)
                result = future.result()
                result_by_id[task_id] = result
                results.append(result)
                if stop_on_failure and result.status in TERMINAL_FAILURE:
                    stopped = True
    return results


def result_to_dict(result: TaskResult) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": result.id,
        "name": result.name,
        "status": result.status,
        "started_at": result.started_at,
        "ended_at": result.ended_at,
        "duration_seconds": result.duration_seconds,
        "outputs": result.outputs,
    }
    if result.returncode is not None:
        data["returncode"] = result.returncode
    if result.stdout_path:
        data["stdout_path"] = result.stdout_path
    if result.stderr_path:
        data["stderr_path"] = result.stderr_path
    if result.error:
        data["error"] = result.error
    return data


def write_reports(
    repo_root: Path,
    work_dir: Path,
    task_file: Path,
    mode: str,
    results: list[TaskResult],
) -> tuple[Path, Path]:
    report_root = process_report_dir_for_work_dir(work_dir)
    run_id = f"task-run-{local_timestamp()}"
    json_path = report_root / f"{run_id}.json"
    md_path = report_root / f"{run_id}.md"

    summary = {
        "total": len(results),
        "success": sum(1 for item in results if item.status == "success"),
        "planned": sum(1 for item in results if item.status == "planned"),
        "skipped": sum(1 for item in results if item.status == "skipped"),
        "failed": sum(1 for item in results if item.status == "failed"),
        "blocked": sum(1 for item in results if item.status == "blocked"),
    }
    result_data = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "task_file": relative_to_repo(repo_root, task_file),
        "execution_mode": mode,
        "created_at": utc_now_iso(),
        "summary": summary,
        "tasks": [result_to_dict(item) for item in results],
    }
    write_json(json_path, result_data)

    lines = [
        "# Task Run Report",
        "",
        f"- Run ID: `{run_id}`",
        f"- Task file: `{relative_to_repo(repo_root, task_file)}`",
        f"- Execution mode: `{mode}`",
        f"- Created at: `{result_data['created_at']}`",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for key in ["success", "planned", "skipped", "failed", "blocked", "total"]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.extend(
        [
            "",
            "## Tasks",
            "",
            "| ID | Name | Status | Duration | Notes |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for result in results:
        note = (result.error or "").replace("|", "\\|")
        lines.append(f"| `{result.id}` | {result.name} | {result.status} | {result.duration_seconds} | {note} |")
    write_markdown_bom(md_path, "\n".join(lines))
    return json_path, md_path


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = work_dir_for_id(repo_root, args.work_id)
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    task_file = Path(args.task_file).resolve()
    plan = load_task_plan(task_file)
    tasks = plan["tasks"]
    selected_mode = args.mode
    if selected_mode == "auto":
        selected_mode = str(plan.get("execution", {}).get("mode") or "parallel")

    report_dir = process_report_dir_for_work_dir(work_dir)
    if selected_mode == "sequential":
        results = run_sequential(tasks, repo_root, work_dir, report_dir, args.dry_run, args.stop_on_failure)
    elif selected_mode == "parallel":
        results = run_parallel(
            tasks,
            repo_root,
            work_dir,
            report_dir,
            args.dry_run,
            args.max_workers,
            args.stop_on_failure,
        )
    else:
        raise ValueError(f"Unsupported execution mode: {selected_mode}")

    json_report, md_report = write_reports(repo_root, work_dir, task_file, selected_mode, results)

    context_dir = context_dir_for_work_dir(work_dir)
    agent_context = read_json(context_dir / "agent-context.json", default={}) or {}
    project_name = agent_context.get("project", {}).get("name", args.work_id)
    workflow_name = agent_context.get("workflow", {}).get("name", "")
    artifact_index = load_artifact_index(work_dir, project_name, workflow_name)
    now = utc_now_iso()
    for artifact_id, title, path in [
        ("TASK-RUN-JSON", json_report.name, json_report),
        ("TASK-RUN-MD", md_report.name, md_report),
    ]:
        upsert_artifact(
            artifact_index,
            {
                "id": f"{artifact_id}-{json_report.stem}",
                "title": title,
                "path": relative_to_repo(repo_root, path),
                "type": "report",
                "status": "draft",
                "owner_agent": "runtime-retrieval",
                "created_at": now,
                "updated_at": now,
                "depends_on": [relative_to_repo(repo_root, task_file)],
                "consumed_by": [],
                "summary": "Task execution report generated by runtime retrieval.",
                "unresolved_items": [result.id for result in results if result.status in TERMINAL_FAILURE],
            },
        )
    write_json(context_dir / "artifact-index.json", artifact_index)

    return {
        "work_id": args.work_id,
        "execution_mode": selected_mode,
        "json_report": relative_to_repo(repo_root, json_report),
        "markdown_report": relative_to_repo(repo_root, md_report),
        "summary": {
            "total": len(results),
            "failed": sum(1 for item in results if item.status == "failed"),
            "blocked": sum(1 for item in results if item.status == "blocked"),
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
