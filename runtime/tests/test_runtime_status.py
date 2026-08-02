from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl
from runtime.observability import logger as runtime_event_logger
from runtime.workflow import runtime_status
from runtime.workflow import workflow_state


class FakeCheck:
    def __init__(self, check_id: str, label: str, *, required: bool, ok: bool) -> None:
        self.check_id = check_id
        self.label = label
        self.required = required
        self.ok = ok

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.check_id,
            "label": self.label,
            "kind": "fake",
            "required": self.required,
            "ok": self.ok,
            "detected": "ok" if self.ok else "",
            "install_hint": "install or configure",
            "install_command": "",
            "fallback_command": "",
            "action_command": "",
        }


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


def test_runtime_status_uses_doctor_guidance_for_duckdb_rebuild_next_action(tmp_path: Path) -> None:
    source = tmp_path / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "jsonized"
    source.mkdir(parents=True)
    (source / "knowledge.json").write_text(
        json.dumps(
            {
                "artifact_type": "rag-jsonized-source",
                "content": "DuckDB rebuild guidance should match workflow doctor.",
            }
        ),
        encoding="utf-8",
    )

    result = runtime_status.collect_status(tmp_path)

    assert (
        "aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset"
        in result["next_actions"]
    )
    assert "aiwfctl rag duckdb rebuild --reset" not in result["next_actions"]


def test_runtime_status_suggests_log_maintenance_when_event_log_is_large(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runtime_status, "RUNTIME_LOG_DEFAULT_KEEP_LAST", 1)
    monkeypatch.setattr(runtime_status, "RUNTIME_LOG_MAINTENANCE_GRACE_EVENTS", 0)
    monkeypatch.setattr(runtime_status.runtime_log, "RUNTIME_LOG_DEFAULT_KEEP_LAST", 1)
    monkeypatch.setattr(runtime_status.runtime_log, "RUNTIME_LOG_MAINTENANCE_GRACE_EVENTS", 0)
    event_logger = runtime_event_logger.RuntimeEventLogger(
        repo_root=tmp_path,
        component="ctl",
        trace_id="trace-large-log",
        use_active_trace=False,
    )
    event_logger.emit("runtime_command_started", command="status", workflow="status")
    event_logger.emit(
        "runtime_command_completed",
        command="status",
        workflow="status",
        output={"status": "completed", "exit_code": 0, "duration_ms": 1, "reason": "completed"},
    )

    result = runtime_status.collect_status(tmp_path)

    assert "aiwfctl log summary" in result["next_actions"]
    assert "aiwfctl log archive --keep-last 1 --dry-run" in result["next_actions"]


def test_runtime_status_exposes_last_problem_event_without_status_noise(tmp_path: Path) -> None:
    event_logger = runtime_event_logger.RuntimeEventLogger(
        repo_root=tmp_path,
        component="ctl",
        trace_id="trace-problem",
        use_active_trace=False,
    )
    event_logger.emit(
        "runtime_command_completed",
        command="preflight --profile github-cli",
        workflow="preflight",
        level="warning",
        diagnostics={
            "recoverable": True,
            "next_action": "review_human_check_and_resume",
            "resume_command": "aiwfctl preflight --profile github-cli",
        },
        output={"status": "blocked", "exit_code": 2, "duration_ms": 7, "reason": "human_check_required"},
    )
    event_logger.emit(
        "runtime_command_completed",
        command="help markdown",
        workflow="help",
        output={"status": "completed", "exit_code": 0, "duration_ms": 1, "reason": "completed"},
    )
    event_logger.emit("runtime_command_started", command="status", workflow="status")
    event_logger.emit(
        "runtime_command_completed",
        command="status",
        workflow="status",
        output={"status": "completed", "exit_code": 0, "duration_ms": 1, "reason": "completed"},
    )

    result = runtime_status.collect_status(tmp_path)
    event_log = result["runtime"]["event_log"]
    text = runtime_status.format_status(result)

    assert event_log["last_event"]["command"] == "status"
    assert event_log["last_relevant_event"]["command"] == "preflight --profile github-cli"
    assert event_log["last_problem_event"]["command"] == "preflight --profile github-cli"
    assert event_log["last_problem_event"]["status"] == "blocked"
    assert event_log["last_problem_event"]["resume_command"] == "aiwfctl preflight --profile github-cli"
    assert event_log["acknowledgement_candidates"][0]["command"] == "preflight --profile github-cli"
    assert event_log["acknowledgement_candidates"][0]["acknowledge_command"].startswith(
        "aiwfctl log acknowledge-problem --trace-id trace-problem --sequence 00001"
    )
    assert any(
        action.startswith("aiwfctl log acknowledge-problem --trace-id trace-problem --sequence 00001")
        for action in result["next_actions"]
    )
    assert any(
        item.get("acknowledge_command", "").startswith(
            "aiwfctl log acknowledge-problem --trace-id trace-problem --sequence 00001"
        )
        for item in result["attention_reasons"]
    )
    assert "Problem   : trace-problem 00001 runtime_command_completed preflight --profile github-cli" in text
    assert "Ack Cand  : 1" in text


