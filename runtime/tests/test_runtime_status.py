from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl
from runtime.observability import logger as runtime_event_logger
from runtime.workflow import runtime_status
from runtime.workflow import workflow_state


def test_runtime_status_collects_trace_log_work_and_knowledge_state(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    work_dir = tmp_path / "work" / "issue-1"
    work_dir.mkdir(parents=True)
    workflow_state.update_state(
        work_dir,
        workflow="/docs-sync",
        work_id="issue-1",
        phase="implementation",
        status="in-progress",
    )
    runtime_event_logger.begin_active_runtime_trace(
        tmp_path,
        workflow="/docs-sync",
        trace_id="trace-status",
        initial_sequence=2,
    )
    event_logger = runtime_event_logger.RuntimeEventLogger(repo_root=tmp_path, component="ctl")
    event_logger.emit(
        "runtime_command_started",
        workflow="/docs-sync",
        phase="execute",
        operation_id="help:list",
        command="help list",
    )
    (tmp_path / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "semantic-hints").mkdir(parents=True)
    (tmp_path / "db" / "rag").mkdir(parents=True)
    (tmp_path / "db" / "rag" / "ariadne-knowledge.duckdb").write_text("", encoding="utf-8")

    result = runtime_status.collect_status(tmp_path, work_id="issue-1")

    assert result["artifact_type"] == "runtime-status"
    assert result["status"] == "attention"
    assert result["trace"]["trace_id"] == "trace-status"
    assert result["trace"]["last_sequence"] == 3
    assert result["runtime"]["event_log"]["event_count"] == 1
    assert result["runtime"]["event_log"]["last_event"]["event"] == "runtime_command_started"
    assert result["work"]["selected"]["status"] == "in-progress"
    assert result["work"]["selected"]["workflow"] == "/docs-sync"
    assert result["knowledge"]["paths"]["source_repo"]["exists"] is True
    assert result["knowledge"]["paths"]["duckdb"]["exists"] is True
    assert "aiwfctl trace status" in result["next_actions"]


def test_ctl_status_outputs_json_and_human_summary(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "runtime" / "windows-script").mkdir(parents=True)
    (tmp_path / "runtime" / "windows-script" / "aiwfctl.cmd").write_text("@echo off\n", encoding="utf-8")

    json_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "status", "--json"])
    code, output = ctl.run(json_args)

    assert code == 0
    payload = json.loads(output)
    assert payload["artifact_type"] == "runtime-status"
    assert payload["runtime"]["aiwfctl"]["exists"] is True
    assert payload["knowledge"]["source_repo_name"] == "ariadne-knowledge-platform"

    text_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "status"])
    code, output = ctl.run(text_args)

    assert code == 0
    assert "Ariadne Runtime Status" in output
    assert "Trace" in output
    assert "Knowledge" in output
    assert "Next Actions" in output
