from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import gate_restart, registry_store, text_boundary  # noqa: E402
from runtime.common import find_repo_root, relative_to_repo  # noqa: E402
from runtime.constants.paths import REGISTRY_DB_PATH  # noqa: E402
from runtime.constants.schemas import (  # noqa: E402
    CONTEXT_MANIFEST_SCHEMA,
    CORRECTIVE_ACTION_REPORT_SCHEMA,
    ENVIRONMENT_SELECTION_SCHEMA,
    EXECUTION_PLAN_SCHEMA,
    GATE_RESTART_SCHEMA,
    GITHUB_OPERATION_GATE_SCHEMA,
    HUMAN_GATES_SCHEMA,
    PYTEST_UT_SPEC_SYNC_REPORT_SCHEMA,
    RAG_BUILD_RUN_SCHEMA,
    RAG_DISPATCH_PLAN_SCHEMA,
    RAG_LOAD_DISPATCH_SCHEMA,
    REALTIME_IAC_HANDOFF_SCHEMA,
    RUNTIME_CONTEXT_SCHEMA,
    RUNTIME_METRICS_SCHEMA,
    TOOL_CANDIDATES_SCHEMA,
    TOOL_SELECTION_SCHEMA,
    VSCODE_ENVIRONMENT_STATE_SCHEMA,
    WORKFLOW_ENVIRONMENT_PROFILES_SCHEMA,
    WORKFLOW_HELP_SCHEMA,
    WORKFLOW_SELECTION_SCHEMA,
)
from runtime.constants.workspace import (  # noqa: E402
    work_dir_for_id,
)
from runtime.rag import duckdb_store  # noqa: E402
from runtime.tools import pytest_ut_spec_sync  # noqa: E402
from runtime.workflow.close_archive import REPORT_FILES  # noqa: E402

WORKSPACE_LAYOUT_LITERAL_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"repo_root\s*/\s*['\"]work['\"]", "use runtime.constants.workspace.work_dir_for_id"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]context['\"]", "use context_dir_for_work_dir or context_file"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]process-report['\"]", "use process_report_dir_for_work_dir"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]reports['\"]", "use reports_dir_for_work_dir"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]test-evidence['\"]", "use test_evidence_dir_for_work_dir"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]test-environment['\"]", "use test_environment_dir_for_work_dir"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]design-document['\"]", "use design_document_dir_for_work_dir"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]requirements['\"]", "use requirements_dir_for_work_dir"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]implementation['\"]", "use implementation_dir_for_work_dir"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]git-worktree['\"]", "use git_worktree_dir_for_work_dir"),
    (r"\b(?:work_dir|work_path|base)\s*/\s*['\"]source['\"]\s*/\s*['\"]repository['\"]", "use target_repository_dir_for_work_dir"),
)

WORKSPACE_LAYOUT_GUARD_EXCLUDED_PARTS = {
    "constants",
    "tests",
    "__pycache__",
}

PATH_CONSTANT_LITERAL_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"['\"]db/registries/registry\.duckdb['\"]", "use runtime.constants.paths.REGISTRY_DB_PATH"),
    (r"['\"]db/rag/ariadne-knowledge\.duckdb['\"]", "use runtime.constants.paths.DUCKDB_DEFAULT_PATH"),
    (r"['\"]work/db/ariadne-knowledge-platform['\"]", "use runtime.constants.paths.KNOWLEDGE_SOURCE_REPO"),
    (r"['\"]\.github/schemas/[^'\"]+\.schema\.json['\"]", "use runtime.constants.schemas constants"),
)


def run_git(repo_root: Path, args: list[str]) -> list[str]:
    result = subprocess.run(["git", *args], cwd=repo_root, text=True, capture_output=True, check=False)
    if result.returncode not in {0, 1}:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def tracked_policy_violations(repo_root: Path) -> list[str]:
    tracked = run_git(repo_root, ["ls-files", "work", "rag"])
    violations: list[str] = []
    for item in tracked:
        normalized = item.replace("\\", "/")
        if normalized.startswith("rag/"):
            violations.append(normalized)
            continue
        if normalized.startswith("work/") and not normalized.endswith("/README.md"):
            violations.append(normalized)
    return violations