def test_runtime_status_work_id_links_related_traces(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-1"
    work_dir.mkdir(parents=True)
    workflow_state.update_state(
        work_dir,
        workflow="/docs-sync",
        work_id="issue-1",
        phase="implementation",
        status="in-progress",
    )
    event_logger = runtime_event_logger.RuntimeEventLogger(
        repo_root=tmp_path,
        component="ctl",
        trace_id="trace-work",
        use_active_trace=False,
    )
    event_logger.emit(
        "runtime_command_started",
        command="scm prepare",
        workflow="scm",
        input={"work_id": "issue-1"},
    )
    event_logger.emit(
        "runtime_command_completed",
        command="scm prepare",
        workflow="scm",
        level="warning",
        input={"work_id": "issue-1"},
        diagnostics={"resume_command": "aiwfctl scm prepare --work-id issue-1"},
        output={"status": "blocked", "exit_code": 2, "duration_ms": 5, "reason": "human_check_required"},
    )

    result = runtime_status.collect_status(tmp_path, work_id="issue-1")
    text = runtime_status.format_status(result)

    assert result["related_traces"]["trace_count"] == 1
    assert result["related_traces"]["latest_trace_id"] == "trace-work"
    assert result["related_traces"]["traces"][0]["problem_count"] == 1
    assert "aiwfctl trace show trace-work" in result["next_actions"]
    assert "Related Traces" in text
    assert "trace-work: events=2 problems=1" in text


def test_runtime_status_acknowledgement_candidates_list_multiple_problems(tmp_path: Path) -> None:
    event_logger = runtime_event_logger.RuntimeEventLogger(
        repo_root=tmp_path,
        component="ctl",
        trace_id="trace-ack-candidates",
        use_active_trace=False,
    )
    for command in ["env select", "rag build"]:
        event_logger.emit(
            "runtime_command_completed",
            command=command,
            workflow=command.split()[0],
            level="warning",
            diagnostics={"resume_command": f"aiwfctl {command}"},
            output={"status": "blocked", "exit_code": 2, "duration_ms": 5, "reason": "human_check_required"},
        )

    result = runtime_status.collect_status(tmp_path)
    candidates = result["runtime"]["event_log"]["acknowledgement_candidates"]

    assert [item["command"] for item in candidates] == ["rag build", "env select"]
    assert "aiwfctl log tail --problems -n 20" in result["next_actions"]
    assert all(item["acknowledge_command"].startswith("aiwfctl log acknowledge-problem --trace-id trace-ack-candidates") for item in candidates)


def test_runtime_status_integrates_doctor_warning_count_and_next_action(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        runtime_status,
        "dependency_readiness",
        lambda repo_root: {
            "artifact_type": "runtime-dependency-readiness",
            "status": "ready",
            "check_count": 1,
            "ready_count": 1,
            "required_missing_count": 0,
            "optional_missing_count": 0,
            "checks": [],
        },
    )
    monkeypatch.setattr(
        runtime_status,
        "doctor_status",
        lambda repo_root: {
            "status": "warning",
            "warning_count": 2,
            "warning_summary": {"severity_counts": {"high": 1, "medium": 1}},
            "warnings": [{"id": "warning-a"}, {"id": "warning-b"}],
        },
    )

    result = runtime_status.collect_status(tmp_path)
    text = runtime_status.format_status(result)

    assert result["status"] == "attention"
    assert result["doctor"]["warning_count"] == 2
    assert any(item["id"] == "doctor-warnings" for item in result["attention_reasons"])
    assert "aiwfctl doctor --json" in result["next_actions"]
    assert "Doctor      : status=warning warnings=2" in text
    assert "Attention Reasons" in text


def test_runtime_status_attention_reasons_explain_dirty_repo(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        runtime_status,
        "git_status",
        lambda repo_root: {"present": True, "branch": "main", "head": "abc1234", "dirty_count": 3},
    )
    monkeypatch.setattr(
        runtime_status,
        "dependency_readiness",
        lambda repo_root: {
            "artifact_type": "runtime-dependency-readiness",
            "status": "ready",
            "check_count": 1,
            "ready_count": 1,
            "required_missing_count": 0,
            "optional_missing_count": 0,
            "checks": [],
        },
    )
    monkeypatch.setattr(
        runtime_status,
        "doctor_status",
        lambda repo_root: {
            "status": "pass",
            "warning_count": 0,
            "warning_summary": {},
            "warnings": [],
        },
    )

    result = runtime_status.collect_status(tmp_path)
    summary = runtime_status.apply_status_view(result, "summary")

    assert result["status"] == "attention"
    assert result["attention_reasons"][0]["id"] == "git-dirty"
    assert result["attention_reasons"][0]["count"] == 3
    assert result["attention_summary"]["attention_reason_count"] == 1
    assert result["attention_summary"]["severity_counts"] == {"info": 1}
    assert summary["attention_reasons"][0]["id"] == "git-dirty"
    assert summary["attention_summary"]["attention_reason_count"] == 1


def test_runtime_status_dependency_readiness_summarizes_required_and_optional_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        runtime_status.preflight,
        "which_check",
        lambda executable, required, install_hint: FakeCheck(f"exe:{executable}", executable, required=required, ok=executable == "git"),
    )
    monkeypatch.setattr(
        runtime_status.preflight,
        "uv_runtime_check",
        lambda repo_root, required: FakeCheck("exe:uv", "uv", required=required, ok=False),
    )
    monkeypatch.setattr(
        runtime_status.preflight,
        "docker_daemon_check",
        lambda required: FakeCheck("docker:daemon", "Docker daemon", required=required, ok=False),
    )
    monkeypatch.setattr(
        runtime_status.preflight,
        "github_cli_version_check",
        lambda required: FakeCheck("github-cli:version", "gh --version", required=required, ok=True),
    )
    monkeypatch.setattr(
        runtime_status.preflight,
        "github_cli_auth_check",
        lambda repo_root, required: FakeCheck("github-cli:auth", "gh auth status", required=required, ok=False),
    )
    monkeypatch.setattr(
        runtime_status.preflight,
        "act_cli_check",
        lambda required: FakeCheck("act:version", "act", required=required, ok=False),
    )
    monkeypatch.setattr(
        runtime_status.preflight,
        "path_check",
        lambda path, check_id, label, required, install_hint: FakeCheck(check_id, label, required=required, ok=check_id == "path:scancode-workflow"),
    )

    readiness = runtime_status.dependency_readiness(tmp_path)

    assert readiness["status"] == "attention"
    assert readiness["check_count"] == 10
    assert readiness["ready_count"] == 3
    assert readiness["required_missing_count"] == 1
    assert readiness["optional_missing_count"] == 6
    assert next(item for item in readiness["checks"] if item["id"] == "exe:uv")["status"] == "missing-required"
    assert next(item for item in readiness["checks"] if item["id"] == "docker:daemon")["status"] == "missing-optional"


