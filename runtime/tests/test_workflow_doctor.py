from __future__ import annotations

import argparse
import runpy
import subprocess
from pathlib import Path

from runtime.workflow import close_archive, workflow_doctor


def test_run_git_allows_returncode_one_and_filters_blank_lines(monkeypatch, tmp_path: Path) -> None:
    def fake_run(command, cwd, text, capture_output, check):
        assert command == ["git", "ls-files", "work", "rag"]
        assert cwd == tmp_path
        assert text is True
        assert capture_output is True
        assert check is False
        return subprocess.CompletedProcess(command, 1, stdout="\nwork/a.txt\n\nrag/b.txt\n", stderr="")

    monkeypatch.setattr(workflow_doctor.subprocess, "run", fake_run)

    lines = workflow_doctor.run_git(tmp_path, ["ls-files", "work", "rag"])

    assert lines == ["work/a.txt", "rag/b.txt"]


def test_run_git_raises_for_unexpected_returncode(monkeypatch, tmp_path: Path) -> None:
    def fake_run(command, cwd, text, capture_output, check):
        return subprocess.CompletedProcess(command, 2, stdout="fallback", stderr="fatal")

    monkeypatch.setattr(workflow_doctor.subprocess, "run", fake_run)

    try:
        workflow_doctor.run_git(tmp_path, ["ls-files", "work", "rag"])
    except RuntimeError as exc:
        assert str(exc) == "fatal"
    else:  # pragma: no cover
        raise AssertionError("RuntimeError was not raised")


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
    assert "runtime/tools/pytest_ut_spec_sync.py" in missing
    assert "runtime/observability/metrics.py" in missing
    assert "runtime/tests/test_observability_metrics.py" in missing
    assert "skills/runtime-health-check/SKILL.md" in missing
    assert ".github/prompts/runtime-health-check.prompt.md" in missing
    assert "docs/workflows/runtime-health-check.md" in missing
    assert ".github/schemas/context-manifest.schema.json" in missing
    assert ".github/schemas/runtime-metrics.schema.json" in missing
    assert ".github/schemas/pytest-ut-spec-sync-report.schema.json" in missing
    assert ".github/agents/runtime-quality-gate-agent.prompt.md" in missing


def test_human_gate_registry_flags_schema_responsibility_boundary(tmp_path: Path) -> None:
    registry = tmp_path / "runtime" / "registries" / "human_gates.json"
    registry.parent.mkdir(parents=True)
    registry.write_text('{"$schema": "x", "schema_version": "1.0"}', encoding="utf-8")

    findings = workflow_doctor.human_gate_registry_findings(tmp_path)

    assert "contains $schema" in findings[0]
    assert "contains schema_version" in findings[1]
    assert "does not contain registry_version" in findings[2]


def test_human_gate_registry_findings_accepts_missing_or_valid_registry(tmp_path: Path) -> None:
    assert workflow_doctor.human_gate_registry_findings(tmp_path) == []

    registry = tmp_path / "runtime" / "registries" / "human_gates.json"
    registry.parent.mkdir(parents=True)
    registry.write_text('{"registry_version": "1.0", "gates": []}', encoding="utf-8")

    assert workflow_doctor.human_gate_registry_findings(tmp_path) == []


def test_close_archive_findings_reports_partial_archive(tmp_path: Path) -> None:
    archive = tmp_path / "work" / "close" / "improvement" / "issue-1"
    archive.mkdir(parents=True)
    (archive / close_archive.REPORT_FILES[0]).write_text("# partial\n", encoding="utf-8")

    findings = workflow_doctor.close_archive_findings(tmp_path)

    assert findings == ["work/close/improvement/issue-1"]


def test_close_archive_findings_accepts_missing_root_and_complete_archive(tmp_path: Path) -> None:
    assert workflow_doctor.close_archive_findings(tmp_path) == []

    archive = tmp_path / "work" / "close" / "improvement" / "issue-1"
    archive.mkdir(parents=True)
    for report_file in close_archive.REPORT_FILES:
        (archive / report_file).write_text("# report\n", encoding="utf-8")

    assert workflow_doctor.close_archive_findings(tmp_path) == []


