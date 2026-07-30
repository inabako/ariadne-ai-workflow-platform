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
        "CITATION.cff",
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
        "docs/legal/README.md",
        "docs/legal/license-policy.md",
        "docs/legal/evidence/legal-review-items.md",
        "docs/legal/evidence/dependency-license-report.json",
        "docs/legal/evidence/license-boundary-report.json",
        "docs/legal/evidence/release-license-check.json",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        "runtime/release/__init__.py",
        "runtime/release/validation.py",
        "runtime/release/manifest.py",
    ]
    missing = [path for path in required if not (root / path).exists()]
    assert missing == []


def test_validate_release_reports_current_repo_as_pass_with_warnings() -> None:
    root = repo_root()
    module = load_module(root / "runtime" / "release" / "validation.py", "validate_release_under_test")
    errors, warnings = module.validate(root)

    assert errors == []
    assert not any(finding.id == "license-policy-human-review" for finding in warnings)


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
