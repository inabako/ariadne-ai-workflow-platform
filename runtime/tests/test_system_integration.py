from __future__ import annotations

import json
from pathlib import Path

from runtime import ctl
from runtime.workflow import system_integration


def write_sdk_context(work_dir: Path) -> None:
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    (context_dir / "sdk-analysis-context.json").write_text(
        json.dumps(
            {
                "artifact_type": "sdk-analysis-context",
                "status": "available",
                "cloud": {
                    "provider": "multiple",
                    "providers": ["aws", "gcp"],
                    "services": ["s3", "pubsub", "unknown-service"],
                },
                "payment": {
                    "vendor": "stripe",
                    "vendors": ["stripe"],
                    "services": ["webhooks"],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def write_target_repo(target: Path) -> None:
    (target / "src" / "adapters").mkdir(parents=True)
    (target / "src" / "ports").mkdir(parents=True)
    (target / "tests").mkdir(parents=True)
    (target / "docs" / "evidence").mkdir(parents=True)
    (target / ".env.example").write_text("AWS_REGION=ap-northeast-1\n", encoding="utf-8")
    (target / "pyproject.toml").write_text("[project]\nname='target'\n", encoding="utf-8")
    (target / "src" / "adapters" / "cloud_adapter.py").write_text("# adapter\n", encoding="utf-8")
    (target / "src" / "ports" / "cloud_port.py").write_text("# port\n", encoding="utf-8")
    (target / "tests" / "test_cloud_adapter.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")


def test_system_integration_analyze_registers_context_and_emulator_candidates(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_dir = repo_root / "work" / "issue-123"
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)

    result = system_integration.build_context(repo_root, command="analyze", work_id="issue-123")

    assert result["artifact_type"] == "system-integration-context"
    assert result["target_system"]["exists"] is True
    assert result["cloud"]["provider"] == "multiple"
    assert result["payment"]["vendor"] == "stripe"
    assert any(item["provider"] == "aws" for item in result["emulator_candidates"])
    assert any(item["provider"] == "gcp" for item in result["emulator_candidates"])
    assert any(item["provider"] == "stripe" for item in result["emulator_candidates"])
    assert any(item["template_path"] == "templates/boilerplates/integration/cloud-emulators/localstack" for item in result["emulator_candidates"])
    assert any(item["template_path"] == "templates/boilerplates/integration/cloud-emulators/gcp-emulators" for item in result["emulator_candidates"])
    assert any(item["template_path"] == "templates/boilerplates/integration/cloud-emulators/stripe-cli" for item in result["emulator_candidates"])
    assert "system-integration" in result["manifest_contexts"]
    assert (work_dir / "reports" / "system-integration-report.md").exists()
    assert (work_dir / "context" / "integration-context.json").exists()


def test_system_integration_verify_with_emulator_classifies_coverage(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_dir = repo_root / "work" / "issue-456"
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)

    result = system_integration.build_context(repo_root, command="verify", work_id="issue-456", with_emulator=True)

    scopes = [
        scope
        for candidate in result["emulator_candidates"]
        for scope in candidate["verification_scope"]
    ]
    assert any(scope["service"] == "s3" and scope["classification"] == "emulator_verified" for scope in scopes)
    assert any(scope["service"] == "pubsub" and scope["classification"] == "emulator_verified" for scope in scopes)
    assert any(scope["service"] == "unknown-service" and scope["classification"] == "real_cloud_verification_required" for scope in scopes)
    assert result["verification"]["mode"] == "with-emulator"
    assert result["verification"]["evidence_status"] == "available"


def test_aiwfctl_integration_verify_command(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    (repo_root / "runtime" / "registries").mkdir(parents=True)
    (repo_root / "runtime" / "registries" / "workflow_help.json").write_text(
        '{"commands": [], "extensions": []}',
        encoding="utf-8",
    )
    work_dir = repo_root / "work" / "issue-789"
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)

    args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "integration", "verify", "--work-id", "issue-789", "--with-emulator"]
    )
    code, output = ctl.run(args)

    assert code in {0, 2}
    assert "System Integration Quality" in output
    assert "work/issue-789/context/integration-context.json" in output


def test_system_integration_emulator_prepare_copies_templates_and_context(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    work_id = "issue-emulator-prepare"
    work_dir = tmp_path / "work" / work_id
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)

    result = system_integration.prepare_emulator(
        repo_root,
        work_id=work_id,
        work_dir=str(work_dir),
        target_repo=str(target),
    )

    assert result["artifact_type"] == "emulator-setup-context"
    assert result["status"] == "prepared"
    assert {item["provider"] for item in result["prepared"]} == {"aws", "gcp", "stripe"}
    assert (work_dir / "test-environment" / "emulator" / "localstack" / "docker-compose.yml").exists()
    assert (work_dir / "test-environment" / "emulator" / "gcp-emulators" / "docker-compose.yml").exists()
    assert (work_dir / "test-environment" / "emulator" / "stripe-cli" / "docker-compose.yml").exists()
    assert (work_dir / "test-evidence" / "emulator" / "aws").exists()
    assert (work_dir / "context" / "emulator-context.json").exists()
    assert "emulator-setup" in result["manifest_contexts"]


def test_system_integration_emulator_prepare_does_not_overwrite_without_force(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    work_id = "issue-emulator-existing"
    work_dir = tmp_path / "work" / work_id
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)
    existing = work_dir / "test-environment" / "emulator" / "localstack"
    existing.mkdir(parents=True)
    marker = existing / "local-only.txt"
    marker.write_text("keep me\n", encoding="utf-8")

    result = system_integration.prepare_emulator(
        repo_root,
        work_id=work_id,
        work_dir=str(work_dir),
        target_repo=str(target),
    )

    localstack = next(item for item in result["prepared"] if item["provider"] == "aws")
    assert localstack["status"] == "existing"
    assert marker.read_text(encoding="utf-8") == "keep me\n"


def test_aiwfctl_integration_emulator_prepare_command(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    (repo_root / "runtime" / "registries").mkdir(parents=True)
    (repo_root / "runtime" / "registries" / "workflow_help.json").write_text(
        '{"commands": [], "extensions": []}',
        encoding="utf-8",
    )
    source_templates = Path(__file__).resolve().parents[2] / "templates" / "boilerplates" / "integration" / "cloud-emulators"
    destination_templates = repo_root / "templates" / "boilerplates" / "integration" / "cloud-emulators"
    for template in ["localstack", "gcp-emulators", "stripe-cli"]:
        (destination_templates / template).mkdir(parents=True)
        (destination_templates / template / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
    assert source_templates.exists()
    work_id = "issue-emulator-cli"
    work_dir = repo_root / "work" / work_id
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)

    args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "integration", "emulator", "prepare", "--work-id", work_id]
    )
    code, output = ctl.run(args)

    assert code == 0
    assert "System Integration Emulator Prepare" in output
    assert f"work/{work_id}/context/emulator-context.json" in output
    assert (work_dir / "test-environment" / "emulator" / "localstack" / "docker-compose.yml").exists()


def test_system_integration_emulator_health_checks_prepared_templates(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    work_id = "issue-emulator-health"
    work_dir = tmp_path / "work" / work_id
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)
    system_integration.prepare_emulator(
        repo_root,
        work_id=work_id,
        work_dir=str(work_dir),
        target_repo=str(target),
    )

    result = system_integration.emulator_health(repo_root, work_id=work_id, work_dir=str(work_dir))

    assert result["artifact_type"] == "emulator-health-context"
    assert result["status"] in {"ready", "warning", "human-check-required"}
    assert {item["provider"] for item in result["checks"]} == {"aws", "gcp", "stripe"}
    assert all(item["destination_exists"] for item in result["checks"])
    assert all(item["evidence_dir_exists"] for item in result["checks"])
    assert all(item["files"]["compose_file"] for item in result["checks"])
    assert all(item["files"]["env_example"] for item in result["checks"])
    assert all(item["files"]["readme"] for item in result["checks"])
    assert all(item["files"]["health_doc"] for item in result["checks"])
    assert "emulator-health" in result["manifest_contexts"]
    assert (work_dir / "context" / "emulator-health-context.json").exists()
    assert (work_dir / "test-evidence" / "emulator" / "health-summary.md").exists()


def test_system_integration_emulator_health_reports_missing_setup(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-emulator-health-missing"
    work_dir = repo_root / "work" / work_id

    result = system_integration.emulator_health(repo_root, work_id=work_id)

    assert result["artifact_type"] == "emulator-health-context"
    assert result["status"] == "human-check-required"
    assert result["checks"] == []
    assert any("emulator-context.json" in item for item in result["human_checks"])
    assert (work_dir / "context" / "emulator-health-context.json").exists()
    assert (work_dir / "test-evidence" / "emulator" / "health-summary.md").exists()


def test_aiwfctl_integration_emulator_health_command(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    (repo_root / "runtime" / "registries").mkdir(parents=True)
    (repo_root / "runtime" / "registries" / "workflow_help.json").write_text(
        '{"commands": [], "extensions": []}',
        encoding="utf-8",
    )
    destination_templates = repo_root / "templates" / "boilerplates" / "integration" / "cloud-emulators"
    for template, health_doc in {
        "localstack": "healthcheck.md",
        "gcp-emulators": "healthcheck.md",
        "stripe-cli": "webhook-test.md",
    }.items():
        template_dir = destination_templates / template
        template_dir.mkdir(parents=True)
        (template_dir / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
        (template_dir / ".env.example").write_text("EXAMPLE=true\n", encoding="utf-8")
        (template_dir / "README.md").write_text("# template\n", encoding="utf-8")
        (template_dir / health_doc).write_text("# health\n", encoding="utf-8")
    work_id = "issue-emulator-health-cli"
    work_dir = repo_root / "work" / work_id
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)
    prepare_args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "integration", "emulator", "prepare", "--work-id", work_id]
    )
    prepare_code, _ = ctl.run(prepare_args)
    assert prepare_code == 0

    args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "integration", "emulator", "health", "--work-id", work_id]
    )
    code, output = ctl.run(args)

    assert code in {0, 2}
    assert "System Integration Emulator Health" in output
    assert f"work/{work_id}/context/emulator-health-context.json" in output
    assert (work_dir / "context" / "emulator-health-context.json").exists()
    assert (work_dir / "test-evidence" / "emulator" / "health-summary.md").exists()


