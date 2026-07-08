from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from runtime.observability import logger
from runtime.observability.metrics import RuntimeMetricsCollector, register_runtime_metrics_context
from runtime.observability.schema import context_usage, cost_usage, runtime_metric_record, token_usage
from runtime.observability.trace import duration_timer


def jsonl_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_monthly_log_path_uses_year_month_suffix() -> None:
    now = datetime(2026, 7, 9, tzinfo=timezone.utc)

    path = logger.monthly_log_path(Path("runtime/logs"), now=now)

    assert path.as_posix() == "runtime/logs/runtime-metrics-202607.jsonl"


def test_resolve_log_path_rotates_base_runtime_metrics_file() -> None:
    now = datetime(2026, 8, 1, tzinfo=timezone.utc)

    path = logger.resolve_log_path(base_path=Path("runtime/logs/runtime-metrics.jsonl"), now=now)

    assert path.as_posix() == "runtime/logs/runtime-metrics-202608.jsonl"


def test_resolve_log_path_can_disable_rotation_for_base_or_directory() -> None:
    base_path = Path("runtime/logs/runtime-metrics.jsonl")

    assert logger.resolve_log_path(base_path=base_path, rotate_monthly=False) == base_path
    assert logger.resolve_log_path(log_dir=Path("runtime/logs"), rotate_monthly=False).as_posix() == "runtime/logs/runtime-metrics.jsonl"


def test_append_jsonl_appends_one_record_per_line(tmp_path: Path) -> None:
    log_path = tmp_path / "runtime-metrics-202607.jsonl"

    first = logger.append_jsonl(log_path, {"event": "workflow_started"})
    second = logger.append_jsonl(log_path, {"event": "workflow_completed"})

    assert first["status"] == "ok"
    assert second["status"] == "ok"
    assert jsonl_rows(log_path) == [{"event": "workflow_started"}, {"event": "workflow_completed"}]


def test_append_jsonl_returns_warning_without_raising_when_parent_is_file(tmp_path: Path) -> None:
    parent_file = tmp_path / "not-a-directory"
    parent_file.write_text("occupied", encoding="utf-8")

    result = logger.append_jsonl(parent_file / "runtime-metrics-202607.jsonl", {"event": "workflow_started"})

    assert result["status"] == "warning"
    assert "runtime metrics write failed" in result["warning"]


def test_schema_helpers_sanitize_negative_and_invalid_values() -> None:
    assert token_usage(input_tokens=-1, output_tokens="bad") == {
        "input": 0,
        "output": 0,
        "total": 0,
        "estimated": True,
    }
    assert context_usage(selected_context_count=-2, estimated_context_tokens="x")["selected_context_count"] == 0
    assert cost_usage(input_cost=-0.1, output_cost="bad")["total_cost"] == 0.0


def test_runtime_metric_record_falls_back_to_runtime_error_for_unknown_event() -> None:
    record = runtime_metric_record(event="unknown", workflow_name="/runtime-health-check")

    assert record["event"] == "runtime_error"
    assert record["workflow_name"] == "/runtime-health-check"
    assert record["token_usage"]["estimated"] is True


def test_duration_timer_records_elapsed_duration() -> None:
    with duration_timer() as timer:
        assert timer["duration_ms"] == 0

    assert timer["duration_ms"] >= 0


def test_collector_defaults_log_dir_under_runtime_logs(tmp_path: Path) -> None:
    collector = RuntimeMetricsCollector(repo_root=tmp_path)

    assert collector.log_path().parent == tmp_path / "runtime" / "logs"


def test_collector_records_non_fatal_log_write_warning(tmp_path: Path) -> None:
    parent_file = tmp_path / "not-a-directory"
    parent_file.write_text("occupied", encoding="utf-8")
    collector = RuntimeMetricsCollector(repo_root=tmp_path, log_base_path=parent_file / "runtime-metrics.jsonl")

    result = collector.workflow_started()

    assert result["_write"]["status"] == "warning"
    assert collector.write_warnings