def missing_required_files(repo_root: Path) -> list[str]:
    required = [
        ".gitignore",
        "runtime/pytest.ini",
        "runtime/tools/aiwfctl.cmd",
        "runtime/tools/register-aiwfctl-path.cmd",
        "runtime/common/ctl.py",
        "runtime/common/registry_store.py",
        "runtime/workflow/close_archive.py",
        "runtime/workflow/noise_reduction.py",
        "runtime/workflow/workflow_state.py",
        "runtime/workflow/context_first.py",
        "runtime/workflow/dispatcher_context.py",
        "runtime/workflow/iac_handoff_context.py",
        "runtime/workflow/human_gate_policy.py",
        "runtime/observability/schema.py",
        "runtime/observability/logger.py",
        "runtime/observability/metrics.py",
        "runtime/tests/test_observability_metrics.py",
        "runtime/tools/pytest_ut_spec_sync.py",
        "runtime/tests/test_pytest_ut_spec_sync.py",
        "skills/runtime-health-check/SKILL.md",
        ".github/prompts/runtime-health-check.prompt.md",
        ".github/agents/runtime-quality-gate-agent.prompt.md",
        "docs/workflows/runtime-health-check.md",
        "db/registries/README.md",
        REGISTRY_DB_PATH.as_posix(),
        HUMAN_GATES_SCHEMA,
        WORKFLOW_HELP_SCHEMA,
        GATE_RESTART_SCHEMA,
        TOOL_CANDIDATES_SCHEMA,
        CONTEXT_MANIFEST_SCHEMA,
        PYTEST_UT_SPEC_SYNC_REPORT_SCHEMA,
        ENVIRONMENT_SELECTION_SCHEMA,
        WORKFLOW_SELECTION_SCHEMA,
        TOOL_SELECTION_SCHEMA,
        RUNTIME_CONTEXT_SCHEMA,
        RUNTIME_METRICS_SCHEMA,
        EXECUTION_PLAN_SCHEMA,
        REALTIME_IAC_HANDOFF_SCHEMA,
        VSCODE_ENVIRONMENT_STATE_SCHEMA,
        WORKFLOW_ENVIRONMENT_PROFILES_SCHEMA,
        GITHUB_OPERATION_GATE_SCHEMA,
        CORRECTIVE_ACTION_REPORT_SCHEMA,
        RAG_BUILD_RUN_SCHEMA,
        RAG_DISPATCH_PLAN_SCHEMA,
        RAG_LOAD_DISPATCH_SCHEMA,
        "runtime/workflow/gui_mode.py",
        "templates/workflows/noise-reduction/README.md",
        "docs/reference/human-gates.md",
        "docs/reference/context-first-architecture.md",
        "docs/reference/environment-selection.md",
        "runtime/tests/test_close_archive.py",
        "runtime/tests/test_rag_dispatcher.py",
        "runtime/tests/test_ctl_help.py",
    ]
    return [path for path in required if not (repo_root / path).exists()]


def pytest_runtime_boundary_findings(repo_root: Path) -> list[str]:
    findings: list[str] = []
    root_config = repo_root / "pytest.ini"
    root_cache = repo_root / ".pytest_cache"
    runtime_config = repo_root / "runtime" / "pytest.ini"
    runtime_cache = repo_root / "runtime" / ".pytest_cache"
    if root_config.exists():
        findings.append("pytest.ini")
    if root_cache.exists():
        findings.append(".pytest_cache")
    if not runtime_config.exists():
        findings.append("missing:runtime/pytest.ini")
    else:
        text = runtime_config.read_text(encoding="utf-8-sig")
        if "cache_dir = .pytest_cache" not in text:
            findings.append("runtime/pytest.ini:cache_dir")
    if not runtime_cache.exists():
        findings.append("missing:runtime/.pytest_cache")
    return findings