def test_vscode_utf8_first_findings_accepts_complete_settings(tmp_path: Path) -> None:
    settings = tmp_path / ".vscode" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        """{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "files.eol": "\\n",
  "terminal.integrated.env.windows": {
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
    "AIWF_TEXT_ENCODING": "utf-8"
  },
  "terminal.integrated.profiles.windows": {
    "Dispatcher PowerShell": {
      "source": "PowerShell",
      "args": [
        "-NoLogo",
        "-NoExit",
        "-Command",
        "[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false); [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); $OutputEncoding = [System.Text.UTF8Encoding]::new($false); chcp 65001 > $null"
      ]
    }
  }
}
""",
        encoding="utf-8",
    )
    (tmp_path / ".editorconfig").write_text(
        """root = true

[*]
charset = utf-8
end_of_line = lf

[*.{bat,cmd}]
charset = unset
end_of_line = crlf
""",
        encoding="utf-8",
    )

    assert workflow_doctor.vscode_utf8_first_findings(tmp_path) == []


def test_vscode_utf8_first_findings_reports_missing_contract_parts(tmp_path: Path) -> None:
    settings = tmp_path / ".vscode" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        """{
  "files.encoding": "shiftjis",
  "terminal.integrated.env.windows": {
    "PYTHONUTF8": "0"
  },
  "terminal.integrated.profiles.windows": {
    "Dispatcher PowerShell": {
      "source": "PowerShell",
      "args": ["-NoLogo"]
    }
  }
}
""",
        encoding="utf-8",
    )

    findings = workflow_doctor.vscode_utf8_first_findings(tmp_path)

    assert ".vscode/settings.json:files.encoding" in findings
    assert ".vscode/settings.json:files.autoGuessEncoding" in findings
    assert ".vscode/settings.json:terminal.integrated.env.windows.PYTHONUTF8" in findings
    assert ".vscode/settings.json:terminal profile Dispatcher PowerShell missing InputEncoding" in findings
    assert ".editorconfig" in findings


def test_workflow_doctor_fail_on_warning_turns_warning_into_fail(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: ["work/issue-1/tmp.txt"])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])
    args = argparse.Namespace(repo_root=str(tmp_path), fail_on_warning=True)

    result = workflow_doctor.run(args)

    assert result["status"] == "fail"
    assert result["warning_count"] == 1
    assert result["warnings"][0]["id"] == "tracked-local-workspace-files"


def test_workflow_doctor_run_reports_all_warning_types(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: ["work/issue-1/tmp.txt"])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: ["runtime/ctl.py"])
    monkeypatch.setattr(
        workflow_doctor,
        "human_gate_registry_findings",
        lambda repo_root: ["runtime/registries/human_gates.json contains $schema"],
    )
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: ["work/close/improvement/issue-1"])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [".vscode/settings.json:files.encoding"])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: ["missing: runtime/tests/test_new.py::test_new"])
    args = argparse.Namespace(repo_root=str(tmp_path), fail_on_warning=False)

    result = workflow_doctor.run(args)

    assert result["status"] == "warning"
    assert result["warning_count"] == 6
    assert [warning["id"] for warning in result["warnings"]] == [
        "tracked-local-workspace-files",
        "missing-required-files",
        "human-gate-registry-responsibility-boundary",
        "incomplete-close-archive",
        "vscode-utf8-first",
        "pytest-ut-spec-sync",
    ]


def test_workflow_doctor_run_passes_without_warnings(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])
    args = argparse.Namespace(repo_root=str(tmp_path), fail_on_warning=True)

    result = workflow_doctor.run(args)

    assert result == {"status": "pass", "warning_count": 0, "warnings": []}


def test_workflow_doctor_main_prints_pass_json(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])

    code = workflow_doctor.main(["--repo-root", str(tmp_path)])

    captured = capsys.readouterr()
    assert code == 0
    assert '"status": "pass"' in captured.out


def test_workflow_doctor_main_returns_one_on_fail_on_warning(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: ["rag/chunks/chunks.jsonl"])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])

    code = workflow_doctor.main(["--repo-root", str(tmp_path), "--fail-on-warning"])

    captured = capsys.readouterr()
    assert code == 1
    assert '"status": "fail"' in captured.out

    namespace = runpy.run_path(str(Path(workflow_doctor.__file__)))
    assert namespace["build_parser"]