def test_collector_records_workflow_agent_token_context_and_monthly_jsonl(tmp_path: Path) -> None:
    collector = RuntimeMetricsCollector(
        repo_root=tmp_path,
        workflow_id="runtime-health-check",
        workflow_name="/runtime-health-check",
        log_dir=tmp_path / "runtime" / "logs",
    )

    collector.workflow_started()
    collector.agent_started("runtime-quality-gate-agent")
    collector.agent_completed("runtime-quality-gate-agent")
    collector.record_token_usage(input_tokens=1200, output_tokens=300, estimated=True, total_cost=0.01)
    collector.record_context_usage(
        selected_context_count=3,
        estimated_context_tokens=900,
        rag_reference_count=2,
        dispatcher_route="intent->metadata->semantic-hint",
    )
    collector.workflow_completed(save_evidence=False)

    log_path = collector.log_path()
    rows = jsonl_rows(log_path)
    assert log_path.name.startswith("runtime-metrics-")
    assert [row["event"] for row in rows] == [
        "workflow_started",
        "agent_started",
        "agent_completed",
        "token_usage_recorded",
        "context_usage_recorded",
        "workflow_completed",
    ]
    assert rows[-1]["token_usage"]["total"] == 1500
    assert rows[-1]["context"]["selected_context_count"] == 3
    assert rows[-1]["cost"]["total_cost"] == 0.01


def test_collector_records_human_check_evidence_and_runtime_error(tmp_path: Path) -> None:
    collector = RuntimeMetricsCollector(repo_root=tmp_path, workflow_name="/demo", log_dir=tmp_path / "runtime" / "logs")

    collector.workflow_started()
    collector.human_check_required(reason="needs approval")
    collector.evidence_generated(path="work/demo/test-evidence/runtime-metrics.json")
    collector.runtime_error(error="simulated")
    result = collector.workflow_failed(error="failed", save_evidence=False)

    assert result["event"] == "workflow_failed"
    assert result["runtime"]["human_check_required"] is True
    assert result["runtime"]["evidence_generated"] is True
    assert result["runtime"]["error_count"] == 2


def test_collector_failed_workflow_saves_human_check_required_evidence(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-1"
    collector = RuntimeMetricsCollector(repo_root=tmp_path, work_dir=work_dir, log_dir=tmp_path / "runtime" / "logs")

    collector.workflow_started()
    result = collector.workflow_failed(error="boom")

    payload = json.loads((work_dir / "context" / "runtime-metrics.json").read_text(encoding="utf-8"))
    assert result["event"] == "workflow_failed"
    assert payload["status"] == "human-check-required"
    assert payload["runtime"]["error_count"] == 1


def test_collector_saves_workflow_evidence_and_registers_context(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_dir = repo_root / "work" / "runtime-health-check"
    collector = RuntimeMetricsCollector(
        repo_root=repo_root,
        work_dir=work_dir,
        workflow_name="/runtime-health-check",
        log_dir=repo_root / "runtime" / "logs",
    )

    collector.workflow_started()
    result = collector.workflow_completed()

    evidence_path = work_dir / "test-evidence" / "runtime-metrics.json"
    context_path = work_dir / "context" / "runtime-metrics.json"
    manifest_path = work_dir / "context" / "context-manifest.json"
    assert result["event"] == "workflow_completed"
    assert evidence_path.exists()
    assert context_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["contexts"][0]["type"] == "runtime-metrics"
    assert manifest["contexts"][0]["schema"] == ".github/schemas/runtime-metrics.schema.json"


def test_collector_evidence_summary_can_skip_work_dir_or_manifest_registration(tmp_path: Path) -> None:
    no_work = RuntimeMetricsCollector(repo_root=tmp_path, log_dir=tmp_path / "runtime" / "logs")
    assert no_work.save_evidence_summary()["status"] == "skipped"

    work_dir = tmp_path / "work" / "issue-1"
    collector = RuntimeMetricsCollector(repo_root=tmp_path, work_dir=work_dir, log_dir=tmp_path / "runtime" / "logs")
    collector.workflow_started()
    result = collector.save_evidence_summary(register_context=False)

    assert result["status"] == "ok"
    assert result["context_manifest"] == ""
    assert not (work_dir / "context" / "context-manifest.json").exists()


def test_collector_evidence_summary_returns_warning_without_raising(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-1"
    work_dir.mkdir(parents=True)
    (work_dir / "test-evidence").write_text("occupied", encoding="utf-8")
    collector = RuntimeMetricsCollector(repo_root=tmp_path, work_dir=work_dir, log_dir=tmp_path / "runtime" / "logs")

    result = collector.save_evidence_summary()

    assert result["status"] == "warning"
    assert "runtime metrics evidence write failed" in result["warning"]


def test_register_runtime_metrics_context_uses_runtime_metrics_type(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_dir = repo_root / "work" / "issue-1"
    metrics_path = work_dir / "context" / "runtime-metrics.json"
    metrics_path.parent.mkdir(parents=True)
    metrics_path.write_text("{}", encoding="utf-8")

    manifest = register_runtime_metrics_context(repo_root=repo_root, work_dir=work_dir, metrics_path=metrics_path)

    assert manifest["contexts"][0]["type"] == "runtime-metrics"
    assert manifest["contexts"][0]["path"] == "work/issue-1/context/runtime-metrics.json"
