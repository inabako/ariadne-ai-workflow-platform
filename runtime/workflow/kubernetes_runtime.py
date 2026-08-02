from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from runtime.common import read_json, relative_to_repo, slugify, utc_now_iso, write_json, write_markdown
from runtime.constants.runtime_values import SCHEMA_VERSION
from runtime.constants.schemas import (
    KUBERNETES_COMPATIBILITY_ASSESSMENT_SCHEMA,
    KUBERNETES_DRY_RUN_EVIDENCE_SCHEMA,
    KUBERNETES_EVIDENCE_SCHEMA,
    KUBERNETES_GAP_REPORT_SCHEMA,
    KUBERNETES_MANIFEST_GENERATION_SCHEMA,
)
from runtime.constants.workspace import (
    context_file,
    context_dir_for_work_dir,
    design_document_dir_for_work_dir,
    implementation_dir_for_work_dir,
    manifest_path_for_work_dir,
    process_report_dir_for_work_dir,
    requirements_dir_for_work_dir,
    resolve_work_dir,
    test_evidence_dir_for_work_dir,
)
from runtime.testing import e2e_runtime
from runtime.workflow.context_first import register_context
from runtime.workflow import iac_deployment_runtime


ARTIFACT_TYPE_ASSESSMENT = "kubernetes-compatibility-assessment"
ARTIFACT_TYPE_GAP_REPORT = "kubernetes-gap-report"
ARTIFACT_TYPE_MANIFEST_GENERATION = "kubernetes-manifest-generation"
ARTIFACT_TYPE_DRY_RUN = "kubernetes-dry-run-evidence"
ARTIFACT_TYPE_EVIDENCE = "kubernetes-evidence"
DEFAULT_NAMESPACE = "ariadne-work"
DEFAULT_PORT = 8080
DEFAULT_IMAGE = "REPLACE_WITH_IMAGE"
DEFAULT_REPLICAS = 1
DEFAULT_HEALTH_PATH = "/health"
DEFAULT_CPU_REQUEST = "100m"
DEFAULT_MEMORY_REQUEST = "128Mi"
DEFAULT_CPU_LIMIT = "500m"
DEFAULT_MEMORY_LIMIT = "512Mi"
DEFAULT_SERVICE_TYPE = "ClusterIP"
KUBECTL_TIMEOUT_SECONDS = 60
KUBERNETES_KEYWORDS = ("kubernetes", "k8s", "k3s", "kubectl", "manifest", "namespace", "deployment")
TEMPLATE_NAME = "kubernetes-app-template"
TEMPLATE_PATH = Path("templates/boilerplates/infrastructure/kubernetes-app-template")
TEMPLATE_MANIFEST_DIR = TEMPLATE_PATH / "manifests"
ALLOWED_SPEC_DELTA_KEYS = {
    "app_name",
    "namespace",
    "image",
    "port",
    "replicas",
    "health_path",
    "cpu_request",
    "memory_request",
    "cpu_limit",
    "memory_limit",
    "service_type",
}


def normalize_items(values: list[str] | tuple[str, ...] | None) -> list[str]:
    return [str(value).strip() for value in values or [] if str(value).strip()]


def resolve_input_path(repo_root: Path, work_dir: Path, value: str) -> Path:
    raw = Path(value)
    if raw.is_absolute():
        return raw
    candidate = work_dir / raw
    if candidate.exists():
        return candidate
    return repo_root / raw


def relative_artifact(repo_root: Path, path: Path) -> str:
    return relative_to_repo(repo_root, path)


def kubernetes_manifest_dir(work_dir: Path) -> Path:
    return implementation_dir_for_work_dir(work_dir) / "kubernetes" / "manifests"


def compatibility_path(work_dir: Path) -> Path:
    return context_file(work_dir, "kubernetes-compatibility-assessment.json")


def gap_report_json_path(work_dir: Path) -> Path:
    return process_report_dir_for_work_dir(work_dir) / "kubernetes-gap-report.json"


def gap_report_markdown_path(work_dir: Path) -> Path:
    return process_report_dir_for_work_dir(work_dir) / "kubernetes-gap-report.md"


def generation_path(work_dir: Path) -> Path:
    return context_file(work_dir, "kubernetes-manifest-generation.json")


def dry_run_json_path(work_dir: Path) -> Path:
    return test_evidence_dir_for_work_dir(work_dir) / "kubernetes" / "dry-run.json"


def dry_run_markdown_path(work_dir: Path) -> Path:
    return test_evidence_dir_for_work_dir(work_dir) / "kubernetes" / "dry-run.md"


def evidence_json_path(work_dir: Path) -> Path:
    return test_evidence_dir_for_work_dir(work_dir) / "kubernetes" / "evidence.json"


def evidence_markdown_path(work_dir: Path) -> Path:
    return test_evidence_dir_for_work_dir(work_dir) / "kubernetes" / "evidence.md"