def test_system_integration_test_plan_creates_runbook_and_manifest(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    work_id = "issue-integration-test-plan"
    work_dir = tmp_path / "work" / work_id
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)
    system_integration.build_context(
        repo_root,
        command="verify",
        work_id=work_id,
        work_dir=str(work_dir),
        target_repo=str(target),
        with_emulator=True,
    )
    system_integration.prepare_emulator(
        repo_root,
        work_id=work_id,
        work_dir=str(work_dir),
        target_repo=str(target),
    )
    system_integration.emulator_health(repo_root, work_id=work_id, work_dir=str(work_dir))

    result = system_integration.integration_test_plan(
        repo_root,
        work_id=work_id,
        work_dir=str(work_dir),
        target_repo=str(target),
    )

    assert result["artifact_type"] == "integration-test-plan-context"
    assert result["status"] in {"planned", "human-check-required"}
    assert [phase["id"] for phase in result["phases"]] == [
        "environment-setup",
        "external-dependency-start",
        "health-check",
        "seed-data",
        "target-system-start",
        "normal-path",
        "error-path",
        "logs-data-check",
        "cleanup",
    ]
    assert any(phase["human_check_required"] for phase in result["phases"])
    assert result["rules"]["do_not_start_emulator_in_plan"] is True
    assert "integration-test-plan" in result["manifest_contexts"]
    assert (work_dir / "context" / "integration-test-plan-context.json").exists()
    assert (work_dir / "test-evidence" / "integration-test" / "integration-test-runbook.md").exists()


