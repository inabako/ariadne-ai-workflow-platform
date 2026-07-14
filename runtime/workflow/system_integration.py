from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402


SCHEMA_VERSION = "1.0"
ARTIFACT_TYPE = "system-integration-context"
EMULATOR_CONTEXT_ARTIFACT_TYPE = "emulator-setup-context"
EMULATOR_HEALTH_ARTIFACT_TYPE = "emulator-health-context"
INTEGRATION_TEST_PLAN_ARTIFACT_TYPE = "integration-test-plan-context"
INTEGRATION_FINALIZATION_ARTIFACT_TYPE = "integration-finalization-context"
DEFAULT_CONTEXT_SCHEMA = ".github/schemas/system-integration-context.schema.json"
DEFAULT_EMULATOR_SCHEMA = ".github/schemas/emulator-setup-context.schema.json"
DEFAULT_EMULATOR_HEALTH_SCHEMA = ".github/schemas/emulator-health-context.schema.json"
DEFAULT_TEST_PLAN_SCHEMA = ".github/schemas/integration-test-plan-context.schema.json"
DEFAULT_FINALIZATION_SCHEMA = ".github/schemas/integration-finalization-context.schema.json"

AWS_EMULATOR_SERVICES = {
    "s3": "LocalStack S3",
    "dynamodb": "LocalStack DynamoDB",
    "sqs": "LocalStack SQS",
    "sns": "LocalStack SNS",
    "lambda": "LocalStack Lambda",
    "kinesis": "LocalStack Kinesis",
    "secretsmanager": "LocalStack Secrets Manager",
    "cloudwatch": "LocalStack CloudWatch",
}
GCP_EMULATOR_SERVICES = {
    "pubsub": "Google Cloud Pub/Sub emulator",
    "firestore": "Google Cloud Firestore emulator",
    "bigquery": "BigQuery local test double / sandbox project",
    "storage": "fake-gcs-server / storage test double",
    "secretmanager": "Secret Manager fake client",
}


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def resolve_work_dir(repo_root: Path, work_id: str, work_dir: str = "") -> Path:
    if work_dir:
        return resolve_repo_path(repo_root, work_dir)
    if not work_id:
        raise ValueError("--work-id is required when --work-dir is not specified.")
    return repo_root / "work" / work_id


def default_target_repo(work_dir: Path) -> Path:
    return work_dir / "source" / "repository"


def load_context(work_dir: Path, name: str) -> dict[str, Any]:
    data = read_json(work_dir / "context" / name, default={})
    return data if isinstance(data, dict) else {}


def load_contexts(work_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        "sdk_analysis": load_context(work_dir, "sdk-analysis-context.json"),
        "sdk_external_discovery": load_context(work_dir, "sdk-external-discovery.json"),
        "environment_selection": load_context(work_dir, "environment-selection.json"),
    }


def limited_files(root: Path, *, max_files: int = 300) -> list[Path]:
    if not root.exists() or not root.is_dir():
        return []
    excluded = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if len(files) >= max_files:
            break
        if not path.is_file():
            continue
        if any(part in excluded for part in path.parts):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix().lower())


