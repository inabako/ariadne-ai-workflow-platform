from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from runtime.common import read_json, relative_to_repo, slugify, utc_now_iso, write_json, write_markdown
from runtime.constants.runtime_values import SCHEMA_VERSION
from runtime.constants.schemas import (
    IAC_APP_RUNTIME_ASSESSMENT_SCHEMA,
    IAC_DEPLOYMENT_CONTRACT_SCHEMA,
    IAC_DEPLOYMENT_GAP_REPORT_SCHEMA,
)
from runtime.constants.workspace import (
    context_dir_for_work_dir,
    context_file,
    design_document_dir_for_work_dir,
    manifest_path_for_work_dir,
    process_report_dir_for_work_dir,
    requirements_dir_for_work_dir,
    resolve_work_dir,
)
from runtime.workflow.context_first import register_context


ASSESSMENT_ARTIFACT_TYPE = "iac-app-runtime-assessment"
CONTRACT_ARTIFACT_TYPE = "iac-deployment-contract"
GAP_REPORT_ARTIFACT_TYPE = "iac-deployment-gap-report"
DEFAULT_APP_NAME = "ariadne-app"
DEFAULT_PORT = 8080
DEFAULT_HEALTH_PATH = "/health"
DEFAULT_SERVICE_TYPE = "web"


def normalize_items(values: list[str] | tuple[str, ...] | None) -> list[str]:
    return [str(value).strip() for value in values or [] if str(value).strip()]


def relative_artifact(repo_root: Path, path: Path) -> str:
    return relative_to_repo(repo_root, path)


def assessment_path(work_dir: Path) -> Path:
    return context_file(work_dir, "iac-app-runtime-assessment.json")


def contract_json_path(work_dir: Path) -> Path:
    return context_file(work_dir, "iac-deployment-contract.json")


def contract_markdown_path(work_dir: Path) -> Path:
    return context_file(work_dir, "iac-deployment-contract.md")


def gap_report_json_path(work_dir: Path) -> Path:
    return process_report_dir_for_work_dir(work_dir) / "iac-deployment-gap-report.json"


def gap_report_markdown_path(work_dir: Path) -> Path:
    return process_report_dir_for_work_dir(work_dir) / "iac-deployment-gap-report.md"


def resolve_input_path(repo_root: Path, work_dir: Path, value: str) -> Path:
    raw = Path(value)
    if raw.is_absolute():
        return raw
    candidate = work_dir / raw
    if candidate.exists():
        return candidate
    return repo_root / raw


def source_candidate_paths(work_dir: Path) -> list[Path]:
    roots = [
        requirements_dir_for_work_dir(work_dir),
        design_document_dir_for_work_dir(work_dir),
        context_dir_for_work_dir(work_dir),
    ]
    paths: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for pattern in ("*.md", "*.txt", "*.json"):
            paths.extend(root.glob(pattern))
    return sorted({path for path in paths if path.is_file()}, key=lambda item: item.as_posix().lower())


def read_source_documents(repo_root: Path, work_dir: Path, sources: list[str] | None) -> list[dict[str, Any]]:
    paths = [resolve_input_path(repo_root, work_dir, value) for value in normalize_items(sources)]
    if not paths:
        paths = source_candidate_paths(work_dir)
    documents: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            documents.append({"path": relative_artifact(repo_root, path), "status": "missing", "content": ""})
            continue
        documents.append(
            {
                "path": relative_artifact(repo_root, path),
                "status": "loaded",
                "content": path.read_text(encoding="utf-8-sig", errors="ignore"),
            }
        )
    return documents