def test_system_integration_test_plan_requires_prior_contexts(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-integration-test-plan-missing"
    work_dir = repo_root / "work" / work_id

    result = system_integration.integration_test_plan(repo_root, work_id=work_id)

    assert result["artifact_type"] == "integration-test-plan-context"
    assert result["status"] == "human-check-required"
    assert any("integration-context.json" in item for item in result["human_checks"])
    assert any("emulator-health-context.json" in item for item in result["human_checks"])
    assert (work_dir / "context" / "integration-test-plan-context.json").exists()
    assert (work_dir / "test-evidence" / "integration-test" / "integration-test-runbook.md").exists()


def test_aiwfctl_integration_test_plan_command(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    (repo_root / "runtime" / "registries").mkdir(parents=True)
    (repo_root / "runtime" / "registries" / "workflow_help.json").write_text(
        '{"commands": [], "extensions": []}',
        encoding="utf-8",
    )
    destination_templates = repo_root / "templates" / "boilerplates" / "integration" / "cloud-emulators"
    for template, health_doc in {
        "localstack": "healthcheck.md",
        "gcp-emulators": "healthcheck.md",
        "stripe-cli": "webhook-test.md",
    }.items():
        template_dir = destination_templates / template
        template_dir.mkdir(parents=True)
        (template_dir / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
        (template_dir / ".env.example").write_text("EXAMPLE=true\n", encoding="utf-8")
        (template_dir / "README.md").write_text("# template\n", encoding="utf-8")
        (template_dir / health_doc).write_text("# health\n", encoding="utf-8")
    work_id = "issue-integration-test-plan-cli"
    work_dir = repo_root / "work" / work_id
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)
    verify_args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "integration", "verify", "--work-id", work_id, "--with-emulator"]
    )
    verify_code, _ = ctl.run(verify_args)
    assert verify_code in {0, 2}
    prepare_args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "integration", "emulator", "prepare", "--work-id", work_id]
    )
    prepare_code, _ = ctl.run(prepare_args)
    assert prepare_code == 0
    health_args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "integration", "emulator", "health", "--work-id", work_id]
    )
    health_code, _ = ctl.run(health_args)
    assert health_code in {0, 2}

    args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "integration", "test-plan", "--work-id", work_id]
    )
    code, output = ctl.run(args)

    assert code in {0, 2}
    assert "System Integration Test Plan" in output
    assert f"work/{work_id}/context/integration-test-plan-context.json" in output
    assert (work_dir / "context" / "integration-test-plan-context.json").exists()
    assert (work_dir / "test-evidence" / "integration-test" / "integration-test-runbook.md").exists()


