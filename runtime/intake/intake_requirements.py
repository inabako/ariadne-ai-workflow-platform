from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    ensure_work_tree,
    extract_repository_config_from_files,
    find_repo_root,
    load_artifact_index,
    make_receipt_id,
    relative_to_repo,
    upsert_artifact,
    utc_now_iso,
    write_json,
)
from runtime.workflow.context_first import register_context  # noqa: E402

REQUIREMENT_EXTENSIONS = {".md", ".markdown", ".txt"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Move submitted requirement documents into work/<receipt_id>/ and initialize workflow context."
    )
    parser.add_argument(
        "requirements",
        nargs="*",
        help="Requirement definition document paths to intake. When omitted, work/requirements/ is used.",
    )
    parser.add_argument(
        "--requirements-dir",
        default=None,
        help="Directory used when requirement paths are omitted. Default: work/requirements/",
    )
    parser.add_argument("--receipt-id", help="Explicit receipt ID. Auto-generated when omitted.")
    parser.add_argument(
        "--id-prefix",
        default=None,
        help="Prefix used for generated receipt IDs. Defaults to SYS for new systems and FEAT for maintenance.",
    )
    parser.add_argument("--project-name", default="unknown-project")
    parser.add_argument("--project-repository", default="")
    parser.add_argument(
        "--workflow",
        default="ariadne-new-system-development",
        choices=[
            "ariadne-new-system-development",
            "ariadne-feature-maintenance-development",
            "ariadne-new-system-iac",
            "realtime-iac",
            "github-knowledge-maintenance",
            "flutter-multiplatform",
        ],
    )
    parser.add_argument("--phase", default="intake")
    parser.add_argument("--intent-summary", default="Requirement document intake")
    parser.add_argument("--risk-level", default="unknown", choices=["low", "medium", "high", "critical", "unknown"])
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--copy", action="store_true", help="Copy requirement documents instead of moving them.")
    return parser


def discover_requirement_documents(requirements_dir: Path) -> list[Path]:
    if not requirements_dir.exists():
        raise FileNotFoundError(
            f"Requirement intake rejected: requirements directory does not exist: {requirements_dir}"
        )
    if not requirements_dir.is_dir():
        raise NotADirectoryError(
            f"Requirement intake rejected: requirements path is not a directory: {requirements_dir}"
        )

    requirement_paths = sorted(
        path
        for path in requirements_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in REQUIREMENT_EXTENSIONS
        and path.name.lower() != "readme.md"
    )
    if not requirement_paths:
        raise ValueError(
            "Requirement intake rejected: no requirement documents were found in "
            f"{requirements_dir}. Place completed requirement documents in work/requirements/ before ordering a Skill."
        )
    if len(requirement_paths) > 1:
        names = ", ".join(path.name for path in requirement_paths)
        raise ValueError(
            "Requirement intake rejected: multiple requirement documents were found in "
            f"{requirements_dir}. Use exactly one requirement document per receipt ID. Files: {names}"
        )
    return requirement_paths


def validate_repository_control(requirement_paths: list[Path]) -> dict[str, str]:
    config = extract_repository_config_from_files(requirement_paths)
    if not config.get("repository"):
        names = ", ".join(str(path) for path in requirement_paths)
        raise ValueError(
            "Requirement intake rejected: Repository Control is missing Target Repository, "
            f"GitHub Repository URL, or GitHub Owner + GitHub Repository. Files: {names}"
        )
    return config


def unique_destination(directory: Path, filename: str) -> Path:
    destination = directory / filename
    if not destination.exists():
        return destination
    stem = destination.stem
    suffix = destination.suffix
    counter = 2
    while True:
        candidate = directory / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def command_for_workflow(workflow: str) -> str:
    if workflow == "ariadne-feature-maintenance-development":
        return "/ariadne-feature-maintenance-development"
    if workflow == "ariadne-new-system-iac":
        return "/ariadne-new-system-iac"
    if workflow == "realtime-iac":
        return "/realtime-iac"
    if workflow == "github-knowledge-maintenance":
        return "/github-knowledge-maintenance"
    if workflow == "flutter-multiplatform":
        return "/flutter-multiplatform"
    return "/ariadne-new-system-development"


def id_prefix_for_workflow(workflow: str) -> str:
    if workflow in {"ariadne-new-system-development", "ariadne-new-system-iac"}:
        return "SYS"
    if workflow == "ariadne-feature-maintenance-development":
        return "FEAT"
    if workflow == "flutter-multiplatform":
        return "FLUTTER"
    return "WF"


