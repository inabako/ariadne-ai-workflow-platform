from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl
from runtime.observability.logger import RuntimeEventLogger
from runtime.workflow import runtime_log
from runtime.workflow import runtime_status


def write_log_fixture(repo_root: Path, trace_id: str = "trace-log") -> Path:
    event_logger = RuntimeEventLogger(repo_root=repo_root, component="ctl", trace_id=trace_id, use_active_trace=False)
    for command in ["status", "doctor", "rag build --dry-run"]:
        event_logger.emit(
            "runtime_command_started",
            command=command,
            workflow=command.split()[0],
            phase="execute",
            operation_id=command.replace(" ", ":"),
        )
        event_logger.emit(
            "runtime_command_completed",
            command=command,
            workflow=command.split()[0],
            phase="execute",
            operation_id=command.replace(" ", ":"),
            output={"status": "completed", "exit_code": 0, "duration_ms": 1, "reason": "completed"},
        )
    return runtime_log.resolve_runtime_log_path(repo_root)


def test_runtime_log_summary_counts_events_traces_and_commands(tmp_path: Path) -> None:
    write_log_fixture(tmp_path)

    result = runtime_log.build_log_summary(tmp_path)

    assert result["artifact_type"] == "runtime-log-summary"
    assert result["status"] == "ok"
    assert result["line_count"] == 6
    assert result["event_count"] == 6
    assert result["trace_count"] == 1
    assert result["event_counts"] == {"runtime_command_completed": 3, "runtime_command_started": 3}
    assert result["top_commands"][0] == {"value": "doctor", "count": 2}
    assert result["maintenance"]["status"] == "ok"
    assert result["maintenance"]["threshold"] >= result["line_count"]
    assert result["next_actions"] == ["aiwfctl log summary"]
    text = runtime_log.format_log_summary(result)
    assert "Runtime Log Summary" in text
    assert "Maintenance" in text


def test_runtime_log_prune_dry_run_reports_counts_without_writing(tmp_path: Path) -> None:
    log_path = write_log_fixture(tmp_path)
    before = log_path.read_text(encoding="utf-8")

    result = runtime_log.prune_runtime_log(tmp_path, keep_last=2, dry_run=True)

    assert result["status"] == "dry-run"
    assert result["prune_count"] == 4
    assert result["kept_count"] == 2
    assert result["would_write"] is False
    assert log_path.read_text(encoding="utf-8") == before


def test_runtime_log_prune_requires_human_check_before_writing(tmp_path: Path) -> None:
    log_path = write_log_fixture(tmp_path)
    before = log_path.read_text(encoding="utf-8")

    result = runtime_log.prune_runtime_log(tmp_path, keep_last=2)

    assert result["status"] == "human-check-required"
    assert result["human_check_required"] is True
    assert result["would_write"] is False
    assert log_path.read_text(encoding="utf-8") == before


def test_runtime_log_archive_with_approval_writes_archive_and_keeps_tail(tmp_path: Path) -> None:
    log_path = write_log_fixture(tmp_path)

    result = runtime_log.archive_runtime_log(tmp_path, keep_last=2, human_check="approved")

    assert result["status"] == "ok"
    assert result["archive_count"] == 4
    assert result["kept_count"] == 2
    assert result["would_write"] is True
    assert len(log_path.read_text(encoding="utf-8").splitlines()) == 2
    archives = list((tmp_path / "logs" / "runtime" / "archive").glob("runtime-events-*.log"))
    assert len(archives) == 1
    assert len(archives[0].read_text(encoding="utf-8").splitlines()) == 4


def test_runtime_log_tail_filters_problem_events(tmp_path: Path) -> None:
    write_log_fixture(tmp_path)
    event_logger = RuntimeEventLogger(repo_root=tmp_path, component="ctl", trace_id="trace-problem", use_active_trace=False)
    event_logger.emit(
        "runtime_command_completed",
        command="preflight --profile github-cli",
        workflow="preflight",
        level="warning",
        diagnostics={"resume_command": "aiwfctl preflight --profile github-cli"},
        output={"status": "blocked", "exit_code": 2, "duration_ms": 7, "reason": "human_check_required"},
    )

    result = runtime_log.tail_runtime_log(tmp_path, limit=1, problems=True)

    assert result["artifact_type"] == "runtime-log-tail"
    assert result["status"] == "ok"
    assert result["selected_event_count"] == 1
    assert result["events"][0]["trace_id"] == "trace-problem"
    assert result["events"][0]["status"] == "blocked"
    assert "Runtime Log Tail" in runtime_log.format_log_events_result(result)