def detect_project_structure(target_repo: Path) -> dict[str, Any]:
    files = limited_files(target_repo)
    rels = {path.relative_to(target_repo).as_posix().lower() for path in files} if target_repo.exists() else set()
    dirs = rels
    return {
        "path": str(target_repo),
        "exists": target_repo.exists(),
        "file_count_sampled": len(files),
        "has_src": any(value.startswith("src/") for value in dirs),
        "has_tests": any(value.startswith(("tests/", "test/", "src/tests/")) or "/tests/" in value for value in dirs),
        "has_docs_evidence": any("docs/evidence" in value for value in dirs),
        "has_docker_compose": any(value.endswith(("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")) for value in rels),
        "has_env_example": any(value.endswith((".env.example", ".env.sample", "env.example")) for value in rels),
        "package_files": sorted(
            value
            for value in rels
            if value.endswith(("pyproject.toml", "package.json", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts"))
        ),
    }


def path_name_hits(target_repo: Path, keywords: list[str]) -> list[str]:
    hits: list[str] = []
    for path in limited_files(target_repo):
        rel = path.relative_to(target_repo).as_posix()
        lowered = rel.lower()
        if any(keyword in lowered for keyword in keywords):
            hits.append(rel)
    return hits[:20]


def extract_cloud(contexts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    for context in [contexts.get("sdk_analysis", {}), contexts.get("sdk_external_discovery", {})]:
        cloud = context.get("cloud")
        if isinstance(cloud, dict) and cloud.get("provider") not in {"", None, "unknown"}:
            return cloud
    return {}


def extract_payment(contexts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    for context in [contexts.get("sdk_analysis", {}), contexts.get("sdk_external_discovery", {})]:
        payment = context.get("payment")
        if isinstance(payment, dict) and payment.get("vendor") not in {"", None, "unknown"}:
            return payment
    return {}


def emulator_candidates(cloud: dict[str, Any], payment: dict[str, Any], *, with_emulator: bool) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    providers = [str(item).lower() for item in cloud.get("providers", [])]
    provider = str(cloud.get("provider", "")).lower()
    if provider in {"aws", "multiple"} or "aws" in providers:
        services = [str(item).lower() for item in cloud.get("services", [])]
        selected = services or ["unknown"]
        candidates.append(
            {
                "provider": "aws",
                "emulator": "LocalStack",
                "template_path": "templates/boilerplates/integration/cloud-emulators/localstack",
                "recommended_work_path": "work/<work-id>/test-environment/emulator/localstack",
                "activation": "manual-or-parent-workflow",
                "required": with_emulator,
                "services": selected,
                "verification_scope": classify_services(selected, AWS_EMULATOR_SERVICES, with_emulator),
                "notes": [
                    "Do not use production AWS credentials for emulator verification.",
                    "Switch endpoint / region / credential through configuration or adapter.",
                ],
            }
        )
    if provider in {"gcp", "multiple"} or "gcp" in providers:
        services = [str(item).lower() for item in cloud.get("services", [])]
        selected = services or ["unknown"]
        candidates.append(
            {
                "provider": "gcp",
                "emulator": "Google Cloud emulators / service-specific test doubles",
                "template_path": "templates/boilerplates/integration/cloud-emulators/gcp-emulators",
                "recommended_work_path": "work/<work-id>/test-environment/emulator/gcp-emulators",
                "activation": "manual-or-parent-workflow",
                "required": with_emulator,
                "services": selected,
                "verification_scope": classify_services(selected, GCP_EMULATOR_SERVICES, with_emulator),
                "notes": [
                    "Do not use production GCP credentials for emulator verification.",
                    "Project ID, endpoint, and credentials must be injectable through configuration or adapter.",
                ],
            }
        )
    if "stripe" in [str(item).lower() for item in payment.get("vendors", [])]:
        services = [str(item).lower() for item in payment.get("services", [])] or ["webhooks"]
        candidates.append(
            {
                "provider": "stripe",
                "emulator": "Stripe CLI / test mode",
                "template_path": "templates/boilerplates/integration/cloud-emulators/stripe-cli",
                "recommended_work_path": "work/<work-id>/test-environment/emulator/stripe-cli",
                "activation": "manual-or-parent-workflow",
                "required": with_emulator,
                "services": services,
                "verification_scope": [
                    {
                        "service": service,
                        "classification": "emulator_verified" if with_emulator else "real_cloud_verification_required",
                        "tool": "Stripe CLI / test mode",
                        "reason": "Stripe test mode can verify integration behavior, but live billing rules still need Human Check.",
                    }
                    for service in services
                ],
                "notes": [
                    "Do not use live secret keys for automated verification.",
                    "Webhook signing secret and idempotency behavior must be explicitly verified.",
                ],
            }
        )
    return candidates


def classify_services(services: list[str], mapping: dict[str, str], with_emulator: bool) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for service in services:
        normalized = service.lower()
        tool = mapping.get(normalized, "")
        if not with_emulator:
            classification = "real_cloud_verification_required"
            reason = "Emulator verification was not requested for this run."
        elif tool:
            classification = "emulator_verified"
            reason = "A known emulator or local test double candidate exists."
        elif normalized in {"unknown", "emulator", "localstack"}:
            classification = "unsupported_by_emulator"
            reason = "The concrete cloud service could not be determined."
        else:
            classification = "real_cloud_verification_required"
            reason = "No reliable emulator mapping is registered for this service."
        result.append({"service": service, "classification": classification, "tool": tool, "reason": reason})
    return result


def integration_points(target_repo: Path, cloud: dict[str, Any], payment: dict[str, Any]) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    adapter_hits = path_name_hits(target_repo, ["adapter", "gateway", "client"])
    port_hits = path_name_hits(target_repo, ["port", "interface", "protocol"])
    config_hits = path_name_hits(target_repo, ["config", "settings", ".env", "application."])
    test_hits = path_name_hits(target_repo, ["test", "spec", "fixture"])
    if adapter_hits or cloud or payment:
        points.append({"type": "adapter-boundary", "evidence": adapter_hits, "required": True})
    if port_hits or cloud or payment:
        points.append({"type": "port-interface", "evidence": port_hits, "required": True})
    points.append({"type": "configuration-injection", "evidence": config_hits, "required": bool(cloud or payment)})
    points.append({"type": "test-double-or-emulator-switch", "evidence": test_hits, "required": bool(cloud or payment)})
    return points


def static_consistency_findings(structure: dict[str, Any], target_repo: Path, cloud: dict[str, Any], payment: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    findings.append(
        {
            "check": "target-repository",
            "status": "pass" if structure.get("exists") else "human-check-required",
            "detail": "target repository exists" if structure.get("exists") else "target repository was not found",
        }
    )
    findings.append(
        {
            "check": "tests-present",
            "status": "pass" if structure.get("has_tests") else "warning",
            "detail": "test directory detected" if structure.get("has_tests") else "test directory was not detected in sampled files",
        }
    )
    findings.append(
        {
            "check": "configuration-boundary",
            "status": "pass" if (structure.get("has_env_example") or not (cloud or payment)) else "warning",
            "detail": "environment sample detected" if structure.get("has_env_example") else "external service settings must be injected via existing configuration",
        }
    )
    findings.append(
        {
            "check": "evidence-layout",
            "status": "pass" if structure.get("has_docs_evidence") else "warning",
            "detail": "docs/evidence detected" if structure.get("has_docs_evidence") else "integration evidence location should be prepared",
        }
    )
    return findings


def human_checks(
    structure: dict[str, Any],
    cloud: dict[str, Any],
    payment: dict[str, Any],
    candidates: list[dict[str, Any]],
    *,
    with_emulator: bool,
) -> list[str]:
    checks: list[str] = []
    if not structure.get("exists"):
        checks.append("対象repositoryが見つからないため、統合ポイントの人間確認が必要。")
    if cloud:
        checks.append("クラウドSDKの本番credential、権限、region / project、endpoint切替方式を人間確認する。")
    if payment:
        checks.append("決済SDKのlive credential、誤課金防止、Webhook署名、返金・税・通貨ルールを人間確認する。")
    if candidates and not with_emulator:
        checks.append("エミュレータ候補はあるが、このrunでは起動・検証していない。必要なら --with-emulator 付きで確認する。")
    for candidate in candidates:
        for item in candidate.get("verification_scope", []):
            if item.get("classification") != "emulator_verified":
                checks.append(f"{candidate.get('provider')}:{item.get('service')} は {item.get('classification')} として扱う。")
    return list(dict.fromkeys(checks))


def knowledge_targets(context: dict[str, Any]) -> list[str]:
    targets = [
        "統合ポイントとAdapter / Port境界",
        "設定・認証・例外・ログの統合判断",
        "Integration TestとEvidence配置の判断",
    ]
    if context.get("emulator_candidates"):
        targets.append("Emulator設定と本番差分")
    if context.get("static_findings"):
        targets.append("検出した違和感と解決方針")
    return targets


def context_status(findings: list[dict[str, str]], checks: list[str]) -> str:
    if checks:
        return "human-check-required"
    if any(item.get("status") == "warning" for item in findings):
        return "available-with-warnings"
    return "available"


def render_report(context: dict[str, Any]) -> str:
    structure = context.get("target_system", {})
    cloud = context.get("cloud", {})
    payment = context.get("payment", {})
    lines = [
        "# System Integration Report",
        "",
        "## 変更概要",
        "",
        f"- status: `{context.get('status', '')}`",
        f"- stage: `{context.get('stage', '')}`",
        f"- work_id: `{context.get('work_id', '')}`",
        "",
        "## 対象システム構造",
        "",
        f"- target repository: `{structure.get('path', '')}`",
        f"- exists: `{structure.get('exists', False)}`",
        f"- package files: `{', '.join(structure.get('package_files', [])) or '未検出'}`",
        f"- has tests: `{structure.get('has_tests', False)}`",
        f"- has docs/evidence: `{structure.get('has_docs_evidence', False)}`",
        "",
        "## 統合ポイント",
        "",
    ]
    for point in context.get("integration_points", []):
        lines.append(f"- {point.get('type')}: evidence=`{', '.join(point.get('evidence', [])) or '未検出'}` required=`{point.get('required', False)}`")
    lines.extend(["", "## SDK・外部サービス", ""])
    lines.append(f"- cloud provider: `{cloud.get('provider', 'unknown')}`")
    lines.append(f"- cloud services: `{', '.join(cloud.get('services', [])) or '未検出'}`")
    lines.append(f"- payment vendor: `{payment.get('vendor', 'unknown')}`")
    lines.append(f"- payment services: `{', '.join(payment.get('services', [])) or '未検出'}`")
    lines.extend(["", "## Emulatorと本番の差分", ""])
    candidates = context.get("emulator_candidates", [])
    if candidates:
        for candidate in candidates:
            lines.append(f"### {candidate.get('provider')} - {candidate.get('emulator')}")
            lines.append(f"- template: `{candidate.get('template_path', '')}`")
            lines.append(f"- recommended work path: `{candidate.get('recommended_work_path', '')}`")
            for scope in candidate.get("verification_scope", []):
                lines.append(
                    f"- {scope.get('service')}: `{scope.get('classification')}`"
                    f" / tool=`{scope.get('tool', '') or '未登録'}`"
                    f" / {scope.get('reason', '')}"
                )
            lines.append("")
    else:
        lines.append("- エミュレータ候補は未検出")
    lines.extend(["## 静的整合性確認", ""])
    for finding in context.get("static_findings", []):
        lines.append(f"- {finding.get('check')}: `{finding.get('status')}` - {finding.get('detail')}")
    lines.extend(["", "## Integration Test結果", ""])
    verify = context.get("verification", {})
    if verify:
        lines.append(f"- mode: `{verify.get('mode', '')}`")
        lines.append(f"- evidence status: `{verify.get('evidence_status', '')}`")
        for item in verify.get("expected_evidence", []):
            lines.append(f"- {item.get('path')}: `{item.get('status')}`")
    else:
        lines.append("- verify未実行")
    lines.extend(["", "## Human Check", ""])
    checks = context.get("human_checks", [])
    lines.extend(f"- {item}" for item in checks) if checks else lines.append("- なし")
    lines.extend(["", "## Knowledge化対象", ""])
    lines.extend(f"- {item}" for item in context.get("knowledge_targets", []))
    lines.extend(["", "## 出力", ""])
    for key, value in context.get("artifacts", {}).items():
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(repo_root: Path, work_dir: Path, context: dict[str, Any]) -> dict[str, str]:
    report_path = work_dir / "reports" / "system-integration-report.md"
    context_path = work_dir / "context" / "integration-context.json"
    artifacts = {
        "report": relative_to_repo(repo_root, report_path),
        "context": relative_to_repo(repo_root, context_path),
    }
    context["artifacts"] = artifacts
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(context), encoding="utf-8")
    write_json(context_path, context)
    return artifacts


def emulator_destination(work_dir: Path, candidate: dict[str, Any]) -> Path:
    recommended = str(candidate.get("recommended_work_path", ""))
    suffix = recommended.replace("work/<work-id>/", "", 1) if recommended.startswith("work/<work-id>/") else ""
    if suffix:
        return work_dir / suffix
    provider = str(candidate.get("provider", "emulator")).strip() or "emulator"
    return work_dir / "test-environment" / "emulator" / provider


def copy_emulator_template(repo_root: Path, work_dir: Path, candidate: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    template_path = resolve_repo_path(repo_root, str(candidate.get("template_path", "")))
    destination = emulator_destination(work_dir, candidate)
    evidence_dir = work_dir / "test-evidence" / "emulator" / str(candidate.get("provider", "emulator"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    if not template_path.exists() or not template_path.is_dir():
        return {
            "provider": candidate.get("provider", ""),
            "status": "missing-template",
            "template_path": relative_to_repo(repo_root, template_path),
            "destination": relative_to_repo(repo_root, destination),
            "evidence_dir": relative_to_repo(repo_root, evidence_dir),
            "message": "Template directory was not found.",
        }
    if destination.exists() and not force:
        return {
            "provider": candidate.get("provider", ""),
            "status": "existing",
            "template_path": relative_to_repo(repo_root, template_path),
            "destination": relative_to_repo(repo_root, destination),
            "evidence_dir": relative_to_repo(repo_root, evidence_dir),
            "message": "Destination already exists. Use --force to refresh the copied emulator template.",
        }
    if destination.exists() and force:
        try:
            destination.resolve().relative_to(work_dir.resolve())
        except ValueError as exc:
            raise ValueError(f"Refusing to remove emulator destination outside work directory: {destination}") from exc
        shutil.rmtree(destination)
    shutil.copytree(template_path, destination)
    copied_files = [
        path.relative_to(destination).as_posix()
        for path in sorted(destination.rglob("*"), key=lambda item: item.relative_to(destination).as_posix().lower())
        if path.is_file()
    ]
    return {
        "provider": candidate.get("provider", ""),
        "status": "copied",
        "template_path": relative_to_repo(repo_root, template_path),
        "destination": relative_to_repo(repo_root, destination),
        "evidence_dir": relative_to_repo(repo_root, evidence_dir),
        "copied_file_count": len(copied_files),
        "copied_files": copied_files,
        "message": "Emulator template was copied to the work area.",
    }


def prepare_emulator(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    target_repo: str = "",
    force: bool = False,
) -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    base_context = build_context(
        repo_root,
        command="analyze",
        work_id=work_id,
        work_dir=work_dir,
        target_repo=target_repo,
        with_emulator=True,
    )
    candidates = base_context.get("emulator_candidates", [])
    prepared = [copy_emulator_template(repo_root, work_path, candidate, force=force) for candidate in candidates]
    status = "prepared"
    if not candidates:
        status = "skipped"
    elif any(item.get("status") == "missing-template" for item in prepared):
        status = "human-check-required"
    elif all(item.get("status") == "existing" for item in prepared):
        status = "existing"
    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": EMULATOR_CONTEXT_ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "workflow": "system-integration-quality",
        "generated_at": utc_now_iso(),
        "source_context": base_context.get("artifacts", {}).get("context", ""),
        "emulator_candidates": candidates,
        "prepared": prepared,
        "rules": {
            "template_source_is_read_only": True,
            "edit_only_work_copy": True,
            "do_not_start_emulator_in_prepare": True,
            "do_not_use_production_credentials": True,
        },
    }
    context_path = work_path / "context" / "emulator-context.json"
    write_json(context_path, context)
    manifest = register_context(
        repo_root,
        work_path,
        work_id=work_id,
        context_type="emulator-setup",
        path=context_path,
        required=False,
        generated_by="system-integration-quality",
        owner="system-integration-quality",
        schema=DEFAULT_EMULATOR_SCHEMA,
        status=status,
    )
    context["artifacts"] = {"context": relative_to_repo(repo_root, context_path)}
    context["manifest_path"] = relative_to_repo(repo_root, work_path / "context" / "context-manifest.json")
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(context_path, context)
    return context


def docker_preflight(*, probe: bool = False) -> dict[str, Any]:
    docker_path = shutil.which("docker")
    result: dict[str, Any] = {
        "docker_path": docker_path or "",
        "docker_available": bool(docker_path),
        "probe_requested": probe,
        "docker_version_status": "not-probed",
        "compose_version_status": "not-probed",
        "notes": [],
    }
    if not docker_path:
        result["docker_version_status"] = "missing"
        result["compose_version_status"] = "missing"
        result["notes"].append("docker executable was not found on PATH.")
        return result
    if not probe:
        result["notes"].append("docker executable was found, but version checks were not executed. Use --probe-docker to run non-mutating checks.")
        return result
    checks = [
        ("docker_version_status", [docker_path, "version", "--format", "{{.Server.Version}}"]),
        ("compose_version_status", [docker_path, "compose", "version"]),
    ]
    for key, command in checks:
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            result[key] = "error"
            result.setdefault("probe_errors", []).append(f"{key}: {exc}")
            continue
        result[key] = "pass" if completed.returncode == 0 else "fail"
        result.setdefault("probe_outputs", {})[key] = (completed.stdout or completed.stderr).strip()[:500]
    return result


def health_file_candidates(destination: Path) -> dict[str, bool]:
    return {
        "compose_file": any((destination / name).exists() for name in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]),
        "env_example": (destination / ".env.example").exists(),
        "readme": (destination / "README.md").exists(),
        "health_doc": any((destination / name).exists() for name in ["healthcheck.md", "webhook-test.md"]),
    }


def emulator_health(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    probe_docker: bool = False,
) -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    setup_context_path = work_path / "context" / "emulator-context.json"
    setup_context = read_json(setup_context_path, default={})
    if not isinstance(setup_context, dict) or setup_context.get("artifact_type") != EMULATOR_CONTEXT_ARTIFACT_TYPE:
        context = {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": EMULATOR_HEALTH_ARTIFACT_TYPE,
            "status": "human-check-required",
            "work_id": work_id,
            "workflow": "system-integration-quality",
            "generated_at": utc_now_iso(),
            "source_context": relative_to_repo(repo_root, setup_context_path),
            "checks": [],
            "docker": docker_preflight(probe=probe_docker),
            "human_checks": ["emulator-context.json が未生成です。先に aiwfctl integration emulator prepare --work-id <work-id> を実行してください。"],
            "rules": {
                "do_not_start_emulator_in_health": True,
                "health_check_is_non_mutating": True,
                "do_not_use_production_credentials": True,
            },
        }
        return write_emulator_health_outputs(repo_root, work_path, context)

    checks: list[dict[str, Any]] = []
    human_checks: list[str] = []
    for item in setup_context.get("prepared", []):
        destination = resolve_repo_path(repo_root, str(item.get("destination", "")))
        evidence_dir = resolve_repo_path(repo_root, str(item.get("evidence_dir", "")))
        files = health_file_candidates(destination)
        missing = [key for key, present in files.items() if not present]
        status = "ready" if destination.exists() and not missing else "warning"
        if not destination.exists():
            status = "human-check-required"
            human_checks.append(f"{item.get('provider', '')} emulator work directory が見つかりません。")
        elif missing:
            human_checks.append(f"{item.get('provider', '')} emulator template の点検項目が不足しています: {', '.join(missing)}")
        checks.append(
            {
                "provider": item.get("provider", ""),
                "status": status,
                "destination": item.get("destination", ""),
                "evidence_dir": item.get("evidence_dir", ""),
                "destination_exists": destination.exists(),
                "evidence_dir_exists": evidence_dir.exists(),
                "files": files,
                "missing": missing,
            }
        )
    docker = docker_preflight(probe=probe_docker)
    if not docker.get("docker_available"):
        human_checks.append("DockerがPATH上に見つかりません。Docker Desktopまたはdocker CLIの利用可否を確認してください。")
    if not checks:
        human_checks.append("emulator prepare結果が空です。SDK解析contextまたはemulator候補を確認してください。")
    status = "ready"
    if any(check.get("status") == "human-check-required" for check in checks) or not docker.get("docker_available") or not checks:
        status = "human-check-required"
    elif any(check.get("status") == "warning" for check in checks):
        status = "warning"
    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": EMULATOR_HEALTH_ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "workflow": "system-integration-quality",
        "generated_at": utc_now_iso(),
        "source_context": relative_to_repo(repo_root, setup_context_path),
        "checks": checks,
        "docker": docker,
        "human_checks": list(dict.fromkeys(human_checks)),
        "rules": {
            "do_not_start_emulator_in_health": True,
            "health_check_is_non_mutating": True,
            "do_not_use_production_credentials": True,
        },
    }
    return write_emulator_health_outputs(repo_root, work_path, context)


def render_emulator_health_summary(context: dict[str, Any]) -> str:
    lines = [
        "# Emulator Health Summary",
        "",
        f"- status: `{context.get('status', '')}`",
        f"- work_id: `{context.get('work_id', '')}`",
        f"- source_context: `{context.get('source_context', '')}`",
        "",
        "## Docker Preflight",
        "",
    ]
    docker = context.get("docker", {})
    lines.extend(
        [
            f"- docker_available: `{docker.get('docker_available', False)}`",
            f"- docker_path: `{docker.get('docker_path', '')}`",
            f"- docker_version_status: `{docker.get('docker_version_status', '')}`",
            f"- compose_version_status: `{docker.get('compose_version_status', '')}`",
            "",
            "## Template Checks",
            "",
        ]
    )
    checks = context.get("checks", [])
    if checks:
        for check in checks:
            lines.append(f"### {check.get('provider', '')}")
            lines.append(f"- status: `{check.get('status', '')}`")
            lines.append(f"- destination: `{check.get('destination', '')}`")
            lines.append(f"- evidence_dir: `{check.get('evidence_dir', '')}`")
            for key, value in check.get("files", {}).items():
                lines.append(f"- {key}: `{value}`")
            if check.get("missing"):
                lines.append(f"- missing: `{', '.join(check.get('missing', []))}`")
            lines.append("")
    else:
        lines.append("- no emulator template checks")
    lines.extend(["## Human Check", ""])
    human_checks = context.get("human_checks", [])
    lines.extend(f"- {item}" for item in human_checks) if human_checks else lines.append("- なし")
    return "\n".join(lines).rstrip() + "\n"


def write_emulator_health_outputs(repo_root: Path, work_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
    context_path = work_dir / "context" / "emulator-health-context.json"
    evidence_path = work_dir / "test-evidence" / "emulator" / "health-summary.md"
    context["artifacts"] = {
        "context": relative_to_repo(repo_root, context_path),
        "evidence": relative_to_repo(repo_root, evidence_path),
    }
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(render_emulator_health_summary(context), encoding="utf-8")
    write_json(context_path, context)
    manifest = register_context(
        repo_root,
        work_dir,
        work_id=str(context.get("work_id", "")),
        context_type="emulator-health",
        path=context_path,
        required=False,
        generated_by="system-integration-quality",
        owner="system-integration-quality",
        schema=DEFAULT_EMULATOR_HEALTH_SCHEMA,
        status=str(context.get("status", "")),
    )
    context["manifest_path"] = relative_to_repo(repo_root, work_dir / "context" / "context-manifest.json")
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(context_path, context)
    return context


def integration_test_phases(emulator_health_context: dict[str, Any], target_repo: Path) -> list[dict[str, Any]]:
    emulator_checks = emulator_health_context.get("checks", []) if isinstance(emulator_health_context, dict) else []
    external_dependencies = [
        {
            "provider": check.get("provider", ""),
            "destination": check.get("destination", ""),
            "start_command": f"docker compose -f {check.get('destination', '')}/docker-compose.yml up -d",
            "stop_command": f"docker compose -f {check.get('destination', '')}/docker-compose.yml down",
            "health_evidence_dir": check.get("evidence_dir", ""),
        }
        for check in emulator_checks
        if check.get("destination")
    ]
    target_commands = {
        "repository": str(target_repo),
        "start_command": "Use target repository's documented startup command after Human Check.",
        "test_command": "Use target repository's documented integration test command after Human Check.",
    }
    return [
        {
            "id": "environment-setup",
            "title": "試験環境構築",
            "purpose": "work配下のemulator template、環境変数sample、証跡ディレクトリ、対象repositoryを確認する。",
            "inputs": ["emulator-health-context.json", "target repository"],
            "human_check_required": False,
            "evidence": ["emulator-health-context.json", "health-summary.md"],
        },
        {
            "id": "external-dependency-start",
            "title": "外部依存起動",
            "purpose": "LocalStack、GCP emulator、Stripe CLIなどの外部依存を起動する。",
            "inputs": external_dependencies,
            "human_check_required": True,
            "reason": "Docker compose起動はローカル状態を変更するため、明示判断後に実行する。",
        },
        {
            "id": "health-check",
            "title": "Health Check",
            "purpose": "外部依存の起動状態と対象service endpointを確認する。",
            "inputs": [item.get("health_evidence_dir", "") for item in external_dependencies],
            "human_check_required": False,
            "evidence": ["test-evidence/emulator/*/healthcheck result"],
        },
        {
            "id": "seed-data",
            "title": "初期データ投入",
            "purpose": "Integration Testに必要なbucket、topic、queue、fixture、webhook secretなどを準備する。",
            "inputs": ["target repository fixture", "emulator setup README"],
            "human_check_required": True,
            "reason": "seed内容が本番相当credentialや課金挙動へ触れないことを確認する。",
        },
        {
            "id": "target-system-start",
            "title": "対象システム起動",
            "purpose": "対象repositoryの既存手順に従ってsystemを起動する。",
            "inputs": target_commands,
            "human_check_required": True,
            "reason": "対象systemの起動はport、process、外部接続、ローカル状態を変更する可能性がある。",
        },
        {
            "id": "normal-path",
            "title": "正常系実行",
            "purpose": "SDK初期化、認証差し替え、データ送受信、正常レスポンス、冪等性を確認する。",
            "inputs": ["integration test command", "normal scenario"],
            "human_check_required": False,
            "evidence": ["test result", "logs", "data snapshot"],
        },
        {
            "id": "error-path",
            "title": "異常系実行",
            "purpose": "SDK例外変換、timeout、retry、外部サービス停止時の挙動を確認する。",
            "inputs": ["failure scenario", "retry/timeout settings"],
            "human_check_required": False,
            "evidence": ["test result", "error logs", "mapped exception"],
        },
        {
            "id": "logs-data-check",
            "title": "ログ・データ確認",
            "purpose": "ログ形式、metrics、永続化、重複処理、後方互換性を確認する。",
            "inputs": ["logs", "metrics", "database/emulator data"],
            "human_check_required": False,
            "evidence": ["log excerpt", "metric snapshot", "data assertion"],
        },
        {
            "id": "cleanup",
            "title": "環境初期化",
            "purpose": "外部依存停止、fixture削除、ローカル状態の復元を行う。",
            "inputs": external_dependencies,
            "human_check_required": True,
            "reason": "停止・削除操作はローカル状態を変更するため、対象を確認してから実行する。",
        },
    ]


def render_integration_test_runbook(context: dict[str, Any]) -> str:
    lines = [
        "# Integration Test Runbook",
        "",
        f"- status: `{context.get('status', '')}`",
        f"- work_id: `{context.get('work_id', '')}`",
        f"- source_context: `{context.get('source_context', '')}`",
        f"- emulator_health_context: `{context.get('emulator_health_context', '')}`",
        "",
        "## 実行前提",
        "",
        "- 本番credential、本番クラウド、本番決済、本番networkを使わない。",
        "- Docker composeや対象システム起動はHuman Check後に実行する。",
        "- emulator成功を本番等価として扱わない。",
        "- 証跡は `work/<work-id>/test-evidence/` 配下へ保存する。",
        "",
        "## Phase",
        "",
    ]
    for phase in context.get("phases", []):
        lines.append(f"### {phase.get('id', '')}: {phase.get('title', '')}")
        lines.append(f"- purpose: {phase.get('purpose', '')}")
        lines.append(f"- human_check_required: `{phase.get('human_check_required', False)}`")
        if phase.get("reason"):
            lines.append(f"- reason: {phase.get('reason', '')}")
        evidence = phase.get("evidence", [])
        if evidence:
            lines.append("- evidence:")
            lines.extend(f"  - `{item}`" for item in evidence)
        lines.append("")
    lines.extend(["## Human Check", ""])
    human_checks = context.get("human_checks", [])
    lines.extend(f"- {item}" for item in human_checks) if human_checks else lines.append("- なし")
    lines.extend(["", "## Completion Evidence", ""])
    for item in context.get("completion_evidence", []):
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def write_integration_test_plan_outputs(repo_root: Path, work_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
    context_path = work_dir / "context" / "integration-test-plan-context.json"
    runbook_path = work_dir / "test-evidence" / "integration-test" / "integration-test-runbook.md"
    context["artifacts"] = {
        "context": relative_to_repo(repo_root, context_path),
        "runbook": relative_to_repo(repo_root, runbook_path),
    }
    runbook_path.parent.mkdir(parents=True, exist_ok=True)
    runbook_path.write_text(render_integration_test_runbook(context), encoding="utf-8")
    write_json(context_path, context)
    manifest = register_context(
        repo_root,
        work_dir,
        work_id=str(context.get("work_id", "")),
        context_type="integration-test-plan",
        path=context_path,
        required=False,
        generated_by="system-integration-quality",
        owner="system-integration-quality",
        schema=DEFAULT_TEST_PLAN_SCHEMA,
        status=str(context.get("status", "")),
    )
    context["manifest_path"] = relative_to_repo(repo_root, work_dir / "context" / "context-manifest.json")
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(context_path, context)
    return context


def integration_test_plan(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    target_repo: str = "",
) -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    target_path = resolve_repo_path(repo_root, target_repo) if target_repo else default_target_repo(work_path)
    integration_context_path = work_path / "context" / "integration-context.json"
    emulator_health_path = work_path / "context" / "emulator-health-context.json"
    integration_context = read_json(integration_context_path, default={})
    emulator_health_context = read_json(emulator_health_path, default={})
    human_checks: list[str] = []
    if not isinstance(integration_context, dict) or integration_context.get("artifact_type") != ARTIFACT_TYPE:
        human_checks.append("integration-context.json が未生成です。先に aiwfctl integration analyze/verify --work-id <work-id> を実行してください。")
    if not isinstance(emulator_health_context, dict) or emulator_health_context.get("artifact_type") != EMULATOR_HEALTH_ARTIFACT_TYPE:
        human_checks.append("emulator-health-context.json が未生成です。先に aiwfctl integration emulator health --work-id <work-id> を実行してください。")
        emulator_health_context = {}
    elif emulator_health_context.get("status") == "human-check-required":
        human_checks.append("emulator health が human-check-required です。Integration Test実行前にhealthのHuman Checkを解消してください。")
    if not target_path.exists():
        human_checks.append("対象repositoryが見つかりません。--target-repo または work/<work-id>/source/repository を確認してください。")
    phases = integration_test_phases(emulator_health_context, target_path)
    human_checks.extend(
        [
            "Docker compose起動、対象システム起動、seed投入、cleanupはローカル状態を変更するためHuman Check後に実行してください。",
            "本番credential、本番クラウド、本番決済、本番networkを使わないことを確認してください。",
        ]
    )
    status = "planned"
    if any("未生成" in item or "見つかりません" in item or "human-check-required" in item for item in human_checks):
        status = "human-check-required"
    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": INTEGRATION_TEST_PLAN_ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "workflow": "system-integration-quality",
        "generated_at": utc_now_iso(),
        "target_repo": str(target_path),
        "source_context": relative_to_repo(repo_root, integration_context_path),
        "emulator_health_context": relative_to_repo(repo_root, emulator_health_path),
        "phases": phases,
        "human_checks": list(dict.fromkeys(human_checks)),
        "completion_evidence": [
            "外部依存起動log",
            "Health Check結果",
            "初期データ投入結果",
            "対象システム起動log",
            "正常系Integration Test結果",
            "異常系Integration Test結果",
            "ログ・metrics・データ確認結果",
            "cleanup結果",
            "emulatorと本番差分の記録",
        ],
        "rules": {
            "do_not_start_emulator_in_plan": True,
            "do_not_start_target_system_in_plan": True,
            "human_check_required_before_mutation": True,
            "do_not_use_production_credentials": True,
            "do_not_treat_emulator_success_as_production_equivalence": True,
        },
    }
    return write_integration_test_plan_outputs(repo_root, work_path, context)


def collect_evidence_files(repo_root: Path, work_dir: Path, target_repo: Path) -> list[dict[str, Any]]:
    roots = [
        ("work-test-evidence", work_dir / "test-evidence"),
        ("work-evidence", work_dir / "evidence"),
        ("target-docs-evidence", target_repo / "docs" / "evidence"),
    ]
    evidence: list[dict[str, Any]] = []
    allowed_suffixes = {
        ".md",
        ".txt",
        ".json",
        ".jsonl",
        ".log",
        ".xml",
        ".html",
        ".csv",
    }
    for category, root in roots:
        if not root.exists() or not root.is_dir():
            continue
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
            if not path.is_file() or path.suffix.lower() not in allowed_suffixes:
                continue
            evidence.append(
                {
                    "category": category,
                    "path": relative_to_repo(repo_root, path),
                    "size_bytes": path.stat().st_size,
                    "status": "present" if path.stat().st_size > 0 else "empty",
                }
            )
    return evidence[:200]


def completion_checks(
    *,
    integration_context: dict[str, Any],
    emulator_health_context: dict[str, Any],
    test_plan_context: dict[str, Any],
    evidence_files: list[dict[str, Any]],
) -> list[dict[str, str]]:
    checks = [
        {
            "id": "target-system-structure",
            "description": "対象システムの構造を解析できる",
            "status": "pass" if integration_context.get("target_system", {}).get("exists") else "missing",
        },
        {
            "id": "integration-points",
            "description": "統合ポイントを明示できる",
            "status": "pass" if integration_context.get("integration_points") else "missing",
        },
        {
            "id": "sdk-boundary",
            "description": "SDKや外部サービスを境界へ閉じ込められる",
            "status": "pass" if any(point.get("type") == "adapter-boundary" for point in integration_context.get("integration_points", [])) else "warning",
        },
        {
            "id": "unit-test",
            "description": "Unit Testが成功する",
            "status": "pass" if any("unit" in item.get("path", "").lower() or "pytest" in item.get("path", "").lower() for item in evidence_files) else "warning",
        },
        {
            "id": "integration-test",
            "description": "Integration Testが成功する",
            "status": "pass" if any("integration" in item.get("path", "").lower() for item in evidence_files) else "missing",
        },
        {
            "id": "emulator-difference",
            "description": "Emulator利用時の差分を明示できる",
            "status": "pass" if emulator_health_context.get("artifact_type") == EMULATOR_HEALTH_ARTIFACT_TYPE else "missing",
        },
        {
            "id": "existing-impact",
            "description": "既存機能への影響を確認できる",
            "status": "pass" if any("regression" in item.get("path", "").lower() or "互換" in item.get("path", "") for item in evidence_files) else "warning",
        },
        {
            "id": "discomfort-record",
            "description": "違和感を検出・記録できる",
            "status": "pass" if integration_context.get("static_findings") else "warning",
        },
        {
            "id": "evidence-saved",
            "description": "Evidenceを保存できる",
            "status": "pass" if evidence_files else "missing",
        },
        {
            "id": "system-integration-report",
            "description": "システム統合レポートを生成できる",
            "status": "pass" if integration_context.get("artifacts", {}).get("report") else "missing",
        },
        {
            "id": "knowledge-handoff",
            "description": "Knowledge化フローへ引き渡せる",
            "status": "pass" if integration_context.get("knowledge_targets") else "warning",
        },
        {
            "id": "workflow-feedback",
            "description": "Workflow Feedbackを残せる",
            "status": "pass" if (test_plan_context.get("artifact_type") == INTEGRATION_TEST_PLAN_ARTIFACT_TYPE) else "warning",
        },
    ]
    return checks


def detect_discomforts(
    *,
    integration_context: dict[str, Any],
    emulator_health_context: dict[str, Any],
    test_plan_context: dict[str, Any],
    evidence_files: list[dict[str, Any]],
    completion: list[dict[str, str]],
) -> list[dict[str, str]]:
    discomforts: list[dict[str, str]] = []
    for finding in integration_context.get("static_findings", []):
        if finding.get("status") != "pass":
            discomforts.append(
                {
                    "source": "static-consistency",
                    "severity": "medium" if finding.get("status") == "warning" else "high",
                    "detail": f"{finding.get('check')}: {finding.get('detail')}",
                }
            )
    if emulator_health_context.get("status") == "human-check-required":
        discomforts.append(
            {
                "source": "emulator-health",
                "severity": "high",
                "detail": "emulator health が human-check-required のため、Integration Test前提に未解決事項があります。",
            }
        )
    if test_plan_context.get("status") == "human-check-required":
        discomforts.append(
            {
                "source": "integration-test-plan",
                "severity": "high",
                "detail": "Integration Test plan が human-check-required のため、実行前の前提に未解決事項があります。",
            }
        )
    empty_files = [item for item in evidence_files if item.get("status") == "empty"]
    if empty_files:
        discomforts.append(
            {
                "source": "evidence",
                "severity": "medium",
                "detail": f"空のEvidence fileが検出されました: {len(empty_files)}件",
            }
        )
    missing = [item for item in completion if item.get("status") == "missing"]
    if missing:
        discomforts.append(
            {
                "source": "completion-check",
                "severity": "high",
                "detail": "完了条件に未達項目があります: " + ", ".join(item.get("id", "") for item in missing),
            }
        )
    return discomforts


def finalization_status(completion: list[dict[str, str]], discomforts: list[dict[str, str]]) -> str:
    if any(item.get("severity") == "high" for item in discomforts):
        return "human-check-required"
    if any(item.get("status") == "missing" for item in completion):
        return "incomplete"
    if any(item.get("status") == "warning" for item in completion):
        return "complete-with-warnings"
    return "complete"


def render_finalization_report(context: dict[str, Any]) -> str:
    lines = [
        "# System Integration Final Report",
        "",
        "## 変更概要",
        "",
        f"- status: `{context.get('status', '')}`",
        f"- work_id: `{context.get('work_id', '')}`",
        f"- target_repo: `{context.get('target_repo', '')}`",
        "",
        "## 完了条件",
        "",
    ]
    for item in context.get("completion_checks", []):
        lines.append(f"- {item.get('id')}: `{item.get('status')}` - {item.get('description')}")
    lines.extend(["", "## Evidence", ""])
    evidence_files = context.get("evidence_files", [])
    if evidence_files:
        for item in evidence_files:
            lines.append(f"- {item.get('category')}: `{item.get('path')}` ({item.get('status')}, {item.get('size_bytes')} bytes)")
    else:
        lines.append("- Evidence未検出")
    lines.extend(["", "## Integration Test結果", ""])
    lines.append(f"- plan context: `{context.get('test_plan_context', '')}`")
    lines.append(f"- emulator health context: `{context.get('emulator_health_context', '')}`")
    lines.extend(["", "## 検出した違和感", ""])
    discomforts = context.get("discomforts", [])
    if discomforts:
        for item in discomforts:
            lines.append(f"- `{item.get('severity')}` {item.get('source')}: {item.get('detail')}")
    else:
        lines.append("- なし")
    lines.extend(["", "## Human Check", ""])
    human_checks = context.get("human_checks", [])
    lines.extend(f"- {item}" for item in human_checks) if human_checks else lines.append("- なし")
    lines.extend(["", "## Knowledge化対象", ""])
    for item in context.get("knowledge_targets", []):
        lines.append(f"- {item}")
    lines.extend(["", "## 残課題", ""])
    open_items = [
        item
        for item in context.get("completion_checks", [])
        if item.get("status") in {"missing", "warning"}
    ]
    if open_items:
        lines.extend(f"- {item.get('description')} ({item.get('status')})" for item in open_items)
    else:
        lines.append("- なし")
    lines.extend(["", "## 出力", ""])
    for key, value in context.get("artifacts", {}).items():
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines).rstrip() + "\n"


def write_finalization_outputs(repo_root: Path, work_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
    context_path = work_dir / "context" / "integration-finalization-context.json"
    report_path = work_dir / "reports" / "system-integration-final-report.md"
    context["artifacts"] = {
        "context": relative_to_repo(repo_root, context_path),
        "report": relative_to_repo(repo_root, report_path),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_finalization_report(context), encoding="utf-8")
    write_json(context_path, context)
    manifest = register_context(
        repo_root,
        work_dir,
        work_id=str(context.get("work_id", "")),
        context_type="integration-finalization",
        path=context_path,
        required=False,
        generated_by="system-integration-quality",
        owner="system-integration-quality",
        schema=DEFAULT_FINALIZATION_SCHEMA,
        status=str(context.get("status", "")),
    )
    context["manifest_path"] = relative_to_repo(repo_root, work_dir / "context" / "context-manifest.json")
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(context_path, context)
    return context


def finalize_integration(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    target_repo: str = "",
) -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    target_path = resolve_repo_path(repo_root, target_repo) if target_repo else default_target_repo(work_path)
    integration_context_path = work_path / "context" / "integration-context.json"
    emulator_health_path = work_path / "context" / "emulator-health-context.json"
    test_plan_path = work_path / "context" / "integration-test-plan-context.json"
    integration_context = read_json(integration_context_path, default={})
    emulator_health_context = read_json(emulator_health_path, default={})
    test_plan_context = read_json(test_plan_path, default={})
    human_checks: list[str] = []
    if not isinstance(integration_context, dict) or integration_context.get("artifact_type") != ARTIFACT_TYPE:
        human_checks.append("integration-context.json が未生成です。先に aiwfctl integration analyze/verify --work-id <work-id> を実行してください。")
        integration_context = {}
    if not isinstance(emulator_health_context, dict) or emulator_health_context.get("artifact_type") != EMULATOR_HEALTH_ARTIFACT_TYPE:
        human_checks.append("emulator-health-context.json が未生成です。先に aiwfctl integration emulator health --work-id <work-id> を実行してください。")
        emulator_health_context = {}
    if not isinstance(test_plan_context, dict) or test_plan_context.get("artifact_type") != INTEGRATION_TEST_PLAN_ARTIFACT_TYPE:
        human_checks.append("integration-test-plan-context.json が未生成です。先に aiwfctl integration test-plan --work-id <work-id> を実行してください。")
        test_plan_context = {}
    evidence_files = collect_evidence_files(repo_root, work_path, target_path)
    completion = completion_checks(
        integration_context=integration_context,
        emulator_health_context=emulator_health_context,
        test_plan_context=test_plan_context,
        evidence_files=evidence_files,
    )
    discomforts = detect_discomforts(
        integration_context=integration_context,
        emulator_health_context=emulator_health_context,
        test_plan_context=test_plan_context,
        evidence_files=evidence_files,
        completion=completion,
    )
    if human_checks:
        discomforts.append(
            {
                "source": "missing-context",
                "severity": "high",
                "detail": "finalizeに必要なContextが不足しています。",
            }
        )
    status = finalization_status(completion, discomforts)
    knowledge_targets = list(dict.fromkeys(integration_context.get("knowledge_targets", []) + [
        "Integration Test実行証跡",
        "検出した違和感と完了条件判定",
    ]))
    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": INTEGRATION_FINALIZATION_ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "workflow": "system-integration-quality",
        "generated_at": utc_now_iso(),
        "target_repo": str(target_path),
        "source_context": relative_to_repo(repo_root, integration_context_path),
        "emulator_health_context": relative_to_repo(repo_root, emulator_health_path),
        "test_plan_context": relative_to_repo(repo_root, test_plan_path),
        "evidence_files": evidence_files,
        "completion_checks": completion,
        "discomforts": discomforts,
        "human_checks": list(dict.fromkeys(human_checks + [item.get("detail", "") for item in discomforts if item.get("severity") == "high"])),
        "knowledge_targets": knowledge_targets,
        "rules": {
            "finalize_is_read_only_over_evidence": True,
            "do_not_execute_tests_in_finalize": True,
            "do_not_use_production_credentials": True,
            "source_code_wholesale_knowledge_capture_is_forbidden": True,
        },
    }
    return write_finalization_outputs(repo_root, work_path, context)


def expected_evidence(work_dir: Path, target_repo: Path) -> list[dict[str, str]]:
    candidates = [
        work_dir / "test-evidence",
        work_dir / "evidence",
        target_repo / "docs" / "evidence",
        target_repo / "tests",
    ]
    result = []
    for path in candidates:
        result.append({"path": path.as_posix(), "status": "present" if path.exists() else "missing"})
    return result


def build_context(
    repo_root: Path,
    *,
    command: str,
    work_id: str,
    work_dir: str = "",
    target_repo: str = "",
    with_emulator: bool = False,
) -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    target_path = resolve_repo_path(repo_root, target_repo) if target_repo else default_target_repo(work_path)
    contexts = load_contexts(work_path)
    cloud = extract_cloud(contexts)
    payment = extract_payment(contexts)
    structure = detect_project_structure(target_path)
    candidates = emulator_candidates(cloud, payment, with_emulator=with_emulator)
    points = integration_points(target_path, cloud, payment)
    findings = static_consistency_findings(structure, target_path, cloud, payment)
    checks = human_checks(structure, cloud, payment, candidates, with_emulator=with_emulator)
    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "work_id": work_id,
        "workflow": "system-integration-quality",
        "stage": command,
        "generated_at": utc_now_iso(),
        "target_system": structure,
        "input_contexts": {
            name: {
                "present": bool(value),
                "artifact_type": value.get("artifact_type", ""),
                "status": value.get("status", ""),
            }
            for name, value in contexts.items()
        },
        "cloud": cloud,
        "payment": payment,
        "integration_points": points,
        "emulator_requested": with_emulator,
        "emulator_candidates": candidates,
        "static_findings": findings,
        "human_checks": checks,
        "rules": {
            "do_not_start_real_cloud_without_human_check": True,
            "do_not_use_production_credentials_for_emulator": True,
            "emulator_setup_is_plan_or_parent_workflow_action": True,
            "real_cloud_verification_requires_human_check": True,
        },
    }
    if command == "verify":
        evidence = expected_evidence(work_path, target_path)
        context["verification"] = {
            "mode": "with-emulator" if with_emulator else "static-and-evidence",
            "expected_evidence": evidence,
            "evidence_status": "available" if any(item["status"] == "present" for item in evidence) else "missing",
        }
        if context["verification"]["evidence_status"] == "missing":
            checks.append("Integration Test evidenceが未検出のため、人間確認または親workflowでの試験実行が必要。")
    context["knowledge_targets"] = knowledge_targets(context)
    context["status"] = context_status(findings, checks)
    artifacts = write_outputs(repo_root, work_path, context)
    manifest = register_context(
        repo_root,
        work_path,
        work_id=work_id,
        context_type="system-integration",
        path=work_path / "context" / "integration-context.json",
        required=False,
        generated_by="system-integration-quality",
        owner="system-integration-quality",
        schema=DEFAULT_CONTEXT_SCHEMA,
        status=context["status"],
    )
    context["artifacts"] = artifacts
    context["manifest_path"] = relative_to_repo(repo_root, work_path / "context" / "context-manifest.json")
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(work_path / "context" / "integration-context.json", context)
    return context


def format_result(result: dict[str, Any]) -> str:
    if result.get("artifact_type") == EMULATOR_CONTEXT_ARTIFACT_TYPE:
        lines = [
            "System Integration Emulator Prepare",
            "",
            f"Status  : {result.get('status', '')}",
            f"Work ID : {result.get('work_id', '')}",
            f"Context : {result.get('artifacts', {}).get('context', '')}",
            "",
            "Prepared Templates",
        ]
        prepared = result.get("prepared", [])
        if prepared:
            for item in prepared:
                lines.extend(
                    [
                        f"  - {item.get('provider', '')}: {item.get('status', '')}",
                        f"    template   : {item.get('template_path', '')}",
                        f"    destination: {item.get('destination', '')}",
                        f"    evidence   : {item.get('evidence_dir', '')}",
                    ]
                )
        else:
            lines.append("  - none")
        return "\n".join(lines).rstrip() + "\n"

    if result.get("artifact_type") == EMULATOR_HEALTH_ARTIFACT_TYPE:
        lines = [
            "System Integration Emulator Health",
            "",
            f"Status   : {result.get('status', '')}",
            f"Work ID  : {result.get('work_id', '')}",
            f"Context  : {result.get('artifacts', {}).get('context', '')}",
            f"Evidence : {result.get('artifacts', {}).get('evidence', '')}",
            "",
            "Checks",
        ]
        checks = result.get("checks", [])
        if checks:
            for check in checks:
                lines.append(f"  - {check.get('provider', '')}: {check.get('status', '')}")
        else:
            lines.append("  - none")
        human_checks = result.get("human_checks", [])
        if human_checks:
            lines.extend(["", "Human Check"])
            lines.extend(f"  - {item}" for item in human_checks)
        return "\n".join(lines).rstrip() + "\n"

    if result.get("artifact_type") == INTEGRATION_TEST_PLAN_ARTIFACT_TYPE:
        lines = [
            "System Integration Test Plan",
            "",
            f"Status  : {result.get('status', '')}",
            f"Work ID : {result.get('work_id', '')}",
            f"Context : {result.get('artifacts', {}).get('context', '')}",
            f"Runbook : {result.get('artifacts', {}).get('runbook', '')}",
            "",
            "Phases",
        ]
        phases = result.get("phases", [])
        if phases:
            for phase in phases:
                lines.append(
                    f"  - {phase.get('id', '')}: {phase.get('title', '')}"
                    f" (human_check_required={phase.get('human_check_required', False)})"
                )
        else:
            lines.append("  - none")
        human_checks = result.get("human_checks", [])
        if human_checks:
            lines.extend(["", "Human Check"])
            lines.extend(f"  - {item}" for item in human_checks)
        return "\n".join(lines).rstrip() + "\n"

    if result.get("artifact_type") == INTEGRATION_FINALIZATION_ARTIFACT_TYPE:
        lines = [
            "System Integration Finalization",
            "",
            f"Status  : {result.get('status', '')}",
            f"Work ID : {result.get('work_id', '')}",
            f"Context : {result.get('artifacts', {}).get('context', '')}",
            f"Report  : {result.get('artifacts', {}).get('report', '')}",
            "",
            "Completion",
        ]
        for item in result.get("completion_checks", []):
            lines.append(f"  - {item.get('id', '')}: {item.get('status', '')}")
        discomforts = result.get("discomforts", [])
        if discomforts:
            lines.extend(["", "Discomforts"])
            for item in discomforts:
                lines.append(f"  - {item.get('severity', '')} {item.get('source', '')}: {item.get('detail', '')}")
        human_checks = result.get("human_checks", [])
        if human_checks:
            lines.extend(["", "Human Check"])
            lines.extend(f"  - {item}" for item in human_checks)
        return "\n".join(lines).rstrip() + "\n"

    lines = [
        "System Integration Quality",
        "",
        f"Status   : {result.get('status', '')}",
        f"Stage    : {result.get('stage', '')}",
        f"Work ID  : {result.get('work_id', '')}",
        f"Context  : {result.get('artifacts', {}).get('context', '')}",
        f"Report   : {result.get('artifacts', {}).get('report', '')}",
        "",
        "Emulator Candidates",
    ]
    candidates = result.get("emulator_candidates", [])
    if candidates:
        for candidate in candidates:
            lines.append(f"  - {candidate.get('provider')}: {candidate.get('emulator')} ({candidate.get('template_path', '')})")
    else:
        lines.append("  - none")
    checks = result.get("human_checks", [])
    if checks:
        lines.extend(["", "Human Check"])
        lines.extend(f"  - {item}" for item in checks)
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze and verify system integration quality.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["analyze", "verify"]:
        cmd = sub.add_parser(name)
        cmd.add_argument("--work-id", required=True)
        cmd.add_argument("--work-dir", default="")
        cmd.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
        cmd.add_argument("--with-emulator", action="store_true", help="Include emulator suitability classification.")
        cmd.add_argument("--json", action="store_true")
    plan = sub.add_parser("test-plan", help="Create Integration Test runbook and Context First plan.")
    plan.add_argument("--work-id", required=True)
    plan.add_argument("--work-dir", default="")
    plan.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
    plan.add_argument("--json", action="store_true")
    finalize = sub.add_parser("finalize", help="Collect evidence, detect discomfort, and create final integration report.")
    finalize.add_argument("--work-id", required=True)
    finalize.add_argument("--work-dir", default="")
    finalize.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
    finalize.add_argument("--json", action="store_true")
    emulator = sub.add_parser("emulator", help="Prepare emulator templates under work/<work-id>.")
    emulator_sub = emulator.add_subparsers(dest="emulator_command", required=True)
    prepare = emulator_sub.add_parser("prepare", help="Copy selected emulator boilerplates to the work area.")
    prepare.add_argument("--work-id", required=True)
    prepare.add_argument("--work-dir", default="")
    prepare.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
    prepare.add_argument("--force", action="store_true", help="Refresh existing copied emulator template directories.")
    prepare.add_argument("--json", action="store_true")
    health = emulator_sub.add_parser("health", help="Check copied emulator templates and write health evidence.")
    health.add_argument("--work-id", required=True)
    health.add_argument("--work-dir", default="")
    health.add_argument("--probe-docker", action="store_true", help="Run non-mutating docker version checks.")
    health.add_argument("--json", action="store_true")
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if getattr(args, "repo_root", "") else find_repo_root()
    if args.command == "emulator" and getattr(args, "emulator_command", "") == "prepare":
        return prepare_emulator(
            repo_root,
            work_id=args.work_id,
            work_dir=getattr(args, "work_dir", ""),
            target_repo=getattr(args, "target_repo", ""),
            force=bool(getattr(args, "force", False)),
        )
    if args.command == "emulator" and getattr(args, "emulator_command", "") == "health":
        return emulator_health(
            repo_root,
            work_id=args.work_id,
            work_dir=getattr(args, "work_dir", ""),
            probe_docker=bool(getattr(args, "probe_docker", False)),
        )
    if args.command == "test-plan":
        return integration_test_plan(
            repo_root,
            work_id=args.work_id,
            work_dir=getattr(args, "work_dir", ""),
            target_repo=getattr(args, "target_repo", ""),
        )
    if args.command == "finalize":
        return finalize_integration(
            repo_root,
            work_id=args.work_id,
            work_dir=getattr(args, "work_dir", ""),
            target_repo=getattr(args, "target_repo", ""),
        )
    return build_context(
        repo_root,
        command=args.command,
        work_id=args.work_id,
        work_dir=getattr(args, "work_dir", ""),
        target_repo=getattr(args, "target_repo", ""),
        with_emulator=bool(getattr(args, "with_emulator", False)),
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run(args)
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_result(result), end="")
    return 0 if result.get("status") != "human-check-required" else 2


if __name__ == "__main__":
    raise SystemExit(main())