def test_runtime_status_json_views_filter_summary_and_problems(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        runtime_status,
        "dependency_readiness",
        lambda repo_root: {
            "artifact_type": "runtime-dependency-readiness",
            "status": "attention",
            "check_count": 2,
            "ready_count": 1,
            "required_missing_count": 0,
            "optional_missing_count": 1,
            "checks": [
                {"id": "exe:git", "ok": True, "required": True, "status": "ready"},
                {"id": "docker:daemon", "ok": False, "required": False, "status": "missing-optional"},
            ],
        },
    )
    monkeypatch.setattr(
        runtime_status,
        "doctor_status",
        lambda repo_root: {
            "status": "warning",
            "warning_count": 1,
            "warning_summary": {"repairable_count": 1},
            "warnings": [{"id": "text-boundary"}],
        },
    )
    event_logger = runtime_event_logger.RuntimeEventLogger(
        repo_root=tmp_path,
        component="ctl",
        trace_id="trace-problem-view",
        use_active_trace=False,
    )
    event_logger.emit(
        "runtime_command_completed",
        command="doctor",
        workflow="doctor",
        level="warning",
        output={"status": "warning", "exit_code": 0, "duration_ms": 1, "reason": "warnings-found"},
    )

    result = runtime_status.collect_status(tmp_path, view_mode="summary")
    summary = runtime_status.apply_status_view(result, "summary")
    problems = runtime_status.apply_status_view(result, "problems")
    verbose = runtime_status.apply_status_view(result, "verbose")

    assert summary["view_mode"] == "summary"
    assert "warnings" not in summary["doctor"]
    assert "repairable_warnings" not in summary["doctor"]["warning_summary"]
    assert summary["doctor"]["warning_count"] == 1
    assert summary["environment"]["dependency_readiness"]["optional_missing_count"] == 1
    assert summary["runtime"]["event_log"]["maintenance"]["status"] == "ok"
    assert problems["view_mode"] == "problems"
    assert problems["runtime"]["last_problem_event"]["command"] == "doctor"
    assert problems["environment"]["dependency_readiness"]["failed_checks"][0]["id"] == "docker:daemon"
    assert any(item["id"] == "runtime-last-problem-event" for item in problems["attention_reasons"])
    assert any(item["id"] == "doctor-warnings" for item in problems["attention_reasons"])
    assert any(item["id"] == "dependency-readiness" for item in problems["attention_reasons"])
    assert verbose["view_mode"] == "verbose"
    assert verbose["doctor"]["warnings"][0]["id"] == "text-boundary"


def test_runtime_status_problems_view_omits_pass_and_empty_sections(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        runtime_status,
        "dependency_readiness",
        lambda repo_root: {
            "artifact_type": "runtime-dependency-readiness",
            "status": "ready",
            "check_count": 1,
            "ready_count": 1,
            "required_missing_count": 0,
            "optional_missing_count": 0,
            "checks": [{"id": "exe:git", "ok": True, "required": True, "status": "ready"}],
        },
    )
    monkeypatch.setattr(
        runtime_status,
        "doctor_status",
        lambda repo_root: {
            "status": "pass",
            "warning_count": 0,
            "warning_summary": {},
            "warnings": [],
        },
    )

    result = runtime_status.collect_status(tmp_path)
    problems = runtime_status.apply_status_view(result, "problems")

    assert problems["status"] == "ok"
    assert problems["attention_reasons"] == []
    assert "doctor" not in problems
    assert "environment" not in problems
    assert "runtime" not in problems
    assert "related_traces" not in problems
