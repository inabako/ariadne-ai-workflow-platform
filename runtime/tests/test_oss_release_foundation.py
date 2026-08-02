from __future__ import annotations

import importlib.util
import json
import runpy
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_oss_release_foundation_files_exist() -> None:
    root = repo_root()
    required = [
        ".gitattributes",
        "CITATION.cff",
        "AGENTS.md",
        "LICENSES/AGPL-3.0-or-later.txt",
        "REUSE.toml",
        "CHANGELOG.md",
        "CHANGELOG.en.md",
        "CONTRIBUTING.md",
        "CONTRIBUTING.en.md",
        "SECURITY.md",
        "SECURITY.en.md",
        "NOTICE",
        "NOTICE.ja",
        "docs/architecture/overview.md",
        "docs/architecture/aiwfctl-architecture.md",
        "docs/architecture/runtime-architecture.md",
        "docs/architecture/workflow-dispatch.md",
        "docs/architecture/state-and-artifact-management.md",
        "docs/architecture/evidence-and-completion.md",
        "docs/architecture/human-gate.md",
        "docs/architecture/retry-and-resume.md",
        "docs/release/release-policy.md",
        "docs/release/release-checklist.md",
        "docs/release/versioning-policy.md",
        "docs/citation/citation-guide.md",
        "docs/security/scancode-github-actions.md",
        "docs/legal/README.md",
        "docs/legal/license-policy.md",
        "docs/legal/evidence/legal-review-items.md",
        "docs/legal/evidence/dependency-license-report.json",
        "docs/legal/evidence/license-boundary-report.json",
        "docs/legal/evidence/release-license-check.json",
        "docs/legal/evidence/reuse-lint-local-rehearsal.md",
        ".github/copilot-instructions.md",
        ".github/instructions/ariadne.instructions.md",
        ".github/prompts/ariadne-workflows.prompt.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/workflows/scancode.yml",
        ".github/workflows/reuse-lint.yml",
        "runtime/release/__init__.py",
        "runtime/release/validation.py",
        "runtime/release/manifest.py",
    ]
    missing = [path for path in required if not (root / path).exists()]
    assert missing == []


def test_gitattributes_documents_line_ending_policy() -> None:
    root = repo_root()
    text = (root / ".gitattributes").read_text(encoding="utf-8")

    assert "line-ending normalization" in text
    assert "* text=auto eol=lf" in text
    assert "*.cmd text eol=crlf" in text
    assert "*.png binary" in text


