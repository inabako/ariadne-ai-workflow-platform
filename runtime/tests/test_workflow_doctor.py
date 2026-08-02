from __future__ import annotations

import argparse
import runpy
import subprocess
from pathlib import Path

from runtime.common import text_boundary
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


def test_tracked_policy_violations_allows_work_readme_but_blocks_rag_files(monkeypatch) -> None:
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

    assert violations == ["work/issue-1/context/state.json", "rag/README.md", "rag/chunks/chunks.jsonl"]


def test_missing_required_files_reports_core_runtime_assets(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "work").mkdir()

    missing = workflow_doctor.missing_required_files(tmp_path)

    assert ".gitignore" in missing
    assert "runtime/pytest.ini" in missing
    assert "runtime/windows-script/aiwfctl.cmd" in missing
    assert "runtime/tools/pytest_ut_spec_sync.py" in missing
    assert "runtime/observability/metrics.py" in missing
    assert "runtime/tests/test_observability_metrics.py" in missing
    assert "skills/runtime-health-check/SKILL.md" in missing
    assert ".ariadne/prompts/runtime-health-check.prompt.md" in missing
    assert "docs/workflows/runtime-health-check.md" in missing
    assert ".ariadne/schemas/context-manifest.schema.json" in missing
    assert ".ariadne/schemas/runtime-metrics.schema.json" in missing
    assert ".ariadne/schemas/pytest-ut-spec-sync-report.schema.json" in missing
    assert ".ariadne/agents/runtime-quality-gate-agent.prompt.md" in missing


def test_pytest_runtime_boundary_findings_blocks_root_config_and_cache(tmp_path: Path) -> None:
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / "runtime").mkdir()

    findings = workflow_doctor.pytest_runtime_boundary_findings(tmp_path)

    assert "pytest.ini" in findings
    assert ".pytest_cache" in findings
    assert "missing:runtime/pytest.ini" in findings

    (tmp_path / "pytest.ini").unlink()
    (tmp_path / ".pytest_cache").rmdir()
    (tmp_path / "runtime" / "pytest.ini").write_text("[pytest]\ncache_dir = .pytest_cache\n", encoding="utf-8")
    (tmp_path / "runtime" / ".pytest_cache").mkdir()

    assert workflow_doctor.pytest_runtime_boundary_findings(tmp_path) == []


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


def test_registry_seed_findings_reports_incomplete_template_source(tmp_path: Path) -> None:
    findings = workflow_doctor.registry_seed_findings(tmp_path)
    assert findings == ["missing:templates/registries"]

    source = tmp_path / workflow_doctor.registry_store.DEFAULT_TEMPLATE_JSON_SOURCE_DIR
    source.mkdir(parents=True)
    for name in (
        *workflow_doctor.registry_store.REQUIRED_REGISTRY_SOURCE_FILES,
        workflow_doctor.registry_store.CTL_HELP_USAGE_REGISTRY_FILE,
        workflow_doctor.registry_store.SEARCH_TERMS_REGISTRY_FILE,
        workflow_doctor.registry_store.RUNTIME_HELP_CAPABILITIES_REGISTRY_FILE,
    ):
        (source / name).write_text('{"registry_version": "1.0"}', encoding="utf-8")

    assert workflow_doctor.registry_seed_findings(tmp_path) == []

    (source / workflow_doctor.registry_store.SEARCH_TERMS_REGISTRY_FILE).unlink()
    missing = workflow_doctor.registry_seed_findings(tmp_path)
    assert missing == ["missing:templates/registries/search_terms.json"]

    (source / workflow_doctor.registry_store.SEARCH_TERMS_REGISTRY_FILE).write_text("[1]", encoding="utf-8")
    invalid_shape = workflow_doctor.registry_seed_findings(tmp_path)
    assert invalid_shape == ["templates/registries/search_terms.json: must be a JSON object"]

    (source / workflow_doctor.registry_store.SEARCH_TERMS_REGISTRY_FILE).write_text("{invalid", encoding="utf-8")
    invalid_json = workflow_doctor.registry_seed_findings(tmp_path)
    assert invalid_json == ["templates/registries/search_terms.json: invalid JSON: Expecting property name enclosed in double quotes"]


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


