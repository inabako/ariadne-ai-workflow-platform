from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime.observability.logger import RuntimeEventLogger


SUBCOMMAND_ATTRIBUTES = (
    "help_command",
    "env_command",
    "context_command",
    "human_gate_command",
    "intake_command",
    "scm_command",
    "github_command",
    "knowledge_command",
    "knowledge_source_command",
    "rag_command",
    "workflow_command",
    "workflow_action",
    "tools_command",
    "gui_command",
    "web_svg_command",
    "retrieval_command",
    "sdk_command",
    "flutter_command",
    "mcp_group_command",
    "github_knowledge_command",
    "work_command",
    "self_improvement_command",
    "review_command",
    "close_archive_command",
    "iac_command",
    "iac_template_command",
    "integration_command",
    "integration_emulator_command",
    "trace_command",
    "log_command",
)


RESUME_OPTION_NAMES: tuple[tuple[str, str], ...] = (
    ("work_id", "--work-id"),
    ("workflow", "--workflow"),
    ("profile", "--profile"),
    ("trace_id", "--trace-id"),
    ("trace_id_option", "--trace-id"),
    ("runtime_log", "--runtime-log"),
    ("source_dir", "--source-dir"),
    ("source_repo", "--source-repo"),
    ("repository", "--repository"),
    ("branch", "--branch"),
    ("target_branch", "--target-branch"),
    ("base_branch", "--base-branch"),
    ("issue_number", "--issue-number"),
    ("plan", "--plan"),
    ("message", "--message"),
    ("output", "--output"),
    ("keep_last", "--keep-last"),
    ("archive_dir", "--archive-dir"),
    ("encoding_paths", "--encoding-paths"),
    ("encoding_extensions", "--encoding-extensions"),
)

RESUME_BOOLEAN_OPTIONS: tuple[tuple[str, str], ...] = (
    ("dry_run", "--dry-run"),
    ("fail_on_warning", "--fail-on-warning"),
    ("skip_ut_spec_sync", "--skip-ut-spec-sync"),
    ("repair_encoding", "--repair-encoding"),
    ("repair_spec_index", "--repair-spec-index"),
    ("fix_suggestion_only", "--fix-suggestion-only"),
    ("problems", "--problems"),
    ("summary", "--summary"),
    ("verbose", "--verbose"),
    ("reset", "--reset"),
    ("force", "--force"),
    ("install", "--install"),
    ("gh_login_from_env", "--gh-login-from-env"),
)


def command_path(args: Any) -> str:
    command = str(getattr(args, "command", "") or "")
    if not command:
        return ""
    parts = [command]
    for attribute in SUBCOMMAND_ATTRIBUTES:
        value = str(getattr(args, attribute, "") or "")
        if value:
            parts.append(value)
    return " ".join(parts)


def _quote_arg(value: object) -> str:
    text = str(value)
    if not text:
        return '""'
    if any(char.isspace() for char in text) or '"' in text:
        return '"' + text.replace('"', '\\"') + '"'
    return text


def runtime_resume_command(args: Any) -> str:
    path = command_path(args)
    if not path:
        return ""
    parts = ["aiwfctl", path]
    for attribute, option in RESUME_OPTION_NAMES:
        value = getattr(args, attribute, None)
        if isinstance(value, list):
            for item in value:
                if item not in {None, ""}:
                    parts.extend([option, _quote_arg(item)])
            continue
        if value in {None, "", False}:
            continue
        parts.extend([option, _quote_arg(value)])
    for attribute, option in RESUME_BOOLEAN_OPTIONS:
        if bool(getattr(args, attribute, False)):
            parts.append(option)
    human_check = str(getattr(args, "human_check", "") or "")
    if human_check:
        parts.extend(["--human-check", _quote_arg(human_check)])
    return " ".join(parts)


def runtime_workflow(args: Any) -> str:
    return str(getattr(args, "command", "") or "")


def runtime_operation_id(command_path: str) -> str:
    if not command_path:
        return "runtime-command"
    return command_path.replace(" ", ":")