def test_github_copilot_bridge_files_point_to_ariadne_source_of_truth() -> None:
    root = repo_root()
    copilot = (root / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
    prompt = (root / ".github" / "prompts" / "ariadne-workflows.prompt.md").read_text(encoding="utf-8")

    assert "薄い bridge" in copilot
    assert "workflow 本体ではありません" in copilot
    assert ".ariadne/prompts/*.prompt.md" in copilot
    assert ".ariadne/agents/*.prompt.md" in copilot
    assert "source of truth" in copilot

    assert "Ariadne Workflow Bridge" in prompt
    assert ".ariadne/prompts/" in prompt
    assert ".ariadne/agents/" in prompt
    assert "#file:../../AGENTS.md" in prompt


def test_ariadne_assets_do_not_point_to_legacy_github_ai_asset_paths() -> None:
    root = repo_root()
    forbidden = [
        ".github/agents",
        ".github/prompts/",
        ".github/schemas",
        ".github/shared",
        ".github\\agents",
        ".github\\prompts",
        ".github\\schemas",
        ".github\\shared",
    ]
    offenders: list[str] = []
    for path in (root / ".ariadne").rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        if any(token in text for token in forbidden):
            offenders.append(path.relative_to(root).as_posix())

    assert offenders == []


def test_validate_release_reports_current_repo_as_pass_with_warnings() -> None:
    root = repo_root()
    module = load_module(root / "runtime" / "release" / "validation.py", "validate_release_under_test")
    errors, warnings = module.validate(root)

    assert errors == []
    assert not any(finding.id == "license-policy-human-review" for finding in warnings)


def test_scancode_workflow_is_manual_only_and_read_only() -> None:
    root = repo_root()
    workflow = root / ".github" / "workflows" / "scancode.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "name: ScanCode License Audit" in text
    assert "workflow_dispatch:" in text
    assert "pull_request:" not in text
    assert "push:" not in text
    assert "contents: read" in text
    assert "scancode-toolkit==${SCANCODE_VERSION}" in text
    assert "SCANCODE_VERSION: \"32.5.0\"" in text
    assert "actions/checkout@v4" in text
    assert "actions/setup-python@v5" in text
    assert "actions/upload-artifact@v4" in text
    assert "SCANCODE_OUTPUT_DIR: scancode-output" in text
    assert "catthehacker/ubuntu:act-22.04" in (root / "docs" / "security" / "scancode-github-actions.md").read_text(
        encoding="utf-8"
    )
    assert "--json-pp \"${SCANCODE_OUTPUT_DIR}/scancode-results.json\"" in text
    assert "--html \"${SCANCODE_OUTPUT_DIR}/scancode-results.html\"" in text
    assert "execution-metadata.json" in text
    assert "\"scannerVersion\": scanner_version" in text
    assert "\"scannerVersionOutput\": scanner_version_output" in text
    assert "scancode-summary.md" in text
    assert "name: ariadne-scancode-results" in text
    assert "path: scancode-output/" in text
    assert "if-no-files-found: error" in text
    assert "retention-days: 30" in text


def test_reuse_lint_workflow_is_manual_only_read_only_and_uploads_evidence() -> None:
    root = repo_root()
    workflow = root / ".github" / "workflows" / "reuse-lint.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "name: REUSE Lint" in text
    assert "workflow_dispatch:" in text
    assert "pull_request:" not in text
    assert "push:" not in text
    assert "contents: read" in text
    assert "REUSE_VERSION: \"6.2.0\"" in text
    assert "PYTHON_VERSION: \"3.12\"" in text
    assert "REUSE_OUTPUT_DIR: reuse-lint-output" in text
    assert "actions/checkout@v4" in text
    assert "actions/setup-python@v5" in text
    assert "actions/upload-artifact@v4" in text
    assert "reuse[charset-normalizer]==${REUSE_VERSION}" in text
    assert "reuse lint > \"${REUSE_OUTPUT_DIR}/reuse-lint.txt\" 2>&1" in text
    assert "execution-metadata.json" in text
    assert "reuse-lint-summary.md" in text
    assert "name: ariadne-reuse-lint-results" in text
    assert "path: reuse-lint-output/" in text
    assert "if-no-files-found: error" in text
    assert "retention-days: 30" in text
    assert "Fail on REUSE lint findings" in text


def test_reuse_metadata_scaffold_covers_repository_files() -> None:
    root = repo_root()
    reuse_toml = (root / "REUSE.toml").read_text(encoding="utf-8")
    license_text = (root / "LICENSES" / "AGPL-3.0-or-later.txt").read_text(encoding="utf-8")

    assert "SPDX-FileCopyrightText" in reuse_toml
    assert "SPDX-License-Identifier" in reuse_toml
    assert "2026 ARIADNE contributors" in reuse_toml
    assert "version = 1" in reuse_toml
    assert 'path = ["*", "**/*"]' in reuse_toml
    assert 'SPDX-FileCopyrightText = "2026 ARIADNE contributors"' in reuse_toml
    assert 'SPDX-License-Identifier = "AGPL-3.0-or-later"' in reuse_toml
    assert "GNU AFFERO GENERAL PUBLIC LICENSE" in license_text


def test_license_audit_local_outputs_are_ignored() -> None:
    root = repo_root()
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")

    assert "scancode-output/" in gitignore
    assert "reuse-lint-output/" in gitignore
    assert ".act-artifacts/" in gitignore


def test_vscode_tasks_include_license_audit_act_rehearsals() -> None:
    root = repo_root()
    tasks = json.loads((root / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
    by_label = {task["label"]: task for task in tasks["tasks"]}

    list_task = by_label["ARIADNE: List ScanCode GitHub Actions Jobs"]
    rehearse_task = by_label["ARIADNE: Rehearse ScanCode Workflow"]
    reuse_list_task = by_label["ARIADNE: List REUSE Lint GitHub Actions Jobs"]
    reuse_rehearse_task = by_label["ARIADNE: Rehearse REUSE Lint Workflow"]

    assert list_task["command"] == "act"
    assert list_task["type"] == "shell"
    assert list_task["args"] == [
        "workflow_dispatch",
        "--list",
        "-W",
        "${workspaceFolder}/.github/workflows/scancode.yml",
        "-P",
        "ubuntu-latest=catthehacker/ubuntu:act-22.04",
    ]
    assert list_task["options"]["cwd"] == "${workspaceFolder}"
    assert list_task["problemMatcher"] == []

    assert rehearse_task["command"] == "act"
    assert rehearse_task["type"] == "shell"
    assert rehearse_task["args"] == [
        "workflow_dispatch",
        "-W",
        "${workspaceFolder}/.github/workflows/scancode.yml",
        "-j",
        "scancode",
        "-P",
        "ubuntu-latest=catthehacker/ubuntu:act-22.04",
        "--artifact-server-path",
        "${workspaceFolder}/.act-artifacts",
    ]
    assert rehearse_task["options"]["cwd"] == "${workspaceFolder}"
    assert rehearse_task["problemMatcher"] == []

    assert reuse_list_task["command"] == "act"
    assert reuse_list_task["type"] == "shell"
    assert reuse_list_task["args"] == [
        "workflow_dispatch",
        "--list",
        "-W",
        "${workspaceFolder}/.github/workflows/reuse-lint.yml",
        "-P",
        "ubuntu-latest=catthehacker/ubuntu:act-22.04",
    ]
    assert reuse_list_task["options"]["cwd"] == "${workspaceFolder}"
    assert reuse_list_task["problemMatcher"] == []

    assert reuse_rehearse_task["command"] == "act"
    assert reuse_rehearse_task["type"] == "shell"
    assert reuse_rehearse_task["args"] == [
        "workflow_dispatch",
        "-W",
        "${workspaceFolder}/.github/workflows/reuse-lint.yml",
        "-j",
        "reuse-lint",
        "-P",
        "ubuntu-latest=catthehacker/ubuntu:act-22.04",
        "--artifact-server-path",
        "${workspaceFolder}/.act-artifacts",
    ]
    assert reuse_rehearse_task["options"]["cwd"] == "${workspaceFolder}"
    assert reuse_rehearse_task["problemMatcher"] == []


def test_validate_release_cli_json_output() -> None:
    root = repo_root()
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "runtime.ctl.ctl",
            "release",
            "validate",
            "--json",
        ],
        check=False,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["status"] == "pass"
    assert not any(item["id"] == "license-policy-human-review" for item in payload["warnings"])


def test_release_manifest_contains_stable_required_fields() -> None:
    root = repo_root()
    module = load_module(root / "runtime" / "release" / "manifest.py", "build_release_manifest_under_test")
    manifest = module.build_manifest(root, "0.1.0", "v0.1.0", ["LICENSE"], "2026-07-30T00:00:00+00:00")

    assert manifest["project_name"] == "ARIADNE"
    assert manifest["version"] == "0.1.0"
    assert manifest["tag"] == "v0.1.0"
    assert manifest["license"] == "AGPL-3.0-or-later"
    assert manifest["generated_at_utc"] == "2026-07-30T00:00:00+00:00"
    assert manifest["artifact_list"][0]["path"] == "LICENSE"
    assert len(manifest["artifact_list"][0]["sha256"]) == 64
    assert "docs/architecture/overview.md" in manifest["documentation_list"]


def test_release_manifest_is_reproducible_with_fixed_timestamp() -> None:
    root = repo_root()
    module = load_module(root / "runtime" / "release" / "manifest.py", "build_release_manifest_repro_under_test")
    first = module.build_manifest(root, "0.1.0", "v0.1.0", ["LICENSE"], "2026-07-30T00:00:00+00:00")
    second = module.build_manifest(root, "0.1.0", "v0.1.0", ["LICENSE"], "2026-07-30T00:00:00+00:00")

    assert first == second


def test_release_runtime_modules_are_executable() -> None:
    root = repo_root()
    assert runpy.run_path(str(root / "runtime" / "release" / "validation.py"))["build_parser"]
    assert runpy.run_path(str(root / "runtime" / "release" / "manifest.py"))["build_parser"]