def requirement_candidate_paths(work_dir: Path) -> list[Path]:
    roots = [
        requirements_dir_for_work_dir(work_dir),
        context_dir_for_work_dir(work_dir),
        design_document_dir_for_work_dir(work_dir),
    ]
    paths: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for pattern in ("*.md", "*.txt", "*.json"):
            paths.extend(root.glob(pattern))
    return sorted({path for path in paths if path.is_file()}, key=lambda item: item.as_posix().lower())


def read_source_documents(repo_root: Path, work_dir: Path, requirements: list[str] | None) -> list[dict[str, Any]]:
    paths = [resolve_input_path(repo_root, work_dir, value) for value in normalize_items(requirements)]
    if not paths:
        paths = requirement_candidate_paths(work_dir)
    documents: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            documents.append(
                {
                    "path": relative_artifact(repo_root, path),
                    "status": "missing",
                    "content": "",
                }
            )
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        documents.append(
            {
                "path": relative_artifact(repo_root, path),
                "status": "loaded",
                "content": text,
            }
        )
    return documents


def first_match(patterns: list[str], text: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip().strip("`\"'")
    return ""


def extract_port(text: str) -> int | None:
    value = first_match(
        [
            r"(?:service\s+port|container\s+port|containerPort|port)\s*[:=]\s*(\d{2,5})",
            r"(?:listen|listening)\s+on\s+(\d{2,5})",
        ],
        text,
    )
    if not value:
        return None
    try:
        port = int(value)
    except ValueError:
        return None
    return port if 1 <= port <= 65535 else None


def infer_target(text: str, explicit_target: str) -> str:
    target = (explicit_target or "auto").strip().lower()
    if target in {"kubernetes", "k8s", "k3s"}:
        return "kubernetes" if target == "k8s" else target
    lower = text.lower()
    if "k3s" in lower:
        return "k3s"
    if "kubernetes" in lower or "k8s" in lower:
        return "kubernetes"
    return "unspecified"


def detect_signals(text: str) -> dict[str, Any]:
    lower = text.lower()
    image = first_match(
        [
            r"(?:container\s+image|docker\s+image|image)\s*[:=]\s*([^\s,]+)",
            r"`([^`]+:[^`]+)`",
        ],
        text,
    )
    namespace = first_match([r"namespace\s*[:=]\s*([a-z0-9]([-a-z0-9]*[a-z0-9])?)"], text)
    app_name = first_match([r"(?:app|application|service)\s+name\s*[:=]\s*([a-zA-Z0-9][-_a-zA-Z0-9]+)"], text)
    return {
        "requested": any(keyword in lower for keyword in KUBERNETES_KEYWORDS),
        "image": image,
        "port": extract_port(text),
        "namespace": namespace,
        "app_name": slugify(app_name) if app_name else "",
        "has_container_runtime": any(keyword in lower for keyword in ("container", "docker", "image")),
        "has_health_probe": any(keyword in lower for keyword in ("health", "readiness", "liveness", "probe")),
        "has_resource_policy": any(keyword in lower for keyword in ("resource", "requests", "limits", "cpu", "memory")),
        "has_secret_boundary": any(keyword in lower for keyword in ("secret", "credential", "token", "configmap", "env")),
        "has_exposure_policy": any(keyword in lower for keyword in ("ingress", "loadbalancer", "nodeport", "service")),
        "stateful_requested": any(keyword in lower for keyword in ("database", "stateful", "pvc", "volume", "storage")),
        "has_storage_policy": any(keyword in lower for keyword in ("pvc", "persistentvolume", "volume", "storage")),
    }


def apply_deployment_contract_signals(repo_root: Path, work_dir: Path, signals: dict[str, Any]) -> tuple[dict[str, Any], str]:
    contract_path = iac_deployment_runtime.contract_json_path(work_dir)
    contract_payload = read_json(contract_path, default={})
    if not isinstance(contract_payload, dict) or not contract_payload:
        return signals, ""
    contract = contract_payload.get("contract", {})
    if not isinstance(contract, dict):
        return signals, ""
    merged = dict(signals)
    merged["app_name"] = merged.get("app_name") or contract.get("app_name", "")
    merged["image"] = merged.get("image") or contract.get("image", "")
    ports = contract.get("ports", [])
    if not merged.get("port") and isinstance(ports, list) and ports:
        try:
            merged["port"] = int(ports[0])
        except (TypeError, ValueError):
            pass
    health = contract.get("health", {})
    if isinstance(health, dict) and health.get("path"):
        merged["has_health_probe"] = True
        merged["health_path"] = health.get("path")
    configuration = contract.get("configuration", {})
    if isinstance(configuration, dict):
        merged["has_secret_boundary"] = merged.get("has_secret_boundary") or bool(configuration.get("secret_boundary_required"))
        merged["has_container_runtime"] = merged.get("has_container_runtime") or bool(contract.get("image"))
    resources = contract.get("resources", {})
    if isinstance(resources, dict):
        merged["has_resource_policy"] = merged.get("has_resource_policy") or bool(resources.get("policy_defined"))
    storage = contract.get("storage", {})
    if isinstance(storage, dict):
        merged["stateful_requested"] = merged.get("stateful_requested") or bool(storage.get("stateful"))
        merged["has_storage_policy"] = merged.get("has_storage_policy") or bool(storage.get("policy_defined"))
    return merged, relative_artifact(repo_root, contract_path)


def capability(name: str, status: str, evidence_refs: list[str], reason: str) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "evidence_refs": evidence_refs,
        "reason": reason,
    }


