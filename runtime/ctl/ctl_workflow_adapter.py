from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.workflow import (
    corrective_action_report,
    docs_sync,
    iac_handoff_context,
    init_corrective_action_fix,
    knowledge_capture,
    noise_reduction,
    validate_output_language,
    validate_vscode_workspace,
    vscode_environment,
    workflow_state,
)


def _action_args(args: argparse.Namespace, repo_root: Path) -> argparse.Namespace:
    return workflow_args(args, repo_root, str(getattr(args, "workflow_action", "") or "run"))


def _run_validate_output_language(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    command_args = workflow_args(args, repo_root, "check")
    findings = [
        finding
        for path in validate_output_language.iter_markdown(
            command_args.paths,
            repo_root,
            command_args.exclude,
        )
        if (finding := validate_output_language.analyze(path, command_args))
    ]
    result = validate_output_language.build_result(repo_root, findings)
    result["exit_code"] = 1 if findings and command_args.fail_on_violation else 0
    return result


def _run_validate_vscode_workspace(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    workspace = Path(args.workspace)
    workspace_root = workspace if workspace.is_absolute() else repo_root / workspace
    files = args.files or validate_vscode_workspace.DEFAULT_FILES
    validated: list[str] = []
    for raw_path in files:
        validate_vscode_workspace.validate_file(workspace_root / raw_path)
        validated.append(raw_path)
    return {
        "status": "ok",
        "workspace": str(workspace_root),
        "validated_files": validated,
    }


def run_workflow(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    command_args = _action_args(args, repo_root)
    action = str(getattr(command_args, "command", "") or "")
    if command == "docs-sync":
        return docs_sync.run(command_args)
    if command == "knowledge-capture":
        return knowledge_capture.knowledge_capture(command_args)
    if command == "corrective-action-fix":
        return init_corrective_action_fix.run(command_args)
    if command == "corrective-action-report":
        if action == "register":
            return corrective_action_report.run_register(command_args)
        if action == "show":
            return corrective_action_report.run_show(command_args)
        raise KeyError(f"{command} {action}")
    if command == "state":
        if action == "show":
            return workflow_state.run_show(command_args)
        if action == "set":
            return workflow_state.run_set(command_args)
        raise KeyError(f"{command} {action}")
    if command == "noise-reduction":
        return noise_reduction.run(command_args)
    if command == "iac-handoff":
        return iac_handoff_context.run(command_args)
    if command == "vscode-environment":
        if action == "init":
            return vscode_environment.init_work(command_args)
        if action == "requirements-template":
            return vscode_environment.write_requirements_template(command_args)
        if action == "validation-template":
            return vscode_environment.write_validation_template(command_args)
        if action == "draft-template":
            return vscode_environment.write_draft_template(command_args)
        if action == "open-questions":
            return vscode_environment.write_open_questions(command_args)
        if action == "rag-template":
            return vscode_environment.write_rag_template(command_args)
        raise KeyError(f"{command} {action}")
    if command == "validate-output-language":
        return _run_validate_output_language(args, repo_root)
    if command == "validate-vscode-workspace":
        return _run_validate_vscode_workspace(args, repo_root)
    raise KeyError(command)
