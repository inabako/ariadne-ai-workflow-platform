from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl
from runtime.workflow import iac_prepare_runtime


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


def test_iac_prepare_runs_deployment_then_kubernetes_flow(tmp_path: Path) -> None:
    work_id = "issue-iac-prepare-k3s"
    requirement = tmp_path / "work" / work_id / "requirements" / "requirement.md"
    requirement.parent.mkdir(parents=True)
    requirement.write_text(
        "\n".join(
            [
                "# Requirement",
                "",
                "k3s に配置する web API service name: runtime-api",
                "image: ghcr.io/example/runtime-api:0.1.0",
                "port: 8080",
                "health endpoint: /ready",
                "Secret boundary と ConfigMap env を分ける。",
                "resources requests limits を定義する。",
                "E2E smoke を実施する。",
            ]
        ),
        encoding="utf-8",
    )

    result = iac_prepare_runtime.build_prepare(tmp_path, work_id=work_id)

    step_names = [item["name"] for item in result["steps"]]
    assert result["artifact_type"] == "iac-prepare-report"
    assert result["provider"] == "kubernetes"
    assert "deployment-contract" in step_names
    assert "kubernetes-generate" in step_names
    assert "kubernetes-e2e-plan" in step_names
    assert result["artifacts"]["prepare_json"] == f"work/{work_id}/process-report/iac-prepare-report.json"
    assert (tmp_path / "work" / work_id / "context" / "iac-deployment-contract.json").exists()
    assert (tmp_path / "work" / work_id / "implementation" / "kubernetes" / "manifests" / "deployment.yaml").exists()
    assert (tmp_path / "work" / work_id / "test-specifications" / "integration-test-plan.json").exists()


def test_iac_prepare_without_provider_stops_after_common_contract(tmp_path: Path) -> None:
    work_id = "issue-iac-prepare-none"
    requirement = tmp_path / "work" / work_id / "requirements" / "requirement.md"
    requirement.parent.mkdir(parents=True)
    requirement.write_text("web\nimage: ghcr.io/example/app:0.1.0\nport: 8080\n", encoding="utf-8")

    result = iac_prepare_runtime.build_prepare(tmp_path, work_id=work_id)

    step_names = [item["name"] for item in result["steps"]]
    assert result["provider"] == "none"
    assert "deployment-contract" in step_names
    assert "kubernetes-generate" not in step_names
    assert any("Provider-specific IaC was not detected" in item for item in result["next_actions"])


def test_aiwfctl_iac_prepare_routes(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    write_minimal_template_registries(repo_root)
    work_id = "issue-iac-prepare-cli"
    requirement = repo_root / "work" / work_id / "requirements" / "requirement.md"
    requirement.parent.mkdir(parents=True)
    requirement.write_text("k8s\nweb\nimage: ghcr.io/example/app:0.1.0\nport: 8080\n", encoding="utf-8")

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "iac",
            "prepare",
            "--work-id",
            work_id,
            "--json",
        ]
    )
    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["artifact_type"] == "iac-prepare-report"
    assert result["provider"] == "kubernetes"
    assert result["artifacts"]["prepare_json"] == f"work/{work_id}/process-report/iac-prepare-report.json"
