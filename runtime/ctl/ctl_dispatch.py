from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from runtime.ctl.ctl_close_archive_adapter import run_close_archive
from runtime.ctl.ctl_context_adapter import run_context
from runtime.ctl.ctl_design_adapter import run_design
from runtime.ctl.ctl_doctor_adapter import run_doctor
from runtime.ctl.ctl_flutter_adapter import format_result as format_flutter_result
from runtime.ctl.ctl_flutter_adapter import run_flutter
from runtime.ctl.ctl_gui_adapter import run_gui
from runtime.ctl.ctl_gui_adapter import run_web_svg
from runtime.ctl.ctl_github_adapter import run_github
from runtime.ctl.ctl_github_knowledge_adapter import run_github_knowledge
from runtime.ctl.ctl_human_gate_adapter import run_human_gate
from runtime.ctl.ctl_iac_adapter import run_iac_template
from runtime.ctl.ctl_intake_adapter import run_intake
from runtime.ctl.ctl_integration_adapter import format_result as format_integration_result
from runtime.ctl.ctl_integration_adapter import run_integration
from runtime.ctl.ctl_knowledge_adapter import run_knowledge
from runtime.ctl.ctl_mcp_group_adapter import format_result as format_mcp_group_result
from runtime.ctl.ctl_mcp_group_adapter import run_mcp_group
from runtime.ctl.ctl_preflight_adapter import run_preflight
from runtime.ctl.ctl_rag_adapter import run_rag
from runtime.ctl.ctl_retrieval_adapter import run_retrieval
from runtime.ctl.ctl_review_adapter import run_review
from runtime.ctl.ctl_scm_adapter import run_scm
from runtime.ctl.ctl_sdk_adapter import format_result as format_sdk_result
from runtime.ctl.ctl_sdk_adapter import run_sdk
from runtime.ctl.ctl_self_improvement_adapter import run_self_improvement
from runtime.ctl.ctl_tools_adapter import run_tools
from runtime.ctl.ctl_work_adapter import run_work_cleanup
from runtime.ctl.ctl_workflow_adapter import run_workflow
from runtime.constants.workflow_limits import CTL_WARNING_PATH_PREVIEW_LIMIT
from runtime.observability import logger as runtime_event_logger
from runtime.release import manifest as release_manifest
from runtime.release import validation as release_validation
from runtime.workflow import runtime_status
from runtime.workflow import runtime_trace


HelperModule = Any
CommandHandler = Callable[[argparse.Namespace, Path, dict[str, Any], HelperModule, bool], tuple[int, str]]


# These names are supplied from runtime.ctl.ctl through _bind_helpers().
# Keeping the annotations here lets static analyzers understand the dispatch module
# while preserving the current bridge-based split.
_github_knowledge_metrics_collector: Any
_record_github_knowledge_metrics_result: Any
context_path_pattern: Any
enrich_environment_selection: Any
environment_selection_record: Any
find_public_environment: Any
format_env_usage: Any
format_environment_list: Any
format_environment_selection: Any
format_knowledge_result: Any
format_knowledge_usage: Any
format_public_environment_detail: Any
format_root_usage_warning: Any
format_unknown_environment: Any
implementation_path_pattern: Any
load_environment_registry: Any
load_registry: Any
process_report_path_pattern: Any
repo_root_from_args: Any
reports_path_pattern: Any
requirements_path_pattern: Any
run_help_command: Any
test_evidence_path_pattern: Any
work_path_pattern: Any
write_environment_selection: Any


def _bind_helpers(helpers: HelperModule) -> None:
    for name in dir(helpers):
        if name.startswith("__"):
            continue
        globals()[name] = getattr(helpers, name)


def _format_dry_run_plan(result: dict[str, Any]) -> str:
    lines = [
        "Dry Run Plan",
        "",
        f"Command : {result.get('command', '')}",
        f"Status  : {result.get('status', '')}",
        f"Execute : {result.get('would_run', False)}",
    ]
    reads = result.get("reads", [])
    writes = result.get("writes", [])
    if reads:
        lines.extend(["", "Reads"])
        for item in reads:
            if isinstance(item, dict):
                lines.append(f"  - {item.get('role', '')}: {item.get('path', '')}")
    if writes:
        lines.extend(["", "Writes"])
        for item in writes:
            if isinstance(item, dict):
                lines.append(f"  - {item.get('role', '')}: {item.get('path', '')}")
    next_action = str(result.get("next_action", "") or "")
    if next_action:
        lines.extend(["", f"Next   : {next_action}"])
    return "\n".join(lines).rstrip() + "\n"


def _handle_env(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    environment_registry = load_environment_registry(repo_root)
    env_command = getattr(args, "env_command", None)
    if env_command is None:
        return 0, format_env_usage()
    if env_command == "list":
        return 0, format_environment_list(environment_registry)
    if env_command == "show":
        try:
            environment = find_public_environment(environment_registry, args.environment)
        except KeyError:
            return 1, format_unknown_environment(environment_registry, args.environment)
        return 0, format_public_environment_detail(environment_registry, environment)
    if env_command in {"select", "check"}:
        record = environment_selection_record(environment_registry, args.target)
        record = enrich_environment_selection(repo_root, environment_registry, record, work_id=args.work_id)
        written = write_environment_selection(
            repo_root,
            record,
            work_id=args.work_id,
            output=args.output,
            selected_by=args.selected_by,
            selection_mode=args.selection_mode,
        )
        if written:
            record["written"] = written
        if getattr(args, "json", False):
            return (0 if not record.get("human_check_required") else 2), json.dumps(record, ensure_ascii=False, indent=2) + "\n"
        if record.get("human_check_required"):
            return 2, format_unknown_environment(environment_registry, args.target, record)
        output = format_environment_selection(record)
        if written:
            output += "\n### Written Artifacts\n\n" + "\n".join(f"- `{path}`" for path in written) + "\n"
        return (0 if not record.get("human_check_required") else 2), output
    return 1, f"Unknown env command: {env_command}\n"


def _format_trace_result(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Runtime Trace",
            "",
            f"Status   : {result.get('status', '')}",
            f"Trace ID : {result.get('trace_id', '')}",
            f"Workflow : {result.get('workflow', '')}",
            f"Last Seq : {result.get('last_sequence', 0)}",
            f"Path     : {result.get('path', '')}",
            f"Reason   : {result.get('reason', '')}",
        ]
    ).rstrip() + "\n"