def test_workflow_doctor_ut_spec_sync_findings_and_skip(monkeypatch, tmp_path: Path) -> None:
    spec = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    runtime_root = tmp_path / "runtime"
    spec.parent.mkdir(parents=True)
    runtime_root.mkdir(parents=True)
    spec.write_text("# spec\n", encoding="utf-8")
    monkeypatch.setattr(
        workflow_doctor.pytest_ut_spec_sync,
        "check_spec",
        lambda spec_path, runtime_root: {
            "status": "error",
            "missing_in_spec": ["runtime/tests/test_new.py::test_new"],
            "stale_in_spec": [],
            "order_matches": False,
            "bad_input_position": ["RT-UT-CASE-001"],
        },
    )

    findings = workflow_doctor.ut_spec_sync_findings(tmp_path)

    assert "missing: runtime/tests/test_new.py::test_new" in findings
    assert "pytest collection order does not match UT spec order" in findings
    assert "bad input position: RT-UT-CASE-001" in findings

    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    args = argparse.Namespace(repo_root=str(tmp_path), fail_on_warning=True, skip_ut_spec_sync=True)
    assert workflow_doctor.run(args)["status"] == "pass"


def test_defensive_specimen_workflow_doctor_reports_missing_ut_spec_inputs(tmp_path: Path) -> None:
    missing_spec = workflow_doctor.ut_spec_sync_findings(tmp_path)
    assert missing_spec == ["docs/reference/runtime-pytest-ut/case-specification.md"]

    spec = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    spec.parent.mkdir(parents=True)
    spec.write_text("# spec\n", encoding="utf-8")

    missing_runtime = workflow_doctor.ut_spec_sync_findings(tmp_path)
    assert missing_runtime == ["runtime"]


def test_defensive_specimen_workflow_doctor_reports_stale_and_bad_position_only(monkeypatch, tmp_path: Path) -> None:
    spec = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    runtime_root = tmp_path / "runtime"
    spec.parent.mkdir(parents=True)
    runtime_root.mkdir(parents=True)
    spec.write_text("# spec\n", encoding="utf-8")
    monkeypatch.setattr(
        workflow_doctor.pytest_ut_spec_sync,
        "check_spec",
        lambda spec_path, runtime_root: {
            "status": "error",
            "missing_in_spec": [],
            "stale_in_spec": ["runtime/tests/test_old.py::test_old"],
            "order_matches": True,
            "bad_input_position": ["RT-UT-CASE-999"],
        },
    )

    findings = workflow_doctor.ut_spec_sync_findings(tmp_path)

    assert findings == [
        "stale: runtime/tests/test_old.py::test_old",
        "bad input position: RT-UT-CASE-999",
    ]


def test_defensive_specimen_workflow_doctor_reports_stale_without_bad_position(monkeypatch, tmp_path: Path) -> None:
    spec = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    runtime_root = tmp_path / "runtime"
    spec.parent.mkdir(parents=True)
    runtime_root.mkdir(parents=True)
    spec.write_text("# spec\n", encoding="utf-8")
    monkeypatch.setattr(
        workflow_doctor.pytest_ut_spec_sync,
        "check_spec",
        lambda spec_path, runtime_root: {
            "status": "error",
            "missing_in_spec": [],
            "stale_in_spec": ["runtime/tests/test_old.py::test_old"],
            "order_matches": True,
            "bad_input_position": [],
        },
    )

    assert workflow_doctor.ut_spec_sync_findings(tmp_path) == ["stale: runtime/tests/test_old.py::test_old"]


def test_defensive_specimen_workflow_doctor_accepts_clean_ut_spec_sync(monkeypatch, tmp_path: Path) -> None:
    spec = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    runtime_root = tmp_path / "runtime"
    spec.parent.mkdir(parents=True)
    runtime_root.mkdir(parents=True)
    spec.write_text("# spec\n", encoding="utf-8")
    monkeypatch.setattr(
        workflow_doctor.pytest_ut_spec_sync,
        "check_spec",
        lambda spec_path, runtime_root: {"status": "ok"},
    )

    assert workflow_doctor.ut_spec_sync_findings(tmp_path) == []
