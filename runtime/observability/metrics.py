from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from runtime.common import relative_to_repo, write_json
from runtime.constants.schemas import RUNTIME_METRICS_SCHEMA
from runtime.constants.workspace import context_file, manifest_path_for_work_dir, test_evidence_dir_for_work_dir
from runtime.observability.logger import append_jsonl, resolve_log_path
from runtime.observability.schema import (
    ARTIFACT_TYPE,
    SCHEMA_VERSION,
    context_usage,
    cost_usage,
    runtime_metric_record,
    runtime_status,
    token_usage,
    utc_now_iso,
)

def _duration_ms(started: float | None) -> int:
    if started is None:
        return 0
    return max(int((perf_counter() - started) * 1000), 0)


def _default_log_dir(repo_root: Path) -> Path:
    return repo_root / "logs"


def register_runtime_metrics_context(
    *,
    repo_root: Path,
    work_dir: Path,
    metrics_path: Path,
    required: bool = False,
    status: str = "available",
) -> dict[str, Any]:
    from runtime.workflow.context_first import register_context

    return register_context(
        repo_root,
        work_dir,
        work_id=work_dir.name,
        context_type="runtime-metrics",
        path=metrics_path,
        required=required,
        generated_by="runtime-observability",
        owner="workflow",
        schema=RUNTIME_METRICS_SCHEMA,
        status=status,
    )