def test_vscode_utf8_first_findings_reports_missing_or_invalid_settings(tmp_path: Path) -> None:
    assert workflow_doctor.vscode_utf8_first_findings(tmp_path) == [".vscode/settings.json"]

    settings = tmp_path / ".vscode" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text("{invalid", encoding="utf-8")

    invalid = workflow_doctor.vscode_utf8_first_findings(tmp_path)
    assert invalid == [".vscode/settings.json invalid JSON: Expecting property name enclosed in double quotes"]

    settings.write_text("[]", encoding="utf-8")

    assert workflow_doctor.vscode_utf8_first_findings(tmp_path) == [".vscode/settings.json is not a JSON object"]


def test_vscode_utf8_first_findings_reports_wrong_terminal_shapes_and_editorconfig_snippets(tmp_path: Path) -> None:
    settings = tmp_path / ".vscode" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        """{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "files.eol": "\\n",
  "terminal.integrated.env.windows": [],
  "terminal.integrated.profiles.windows": [
    "PowerShell"
  ]
}
""",
        encoding="utf-8",
    )
    (tmp_path / ".editorconfig").write_text("root = true\n", encoding="utf-8")

    findings = workflow_doctor.vscode_utf8_first_findings(tmp_path)

    assert ".vscode/settings.json:terminal.integrated.env.windows" in findings
    assert ".vscode/settings.json:terminal.integrated.profiles.windows" in findings
    assert ".editorconfig:charset = utf-8" in findings
    assert ".editorconfig:end_of_line = crlf" in findings


def test_vscode_utf8_first_findings_ignores_non_powershell_profiles(tmp_path: Path) -> None:
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
    "Command Prompt": {
      "source": "Command Prompt",
      "args": []
    },
    "Malformed": []
  }
}
""",
        encoding="utf-8",
    )
    (tmp_path / ".editorconfig").write_text(
        """charset = utf-8