def human_gate_registry_findings(repo_root: Path) -> list[str]:
    db_path = registry_store.registry_db_path(repo_root)
    legacy_path = registry_store.legacy_registry_dir(repo_root) / "human_gates.json"
    if not db_path.exists() and not legacy_path.exists():
        return []
    try:
        data = registry_store.load_registry(repo_root, "human_gates", {})
    except Exception as exc:
        return [f"{registry_store.REGISTRY_DB_PATH.as_posix()} could not load human_gates: {exc}"]
    if not isinstance(data, dict):
        return ["human_gates registry must be an object"]
    findings: list[str] = []
    if "$schema" in data:
        findings.append("human_gates registry contains $schema")
    if "schema_version" in data:
        findings.append("human_gates registry contains schema_version")
    if "registry_version" not in data:
        findings.append("human_gates registry does not contain registry_version")
    return findings


def close_archive_findings(repo_root: Path) -> list[str]:
    findings: list[str] = []
    close_root = work_dir_for_id(repo_root, "close")
    if not close_root.exists():
        return findings
    for archive_dir in [path for path in close_root.rglob("*") if path.is_dir()]:
        children = {child.name for child in archive_dir.iterdir() if child.is_file()}
        if children & set(REPORT_FILES) and not set(REPORT_FILES).issubset(children):
            findings.append(relative_to_repo(repo_root, archive_dir))
    return findings


def vscode_utf8_first_findings(repo_root: Path) -> list[str]:
    findings: list[str] = []
    settings_path = repo_root / ".vscode" / "settings.json"
    if not settings_path.exists():
        return [".vscode/settings.json"]
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return [f".vscode/settings.json invalid JSON: {exc.msg}"]
    if not isinstance(settings, dict):
        return [".vscode/settings.json is not a JSON object"]

    expected_root = {
        "files.encoding": "utf8",
        "files.autoGuessEncoding": False,
        "files.eol": "\n",
    }
    for key, expected in expected_root.items():
        if settings.get(key) != expected:
            findings.append(f".vscode/settings.json:{key}")

    terminal_env = settings.get("terminal.integrated.env.windows")
    if not isinstance(terminal_env, dict):
        findings.append(".vscode/settings.json:terminal.integrated.env.windows")
    else:
        expected_env = {
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "AIWF_TEXT_ENCODING": "utf-8",
        }
        for key, expected in expected_env.items():
            if terminal_env.get(key) != expected:
                findings.append(f".vscode/settings.json:terminal.integrated.env.windows.{key}")

    profiles = settings.get("terminal.integrated.profiles.windows")
    if isinstance(profiles, dict):
        for name, profile in profiles.items():
            if not isinstance(profile, dict) or profile.get("source") != "PowerShell":
                continue
            args = " ".join(str(item) for item in profile.get("args", []))
            for token in ["InputEncoding", "OutputEncoding", "$OutputEncoding", "chcp 65001"]:
                if token not in args:
                    findings.append(f".vscode/settings.json:terminal profile {name} missing {token}")
    else:
        findings.append(".vscode/settings.json:terminal.integrated.profiles.windows")

    editorconfig = repo_root / ".editorconfig"
    if not editorconfig.exists():
        findings.append(".editorconfig")
    else:
        editorconfig_text = editorconfig.read_text(encoding="utf-8-sig")
        required_snippets = [
            "charset = utf-8",
            "end_of_line = lf",
            "[*.{bat,cmd}]",
            "charset = unset",
            "end_of_line = crlf",
        ]
        for snippet in required_snippets:
            if snippet not in editorconfig_text:
                findings.append(f".editorconfig:{snippet}")
    return findings


def duckdb_read_model_findings(repo_root: Path) -> list[str]:
    source_repo = (repo_root / duckdb_store.DEFAULT_SOURCE_REPO_PATH).resolve()
    if not source_repo.exists():
        return []
    source_dirs = duckdb_store.source_repo_standard_sources(repo_root, source_repo)
    has_source_records = any(source_dir.exists() and any(source_dir.rglob("*.json")) for source_dir in source_dirs)
    if not has_source_records:
        return []
    db_path = (repo_root / duckdb_store.DEFAULT_DB_PATH).resolve()
    if db_path.exists():
        return []
    return [
        f"missing:{relative_to_repo(repo_root, db_path)}",
        f"source:{relative_to_repo(repo_root, source_repo)}",
        f"rebuild:aiwfctl knowledge rebuild --source-repo {duckdb_store.DEFAULT_SOURCE_REPO_PATH.as_posix()} --reset",
    ]