def _handle_trace(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    trace_command = getattr(args, "trace_command", None)
    if trace_command is None:
        return 1, (
            "Runtime Trace\n\n"
            "Usage:\n"
            "  aiwfctl trace begin --workflow /runtime-health-check\n"
            "  aiwfctl trace status\n"
            "  aiwfctl trace end\n"
        )
    if trace_command == "begin":
        result = runtime_event_logger.begin_active_runtime_trace(
            repo_root,
            workflow=str(getattr(args, "workflow", "") or ""),
            trace_id=str(getattr(args, "_runtime_trace_id", "") or getattr(args, "trace_id", "") or ""),
            force=bool(getattr(args, "force", False)),
            initial_sequence=int(getattr(args, "_runtime_sequence", 0) or 0),
        )
        code = 0 if result.get("status") == "active" else 2
    elif trace_command == "status":
        active = runtime_event_logger.load_active_runtime_trace(repo_root)
        result = {
            **active,
            "status": active.get("status", "not-active") if active else "not-active",
            "path": str(runtime_event_logger.active_runtime_trace_path(repo_root)),
        }
        code = 0 if active else 2
    elif trace_command == "end":
        result = runtime_event_logger.end_active_runtime_trace(repo_root)
        code = 0 if result.get("status") == "ended" else 2
    elif trace_command == "show":
        trace_id = str(getattr(args, "trace_id_option", "") or getattr(args, "trace_id", "") or "")
        result = runtime_trace.build_trace_report(
            repo_root,
            trace_id=trace_id,
            runtime_log=str(getattr(args, "runtime_log", "") or ""),
            exclude_trace_id="" if trace_id else str(getattr(args, "_runtime_trace_id", "") or ""),
        )
        code = 0 if result.get("status") == "ok" else 2
    else:
        return 1, f"Unknown trace command: {trace_command}\n"
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if trace_command == "show":
        return code, runtime_trace.format_trace_report(result)
    return code, _format_trace_result(result)


def _handle_status(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    result = runtime_status.collect_status(repo_root, work_id=str(getattr(args, "work_id", "") or ""))
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return 0, runtime_status.format_status(result)


def _handle_context(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    context_command = getattr(args, "context_command", None)
    if context_command is None:
        return 1, (
            "Context Management\n\n"
            "Usage:\n"
            "  aiwfctl context init --work-id <work-id> --workflow <workflow>\n"
            f"  aiwfctl context show --work-dir {work_path_pattern()}\n"
            f"  aiwfctl context require --work-dir {work_path_pattern()} --context environment-selection\n"
            f"  aiwfctl context require-environment --work-dir {work_path_pattern()} --environment docker\n\n"
            "Example:\n"
            "  aiwfctl context init --work-id issue-123 --workflow /docs-sync --tool gh:read-only:GitHub metadata collection\n"
        )
    if context_command == "init":
        result = run_context(args, repo_root, context_command)
        if getattr(args, "json", False):
            return (0 if result.get("status") != "human-check-required" else 2), json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        lines = [
            "Context First Dispatcher Context",
            "",
            f"Status        : {result.get('status', '')}",
            f"Work ID       : {result.get('work_id', '')}",
            f"Workflow      : {result.get('workflow', '')}",
            f"Manifest      : {result.get('manifest_path', '')}",
            "",
            "Contexts",
        ]
        lines.extend(f"  - {item}" for item in result.get("contexts", []))
        written = result.get("written", [])
        if written:
            lines.extend(["", "Written Artifacts"])
            lines.extend(f"  - {item}" for item in written)
        return (0 if result.get("status") != "human-check-required" else 2), "\n".join(lines).rstrip() + "\n"
    try:
        result = run_context(args, repo_root, context_command)
    except KeyError:
        return 1, f"Unknown context command: {context_command}\n"
    except Exception as exc:
        return 1, f"Context First failed: {exc}\n"
    code = 0 if result.get("status") not in {"human-check-required", "failed"} else 2
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = [
        "Context First",
        "",
        f"Command : {context_command}",
        f"Status  : {result.get('status', '')}",
        f"Manifest: {result.get('manifest_path', '')}",
    ]
    missing = result.get("missing", [])
    if missing:
        lines.extend(["", "Missing"])
        lines.extend(f"  - {item}" for item in missing)
    if "environment" in result:
        lines.append(f"Environment: {result.get('environment', '')}")
    if "context_path" in result:
        lines.append(f"Context    : {result.get('context_path', '')}")
    return code, "\n".join(lines).rstrip() + "\n"
    return 1, f"Unknown context command: {context_command}\n"


def _handle_human_gate(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    human_gate_command = getattr(args, "human_gate_command", None)
    if human_gate_command is None:
        return 1, (
            "Human Gate Registry\n\n"
            "Usage:\n"
            "  aiwfctl human-gate list\n"
            "  aiwfctl human-gate check --gate <gate-id> --human-check approved\n"
        )
    try:
        result = run_human_gate(args, repo_root, human_gate_command)
    except KeyError:
        return 1, f"Unknown human-gate command: {human_gate_command}\n"
    except Exception as exc:
        return 1, f"Human gate failed: {exc}\n"
    code = 0 if result.get("status") != "blocked" else 2
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = ["Human Gate Registry", "", f"Command : {human_gate_command}", f"Status  : {result.get('status', '')}"]
    if "gate" in result:
        lines.append(f"Gate    : {result.get('gate', '')}")
    if "registry" in result:
        lines.append(f"Registry: {result.get('registry', '')}")
    if "reason" in result:
        lines.append(f"Reason  : {result.get('reason', '')}")
    return code, "\n".join(lines).rstrip() + "\n"


def _handle_design(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    design_area = getattr(args, "design_area", None)
    if design_area is None:
        return 1, (
            "Expectation-Driven Design\n\n"
            "Usage:\n"
            "  aiwfctl design expectation init --work-id <work-id>\n"
            "  aiwfctl design expectation evaluate --work-id <work-id>\n"
            "  aiwfctl design expectation compare --work-id <work-id>\n"
            "  aiwfctl design expectation gate --work-id <work-id> --human-check approved --selected-candidate DESIGN-B\n"
        )
    try:
        result = run_design(args, repo_root, design_area)
    except KeyError:
        return 1, f"Unknown design command: {design_area}\n"
    except Exception as exc:
        return 1, f"Expectation design failed: {exc}\n"
    code = 0 if result.get("status") not in {"human-check-required", "ready-for-human-check", "review-blocked", "failed", "blocked"} else 2
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = [
        "Expectation-Driven Design",
        "",
        f"Area    : {design_area}",
        f"Command : {getattr(args, 'expectation_command', '')}",
        f"Status  : {result.get('status', '')}",
        f"Work ID : {result.get('work_id', '')}",
    ]
    for key, label in [
        ("base_dir", "Base   "),
        ("artifact_index", "Index  "),
        ("candidates", "Cand.  "),
        ("review_report", "Review "),
        ("output", "Output "),
        ("violations_output", "Viol.  "),
        ("tradeoffs_output", "Trade  "),
        ("report", "Report "),
        ("comparison_json", "Packet "),
        ("tradeoff_report", "T.Report"),
        ("human_decision", "Decision"),
        ("human_gate_summary", "H.Gate "),
        ("refinement_plan", "Refine "),
        ("selected_spec", "Spec   "),
        ("contracts", "Contracts"),
        ("verification", "Verify "),
        ("feedback", "Feedback"),
        ("dispatch", "Dispatch"),
        ("review_council_feedback", "R.Council"),
        ("review_council_feedback_report", "R.Report"),
        ("events", "Events "),
        ("selected_candidate", "Selected"),
        ("repair_command", "Repair "),
        ("review_start_command", "R.Start"),
    ]:
        if key in result:
            lines.append(f"{label}: {result.get(key, '')}")
    if "candidate_count" in result:
        lines.append(f"Candidates: {result.get('candidate_count', 0)}")
    if "decision_required" in result:
        lines.extend(["", "Decision Required"])
        lines.extend(f"  - {item}" for item in result.get("decision_required", []))
    return code, "\n".join(lines).rstrip() + "\n"


def _handle_intake(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    intake_command = getattr(args, "intake_command", None)
    if intake_command is None:
        return 1, (
            "Requirement Intake\n\n"
            "Usage:\n"
            "  aiwfctl intake run\n"
            "  aiwfctl intake run work/requirements/requirements.md --copy\n"
            "  aiwfctl intake run --workflow ariadne-feature-maintenance-development --project-name <name>\n\n"
            "Outputs:\n"
            f"  {work_path_pattern('design-document', '<requirement-file>')}\n"
            f"  {context_path_pattern('agent-context.json')}\n"
            f"  {context_path_pattern('artifact-index.json')}\n"
            f"  {context_path_pattern('context-manifest.json')}\n"
        )
    try:
        result = run_intake(args, repo_root, intake_command)
    except KeyError:
        return 1, f"Unknown intake command: {intake_command}\n"
    except Exception as exc:
        return 1, f"Requirement intake failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = [
        "Requirement Intake",
        "",
        f"Command : {intake_command}",
        f"Receipt : {result.get('receipt_id', '')}",
        f"Work Dir: {result.get('work_dir', '')}",
        f"Repo    : {result.get('repository', '')}",
        f"Branch  : {result.get('target_branch', '') or ''}",
        f"Copied  : {str(result.get('copied', False)).lower()}",
    ]
    accepted_files = result.get("accepted_files", [])
    if accepted_files:
        lines.extend(["", "Accepted Files"])
        lines.extend(f"  - {item}" for item in accepted_files)
    requirements_dir = result.get("requirements_dir")
    if requirements_dir:
        lines.append(f"Requirements Dir: {requirements_dir}")
    return 0, "\n".join(lines).rstrip() + "\n"


def _handle_scm(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    scm_command = getattr(args, "scm_command", None)
    if scm_command is None:
        return 1, (
            "SCM Runtime\n\n"
            "Usage:\n"
            "  aiwfctl scm prepare --work-id <work-id> --repository <owner/repo> --dry-run\n"
            "  aiwfctl scm compare --work-id <work-id>\n"
            "  aiwfctl scm branch --work-id <work-id> --issue-number <number> --local-only\n"
            "  aiwfctl scm commit --work-id <work-id> --message \"feat: add feature\"\n"
            "  aiwfctl scm push --work-id <work-id> --human-check approved\n"
            "  aiwfctl scm bootstrap --work-id <work-id> --github-repo <owner/repo> --dry-run\n"
        )
    try:
        result = run_scm(args, repo_root, scm_command)
    except KeyError:
        return 1, f"Unknown scm command: {scm_command}\n"
    except Exception as exc:
        return 1, f"SCM runtime failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = ["SCM Runtime", "", f"Command : {scm_command}"]
    for key, label in [
        ("work_id", "Work ID "),
        ("source_dir", "Source  "),
        ("repository", "Repo    "),
        ("github_repo", "GitHub  "),
        ("target_branch", "Target  "),
        ("base_branch", "Base    "),
        ("branch", "Branch  "),
        ("working_branch", "Branch  "),
        ("current_branch", "Current "),
        ("commit", "Commit  "),
        ("current_commit", "Commit  "),
        ("markdown_report", "Report  "),
        ("json_report", "JSON    "),
        ("record_path", "Record  "),
        ("remote_branch_ref", "Remote  "),
        ("linked_branch_status", "Linked  "),
        ("action", "Action  "),
        ("dry_run", "Dry Run "),
        ("pushed", "Pushed  "),
    ]:
        if key in result:
            lines.append(f"{label}: {result.get(key, '')}")
    return 0, "\n".join(lines).rstrip() + "\n"


def _handle_github(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    github_command = getattr(args, "github_command", None)
    if github_command is None:
        return 1, (
            "GitHub Runtime\n\n"
            "Usage:\n"
            "  aiwfctl github issue --work-id <work-id> --title <title>\n"
            "  aiwfctl github issue --work-id <work-id> --title <title> --create\n"
            "  aiwfctl github pr --work-id <work-id> --head feature/issue-1\n"
            "  aiwfctl github pr --work-id <work-id> --head feature/issue-1 --create --human-check approved\n"
        )
    try:
        result = run_github(args, repo_root, github_command)
    except KeyError:
        return 1, f"Unknown github command: {github_command}\n"
    except Exception as exc:
        return 1, f"GitHub runtime failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = ["GitHub Runtime", "", f"Command : {github_command}"]
    for key, label in [
        ("work_id", "Work ID "),
        ("github_repo", "GitHub  "),
        ("title", "Title   "),
        ("status", "Status  "),
        ("issue_number", "Issue # "),
        ("issue_url", "Issue   "),
        ("pull_request_number", "PR #    "),
        ("pull_request_url", "PR      "),
        ("base", "Base    "),
        ("head", "Head    "),
        ("body_path", "Body    "),
        ("record_path", "Record  "),
    ]:
        if key in result:
            lines.append(f"{label}: {result.get(key, '') or ''}")
    return 0, "\n".join(lines).rstrip() + "\n"


def _handle_knowledge(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    knowledge_command = getattr(args, "knowledge_command", None)
    if knowledge_command is None:
        return 1, format_knowledge_usage()
    try:
        result = run_knowledge(args, repo_root, knowledge_command)
    except Exception as exc:
        return 1, f"Knowledge command failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if result.get("artifact_type") == "rag-dry-run-plan":
        return 0, _format_dry_run_plan(result)
    return 0, format_knowledge_result(result)


def _handle_rag(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    rag_command = getattr(args, "rag_command", None)
    if rag_command is None:
        return 1, (
            "RAG Runtime\n\n"
            "Usage:\n"
            "  aiwfctl rag build --source-dir <rag-source-dir> --skip-optimization\n"
            "  aiwfctl rag load --query <query> --build-if-missing\n"
            "  aiwfctl rag retrieve <query> --chunks-index <chunks.jsonl> --embeddings-index <embeddings.jsonl>\n"
            "  aiwfctl rag normalize --source-dir <source> --output-dir <normalized>\n"
            "  aiwfctl rag chunk --input-dir <normalized> --output-dir <chunks>\n"
            "  aiwfctl rag index --normalized-dir <normalized> --chunks-dir <chunks> --output-dir <indexes>\n"
            "  aiwfctl rag embed --chunks-index <chunks.jsonl> --output <embeddings.jsonl>\n"
            "  aiwfctl rag semantic-hints generate\n"
            "  aiwfctl rag semantic-hints build --skip-optimization\n"
            "  aiwfctl rag semantic-hints read --semantic-hint <hint>\n"
            "  aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset\n"
            "  aiwfctl rag duckdb verify --query workflow --query runtime\n"
            "  aiwfctl rag jsonize --rag-dir <rag-dir> --output-dir <jsonized-dir>\n"
            "  aiwfctl rag migrate-legacy-root --legacy-dir <legacy-root-rag-dir>\n"
        )
    if rag_command == "duckdb":
        duckdb_command = getattr(args, "rag_duckdb_command", None)
        if duckdb_command is None:
            return 1, (
                "RAG DuckDB Runtime\n\n"
                "Usage:\n"
                "  aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset\n"
                "  aiwfctl rag duckdb verify --query workflow --query runtime\n"
            )
        try:
            result = run_knowledge(args, repo_root, duckdb_command)
        except Exception as exc:
            return 1, f"RAG DuckDB command failed: {exc}\n"
        if getattr(args, "json", False):
            return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if result.get("artifact_type") == "rag-dry-run-plan":
            return 0, _format_dry_run_plan(result)
        return 0, format_knowledge_result(result)
    try:
        result = run_rag(args, repo_root, rag_command)
    except KeyError:
        return 1, f"Unknown rag command: {rag_command}\n"
    except Exception as exc:
        return 1, f"RAG runtime failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if result.get("artifact_type") == "rag-dry-run-plan":
        return 0, _format_dry_run_plan(result)
    lines = ["RAG Runtime", "", f"Command : {rag_command}"]
    for key, label in [
        ("status", "Status  "),
        ("rag_build_run", "Build   "),
        ("dispatch_plan", "Plan    "),
        ("dispatch_result", "Dispatch"),
        ("retrieval_result", "Retrieval"),
        ("context_pack", "Context "),
        ("output_dir", "Output  "),
        ("documents_index", "DocsIdx "),
        ("chunks_index", "Chunks  "),
        ("embedding_count", "Embed   "),
        ("document_count", "Docs    "),
        ("chunk_count", "Chunks# "),
        ("source_count", "Sources "),
        ("generated_count", "Generated"),
        ("hint_count", "Hints   "),
        ("converted_count", "Convert "),
        ("migrated_count", "Migrate "),
        ("renamed_count", "Renamed "),
    ]:
        if key in result:
            lines.append(f"{label}: {result.get(key, '')}")
    return 0, "\n".join(lines).rstrip() + "\n"


def _handle_workflow(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    workflow_command = getattr(args, "workflow_command", None)
    if workflow_command is None:
        return 1, (
            "Workflow Support Runtime\n\n"
            "Usage:\n"
            "  aiwfctl workflow docs-sync init --repository <repo> --target-branch <branch>\n"
            "  aiwfctl workflow knowledge-capture --issue <issue-id>\n"
            "  aiwfctl workflow corrective-action-report register --report-path <path>\n"
            "  aiwfctl workflow corrective-action-fix init --repository <repo> --target-branch <branch>\n"
            "  aiwfctl workflow state show --work-dir work/<work-id>\n"
            "  aiwfctl workflow noise-reduction run --draft <path>\n"
            "  aiwfctl workflow validate-output-language check --paths work docs\n"
            "  aiwfctl workflow validate-vscode-workspace check\n"
        )
    try:
        result = run_workflow(args, repo_root, workflow_command)
    except KeyError:
        action = getattr(args, "workflow_action", "") or ""
        return 1, f"Unknown workflow command: {workflow_command} {action}\n"
    except Exception as exc:
        return 1, f"Workflow support runtime failed: {exc}\n"
    code = int(result.get("exit_code", 0) or 0)
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = ["Workflow Support Runtime", "", f"Command : {workflow_command}"]
    action = getattr(args, "workflow_action", "") or ""
    if action:
        lines.append(f"Action  : {action}")
    for key, label in [
        ("status", "Status  "),
        ("work_id", "Work ID "),
        ("work_dir", "Work Dir"),
        ("state_path", "State   "),
        ("analysis_path", "Analysis"),
        ("issue_body", "Issue   "),
        ("context_path", "Context "),
        ("report_path", "Report  "),
        ("handoff_context", "Handoff "),
        ("execution_plan", "Plan    "),
        ("json_path", "JSON    "),
        ("markdown_path", "Markdown"),
        ("finding_count", "Findings"),
    ]:
        if key in result:
            lines.append(f"{label}: {result.get(key, '')}")
    created_files = result.get("created_files", [])
    if created_files:
        lines.extend(["", "Created Files"])
        lines.extend(f"  - {item}" for item in created_files)
    return code, "\n".join(lines).rstrip() + "\n"


def _format_visual_runtime_result(title: str, command: str, result: dict[str, Any]) -> str:
    lines = [title, "", f"Command : {command}"]
    for key, label in [
        ("status", "Status  "),
        ("mode", "Mode    "),
        ("issue_id", "Issue   "),
        ("work_dir", "Work Dir"),
        ("input_dir", "Input   "),
        ("readme", "README  "),
        ("svg_input_dir", "SVG Dir "),
        ("input_prefix", "Prefix  "),
        ("reason", "Reason  "),
        ("file_count", "Files   "),
    ]:
        if key in result:
            lines.append(f"{label}: {result.get(key, '')}")
    errors = result.get("errors", [])
    if errors:
        lines.extend(["", "Errors"])
        lines.extend(f"  - {item}" for item in errors)
    warnings = result.get("warnings", [])
    if warnings:
        lines.extend(["", "Warnings"])
        lines.extend(f"  - {item}" for item in warnings)
    checks = result.get("checks", [])
    if checks:
        lines.extend(["", "Checks"])
        lines.extend(f"  - {item}" for item in checks)
    artifacts = result.get("artifacts", [])
    if artifacts:
        lines.extend(["", "Artifacts"])
        for artifact in artifacts:
            if isinstance(artifact, dict):
                lines.append(f"  - {artifact.get('path', artifact)}")
            else:
                lines.append(f"  - {artifact}")
    return "\n".join(lines).rstrip() + "\n"


def _handle_gui(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    gui_command = getattr(args, "gui_command", None)
    if gui_command is None:
        return 1, (
            "GUI Runtime\n\n"
            "Usage:\n"
            "  aiwfctl gui init-input\n"
            "  aiwfctl gui inspect-input\n"
            "  aiwfctl gui run --issue-id <issue-id>\n"
            "  aiwfctl gui validate --issue-id <issue-id>\n"
            "  aiwfctl gui self-test\n"
        )
    try:
        result = run_gui(args, repo_root, gui_command)
    except KeyError:
        return 1, f"Unknown gui command: {gui_command}\n"
    except Exception as exc:
        return 1, f"GUI runtime failed: {exc}\n"
    code = 0 if result.get("status") not in {"fail"} else 1
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    return code, _format_visual_runtime_result("GUI Runtime", gui_command, result)


def _handle_web_svg(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    web_svg_command = getattr(args, "web_svg_command", None)
    if web_svg_command is None:
        return 1, (
            "Web SVG Runtime\n\n"
            "Usage:\n"
            "  aiwfctl web-svg init-input\n"
            "  aiwfctl web-svg run --issue-id <issue-id>\n"
            "  aiwfctl web-svg validate --issue-id <issue-id>\n"
        )
    try:
        result = run_web_svg(args, repo_root, web_svg_command)
    except KeyError:
        return 1, f"Unknown web-svg command: {web_svg_command}\n"
    except Exception as exc:
        return 1, f"Web SVG runtime failed: {exc}\n"
    code = 0 if result.get("status") not in {"fail"} else 1
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    return code, _format_visual_runtime_result("Web SVG Runtime", web_svg_command, result)


def _handle_retrieval(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    retrieval_command = getattr(args, "retrieval_command", None)
    if retrieval_command is None:
        return 1, (
            "Retrieval Task Runtime\n\n"
            "Usage:\n"
            "  aiwfctl retrieval run --work-id <work-id> --task-file work/<work-id>/context/task-plan.json\n"
        )
    try:
        result = run_retrieval(args, repo_root, retrieval_command)
    except KeyError:
        return 1, f"Unknown retrieval command: {retrieval_command}\n"
    except Exception as exc:
        return 1, f"Retrieval runtime failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    summary = result.get("summary", {}) if isinstance(result.get("summary"), dict) else {}
    lines = [
        "Retrieval Task Runtime",
        "",
        f"Command : {retrieval_command}",
        f"Work ID : {result.get('work_id', '')}",
        f"Mode    : {result.get('execution_mode', '')}",
        f"JSON    : {result.get('json_report', '')}",
        f"Markdown: {result.get('markdown_report', '')}",
        "",
        "Summary",
        f"  total  : {summary.get('total', 0)}",
        f"  failed : {summary.get('failed', 0)}",
        f"  blocked: {summary.get('blocked', 0)}",
    ]
    return 0, "\n".join(lines).rstrip() + "\n"


def _handle_sdk(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    sdk_command = getattr(args, "sdk_command", None)
    if sdk_command is None:
        return 1, (
            "SDK Analysis\n\n"
            "Usage:\n"
            "  aiwfctl sdk analyze --work-id <work-id>\n"
            "  aiwfctl sdk discover --work-id <work-id>\n"
            "  aiwfctl sdk analyze --work-id <work-id> --source work/requirements/sdk\n\n"
            "Outputs:\n"
            f"  {reports_path_pattern('sdk-analysis-report.md')}\n"
            f"  {context_path_pattern('sdk-analysis-context.json')}\n"
            f"  {requirements_path_pattern('sdk-integration-requirements.md')}\n"
            f"  {reports_path_pattern('sdk-external-discovery-report.md')}\n"
            f"  {context_path_pattern('sdk-external-discovery.json')}\n"
            f"  {requirements_path_pattern('sdk-external-requirements.md')}\n"
        )
    try:
        result = run_sdk(args, repo_root, sdk_command)
    except Exception as exc:
        return 1, f"SDK analysis failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    return 0, format_sdk_result(result) + "\n"


def _handle_flutter(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    flutter_command = getattr(args, "flutter_command", None)
    if flutter_command is None:
        return 1, (
            "Flutter Multi-platform\n\n"
            "Usage:\n"
            "  aiwfctl flutter analyze --work-id <work-id>\n"
            "  aiwfctl flutter init --work-id <work-id> --targets android,web,windows\n"
            "  aiwfctl flutter verify --work-id <work-id> --execute\n"
            "  aiwfctl flutter build --work-id <work-id> --targets android,web,windows --mode release --execute --human-check approved\n"
            "  aiwfctl flutter finalize --work-id <work-id>\n"
            "  aiwfctl flutter run-workflow --work-id <work-id> --targets android,web,windows\n\n"
            "Outputs:\n"
            f"  {context_path_pattern('flutter-development-context.json')}\n"
            f"  {reports_path_pattern('flutter-multiplatform-report.md')}\n"
            f"  {work_path_pattern('evidence', 'flutter', 'common', 'verification-plan.md')}\n"
        )
    try:
        result = run_flutter(args, repo_root, flutter_command)
    except Exception as exc:
        return 1, f"Flutter multi-platform failed: {exc}\n"
    code = 0 if result.get("status") not in {"human-check-required", "failed"} else 2
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    return code, format_flutter_result(result) + "\n"


def _handle_mcp_group(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    mcp_group_command = getattr(args, "mcp_group_command", None)
    if mcp_group_command is None:
        return 1, (
            "MCP Server Group Implementation\n\n"
            "Usage:\n"
            "  aiwfctl mcp-group analyze --work-id <work-id>\n"
            "  aiwfctl mcp-group init --work-id <work-id> --components local-model-mcp-server,mcp-client\n"
            "  aiwfctl mcp-group run-workflow --work-id <work-id> --components local-model-mcp-server,mcp-client,local-ai-agent-runtime,discord-gateway\n\n"
            "Outputs:\n"
            f"  {context_path_pattern('mcp-server-group-implementation-context.json')}\n"
            f"  {reports_path_pattern('mcp-server-group-implementation-report.md')}\n"
            f"  {implementation_path_pattern('mcp-server-group', '<component>')}/\n"
        )
    try:
        result = run_mcp_group(args, repo_root, mcp_group_command)
    except Exception as exc:
        return 1, f"MCP server group implementation failed: {exc}\n"
    code = 0 if result.get("status") != "human-check-required" else 2
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    return code, format_mcp_group_result(result) + "\n"


def _handle_github_knowledge(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    github_knowledge_command = getattr(args, "github_knowledge_command", None)
    if github_knowledge_command is None:
        return 1, (
            "GitHub Knowledge Maintenance\n\n"
            "Usage:\n"
            "  aiwfctl github-knowledge init --repository <owner/repo>\n"
            "  default work folders: work/github/<target-branch>/<scan-mode> or work/github/original/<scan-mode>\n"
            "  aiwfctl github-knowledge analysis-template --work-id <work-id>\n"
            "  aiwfctl github-knowledge status --work-id <work-id>\n"
            "  aiwfctl github-knowledge next-action --work-id <work-id>\n"
            "  aiwfctl github-knowledge verify-remote --work-id <work-id>\n"
            "  aiwfctl github-knowledge cleanup-worktree --work-id <work-id> --force\n"
            "  aiwfctl github-knowledge artifact-integrity --work-id <work-id>\n"
            "  aiwfctl github-knowledge detect-rebase --work-id <work-id>\n"
            "  aiwfctl github-knowledge repair-plan --work-id <work-id>\n"
            "  aiwfctl github-knowledge rebase-plan --work-id <work-id>\n"
            "  aiwfctl github-knowledge rebase-review-intake --work-id <work-id> --human-check approved\n"
            "  aiwfctl github-knowledge sync-plan --work-id <work-id>\n"
            "  aiwfctl github-knowledge sync-review-plan --work-id <work-id>\n"
            "  aiwfctl github-knowledge sync-review-intake --work-id <work-id> --human-check approved\n"
            "  aiwfctl github-knowledge sync-apply --work-id <work-id> --action-id <action-id> --human-check approved\n\n"
            "  aiwfctl github-knowledge rebase-package --work-id <work-id> --target-branch <branch>\n"
            "  aiwfctl github-knowledge rebase-apply --work-id <work-id> --human-check approved\n\n"
            "  aiwfctl github-knowledge message-repair-plan --work-id <work-id>\n"
            "  aiwfctl github-knowledge message-review-intake --work-id <work-id> --human-check approved\n"
            "  aiwfctl github-knowledge message-repair-package --work-id <work-id> --target-branch <branch>\n\n"
            "  aiwfctl github-knowledge publish-verified-replay --work-id <work-id> --target-branch <branch> --expected-remote-sha <sha> --human-check approved\n"
            "  aiwfctl github-knowledge rag-candidate --work-id <work-id>\n\n"
            "Outputs:\n"
            f"  {context_path_pattern('github-knowledge-analysis.json')}\n"
            f"  {process_report_path_pattern('github-knowledge-repair-plan-*.md')}\n"
            f"  {process_report_path_pattern('github-documentation-sync-plan-*.md')}\n"
            f"  {process_report_path_pattern('github-documentation-sync-review-plan-*.md')}\n"
            f"  {process_report_path_pattern('github-history-message-repair-plan-*.md')}\n"
            f"  {context_path_pattern('rebase-replay-package.json')}\n"
            f"  {context_path_pattern('message-repair-package.json')}\n"
            f"  {process_report_path_pattern('github-history-rebase-replay-execution-*.md')}\n"
            f"  {process_report_path_pattern('github-knowledge-rag-candidate-*.md')}\n"
        )
    try:
        result = run_github_knowledge(
            args,
            repo_root,
            github_knowledge_command,
            metrics_factory=_github_knowledge_metrics_collector,
            metrics_recorder=_record_github_knowledge_metrics_result,
        )
    except KeyError:
        return 1, f"Unknown GitHub knowledge command: {github_knowledge_command}\n"
    except Exception as exc:
        return 1, f"GitHub knowledge maintenance failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = [
        "GitHub Knowledge Maintenance",
        "",
        f"Command : {github_knowledge_command}",
        f"Work ID : {result.get('work_id', getattr(args, 'work_id', ''))}",
    ]
    if "sync_plan" in result:
        lines.append(f"Plan    : {result.get('sync_plan', '')}")
    if "sync_review_plan" in result:
        lines.append(f"Review  : {result.get('sync_review_plan', '')}")
    if "repair_plan" in result:
        lines.append(f"Plan    : {result.get('repair_plan', '')}")
    if "rebase_plan" in result:
        lines.append(f"Plan    : {result.get('rebase_plan', '')}")
    if "message_repair_plan" in result:
        lines.append(f"Plan    : {result.get('message_repair_plan', '')}")
    if "plan_path" in result:
        lines.append(f"Review  : {result.get('plan_path', '')}")
    if "rag_candidate" in result:
        lines.append(f"RAG     : {result.get('rag_candidate', '')}")
    if "analysis_path" in result:
        lines.append(f"Analysis: {result.get('analysis_path', '')}")
    if "status" in result:
        lines.append(f"Status  : {result.get('status', '')}")
    if "findings" in result:
        lines.append(f"Findings: {len(result.get('findings', []))}")
    if "next_action" in result:
        next_action = result.get("next_action", {}) or {}
        lines.append(f"Next    : {next_action.get('action', '')}")
        if next_action.get("reason"):
            lines.append(f"Reason  : {next_action.get('reason', '')}")
        if next_action.get("verify_command"):
            lines.append(f"Verify  : {next_action.get('verify_command', '')}")
        if next_action.get("command"):
            lines.append(f"Command : {next_action.get('command', '')}")
        if next_action.get("cleanup_command"):
            lines.append(f"Cleanup : {next_action.get('cleanup_command', '')}")
    if "latest_package" in result:
        package = result.get("latest_package", {}) or {}
        lines.append(f"Package : {package.get('path', '')}")
        lines.append(f"Push OK : {str(package.get('allow_push', False)).lower()}")
    if "worktree" in result:
        worktree = result.get("worktree", {}) or {}
        lines.append(f"Worktree: {worktree.get('path', '')}")
        lines.append(f"Exists  : {str(worktree.get('exists', False)).lower()}")
    if "matches" in result:
        lines.append(f"Matches : {str(result.get('matches', False)).lower()}")
    if "actual_remote_sha" in result:
        lines.append(f"Remote  : {result.get('actual_remote_sha', '')}")
    if "removed" in result:
        lines.append(f"Removed : {str(result.get('removed', False)).lower()}")
    if "exists_after" in result:
        lines.append(f"Exists After: {str(result.get('exists_after', False)).lower()}")
    if "force_required" in result:
        lines.append(f"Force Required: {str(result.get('force_required', False)).lower()}")
    if "report_json" in result:
        lines.append(f"JSON    : {result.get('report_json', '')}")
    if "rebase_replay_package" in result:
        lines.append(f"Package : {result.get('rebase_replay_package', '')}")
        lines.append(f"Targets : {result.get('candidate_count', 0)} candidate(s)")
    if "message_repair_package" in result:
        lines.append(f"Package : {result.get('message_repair_package', '')}")
        lines.append(f"Targets : {result.get('candidate_count', 0)} candidate(s)")
    if "report_path" in result:
        lines.append(f"Report  : {result.get('report_path', '')}")
    if "mapping_path" in result:
        lines.append(f"SHA Map : {result.get('mapping_path', '')}")
    if "new_tip" in result:
        lines.append(f"New Tip : {result.get('new_tip', '')}")
    if "remote_before" in result:
        lines.append(f"Remote Before: {result.get('remote_before', '')}")
    if "remote_after" in result:
        lines.append(f"Remote After : {result.get('remote_after', '')}")
    if "action_id" in result:
        lines.append(f"Action  : {result.get('action_id', '')}")
    if "approved_count" in result:
        lines.append(f"Approved: {result.get('approved_count', 0)}")
    if "rejected_count" in result:
        lines.append(f"Rejected: {result.get('rejected_count', 0)}")
    if "apply_mode" in result:
        lines.append(f"Apply   : {result.get('apply_mode', '')}")
    if "pushed" in result:
        lines.append(f"Pushed  : {str(result.get('pushed', False)).lower()}")
    if "dry_run" in result:
        lines.append(f"Dry Run : {str(result.get('dry_run', False)).lower()}")
    if "executed" in result:
        lines.append(f"Executed: {str(result.get('executed', False)).lower()}")
    return 0, "\n".join(lines).rstrip() + "\n"


def _handle_work(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    work_command = getattr(args, "work_command", None)
    if work_command is None:
        return 1, (
            "Work Cleanup\n\n"
            "Usage:\n"
            "  aiwfctl work cleanup-check --work-id github/original --recursive\n"
            "  aiwfctl work cleanup-apply --work-id github/original --recursive --human-check approved\n"
        )
    try:
        result = run_work_cleanup(args, repo_root, work_command)
    except Exception as exc:
        return 1, f"Work cleanup failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = [
        "Work Cleanup",
        "",
        f"Command : {work_command}",
        f"Status  : {result.get('status', '')}",
        f"Target  : {result.get('target', '')}",
        f"Checks  : {len(result.get('checks', []))}",
    ]
    if "removed" in result:
        lines.append(f"Removed : {str(result.get('removed', False)).lower()}")
    if result.get("apply_command"):
        lines.append(f"Apply   : {result.get('apply_command', '')}")
    blockers = result.get("blockers", [])
    if blockers:
        lines.extend(["", "Blockers"])
        lines.extend(f"  - {item}" for item in blockers)
    return 0, "\n".join(lines).rstrip() + "\n"


def _handle_self_improvement(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    self_command = getattr(args, "self_improvement_command", None)
    if self_command is None:
        return 1, (
            "Self Improvement\n\n"
            "Usage:\n"
            "  aiwfctl self-improvement create-feedback --target-workflow <workflow> --situation <text> --friction <text>\n"
            "  aiwfctl self-improvement create-feedback --target-workflow <workflow> --situation <text> --friction <text> --runtime-trace-id <trace-id>\n"
            "  aiwfctl self-improvement review-feedback --feedback <path> --decision accepted --reviewer Human --reason <text>\n"
            "  aiwfctl self-improvement issue-body --feedback <path>\n"
            "  aiwfctl self-improvement evidence-scaffold --work-id issue-<number>\n"
        )
    try:
        result = run_self_improvement(args, repo_root, self_command)
    except KeyError:
        return 1, f"Unknown self-improvement command: {self_command}\n"
    except Exception as exc:
        return 1, f"Self improvement failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = ["Self Improvement", "", f"Command : {self_command}"]
    for key, label in [
        ("feedback_readme", "README  "),
        ("feedback", "Feedback"),
        ("issue_body", "Issue   "),
        ("branch", "Branch  "),
        ("work_id", "Work ID "),
        ("process_report", "Process "),
        ("test_evidence", "Evidence"),
        ("artifact_index", "Artifacts"),
        ("decision", "Decision"),
        ("status", "Status  "),
    ]:
        if key in result:
            lines.append(f"{label}: {result.get(key, '')}")
    return 0, "\n".join(lines).rstrip() + "\n"


def _handle_review(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    review_command = getattr(args, "review_command", None)
    if review_command is None:
        return 1, (
            "Ariadne Review Council\n\n"
            "Usage:\n"
            "  aiwfctl review plan --work-id <work-id> --intent <text> --changed-file runtime/review/council.py\n"
            "  aiwfctl review start --work-id <work-id> --intent <text> --reviewer security\n"
            "  aiwfctl review handoff --review-id <review-id>\n"
            "  aiwfctl review orchestrate --review-id <review-id>\n"
            "  aiwfctl review next-action --review-id <review-id>\n"
            "  aiwfctl review summary --review-id <review-id>\n"
            "  aiwfctl review human-gate --review-id <review-id> --gate review-council-final-verdict --human-check approved\n"
            "  aiwfctl review run-specialist --review-id <review-id> --reviewer security\n"
            "  aiwfctl review execute-specialist --review-id <review-id> --reviewer security --human-check approved --agent-command <command>\n"
            "  aiwfctl review draft-findings --review-id <review-id> --reviewer security --report <path>\n"
            "  aiwfctl review capture-knowledge --review-id <review-id>\n"
            "  aiwfctl review rag-build --review-id <review-id>\n"
            "  aiwfctl review add-finding --review-id <review-id> --reviewer security --category security --severity high --claim <text> --verdict fail\n"
            "  aiwfctl review challenge --review-id <review-id> --challenger runtime-quality --summary <text>\n"
            "  aiwfctl review evidence-gate --review-id <review-id>\n"
            "  aiwfctl review reinspect --review-id <review-id> --finding-id FND-001 --status verified --reviewer security --summary <text>\n"
            "  aiwfctl review status --review-id <review-id>\n"
            "  aiwfctl review issues --review-id <review-id>\n"
            "  aiwfctl review verdict --review-id <review-id>\n"
        )
    try:
        result = run_review(args, repo_root, review_command)
    except KeyError:
        return 1, f"Unknown review command: {review_command}\n"
    except Exception as exc:
        return 1, f"Review council failed: {exc}\n"
    code = 0
    verdict_value = result.get("verdict")
    verdict_status = verdict_value.get("verdict") if isinstance(verdict_value, dict) else verdict_value
    if (
        result.get("artifact_type") == "review-council-human-gate"
        and result.get("status") == "blocked"
    ) or (
        result.get("artifact_type") == "review-council-specialist-execution"
        and result.get("status") in {"human-check-required", "blocked", "failed"}
    ) or verdict_status in {"CHANGES_REQUIRED", "HUMAN_DECISION_REQUIRED", "REJECTED"}:
        code = 2
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = ["Ariadne Review Council", "", f"Command : {review_command}"]
    for key, label in [
        ("review_id", "Review ID"),
        ("run_id", "Run ID   "),
        ("challenge_id", "Challenge"),
        ("reinspection_id", "Reinspect"),
        ("summary_id", "Summary  "),
        ("gate", "Gate     "),
        ("work_id", "Work ID  "),
        ("reviewer", "Reviewer "),
        ("agent_id", "Agent    "),
        ("status", "Status   "),
        ("verdict", "Verdict  "),
        ("draft_count", "Drafts   "),
        ("finding_count", "Findings "),
        ("issue_count", "Issues   "),
        ("rag_candidate_count", "RAG Candidates"),
    ]:
        if key in result:
            value = result.get(key, "")
            if key == "verdict" and isinstance(value, dict):
                value = value.get("verdict", "")
            lines.append(f"{label}: {value}")
    if "reason" in result:
        lines.append(f"Reason   : {result.get('reason', '')}")
    if "prompt_path" in result:
        lines.append(f"Prompt   : {result.get('prompt_path', '')}")
    if "output_path" in result:
        lines.append(f"Output   : {result.get('output_path', '')}")
    if "source_document" in result:
        lines.append(f"RAG Doc  : {result.get('source_document', '')}")
    if "source_dir" in result:
        lines.append(f"RAG Src  : {result.get('source_dir', '')}")
    if "missing_evidence" in result:
        lines.append(f"Missing Evidence: {len(result.get('missing_evidence', []))}")
    if "missing_required_tests" in result:
        lines.append(f"Missing Tests   : {len(result.get('missing_required_tests', []))}")
    required_reviewers = result.get("required_reviewers")
    if isinstance(required_reviewers, list):
        lines.append(f"Reviewers       : {', '.join(required_reviewers)}")
    reviewer_handoffs = result.get("reviewer_handoffs")
    if isinstance(reviewer_handoffs, list):
        lines.append(f"Handoffs        : {len(reviewer_handoffs)}")
    if "start_command" in result:
        lines.extend(["", "Start Command", f"  {result.get('start_command', '')}"])
    if "build_command" in result:
        lines.extend(["", "Build Command", f"  {result.get('build_command', '')}"])
    if "command" in result and result.get("artifact_type") == "review-council-specialist-execution":
        lines.extend(["", "Execution Command", f"  {result.get('command', '')}"])
    draft_findings = result.get("draft_findings")
    if isinstance(draft_findings, dict):
        lines.append(f"Draft Findings  : {draft_findings.get('draft_count', 0)}")
    next_actions = result.get("next_actions", [])
    if next_actions:
        lines.extend(["", "Next Actions"])
        for item in next_actions:
            command = item.get("agent_command") or item.get("command", "")
            lines.append(f"  - {item.get('action', '')}: {command}")
    selected_action = result.get("selected_action")
    if isinstance(selected_action, dict):
        command = selected_action.get("agent_command") or selected_action.get("command", "")
        lines.extend(["", "Selected Action", f"  {selected_action.get('action', '')}: {command}"])
    artifacts = result.get("artifacts", {})
    if isinstance(artifacts, dict) and artifacts:
        lines.extend(["", "Artifacts"])
        lines.extend(f"  - {key}: {value}" for key, value in artifacts.items())
    issues = result.get("issues", [])
    if issues:
        lines.extend(["", "Issues"])
        for item in issues:
            lines.append(
                f"  - {item.get('issue_id', '')}: {item.get('severity', '')} blocking={str(item.get('blocking', False)).lower()} {item.get('claim', '')}"
            )
    return code, "\n".join(lines).rstrip() + "\n"


def _handle_close_archive(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    close_command = getattr(args, "close_archive_command", None)
    if close_command is None:
        return 1, (
            "Close Archive\n\n"
            "Usage:\n"
            "  aiwfctl close-archive prepare --work-id <work-id>\n"
            "  aiwfctl close-archive audit --work-id <work-id> --archive-id <archive-id>\n"
            "  aiwfctl close-archive prune --work-id <work-id> --execute --human-check approved\n"
        )
    try:
        result = run_close_archive(args, repo_root, close_command)
    except KeyError:
        return 1, f"Unknown close-archive command: {close_command}\n"
    except Exception as exc:
        return 1, f"Close archive failed: {exc}\n"
    if getattr(args, "json", False):
        return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = [
        "Close Archive",
        "",
        f"Command : {close_command}",
        f"Status  : {result.get('status', '')}",
        f"Archive : {result.get('archive_dir', result.get('archive', ''))}",
    ]
    if "prune_target_count" in result:
        lines.append(f"Prune   : {result.get('prune_target_count', 0)} target(s)")
    if "removed_count" in result:
        lines.append(f"Removed : {result.get('removed_count', 0)}")
    return 0, "\n".join(lines).rstrip() + "\n"


def _handle_iac(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    iac_command = getattr(args, "iac_command", None)
    if iac_command != "template":
        return 1, (
            "IaC Template\n\n"
            "Usage:\n"
            "  aiwfctl iac template list\n"
            "  aiwfctl iac template prepare --template opentelemetry-collector --work-id <work-id>\n"
            "  aiwfctl iac template health --template opentelemetry-collector --work-id <work-id>\n\n"
            "Outputs:\n"
            f"  {work_path_pattern('source', 'infrastructure', 'opentelemetry-collector')}/\n"
            f"  {context_path_pattern('iac-template-context.json')}\n"
            f"  {context_path_pattern('iac-template-health-context.json')}\n"
            f"  {test_evidence_path_pattern('infrastructure/opentelemetry-collector/health-summary.md')}\n"
        )
    template_command = getattr(args, "iac_template_command", None)
    try:
        result = run_iac_template(args, repo_root, template_command)
    except KeyError:
        return 1, f"Unknown IaC template command: {template_command}\n"
    except Exception as exc:
        return 1, f"IaC template failed: {exc}\n"
    code = 0 if result.get("status") not in {"human-check-required", "missing-template"} else 2
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    lines = ["IaC Template", "", f"Status   : {result.get('status', 'available')}", f"Template : {result.get('template', '')}"]
    artifacts = result.get("artifacts", {})
    if artifacts:
        lines.extend(["", "Artifacts"])
        lines.extend(f"  - {key}: {value}" for key, value in artifacts.items())
    prepared = result.get("prepared", {})
    if prepared:
        lines.extend(["", f"Destination: {prepared.get('destination', '')}"])
    for item in result.get("templates", []):
        lines.append(f"  - {item.get('name', '')}: {item.get('template_path', '')} exists={item.get('exists', False)}")
    human_checks = result.get("human_checks", [])
    if human_checks:
        lines.extend(["", "Human Check"])
        lines.extend(f"  - {item}" for item in human_checks)
    return code, "\n".join(lines).rstrip() + "\n"


def _handle_integration(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    integration_command = getattr(args, "integration_command", None)
    if integration_command is None:
        return 1, (
            "System Integration Quality\n\n"
            "Usage:\n"
            "  aiwfctl integration analyze --work-id <work-id>\n"
            "  aiwfctl integration verify --work-id <work-id>\n"
            "  aiwfctl integration verify --work-id <work-id> --with-emulator\n\n"
            "  aiwfctl integration emulator prepare --work-id <work-id>\n"
            "  aiwfctl integration emulator health --work-id <work-id>\n\n"
            "  aiwfctl integration test-plan --work-id <work-id>\n\n"
            "  aiwfctl integration finalize --work-id <work-id>\n\n"
            "Outputs:\n"
            f"  {reports_path_pattern('system-integration-report.md')}\n"
            f"  {context_path_pattern('integration-context.json')}\n"
            f"  {context_path_pattern('emulator-context.json')}\n"
            f"  {context_path_pattern('emulator-health-context.json')}\n"
            f"  {test_evidence_path_pattern('emulator/health-summary.md')}\n"
            f"  {context_path_pattern('integration-test-plan-context.json')}\n"
            f"  {test_evidence_path_pattern('integration-test/integration-test-runbook.md')}\n"
            f"  {context_path_pattern('integration-finalization-context.json')}\n"
            f"  {reports_path_pattern('system-integration-final-report.md')}\n"
        )
    try:
        result = run_integration(args, repo_root, integration_command)
    except Exception as exc:
        return 1, f"System integration failed: {exc}\n"
    code = 0 if result.get("status") != "human-check-required" else 2
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    return code, format_integration_result(result) + "\n"


def _handle_doctor(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    result = run_doctor(args, repo_root)
    code = 1 if result.get("status") == "fail" else 0
    if getattr(args, "json", False):
        return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    repairs = result.get("repairs", [])
    lines = [
        "Workflow Doctor",
        "",
        f"Status        : {result.get('status', '')}",
        f"Warning Count : {result.get('warning_count', 0)}",
        f"Repair Count  : {sum(len(item.get('repairs', [])) for item in repairs if isinstance(item, dict))}",
    ]
    gate_restart = result.get("gate_restart", {})
    if isinstance(gate_restart, dict):
        lines.append(f"Restart From : {gate_restart.get('restart_from', '')}")
        next_key = "next_on_pass" if result.get("status") == "pass" else "next_on_fail"
        lines.append(f"Next         : {gate_restart.get(next_key, '')}")
    warnings = result.get("warnings", [])
    if warnings:
        lines.extend(["", "Warnings"])
        for warning in warnings:
            lines.extend(
                [
                    f"  - {warning.get('id', '')}",
                    f"    message: {warning.get('message', '')}",
                ]
            )
            if warning.get("next_action"):
                lines.append(f"    next: {warning.get('next_action', '')}")
            if warning.get("repair_command"):
                lines.append(f"    repair: {warning.get('repair_command', '')}")
            if warning.get("ignore_condition"):
                lines.append(f"    ignore: {warning.get('ignore_condition', '')}")
            for path in warning.get("paths", [])[:CTL_WARNING_PATH_PREVIEW_LIMIT]:
                lines.append(f"    path: {path}")
    else:
        lines.extend(["", "Warnings", "  - なし"])
    if repairs:
        lines.extend(["", "Repairs"])
        for repair in repairs:
            if not isinstance(repair, dict):
                continue
            repair_items = repair.get("repairs", [])
            lines.extend(
                [
                    f"  - {repair.get('artifact_type', 'repair')}",
                    f"    status: {repair.get('status', '')}",
                    f"    repaired: {len(repair_items) if isinstance(repair_items, list) else 0}",
                ]
            )
            if isinstance(repair_items, list):
                for item in repair_items[:CTL_WARNING_PATH_PREVIEW_LIMIT]:
                    if not isinstance(item, dict):
                        continue
                    detail = item.get("node_id") or item.get("path") or item.get("case_id") or item.get("kinds", "")
                    if detail:
                        lines.append(f"    item: {detail}")
    return code, "\n".join(lines).rstrip() + "\n"


def _handle_help(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    return run_help_command(args, repo_root, registry, color=color)


def _handle_preflight(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    return run_preflight(args, repo_root)


def _handle_tools(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    tools_command = getattr(args, "tools_command", None)
    if tools_command is None:
        return 1, (
            "Runtime Tools\n\n"
            "Usage:\n"
            "  aiwfctl tools coverage-audit --skip-run\n"
            "  aiwfctl tools spec-check\n"
            "  aiwfctl tools bom-scan --paths docs\n"
            "  aiwfctl tools encoding-guard --paths docs\n"
        )
    try:
        return run_tools(args, repo_root, tools_command)
    except KeyError:
        return 1, f"Unknown tools command: {tools_command}\n"


def _handle_release(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    release_command = getattr(args, "release_command", None)
    if release_command is None:
        return 1, (
            "Release Runtime\n\n"
            "Usage:\n"
            "  aiwfctl release validate --json\n"
            "  aiwfctl release manifest --artifact LICENSE\n"
        )
    if release_command == "validate":
        result = release_validation.validation_result(
            repo_root,
            getattr(args, "expected_license", None),
            fail_on_warning=getattr(args, "fail_on_warning", False),
        )
        if getattr(args, "json", False):
            output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        else:
            output = release_validation.format_validation_result(result)
        return (0 if result.get("status") == "pass" else 1), output
    if release_command == "manifest":
        try:
            result = release_manifest.build_manifest(
                repo_root,
                getattr(args, "version", None),
                getattr(args, "tag", None),
                getattr(args, "artifact", []),
                getattr(args, "generated_at_utc", None),
            )
        except FileNotFoundError as exc:
            return 1, f"{exc}\n"
        output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if getattr(args, "output", ""):
            output_path = (repo_root / args.output).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output, encoding="utf-8")
            result["output"] = str(output_path.relative_to(repo_root))
            output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        return 0, output
    return 1, f"Unknown release command: {release_command}\n"


COMMAND_HANDLERS: dict[str, CommandHandler] = {
    "status": _handle_status,
    "env": _handle_env,
    "trace": _handle_trace,
    "context": _handle_context,
    "human-gate": _handle_human_gate,
    "design": _handle_design,
    "intake": _handle_intake,
    "scm": _handle_scm,
    "github": _handle_github,
    "knowledge": _handle_knowledge,
    "rag": _handle_rag,
    "workflow": _handle_workflow,
    "gui": _handle_gui,
    "web-svg": _handle_web_svg,
    "retrieval": _handle_retrieval,
    "sdk": _handle_sdk,
    "flutter": _handle_flutter,
    "mcp-group": _handle_mcp_group,
    "github-knowledge": _handle_github_knowledge,
    "work": _handle_work,
    "self-improvement": _handle_self_improvement,
    "review": _handle_review,
    "close-archive": _handle_close_archive,
    "iac": _handle_iac,
    "integration": _handle_integration,
    "preflight": _handle_preflight,
    "tools": _handle_tools,
    "release": _handle_release,
    "doctor": _handle_doctor,
    "help": _handle_help,
}


def run_impl(args: argparse.Namespace, *, helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    _bind_helpers(helpers)
    repo_root = repo_root_from_args(args)
    registry = load_registry(repo_root)
    command = args.command
    if command is None:
        return 1, format_root_usage_warning(color=color)
    handler = COMMAND_HANDLERS.get(command)
    if handler is None:
        return 1, f"Unknown command: {command}\n"
    return handler(args, repo_root, registry, helpers, color)