def test_runtime_log_grep_filters_trace_id(tmp_path: Path) -> None:
    write_log_fixture(tmp_path, trace_id="trace-one")
    write_log_fixture(tmp_path, trace_id="trace-two")

    result = runtime_log.grep_runtime_log(tmp_path, trace_id="trace-two")

    assert result["artifact_type"] == "runtime-log-grep"
    assert result["status"] == "ok"
    assert result["selected_event_count"] == 6
    assert {event["trace_id"] for event in result["events"]} == {"trace-two"}


def test_ctl_log_export_writes_trace_evidence(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    write_log_fixture(tmp_path, trace_id="trace-export")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "log",
            "export",
            "--trace-id",
            "trace-export",
            "--output",
            "work/evidence/trace-export.json",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["artifact_type"] == "runtime-log-export"
    assert result["selected_event_count"] == 6
    assert result["written"] is True
    saved = json.loads((tmp_path / "work" / "evidence" / "trace-export.json").read_text(encoding="utf-8"))
    assert saved["artifact_type"] == "runtime-log-export"
    assert saved["events"][0]["trace_id"] == "trace-export"


def test_ctl_log_acknowledge_problem_hides_it_from_status(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    event_logger = RuntimeEventLogger(repo_root=tmp_path, component="ctl", trace_id="trace-problem", use_active_trace=False)
    event_logger.emit(
        "runtime_command_completed",
        command="env select",
        workflow="env",
        level="warning",
        diagnostics={"resume_command": "aiwfctl env select"},
        output={"status": "blocked", "exit_code": 2, "duration_ms": 7, "reason": "human_check_required"},
    )
    before = runtime_status.collect_status(tmp_path)
    assert before["runtime"]["event_log"]["last_problem_event"]["trace_id"] == "trace-problem"

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "log",
            "acknowledge-problem",
            "--trace-id",
            "trace-problem",
            "--sequence",
            "1",
            "--reason",
            "known interactive selection check",
            "--json",
        ]
    )
    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["artifact_type"] == "runtime-problem-acknowledgement"
    assert result["written"] is True
    after = runtime_status.collect_status(tmp_path)
    assert after["runtime"]["event_log"]["last_problem_event"] == {}
    assert after["runtime"]["event_log"]["acknowledged_problem_count"] == 1


def test_runtime_log_acknowledge_all_matching_command(tmp_path: Path) -> None:
    event_logger = RuntimeEventLogger(repo_root=tmp_path, component="ctl", trace_id="trace-env", use_active_trace=False)
    for command in ["env select", "env select", "env show"]:
        event_logger.emit(
            "runtime_command_completed",
            command=command,
            workflow="env",
            level="warning",
            diagnostics={"resume_command": f"aiwfctl {command}"},
            output={"status": "blocked", "exit_code": 2, "duration_ms": 7, "reason": "human_check_required"},
        )

    result = runtime_log.acknowledge_runtime_problem(
        tmp_path,
        command="env select",
        all_matching=True,
        reason="known historical env select checks",
    )

    assert result["status"] == "ok"
    assert result["acknowledged_count"] == 2
    assert result["written"] is True
    assert len(runtime_log.acknowledged_problem_keys(tmp_path)) == 2


def test_ctl_log_summary_and_prune_dry_run_route(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    log_path = write_log_fixture(tmp_path)
    before_count = len(log_path.read_text(encoding="utf-8").splitlines())

    summary_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "log", "summary", "--json"])
    code, output = ctl.run(summary_args)

    assert code == 0
    summary = json.loads(output)
    assert summary["artifact_type"] == "runtime-log-summary"
    assert summary["event_count"] >= before_count

    prune_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "log",
            "prune",
            "--keep-last",
            "2",
            "--dry-run",
            "--output",
            "work/evidence/log-prune-dry-run.json",
        ]
    )
    code, output = ctl.run(prune_args)

    assert code == 0
    assert "Runtime Log Prune" in output
    assert "Dry Run     : true" in output
    assert "Output      : work/evidence/log-prune-dry-run.json" in output
    assert len(log_path.read_text(encoding="utf-8").splitlines()) >= before_count
    saved = json.loads((tmp_path / "work" / "evidence" / "log-prune-dry-run.json").read_text(encoding="utf-8"))
    assert saved["artifact_type"] == "runtime-log-prune"
    assert saved["status"] == "dry-run"
