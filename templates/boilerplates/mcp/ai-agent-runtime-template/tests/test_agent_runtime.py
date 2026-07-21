from __future__ import annotations

import json
from pathlib import Path

from local_agent_runtime.completion import CompletionEvaluator
from local_agent_runtime.commands import CommandAPI
from local_agent_runtime.jobs import Job, JobState
from local_agent_runtime.retry import RetryPolicy
from local_agent_runtime.runtime import AgentRuntime
from local_agent_runtime.runtime_clock import RuntimeClock
from local_agent_runtime.storage import SQLiteJobStore
from local_agent_runtime.worker import WorkerLeaseManager
from local_agent_runtime.workflow import Workflow, WorkflowEngine, WorkflowStep


def test_workflow_runs_steps_and_completion_uses_evidence(tmp_path: Path) -> None:
    workflow = Workflow(
        name="analysis",
        steps=[
            WorkflowStep(name="inspect", action="inspect"),
            WorkflowStep(name="report", action="report", produces_artifact="analysis-report.md"),
        ],
        required_artifacts=["analysis-report.md"],
    )
    runtime = AgentRuntime(tmp_path / "checkpoints")

    job, result = runtime.submit_and_run("analyze repo", workflow)

    assert result.complete is True
    assert job.state == JobState.COMPLETED
    assert job.completed_steps == ["inspect", "report"]
    checkpoint = json.loads((tmp_path / "checkpoints" / f"{job.job_id}.json").read_text(encoding="utf-8"))
    assert checkpoint["state"] == "completed"
    assert runtime.artifacts.paths_for(job.job_id) == ["analysis-report.md"]
    assert runtime.events.events[-1]["event_type"] == "job.finished"
    assert (tmp_path / "evidence" / f"{job.job_id}-completion.json").exists()
    assert runtime.job_store.load(job.job_id).state == JobState.COMPLETED


def test_human_check_pauses_at_safe_boundary() -> None:
    workflow = Workflow(
        name="unsafe",
        steps=[WorkflowStep(name="overwrite", action="overwrite file", requires_human_check=True)],
    )
    job = Job(goal="change file", workflow_name="unsafe")

    WorkflowEngine().run_until_blocked_or_complete(job, workflow)

    assert job.state == JobState.WAITING_HUMAN
    assert job.completed_steps == []
    assert job.human_check_request is not None


def test_model_self_report_does_not_complete_job() -> None:
    workflow = Workflow(
        name="report",
        steps=[WorkflowStep(name="report", action="write report", produces_artifact="report.md")],
        required_artifacts=["report.md"],
    )
    job = Job(goal="write report", workflow_name="report", model_claimed_done=True)

    result = CompletionEvaluator().evaluate(job, workflow)

    assert result.complete is False
    assert result.missing_steps == ["report"]
    assert result.missing_artifacts == ["report.md"]


def test_phase2_runtime_clock_retry_and_command_api() -> None:
    job = Job(goal="pause me", workflow_name="analysis", state=JobState.RUNNING)
    command_api = CommandAPI()

    pause = command_api.pause(job)
    resume = command_api.resume(job)
    cancel = command_api.cancel(job)

    assert pause.status == "ok"
    assert resume.status == "ok"
    assert cancel.status == "ok"
    assert job.state == JobState.CANCELLED
    assert RetryPolicy().can_retry("mcp_timeout", attempt=1) is True
    assert RetryPolicy().can_retry("unsafe_mutation", attempt=1) is False

    clock = RuntimeClock(max_runtime_seconds=1)
    started = clock.now()
    assert clock.deadline_from(started) > started


def test_phase3_sqlite_job_store_and_worker_lease(tmp_path: Path) -> None:
    store = SQLiteJobStore(tmp_path / "runtime.db")
    job = Job(goal="durable", workflow_name="analysis", completed_steps=["inspect"])
    store.save(job)

    loaded = store.load(job.job_id)
    lease_manager = WorkerLeaseManager(lease_seconds=30)
    lease = lease_manager.acquire("worker-1", loaded.job_id)
    renewed = lease_manager.heartbeat(loaded.job_id)

    assert loaded.completed_steps == ["inspect"]
    assert lease.worker_id == "worker-1"
    assert renewed.expires_at >= lease.expires_at
    assert renewed.expired() is False
