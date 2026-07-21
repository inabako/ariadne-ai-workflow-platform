from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from runtime.common.ctl_close_archive_adapter import run_close_archive
from runtime.common.ctl_context_adapter import run_context
from runtime.common.ctl_doctor_adapter import run_doctor
from runtime.common.ctl_flutter_adapter import format_result as format_flutter_result
from runtime.common.ctl_flutter_adapter import run_flutter
from runtime.common.ctl_github_knowledge_adapter import run_github_knowledge
from runtime.common.ctl_human_gate_adapter import run_human_gate
from runtime.common.ctl_iac_adapter import run_iac_template
from runtime.common.ctl_integration_adapter import format_result as format_integration_result
from runtime.common.ctl_integration_adapter import run_integration
from runtime.common.ctl_knowledge_adapter import run_knowledge
from runtime.common.ctl_mcp_group_adapter import format_result as format_mcp_group_result
from runtime.common.ctl_mcp_group_adapter import run_mcp_group
from runtime.common.ctl_sdk_adapter import format_result as format_sdk_result
from runtime.common.ctl_sdk_adapter import run_sdk
from runtime.common.ctl_self_improvement_adapter import run_self_improvement
from runtime.common.ctl_work_adapter import run_work_cleanup


HelperModule = Any
CommandHandler = Callable[[argparse.Namespace, Path, dict[str, Any], HelperModule, bool], tuple[int, str]]


# These names are supplied from runtime.common.ctl through _bind_helpers().
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
    return 0, format_knowledge_result(result)


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
    lines = [
        "Workflow Doctor",
        "",
        f"Status        : {result.get('status', '')}",
        f"Warning Count : {result.get('warning_count', 0)}",
        f"Repair Count  : {sum(len(item.get('repairs', [])) for item in result.get('repairs', []))}",
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
            for path in warning.get("paths", [])[:10]:
                lines.append(f"    path: {path}")
    else:
        lines.extend(["", "Warnings", "  - なし"])
    return code, "\n".join(lines).rstrip() + "\n"


def _handle_help(args: argparse.Namespace, repo_root: Path, registry: dict[str, Any], helpers: HelperModule, color: bool = False) -> tuple[int, str]:
    return run_help_command(args, repo_root, registry, color=color)


COMMAND_HANDLERS: dict[str, CommandHandler] = {
    "env": _handle_env,
    "context": _handle_context,
    "human-gate": _handle_human_gate,
    "knowledge": _handle_knowledge,
    "sdk": _handle_sdk,
    "flutter": _handle_flutter,
    "mcp-group": _handle_mcp_group,
    "github-knowledge": _handle_github_knowledge,
    "work": _handle_work,
    "self-improvement": _handle_self_improvement,
    "close-archive": _handle_close_archive,
    "iac": _handle_iac,
    "integration": _handle_integration,
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

