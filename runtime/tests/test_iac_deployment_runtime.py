from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl
from runtime.workflow import iac_deployment_runtime
from runtime.workflow import kubernetes_runtime


def write_minimal_template_registries(repo_root: Path) -> None:
    registry_dir = repo_root / "templates" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")
    (registry_dir / "tool_candidates.json").write_text('{"tools": []}', encoding="utf-8")
    (registry_dir / "human_gates.json").write_text('{"gates": []}', encoding="utf-8")
    (registry_dir / "workflow_environment_profiles.json").write_text(
        '{"environments": [], "profiles": [], "mappings": []}',
        encoding="utf-8",
    )


def test_iac_deployment_assessment_contract_and_gap_report(tmp_path: Path) -> None:
    work_id = "issue-iac-app"
    requirement = tmp_path / "work" / work_id / "requirements" / "requirement.md"
    requirement.parent.mkdir(parents=True)
    requirement.write_text(
        "\n".join(
            [
                "# Requirement",
                "",
                "web API service name: payment-api",
                "image: ghcr.io/example/payment-api:0.1.0",
                "port: 8080",
                "health endpoint: /ready",
                "Secret boundary と ConfigMap env を分ける。",
                "resources requests limits を定義する。",
                "logs metrics trace を確認する。",
                "E2E smoke を実施する。",
            ]
        ),
        encoding="utf-8",
    )

    assessment = iac_deployment_runtime.build_assessment(tmp_path, work_id=work_id)
    contract = iac_deployment_runtime.build_contract(tmp_path, work_id=work_id)
    gap_report = iac_deployment_runtime.build_gap_report(tmp_path, work_id=work_id)

    assert assessment["artifact_type"] == "iac-app-runtime-assessment"
    assert assessment["detected"]["execution_unit"] == "web"
    assert assessment["detected"]["port"] == 8080
    assert contract["artifact_type"] == "iac-deployment-contract"
    assert contract["contract"]["app_name"] == "payment-api"
    assert contract["contract"]["image"] == "ghcr.io/example/payment-api:0.1.0"
    assert contract["contract"]["health"]["path"] == "/ready"
    assert gap_report["artifact_type"] == "iac-deployment-gap-report"
    assert (tmp_path / "work" / work_id / "context" / "iac-deployment-contract.md").exists()


def test_kubernetes_assessment_uses_iac_deployment_contract(tmp_path: Path) -> None:
    work_id = "issue-k8s-contract"
    requirement = tmp_path / "work" / work_id / "requirements" / "requirement.md"
    requirement.parent.mkdir(parents=True)
    requirement.write_text(
        "\n".join(
            [
                "# Requirement",
                "",
                "k3s に配置する。",
                "web service name: app-runtime",
                "image: ghcr.io/example/runtime:1.0.0",
                "port: 9090",
                "health endpoint: /healthz",
                "Secret boundary と resources limits を定義する。",
            ]
        ),
        encoding="utf-8",
    )
    iac_deployment_runtime.build_contract(tmp_path, work_id=work_id)

    assessment = kubernetes_runtime.build_compatibility_assessment(tmp_path, work_id=work_id)
    generation = kubernetes_runtime.build_manifest_generation(tmp_path, work_id=work_id)

    assert assessment["deployment_contract_path"] == f"work/{work_id}/context/iac-deployment-contract.json"
    assert assessment["detected"]["image"] == "ghcr.io/example/runtime:1.0.0"
    assert assessment["detected"]["port"] == 9090
    assert generation["applied_values"]["app_name"] == "app-runtime"
    deployment = (
        tmp_path / "work" / work_id / "implementation" / "kubernetes" / "manifests" / "deployment.yaml"
    ).read_text(encoding="utf-8")
    assert "name: app-runtime" in deployment
    assert "ghcr.io/example/runtime:1.0.0" in deployment
    assert "containerPort: 9090" in deployment


def test_aiwfctl_iac_deployment_routes(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    write_minimal_template_registries(repo_root)
    work_id = "issue-iac-deployment-cli"
    requirement = repo_root / "work" / work_id / "requirements" / "requirement.md"
    requirement.parent.mkdir(parents=True)
    requirement.write_text("web\nimage: ghcr.io/example/app:0.1.0\nport: 8080\n", encoding="utf-8")

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "iac",
            "deployment",
            "contract",
            "--work-id",
            work_id,
            "--json",
        ]
    )
    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["artifact_type"] == "iac-deployment-contract"
    assert result["artifacts"]["contract_json"] == f"work/{work_id}/context/iac-deployment-contract.json"