def open_questions_for_workflow(workflow: str) -> list[str]:
    if workflow == "realtime-iac":
        return [
            "Communication specification is not confirmed at intake.",
            "Port definition list is not confirmed at intake.",
            "Network boundary definition is not confirmed at intake.",
            "Public exposure scope and secret handling are not confirmed at intake.",
        ]
    if workflow == "ariadne-new-system-iac":
        return [
            "STOP / emergency stop behavior is not confirmed at intake.",
            "Communication loss behavior is not confirmed at intake.",
            "Shared Artifacts readiness for IaC handoff is not confirmed at intake.",
            "Software inventory for infrastructure ownership is not confirmed at intake.",
            "Communication specification, port definition, and network boundary definition must be validated before IaC starts.",
        ]
    if workflow == "github-knowledge-maintenance":
        return [
            "GitHub mutation approval is not confirmed at intake.",
            "Clone approval is not confirmed at intake.",
            "RAG publication approval is not confirmed at intake.",
        ]
    if workflow == "flutter-multiplatform":
        return [
            "Flutter target platforms are not confirmed at intake.",
            "Build host OS and remote build requirements are not confirmed at intake.",
            "Signing, Store distribution, Platform Channel, and native dependency policy are not confirmed at intake.",
        ]
    return [
        "STOP / emergency stop behavior is not confirmed at intake.",
        "Communication loss behavior is not confirmed at intake.",
    ]


def consumed_by_for_workflow(workflow: str) -> list[str]:
    if workflow == "realtime-iac":
        return ["iac-requirements-agent"]
    if workflow == "ariadne-new-system-iac":
        return [
            "ariadne-architect-agent",
            "shared-artifact-validator-agent",
            "iac-requirements-agent",
        ]
    if workflow == "github-knowledge-maintenance":
        return [
            "repository-discovery-agent",
            "github-metadata-collector-agent",
            "knowledge-asset-discovery-agent",
            "narrative-analyzer-agent",
        ]
    if workflow == "flutter-multiplatform":
        return [
            "flutter-requirements-agent",
            "flutter-environment-dispatcher",
            "flutter-build-dispatcher",
        ]
    return ["ariadne-architect-agent"]


def initialize_context(
    repo_root: Path,
    work_dir: Path,
    receipt_id: str,
    project_name: str,
    project_repository: str,
    workflow: str,
    phase: str,
    intent_summary: str,
    risk_level: str,
) -> None:
    context_dir = work_dir / "context"
    command = command_for_workflow(workflow)
    open_safety_questions = open_questions_for_workflow(workflow)
    agent_context = {
        "schema_version": "1.0",
        "project": {
            "name": project_name,
            "repository": project_repository or str(repo_root),
            "environment": "",
        },
        "workflow": {
            "name": workflow,
            "phase": phase,
            "risk_level": risk_level,
            "command": command,
        },
        "agent": {
            "name": "runtime-intake",
            "role": "requirement intake and work directory initialization",
            "input_artifacts": [],
            "output_artifacts": [
                relative_to_repo(repo_root, context_dir / "agent-context.json"),
                relative_to_repo(repo_root, context_dir / "artifact-index.json"),
            ],
        },
        "intent": {
            "summary": intent_summary,
            "non_goals": [],
            "success_criteria": [],
        },
        "safety_context": {
            "stop_behavior_known": False,
            "communication_loss_behavior_known": False,
            "startup_safe_state_known": False,
            "shutdown_safe_state_known": False,
            "field_trial_allowed": False,
            "open_safety_questions": open_safety_questions,
        },
        "assumptions": [
            f"receipt_id={receipt_id}",
            "Requirement documents were accepted by runtime/intake.",
        ],
        "constraints": [],
    }

    write_json(context_dir / "agent-context.json", agent_context)
    write_json(context_dir / "qa-records.json", [])
    write_json(context_dir / "finding-records.json", [])
    write_json(context_dir / "decision-records.json", [])
    write_json(context_dir / "test-evidence.json", [])
    write_json(
        context_dir / "handoff-package.json",
        {
            "schema_version": "1.0",
            "from_agent": "runtime-intake",
            "to_agent": "next-agent",
            "workflow": workflow,
            "phase": phase,
            "intent": intent_summary,
            "summary": f"Initialized work area for receipt ID {receipt_id}.",
            "decisions": [],
            "artifacts": [],
            "open_questions": open_safety_questions,
            "risks": ["Safety behavior is not yet defined."],
            "required_next_actions": [
                "Review requirement documents.",
                "Create initial intent and operational context.",
                "Identify safety-critical QA before implementation.",
            ],
            "stop_conditions": [
                "Do not proceed to implementation or field trial until safety-critical QA is answered."
            ],
            "notes_for_next_agent": "Use artifact-index.json to locate accepted requirement documents.",
        },
    )