def workspace_layout_literal_findings(repo_root: Path) -> list[str]:
    runtime_root = repo_root / "runtime"
    if not runtime_root.exists():
        return []
    compiled = [(re.compile(pattern), hint) for pattern, hint in WORKSPACE_LAYOUT_LITERAL_PATTERNS]
    findings: list[str] = []
    for path in sorted(runtime_root.rglob("*.py"), key=lambda item: item.as_posix()):
        relative_parts = set(path.relative_to(runtime_root).parts)
        if relative_parts & WORKSPACE_LAYOUT_GUARD_EXCLUDED_PARTS:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            for pattern, hint in compiled:
                if pattern.search(line):
                    findings.append(f"{relative_to_repo(repo_root, path)}:{line_number}: {hint}")
                    break
    return findings


def path_constant_literal_findings(repo_root: Path) -> list[str]:
    runtime_root = repo_root / "runtime"
    if not runtime_root.exists():
        return []
    compiled = [(re.compile(pattern), hint) for pattern, hint in PATH_CONSTANT_LITERAL_PATTERNS]
    findings: list[str] = []
    for path in sorted(runtime_root.rglob("*.py"), key=lambda item: item.as_posix()):
        relative_parts = set(path.relative_to(runtime_root).parts)
        if relative_parts & WORKSPACE_LAYOUT_GUARD_EXCLUDED_PARTS:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            for pattern, hint in compiled:
                if pattern.search(line):
                    findings.append(f"{relative_to_repo(repo_root, path)}:{line_number}: {hint}")
                    break
    return findings


