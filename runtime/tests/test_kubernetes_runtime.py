from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl
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


def test_kubernetes_assessment_detects_k3s_and_required_gaps(tmp_path: Path) -> None:
    work_id = "issue-k3s"
    requirements = tmp_path / "work" / work_id / "requirements" / "requirement.md"
    requirements.parent.mkdir(parents=True)
    requirements.write_text(
        "\n".join(
            [
                "# Requirement",
                "",
                "k3s に配置する。",
                "service port: 8081",
                "readiness probe が必要。",
            ]
        ),
        encoding="utf-8",
    )

    assessment = kubernetes_runtime.build_compatibility_assessment(tmp_path, work_id=work_id)
    report = kubernetes_runtime.build_gap_report(tmp_path, work_id=work_id)

    assert assessment["target"] == "k3s"
    assert assessment["detected"]["port"] == 8081
    assert assessment["status"] == "compatible-with-gaps"
    assert "container_image" in assessment["missing_capabilities"]
    assert report["artifact_type"] == "kubernetes-gap-report"
    assert report["status"] == "generation-constrained"
    assert any(item["gap_id"] == "container-image-missing" for item in report["gaps"])
    assert (tmp_path / "work" / work_id / "context" / "kubernetes-compatibility-assessment.json").exists()
    assert (tmp_path / "work" / work_id / "process-report" / "kubernetes-gap-report.md").exists()


def test_kubernetes_generate_dry_run_e2e_and_evidence_flow(tmp_path: Path) -> None:
    work_id = "issue-k8s-flow"
    requirements = tmp_path / "work" / work_id / "requirements" / "requirement.md"
    requirements.parent.mkdir(parents=True)
    requirements.write_text(
        "\n".join(
            [
                "# Requirement",
                "",
                "Kubernetes に配置する。",
                "image: ghcr.io/example/app:0.1.0",
                "port: 8080",
                "resources limits と Secret boundary を定義する。",
                "Service は ClusterIP とする。",
            ]
        ),
        encoding="utf-8",
    )

    generation = kubernetes_runtime.build_manifest_generation(tmp_path, work_id=work_id)
    dry_run = kubernetes_runtime.build_dry_run_evidence(tmp_path, work_id=work_id)
    e2e_plan = kubernetes_runtime.build_kubernetes_e2e_plan(tmp_path, work_id=work_id)
    evidence = kubernetes_runtime.build_kubernetes_evidence(tmp_path, work_id=work_id)

    manifest_dir = tmp_path / "work" / work_id / "implementation" / "kubernetes" / "manifests"
    deployment = (manifest_dir / "deployment.yaml").read_text(encoding="utf-8")

    assert generation["status"] == "generated"
    assert generation["template"] == "kubernetes-app-template"
    assert generation["template_path"] == "templates/boilerplates/infrastructure/kubernetes-app-template"
    assert "ghcr.io/example/app:0.1.0" in deployment
    assert "containerPort: 8080" in deployment
    assert dry_run["status"] == "dry-run"
    assert dry_run["executed"] is False
    assert e2e_plan["artifact_type"] == "integration-test-plan"
    assert "kubectl apply --dry-run=client" in e2e_plan["commands"][0]
    assert evidence["artifact_type"] == "kubernetes-evidence"
    assert "assessment" in evidence["collected_artifacts"]
    assert (tmp_path / "work" / work_id / "test-evidence" / "kubernetes" / "dry-run.md").exists()


def test_kubernetes_generate_applies_allowed_spec_delta_only(tmp_path: Path) -> None:
    work_id = "issue-k8s-delta"
    requirements = tmp_path / "work" / work_id / "requirements" / "requirement.md"
    requirements.parent.mkdir(parents=True)
    requirements.write_text("k8s\nimage: ghcr.io/example/app:0.1.0\nport: 8080\n", encoding="utf-8")
    delta = tmp_path / "work" / work_id / "context" / "spec-delta.json"
    delta.parent.mkdir(parents=True, exist_ok=True)
    delta.write_text(
        json.dumps(
            {
                "namespace": "preview",
                "replicas": 2,
                "health_path": "/ready",
                "secret_value": "must-not-render",
            }
        ),
        encoding="utf-8",
    )

    result = kubernetes_runtime.build_manifest_generation(
        tmp_path,
        work_id=work_id,
        spec_delta=str(delta),
    )

    manifest_dir = tmp_path / "work" / work_id / "implementation" / "kubernetes" / "manifests"
    deployment = (manifest_dir / "deployment.yaml").read_text(encoding="utf-8")
    service = (manifest_dir / "service.yaml").read_text(encoding="utf-8")

    assert result["applied_values"]["namespace"] == "preview"
    assert result["applied_values"]["replicas"] == 2
    assert result["ignored_spec_delta_keys"] == ["secret_value"]
    assert "namespace: preview" in deployment
    assert "replicas: 2" in deployment
    assert "path: /ready" in deployment
    assert "must-not-render" not in deployment
    assert "namespace: preview" in service


def test_kubernetes_dry_run_execute_requires_human_check(monkeypatch, tmp_path: Path) -> None:
    work_id = "issue-k8s-human"
    kubernetes_runtime.build_manifest_generation(tmp_path, work_id=work_id)
    monkeypatch.setattr(kubernetes_runtime.shutil, "which", lambda name: "kubectl" if name == "kubectl" else None)
    monkeypatch.setattr(
        kubernetes_runtime.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("kubectl must not run without approval")),
    )

    result = kubernetes_runtime.build_dry_run_evidence(tmp_path, work_id=work_id, execute=True)

    assert result["status"] == "human-check-required"
    assert result["executed"] is False


def test_aiwfctl_iac_kubernetes_routes(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    write_minimal_template_registries(repo_root)
    work_id = "issue-k8s-cli"
    requirements = repo_root / "work" / work_id / "requirements" / "requirement.md"
    requirements.parent.mkdir(parents=True)
    requirements.write_text("k8s\nimage: ghcr.io/example/app:0.1.0\nport: 8080\n", encoding="utf-8")

    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "iac",
            "kubernetes",
            "generate",
            "--work-id",
            work_id,
            "--json",
        ]
    )
    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["artifact_type"] == "kubernetes-manifest-generation"
    assert result["artifacts"]["generation_json"] == f"work/{work_id}/context/kubernetes-manifest-generation.json"
    assert (repo_root / "work" / work_id / "implementation" / "kubernetes" / "manifests" / "deployment.yaml").exists()
