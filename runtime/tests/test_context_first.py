from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.intake import intake_requirements
from runtime.rag import rag_build
from runtime.workflow import context_first
from runtime.workflow import (
    corrective_action_report,
    dispatcher_context,
    docs_sync,
    gui_mode,
    github_knowledge_maintenance,
    iac_handoff_context,
    init_corrective_action_fix,
    knowledge_capture,
    vscode_environment,
    web_svg_layout_mode,
)


def test_context_manifest_registers_dispatcher_context(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_dir = repo_root / "work" / "issue-123"
    context_path = work_dir / "context" / "environment-selection.json"
    context_path.parent.mkdir(parents=True)
    context_path.write_text("{}", encoding="utf-8")

    manifest = context_first.register_context(
        repo_root,
        work_dir,
        work_id="issue-123",
        context_type="environment-selection",
        path=context_path,
        required=True,
        generated_by="environment-dispatcher",
        owner="dispatcher",
        schema=".github/schemas/environment-selection.schema.json",
    )

    assert manifest["artifact_type"] == "context-manifest"
    assert manifest["architecture"] == "context-first"
    assert manifest["rules"]["dispatcher_contexts_are_authoritative"] is True
    assert manifest["contexts"] == [
        {
            "type": "environment-selection",
            "path": "work/issue-123/context/environment-selection.json",
            "required": True,
            "generated_by": "environment-dispatcher",
            "owner": "dispatcher",
            "schema": ".github/schemas/environment-selection.schema.json",
            "status": "available",
            "updated_at": manifest["contexts"][0]["updated_at"],
        }
    ]


def test_context_first_require_reports_missing_dispatcher_context(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-123"
    work_dir.mkdir(parents=True)
    args = argparse.Namespace(repo_root=str(tmp_path), work_dir=str(work_dir), context=["environment-selection"])

    result = context_first.run_require(args)

    assert result["status"] == "human-check-required"
    assert result["human_check_required"] is True
    assert result["missing"] == ["environment-selection"]


def test_context_first_require_passes_when_context_exists(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_dir = repo_root / "work" / "issue-123"
    context_path = work_dir / "context" / "environment-selection.json"
    context_path.parent.mkdir(parents=True)
    context_path.write_text("{}", encoding="utf-8")
    context_first.register_context(
        repo_root,
        work_dir,
        work_id="issue-123",
        context_type="environment-selection",
        path=context_path,
        required=True,
        generated_by="environment-dispatcher",
        owner="dispatcher",
        schema=".github/schemas/environment-selection.schema.json",
    )
    args = argparse.Namespace(repo_root=str(repo_root), work_dir=str(work_dir), context=["environment-selection"])

    result = context_first.run_require(args)

    assert result["status"] == "ready"
    assert result["human_check_required"] is False
    assert result["missing"] == []


def test_context_first_loads_test_evidence_context(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_dir = repo_root / "work" / "issue-123"
    report = work_dir / "context" / "pytest-ut-spec-sync-report.json"
    report.parent.mkdir(parents=True)
    report.write_text('{"status": "ok", "artifact_type": "pytest-ut-spec-sync-report"}', encoding="utf-8")
    context_first.register_context(
        repo_root,
        work_dir,
        work_id="issue-123",
        context_type="test-evidence",
        path=report,
        required=True,
        generated_by="pytest-ut-spec-sync",
        owner="workflow",
        schema=".github/schemas/pytest-ut-spec-sync-report.schema.json",
    )

    evidence = context_first.load_test_evidence_context(repo_root, work_dir)

    assert evidence["status"] == "available"
    assert evidence["count"] == 1
    assert evidence["items"][0]["payload"]["artifact_type"] == "pytest-ut-spec-sync-report"


def test_context_first_parser_show_and_main_status_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    parser = context_first.build_parser()
    parsed_show = parser.parse_args(["--repo-root", str(tmp_path), "--work-dir", "work/issue-1", "show"])
    parsed_require = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "--work-dir",
            "work/issue-1",
            "require",
            "--context",
            "workflow-selection",
            "--context",
            "runtime-context",
        ]
    )
    parsed_environment = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "--work-dir",
            "work/issue-1",
            "require-environment",
            "--environment",
            "docker",
        ]
    )

    assert parsed_show.command == "show"
    assert parsed_require.context == ["workflow-selection", "runtime-context"]
    assert parsed_environment.environment == "docker"

    missing = context_first.run_show(parsed_show)
    assert missing["status"] == "missing"
    assert missing["manifest"]["artifact_type"] == "context-manifest"

    context_dir = tmp_path / "work" / "issue-1" / "context"
    context_dir.mkdir(parents=True)
    (context_dir / "context-manifest.json").write_text(json.dumps({"contexts": []}), encoding="utf-8")
    existing = context_first.run_show(parsed_show)
    assert existing["status"] == "ok"

    monkeypatch.setattr(context_first, "run_show", lambda args: {"status": "ready"})
    assert context_first.main(["--repo-root", str(tmp_path), "--work-dir", "work/issue-1", "show"]) == 0
    assert '"status": "ready"' in capsys.readouterr().out

    monkeypatch.setattr(context_first, "run_show", lambda args: {"status": "human-check-required"})
    assert context_first.main(["--repo-root", str(tmp_path), "--work-dir", "work/issue-1", "show"]) == 2

    def raise_error(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(context_first, "run_show", raise_error)
    assert context_first.main(["--repo-root", str(tmp_path), "--work-dir", "work/issue-1", "show"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err


def test_context_first_require_environment_rejects_missing_entry_after_status_ready(
    tmp_path: Path,
    monkeypatch,
) -> None:
    work_dir = tmp_path / "work" / "issue-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    (context_dir / "context-manifest.json").write_text(
        json.dumps(
            {
                "artifact_type": "context-manifest",
                "contexts": [
                    {
                        "type": "environment-selection",
                        "path": "work/issue-9001/context/environment-selection.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(context_first, "context_entry", lambda manifest, context_type: None)

    with pytest.raises(RuntimeError, match="context entry was not found"):
        context_first.require_environment_selection(
            tmp_path,
            work_dir,
            expected_environment="docker",
        )


def test_context_first_require_environment_rejects_invalid_selection_document(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    selection_path = context_dir / "environment-selection.json"
    selection_path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
    context_first.register_context(
        tmp_path,
        work_dir,
        work_id="issue-9001",
        context_type="environment-selection",
        path=selection_path,
        required=True,
        generated_by="environment-dispatcher",
        owner="dispatcher",
        schema=".github/schemas/environment-selection.schema.json",
    )

    with pytest.raises(RuntimeError, match="invalid environment-selection context"):
        context_first.require_environment_selection(
            tmp_path,
            work_dir,
            expected_environment="docker",
        )


def test_context_first_module_can_be_loaded_as_script_path() -> None:
    namespace = runpy.run_path(str(Path(context_first.__file__)))

    assert namespace["build_parser"]


def test_requirement_intake_registers_context_manifest(tmp_path: Path) -> None:
    requirements_dir = tmp_path / "work" / "requirements"
    requirements_dir.mkdir(parents=True)
    (requirements_dir / "requirements.md").write_text(
        "# Requirement\n\nRepository: owner/ariadne-target\nTarget Branch: main\n",
        encoding="utf-8",
    )

    args = argparse.Namespace(
        requirements=[],
        requirements_dir=str(requirements_dir),
        receipt_id="SYS-9001",
        id_prefix=None,
        project_name="ariadne-target",
        project_repository="",
        workflow="ariadne-new-system-development",
        phase="intake",
        intent_summary="test intake",
        risk_level="unknown",
        repo_root=str(tmp_path),
        copy=True,
    )

    intake_requirements.run(args)

    manifest = json.loads(
        (tmp_path / "work" / "SYS-9001" / "context" / "context-manifest.json").read_text(encoding="utf-8")
    )
    context_types = {item["type"] for item in manifest["contexts"]}
    assert {"agent-context", "artifact-index", "handoff-package", "test-evidence"} <= context_types


def test_corrective_action_fix_init_registers_context_manifest(tmp_path: Path) -> None:
    args = argparse.Namespace(
        repository="owner/ariadne-target",
        target_branch="feature/issue-9001",
        work_id="issue-9001",
        base_work_id="",
        reuse_existing=False,
        report_path="",
        intent_summary="",
        repo_root=str(tmp_path),
    )

    init_corrective_action_fix.run(args)

    manifest = json.loads(
        (tmp_path / "work" / "issue-9001" / "context" / "context-manifest.json").read_text(encoding="utf-8")
    )
    context_types = {item["type"] for item in manifest["contexts"]}
    assert {"agent-context", "artifact-index", "handoff-package", "test-evidence"} <= context_types


def test_vscode_environment_init_registers_context_manifest(tmp_path: Path) -> None:
    args = argparse.Namespace(
        work_id="vscode-environment",
        target_dir="",
        mode="self-provision",
        repo_root=str(tmp_path),
        reuse_existing=False,
    )

    vscode_environment.init_work(args)

    manifest = json.loads(
        (tmp_path / "work" / "vscode-environment" / "context" / "context-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    context_types = {item["type"] for item in manifest["contexts"]}
    assert {"vscode-environment-state", "runtime-context"} <= context_types
    assert (tmp_path / "work" / "vscode-environment" / "context" / "runtime-context.json").exists()


def test_gui_mode_requires_environment_selection_before_run(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "SYS-9001"
    work_dir.mkdir(parents=True)
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_dir=None,
        issue_id="SYS-9001",
        mode="auto",
        force=False,
        svg_input_dir=None,
        input_prefix=None,
        skip_context_check=False,
    )

    try:
        gui_mode.run_generate(args)
    except RuntimeError as exc:
        assert "environment-selection context is required" in str(exc)
    else:
        raise AssertionError("gui_mode.run_generate should require environment-selection context")


def test_gui_mode_registers_state_after_environment_selection(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "SYS-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    selection_path = context_dir / "environment-selection.json"
    selection_path.write_text(json.dumps({"environment": "gui-mode"}), encoding="utf-8")
    context_first.register_context(
        tmp_path,
        work_dir,
        work_id="SYS-9001",
        context_type="environment-selection",
        path=selection_path,
        required=True,
        generated_by="environment-dispatcher",
        owner="dispatcher",
        schema=".github/schemas/environment-selection.schema.json",
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_dir=None,
        issue_id="SYS-9001",
        mode="auto",
        force=False,
        svg_input_dir=None,
        input_prefix=None,
        skip_context_check=False,
    )

    result = gui_mode.run_generate(args)

    manifest = context_first.load_manifest(work_dir)
    context_types = {item["type"] for item in manifest["contexts"]}
    assert result["status"] == "skipped"
    assert {"environment-selection", "gui-mode-state"} <= context_types


def test_web_svg_layout_mode_rejects_gui_environment_selection(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "SYS-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    selection_path = context_dir / "environment-selection.json"
    selection_path.write_text(json.dumps({"environment": "gui-mode"}), encoding="utf-8")
    context_first.register_context(
        tmp_path,
        work_dir,
        work_id="SYS-9001",
        context_type="environment-selection",
        path=selection_path,
        required=True,
        generated_by="environment-dispatcher",
        owner="dispatcher",
        schema=".github/schemas/environment-selection.schema.json",
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_dir=None,
        issue_id="SYS-9001",
        mode="auto",
        force=False,
        svg_input_dir=None,
        input_prefix=None,
        skip_context_check=False,
    )

    try:
        web_svg_layout_mode.run_generate(args)
    except RuntimeError as exc:
        assert "environment mismatch" in str(exc)
    else:
        raise AssertionError("web_svg_layout_mode.run_generate should reject gui-mode context")


def test_context_first_require_environment_checks_expected_environment(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    selection_path = context_dir / "environment-selection.json"
    selection_path.write_text(json.dumps({"environment": "docker"}), encoding="utf-8")
    context_first.register_context(
        tmp_path,
        work_dir,
        work_id="issue-9001",
        context_type="environment-selection",
        path=selection_path,
        required=True,
        generated_by="environment-dispatcher",
        owner="dispatcher",
        schema=".github/schemas/environment-selection.schema.json",
    )
    args = argparse.Namespace(repo_root=str(tmp_path), work_dir=str(work_dir), environment="docker")

    result = context_first.run_require_environment(args)

    assert result["status"] == "ready"
    assert result["environment"] == "docker"


def test_context_first_require_environment_rejects_mismatch(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    selection_path = context_dir / "environment-selection.json"
    selection_path.write_text(json.dumps({"environment": "gui-mode"}), encoding="utf-8")
    context_first.register_context(
        tmp_path,
        work_dir,
        work_id="issue-9001",
        context_type="environment-selection",
        path=selection_path,
        required=True,
        generated_by="environment-dispatcher",
        owner="dispatcher",
        schema=".github/schemas/environment-selection.schema.json",
    )
    args = argparse.Namespace(repo_root=str(tmp_path), work_dir=str(work_dir), environment="docker")

    try:
        context_first.run_require_environment(args)
    except RuntimeError as exc:
        assert "environment mismatch" in str(exc)
    else:
        raise AssertionError("run_require_environment should reject mismatched environment")


def test_iac_handoff_context_registers_execution_plan_and_handoff(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "SYS-9001"
    validation_path = work_dir / "context" / "shared-artifact-validation.json"
    validation_path.parent.mkdir(parents=True)
    validation_path.write_text(json.dumps({"judgment": "pass"}), encoding="utf-8")
    source_artifact = work_dir / "design-document" / "shared-artifacts-index.md"
    source_artifact.parent.mkdir(parents=True)
    source_artifact.write_text("# Shared Artifacts\n", encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_id="SYS-9001",
        force=False,
        target_repository="owner/realtime-target",
        target_branch="main",
        validator_judgment="unknown",
        source_artifact=[str(source_artifact)],
        validation_path="",
        handoff_path="",
    )

    result = iac_handoff_context.run(args)

    manifest = context_first.load_manifest(work_dir)
    context_types = {item["type"] for item in manifest["contexts"]}
    assert result["status"] == "ready-for-human-check"
    assert {"execution-plan", "realtime-iac-handoff"} <= context_types
    execution_plan = json.loads((work_dir / "context" / "execution-plan.json").read_text(encoding="utf-8"))
    assert execution_plan["required_environment"] == "docker"
    handoff = json.loads((work_dir / "context" / "realtime-iac-handoff.json").read_text(encoding="utf-8"))
    assert handoff["shared_artifact_validation"]["judgment"] == "pass"


def test_iac_handoff_context_parser_paths_and_handoff_defaults(tmp_path: Path) -> None:
    parser = iac_handoff_context.build_parser()
    args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "--work-id",
            "SYS-9001",
            "--force",
            "--target-repository",
            "owner/realtime-target",
            "--target-branch",
            "main",
            "--validator-judgment",
            "conditional-pass",
            "--source-artifact",
            "work/SYS-9001/design-document/shared-artifacts-index.md",
            "--validation-path",
            "work/SYS-9001/context/validator.json",
            "--handoff-path",
            "work/SYS-9001/context/custom-handoff.json",
        ]
    )

    assert args.work_id == "SYS-9001"
    assert args.force is True
    assert args.validator_judgment == "conditional-pass"
    assert args.source_artifact == ["work/SYS-9001/design-document/shared-artifacts-index.md"]
    assert iac_handoff_context.resolve_path(tmp_path, "", tmp_path / "default.json") == tmp_path / "default.json"
    assert iac_handoff_context.resolve_path(tmp_path, "relative.json", tmp_path / "default.json") == tmp_path / "relative.json"
    assert iac_handoff_context.resolve_path(tmp_path, str(tmp_path / "absolute.json"), tmp_path / "default.json") == (
        tmp_path / "absolute.json"
    )

    validation_path = tmp_path / "work" / "SYS-9001" / "context" / "validator.json"
    validation_path.parent.mkdir(parents=True)
    validation_path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")

    handoff = iac_handoff_context.create_handoff(
        tmp_path,
        "SYS-9001",
        validation_path=validation_path,
        source_artifacts=[],
        validator_judgment="conditional-pass",
        target_repository="owner/realtime-target",
        target_branch="main",
    )

    assert handoff["shared_artifact_validation"]["judgment"] == "conditional-pass"
    assert handoff["target_repository"] == "owner/realtime-target"
    assert handoff["required_environment"] == "docker"


def test_iac_handoff_context_reuses_existing_handoff_and_rejects_invalid_existing(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "SYS-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    handoff_path = context_dir / "realtime-iac-handoff.json"
    validation_path = context_dir / "shared-artifact-validation.json"
    validation_path.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
    handoff_path.write_text(json.dumps({"preserved": True}), encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_id="SYS-9001",
        force=False,
        target_repository="",
        target_branch="",
        validator_judgment="unknown",
        source_artifact=[],
        validation_path="",
        handoff_path="",
    )

    result = iac_handoff_context.run(args)

    assert result["status"] == "ready-for-human-check"
    assert json.loads(handoff_path.read_text(encoding="utf-8")) == {"preserved": True}

    handoff_path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
    with pytest.raises(ValueError, match="Existing handoff context is not a JSON object"):
        iac_handoff_context.run(args)


def test_iac_handoff_context_main_and_script_load_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        iac_handoff_context,
        "run",
        lambda args: {
            "status": "ready-for-human-check",
            "work_id": args.work_id,
        },
    )
    assert iac_handoff_context.main(["--repo-root", str(tmp_path), "--work-id", "SYS-9001"]) == 0
    assert '"status": "ready-for-human-check"' in capsys.readouterr().out

    monkeypatch.setattr(iac_handoff_context, "run", lambda args: {"status": "failed"})
    assert iac_handoff_context.main(["--repo-root", str(tmp_path), "--work-id", "SYS-9001"]) == 1

    def raise_error(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(iac_handoff_context, "run", raise_error)
    assert iac_handoff_context.main(["--repo-root", str(tmp_path), "--work-id", "SYS-9001"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(iac_handoff_context.__file__)))
    assert namespace["build_parser"]


def test_dispatcher_context_init_registers_phase3_contexts(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "/docs-sync",
                        "workflow": "docs-sync",
                        "overview": "docs only sync",
                        "aliases": [],
                    }
                ],
                "extensions": [],
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_id="issue-9001",
        workflow="/docs-sync",
        intent_summary="sync docs",
        tool=["gh:read-only:GitHub metadata collection"],
        tool_mode="",
        tool_purpose="workflow execution",
        runtime_mode="standard",
        target_dir="",
        required_context=[],
        required_environment="",
        next_command=["/docs-sync owner/repo develop"],
        stop_condition=[],
        force=False,
    )

    result = dispatcher_context.run_init(args)

    work_dir = tmp_path / "work" / "issue-9001"
    manifest = context_first.load_manifest(work_dir)
    context_types = {item["type"] for item in manifest["contexts"]}
    assert result["status"] == "ready"
    assert {"workflow-selection", "tool-selection", "runtime-context", "execution-plan"} <= context_types
    tool_selection = json.loads((work_dir / "context" / "tool-selection.json").read_text(encoding="utf-8"))
    assert tool_selection["tools"][0]["name"] == "gh"
    assert tool_selection["tools"][0]["mode"] == "read-only"


def test_dispatcher_context_init_preserves_existing_context_without_force(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(json.dumps({"commands": [], "extensions": []}), encoding="utf-8")
    context_dir = tmp_path / "work" / "issue-9001" / "context"
    context_dir.mkdir(parents=True)
    existing = {"schema_version": "1.0", "artifact_type": "workflow-selection", "workflow": "manual-workflow"}
    (context_dir / "workflow-selection.json").write_text(json.dumps(existing), encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_id="issue-9001",
        workflow="/unknown-workflow",
        intent_summary="",
        tool=[],
        tool_mode="",
        tool_purpose="workflow execution",
        runtime_mode="standard",
        target_dir="",
        required_context=[],
        required_environment="",
        next_command=[],
        stop_condition=[],
        force=False,
    )

    dispatcher_context.run_init(args)

    preserved = json.loads((context_dir / "workflow-selection.json").read_text(encoding="utf-8"))
    assert preserved == existing


def test_dispatcher_context_auto_selects_clear_workflow_candidate(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "/docs-sync",
                        "workflow": "docs-sync",
                        "skill": "docs-sync",
                        "overview": "Synchronize documentation with implementation.",
                        "aliases": [],
                        "docs": ["docs/workflows/docs-sync.md"],
                    },
                    {
                        "command": "/rag-build",
                        "workflow": "rag-build",
                        "skill": "rag-build",
                        "overview": "Build file based RAG artifacts.",
                        "aliases": [],
                    },
                ],
                "extensions": [],
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_id="issue-9002",
        workflow="docs sync",
        intent_summary="documentation synchronization",
        tool=[],
        tool_mode="",
        tool_purpose="workflow execution",
        runtime_mode="standard",
        target_dir="",
        required_context=[],
        required_environment="",
        next_command=[],
        stop_condition=[],
        candidate_limit=5,
        force=False,
    )

    result = dispatcher_context.run_init(args)

    selection = json.loads(
        (tmp_path / "work" / "issue-9002" / "context" / "workflow-selection.json").read_text(encoding="utf-8")
    )
    assert result["status"] == "ready"
    assert selection["workflow"] == "docs-sync"
    assert selection["selection_mode"] == "auto"
    assert selection["candidate_selection"]["candidates"][0]["command"] == "/docs-sync"
    assert selection["candidate_selection"]["candidates"][0]["selected"] is True


def test_dispatcher_context_auto_scores_tool_candidates(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "/docs-sync",
                        "workflow": "docs-sync",
                        "overview": "Synchronize documentation with implementation.",
                        "aliases": [],
                    }
                ],
                "extensions": [],
            }
        ),
        encoding="utf-8",
    )
    (registry_dir / "tool_candidates.json").write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "tools": [
                    {
                        "name": "gh",
                        "aliases": ["github-cli"],
                        "default_mode": "read-only",
                        "purpose": "GitHub metadata collection",
                        "workflows": ["/docs-sync"],
                        "keywords": ["github", "issue", "docs", "sync"],
                        "install_required": False,
                        "mutation_capable": True,
                        "human_check_required": False,
                        "human_check_reasons": [],
                    },
                    {
                        "name": "git",
                        "aliases": ["scm"],
                        "default_mode": "read-only",
                        "purpose": "SCM branch and diff inspection",
                        "workflows": ["/docs-sync"],
                        "keywords": ["git", "branch", "diff", "docs"],
                        "install_required": False,
                        "mutation_capable": True,
                        "human_check_required": False,
                        "human_check_reasons": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_id="issue-9005",
        workflow="/docs-sync",
        intent_summary="sync docs with GitHub metadata and git diff",
        tool=[],
        tool_mode="",
        tool_purpose="workflow execution",
        runtime_mode="standard",
        target_dir="",
        required_context=[],
        required_environment="",
        next_command=[],
        stop_condition=[],
        candidate_limit=5,
        force=False,
    )

    result = dispatcher_context.run_init(args)

    tool_selection = json.loads(
        (tmp_path / "work" / "issue-9005" / "context" / "tool-selection.json").read_text(encoding="utf-8")
    )
    selected_tools = {item["name"] for item in tool_selection["tools"]}
    assert result["status"] == "ready"
    assert {"gh", "git"} <= selected_tools
    assert tool_selection["selection_mode"] == "auto"
    assert tool_selection["candidate_selection"]["candidate_count"] == 2
    assert all(item["selected"] is True for item in tool_selection["candidate_selection"]["candidates"])


def test_dispatcher_context_tool_candidate_human_check_for_docker(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "/realtime-iac",
                        "workflow": "realtime-iac",
                        "overview": "Generate realtime infrastructure with Docker.",
                        "aliases": [],
                    }
                ],
                "extensions": [],
            }
        ),
        encoding="utf-8",
    )
    (registry_dir / "tool_candidates.json").write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "tools": [
                    {
                        "name": "docker",
                        "aliases": ["compose"],
                        "default_mode": "local",
                        "purpose": "Container runtime validation",
                        "workflows": ["/realtime-iac"],
                        "keywords": ["docker", "compose", "iac"],
                        "install_required": False,
                        "mutation_capable": True,
                        "human_check_required": True,
                        "human_check_reasons": ["Docker may affect host networking."],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_id="issue-9006",
        workflow="/realtime-iac",
        intent_summary="docker compose realtime gateway",
        tool=[],
        tool_mode="",
        tool_purpose="workflow execution",
        runtime_mode="standard",
        target_dir="",
        required_context=[],
        required_environment="",
        next_command=[],
        stop_condition=[],
        candidate_limit=5,
        force=False,
    )

    result = dispatcher_context.run_init(args)

    tool_selection = json.loads(
        (tmp_path / "work" / "issue-9006" / "context" / "tool-selection.json").read_text(encoding="utf-8")
    )
    assert result["status"] == "human-check-required"
    assert tool_selection["human_check_required"] is True
    assert tool_selection["tools"][0]["name"] == "docker"
    assert "Docker may affect host networking." in tool_selection["human_check_reasons"]


def test_rag_build_registers_pipeline_context(tmp_path: Path) -> None:
    source_dir = tmp_path / "rag" / "corrective-action-report"
    source_dir.mkdir(parents=True)
    (source_dir / "report.md").write_text(
        "# Workflow doctor\n\nHuman gate registry and workflow doctor regression evidence.\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        work_id="issue-9003",
        work_dir="",
        source_dir="rag/corrective-action-report",
        document_type="corrective-action-report",
        normalized_dir="rag/normalized",
        chunks_dir="rag/chunks",
        indexes_dir="rag/indexes",
        embeddings_output="rag/embeddings/chunks-embeddings.jsonl",
        output="rag/retrieval/rag-build-run-latest.json",
        project="",
        repository="",
        branch="",
        commit="",
        status="draft",
        chunk_size=500,
        chunk_overlap=0,
        embedding_dimensions=64,
        clean_output=True,
        standardize_filenames=False,
        skip_standardize=True,
        replace_references=False,
        random_length=8,
    )

    result = rag_build.run(args)

    work_dir = tmp_path / "work" / "issue-9003"
    manifest = context_first.load_manifest(work_dir)
    artifact = json.loads((tmp_path / result["rag_build_run"]).read_text(encoding="utf-8"))
    assert result["document_count"] == 1
    assert result["chunk_count"] == 1
    assert result["embedding_count"] == 1
    assert artifact["artifact_type"] == "rag-build-run"
    assert "rag-build-run" in {item["type"] for item in manifest["contexts"]}


def test_corrective_action_report_registers_report_context(tmp_path: Path) -> None:
    report_dir = tmp_path / "rag" / "corrective-action-report"
    report_dir.mkdir(parents=True)
    report_path = report_dir / "20260705010101_ABC12345_repo.md"
    report_path.write_text(
        "\n".join(
            [
                "---",
                "type: corrective-action-report",
                "repository: owner/repo",
                "branch: develop",
                "commit: abcdef0",
                "status: draft",
                "---",
                "",
                "# Corrective Action Report",
                "",
                "## Findings",
                "",
                "| ID | Severity | Area | Finding | Why It Matters | Recommended Action |",
                "| --- | --- | --- | --- | --- | --- |",
                "| F-001 | high | runtime | finding | reason | action |",
                "",
                "## RAG Capture Candidates",
                "",
                "- runtime finding",
            ]
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        command="register",
        report_path=str(report_path),
        repository="owner/repo",
        target_branch="develop",
        work_id="develop",
        work_dir="",
    )

    result = corrective_action_report.run_register(args)

    work_dir = tmp_path / "work" / "develop"
    context = json.loads((work_dir / "context" / "corrective-action-report.json").read_text(encoding="utf-8"))
    manifest = context_first.load_manifest(work_dir)
    assert result["status"] == "registered"
    assert context["report_path"] == "rag/corrective-action-report/20260705010101_ABC12345_repo.md"
    assert context["target_commit"] == "abcdef0"
    assert context["finding_summary"]["finding_count"] == 1
    assert "corrective-action-report" in {item["type"] for item in manifest["contexts"]}


def test_corrective_action_fix_prefers_manifest_report_when_argument_missing(tmp_path: Path) -> None:
    report_dir = tmp_path / "rag" / "corrective-action-report"
    report_dir.mkdir(parents=True)
    report_path = report_dir / "20260705020202_DEF67890_repo.md"
    report_path.write_text(
        "---\nrepository: owner/repo\nbranch: develop\n---\n\n# Corrective Action Report\n",
        encoding="utf-8",
    )
    corrective_action_report.run_register(
        argparse.Namespace(
            repo_root=str(tmp_path),
            command="register",
            report_path=str(report_path),
            repository="owner/repo",
            target_branch="develop",
            work_id="develop",
            work_dir="",
        )
    )
    args = argparse.Namespace(
        repository="owner/repo",
        target_branch="feature/issue-9004",
        work_id="issue-9004",
        base_work_id="develop",
        reuse_existing=False,
        report_path="",
        intent_summary="",
        repo_root=str(tmp_path),
    )

    result = init_corrective_action_fix.run(args)

    fix_work_dir = tmp_path / "work" / "issue-9004"
    fix_context = json.loads((fix_work_dir / "context" / "corrective-action-report.json").read_text(encoding="utf-8"))
    manifest = context_first.load_manifest(fix_work_dir)
    assert result["report_resolution"] == "manifest"
    assert result["report_path"] == "rag/corrective-action-report/20260705020202_DEF67890_repo.md"
    assert fix_context["resolution"]["source_context_path"] == "work/develop/context/corrective-action-report.json"
    assert "corrective-action-report" in {item["type"] for item in manifest["contexts"]}


def test_docs_sync_registers_manifest_contexts(tmp_path: Path) -> None:
    args = argparse.Namespace(
        command="init",
        repository="owner/repo",
        target_branch="develop",
        work_id="docs-develop",
        base_work_id="",
        reuse_existing=False,
        intent_summary="",
        repo_root=str(tmp_path),
    )

    docs_sync.init_work(args)
    scm_state_path = tmp_path / "work" / "docs-develop" / "context" / "scm-state.json"
    scm_state_path.write_text(
        json.dumps({"repository": "owner/repo", "current_branch": "develop"}),
        encoding="utf-8",
    )
    result = docs_sync.create_analysis_template(
        argparse.Namespace(
            command="analysis-template",
            work_id="docs-develop",
            analysis_path="",
            repo_root=str(tmp_path),
            allow_missing_scm_state=False,
        )
    )

    manifest = context_first.load_manifest(tmp_path / "work" / "docs-develop")
    context_types = {item["type"] for item in manifest["contexts"]}
    assert {"agent-context", "artifact-index", "scm-state", "docs-drift-analysis"} <= context_types
    assert result["context_gate"]["status"] == "ready"


def test_docs_sync_analysis_requires_scm_state_for_new_work(tmp_path: Path) -> None:
    docs_sync.init_work(
        argparse.Namespace(
            command="init",
            repository="owner/repo",
            target_branch="develop",
            work_id="docs-develop",
            base_work_id="",
            reuse_existing=False,
            intent_summary="",
            repo_root=str(tmp_path),
        )
    )

    with pytest.raises(RuntimeError, match="scm-state"):
        docs_sync.create_analysis_template(
            argparse.Namespace(
                command="analysis-template",
                work_id="docs-develop",
                analysis_path="",
                repo_root=str(tmp_path),
                allow_missing_scm_state=False,
            )
        )


def test_github_knowledge_registers_tool_selection_and_gate(tmp_path: Path) -> None:
    args = argparse.Namespace(
        command="init",
        repository="owner/repo",
        target_branch="main",
        scan_mode=["recent"],
        repair_mode="apply",
        rag_output=True,
        work_id="github-knowledge-repo-recent",
        reuse_existing=False,
        intent_summary="",
        repo_root=str(tmp_path),
    )

    github_knowledge_maintenance.init_work(args)

    work_dir = tmp_path / "work" / "github-knowledge-repo-recent"
    manifest = context_first.load_manifest(work_dir)
    context_types = {item["type"] for item in manifest["contexts"]}
    gate = json.loads((work_dir / "context" / "github-operation-gate.json").read_text(encoding="utf-8"))
    tool_selection = json.loads((work_dir / "context" / "tool-selection.json").read_text(encoding="utf-8"))
    assert {"tool-selection", "github-operation-gate"} <= context_types
    assert gate["human_check_required"] is True
    assert any(item["mode"] == "mutation" for item in tool_selection["tools"])


def test_github_knowledge_sync_plan_requires_mutation_gate(tmp_path: Path) -> None:
    github_knowledge_maintenance.init_work(
        argparse.Namespace(
            command="init",
            repository="owner/repo",
            target_branch="main",
            scan_mode=["recent"],
            repair_mode="apply",
            rag_output=False,
            work_id="github-knowledge-repo-recent",
            reuse_existing=False,
            intent_summary="",
            repo_root=str(tmp_path),
        )
    )
    github_knowledge_maintenance.create_analysis_template(
        argparse.Namespace(
            command="analysis-template",
            work_id="github-knowledge-repo-recent",
            analysis_path="",
            repo_root=str(tmp_path),
        )
    )

    result = github_knowledge_maintenance.create_sync_plan(
        argparse.Namespace(
            command="github-sync-plan",
            work_id="github-knowledge-repo-recent",
            analysis_path="",
            output="",
            repo_root=str(tmp_path),
        )
    )

    assert result["context_gate"]["require_mutation_gate"] is True
    assert result["context_gate"]["status"] == "ready"


def test_knowledge_capture_prefers_manifest_context_then_records_resolution(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    source_dir = work_dir / "source" / "repository"
    (source_dir / "docs").mkdir(parents=True)
    manifest_scm = context_dir / "manifest-scm-state.json"
    manifest_scm.write_text(
        json.dumps({"repository": "manifest/repo", "current_branch": "feature/manifest"}),
        encoding="utf-8",
    )
    (context_dir / "scm-state.json").write_text(
        json.dumps({"repository": "fallback/repo", "current_branch": "feature/fallback"}),
        encoding="utf-8",
    )
    context_first.register_context(
        tmp_path,
        work_dir,
        work_id="issue-9001",
        context_type="scm-state",
        path=manifest_scm,
        required=True,
        generated_by="runtime-scm",
        owner="workflow",
        schema=".github/schemas/scm-state.schema.json",
    )
    args = argparse.Namespace(
        issue="issue-9001",
        repository="",
        branch="",
        base_work_id="",
        repo_root=str(tmp_path),
        source_dir=str(source_dir),
        dry_run=True,
        allow_legacy_scm_fallback=False,
    )

    result = knowledge_capture.knowledge_capture(args)

    assert result["repository"] == "manifest/repo"
    assert result["branch"] == "feature/manifest"
    assert result["context_resolution"]["scm_state"]["mode"] == "manifest"
    assert result["context_resolution"]["manifest_scm_state_required"] is True


def test_knowledge_capture_requires_manifest_scm_state_for_active_work(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-9002"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    source_dir = work_dir / "source" / "repository"
    (source_dir / "docs").mkdir(parents=True)
    (context_dir / "scm-state.json").write_text(
        json.dumps({"repository": "fallback/repo", "current_branch": "feature/fallback"}),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        issue="issue-9002",
        repository="",
        branch="",
        base_work_id="",
        repo_root=str(tmp_path),
        source_dir=str(source_dir),
        dry_run=True,
        allow_legacy_scm_fallback=False,
    )

    with pytest.raises(RuntimeError, match="manifest scm-state"):
        knowledge_capture.knowledge_capture(args)