end_of_line = lf
[*.{bat,cmd}]
charset = unset
end_of_line = crlf
""",
        encoding="utf-8",
    )

    assert workflow_doctor.vscode_utf8_first_findings(tmp_path) == []


def test_duckdb_read_model_findings_reports_missing_read_model_when_sources_exist(tmp_path: Path) -> None:
    source_repo = tmp_path / workflow_doctor.duckdb_store.DEFAULT_SOURCE_REPO_PATH
    source_dir = source_repo / "rag" / "normalized"
    source_dir.mkdir(parents=True)
    (source_dir / "doc.json").write_text("{}", encoding="utf-8")

    findings = workflow_doctor.duckdb_read_model_findings(tmp_path)

    assert findings == [
        "missing:db/rag/ariadne-knowledge.duckdb",
        "source:work/db/ariadne-knowledge-platform",
        "rebuild:aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset",
    ]


def test_duckdb_read_model_findings_accepts_missing_sources_or_existing_db(tmp_path: Path) -> None:
    assert workflow_doctor.duckdb_read_model_findings(tmp_path) == []

    source_repo = tmp_path / workflow_doctor.duckdb_store.DEFAULT_SOURCE_REPO_PATH
    source_repo.mkdir(parents=True)
    assert workflow_doctor.duckdb_read_model_findings(tmp_path) == []

    source_dir = source_repo / "rag" / "normalized"
    source_dir.mkdir(parents=True)
    (source_dir / "doc.json").write_text("{}", encoding="utf-8")
    db_path = tmp_path / workflow_doctor.duckdb_store.DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True)
    db_path.write_bytes(b"duckdb")

    assert workflow_doctor.duckdb_read_model_findings(tmp_path) == []


def test_workspace_layout_literal_findings_reports_runtime_path_joins(tmp_path: Path) -> None:
    bad_runtime = tmp_path / "runtime" / "workflow" / "bad_layout.py"
    bad_runtime.parent.mkdir(parents=True)
    bad_runtime.write_text(
        "from pathlib import Path\n"
        "def bad(repo_root: Path, work_dir: Path):\n"
        "    a = repo_root / \"work\" / \"issue-1\"\n"
        "    b = work_dir / \"context\" / \"state.json\"\n"
        "    c = work_dir / \"source\" / \"repository\"\n"
        "    return a, b, c\n",
        encoding="utf-8",
    )

    findings = workflow_doctor.workspace_layout_literal_findings(tmp_path)

    assert findings == [
        "runtime/workflow/bad_layout.py:3: use runtime.constants.workspace.work_dir_for_id",
        "runtime/workflow/bad_layout.py:4: use context_dir_for_work_dir or context_file",
        "runtime/workflow/bad_layout.py:5: use target_repository_dir_for_work_dir",
    ]


def test_workspace_layout_literal_findings_ignores_constants_and_tests(tmp_path: Path) -> None:
    constants = tmp_path / "runtime" / "constants" / "workspace.py"
    tests = tmp_path / "runtime" / "tests" / "test_layout.py"
    helper_runtime = tmp_path / "runtime" / "workflow" / "good_layout.py"
    constants.parent.mkdir(parents=True)
    tests.parent.mkdir(parents=True)
    helper_runtime.parent.mkdir(parents=True)
    constants.write_text("WORK_ROOT = \"work\"\n", encoding="utf-8")
    tests.write_text("def test_path(work_dir):\n    assert work_dir / \"context\"\n", encoding="utf-8")
    helper_runtime.write_text(
        "from runtime.constants.workspace import context_file\n"
        "def good(work_dir):\n"
        "    return context_file(work_dir, \"state.json\")\n",
        encoding="utf-8",
    )

    assert workflow_doctor.workspace_layout_literal_findings(tmp_path) == []


def test_path_constant_literal_findings_reports_runtime_path_constants(tmp_path: Path) -> None:
    bad_runtime = tmp_path / "runtime" / "workflow" / "bad_paths.py"
    bad_runtime.parent.mkdir(parents=True)
    bad_runtime.write_text(
        "def bad():\n"
        "    registry = \"db/registries/registry.duckdb\"\n"
        "    duckdb = \"db/rag/ariadne-knowledge.duckdb\"\n"
        "    source = \"work/db/ariadne-knowledge-platform\"\n"
        "    schema = \".ariadne/schemas/context-manifest.schema.json\"\n"
        "    return registry, duckdb, source, schema\n",
        encoding="utf-8",
    )

    findings = workflow_doctor.path_constant_literal_findings(tmp_path)

    assert findings == [
        "runtime/workflow/bad_paths.py:2: use runtime.constants.paths.REGISTRY_DB_PATH",
        "runtime/workflow/bad_paths.py:3: use runtime.constants.paths.DUCKDB_DEFAULT_PATH",
        "runtime/workflow/bad_paths.py:4: use runtime.constants.paths.KNOWLEDGE_SOURCE_REPO",
        "runtime/workflow/bad_paths.py:5: use runtime.constants.schemas constants",
    ]


def test_path_constant_literal_findings_ignores_constants_and_tests(tmp_path: Path) -> None:
    constants = tmp_path / "runtime" / "constants" / "paths.py"
    tests = tmp_path / "runtime" / "tests" / "test_paths.py"
    helper_runtime = tmp_path / "runtime" / "workflow" / "good_paths.py"
    constants.parent.mkdir(parents=True)
    tests.parent.mkdir(parents=True)
    helper_runtime.parent.mkdir(parents=True)
    constants.write_text('REGISTRY_DB_PATH = "db/registries/registry.duckdb"\n', encoding="utf-8")
    tests.write_text('def test_path():\n    assert "db/rag/ariadne-knowledge.duckdb"\n', encoding="utf-8")
    helper_runtime.write_text(
        "from runtime.constants.paths import REGISTRY_DB_PATH\n"
        "def good():\n"
        "    return REGISTRY_DB_PATH.as_posix()\n",
        encoding="utf-8",
    )

    assert workflow_doctor.path_constant_literal_findings(tmp_path) == []


def test_git_attributes_and_uv_startup_findings(tmp_path: Path) -> None:
    assert workflow_doctor.git_attributes_findings(tmp_path) == [".gitattributes"]

    (tmp_path / ".gitattributes").write_text(
        "* text=auto eol=lf\n*.cmd text eol=crlf\n*.bat text eol=crlf\n",
        encoding="utf-8",
    )
    assert workflow_doctor.git_attributes_findings(tmp_path) == []

    assert "runtime/windows-script/uv.cmd" in workflow_doctor.uv_startup_findings(tmp_path)
    script_dir = tmp_path / "runtime" / "windows-script"
    script_dir.mkdir(parents=True)
    (script_dir / "uv.cmd").write_text("@echo off\n", encoding="utf-8")
    (script_dir / "register-uv-path.cmd").write_text("@echo off\n", encoding="utf-8")
    (script_dir / "aiwfctl.cmd").write_text('call "%~dp0uv.cmd" run --project "%REPO_ROOT%runtime"\n', encoding="utf-8")
    (script_dir / "aiwf.ps1").write_text(
        "function Get-AiwfUvPath {}\n"
        "$localUv = Join-Path $RuntimeRoot \"windows-script/uv.cmd\"\n"
        "Invoke-AiwfUv\n",
        encoding="utf-8",
    )

    assert workflow_doctor.uv_startup_findings(tmp_path) == []


def test_workflow_doctor_fail_on_warning_turns_warning_into_fail(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: ["work/issue-1/tmp.txt"])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])
    args = argparse.Namespace(repo_root=str(tmp_path), fail_on_warning=True)

    result = workflow_doctor.run(args)

    assert result["status"] == "fail"
    assert result["warning_count"] == 1
    assert result["warnings"][0]["id"] == "tracked-local-workspace-files"
    assert result["warnings"][0]["next_action"] == "Remove generated work/RAG files from Git tracking or move durable knowledge into work/db."
    assert result["warnings"][0]["repair_command"] == "git rm --cached <path>"
    assert "ignore_condition" in result["warnings"][0]


def test_workflow_doctor_run_reports_all_warning_types(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: ["work/issue-1/tmp.txt"])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: ["runtime/ctl/ctl.py"])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: ["pytest.ini"])
    monkeypatch.setattr(
        workflow_doctor,
        "human_gate_registry_findings",
        lambda repo_root: ["human_gates registry contains $schema"],
    )
    monkeypatch.setattr(
        workflow_doctor,
        "registry_seed_findings",
        lambda repo_root: ["missing:templates/registries/search_terms.json"],
    )
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: ["work/close/improvement/issue-1"])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [".vscode/settings.json:files.encoding"])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [".gitattributes"])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: ["runtime/windows-script/uv.cmd"])
    monkeypatch.setattr(
        workflow_doctor,
        "duckdb_read_model_findings",
        lambda repo_root: ["missing:db/rag/ariadne-knowledge.duckdb"],
    )
    monkeypatch.setattr(
        workflow_doctor,
        "workspace_layout_literal_findings",
        lambda repo_root: ["runtime/workflow/bad_layout.py:3: use context_file"],
    )
    monkeypatch.setattr(
        workflow_doctor,
        "path_constant_literal_findings",
        lambda repo_root: ["runtime/workflow/bad_paths.py:2: use REGISTRY_DB_PATH"],
    )
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: ["missing: runtime/tests/test_new.py::test_new"])
    args = argparse.Namespace(repo_root=str(tmp_path), fail_on_warning=False)

    result = workflow_doctor.run(args)

    assert result["status"] == "warning"
    assert result["warning_count"] == 13
    assert [warning["id"] for warning in result["warnings"]] == [
        "tracked-local-workspace-files",
        "missing-required-files",
        "pytest-runtime-boundary",
        "human-gate-registry-responsibility-boundary",
        "runtime-registry-bootstrap-source",
        "incomplete-close-archive",
        "vscode-utf8-first",
        "git-line-ending-policy",
        "uv-startup-route",
        "rag-duckdb-read-model-missing",
        "workspace-layout-literal",
        "path-constant-literal",
        "pytest-ut-spec-sync",
    ]
    for warning in result["warnings"]:
        assert warning["cause"]
        assert warning["impact"]
        assert warning["next_action"]
        assert warning["repair_command"]
        assert warning["ignore_condition"]
        assert warning["severity"] in {"critical", "high", "medium", "low"}
        assert warning["category"]
        assert isinstance(warning["repairable"], bool)
        assert isinstance(warning["human_review_required"], bool)
    assert result["warnings"][9]["repair_command"] == (
        "aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset"
    )
    assert result["warnings"][9]["repairable"] is True
    assert result["warnings"][9]["human_review_required"] is False
    assert result["warning_summary"]["repairable_count"] == 2
    assert result["warning_summary"]["human_review_count"] == 11
    assert result["warning_summary"]["severity_counts"]["critical"] == 1
    assert result["warning_summary"]["category_counts"]["knowledge-read-model"] == 1
    assert result["schema"]["warning"] == ".ariadne/schemas/workflow-doctor-warning.schema.json"
    assert result["fix_suggestions"][9]["warning_id"] == "rag-duckdb-read-model-missing"
    assert result["fix_suggestions"][9]["suggested_command"] == (
        "aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset"
    )


def test_warning_guidance_uses_rebuild_hint_from_duckdb_paths() -> None:
    guidance = workflow_doctor.warning_guidance(
        "rag-duckdb-read-model-missing",
        [
            "missing:db/rag/ariadne-knowledge.duckdb",
            "source:work/db/ariadne-knowledge-platform",
            "rebuild:aiwfctl rag duckdb rebuild --source-repo work/db/custom-knowledge --reset",
        ],
    )

    assert guidance["repair_command"] == "aiwfctl rag duckdb rebuild --source-repo work/db/custom-knowledge --reset"


def test_workflow_doctor_run_passes_without_warnings(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])
    args = argparse.Namespace(repo_root=str(tmp_path), fail_on_warning=True)

    result = workflow_doctor.run(args)

    assert result == {
        "artifact_type": "workflow-doctor-report",
        "schema": {
            "warning": ".ariadne/schemas/workflow-doctor-warning.schema.json",
        },
        "status": "pass",
        "warning_count": 0,
        "warnings": [],
        "warning_summary": {
            "severity_counts": {},
            "category_counts": {},
            "repairable_count": 0,
            "human_review_count": 0,
            "repairable_warnings": [],
            "human_review_warnings": [],
        },
        "fix_suggestions": [],
        "fix_suggestion_only": False,
        "repairs": [],
        "dry_run": False,
        "gate_restart": {
            "schema_version": "1.0",
            "artifact_type": "gate-restart",
            "gate": "doctor-gate",
            "restart_from": "doctor-gate",
            "restart_reason": "normal-doctor-gate",
            "repair_available": True,
            "repair_command": "aiwfctl doctor --repair-encoding --repair-spec-index --fail-on-warning",
            "status_after_restart": "pass",
            "next_on_pass": "return-to-calling-workflow-after-gate",
            "next_on_fail": "stay-at-gate",
        },
    }


def test_text_boundary_scan_and_repair_recovers_utf8_saved_mojibake(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    original = "\u3042\u3042"
    mojibake = original.encode("utf-8").decode("cp932")
    target = docs / "guide.md"
    target.write_text(f"# {mojibake}\n", encoding="utf-8")

    assert text_boundary.marker_count(mojibake[:1]) == 1
    scan = text_boundary.scan_text_boundary(tmp_path, ["docs"], {".md"})
    assert scan["status"] == "finding"
    assert scan["findings"][0]["kind"] == "semantic-mojibake-marker"
    assert scan["findings"][0]["repairable"] is True

    repair = text_boundary.repair_text_boundary(tmp_path, ["docs"], {".md"})

    assert repair["status"] == "repaired"
    assert repair["remaining_findings"] == []
    assert target.read_text(encoding="utf-8") == f"# {original}\n"
    assert (docs / "guide.md.encoding-bak").exists()


def test_workflow_doctor_repair_encoding_clears_text_boundary_warning(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])
    docs = tmp_path / "docs"
    docs.mkdir()
    original = "\u3042\u3042"
    mojibake = original.encode("utf-8").decode("cp932")
    target = docs / "guide.md"
    target.write_text(f"# {mojibake}\n", encoding="utf-8")

    warning = workflow_doctor.run(
        argparse.Namespace(
            repo_root=str(tmp_path),
            fail_on_warning=True,
            skip_ut_spec_sync=False,
            repair_encoding=False,
            encoding_paths=["docs"],
            encoding_extensions=[".md"],
        )
    )
    repaired = workflow_doctor.run(
        argparse.Namespace(
            repo_root=str(tmp_path),
            fail_on_warning=True,
            skip_ut_spec_sync=False,
            repair_encoding=True,
            encoding_paths=["docs"],
            encoding_extensions=[".md"],
        )
    )

    assert warning["status"] == "fail"
    assert warning["warnings"][0]["id"] == "text-boundary"
    assert warning["gate_restart"]["next_on_fail"] == "stay-at-gate"
    assert repaired["status"] == "pass"
    assert repaired["warning_count"] == 0
    assert repaired["gate_restart"]["restart_from"] == "doctor-gate"
    assert repaired["gate_restart"]["restart_reason"] == "failed-doctor-gate"
    assert repaired["gate_restart"]["repair_available"] is True
    assert repaired["gate_restart"]["repair_command"] == "aiwfctl doctor --repair-encoding --repair-spec-index --fail-on-warning"
    assert repaired["gate_restart"]["next_on_pass"] == "return-to-calling-workflow-after-gate"
    assert repaired["repairs"][0]["repairs"][0]["path"] == "docs/guide.md"
    assert target.read_text(encoding="utf-8") == f"# {original}\n"


def test_workflow_doctor_repair_encoding_dry_run_previews_without_writing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])
    docs = tmp_path / "docs"
    docs.mkdir()
    original = "\u3042\u3042"
    mojibake = original.encode("utf-8").decode("cp932")
    target = docs / "guide.md"
    target.write_text(f"# {mojibake}\n", encoding="utf-8")

    result = workflow_doctor.run(
        argparse.Namespace(
            repo_root=str(tmp_path),
            fail_on_warning=True,
            skip_ut_spec_sync=False,
            repair_encoding=True,
            repair_spec_index=False,
            dry_run=True,
            encoding_paths=["docs"],
            encoding_extensions=[".md"],
        )
    )

    assert result["status"] == "fail"
    assert result["dry_run"] is True
    assert result["gate_restart"]["restart_reason"] == "dry-run-doctor-gate"
    assert result["repairs"][0]["artifact_type"] == "text-boundary-repair-preview"
    assert result["repairs"][0]["status"] == "dry-run"
    assert result["repairs"][0]["would_write"] is True
    assert result["repairs"][0]["planned_count"] == 1
    assert result["repairs"][0]["repairs"][0]["path"] == "docs/guide.md"
    assert result["repairs"][0]["repairs"][0]["written"] is False
    assert target.read_text(encoding="utf-8") == f"# {mojibake}\n"
    assert not (docs / "guide.md.encoding-bak").exists()


def test_workflow_doctor_repair_spec_index_scaffolds_missing_cases(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])
    runtime_root = tmp_path / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_new():
    assert True
""",
        encoding="utf-8",
    )
    spec_path = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text("# Spec index\n", encoding="utf-8")
    monkeypatch.setattr(
        workflow_doctor.pytest_ut_spec_sync,
        "collect_pytest_nodes",
        lambda runtime_root: ["runtime/tests/test_sample.py::test_new"],
    )

    result = workflow_doctor.run(
        argparse.Namespace(
            repo_root=str(tmp_path),
            fail_on_warning=True,
            skip_ut_spec_sync=False,
            repair_encoding=False,
            repair_spec_index=True,
            encoding_paths=[],
            encoding_extensions=[".md"],
        )
    )

    assert result["status"] == "pass"
    assert result["repairs"][0]["artifact_type"] == "pytest-ut-spec-index-repair"
    assert result["repairs"][0]["repairs"][0]["node_id"] == "runtime/tests/test_sample.py::test_new"
    assert (spec_path.with_name("cases") / "test_sample.md").exists()


