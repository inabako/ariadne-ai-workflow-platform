from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.common import read_json, relative_to_repo, utc_now_iso, write_json, write_markdown
from runtime.constants.runtime_values import SCHEMA_VERSION
from runtime.constants.schemas import IAC_PREPARE_REPORT_SCHEMA
from runtime.constants.workspace import (
    design_document_dir_for_work_dir,
    manifest_path_for_work_dir,
    process_report_dir_for_work_dir,
    requirements_dir_for_work_dir,
    resolve_work_dir,
)
from runtime.workflow import iac_deployment_runtime
from runtime.workflow import kubernetes_runtime
from runtime.workflow.context_first import register_context


ARTIFACT_TYPE = "iac-prepare-report"


def report_json_path(work_dir: Path) -> Path:
    return process_report_dir_for_work_dir(work_dir) / "iac-prepare-report.json"


def report_markdown_path(work_dir: Path) -> Path:
    return process_report_dir_for_work_dir(work_dir) / "iac-prepare-report.md"


def relative_artifact(repo_root: Path, path: Path) -> str:
    return relative_to_repo(repo_root, path)


def status_rank(status: str) -> int:
    if status in {"blocked", "failed", "fail", "human-check-required"}:
        return 3
    if status in {"incomplete", "blocked-for-iac-finalization", "generation-constrained", "compatible-with-gaps", "generated-with-gaps"}:
        return 2
    if status in {"warning", "dry-run"}:
        return 1
    return 0


def overall_status(step_results: list[dict[str, Any]]) -> str:
    worst = max((status_rank(str(item.get("status", ""))) for item in step_results), default=0)
    if worst >= 3:
        return "blocked"
    if worst == 2:
        return "prepared-with-gaps"
    if worst == 1:
        return "prepared"
    return "ready-for-e2e"


def detect_provider(provider: str, kubernetes_assessment: dict[str, Any] | None) -> str:
    normalized = (provider or "auto").strip().lower()
    if normalized in {"kubernetes", "k8s", "k3s"}:
        return "kubernetes"
    if not kubernetes_assessment:
        return "none"
    if kubernetes_assessment.get("requested"):
        return "kubernetes"
    return "none"


def step(name: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "artifact_type": result.get("artifact_type", ""),
        "status": result.get("status", ""),
        "artifacts": result.get("artifacts", {}),
    }


def provider_detection_sources(repo_root: Path, work_dir: Path, source: list[str] | None) -> list[str]:
    if source:
        return source
    paths: list[Path] = []
    for root in [requirements_dir_for_work_dir(work_dir), design_document_dir_for_work_dir(work_dir)]:
        if not root.exists():
            continue
        for pattern in ("*.md", "*.txt", "*.json"):
            paths.extend(root.glob(pattern))
    return [relative_artifact(repo_root, path) for path in sorted(paths, key=lambda item: item.as_posix().lower())]


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# IaC Prepare Report",
        "",
        f"- Work ID: `{report.get('work_id', '')}`",
        f"- Status: `{report.get('status', '')}`",
        f"- Provider: `{report.get('provider', '')}`",
        "",
        "## Steps",
        "",
    ]
    for item in report.get("steps", []):
        lines.append(f"- `{item.get('name', '')}` -> `{item.get('status', '')}`")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- `{item}`" for item in report.get("next_actions", []))
    return "\n".join(lines)


