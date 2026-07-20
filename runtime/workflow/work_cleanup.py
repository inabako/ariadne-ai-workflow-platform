from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo  # noqa: E402
from runtime.constants.workspace import work_dir_for_id  # noqa: E402
from runtime.workflow.work_cleanup_hint import artifact_index_evidence  # noqa: E402


PROTECTED_WORK_ROOTS = {"db", "requirements", "feedback", "runtime-dev", "close"}
PROTECTED_WORK_IDS = {"github"}
WORKFLOW_CONTEXT_FILES = {
    "github-knowledge-maintenance": "github-knowledge-analysis.json",
    "vscode-environment": "vscode-environment-state.json",
    "corrective-action-report": "corrective-action-report.json",
    "sdk-analysis": "sdk-analysis-context.json",
}
KNOWLEDGE_WORKFLOWS = set(WORKFLOW_CONTEXT_FILES)
METRICS_ONLY_ALLOWED_FILES = {
    "context/context-manifest.json",
    "context/runtime-metrics.json",
    "test-evidence/runtime-metrics.json",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check and remove completed temporary work directories.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("cleanup-check", "cleanup-apply"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--work-id", required=True)
        sub.add_argument("--repo-root", default="")
        sub.add_argument("--recursive", action="store_true", help="Check child workflow directories and remove the parent scope.")
        sub.add_argument(
            "--required-artifact",
            action="append",
            default=[],
            help="Long-lived artifact path that must exist before cleanup can proceed.",
        )
        sub.add_argument("--json", action="store_true")
        if name == "cleanup-apply":
            sub.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    return parser


def resolve_repo_root(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve() if getattr(args, "repo_root", "") else find_repo_root()


def resolve_work_dir(repo_root: Path, work_id: str) -> Path:
    if not work_id.strip():
        raise ValueError("--work-id is required")
    normalized_work_id = "/".join(part for part in Path(work_id).parts if part)
    if normalized_work_id in PROTECTED_WORK_IDS:
        raise ValueError(f"Refusing to cleanup protected work scope: work/{normalized_work_id}")
    first = Path(work_id).parts[0] if Path(work_id).parts else work_id
    if first in PROTECTED_WORK_ROOTS:
        raise ValueError(f"Refusing to cleanup protected work root: work/{first}")
    work_dir = work_dir_for_id(repo_root, work_id)
    work_root = repo_root / "work"
    resolved = work_dir.resolve()
    if resolved == work_root.resolve() or work_root.resolve() not in resolved.parents:
        raise ValueError(f"Cleanup target must stay under work/: {resolved}")
    return work_dir


def workflow_kind(work_dir: Path) -> str:
    context_dir = work_dir / "context"
    for workflow, filename in WORKFLOW_CONTEXT_FILES.items():
        if (context_dir / filename).exists():
            return workflow
    if metrics_only_empty_work(work_dir):
        return "metrics-only-empty-work"
    return "generic"


def relative_files(work_dir: Path) -> set[str]:
    if not work_dir.exists():
        return set()
    return {
        path.relative_to(work_dir).as_posix()
        for path in work_dir.rglob("*")
        if path.is_file()
    }


def metrics_only_empty_work(work_dir: Path) -> bool:
    files = relative_files(work_dir)
    if not files:
        return False
    return files <= METRICS_ONLY_ALLOWED_FILES and "context/runtime-metrics.json" in files


def child_work_dirs(work_dir: Path) -> list[Path]:
    if (work_dir / "context").is_dir():
        return [work_dir]
    if not work_dir.exists():
        return []
    return sorted(path.parent for path in work_dir.rglob("context") if path.is_dir())


def existing_repo_path(repo_root: Path, value: str) -> bool:
    path = Path(value)
    target = path if path.is_absolute() else repo_root / path
    return target.exists()


def has_absorption_evidence(repo_root: Path, work_dir: Path, required_artifacts: list[str]) -> tuple[bool, list[str]]:
    evidence: list[str] = []
    for artifact in required_artifacts:
        if existing_repo_path(repo_root, artifact):
            evidence.append(artifact)

    evidence.extend(artifact_index_evidence(repo_root, work_dir))

    return bool(evidence), sorted(set(evidence))


def command_value(value: str) -> str:
    if not value or any(char.isspace() or char == '"' for char in value):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def build_apply_command(args: argparse.Namespace) -> str:
    parts = ["aiwfctl", "work", "cleanup-apply", "--work-id", command_value(args.work_id)]
    if getattr(args, "recursive", False):
        parts.append("--recursive")
    for artifact in getattr(args, "required_artifact", []) or []:
        parts.extend(["--required-artifact", command_value(artifact)])
    parts.extend(["--human-check", "approved"])
    return " ".join(parts)


def check_one(repo_root: Path, work_dir: Path, required_artifacts: list[str]) -> dict[str, Any]:
    exists = work_dir.exists()
    kind = workflow_kind(work_dir) if exists else "missing"
    has_evidence, evidence = has_absorption_evidence(repo_root, work_dir, required_artifacts) if exists else (False, [])
    blockers: list[str] = []
    if not exists:
        blockers.append("work directory does not exist")
    if kind in KNOWLEDGE_WORKFLOWS and not has_evidence:
        blockers.append("long-lived knowledge artifact is not confirmed")
    return {
        "work_dir": relative_to_repo(repo_root, work_dir),
        "workflow": kind,
        "exists": exists,
        "empty_runtime_metrics_only": kind == "metrics-only-empty-work",
        "knowledge_absorbed": has_evidence,
        "absorption_evidence": evidence,
        "blockers": blockers,
        "ready": exists and not blockers,
    }


def cleanup_check(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args)
    target = resolve_work_dir(repo_root, args.work_id)
    work_dirs = child_work_dirs(target) if getattr(args, "recursive", False) else [target]
    checks = [check_one(repo_root, work_dir, args.required_artifact) for work_dir in work_dirs]
    blockers = [blocker for check in checks for blocker in check["blockers"]]
    if getattr(args, "recursive", False) and not checks:
        blockers.append("no child workflow directories found")
    ready = bool(checks) and not blockers
    return {
        "schema_version": "1.0",
        "artifact_type": "work-cleanup-check",
        "work_id": args.work_id,
        "target": relative_to_repo(repo_root, target),
        "recursive": bool(getattr(args, "recursive", False)),
        "status": "ready" if ready else "blocked",
        "ready": ready,
        "checks": checks,
        "blockers": blockers,
        "apply_command": build_apply_command(args) if ready else "",
    }


def cleanup_apply(args: argparse.Namespace) -> dict[str, Any]:
    if getattr(args, "human_check", "pending") != "approved":
        raise PermissionError("cleanup-apply requires --human-check approved")
    repo_root = resolve_repo_root(args)
    target = resolve_work_dir(repo_root, args.work_id)
    check = cleanup_check(args)
    if not check["ready"]:
        raise RuntimeError("cleanup check is not ready: " + "; ".join(check["blockers"]))
    shutil.rmtree(target)
    return {
        **check,
        "artifact_type": "work-cleanup-apply",
        "status": "removed",
        "removed": True,
        "exists_after": target.exists(),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "cleanup-check":
        return cleanup_check(args)
    if args.command == "cleanup-apply":
        return cleanup_apply(args)
    raise ValueError(f"Unknown work cleanup command: {args.command}")