def test_system_integration_finalize_collects_evidence_and_report(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    work_id = "issue-integration-finalize"
    work_dir = tmp_path / "work" / work_id
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)
    system_integration.build_context(
        repo_root,
        command="verify",
        work_id=work_id,
        work_dir=str(work_dir),
        target_repo=str(target),
        with_emulator=True,
    )
    system_integration.prepare_emulator(repo_root, work_id=work_id, work_dir=str(work_dir), target_repo=str(target))
    system_integration.emulator_health(repo_root, work_id=work_id, work_dir=str(work_dir))
    system_integration.integration_test_plan(repo_root, work_id=work_id, work_dir=str(work_dir), target_repo=str(target))
    evidence_dir = work_dir / "test-evidence" / "integration-test"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "unit-pytest.log").write_text("pytest passed\n", encoding="utf-8")
    (evidence_dir / "integration-test-result.md").write_text("# Integration Test\npassed\n", encoding="utf-8")
    (evidence_dir / "regression-report.md").write_text("# Regression\npassed\n", encoding="utf-8")

    result = system_integration.finalize_integration(
        repo_root,
        work_id=work_id,
        work_dir=str(work_dir),
        target_repo=str(target),
    )

    assert result["artifact_type"] == "integration-finalization-context"
    assert result["status"] in {"complete", "complete-with-warnings", "incomplete", "human-check-required"}
    assert any(item["path"].endswith("integration-test-result.md") for item in result["evidence_files"])
    assert any(item["id"] == "integration-test" and item["status"] == "pass" for item in result["completion_checks"])
    assert result["rules"]["do_not_execute_tests_in_finalize"] is True
    assert "integration-finalization" in result["manifest_contexts"]
    assert (work_dir / "context" / "integration-finalization-context.json").exists()
    assert (work_dir / "reports" / "system-integration-final-report.md").exists()


def test_system_integration_finalize_requires_prior_contexts(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-integration-finalize-missing"
    work_dir = repo_root / "work" / work_id

    result = system_integration.finalize_integration(repo_root, work_id=work_id)

    assert result["artifact_type"] == "integration-finalization-context"
    assert result["status"] == "human-check-required"
    assert any("integration-context.json" in item for item in result["human_checks"])
    assert any("emulator-health-context.json" in item for item in result["human_checks"])
    assert any("integration-test-plan-context.json" in item for item in result["human_checks"])
    assert (work_dir / "context" / "integration-finalization-context.json").exists()
    assert (work_dir / "reports" / "system-integration-final-report.md").exists()


def test_aiwfctl_integration_finalize_command(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    (repo_root / "runtime" / "registries").mkdir(parents=True)
    (repo_root / "runtime" / "registries" / "workflow_help.json").write_text(
        '{"commands": [], "extensions": []}',
        encoding="utf-8",
    )
    destination_templates = repo_root / "templates" / "boilerplates" / "integration" / "cloud-emulators"
    for template, health_doc in {
        "localstack": "healthcheck.md",
        "gcp-emulators": "healthcheck.md",
        "stripe-cli": "webhook-test.md",
    }.items():
        template_dir = destination_templates / template
        template_dir.mkdir(parents=True)
        (template_dir / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
        (template_dir / ".env.example").write_text("EXAMPLE=true\n", encoding="utf-8")
        (template_dir / "README.md").write_text("# template\n", encoding="utf-8")
        (template_dir / health_doc).write_text("# health\n", encoding="utf-8")
    work_id = "issue-integration-finalize-cli"
    work_dir = repo_root / "work" / work_id
    target = work_dir / "source" / "repository"
    write_sdk_context(work_dir)
    write_target_repo(target)
    for command in [
        ["integration", "verify", "--work-id", work_id, "--with-emulator"],
        ["integration", "emulator", "prepare", "--work-id", work_id],
        ["integration", "emulator", "health", "--work-id", work_id],
        ["integration", "test-plan", "--work-id", work_id],
    ]:
        args = ctl.build_parser().parse_args(["--repo-root", str(repo_root), *command])
        code, _ = ctl.run(args)
        assert code in {0, 2}
    evidence_dir = work_dir / "test-evidence" / "integration-test"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "integration-test-result.md").write_text("# Integration Test\npassed\n", encoding="utf-8")

    args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "integration", "finalize", "--work-id", work_id]
    )
    code, output = ctl.run(args)

    assert code in {0, 2}
    assert "System Integration Finalization" in output
    assert f"work/{work_id}/context/integration-finalization-context.json" in output
    assert (work_dir / "context" / "integration-finalization-context.json").exists()
    assert (work_dir / "reports" / "system-integration-final-report.md").exists()