def test_workflow_doctor_repair_spec_index_dry_run_previews_without_scaffolding(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: ["missing: runtime/tests/test_sample.py::test_new"])
    monkeypatch.setattr(
        workflow_doctor,
        "repair_ut_spec_index",
        lambda repo_root: (_ for _ in ()).throw(AssertionError("repair must not run during dry-run")),
    )

    result = workflow_doctor.run(
        argparse.Namespace(
            repo_root=str(tmp_path),
            fail_on_warning=False,
            skip_ut_spec_sync=False,
            repair_encoding=False,
            repair_spec_index=True,
            dry_run=True,
            encoding_paths=["docs"],
            encoding_extensions=[".md"],
        )
    )

    assert result["status"] == "warning"
    assert result["dry_run"] is True
    assert result["repairs"][0]["artifact_type"] == "pytest-ut-spec-index-repair-preview"
    assert result["repairs"][0]["status"] == "dry-run"
    assert result["repairs"][0]["would_write"] is True
    assert result["repairs"][0]["planned_count"] == 1
    assert result["repairs"][0]["findings"] == ["missing: runtime/tests/test_sample.py::test_new"]


def test_workflow_doctor_fix_suggestion_only_does_not_run_repairs(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])
    docs = tmp_path / "docs"
    docs.mkdir()
    original = "\u3042\u3042"
    mojibake = original.encode("utf-8").decode("cp932")
    target = docs / "guide.md"
    target.write_text(f"# {mojibake}\n", encoding="utf-8")

    result = workflow_doctor.run(
        argparse.Namespace(
            repo_root=str(tmp_path),
            fail_on_warning=False,
            skip_ut_spec_sync=False,
            repair_encoding=True,
            repair_spec_index=True,
            dry_run=False,
            fix_suggestion_only=True,
            encoding_paths=["docs"],
            encoding_extensions=[".md"],
        )
    )

    assert result["status"] == "warning"
    assert result["fix_suggestion_only"] is True
    assert result["repairs"] == []
    assert result["warnings"][0]["id"] == "text-boundary"
    assert result["fix_suggestions"][0]["suggested_command"] == "aiwfctl doctor --repair-encoding --fail-on-warning"
    assert target.read_text(encoding="utf-8") == f"# {mojibake}\n"


def test_workflow_doctor_main_prints_pass_json(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])

    code = workflow_doctor.main(["--repo-root", str(tmp_path)])

    captured = capsys.readouterr()
    assert code == 0
    assert '"status": "pass"' in captured.out


def test_workflow_doctor_main_returns_one_on_fail_on_warning(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(workflow_doctor, "tracked_policy_violations", lambda repo_root: ["rag/chunks/chunks.jsonl"])
    monkeypatch.setattr(workflow_doctor, "missing_required_files", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "ut_spec_sync_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])

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
    monkeypatch.setattr(workflow_doctor, "pytest_runtime_boundary_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "human_gate_registry_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "registry_seed_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "close_archive_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "vscode_utf8_first_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "git_attributes_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "uv_startup_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "duckdb_read_model_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "workspace_layout_literal_findings", lambda repo_root: [])
    monkeypatch.setattr(workflow_doctor, "path_constant_literal_findings", lambda repo_root: [])
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
