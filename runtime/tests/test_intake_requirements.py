from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.ctl import ctl
from runtime.intake import intake_requirements


def write_requirement(path: Path, repository: str = "owner/ariadne-target", branch: str = "main") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Requirement\n\nRepository: {repository}\nTarget Branch: {branch}\n",
        encoding="utf-8",
    )
    return path


def make_args(repo_root: Path, **overrides) -> argparse.Namespace:
    defaults = {
        "requirements": [],
        "requirements_dir": None,
        "receipt_id": "SYS-1000",
        "id_prefix": None,
        "project_name": "ariadne-target",
        "project_repository": "",
        "workflow": "ariadne-new-system-development",
        "phase": "intake",
        "intent_summary": "test intake",
        "risk_level": "unknown",
        "repo_root": str(repo_root),
        "copy": True,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_parser_and_workflow_mapping_helpers() -> None:
    parsed = intake_requirements.build_parser().parse_args(
        [
            "req.md",
            "--requirements-dir",
            "work/requirements",
            "--receipt-id",
            "WF-1",
            "--id-prefix",
            "CUSTOM",
            "--project-name",
            "Ariadne",
            "--project-repository",
            "owner/repo",
            "--workflow",
            "realtime-iac",
            "--phase",
            "design",
            "--intent-summary",
            "Build realtime infrastructure",
            "--risk-level",
            "critical",
            "--repo-root",
            ".",
            "--copy",
        ]
    )

    assert parsed.requirements == ["req.md"]
    assert parsed.workflow == "realtime-iac"
    assert parsed.risk_level == "critical"
    assert parsed.copy is True

    assert intake_requirements.command_for_workflow("ariadne-feature-maintenance-development") == "/ariadne-feature-maintenance-development"
    assert intake_requirements.command_for_workflow("ariadne-new-system-iac") == "/ariadne-new-system-iac"
    assert intake_requirements.command_for_workflow("realtime-iac") == "/realtime-iac"
    assert intake_requirements.command_for_workflow("github-knowledge-maintenance") == "/github-knowledge-maintenance"
    assert intake_requirements.command_for_workflow("ariadne-new-system-development") == "/ariadne-new-system-development"

    assert intake_requirements.id_prefix_for_workflow("ariadne-new-system-development") == "SYS"
    assert intake_requirements.id_prefix_for_workflow("ariadne-new-system-iac") == "SYS"
    assert intake_requirements.id_prefix_for_workflow("ariadne-feature-maintenance-development") == "FEAT"
    assert intake_requirements.id_prefix_for_workflow("realtime-iac") == "WF"

    assert "Port definition list is not confirmed at intake." in intake_requirements.open_questions_for_workflow("realtime-iac")
    assert "Shared Artifacts readiness for IaC handoff is not confirmed at intake." in intake_requirements.open_questions_for_workflow("ariadne-new-system-iac")
    assert "GitHub mutation approval is not confirmed at intake." in intake_requirements.open_questions_for_workflow("github-knowledge-maintenance")
    assert intake_requirements.open_questions_for_workflow("ariadne-new-system-development") == [
        "STOP / emergency stop behavior is not confirmed at intake.",
        "Communication loss behavior is not confirmed at intake.",
    ]

    assert intake_requirements.consumed_by_for_workflow("realtime-iac") == ["iac-requirements-agent"]
    assert "shared-artifact-validator-agent" in intake_requirements.consumed_by_for_workflow("ariadne-new-system-iac")
    assert "github-metadata-collector-agent" in intake_requirements.consumed_by_for_workflow("github-knowledge-maintenance")
    assert intake_requirements.consumed_by_for_workflow("ariadne-new-system-development") == ["ariadne-architect-agent"]


def test_discover_requirement_documents_rejects_invalid_inputs(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        intake_requirements.discover_requirement_documents(missing)

    file_path = tmp_path / "requirements.md"
    file_path.write_text("# not dir\n", encoding="utf-8")
    with pytest.raises(NotADirectoryError, match="not a directory"):
        intake_requirements.discover_requirement_documents(file_path)

    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "README.md").write_text("# guide\n", encoding="utf-8")
    (empty / "ignore.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no requirement documents"):
        intake_requirements.discover_requirement_documents(empty)

    multiple = tmp_path / "multiple"
    multiple.mkdir()
    write_requirement(multiple / "a.md")
    write_requirement(multiple / "b.txt")
    with pytest.raises(ValueError, match="multiple requirement documents"):
        intake_requirements.discover_requirement_documents(multiple)

    single = tmp_path / "single"
    single.mkdir()
    expected = write_requirement(single / "accepted.markdown")
    assert intake_requirements.discover_requirement_documents(single) == [expected]


def test_repository_control_and_unique_destination(tmp_path: Path) -> None:
    missing_repo = tmp_path / "missing-repo.md"
    missing_repo.write_text("# Requirement\n\nTarget Branch: main\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Repository Control is missing"):
        intake_requirements.validate_repository_control([missing_repo])

    owner_repo = tmp_path / "owner-repo.md"
    owner_repo.write_text(
        "# Requirement\n\nGitHub Owner: octo\nGitHub Repository: robot\nBranch: develop\n",
        encoding="utf-8",
    )
    assert intake_requirements.validate_repository_control([owner_repo]) == {
        "repository": "octo/robot",
        "target_branch": "develop",
    }

    destination_dir = tmp_path / "dest"
    destination_dir.mkdir()
    (destination_dir / "req.md").write_text("first\n", encoding="utf-8")
    (destination_dir / "req-2.md").write_text("second\n", encoding="utf-8")
    assert intake_requirements.unique_destination(destination_dir, "req.md") == destination_dir / "req-3.md"


def test_initialize_context_and_manifest_registration(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "WF-1"
    (work_dir / "context").mkdir(parents=True)

    intake_requirements.initialize_context(
        repo_root=tmp_path,
        work_dir=work_dir,
        receipt_id="WF-1",
        project_name="Realtime",
        project_repository="owner/realtime",
        workflow="realtime-iac",
        phase="intake",
        intent_summary="Prepare realtime IaC",
        risk_level="high",
    )
    intake_requirements.register_initial_context_manifest(tmp_path, work_dir, "WF-1")

    context_dir = work_dir / "context"
    agent_context = json.loads((context_dir / "agent-context.json").read_text(encoding="utf-8"))
    handoff = json.loads((context_dir / "handoff-package.json").read_text(encoding="utf-8"))
    manifest = json.loads((context_dir / "context-manifest.json").read_text(encoding="utf-8"))

    assert agent_context["workflow"]["command"] == "/realtime-iac"
    assert agent_context["project"]["repository"] == "owner/realtime"
    assert "Port definition list is not confirmed at intake." in agent_context["safety_context"]["open_safety_questions"]
    assert handoff["required_next_actions"][0] == "Review requirement documents."
    assert {"agent-context", "artifact-index", "handoff-package", "qa-records"} <= {
        item["type"] for item in manifest["contexts"]
    }


def test_run_with_explicit_requirements_copies_and_uses_unique_names(tmp_path: Path) -> None:
    source_a = write_requirement(tmp_path / "incoming-a" / "requirements.md")
    source_b = write_requirement(tmp_path / "incoming-b" / "requirements.md")
    design_dir = tmp_path / "work" / "GITHUB-1" / "design-document"
    design_dir.mkdir(parents=True)
    (design_dir / "requirements.md").write_text("existing\n", encoding="utf-8")

    result = intake_requirements.run(
        make_args(
            tmp_path,
            requirements=[str(source_a), str(source_b)],
            requirements_dir=None,
            receipt_id="GITHUB-1",
            workflow="github-knowledge-maintenance",
            project_repository="override/repo",
            copy=True,
        )
    )

    assert result["receipt_id"] == "GITHUB-1"
    assert result["repository"] == "owner/ariadne-target"
    assert result["target_branch"] == "main"
    assert result["copied"] is True
    assert result["requirements_dir"] is None
    assert source_a.exists()
    assert source_b.exists()
    assert (design_dir / "requirements.md").read_text(encoding="utf-8") == "existing\n"
    assert (design_dir / "requirements-2.md").exists()
    assert (design_dir / "requirements-3.md").exists()

    context_dir = tmp_path / "work" / "GITHUB-1" / "context"
    agent_context = json.loads((context_dir / "agent-context.json").read_text(encoding="utf-8"))
    artifact_index = json.loads((context_dir / "artifact-index.json").read_text(encoding="utf-8"))
    handoff = json.loads((context_dir / "handoff-package.json").read_text(encoding="utf-8"))

    assert agent_context["project"]["repository"] == "override/repo"
    assert artifact_index["artifacts"][0]["consumed_by"] == intake_requirements.consumed_by_for_workflow(
        "github-knowledge-maintenance"
    )
    assert handoff["artifacts"] == result["accepted_files"]


def test_run_discovers_single_requirement_moves_and_generates_receipt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    requirements_dir = tmp_path / "work" / "requirements"
    requirement = write_requirement(requirements_dir / "maintenance.txt", repository="owner/maint", branch="feature/base")
    monkeypatch.setattr(intake_requirements, "make_receipt_id", lambda prefix: f"{prefix}-AUTO")

    result = intake_requirements.run(
        make_args(
            tmp_path,
            requirements=[],
            requirements_dir=str(requirements_dir),
            receipt_id=None,
            id_prefix=None,
            workflow="ariadne-feature-maintenance-development",
            project_name="Maint",
            copy=False,
        )
    )

    assert result["receipt_id"] == "FEAT-AUTO"
    assert result["repository"] == "owner/maint"
    assert result["target_branch"] == "feature/base"
    assert result["copied"] is False
    assert result["requirements_dir"] == "work/requirements"
    assert not requirement.exists()
    assert (tmp_path / "work" / "FEAT-AUTO" / "design-document" / "maintenance.txt").exists()


def test_run_rejects_missing_explicit_requirement(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Requirement document not found"):
        intake_requirements.run(
            make_args(
                tmp_path,
                requirements=[str(tmp_path / "missing.md")],
                receipt_id="SYS-MISSING",
            )
        )


def test_ctl_intake_run_accepts_requirement_document(tmp_path: Path) -> None:
    requirement = write_requirement(tmp_path / "work" / "requirements" / "requirements.md", repository="owner/ctl")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "intake",
            "run",
            "--receipt-id",
            "SYS-CTL",
            "--project-name",
            "Ctl Intake",
            "--copy",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    assert "Requirement Intake" in output
    assert "Receipt : SYS-CTL" in output
    assert requirement.exists()
    assert (tmp_path / "work" / "SYS-CTL" / "design-document" / "requirements.md").exists()
    assert (tmp_path / "work" / "SYS-CTL" / "context" / "context-manifest.json").exists()
    log_path = tmp_path / "logs" / "runtime" / "runtime-events.log"
    completed = json.loads(log_path.read_text(encoding="utf-8").splitlines()[-1].split(" | ", 3)[3])
    assert completed["command"] == "intake run"
    assert completed["operation_id"] == "intake:run"


def test_ctl_intake_run_outputs_json(tmp_path: Path) -> None:
    requirement = write_requirement(tmp_path / "incoming" / "requirements.md", repository="owner/json")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "intake",
            "run",
            str(requirement),
            "--receipt-id",
            "SYS-JSON",
            "--copy",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["receipt_id"] == "SYS-JSON"
    assert result["repository"] == "owner/json"
    assert result["accepted_files"] == ["work/SYS-JSON/design-document/requirements.md"]


def test_main_outputs_json_and_reports_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    requirement = write_requirement(tmp_path / "req.md")

    code = intake_requirements.main(
        [
            str(requirement),
            "--repo-root",
            str(tmp_path),
            "--receipt-id",
            "SYS-MAIN",
            "--project-name",
            "Main",
            "--copy",
        ]
    )
    stdout = capsys.readouterr().out

    assert code == 0
    assert '"receipt_id": "SYS-MAIN"' in stdout

    def raise_error(args):
        raise RuntimeError("boom")

    monkeypatch.setattr(intake_requirements, "run", raise_error)
    assert intake_requirements.main([str(requirement), "--repo-root", str(tmp_path)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(intake_requirements.__file__)))
    assert namespace["build_parser"]
