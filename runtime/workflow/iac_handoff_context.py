from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create Context First execution-plan and realtime IaC handoff context."
    )
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--target-repository", default="")
    parser.add_argument("--target-branch", default="")
    parser.add_argument(
        "--validator-judgment",
        default="unknown",
        choices=["pass", "conditional-pass", "fail", "unknown"],
    )
    parser.add_argument("--source-artifact", action="append", default=[])
    parser.add_argument(
        "--validation-path",
        default="",
        help="Shared Artifact Validator JSON path. Default: work/<work-id>/context/shared-artifact-validation.json",
    )
    parser.add_argument(
        "--handoff-path",
        default="",
        help="Realtime IaC handoff JSON path. Default: work/<work-id>/context/realtime-iac-handoff.json",
    )
    return parser


def resolve_repo_root(raw_repo_root: str) -> Path:
    return Path(raw_repo_root).resolve() if raw_repo_root else find_repo_root()


def resolve_work_dir(repo_root: Path, work_id: str) -> Path:
    return repo_root / "work" / work_id


def resolve_path(repo_root: Path, raw_path: str, default_path: Path) -> Path:
    if not raw_path:
        return default_path
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def relative_paths(repo_root: Path, raw_paths: list[str]) -> list[str]:
    results: list[str] = []
    for raw_path in raw_paths:
        path = Path(raw_path)
        absolute = path if path.is_absolute() else repo_root / path
        results.append(relative_to_repo(repo_root, absolute))
    return results


def create_handoff(
    repo_root: Path,
    work_id: str,
    *,
    validation_path: Path,
    source_artifacts: list[str],
    validator_judgment: str,
    target_repository: str,
    target_branch: str,
) -> dict[str, Any]:
    validation = read_json(validation_path, default={})
    validation_judgment = validator_judgment
    if isinstance(validation, dict):
        validation_judgment = str(validation.get("judgment") or validation.get("status") or validator_judgment)
    return {
        "schema_version": "1.0",
        "artifact_type": "realtime-iac-handoff",
        "source_workflow": "robotics-new-system-iac",
        "target_workflow": "realtime-iac",
        "work_id": work_id,
        "created_at": utc_now_iso(),
        "source_artifacts": source_artifacts,
        "shared_artifact_validation": {
            "path": relative_to_repo(repo_root, validation_path),
            "judgment": validation_judgment,
        },
        "blocked_areas": [],
        "residual_risks": [],
        "iac_repository_mode": "",
        "target_repository": target_repository,
        "target_branch": target_branch,
        "required_human_approvals": [
            "Approve conditional-pass residual risks before starting IaC.",
            "Approve external I/O, Docker Desktop, Linux runtime, and integration validation as required.",
        ],
        "required_environment": "docker",
        "recommended_next_commands": [
            f"aiwfctl env select docker --work-id {work_id}",
            "uv run --project runtime python runtime/workflow/context_first.py "
            f"--work-dir work/{work_id} require-environment --environment docker",
            "/realtime-iac",
        ],
        "boilerplate_template_expectation": "Check templates/boilerplates/realtime-gateway-infra-template/ when realtime gateway infrastructure is in scope.",
    }


def create_execution_plan(
    repo_root: Path,
    work_id: str,
    *,
    handoff_path: Path,
    validation_path: Path,
    source_artifacts: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact_type": "execution-plan",
        "architecture": "context-first",
        "work_id": work_id,
        "source_workflow": "robotics-new-system-iac",
        "target_workflow": "realtime-iac",
        "created_at": utc_now_iso(),
        "status": "ready-for-human-check",
        "required_dispatcher_contexts": [
            "environment-selection"
        ],
        "required_environment": "docker",
        "handoff_context": relative_to_repo(repo_root, handoff_path),
        "validation_context": relative_to_repo(repo_root, validation_path),
        "source_artifacts": source_artifacts,
        "stop_conditions": [
            "Do not start realtime IaC when Shared Artifact Validator judgment is fail.",
            "Do not start realtime IaC until environment-selection.environment is docker.",
            "Do not infer missing communication, port, network boundary, software inventory, or public exposure values.",
        ],
        "next_commands": [
            f"aiwfctl env select docker --work-id {work_id}",
            "uv run --project runtime python runtime/workflow/context_first.py "
            f"--work-dir work/{work_id} require-environment --environment docker",
            "/realtime-iac",
        ],
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args.repo_root)
    work_dir = resolve_work_dir(repo_root, args.work_id)
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True, exist_ok=True)
    validation_path = resolve_path(
        repo_root,
        args.validation_path,
        context_dir / "shared-artifact-validation.json",
    )
    handoff_path = resolve_path(
        repo_root,
        args.handoff_path,
        context_dir / "realtime-iac-handoff.json",
    )
    execution_plan_path = context_dir / "execution-plan.json"
    source_artifacts = relative_paths(repo_root, args.source_artifact)

    if handoff_path.exists() and not args.force:
        handoff = read_json(handoff_path, default={})
        if not isinstance(handoff, dict):
            raise ValueError(f"Existing handoff context is not a JSON object: {handoff_path}")
    else:
        handoff = create_handoff(
            repo_root,
            args.work_id,
            validation_path=validation_path,
            source_artifacts=source_artifacts,
            validator_judgment=args.validator_judgment,
            target_repository=args.target_repository,
            target_branch=args.target_branch,
        )
        write_json(handoff_path, handoff)

    execution_plan = create_execution_plan(
        repo_root,
        args.work_id,
        handoff_path=handoff_path,
        validation_path=validation_path,
        source_artifacts=source_artifacts,
    )
    write_json(execution_plan_path, execution_plan)

    register_context(
        repo_root,
        work_dir,
        work_id=args.work_id,
        context_type="realtime-iac-handoff",
        path=handoff_path,
        required=True,
        generated_by="robotics-new-system-iac",
        owner="workflow",
        schema=".github/schemas/realtime-iac-handoff.schema.json",
    )
    manifest = register_context(
        repo_root,
        work_dir,
        work_id=args.work_id,
        context_type="execution-plan",
        path=execution_plan_path,
        required=True,
        generated_by="robotics-new-system-iac",
        owner="workflow",
        schema=".github/schemas/execution-plan.schema.json",
    )
    return {
        "status": "ready-for-human-check",
        "work_id": args.work_id,
        "handoff_context": relative_to_repo(repo_root, handoff_path),
        "execution_plan": relative_to_repo(repo_root, execution_plan_path),
        "manifest_contexts": [item.get("type") for item in manifest.get("contexts", [])],
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
    return 0 if result.get("status") not in {"failed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