class RuntimeMetricsCollector:
    def __init__(
        self,
        *,
        repo_root: Path,
        work_dir: Path | None = None,
        workflow_id: str = "",
        workflow_name: str = "",
        agent_name: str = "",
        log_dir: Path | None = None,
        log_base_path: Path | None = None,
        rotate_monthly: bool = True,
    ) -> None:
        self.repo_root = repo_root
        self.work_dir = work_dir
        self.workflow_id = workflow_id or (work_dir.name if work_dir else "")
        self.workflow_name = workflow_name
        self.agent_name = agent_name
        self.log_dir = log_dir or _default_log_dir(repo_root)
        self.log_base_path = log_base_path
        self.rotate_monthly = rotate_monthly
        self.started_at = ""
        self.ended_at = ""
        self._workflow_started_perf: float | None = None
        self._agent_started_perf: dict[str, float] = {}
        self._token_usage = token_usage()
        self._context_usage = context_usage()
        self._runtime_status = runtime_status()
        self._cost_usage = cost_usage()
        self.events: list[dict[str, Any]] = []
        self.write_warnings: list[dict[str, Any]] = []

    def log_path(self, now: datetime | None = None) -> Path:
        return resolve_log_path(
            log_dir=self.log_dir,
            base_path=self.log_base_path,
            rotate_monthly=self.rotate_monthly,
            now=now,
        )

    def _append(self, record: dict[str, Any]) -> dict[str, Any]:
        write_result = append_jsonl(self.log_path(), record)
        if write_result["status"] != "ok":
            self.write_warnings.append(write_result)
        return {**record, "_write": write_result}

    def record_event(self, event: str, *, agent_name: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        record = runtime_metric_record(
            event=event,
            workflow_id=self.workflow_id,
            workflow_name=self.workflow_name,
            agent_name=agent_name or self.agent_name,
            started_at=self.started_at,
            ended_at=self.ended_at,
            duration_ms=_duration_ms(self._workflow_started_perf),
            token=self._token_usage,
            context=self._context_usage,
            runtime=self._runtime_status,
            cost=self._cost_usage,
            metadata=metadata or {},
        )
        self.events.append(record)
        return self._append(record)

    def workflow_started(self, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        self.started_at = utc_now_iso()
        self._workflow_started_perf = perf_counter()
        return self.record_event("workflow_started", metadata=metadata)

    def workflow_completed(self, *, save_evidence: bool = True, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        self.ended_at = utc_now_iso()
        result = self.record_event("workflow_completed", metadata=metadata)
        if save_evidence and self.work_dir is not None:
            self.save_evidence_summary()
        return result

    def workflow_failed(self, *, error: str = "", save_evidence: bool = True) -> dict[str, Any]:
        self.ended_at = utc_now_iso()
        self._runtime_status["error_count"] = int(self._runtime_status.get("error_count", 0)) + 1
        result = self.record_event("workflow_failed", metadata={"error": error} if error else {})
        if save_evidence and self.work_dir is not None:
            self.save_evidence_summary(status="human-check-required")
        return result

    def agent_started(self, agent_name: str) -> dict[str, Any]:
        self._agent_started_perf[agent_name] = perf_counter()
        return self.record_event("agent_started", agent_name=agent_name)

    def agent_completed(self, agent_name: str) -> dict[str, Any]:
        started = self._agent_started_perf.pop(agent_name, None)
        return self.record_event(
            "agent_completed",
            agent_name=agent_name,
            metadata={"agent_duration_ms": _duration_ms(started)},
        )

    def record_token_usage(
        self,
        *,
        input_tokens: Any = 0,
        output_tokens: Any = 0,
        total_tokens: Any | None = None,
        estimated: bool = True,
        input_cost: Any = 0.0,
        output_cost: Any = 0.0,
        total_cost: Any | None = None,
        currency: str = "USD",
    ) -> dict[str, Any]:
        self._token_usage = token_usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated=estimated,
        )
        self._cost_usage = cost_usage(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            currency=currency,
            estimated=estimated,
        )
        return self.record_event("token_usage_recorded")

    def record_context_usage(
        self,
        *,
        selected_context_count: Any = 0,
        estimated_context_tokens: Any = 0,
        rag_reference_count: Any = 0,
        dispatcher_route: str = "",
    ) -> dict[str, Any]:
        self._context_usage = context_usage(
            selected_context_count=selected_context_count,
            estimated_context_tokens=estimated_context_tokens,
            rag_reference_count=rag_reference_count,
            dispatcher_route=dispatcher_route,
        )
        return self.record_event("context_usage_recorded")

    def human_check_required(self, *, reason: str = "") -> dict[str, Any]:
        self._runtime_status["human_check_required"] = True
        return self.record_event("human_check_required", metadata={"reason": reason} if reason else {})

    def evidence_generated(self, *, path: str = "") -> dict[str, Any]:
        self._runtime_status["evidence_generated"] = True
        return self.record_event("evidence_generated", metadata={"path": path} if path else {})

    def runtime_error(self, *, error: str = "") -> dict[str, Any]:
        self._runtime_status["error_count"] = int(self._runtime_status.get("error_count", 0)) + 1
        return self.record_event("runtime_error", metadata={"error": error} if error else {})

    def summary(self, *, status: str = "available") -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": ARTIFACT_TYPE,
            "generated_at": utc_now_iso(),
            "status": status,
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms": _duration_ms(self._workflow_started_perf),
            "event_count": len(self.events),
            "token_usage": self._token_usage,
            "context": self._context_usage,
            "runtime": self._runtime_status,
            "cost": self._cost_usage,
            "log_path": relative_to_repo(self.repo_root, self.log_path()),
            "write_warnings": self.write_warnings,
            "events": self.events,
        }

    def save_evidence_summary(
        self,
        *,
        status: str = "available",
        register_context: bool = True,
    ) -> dict[str, Any]:
        if self.work_dir is None:
            return {"status": "skipped", "reason": "work_dir is not set"}
        payload = self.summary(status=status)
        test_evidence_path = test_evidence_dir_for_work_dir(self.work_dir) / "runtime-metrics.json"
        context_path = context_file(self.work_dir, "runtime-metrics.json")
        try:
            write_json(test_evidence_path, payload)
            write_json(context_path, payload)
            manifest = None
            if register_context:
                manifest = register_runtime_metrics_context(
                    repo_root=self.repo_root,
                    work_dir=self.work_dir,
                    metrics_path=context_path,
                    status=status,
                )
            return {
                "status": "ok",
                "test_evidence_path": relative_to_repo(self.repo_root, test_evidence_path),
                "context_path": relative_to_repo(self.repo_root, context_path),
                "context_manifest": relative_to_repo(self.repo_root, manifest_path_for_work_dir(self.work_dir)) if manifest else "",
            }
        except OSError as exc:
            warning = {"status": "warning", "warning": f"runtime metrics evidence write failed: {exc}"}
            self.write_warnings.append(warning)
            return warning
