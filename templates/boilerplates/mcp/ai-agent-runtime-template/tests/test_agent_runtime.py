from __future__ import annotations

import json
import sqlite3
import ast
from pathlib import Path

from local_agent_runtime.completion import CompletionEvaluator
from local_agent_runtime.commands import CommandAPI
from local_agent_runtime.contracts import (
    WorkflowRequest,
    WorkflowResult,
    WorkflowStatus,
    generate_trace_id,
    validate_trace_id,
)
from local_agent_runtime.framework_adapters import (
    AutoGenCompatibilityAdapter,
    CrewAIRuntimeAdapter,
    LangGraphRuntimeAdapter,
    MicrosoftAgentFrameworkRuntimeAdapter,
)
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
    assert len(checkpoint["trace_id"]) == 24
    assert runtime.artifacts.paths_for(job.job_id) == ["analysis-report.md"]
    assert runtime.events.events[-1]["event_type"] == "job.finished"
    evidence = json.loads((tmp_path / "evidence" / f"{job.job_id}-completion.json").read_text(encoding="utf-8"))
    assert evidence["trace_id"] == job.trace_id
    assert evidence["evidence"]["status"] == "available"
    assert runtime.job_store.load(job.job_id).state == JobState.COMPLETED
    assert runtime.job_store.load(job.job_id).trace_id == job.trace_id


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


def test_sqlite_job_store_migrates_existing_rows_to_trace_id(tmp_path: Path) -> None:
    db_path = tmp_path / "runtime.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            create table jobs (
              job_id text primary key,
              goal text not null,
              workflow_name text not null,
              state text not null,
              payload text not null
            )
            """
        )
        connection.execute(
            "insert into jobs(job_id, goal, workflow_name, state, payload) values (?, ?, ?, ?, ?)",
            (
                "job-existing",
                "migrate",
                "analysis",
                "accepted",
                json.dumps(
                    {
                        "completed_steps": [],
                        "artifacts": [],
                        "events": [],
                        "human_check_request": None,
                        "model_claimed_done": False,
                    }
                ),
            ),
        )

    loaded = SQLiteJobStore(db_path).load("job-existing")

    assert loaded.trace_id
    assert len(loaded.trace_id) == 24


def test_runtime_contracts_use_ariadne_trace_id_and_reject_secret_fields() -> None:
    trace_id = generate_trace_id()
    validate_trace_id(trace_id)

    request = WorkflowRequest(
        workflow_id="issue-123",
        trace_id=trace_id,
        workflow_type="feature-development",
        input={"goal": "implement runtime"},
    ).to_contract()
    result = WorkflowResult(
        workflow_id=request["workflow_id"],
        trace_id=request["trace_id"],
        status=WorkflowStatus.COMPLETED,
        completed_at="2026-07-22T00:30:00+00:00",
    ).to_contract()

    assert request["schema_version"] == "1.0"
    assert request["trace_id"] == trace_id
    assert result["status"] == "completed"

    try:
        WorkflowRequest(
            workflow_id="issue-unsafe",
            workflow_type="feature-development",
            input={"api_key": "do-not-store"},
        ).to_contract()
    except ValueError as exc:
        assert "Secret-like field" in str(exc)
    else:
        raise AssertionError("secret-like contract payload should be rejected")


def test_framework_adapter_patterns_map_contracts_without_sdk_dependency() -> None:
    request = WorkflowRequest(
        workflow_id="issue-456",
        workflow_type="feature-development",
        input={"goal": "run through adapter"},
    )
    adapters = [
        LangGraphRuntimeAdapter(),
        CrewAIRuntimeAdapter(),
        MicrosoftAgentFrameworkRuntimeAdapter(),
        AutoGenCompatibilityAdapter(),
    ]

    for adapter in adapters:
        plan = adapter.build_execution_plan(request, framework_metadata={"native_state_ref": "adapter-owned"})
        result = adapter.result_from_plan(
            plan,
            status=WorkflowStatus.COMPLETED,
            completed_at="2026-07-22T00:30:00+00:00",
        )

        assert plan["workflow_request"]["trace_id"] == request.trace_id
        assert plan["runtime_context"]["trace_id"] == request.trace_id
        assert plan["framework_metadata"] == {"native_state_ref": "adapter-owned"}
        assert result["trace_id"] == request.trace_id
        assert result["status"] == "completed"
        assert "framework_metadata" not in result


def test_framework_adapter_skeletons_do_not_import_framework_sdks() -> None:
    adapter_dir = Path(__file__).resolve().parents[1] / "src" / "local_agent_runtime" / "framework_adapters"
    forbidden_roots = {"langgraph", "crewai", "autogen", "microsoft"}

    for path in adapter_dir.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0].lower() for alias in node.names}
                assert imported.isdisjoint(forbidden_roots)
            if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                assert node.module.split(".")[0].lower() not in forbidden_roots