def first_match(patterns: list[str], text: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip().strip("`\"'")
    return ""


def extract_int(patterns: list[str], text: str) -> int | None:
    value = first_match(patterns, text)
    if not value:
        return None
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed


def infer_execution_unit(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ("cronjob", "cron job", "scheduled job")):
        return "cron"
    if any(word in lower for word in ("batch", "job runner")):
        return "batch"
    if any(word in lower for word in ("worker", "queue consumer", "consumer")):
        return "worker"
    if any(word in lower for word in ("daemon", "agent", "sidecar")):
        return "daemon"
    if any(word in lower for word in ("web", "api", "http", "service", "frontend")):
        return "web"
    return "unknown"


def extract_detected_values(text: str) -> dict[str, Any]:
    lower = text.lower()
    app_name = first_match([r"(?:app|application|service)\s+name\s*[:=]\s*([a-zA-Z0-9][-_a-zA-Z0-9]+)"], text)
    image = first_match(
        [
            r"(?:container\s+image|docker\s+image|image)\s*[:=]\s*([^\s,]+)",
            r"`([^`]+:[^`]+)`",
        ],
        text,
    )
    start_command = first_match([r"(?:start\s+command|command|entrypoint)\s*[:=]\s*(.+)$"], text)
    health_path = first_match([r"(?:health|readiness|liveness)\s+(?:path|endpoint)\s*[:=]\s*(/[^\s,]+)"], text)
    return {
        "app_name": slugify(app_name) if app_name else "",
        "execution_unit": infer_execution_unit(text),
        "image": image,
        "start_command": start_command,
        "port": extract_int([r"(?:service\s+port|container\s+port|containerPort|port)\s*[:=]\s*(\d{2,5})"], text),
        "health_path": health_path,
        "has_env_config": any(word in lower for word in ("env", "environment variable", "configmap", "configuration")),
        "has_secret_boundary": any(word in lower for word in ("secret", "credential", "token", "password")),
        "has_external_dependency": any(word in lower for word in ("database", "redis", "queue", "mq", "s3", "object storage", "external api")),
        "dependencies": sorted(
            {
                name
                for name, aliases in {
                    "database": ("database", "postgres", "mysql", "sqlite"),
                    "redis": ("redis",),
                    "queue": ("queue", "mq", "rabbitmq", "kafka"),
                    "object-storage": ("s3", "object storage", "blob"),
                    "external-api": ("external api", "third party api"),
                }.items()
                if any(alias in lower for alias in aliases)
            }
        ),
        "stateful": any(word in lower for word in ("stateful", "storage", "volume", "pvc", "database")),
        "has_storage_policy": any(word in lower for word in ("storageclass", "pvc", "persistentvolume", "backup", "restore")),
        "has_resource_policy": any(word in lower for word in ("resources", "requests", "limits", "cpu", "memory")),
        "has_startup_shutdown_policy": any(word in lower for word in ("startup", "shutdown", "graceful", "termination", "prestop")),
        "has_observability": any(word in lower for word in ("log", "metrics", "trace", "opentelemetry", "prometheus")),
        "has_e2e_target": any(word in lower for word in ("e2e", "acceptance", "business endpoint", "smoke")),
    }


def capability(name: str, status: str, reason: str, evidence_refs: list[str]) -> dict[str, Any]:
    return {"name": name, "status": status, "reason": reason, "evidence_refs": evidence_refs}


def build_assessment(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    source: list[str] | None = None,
) -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    documents = read_source_documents(repo_root, resolved_work_dir, source)
    loaded = [item for item in documents if item["status"] == "loaded"]
    text = "\n\n".join(item["content"] for item in loaded)
    detected = extract_detected_values(text)
    evidence_refs = [item["path"] for item in loaded]
    is_web_like = detected["execution_unit"] in {"web", "unknown"}
    capabilities = [
        capability("execution_unit", "ready" if detected["execution_unit"] != "unknown" else "missing", "アプリの実行単位です。", evidence_refs),
        capability("container_image", "ready" if detected["image"] else "missing", "IaC が配置する container image です。", evidence_refs),
        capability("service_port", "ready" if detected["port"] or not is_web_like else "missing", "Service や疎通確認に使う port です。", evidence_refs),
        capability("health_endpoint", "ready" if detected["health_path"] or not is_web_like else "missing", "readiness / liveness / smoke check に使う endpoint です。", evidence_refs),
        capability("env_config", "ready" if detected["has_env_config"] else "missing", "ConfigMap / env の境界です。", evidence_refs),
        capability("secret_boundary", "ready" if detected["has_secret_boundary"] else "missing", "Secret や credential の境界です。", evidence_refs),
        capability("external_dependencies", "ready" if detected["has_external_dependency"] else "not-applicable", "外部依存の有無です。", evidence_refs),
        capability("storage_policy", "ready" if not detected["stateful"] or detected["has_storage_policy"] else "missing", "永続化が必要な場合の storage 方針です。", evidence_refs),
        capability("resource_policy", "ready" if detected["has_resource_policy"] else "missing", "CPU/Memory requests/limits の方針です。", evidence_refs),
        capability("startup_shutdown_policy", "ready" if detected["has_startup_shutdown_policy"] else "missing", "起動、停止、復帰の運用条件です。", evidence_refs),
        capability("observability", "ready" if detected["has_observability"] else "missing", "ログ、metrics、trace の観測条件です。", evidence_refs),
        capability("e2e_target", "ready" if detected["has_e2e_target"] else "missing", "E2E が照合する endpoint や業務シナリオです。", evidence_refs),
    ]
    missing = [item["name"] for item in capabilities if item["status"] == "missing"]
    status = "ready" if not missing else "incomplete"
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": IAC_APP_RUNTIME_ASSESSMENT_SCHEMA,
        "artifact_type": ASSESSMENT_ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "generated_at": utc_now_iso(),
        "source_documents": [{"path": item["path"], "status": item["status"]} for item in documents],
        "detected": detected,
        "capabilities": capabilities,
        "missing_capabilities": missing,
        "rules": {
            "assessment_before_iac_generation": True,
            "infrastructure_must_follow_deployment_contract": True,
        },
        "next_actions": [
            f"aiwfctl iac deployment contract --work-id {work_id}",
            f"aiwfctl iac deployment gap-report --work-id {work_id}",
        ],
    }
    output_path = assessment_path(resolved_work_dir)
    result["artifacts"] = {"assessment_json": relative_artifact(repo_root, output_path)}
    write_json(output_path, result)
    manifest = register_context(
        repo_root,
        resolved_work_dir,
        work_id=work_id,
        context_type=ASSESSMENT_ARTIFACT_TYPE,
        path=output_path,
        required=False,
        generated_by="iac-deployment-runtime",
        owner="iac",
        schema=IAC_APP_RUNTIME_ASSESSMENT_SCHEMA,
        status=status,
    )
    result["manifest_path"] = relative_artifact(repo_root, manifest_path_for_work_dir(resolved_work_dir))
    result["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(output_path, result)
    return result


def contract_from_assessment(work_id: str, assessment: dict[str, Any]) -> dict[str, Any]:
    detected = assessment.get("detected", {})
    execution_unit = detected.get("execution_unit") or "unknown"
    return {
        "app_name": detected.get("app_name") or slugify(work_id) or DEFAULT_APP_NAME,
        "execution_unit": execution_unit,
        "image": detected.get("image") or "REPLACE_WITH_IMAGE",
        "start_command": detected.get("start_command") or "",
        "ports": [detected["port"] or DEFAULT_PORT] if execution_unit in {"web", "unknown"} else [],
        "health": {
            "path": detected.get("health_path") or DEFAULT_HEALTH_PATH,
            "readiness_required": execution_unit in {"web", "unknown"},
            "liveness_required": execution_unit in {"web", "unknown"},
        },
        "configuration": {
            "env_config_required": bool(detected.get("has_env_config")),
            "secret_boundary_required": bool(detected.get("has_secret_boundary")),
        },
        "dependencies": detected.get("dependencies", []),
        "storage": {
            "stateful": bool(detected.get("stateful")),
            "policy_defined": bool(detected.get("has_storage_policy")),
        },
        "resources": {
            "policy_defined": bool(detected.get("has_resource_policy")),
            "cpu_request": "100m",
            "memory_request": "128Mi",
            "cpu_limit": "500m",
            "memory_limit": "512Mi",
        },
        "operations": {
            "startup_shutdown_policy_defined": bool(detected.get("has_startup_shutdown_policy")),
            "observability_defined": bool(detected.get("has_observability")),
            "e2e_target_defined": bool(detected.get("has_e2e_target")),
        },
    }


def render_contract_markdown(contract: dict[str, Any]) -> str:
    payload = contract.get("contract", {})
    lines = [
        "# IaC Deployment Contract",
        "",
        f"- Work ID: `{contract.get('work_id', '')}`",
        f"- Status: `{contract.get('status', '')}`",
        f"- App: `{payload.get('app_name', '')}`",
        f"- Execution Unit: `{payload.get('execution_unit', '')}`",
        f"- Image: `{payload.get('image', '')}`",
        f"- Ports: `{', '.join(str(item) for item in payload.get('ports', [])) or 'none'}`",
        f"- Health Path: `{payload.get('health', {}).get('path', '')}`",
        "",
        "## Missing Capabilities",
        "",
    ]
    lines.extend(f"- {item}" for item in contract.get("missing_capabilities", []) or ["none"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- `{item}`" for item in contract.get("next_actions", []))
    return "\n".join(lines)


def build_contract(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    source: list[str] | None = None,
) -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    assessment = read_json(assessment_path(resolved_work_dir), default={})
    if not isinstance(assessment, dict) or not assessment:
        assessment = build_assessment(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), source=source)
    missing = list(assessment.get("missing_capabilities", []))
    contract = {
        "schema_version": SCHEMA_VERSION,
        "schema": IAC_DEPLOYMENT_CONTRACT_SCHEMA,
        "artifact_type": CONTRACT_ARTIFACT_TYPE,
        "status": "draft-with-gaps" if missing else "ready",
        "work_id": work_id,
        "generated_at": utc_now_iso(),
        "assessment_path": relative_artifact(repo_root, assessment_path(resolved_work_dir)),
        "missing_capabilities": missing,
        "contract": contract_from_assessment(work_id, assessment),
        "rules": {
            "deployment_contract_is_iac_input": True,
            "do_not_embed_secret_values": True,
            "human_review_required_before_real_apply": True,
        },
        "next_actions": [
            f"aiwfctl iac deployment gap-report --work-id {work_id}",
            f"aiwfctl iac kubernetes assess --work-id {work_id}",
        ],
    }
    json_path = contract_json_path(resolved_work_dir)
    markdown_path = contract_markdown_path(resolved_work_dir)
    contract["artifacts"] = {
        "contract_json": relative_artifact(repo_root, json_path),
        "contract_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, contract)
    write_markdown(markdown_path, render_contract_markdown(contract))
    manifest = register_context(
        repo_root,
        resolved_work_dir,
        work_id=work_id,
        context_type=CONTRACT_ARTIFACT_TYPE,
        path=json_path,
        required=False,
        generated_by="iac-deployment-runtime",
        owner="iac",
        schema=IAC_DEPLOYMENT_CONTRACT_SCHEMA,
        status=contract["status"],
    )
    contract["manifest_path"] = relative_artifact(repo_root, manifest_path_for_work_dir(resolved_work_dir))
    contract["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(json_path, contract)
    return contract


def gap_item(gap_id: str, severity: str, category: str, title: str, recommendation: str) -> dict[str, str]:
    return {
        "gap_id": gap_id,
        "severity": severity,
        "category": category,
        "title": title,
        "recommendation": recommendation,
    }


def gaps_from_contract(contract: dict[str, Any]) -> list[dict[str, str]]:
    missing = set(contract.get("missing_capabilities", []))
    gaps: list[dict[str, str]] = []
    mapping = {
        "execution_unit": ("critical", "runtime", "アプリの実行単位が未確定です", "web / worker / batch / cron / daemon のどれかを設計書へ明記してください。"),
        "container_image": ("critical", "artifact", "container image が未確定です", "image、tag、registry、pull policy を確定してください。"),
        "service_port": ("high", "network", "公開または疎通 port が未確定です", "container port、service port、疎通確認方法を確定してください。"),
        "health_endpoint": ("high", "operations", "health endpoint が未確定です", "readiness/liveness/smoke check の path と期待 status を定義してください。"),
        "env_config": ("medium", "configuration", "ConfigMap/env 境界が未確定です", "環境変数と設定値の注入責務を定義してください。"),
        "secret_boundary": ("medium", "security", "Secret 境界が未確定です", "秘密値を IaC に直書きせず、Secret 名と参照だけを contract に残してください。"),
        "storage_policy": ("high", "storage", "永続化方針が未確定です", "stateful workload の PVC、backup、restore 条件を定義してください。"),
        "resource_policy": ("medium", "operations", "resources 方針が未確定です", "CPU/Memory requests/limits の初期値を決めてください。"),
        "startup_shutdown_policy": ("medium", "operations", "起動/停止条件が未確定です", "startup safe state、shutdown、graceful termination を定義してください。"),
        "observability": ("medium", "observability", "観測条件が未確定です", "log、metrics、trace、alert の最小条件を定義してください。"),
        "e2e_target": ("medium", "test", "E2E 照合対象が未確定です", "health だけでなく業務的に確認する endpoint / scenario を定義してください。"),
    }
    for key in sorted(missing):
        if key not in mapping:
            continue
        severity, category, title, recommendation = mapping[key]
        gaps.append(gap_item(key, severity, category, title, recommendation))
    return gaps


def render_gap_report(report: dict[str, Any]) -> str:
    lines = [
        "# IaC Deployment Gap Report",
        "",
        f"- Work ID: `{report.get('work_id', '')}`",
        f"- Status: `{report.get('status', '')}`",
        "",
        "## Gaps",
        "",
    ]
    lines.extend(
        f"- `{item['severity']}` `{item['gap_id']}`: {item['title']} / {item['recommendation']}"
        for item in report.get("gaps", [])
    )
    if not report.get("gaps"):
        lines.append("- none")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- `{item}`" for item in report.get("next_actions", []))
    return "\n".join(lines)


def build_gap_report(repo_root: Path, *, work_id: str, work_dir: str = "", source: list[str] | None = None) -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    contract = read_json(contract_json_path(resolved_work_dir), default={})
    if not isinstance(contract, dict) or not contract:
        contract = build_contract(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), source=source)
    gaps = gaps_from_contract(contract)
    critical_or_high = [item for item in gaps if item["severity"] in {"critical", "high"}]
    report = {
        "schema_version": SCHEMA_VERSION,
        "schema": IAC_DEPLOYMENT_GAP_REPORT_SCHEMA,
        "artifact_type": GAP_REPORT_ARTIFACT_TYPE,
        "status": "blocked-for-iac-finalization" if critical_or_high else "ready-for-iac",
        "work_id": work_id,
        "generated_at": utc_now_iso(),
        "contract_path": relative_artifact(repo_root, contract_json_path(resolved_work_dir)),
        "gaps": gaps,
        "rules": {
            "iac_finalization_requires_deployment_contract": True,
            "critical_or_high_gap_blocks_final_manifest": True,
        },
        "next_actions": [
            f"aiwfctl iac deployment contract --work-id {work_id}",
            f"aiwfctl iac kubernetes assess --work-id {work_id}",
        ],
    }
    json_path = gap_report_json_path(resolved_work_dir)
    markdown_path = gap_report_markdown_path(resolved_work_dir)
    report["artifacts"] = {
        "gap_report_json": relative_artifact(repo_root, json_path),
        "gap_report_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, report)
    write_markdown(markdown_path, render_gap_report(report))
    manifest = register_context(
        repo_root,
        resolved_work_dir,
        work_id=work_id,
        context_type=GAP_REPORT_ARTIFACT_TYPE,
        path=json_path,
        required=False,
        generated_by="iac-deployment-runtime",
        owner="iac",
        schema=IAC_DEPLOYMENT_GAP_REPORT_SCHEMA,
        status=report["status"],
    )
    report["manifest_path"] = relative_artifact(repo_root, manifest_path_for_work_dir(resolved_work_dir))
    report["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(json_path, report)
    return report


def run(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    command = getattr(args, "deployment_command", "")
    common = {
        "work_id": getattr(args, "work_id", ""),
        "work_dir": getattr(args, "work_dir", ""),
        "source": getattr(args, "source", []),
    }
    if command == "assess":
        return build_assessment(repo_root, **common)
    if command == "contract":
        return build_contract(repo_root, **common)
    if command == "gap-report":
        return build_gap_report(repo_root, **common)
    raise ValueError(f"Unknown IaC deployment command: {command}")


def format_result(result: dict[str, Any]) -> str:
    lines = [
        "IaC Deployment",
        "",
        f"Type   : {result.get('artifact_type', '')}",
        f"Status : {result.get('status', '')}",
        f"Work ID: {result.get('work_id', '')}",
    ]
    artifacts = result.get("artifacts", {})
    if artifacts:
        lines.extend(["", "Artifacts"])
        lines.extend(f"  - {key}: {value}" for key, value in artifacts.items())
    if result.get("missing_capabilities"):
        lines.extend(["", "Missing Capabilities"])
        lines.extend(f"  - {item}" for item in result["missing_capabilities"])
    if result.get("gaps"):
        lines.extend(["", "Gaps"])
        for item in result["gaps"]:
            lines.append(f"  - {item.get('severity', '')}: {item.get('gap_id', '')} - {item.get('title', '')}")
    next_actions = result.get("next_actions", [])
    if next_actions:
        lines.extend(["", "Next Actions"])
        lines.extend(f"  - {item}" for item in next_actions)
    return "\n".join(lines).rstrip() + "\n"