def ut_spec_sync_findings(repo_root: Path) -> list[str]:
    spec_path = repo_root / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    runtime_root = repo_root / "runtime"
    if not spec_path.exists():
        return [relative_to_repo(repo_root, spec_path)]
    if not runtime_root.exists():
        return [relative_to_repo(repo_root, runtime_root)]
    result = pytest_ut_spec_sync.check_spec(spec_path, runtime_root)
    if result.get("status") == "ok":
        return []
    findings: list[str] = []
    if result.get("missing_in_spec"):
        findings.extend(f"missing: {node}" for node in result["missing_in_spec"])
    if result.get("stale_in_spec"):
        findings.extend(f"stale: {node}" for node in result["stale_in_spec"])
    if result.get("order_matches") is False:
        findings.append("pytest collection order does not match UT spec order")
    if result.get("bad_input_position"):
        findings.extend(f"bad input position: {case_id}" for case_id in result["bad_input_position"])
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run lightweight workflow repository health checks.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--fail-on-warning", action="store_true")
    parser.add_argument("--skip-ut-spec-sync", action="store_true", help="Skip pytest UT specification sync check.")
    parser.add_argument("--repair-encoding", action="store_true", help="Repair safe text-boundary findings before returning doctor status.")
    parser.add_argument(
        "--encoding-paths",
        nargs="+",
        default=text_boundary.DEFAULT_PATHS,
        help="Text-boundary paths to scan or repair.",
    )
    parser.add_argument(
        "--encoding-extensions",
        nargs="+",
        default=sorted(text_boundary.TEXT_EXTENSIONS),
        help="Text extensions included in text-boundary scan or repair.",
    )
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    warnings = []
    repairs = []
    tracked_violations = tracked_policy_violations(repo_root)
    if tracked_violations:
        warnings.append(
            {
                "id": "tracked-local-workspace-files",
                "message": "work/ 配下でREADME以外、または rag/ 配下のファイルがGit管理されています。",
                "paths": tracked_violations,
            }
        )
    missing = missing_required_files(repo_root)
    if missing:
        warnings.append({"id": "missing-required-files", "message": "必須workflow fileが不足しています。", "paths": missing})
    pytest_boundary_findings = pytest_runtime_boundary_findings(repo_root)
    if pytest_boundary_findings:
        warnings.append(
            {
                "id": "pytest-runtime-boundary",
                "message": "pytest config and cache must stay under runtime/. Root pytest.ini or .pytest_cache is workflow noise.",
                "paths": pytest_boundary_findings,
            }
        )
    registry_findings = human_gate_registry_findings(repo_root)
    if registry_findings:
        warnings.append(
            {
                "id": "human-gate-registry-responsibility-boundary",
                "message": "Human Gate Registry実体にschema責務の表現が混在しています。",
                "paths": registry_findings,
            }
        )
    close_findings = close_archive_findings(repo_root)
    if close_findings:
        warnings.append({"id": "incomplete-close-archive", "message": "標準8ファイルが揃っていないclose archiveがあります。", "paths": close_findings})
    utf8_findings = vscode_utf8_first_findings(repo_root)
    if utf8_findings:
        warnings.append(
            {
                "id": "vscode-utf8-first",
                "message": "VSCode workspace UTF-8 first settings are incomplete.",
                "paths": utf8_findings,
            }
        )
    duckdb_findings = duckdb_read_model_findings(repo_root)
    if duckdb_findings:
        warnings.append(
            {
                "id": "rag-duckdb-read-model-missing",
                "message": "knowledge sourceが存在しますが、生成DuckDB read modelが見つかりません。rag cleanup後はrebuildが必要です。",
                "paths": duckdb_findings,
            }
        )
    layout_findings = workspace_layout_literal_findings(repo_root)
    if layout_findings:
        warnings.append(
            {
                "id": "workspace-layout-literal",
                "message": "runtime implementation contains hard-coded work layout path literals. Use runtime.constants.workspace helpers first.",
                "paths": layout_findings,
            }
        )
    path_constant_findings = path_constant_literal_findings(repo_root)
    if path_constant_findings:
        warnings.append(
            {
                "id": "path-constant-literal",
                "message": "runtime implementation contains hard-coded canonical path literals. Use runtime.constants.paths or runtime.constants.schemas first.",
                "paths": path_constant_findings,
            }
        )
    if not getattr(args, "skip_ut_spec_sync", False):
        sync_findings = ut_spec_sync_findings(repo_root)
        if sync_findings:
            warnings.append(
                {
                    "id": "pytest-ut-spec-sync",
                    "message": "pytest実体とUT仕様書の同期にズレがあります。",
                    "paths": sync_findings,
                }
            )
    encoding_paths = list(getattr(args, "encoding_paths", None) or text_boundary.DEFAULT_PATHS)
    encoding_extensions = text_boundary.normalize_extensions(getattr(args, "encoding_extensions", None))
    if getattr(args, "repair_encoding", False):
        repair_result = text_boundary.repair_text_boundary(repo_root, encoding_paths, encoding_extensions)
        repairs.append(repair_result)
        boundary_findings = repair_result.get("remaining_findings", [])
    else:
        boundary_scan = text_boundary.scan_text_boundary(repo_root, encoding_paths, encoding_extensions)
        boundary_findings = boundary_scan.get("findings", [])
    if boundary_findings:
        warnings.append(
            {
                "id": "text-boundary",
                "message": "Text boundary findings remain. Run doctor with --repair-encoding for repairable encoding issues, then rerun doctor.",
                "paths": [
                    f"{item.get('path')}:{item.get('line')}: {item.get('kind')}"
                    for item in boundary_findings
                    if isinstance(item, dict)
                ],
            }
        )
    status = "fail" if warnings and args.fail_on_warning else "warning" if warnings else "pass"
    return {
        "status": status,
        "warning_count": len(warnings),
        "warnings": warnings,
        "repairs": repairs,
        "gate_restart": gate_restart.build_gate_restart(
            "doctor-gate",
            restart_reason="failed-doctor-gate" if repairs else "normal-doctor-gate",
            repair_available=True,
            repair_command="aiwfctl doctor --repair-encoding --fail-on-warning",
            status_after_restart=status,
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