def build_compatibility_assessment(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    target: str = "auto",
    requirements: list[str] | None = None,
) -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    documents = read_source_documents(repo_root, resolved_work_dir, requirements)
    loaded_documents = [item for item in documents if item["status"] == "loaded"]
    text = "\n\n".join(item["content"] for item in loaded_documents)
    signals = detect_signals(text)
    signals, deployment_contract_path = apply_deployment_contract_signals(repo_root, resolved_work_dir, signals)
    resolved_target = infer_target(text, target)
    evidence_refs = [item["path"] for item in loaded_documents]
    if deployment_contract_path:
        evidence_refs.append(deployment_contract_path)
    requested = signals["requested"] or resolved_target != "unspecified"
    capabilities = [
        capability(
            "kubernetes_target",
            "ready" if requested else "missing",
            evidence_refs,
            "要件に Kubernetes/k3s の指定があります。" if requested else "要件から Kubernetes/k3s 指定を検出できません。",
        ),
        capability(
            "container_image",
            "ready" if signals["image"] else "missing",
            evidence_refs,
            "container image が明示されています。" if signals["image"] else "manifest 生成には container image の確定が必要です。",
        ),
        capability(
            "service_port",
            "ready" if signals["port"] else "missing",
            evidence_refs,
            "service/container port が明示されています。" if signals["port"] else "Service と probe の既定 port が未確定です。",
        ),
        capability(
            "health_probe",
            "ready" if signals["has_health_probe"] else "missing",
            evidence_refs,
            "health/readiness/liveness probe の記載があります。" if signals["has_health_probe"] else "Probe は scaffold 上の placeholder として扱います。",
        ),
        capability(
            "resource_policy",
            "ready" if signals["has_resource_policy"] else "missing",
            evidence_refs,
            "resources requests/limits の記載があります。" if signals["has_resource_policy"] else "requests/limits は運用前に確認が必要です。",
        ),
        capability(
            "secret_config_boundary",
            "ready" if signals["has_secret_boundary"] else "missing",
            evidence_refs,
            "Secret/ConfigMap/env の境界が示されています。" if signals["has_secret_boundary"] else "秘密情報を manifest に直書きしない方針確認が必要です。",
        ),
        capability(
            "exposure_policy",
            "ready" if signals["has_exposure_policy"] else "missing",
            evidence_refs,
            "Service/Ingress 等の公開方針が示されています。" if signals["has_exposure_policy"] else "公開方式は ClusterIP scaffold に制約します。",
        ),
    ]
    if signals["stateful_requested"]:
        capabilities.append(
            capability(
                "storage_policy",
                "ready" if signals["has_storage_policy"] else "missing",
                evidence_refs,
                "永続化方針が示されています。" if signals["has_storage_policy"] else "Stateful 要件がありますが storage 方針が未確定です。",
            )
        )
    missing = [item["name"] for item in capabilities if item["status"] == "missing"]
    status = "not-requested" if not requested else "compatible" if not missing else "compatible-with-gaps"
    assessment = {
        "schema_version": SCHEMA_VERSION,
        "schema": KUBERNETES_COMPATIBILITY_ASSESSMENT_SCHEMA,
        "artifact_type": ARTIFACT_TYPE_ASSESSMENT,
        "status": status,
        "work_id": work_id,
        "target": resolved_target,
        "requested": requested,
        "generated_at": utc_now_iso(),
        "source_documents": [{"path": item["path"], "status": item["status"]} for item in documents],
        "deployment_contract_path": deployment_contract_path,
        "detected": signals,
        "capabilities": capabilities,
        "missing_capabilities": missing,
        "rules": {
            "assessment_is_non_mutating": True,
            "do_not_apply_to_cluster": True,
            "secret_values_must_not_be_generated": True,
        },
    }
    output_path = compatibility_path(resolved_work_dir)
    assessment["artifacts"] = {"assessment_json": relative_artifact(repo_root, output_path)}
    write_json(output_path, assessment)
    manifest = register_context(
        repo_root,
        resolved_work_dir,
        work_id=work_id,
        context_type=ARTIFACT_TYPE_ASSESSMENT,
        path=output_path,
        required=False,
        generated_by="kubernetes-runtime",
        owner="iac",
        schema=KUBERNETES_COMPATIBILITY_ASSESSMENT_SCHEMA,
        status=status,
    )
    assessment["manifest_path"] = relative_artifact(repo_root, manifest_path_for_work_dir(resolved_work_dir))
    assessment["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(output_path, assessment)
    return assessment


def gap_item(gap_id: str, severity: str, category: str, title: str, impact: str, recommendation: str) -> dict[str, Any]:
    return {
        "gap_id": gap_id,
        "severity": severity,
        "category": category,
        "title": title,
        "impact": impact,
        "recommendation": recommendation,
    }


def gaps_from_assessment(assessment: dict[str, Any]) -> list[dict[str, Any]]:
    detected = assessment.get("detected", {})
    gaps: list[dict[str, Any]] = []
    if not assessment.get("requested", False):
        gaps.append(
            gap_item(
                "k8s-target-not-requested",
                "info",
                "requirements",
                "Kubernetes/k3s 指定を検出できません",
                "manifest 生成はできますが、要件根拠は弱い状態です。",
                "要件定義へ k8s/k3s の対象、目的、運用環境を明記してください。",
            )
        )
    if not detected.get("image"):
        gaps.append(
            gap_item(
                "container-image-missing",
                "critical",
                "runtime",
                "container image が未確定です",
                "Deployment は placeholder image で constrained scaffold になります。",
                "build 済み image 名、tag、registry、pull policy を確定してください。",
            )
        )
    if not detected.get("port"):
        gaps.append(
            gap_item(
                "service-port-missing",
                "high",
                "network",
                "service port が未確定です",
                "Service と probe は既定 port 8080 の scaffold になります。",
                "containerPort と Service port を要件または設計へ追記してください。",
            )
        )
    if not detected.get("has_health_probe"):
        gaps.append(
            gap_item(
                "health-probe-missing",
                "medium",
                "operations",
                "health/readiness/liveness probe が未確定です",
                "起動成功と業務的な利用可能状態を分けて検証しづらくなります。",
                "readinessProbe と livenessProbe の path、timeout、初期待機を決めてください。",
            )
        )
    if not detected.get("has_resource_policy"):
        gaps.append(
            gap_item(
                "resource-policy-missing",
                "medium",
                "operations",
                "resources requests/limits が未確定です",
                "k3s 等の小さな環境で予期せぬ eviction や過負荷が起きやすくなります。",
                "CPU/Memory の requests/limits を最小運用値として定義してください。",
            )
        )
    if not detected.get("has_secret_boundary"):
        gaps.append(
            gap_item(
                "secret-config-boundary-missing",
                "medium",
                "security",
                "Secret/ConfigMap の境界が未確定です",
                "秘密値を manifest に直書きする事故を防ぎにくくなります。",
                "Secret 名、ConfigMap 名、env の責務境界だけを manifest に残し、値は外部注入にしてください。",
            )
        )
    if detected.get("stateful_requested") and not detected.get("has_storage_policy"):
        gaps.append(
            gap_item(
                "storage-policy-missing",
                "high",
                "storage",
                "永続化方針が未確定です",
                "Stateful workload の再起動、バックアップ、復旧条件を評価できません。",
                "PVC、StorageClass、backup/restore 条件を確定してください。",
            )
        )
    return gaps


def render_gap_report(report: dict[str, Any]) -> str:
    lines = [
        "# Kubernetes / k3s Gap Report",
        "",
        f"- Work ID: `{report.get('work_id', '')}`",
        f"- Status: `{report.get('status', '')}`",
        f"- Target: `{report.get('target', '')}`",
        "",
        "## Gaps",
        "",
    ]
    for item in report.get("gaps", []):
        lines.append(f"- `{item['severity']}` `{item['gap_id']}`: {item['title']}")
        lines.append(f"  - 影響: {item['impact']}")
        lines.append(f"  - 対応: {item['recommendation']}")
    if not report.get("gaps"):
        lines.append("- 主要 gap は検出されていません。")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- `{item}`" for item in report.get("next_actions", []))
    return "\n".join(lines)


def build_gap_report(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    target: str = "auto",
    requirements: list[str] | None = None,
) -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    assessment = read_json(compatibility_path(resolved_work_dir), default={})
    if not isinstance(assessment, dict) or not assessment:
        assessment = build_compatibility_assessment(
            repo_root,
            work_id=work_id,
            work_dir=str(resolved_work_dir),
            target=target,
            requirements=requirements,
        )
    gaps = gaps_from_assessment(assessment)
    critical_or_high = [item for item in gaps if item["severity"] in {"critical", "high"}]
    status = "ready-for-generation" if not critical_or_high else "generation-constrained"
    report = {
        "schema_version": SCHEMA_VERSION,
        "schema": KUBERNETES_GAP_REPORT_SCHEMA,
        "artifact_type": ARTIFACT_TYPE_GAP_REPORT,
        "status": status,
        "work_id": work_id,
        "target": assessment.get("target", "unspecified"),
        "generated_at": utc_now_iso(),
        "assessment_path": relative_artifact(repo_root, compatibility_path(resolved_work_dir)),
        "gaps": gaps,
        "rules": {
            "do_not_delete_constrained_candidate": True,
            "manifest_generation_uses_placeholders_for_missing_values": True,
        },
        "next_actions": [
            f"aiwfctl iac kubernetes generate --work-id {work_id}",
            f"aiwfctl iac kubernetes dry-run --work-id {work_id}",
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
        context_type=ARTIFACT_TYPE_GAP_REPORT,
        path=json_path,
        required=False,
        generated_by="kubernetes-runtime",
        owner="iac",
        schema=KUBERNETES_GAP_REPORT_SCHEMA,
        status=status,
    )
    report["manifest_path"] = relative_artifact(repo_root, manifest_path_for_work_dir(resolved_work_dir))
    report["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(json_path, report)
    return report


def manifest_values(work_id: str, assessment: dict[str, Any]) -> dict[str, Any]:
    detected = assessment.get("detected", {})
    app_name = detected.get("app_name") or slugify(work_id)
    return {
        "app_name": app_name,
        "namespace": detected.get("namespace") or DEFAULT_NAMESPACE,
        "image": detected.get("image") or DEFAULT_IMAGE,
        "port": detected.get("port") or DEFAULT_PORT,
        "replicas": DEFAULT_REPLICAS,
        "health_path": DEFAULT_HEALTH_PATH,
        "cpu_request": DEFAULT_CPU_REQUEST,
        "memory_request": DEFAULT_MEMORY_REQUEST,
        "cpu_limit": DEFAULT_CPU_LIMIT,
        "memory_limit": DEFAULT_MEMORY_LIMIT,
        "service_type": DEFAULT_SERVICE_TYPE,
    }


def normalize_spec_delta(raw: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    normalized: dict[str, Any] = {}
    ignored: list[str] = []
    for key, value in raw.items():
        if key not in ALLOWED_SPEC_DELTA_KEYS:
            ignored.append(key)
            continue
        if key in {"port", "replicas"}:
            try:
                normalized[key] = int(value)
            except (TypeError, ValueError):
                ignored.append(key)
            continue
        normalized[key] = str(value).strip()
    return normalized, sorted(ignored)


def load_spec_delta(repo_root: Path, work_dir: Path, spec_delta: str = "") -> tuple[dict[str, Any], list[str], str]:
    if not spec_delta:
        return {}, [], ""
    path = resolve_input_path(repo_root, work_dir, spec_delta)
    raw = read_json(path, default={})
    if not isinstance(raw, dict):
        return {}, ["<invalid-spec-delta>"], relative_artifact(repo_root, path)
    normalized, ignored = normalize_spec_delta(raw)
    return normalized, ignored, relative_artifact(repo_root, path)


def merged_manifest_values(
    repo_root: Path,
    work_dir: Path,
    work_id: str,
    assessment: dict[str, Any],
    spec_delta: str = "",
) -> tuple[dict[str, Any], list[str], str]:
    values = manifest_values(work_id, assessment)
    delta, ignored, delta_path = load_spec_delta(repo_root, work_dir, spec_delta)
    values.update(delta)
    return values, ignored, delta_path


def template_tokens(values: dict[str, Any]) -> dict[str, str]:
    return {
        "{{APP_NAME}}": str(values["app_name"]),
        "{{NAMESPACE}}": str(values["namespace"]),
        "{{IMAGE}}": str(values["image"]),
        "{{PORT}}": str(values["port"]),
        "{{REPLICAS}}": str(values["replicas"]),
        "{{HEALTH_PATH}}": str(values["health_path"]),
        "{{CPU_REQUEST}}": str(values["cpu_request"]),
        "{{MEMORY_REQUEST}}": str(values["memory_request"]),
        "{{CPU_LIMIT}}": str(values["cpu_limit"]),
        "{{MEMORY_LIMIT}}": str(values["memory_limit"]),
        "{{SERVICE_TYPE}}": str(values["service_type"]),
    }


def render_template_text(template_text: str, values: dict[str, Any]) -> str:
    rendered = template_text
    for token, value in template_tokens(values).items():
        rendered = rendered.replace(token, value)
    return rendered


def template_manifest_source_dir(repo_root: Path) -> Path:
    repo_template = repo_root / TEMPLATE_MANIFEST_DIR
    if repo_template.exists():
        return repo_template
    return Path(__file__).resolve().parents[2] / TEMPLATE_MANIFEST_DIR


def write_manifests(repo_root: Path, manifest_dir: Path, values: dict[str, Any]) -> list[Path]:
    source_dir = template_manifest_source_dir(repo_root)
    if not source_dir.exists():
        raise FileNotFoundError(f"Kubernetes template manifest directory was not found: {source_dir}")
    written: list[Path] = []
    for template_path in sorted(source_dir.glob("*.yaml"), key=lambda item: item.name):
        path = manifest_dir / template_path.name
        write_markdown(path, render_template_text(template_path.read_text(encoding="utf-8"), values))
        written.append(path)
    return written


def build_manifest_generation(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    spec_delta: str = "",
    force: bool = False,
) -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    assessment = read_json(compatibility_path(resolved_work_dir), default={})
    if not isinstance(assessment, dict) or not assessment:
        assessment = build_compatibility_assessment(repo_root, work_id=work_id, work_dir=str(resolved_work_dir))
    gap_report = read_json(gap_report_json_path(resolved_work_dir), default={})
    if not isinstance(gap_report, dict) or not gap_report:
        gap_report = build_gap_report(repo_root, work_id=work_id, work_dir=str(resolved_work_dir))
    manifest_dir = kubernetes_manifest_dir(resolved_work_dir)
    if manifest_dir.exists() and any(manifest_dir.iterdir()) and not force:
        status = "existing"
        written_files = sorted([path for path in manifest_dir.iterdir() if path.is_file()])
    else:
        manifest_dir.mkdir(parents=True, exist_ok=True)
        values, ignored_delta_keys, delta_path = merged_manifest_values(
            repo_root,
            resolved_work_dir,
            work_id,
            assessment,
            spec_delta,
        )
        written_files = write_manifests(repo_root, manifest_dir, values)
        status = "generated-with-gaps" if gap_report.get("status") == "generation-constrained" else "generated"
    if status == "existing":
        values, ignored_delta_keys, delta_path = merged_manifest_values(
            repo_root,
            resolved_work_dir,
            work_id,
            assessment,
            spec_delta,
        )
    generation = {
        "schema_version": SCHEMA_VERSION,
        "schema": KUBERNETES_MANIFEST_GENERATION_SCHEMA,
        "artifact_type": ARTIFACT_TYPE_MANIFEST_GENERATION,
        "status": status,
        "work_id": work_id,
        "target": assessment.get("target", "unspecified"),
        "generated_at": utc_now_iso(),
        "template": TEMPLATE_NAME,
        "template_path": TEMPLATE_PATH.as_posix(),
        "spec_delta_path": delta_path,
        "allowed_spec_delta_keys": sorted(ALLOWED_SPEC_DELTA_KEYS),
        "ignored_spec_delta_keys": ignored_delta_keys,
        "applied_values": values,
        "manifest_dir": relative_artifact(repo_root, manifest_dir),
        "manifest_files": [relative_artifact(repo_root, path) for path in written_files],
        "assessment_path": relative_artifact(repo_root, compatibility_path(resolved_work_dir)),
        "gap_report_path": relative_artifact(repo_root, gap_report_json_path(resolved_work_dir)),
        "rules": {
            "generated_manifests_are_scaffold": True,
            "do_not_commit_secret_values": True,
            "apply_to_cluster_requires_human_check": True,
            "only_allowed_spec_delta_keys_are_applied": True,
        },
        "next_actions": [
            f"aiwfctl iac kubernetes dry-run --work-id {work_id}",
            f"aiwfctl iac kubernetes e2e-plan --work-id {work_id}",
        ],
    }
    output_path = generation_path(resolved_work_dir)
    generation["artifacts"] = {"generation_json": relative_artifact(repo_root, output_path)}
    write_json(output_path, generation)
    manifest = register_context(
        repo_root,
        resolved_work_dir,
        work_id=work_id,
        context_type=ARTIFACT_TYPE_MANIFEST_GENERATION,
        path=output_path,
        required=False,
        generated_by="kubernetes-runtime",
        owner="iac",
        schema=KUBERNETES_MANIFEST_GENERATION_SCHEMA,
        status=status,
    )
    generation["manifest_path"] = relative_artifact(repo_root, manifest_path_for_work_dir(resolved_work_dir))
    generation["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(output_path, generation)
    return generation


def kubectl_command(manifest_dir: Path, mode: str) -> list[str]:
    return ["kubectl", "apply", f"--dry-run={mode}", "-k", str(manifest_dir)]


def render_dry_run_evidence(evidence: dict[str, Any]) -> str:
    lines = [
        "# Kubernetes / k3s Dry-run Evidence",
        "",
        f"- Work ID: `{evidence.get('work_id', '')}`",
        f"- Status: `{evidence.get('status', '')}`",
        f"- Mode: `{evidence.get('mode', '')}`",
        f"- Command: `{' '.join(evidence.get('command', []))}`",
        "",
        "## Result",
        "",
        f"- kubectl available: `{evidence.get('kubectl_available', False)}`",
        f"- executed: `{evidence.get('executed', False)}`",
        f"- exit_code: `{evidence.get('exit_code', '')}`",
    ]
    if evidence.get("stdout"):
        lines.extend(["", "## Stdout", "", "```text", str(evidence["stdout"]), "```"])
    if evidence.get("stderr"):
        lines.extend(["", "## Stderr", "", "```text", str(evidence["stderr"]), "```"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- `{item}`" for item in evidence.get("next_actions", []))
    return "\n".join(lines)


def build_dry_run_evidence(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    mode: str = "client",
    execute: bool = False,
    human_check: str = "pending",
) -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    generation = read_json(generation_path(resolved_work_dir), default={})
    if not isinstance(generation, dict) or not generation:
        generation = build_manifest_generation(repo_root, work_id=work_id, work_dir=str(resolved_work_dir))
    manifest_dir = kubernetes_manifest_dir(resolved_work_dir)
    command = kubectl_command(manifest_dir, mode)
    kubectl_path = shutil.which("kubectl")
    status = "dry-run"
    exit_code: int | None = None
    stdout = ""
    stderr = ""
    if execute and human_check != "approved":
        status = "human-check-required"
    elif execute and not kubectl_path:
        status = "blocked"
        stderr = "kubectl was not found on PATH."
    elif execute:
        completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, timeout=KUBECTL_TIMEOUT_SECONDS, check=False)
        exit_code = completed.returncode
        stdout = (completed.stdout or "").strip()
        stderr = (completed.stderr or "").strip()
        status = "pass" if completed.returncode == 0 else "fail"
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "schema": KUBERNETES_DRY_RUN_EVIDENCE_SCHEMA,
        "artifact_type": ARTIFACT_TYPE_DRY_RUN,
        "status": status,
        "work_id": work_id,
        "mode": mode,
        "generated_at": utc_now_iso(),
        "manifest_dir": relative_artifact(repo_root, manifest_dir),
        "generation_path": relative_artifact(repo_root, generation_path(resolved_work_dir)),
        "command": command,
        "kubectl_path": kubectl_path or "",
        "kubectl_available": bool(kubectl_path),
        "executed": bool(execute and human_check == "approved" and kubectl_path),
        "human_check": human_check,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "rules": {
            "dry_run_is_non_mutating": True,
            "execute_requires_human_check": True,
            "server_dry_run_may_contact_cluster": mode == "server",
        },
        "next_actions": [
            f"aiwfctl iac kubernetes e2e-plan --work-id {work_id}",
            f"aiwfctl e2e run --work-id {work_id} --test-kind integration --dry-run",
            f"aiwfctl iac kubernetes evidence --work-id {work_id}",
        ],
    }
    json_path = dry_run_json_path(resolved_work_dir)
    markdown_path = dry_run_markdown_path(resolved_work_dir)
    evidence["artifacts"] = {
        "dry_run_json": relative_artifact(repo_root, json_path),
        "dry_run_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, evidence)
    write_markdown(markdown_path, render_dry_run_evidence(evidence))
    manifest = register_context(
        repo_root,
        resolved_work_dir,
        work_id=work_id,
        context_type=ARTIFACT_TYPE_DRY_RUN,
        path=json_path,
        required=False,
        generated_by="kubernetes-runtime",
        owner="iac",
        schema=KUBERNETES_DRY_RUN_EVIDENCE_SCHEMA,
        status=status,
    )
    evidence["manifest_path"] = relative_artifact(repo_root, manifest_path_for_work_dir(resolved_work_dir))
    evidence["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(json_path, evidence)
    return evidence


def build_kubernetes_e2e_plan(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    command: list[str] | None = None,
) -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    manifest_dir = kubernetes_manifest_dir(resolved_work_dir)
    default_command = " ".join(kubectl_command(manifest_dir, "client"))
    commands = [default_command, *normalize_items(command)]
    return e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        work_dir=str(resolved_work_dir),
        test_kind="integration",
        objective="Kubernetes/k3s manifest の dry-run と後続 E2E の成立条件を確認する。",
        scenarios=[
            "要件から Kubernetes/k3s 互換性を評価し、gap を確認する。",
            "生成済み manifest scaffold を kubectl dry-run で検証する。",
            "必要な Stub と実行コマンドを明示し、実行後 evidence と照合する。",
        ],
        targets=[relative_artifact(repo_root, manifest_dir)],
        expectations=[
            "manifest に秘密値が直書きされていない。",
            "kubectl dry-run が pass または human review 対象として記録されている。",
            "失敗時は aiwfctl e2e loop で問題発見、修正指示、再テストへ進める。",
        ],
        required_stubs=[],
        commands=commands,
    )


def render_kubernetes_evidence(evidence: dict[str, Any]) -> str:
    lines = [
        "# Kubernetes / k3s Evidence",
        "",
        f"- Work ID: `{evidence.get('work_id', '')}`",
        f"- Status: `{evidence.get('status', '')}`",
        "",
        "## Artifacts",
        "",
    ]
    for key, value in evidence.get("collected_artifacts", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Judgment", ""])
    lines.extend(f"- {item}" for item in evidence.get("judgment", []))
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- `{item}`" for item in evidence.get("next_actions", []))
    return "\n".join(lines)


def build_kubernetes_evidence(repo_root: Path, *, work_id: str, work_dir: str = "") -> dict[str, Any]:
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    artifacts = {
        "assessment": compatibility_path(resolved_work_dir),
        "gap_report": gap_report_json_path(resolved_work_dir),
        "manifest_generation": generation_path(resolved_work_dir),
        "dry_run": dry_run_json_path(resolved_work_dir),
        "integration_plan": e2e_runtime.plan_json_path(resolved_work_dir, "integration"),
        "integration_verification": e2e_runtime.evidence_json_path(resolved_work_dir, "integration", "verification"),
    }
    collected = {key: relative_artifact(repo_root, path) for key, path in artifacts.items() if path.exists()}
    missing = [key for key, path in artifacts.items() if not path.exists()]
    dry_run = read_json(dry_run_json_path(resolved_work_dir), default={})
    dry_run_status = dry_run.get("status", "missing") if isinstance(dry_run, dict) else "missing"
    status = "ready-for-human-review" if not missing and dry_run_status in {"pass", "dry-run"} else "incomplete"
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "schema": KUBERNETES_EVIDENCE_SCHEMA,
        "artifact_type": ARTIFACT_TYPE_EVIDENCE,
        "status": status,
        "work_id": work_id,
        "generated_at": utc_now_iso(),
        "collected_artifacts": collected,
        "missing_artifacts": missing,
        "dry_run_status": dry_run_status,
        "judgment": [
            "Kubernetes/k3s 指定時は compatibility assessment と gap report を先に確認する。",
            "manifest は scaffold として扱い、秘密値や本番固有値は含めない。",
            "dry-run と integration/E2E evidence を Human Check の判断材料にする。",
        ],
        "next_actions": [
            f"aiwfctl iac kubernetes dry-run --work-id {work_id} --execute --human-check approved",
            f"aiwfctl e2e run --work-id {work_id} --test-kind integration --human-check approved",
            f"aiwfctl e2e loop --work-id {work_id} --test-kind integration",
        ],
    }
    json_path = evidence_json_path(resolved_work_dir)
    markdown_path = evidence_markdown_path(resolved_work_dir)
    evidence["artifacts"] = {
        "evidence_json": relative_artifact(repo_root, json_path),
        "evidence_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, evidence)
    write_markdown(markdown_path, render_kubernetes_evidence(evidence))
    manifest = register_context(
        repo_root,
        resolved_work_dir,
        work_id=work_id,
        context_type=ARTIFACT_TYPE_EVIDENCE,
        path=json_path,
        required=False,
        generated_by="kubernetes-runtime",
        owner="iac",
        schema=KUBERNETES_EVIDENCE_SCHEMA,
        status=status,
    )
    evidence["manifest_path"] = relative_artifact(repo_root, manifest_path_for_work_dir(resolved_work_dir))
    evidence["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(json_path, evidence)
    return evidence


def run(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    command = getattr(args, "kubernetes_command", "")
    common = {
        "work_id": getattr(args, "work_id", ""),
        "work_dir": getattr(args, "work_dir", ""),
    }
    if command == "assess":
        return build_compatibility_assessment(
            repo_root,
            **common,
            target=getattr(args, "target", "auto"),
            requirements=getattr(args, "requirements", []),
        )
    if command == "gap-report":
        return build_gap_report(
            repo_root,
            **common,
            target=getattr(args, "target", "auto"),
            requirements=getattr(args, "requirements", []),
        )
    if command == "generate":
        return build_manifest_generation(
            repo_root,
            **common,
            spec_delta=getattr(args, "spec_delta", ""),
            force=getattr(args, "force", False),
        )
    if command == "dry-run":
        return build_dry_run_evidence(
            repo_root,
            **common,
            mode=getattr(args, "mode", "client"),
            execute=getattr(args, "execute", False),
            human_check=getattr(args, "human_check", "pending"),
        )
    if command == "e2e-plan":
        return build_kubernetes_e2e_plan(repo_root, **common, command=getattr(args, "run_command", []))
    if command == "evidence":
        return build_kubernetes_evidence(repo_root, **common)
    raise ValueError(f"Unknown Kubernetes IaC command: {command}")


def format_result(result: dict[str, Any]) -> str:
    lines = [
        "Kubernetes / k3s IaC",
        "",
        f"Type   : {result.get('artifact_type', '')}",
        f"Status : {result.get('status', '')}",
        f"Work ID: {result.get('work_id', '')}",
    ]
    artifacts = result.get("artifacts", {})
    if artifacts:
        lines.extend(["", "Artifacts"])
        lines.extend(f"  - {key}: {value}" for key, value in artifacts.items())
    if result.get("manifest_files"):
        lines.extend(["", "Manifest Files"])
        lines.extend(f"  - {item}" for item in result["manifest_files"])
    if result.get("gaps"):
        lines.extend(["", "Gaps"])
        for item in result["gaps"]:
            lines.append(f"  - {item.get('severity', '')}: {item.get('gap_id', '')} - {item.get('title', '')}")
    next_actions = result.get("next_actions", [])
    if next_actions:
        lines.extend(["", "Next Actions"])
        lines.extend(f"  - {item}" for item in next_actions)
    return "\n".join(lines).rstrip() + "\n"
