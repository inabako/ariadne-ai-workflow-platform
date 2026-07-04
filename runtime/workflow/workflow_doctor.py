from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo  # noqa: E402
from runtime.workflow.close_archive import REPORT_FILES  # noqa: E402


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
        if normalized.startswith(("work/", "rag/")) and not normalized.endswith("/README.md"):
            violations.append(normalized)
    return violations


def missing_required_files(repo_root: Path) -> list[str]:
    required = [
        ".gitignore",
        "runtime/pytest.ini",
        "runtime/tools/aiwfctl.cmd",
        "runtime/tools/register-aiwfctl-path.cmd",
        "runtime/ctl.py",
        "runtime/workflow/close_archive.py",
        "runtime/workflow/noise_reduction.py",
        "runtime/workflow/workflow_state.py",
        "runtime/workflow/human_gate_policy.py",
        "runtime/registries/README.md",
        "runtime/registries/human_gates.json",
        "runtime/registries/workflow_help.json",
        ".github/schemas/human-gates.schema.json",
        ".github/schemas/workflow-help.schema.json",
        ".github/schemas/rag-dispatch-plan.schema.json",
        "runtime/workflow/gui_mode.py",
        "templates/noise-reduction/README.md",
        "docs/reference/human-gates.md",
        "runtime/tests/test_close_archive.py",
        "runtime/tests/test_rag_dispatcher.py",
        "runtime/tests/test_ctl_help.py",
    ]
    return [path for path in required if not (repo_root / path).exists()]


def human_gate_registry_findings(repo_root: Path) -> list[str]:
    registry_path = repo_root / "runtime" / "registries" / "human_gates.json"
    if not registry_path.exists():
        return []
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    findings: list[str] = []
    if "$schema" in data:
        findings.append("runtime/registries/human_gates.json contains $schema")
    if "schema_version" in data:
        findings.append("runtime/registries/human_gates.json contains schema_version")
    if "registry_version" not in data:
        findings.append("runtime/registries/human_gates.json does not contain registry_version")
    return findings


def close_archive_findings(repo_root: Path) -> list[str]:
    findings: list[str] = []
    close_root = repo_root / "work" / "close"
    if not close_root.exists():
        return findings
    for archive_dir in [path for path in close_root.rglob("*") if path.is_dir()]:
        children = {child.name for child in archive_dir.iterdir() if child.is_file()}
        if children & set(REPORT_FILES) and not set(REPORT_FILES).issubset(children):
            findings.append(relative_to_repo(repo_root, archive_dir))
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run lightweight workflow repository health checks.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--fail-on-warning", action="store_true")
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    warnings = []
    tracked_violations = tracked_policy_violations(repo_root)
    if tracked_violations:
        warnings.append(
            {
                "id": "tracked-local-workspace-files",
                "message": "work/ または rag/ 配下でREADME以外がGit管理されています。",
                "paths": tracked_violations,
            }
        )
    missing = missing_required_files(repo_root)
    if missing:
        warnings.append({"id": "missing-required-files", "message": "必須workflow fileが不足しています。", "paths": missing})
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
    status = "fail" if warnings and args.fail_on_warning else "warning" if warnings else "pass"
    return {
        "status": status,
        "warning_count": len(warnings),
        "warnings": warnings,
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