def register_initial_context_manifest(repo_root: Path, work_dir: Path, receipt_id: str) -> None:
    context_dir = work_dir / "context"
    registrations = [
        (
            "agent-context",
            context_dir / "agent-context.json",
            True,
            ".github/schemas/agent-context.schema.json",
        ),
        (
            "artifact-index",
            context_dir / "artifact-index.json",
            True,
            ".github/schemas/artifact-index.schema.json",
        ),
        (
            "handoff-package",
            context_dir / "handoff-package.json",
            False,
            ".github/schemas/handoff-package.schema.json",
        ),
        ("qa-records", context_dir / "qa-records.json", False, ""),
        ("finding-records", context_dir / "finding-records.json", False, ""),
        ("decision-records", context_dir / "decision-records.json", False, ""),
        ("test-evidence", context_dir / "test-evidence.json", False, ""),
    ]
    for context_type, path, required, schema in registrations:
        register_context(
            repo_root,
            work_dir,
            work_id=receipt_id,
            context_type=context_type,
            path=path,
            required=required,
            generated_by="runtime-intake",
            owner="workflow",
            schema=schema,
        )


def run(args: argparse.Namespace) -> dict[str, object]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    receipt_id = args.receipt_id or make_receipt_id(
        args.id_prefix or id_prefix_for_workflow(args.workflow)
    )
    if args.requirements:
        requirement_sources = [Path(raw_path).resolve() for raw_path in args.requirements]
        requirements_dir = None
    else:
        requirements_dir = (
            Path(args.requirements_dir).resolve() if args.requirements_dir else repo_root / "work" / "requirements"
        )
        requirement_sources = discover_requirement_documents(requirements_dir)

    for source in requirement_sources:
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"Requirement document not found: {source}")
    requirement_config = validate_repository_control(requirement_sources)
    project_repository = args.project_repository or requirement_config["repository"]

    work_dir = ensure_work_tree(repo_root, receipt_id)
    design_dir = work_dir / "design-document"

    initialize_context(
        repo_root=repo_root,
        work_dir=work_dir,
        receipt_id=receipt_id,
        project_name=args.project_name,
        project_repository=project_repository,
        workflow=args.workflow,
        phase=args.phase,
        intent_summary=args.intent_summary,
        risk_level=args.risk_level,
    )

    artifact_index = load_artifact_index(work_dir, args.project_name, args.workflow)
    accepted_files: list[str] = []
    now = utc_now_iso()

    for source in requirement_sources:
        destination = unique_destination(design_dir, source.name)
        if args.copy:
            shutil.copy2(source, destination)
        else:
            shutil.move(str(source), str(destination))

        relative_path = relative_to_repo(repo_root, destination)
        accepted_files.append(relative_path)
        upsert_artifact(
            artifact_index,
            {
                "id": f"REQ-{len(accepted_files):03d}",
                "title": destination.name,
                "path": relative_path,
                "type": "requirement",
                "status": "draft",
                "owner_agent": "runtime-intake",
                "created_at": now,
                "updated_at": now,
                "depends_on": [],
                "consumed_by": consumed_by_for_workflow(args.workflow),
                "summary": "Requirement document accepted by runtime intake.",
                "unresolved_items": [],
            },
        )

    context_dir = work_dir / "context"
    handoff_data = json.loads((context_dir / "handoff-package.json").read_text(encoding="utf-8-sig"))
    handoff_data["artifacts"] = accepted_files
    write_json(context_dir / "handoff-package.json", handoff_data)
    write_json(context_dir / "artifact-index.json", artifact_index)
    register_initial_context_manifest(repo_root, work_dir, receipt_id)

    return {
        "receipt_id": receipt_id,
        "work_dir": relative_to_repo(repo_root, work_dir),
        "accepted_files": accepted_files,
        "repository": requirement_config["repository"],
        "target_branch": requirement_config.get("target_branch"),
        "copied": bool(args.copy),
        "requirements_dir": relative_to_repo(repo_root, requirements_dir) if requirements_dir else None,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
