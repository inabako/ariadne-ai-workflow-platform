from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..contracts import WorkflowRequest, WorkflowResult, WorkflowStatus


@dataclass(frozen=True)
class FrameworkAdapterPattern:
    adapter_name: str
    framework_name: str

    def build_execution_plan(
        self,
        request: WorkflowRequest,
        *,
        framework_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        contract = request.to_contract()
        return {
            "schema_version": "1.0",
            "adapter": self.adapter_name,
            "framework": self.framework_name,
            "workflow_request": contract,
            "runtime_context": {
                "schema_version": "1.0",
                "workflow_id": contract["workflow_id"],
                "trace_id": contract["trace_id"],
                "agent": {},
                "tools": {},
                "model": {},
                "human_check": {},
                "retry": {},
                "limits": {},
                "evidence": {},
                "checkpoint": {},
            },
            "framework_metadata": framework_metadata or {},
        }

    def result_from_plan(
        self,
        plan: dict[str, Any],
        *,
        status: WorkflowStatus = WorkflowStatus.RUNNING,
        outputs: list[dict[str, Any]] | None = None,
        evidence: list[dict[str, Any]] | None = None,
        errors: list[dict[str, Any]] | None = None,
        next_action: str | None = None,
        completed_at: str | None = None,
    ) -> dict[str, Any]:
        request = plan["workflow_request"]
        return WorkflowResult(
            workflow_id=request["workflow_id"],
            trace_id=request["trace_id"],
            status=status,
            outputs=outputs or [],
            evidence=evidence or [],
            errors=errors or [],
            next_action=next_action,
            completed_at=completed_at,
        ).to_contract()
