from __future__ import annotations

from pathlib import Path

from runtime.ctl import ctl
from runtime.workflow import iac_template


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_iac_template_list_includes_opentelemetry_collector() -> None:
    result = iac_template.list_templates(REPO_ROOT)

    templates = {item["name"]: item for item in result["templates"]}
    assert "opentelemetry-collector" in templates
    assert templates["opentelemetry-collector"]["exists"] is True


def test_iac_template_prepare_copies_opentelemetry_template(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-otel"

    result = iac_template.prepare_template(
        REPO_ROOT,
        template="opentelemetry-collector",
        work_id="issue-otel",
        work_dir=str(work_dir),
    )

    destination = work_dir / "source" / "infrastructure" / "opentelemetry-collector"
    assert result["artifact_type"] == "iac-template-setup-context"
    assert result["status"] == "copied"
    assert (destination / "README.md").exists()
    assert (destination / "config" / "base.yaml").exists()
    assert (destination / "scripts" / "otel_template.py").exists()
    assert (work_dir / "context" / "iac-template-context.json").exists()
    assert "iac-template-setup" in result["manifest_contexts"]


def test_iac_template_prepare_preserves_existing_copy_without_force(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-otel-existing"
    destination = work_dir / "source" / "infrastructure" / "opentelemetry-collector"
    destination.mkdir(parents=True)
    marker = destination / "local-marker.txt"
    marker.write_text("keep\n", encoding="utf-8")

    result = iac_template.prepare_template(
        REPO_ROOT,
        template="opentelemetry-collector",
        work_id="issue-otel-existing",
        work_dir=str(work_dir),
    )

    assert result["status"] == "existing"
    assert marker.read_text(encoding="utf-8") == "keep\n"


def test_iac_template_health_checks_copied_template(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-otel-health"
    iac_template.prepare_template(
        REPO_ROOT,
        template="opentelemetry-collector",
        work_id="issue-otel-health",
        work_dir=str(work_dir),
    )

    result = iac_template.health_template(
        REPO_ROOT,
        template="opentelemetry-collector",
        work_id="issue-otel-health",
        work_dir=str(work_dir),
    )

    assert result["artifact_type"] == "iac-template-health-context"
    assert result["status"] in {"ready", "warning"}
    assert all(check["status"] == "ready" for check in result["checks"])
    assert (work_dir / "context" / "iac-template-health-context.json").exists()
    assert (work_dir / "test-evidence" / "infrastructure" / "opentelemetry-collector" / "health-summary.md").exists()
    assert "iac-template-health" in result["manifest_contexts"]


def test_iac_template_tool_preflight_uses_terraform_env_path(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    terraform = tmp_path / "terraform.exe"
    terraform.write_text("", encoding="utf-8")
    (repo_root / ".env").write_text(f"AIWF_TERRAFORM_EXE={terraform}\n", encoding="utf-8")

    monkeypatch.setattr(iac_template.shutil, "which", lambda name: None)

    result = iac_template.tool_preflight(repo_root=repo_root)

    assert result["terraform"]["available"] is True
    assert result["terraform"]["path"] == str(terraform)
    assert result["docker"]["available"] is False


def test_aiwfctl_iac_template_prepare_and_health(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-otel-cli"

    prepare_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(REPO_ROOT),
            "iac",
            "template",
            "prepare",
            "--template",
            "opentelemetry-collector",
            "--work-id",
            "issue-otel-cli",
            "--work-dir",
            str(work_dir),
        ]
    )
    prepare_code, prepare_output = ctl.run(prepare_args)

    assert prepare_code == 0
    assert "IaC Template" in prepare_output
    assert (work_dir / "source" / "infrastructure" / "opentelemetry-collector").exists()

    health_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(REPO_ROOT),
            "iac",
            "template",
            "health",
            "--template",
            "opentelemetry-collector",
            "--work-id",
            "issue-otel-cli",
            "--work-dir",
            str(work_dir),
        ]
    )
    health_code, health_output = ctl.run(health_args)

    assert health_code == 0
    assert "IaC Template" in health_output
    assert "iac-template-health-context.json" in health_output
