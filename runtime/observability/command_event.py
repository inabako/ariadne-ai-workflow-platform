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
    workflow: str
    operation_id: str
    input: dict[str, Any]

    @classmethod
    def from_args(cls, args: Any, repo_root: Path) -> RuntimeCommandEventContext:
        path = command_path(args)
        return cls(
            repo_root=repo_root,
            command_path=path,
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
                "resume_command": f"aiwfctl {self.command_path}" if self.command_path else "",
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
            diagnostics=runtime_diagnostics_for_result(self.command_path, status, reason),
            input=self.input,
            output={
                "status": status,
                "exit_code": code,
                "duration_ms": duration_ms,
                "output_bytes": len(output.encode("utf-8")),
                "reason": reason,
            },
        )
