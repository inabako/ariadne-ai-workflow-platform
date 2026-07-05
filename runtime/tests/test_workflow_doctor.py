from __future__ import annotations

import argparse
from pathlib import Path

from runtime.workflow import close_archive, workflow_doctor


def test_tracked_policy_violations_allows_only_readme_under_work_and_rag(monkeypatch) -> None:
    monkeypatch.setattr(
        workflow_doctor,
        "run_git",
        lambda repo_root, args: [
            "work/README.md",
            "work/issue-1/context/state.json",
            "rag/README.md",
            "rag/chunks/chunks.jsonl",
            "docs/README.md",
        ],
    )

    violations = workflow_doctor.tracked_policy_violations(Path("repo"))

    assert violations == ["work/issue-1/context/state.json", "rag/chunks/chunks.jsonl"]


def test_missing_required_files_reports_core_runtime_assets(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "work").mkdir()

    missing = workflow_doctor.missing_required_files(tmp_path)

    assert ".gitignore" in missing
    assert "runtime/pytest.ini" in missing
    assert "runtime/tools/aiwfctl.cmd" in missing
    assert ".github/schemas/context-manifest.schema.json" in missing


def test_human_gate_registry_flags_schema_responsibility_boundary(tmp_path: Path) -> None:
    registry = tmp_path / "runtime" / "registries" / "human_gates.json"
    registry.parent.mkdir(parents=True)
    registry.write_text('{"$schema": "x", "schema_version": "1.0"}', encoding="utf-8")

    findings = workflow_doctor.human_gate_registry_findings(tmp_path)

    assert "contains $schema" in findings[0]
    assert "contains schema_version" in findings[1]
    assert "does not contain registry_version" in findings[2]


def test_close_archive_findings_reports_partial_archive(tmp_path: Path) -> None:
    archive = tmp_path / "work" / "close" / "improvement" / "issue-1"
    archive.mkdir(parents=True)
    (archive / close_archive.REPORT_FILES[0]).write_text("# partial\n", encoding="utf-8")

    findings = workflow_doctor.close_archive_findings(tmp_path)

    assert findings == ["work/close/improvement/issue-1"]


def test_workflow_doctor_fail_on_warning_turns_warning_into_fail(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: ["work/issue-1/tmp.txt"])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    args = argparse.Namespace(repo_root=str(tmp_path), fail_on_warning=True)

    result = workflow_doctor.run(args)

    assert result["status"] == "fail"
    assert result["warning_count"] == 1
    assert result["warnings"][0]["id"] == "tracked-local-workspace-files"
