from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl
from runtime.observability.logger import RuntimeEventLogger
from runtime.workflow import runtime_trace


def write_trace_fixture(repo_root: Path, trace_id: str = "trace-show") -> None:
    event_logger = RuntimeEventLogger(repo_root=repo_root, component="ctl", trace_id=trace_id, use_active_trace=False)
    event_logger.emit(
        "runtime_command_started",
        command="help list",
        workflow="help",
        phase="execute",
        operation_id="help:list",
    )
    event_logger.emit(
        "runtime_command_completed",
        command="help list",
        workflow="help",
        phase="execute",
        operation_id="help:list",
        output={
            "status": "completed",
            "exit_code": 0,
            "duration_ms": 3,
            "reason": "completed",
        },
    )
    event_logger.emit(
        "runtime_command_started",
        command="preflight --profile github-cli",
        workflow="preflight",
        phase="execute",
        operation_id="preflight",
    )
    event_logger.emit(
        "runtime_command_completed",
        command="preflight --profile github-cli",
        workflow="preflight",
        phase="execute",
        operation_id="preflight",
        level="warning",
        diagnostics={
            "recoverable": True,
            "next_action": "review_human_check_and_resume",
            "resume_command": "aiwfctl preflight --profile github-cli",
        },
        output={
            "status": "blocked",
            "exit_code": 2,
            "duration_ms": 7,
            "reason": "human_check_required",
        },
    )


def test_runtime_trace_show_summarizes_commands_and_problem_events(tmp_path: Path) -> None:
    write_trace_fixture(tmp_path)

    result = runtime_trace.build_trace_report(tmp_path, trace_id="trace-show")

    assert result["artifact_type"] == "runtime-trace-report"
    assert result["status"] == "ok"
    assert result["outcome"] == "blocked"
    assert result["event_count"] == 4
    assert result["started_count"] == 2
    assert result["terminal_count"] == 2
    assert result["commands"] == ["help list", "preflight --profile github-cli"]
    assert result["statuses"] == {"completed": 1, "blocked": 1}
    assert result["reasons"] == {"completed": 1, "human_check_required": 1}
    assert result["last_successful_command"] == "help list"
    assert result["problem_events"][0]["command"] == "preflight --profile github-cli"
    assert result["problem_event_count"] == 1
    assert result["resume_hint"]["last_successful_command"] == "help list"
    assert result["resume_hint"]["failed_command"] == "preflight --profile github-cli"
    assert result["resume_hint"]["next_command"] == "aiwfctl preflight --profile github-cli"
    assert result["next_actions"][0] == "aiwfctl preflight --profile github-cli"

    text = runtime_trace.format_trace_report(result)
    assert "Runtime Trace Report" in text
    assert "Outcome      : blocked" in text
    assert "Last Success : help list" in text
    assert "Resume Hint" in text
    assert "Next Command : aiwfctl preflight --profile github-cli" in text
    assert "seq=00004" in text


def test_runtime_trace_show_problems_mode_filters_timeline(tmp_path: Path) -> None:
    write_trace_fixture(tmp_path)

    result = runtime_trace.build_trace_report(tmp_path, trace_id="trace-show", problems_only=True)
    text = runtime_trace.format_trace_report(result)

    assert result["view_mode"] == "problems"
    assert result["event_count"] == 4
    assert result["problem_event_count"] == 1
    assert len(result["timeline"]) == 1
    assert result["timeline"][0]["command"] == "preflight --profile github-cli"
    assert "Problems     : 1" in text
    assert "Commands" not in text
    assert "Timeline" not in text


def test_runtime_trace_show_latest_can_exclude_current_command_trace(tmp_path: Path) -> None:
    write_trace_fixture(tmp_path, trace_id="previous-trace")
    write_trace_fixture(tmp_path, trace_id="current-trace")

    result = runtime_trace.build_trace_report(tmp_path, exclude_trace_id="current-trace")

    assert result["trace_id"] == "previous-trace"
    assert result["selected_latest_trace"] is True
    assert result["event_count"] == 4


def test_ctl_trace_show_outputs_json_and_missing_trace_code(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    write_trace_fixture(tmp_path)

    args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "trace", "show", "trace-show", "--json"])
    code, output = ctl.run(args)

    assert code == 0
    payload = json.loads(output)
    assert payload["trace_id"] == "trace-show"
    assert payload["outcome"] == "blocked"
    assert payload["problem_events"][0]["reason"] == "human_check_required"
    assert payload["resume_hint"]["next_command"] == "aiwfctl preflight --profile github-cli"

    problem_args = ctl.build_parser().parse_args(
        ["--repo-root", str(tmp_path), "trace", "show", "trace-show", "--problems", "--json"]
    )
    code, output = ctl.run(problem_args)

    assert code == 0
    problems = json.loads(output)
    assert problems["view_mode"] == "problems"
    assert len(problems["timeline"]) == 1

    missing_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "trace", "show", "missing-trace"])
    code, output = ctl.run(missing_args)

    assert code == 2
    assert "Status       : missing-trace" in output


def test_ctl_trace_begin_records_work_id_in_active_trace(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "trace",
            "begin",
            "--workflow",
            "/docs-sync",
            "--work-id",
            "issue-1",
            "--trace-id",
            "trace-work-id",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    payload = json.loads(output)
    assert payload["work_id"] == "issue-1"
    active = json.loads((tmp_path / "logs" / "runtime" / "active-trace.json").read_text(encoding="utf-8"))
    assert active["work_id"] == "issue-1"


def test_ctl_trace_recover_previews_invalid_active_trace_and_archives_with_approval(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    active_path = tmp_path / "logs" / "runtime" / "active-trace.json"
    active_path.parent.mkdir(parents=True)
    active_path.write_text("{invalid json", encoding="utf-8")

    status_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "trace", "status", "--json"])
    code, output = ctl.run(status_args)

    assert code == 2
    status = json.loads(output)
    assert status["status"] == "invalid"
    assert status["recovery_command"] == "aiwfctl trace recover --dry-run"

    dry_run_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "trace", "recover", "--dry-run", "--json"])
    code, output = ctl.run(dry_run_args)

    assert code == 0
    preview = json.loads(output)
    assert preview["status"] == "dry-run"
    assert preview["would_archive"] is True
    assert active_path.exists()

    approved_args = ctl.build_parser().parse_args(
        ["--repo-root", str(tmp_path), "trace", "recover", "--human-check", "approved", "--json"]
    )
    code, output = ctl.run(approved_args)

    assert code == 0
    recovered = json.loads(output)
    assert recovered["status"] == "recovered"
    assert recovered["written"] is True
    assert not active_path.exists()
    assert (tmp_path / recovered["recovery_path"]).exists()