def runtime_log_input(args: Any, repo_root: Path) -> dict[str, Any]:
    return {
        "json": bool(getattr(args, "json", False)),
        "repo_root": str(repo_root),
        "work_id": str(getattr(args, "work_id", "") or ""),
    }


def runtime_status_for_exit_code(code: int) -> str:
    if code == 0:
        return "completed"
    if code == 2:
        return "blocked"
    return "failed"


def runtime_reason_for_result(code: int, output: str) -> str:
    normalized = output.lower()
    if code == 0:
        return "completed"
    if "human check" in normalized or "human-check" in normalized:
        return "human_check_required"
    if "usage:" in normalized or "警告" in output:
        return "required_argument_missing"
    if "unknown" in normalized:
        return "unknown_command"
    if "failed:" in normalized or "error" in normalized:
        return "runtime_error"
    if code == 2:
        return "blocked"
    return "command_failed"


def runtime_level_for_status(status: str) -> str:
    if status == "completed":
        return "info"
    if status == "blocked":
        return "warning"
    return "error"


def runtime_diagnostics_for_result(command_path: str, status: str, reason: str) -> dict[str, Any]:
    if status == "completed":
        return {
            "recoverable": False,
            "next_action": "",
            "resume_command": "",
        }
    if reason == "human_check_required":
        next_action = "review_human_check_and_resume"
    elif reason in {"required_argument_missing", "unknown_command"}:
        next_action = "review_command_usage"
    elif status == "blocked":
        next_action = "inspect_block_reason_and_resume"
    else:
        next_action = "inspect_runtime_error"
    resume_command = f"aiwfctl {command_path}" if command_path else ""
    return {
        "recoverable": status == "blocked",
        "next_action": next_action,
        "resume_command": resume_command,
    }


@dataclass(frozen=True)
class RuntimeCommandEventContext:
    repo_root: Path
    command_path: str
    resume_command: str
    workflow: str
    operation_id: str
    input: dict[str, Any]

    @classmethod
    def from_args(cls, args: Any, repo_root: Path) -> RuntimeCommandEventContext:
        path = command_path(args)
        return cls(
            repo_root=repo_root,
            command_path=path,
            resume_command=runtime_resume_command(args),
            workflow=runtime_workflow(args),
            operation_id=runtime_operation_id(path),
            input=runtime_log_input(args, repo_root),
        )

    def emit_started(self, event_logger: RuntimeEventLogger) -> dict[str, Any]:
        return event_logger.emit(
            "runtime_command_started",
            command=self.command_path,
            phase="execute",
            operation_id=self.operation_id,
            diagnostics={
                "recoverable": False,
                "next_action": "",
                "resume_command": "",
            },
            input=self.input,
        )

    def emit_failed(self, event_logger: RuntimeEventLogger, exc: Exception, *, duration_ms: int) -> dict[str, Any]:
        return event_logger.emit(
            "runtime_command_failed",
            command=self.command_path,
            level="error",
            phase="execute",
            operation_id=self.operation_id,
            error_type=type(exc).__name__,
            diagnostics={
                "recoverable": False,
                "next_action": "inspect_runtime_error",
                "resume_command": self.resume_command,
            },
            input=self.input,
            output={
                "status": "failed",
                "exit_code": 1,
                "duration_ms": duration_ms,
                "output_bytes": 0,
                "reason": "exception",
                "error": str(exc),
            },
        )

    def emit_completed(
        self,
        event_logger: RuntimeEventLogger,
        *,
        code: int,
        output: str,
        duration_ms: int,
    ) -> dict[str, Any]:
        status = runtime_status_for_exit_code(code)
        reason = runtime_reason_for_result(code, output)
        return event_logger.emit(
            "runtime_command_completed",
            command=self.command_path,
            level=runtime_level_for_status(status),
            phase="execute",
            operation_id=self.operation_id,
            diagnostics={
                **runtime_diagnostics_for_result(self.command_path, status, reason),
                "resume_command": self.resume_command if status != "completed" else "",
            },
            input=self.input,
            output={
                "status": status,
                "exit_code": code,
                "duration_ms": duration_ms,
                "output_bytes": len(output.encode("utf-8")),
                "reason": reason,
            },
        )