def build_prepare(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    provider: str = "auto",
    source: list[str] | None = None,
    spec_delta: str = "",
    force: bool = False,
) -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    steps: list[dict[str, Any]] = []

    app_assessment = iac_deployment_runtime.build_assessment(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), source=source)
    deployment_contract = iac_deployment_runtime.build_contract(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), source=source)
    deployment_gap = iac_deployment_runtime.build_gap_report(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), source=source)
    steps.extend(
        [
            step("deployment-assess", app_assessment),
            step("deployment-contract", deployment_contract),
            step("deployment-gap-report", deployment_gap),
        ]
    )
    provider_sources = provider_detection_sources(repo_root, resolved_work_dir, source)

    kubernetes_assessment = kubernetes_runtime.build_compatibility_assessment(
        repo_root,
        work_id=work_id,
        work_dir=str(resolved_work_dir),
        target="auto" if provider == "auto" else provider,
        requirements=provider_sources,
    )
    selected_provider = detect_provider(provider, kubernetes_assessment)

    if selected_provider == "kubernetes":
        kubernetes_gap = kubernetes_runtime.build_gap_report(
            repo_root,
            work_id=work_id,
            work_dir=str(resolved_work_dir),
            target="auto" if provider == "auto" else provider,
            requirements=provider_sources,
        )
        generation = kubernetes_runtime.build_manifest_generation(
            repo_root,
            work_id=work_id,
            work_dir=str(resolved_work_dir),
            spec_delta=spec_delta,
            force=force,
        )
        dry_run = kubernetes_runtime.build_dry_run_evidence(repo_root, work_id=work_id, work_dir=str(resolved_work_dir))
        e2e_plan = kubernetes_runtime.build_kubernetes_e2e_plan(repo_root, work_id=work_id, work_dir=str(resolved_work_dir))
        steps.extend(
            [
                step("kubernetes-assess", kubernetes_assessment),
                step("kubernetes-gap-report", kubernetes_gap),
                step("kubernetes-generate", generation),
                step("kubernetes-dry-run", dry_run),
                step("kubernetes-e2e-plan", e2e_plan),
            ]
        )
        next_actions = [
            f"aiwfctl e2e readiness --work-id {work_id} --test-kind integration",
            f"aiwfctl e2e run --work-id {work_id} --test-kind integration --dry-run",
            f"aiwfctl iac kubernetes evidence --work-id {work_id}",
        ]
    else:
        steps.append(step("kubernetes-assess", kubernetes_assessment))
        next_actions = [
            f"aiwfctl iac deployment gap-report --work-id {work_id}",
            "Provider-specific IaC was not detected. Add provider details or run provider-specific IaC command explicitly.",
        ]

    report = {
        "schema_version": SCHEMA_VERSION,
        "schema": IAC_PREPARE_REPORT_SCHEMA,
        "artifact_type": ARTIFACT_TYPE,
        "status": overall_status(steps),
        "work_id": work_id,
        "provider": selected_provider,
        "generated_at": utc_now_iso(),
        "steps": steps,
        "rules": {
            "deployment_contract_before_provider_iac": True,
            "provider_specific_iac_is_prepared_only_when_detected": True,
            "real_apply_requires_separate_human_check": True,
        },
        "next_actions": next_actions,
    }
    json_path = report_json_path(resolved_work_dir)
    markdown_path = report_markdown_path(resolved_work_dir)
    report["artifacts"] = {
        "prepare_json": relative_artifact(repo_root, json_path),
        "prepare_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, report)
    write_markdown(markdown_path, render_report(report))
    manifest = register_context(
        repo_root,
        resolved_work_dir,
        work_id=work_id,
        context_type=ARTIFACT_TYPE,
        path=json_path,
        required=False,
        generated_by="iac-prepare-runtime",
        owner="iac",
        schema=IAC_PREPARE_REPORT_SCHEMA,
        status=report["status"],
    )
    report["manifest_path"] = relative_artifact(repo_root, manifest_path_for_work_dir(resolved_work_dir))
    report["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(json_path, report)
    return report


def run(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    return build_prepare(
        repo_root,
        work_id=getattr(args, "work_id", ""),
        work_dir=getattr(args, "work_dir", ""),
        provider=getattr(args, "provider", "auto"),
        source=getattr(args, "source", []),
        spec_delta=getattr(args, "spec_delta", ""),
        force=getattr(args, "force", False),
    )


def format_result(result: dict[str, Any]) -> str:
    lines = [
        "IaC Prepare",
        "",
        f"Status  : {result.get('status', '')}",
        f"Work ID : {result.get('work_id', '')}",
        f"Provider: {result.get('provider', '')}",
        "",
        "Steps",
    ]
    lines.extend(f"  - {item.get('name', '')}: {item.get('status', '')}" for item in result.get("steps", []))
    artifacts = result.get("artifacts", {})
    if artifacts:
        lines.extend(["", "Artifacts"])
        lines.extend(f"  - {key}: {value}" for key, value in artifacts.items())
    next_actions = result.get("next_actions", [])
    if next_actions:
        lines.extend(["", "Next Actions"])
        lines.extend(f"  - {item}" for item in next_actions)
    return "\n".join(lines).rstrip() + "\n"
