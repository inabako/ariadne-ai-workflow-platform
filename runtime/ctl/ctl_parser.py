from __future__ import annotations

import argparse

from runtime.constants.paths import GENERATED_JSONIZED
from runtime.constants.workspace import (
    DEFAULT_TARGET_REPO_HELP,
    DEFAULT_WORK_DIR_HELP,
    process_report_path_pattern,
    work_path_pattern,
)
from runtime.rag import duckdb_store
from runtime.workflow import close_archive
from runtime.workflow import context_first
from runtime.workflow import dispatcher_context
from runtime.workflow import flutter_multiplatform
from runtime.workflow import github_knowledge_maintenance
from runtime.workflow import self_improvement


def _add_review_packet_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--work-id", required=True)
    command.add_argument("--review-id", default="")
    command.add_argument("--target", default="")
    command.add_argument("--target-revision", default="")
    command.add_argument("--intent", required=True)
    command.add_argument("--requirement", action="append", default=[])
    command.add_argument("--changed-file", action="append", default=[])
    command.add_argument("--guardrail", action="append", default=[])
    command.add_argument("--evidence", action="append", default=[])
    command.add_argument("--scope", action="append", default=[])
    command.add_argument("--known-constraint", action="append", default=[])
    command.add_argument("--reviewer", action="append", default=[])
    command.add_argument("--json", action="store_true")


def _add_review_lookup_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--review-id", default="")
    command.add_argument("--work-id", default="")
    command.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aiwfctl", description="Ariadne AI Workflow control helper.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command")

    help_cmd = sub.add_parser("help", help="AI workflow prompt command help.")
    help_sub = help_cmd.add_subparsers(dest="help_command")

    help_sub.add_parser("list", help="List workflow prompt commands.")

    show = help_sub.add_parser("show", help="Show one workflow command.")
    show.add_argument("name")

    search = help_sub.add_parser("search", help="Search workflow command help.")
    search.add_argument("keywords", nargs="+")

    open_cmd = help_sub.add_parser("open", help="Print searchable full help markdown.")
    open_cmd.add_argument("--query", action="append", default=[], help="Filter full help by keyword. Can be repeated.")

    markdown = help_sub.add_parser("markdown", help="Write searchable help markdown.")
    markdown.add_argument("--output", default="work/help/ai-workflow-help.md")
    markdown.add_argument("--query", action="append", default=[], help="Filter markdown by keyword. Can be repeated.")

    env_cmd = sub.add_parser("env", help="Select workflow execution environment.")
    env_sub = env_cmd.add_subparsers(dest="env_command")

    env_sub.add_parser("list", help="List public execution environments.")

    env_show = env_sub.add_parser("show", help="Show one public execution environment.")
    env_show.add_argument("environment")

    env_select = env_sub.add_parser("select", help="Select an execution environment for a workflow, extension, or keyword.")
    env_select.add_argument("target")
    env_select.add_argument("--json", action="store_true", help="Print selection as JSON.")
    env_select.add_argument("--work-id", default="", help=f"Write selection artifacts under {process_report_path_pattern()}.")
    env_select.add_argument("--output", default="", help="Write selection artifact to an explicit .md or .json path.")
    env_select.add_argument("--selected-by", choices=["dispatcher", "human", "workflow"], default="dispatcher")
    env_select.add_argument("--selection-mode", choices=["manual", "auto", "human-check"], default="manual")

    env_check = env_sub.add_parser("check", help="Alias of env select for pre-execution checks.")
    env_check.add_argument("target")
    env_check.add_argument("--json", action="store_true", help="Print selection as JSON.")
    env_check.add_argument("--work-id", default="", help=f"Write selection artifacts under {process_report_path_pattern()}.")
    env_check.add_argument("--output", default="", help="Write selection artifact to an explicit .md or .json path.")
    env_check.add_argument("--selected-by", choices=["dispatcher", "human", "workflow"], default="dispatcher")
    env_check.add_argument("--selection-mode", choices=["manual", "auto", "human-check"], default="manual")

    context_cmd = sub.add_parser("context", help="Create and inspect Context First Dispatcher Context.")
    context_sub = context_cmd.add_subparsers(dest="context_command")
    context_init = context_sub.add_parser("init", help="Create workflow/tool/runtime/execution-plan context.")
    dispatcher_context.add_init_arguments(context_init)
    context_init.add_argument("--json", action="store_true", help="Print result as JSON.")
    context_show = context_sub.add_parser("show", help="Show Context First manifest.")
    context_show.add_argument("--work-dir", required=True)
    context_show.add_argument("--json", action="store_true", help="Print result as JSON.")
    context_require = context_sub.add_parser("require", help="Require dispatcher context entries.")
    context_require.add_argument("--work-dir", required=True)
    context_require.add_argument("--context", action="append", required=True, choices=sorted(context_first.DISPATCHER_CONTEXT_TYPES))
    context_require.add_argument("--json", action="store_true", help="Print result as JSON.")
    context_require_env = context_sub.add_parser("require-environment", help="Require a selected execution environment.")
    context_require_env.add_argument("--work-dir", required=True)
    context_require_env.add_argument("--environment", required=True)
    context_require_env.add_argument("--json", action="store_true", help="Print result as JSON.")

    human_gate_cmd = sub.add_parser("human-gate", help="Inspect and enforce Human Gate Registry.")
    human_gate_sub = human_gate_cmd.add_subparsers(dest="human_gate_command")
    human_gate_list = human_gate_sub.add_parser("list", help="List registered human gates.")
    human_gate_list.add_argument("--json", action="store_true")
    human_gate_check = human_gate_sub.add_parser("check", help="Check one human gate approval value.")
    human_gate_check.add_argument("--gate", required=True)
    human_gate_check.add_argument("--human-check", default="pending")
    human_gate_check.add_argument("--json", action="store_true")

    knowledge_cmd = sub.add_parser("knowledge", help="Manage generated DuckDB RAG read model.")
    knowledge_cmd.add_argument("--db", default=str(duckdb_store.DEFAULT_DB_PATH), help="Generated DuckDB file path.")
    knowledge_sub = knowledge_cmd.add_subparsers(dest="knowledge_command")

    knowledge_init = knowledge_sub.add_parser("init", help="Create generated DuckDB RAG schema.")
    knowledge_init.add_argument("--json", action="store_true")

    knowledge_migrate = knowledge_sub.add_parser("migrate", help="Register JSON RAG records from a directory.")
    knowledge_migrate.add_argument("--source", required=True)
    knowledge_migrate.add_argument("--policy", default=str(duckdb_store.ingestion_optimizer.DEFAULT_POLICY_PATH))
    knowledge_migrate.add_argument("--error-log", default=str(duckdb_store.DEFAULT_ERROR_LOG))
    knowledge_migrate.add_argument("--json", action="store_true")

    knowledge_source = knowledge_sub.add_parser("source", help="Manage external RAG source repository clone.")
    knowledge_source.add_argument("--path", default=str(duckdb_store.DEFAULT_SOURCE_REPO_PATH))
    knowledge_source.add_argument("--url", default=duckdb_store.DEFAULT_SOURCE_REPO_URL)
    knowledge_source_sub = knowledge_source.add_subparsers(dest="source_command", required=True)
    knowledge_source_sub.add_parser("status", help="Inspect local source repository clone.")
    knowledge_source_clone = knowledge_source_sub.add_parser("clone", help="Clone source repository when missing.")
    knowledge_source_clone.add_argument("--pull-if-exists", action="store_true")
    knowledge_source_sub.add_parser("pull", help="Pull source repository clone.")
    knowledge_source_import = knowledge_source_sub.add_parser("import-local", help="Copy local RAG JSON sources into source repository.")
    knowledge_source_import.add_argument("--clean", action="store_true")
    knowledge_source.add_argument("--json", action="store_true")

    knowledge_rebuild = knowledge_sub.add_parser("rebuild", help="Rebuild DuckDB read model from standard RAG JSON sources.")
    knowledge_rebuild.add_argument("--source", action="append", default=[])
    knowledge_rebuild.add_argument("--source-repo", default="")
    knowledge_rebuild.add_argument("--source-repo-url", default=duckdb_store.DEFAULT_SOURCE_REPO_URL)
    knowledge_rebuild.add_argument("--policy", default=str(duckdb_store.ingestion_optimizer.DEFAULT_POLICY_PATH))
    knowledge_rebuild.add_argument("--error-log", default=str(duckdb_store.DEFAULT_ERROR_LOG))
    knowledge_rebuild.add_argument("--reset", action="store_true")
    knowledge_rebuild.add_argument("--json", action="store_true")

    knowledge_ingest = knowledge_sub.add_parser("ingest", help="Register one JSON RAG record.")
    knowledge_ingest.add_argument("--file", required=True)
    knowledge_ingest.add_argument("--policy", default=str(duckdb_store.ingestion_optimizer.DEFAULT_POLICY_PATH))
    knowledge_ingest.add_argument("--json", action="store_true")

    knowledge_search = knowledge_sub.add_parser("search", help="Search generated DuckDB RAG read model.")
    duckdb_store.add_search_arguments(knowledge_search)
    knowledge_search.add_argument("--json", action="store_true")

    knowledge_export = knowledge_sub.add_parser("export-context", help="Export DuckDB RAG search results as context JSON.")
    duckdb_store.add_search_arguments(knowledge_export)
    knowledge_export.add_argument("--output", required=True)
    knowledge_export.add_argument("--max-chars", type=int, default=4000)
    knowledge_export.add_argument("--json", action="store_true")

    knowledge_verify = knowledge_sub.add_parser("verify", help="Verify DuckDB reference searches and write evidence.")
    knowledge_verify.add_argument("--query", action="append", default=[])
    knowledge_verify.add_argument("--min-results", type=int, default=1)
    knowledge_verify.add_argument("--limit", type=int, default=5)
    knowledge_verify.add_argument("--output", default=str(duckdb_store.DEFAULT_REFERENCE_CHECK_OUTPUT))
    knowledge_verify.add_argument("--work-id", default="")
    knowledge_verify.add_argument("--work-dir", default="")
    knowledge_verify.add_argument("--source-repo", default="")
    knowledge_verify.add_argument("--json", action="store_true")

    sdk_cmd = sub.add_parser("sdk", help="Analyze SDK input before requirement discovery review drafting.")
    sdk_sub = sdk_cmd.add_subparsers(dest="sdk_command")
    sdk_analyze = sdk_sub.add_parser("analyze", help="Analyze work/requirements/sdk and create SDK analysis context.")
    sdk_analyze.add_argument("--work-id", required=True)
    sdk_analyze.add_argument("--source", default="", help="SDK program directory. Default: work/requirements/sdk")
    sdk_analyze.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    sdk_analyze.add_argument(
        "--knowledge-dir",
        default="",
        help=f"Knowledge JSON output directory. Default: {GENERATED_JSONIZED.as_posix()}",
    )
    sdk_analyze.add_argument("--no-knowledge", action="store_true", help="Do not write Knowledge JSON.")
    sdk_analyze.add_argument("--skip-sdk-analysis", action="store_true")
    sdk_analyze.add_argument("--max-files", type=int, default=200)
    sdk_analyze.add_argument("--max-bytes", type=int, default=120_000)
    sdk_analyze.add_argument("--json", action="store_true")
    sdk_discover = sdk_sub.add_parser("discover", help="Create external source discovery plan from work/requirements/sdk.")
    sdk_discover.add_argument("--work-id", required=True)
    sdk_discover.add_argument("--source", default="", help="SDK program directory. Default: work/requirements/sdk")
    sdk_discover.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    sdk_discover.add_argument("--max-files", type=int, default=200)
    sdk_discover.add_argument("--max-bytes", type=int, default=120_000)
    sdk_discover.add_argument("--json", action="store_true")

    flutter_cmd = sub.add_parser("flutter", help="Analyze Flutter multi-platform targets and build dispatch.")
    flutter_sub = flutter_cmd.add_subparsers(dest="flutter_command")
    for name in ["analyze", "init", "verify", "build", "run-workflow"]:
        flutter_item = flutter_sub.add_parser(name)
        flutter_item.add_argument("--work-id", required=True)
        flutter_item.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
        flutter_item.add_argument("--target-repo", default="", help=DEFAULT_TARGET_REPO_HELP)
        flutter_item.add_argument("--targets", default="", help="Comma-separated Flutter targets: android,ios,web,windows,macos,linux")
        flutter_item.add_argument("--mode", choices=flutter_multiplatform.BUILD_MODES, default="debug")
        flutter_item.add_argument("--force", action="store_true", help="Refresh copied boilerplate during init.")
        flutter_item.add_argument("--execute", action="store_true", help="Run verification/build commands and capture evidence.")
        flutter_item.add_argument("--human-check", choices=["approved"], default="", help="Required for release execution.")
        flutter_item.add_argument("--timeout-seconds", type=int, default=600)
        flutter_item.add_argument("--json", action="store_true")
    flutter_finalize = flutter_sub.add_parser("finalize", help="Judge Flutter verification/build evidence completion.")
    flutter_finalize.add_argument("--work-id", required=True)
    flutter_finalize.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    flutter_finalize.add_argument("--target-repo", default="", help=DEFAULT_TARGET_REPO_HELP)
    flutter_finalize.add_argument("--json", action="store_true")

    mcp_group_cmd = sub.add_parser("mcp-group", help="Prepare MCP server group implementation templates and boundary checks.")
    mcp_group_sub = mcp_group_cmd.add_subparsers(dest="mcp_group_command")
    for name in ["analyze", "init", "run-workflow"]:
        mcp_group_item = mcp_group_sub.add_parser(name)
        mcp_group_item.add_argument("--work-id", required=True)
        mcp_group_item.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
        mcp_group_item.add_argument(
            "--components",
            default="",
            help="Comma-separated components: local-model-mcp-server,mcp-client,local-ai-agent-runtime,discord-gateway",
        )
        mcp_group_item.add_argument("--force", action="store_true", help="Refresh copied template directories during init.")
        mcp_group_item.add_argument("--json", action="store_true")

    github_knowledge_cmd = sub.add_parser("github-knowledge", help="Plan and apply approved GitHub knowledge sync actions.")
    github_knowledge_sub = github_knowledge_cmd.add_subparsers(dest="github_knowledge_command")
    github_init = github_knowledge_sub.add_parser("init", help="Initialize GitHub knowledge maintenance context.")
    github_init.add_argument("--repository", required=True)
    github_init.add_argument("--target-branch", default="")
    github_init.add_argument("--scan-mode", nargs="+", choices=github_knowledge_maintenance.SCAN_MODES, default=["recent"])
    github_init.add_argument("--repair-mode", choices=github_knowledge_maintenance.REPAIR_MODES, default="proposal")
    github_init.add_argument("--rag-output", action="store_true")
    github_init.add_argument("--work-id", default=None)
    github_init.add_argument("--reuse-existing", action="store_true")
    github_init.add_argument("--intent-summary", default="")
    github_init.add_argument("--json", action="store_true")
    github_analysis = github_knowledge_sub.add_parser("analysis-template", help="Create analysis JSON scaffold.")
    github_analysis.add_argument("--work-id", required=True)
    github_analysis.add_argument("--analysis-path", default="")
    github_analysis.add_argument("--json", action="store_true")
    github_integrity = github_knowledge_sub.add_parser(
        "artifact-integrity",
        help="Verify analysis JSON and generated reports using strict UTF-8/file-content checks.",
    )
    github_integrity.add_argument("--work-id", required=True)
    github_integrity.add_argument("--analysis-path", default="")
    github_integrity.add_argument("--output", default="")
    github_integrity.add_argument("--fail-on-finding", action="store_true")
    github_integrity.add_argument("--json", action="store_true")
    github_status = github_knowledge_sub.add_parser("status", help="Summarize current GitHub knowledge workflow state.")
    github_status.add_argument("--work-id", required=True)
    github_status.add_argument("--analysis-path", default="")
    github_status.add_argument("--json", action="store_true")
    github_next = github_knowledge_sub.add_parser("next-action", help="Show the next safe resume action.")
    github_next.add_argument("--work-id", required=True)
    github_next.add_argument("--analysis-path", default="")
    github_next.add_argument("--json", action="store_true")
    github_resume = github_knowledge_sub.add_parser("resume", help="Alias for next-action; does not mutate by default.")
    github_resume.add_argument("--work-id", required=True)
    github_resume.add_argument("--analysis-path", default="")
    github_resume.add_argument("--json", action="store_true")
    github_verify_remote = github_knowledge_sub.add_parser(
        "verify-remote",
        help="Verify package expected_remote_sha against the current remote branch.",
    )
    github_verify_remote.add_argument("--work-id", required=True)
    github_verify_remote.add_argument("--analysis-path", default="")
    github_verify_remote.add_argument("--package-path", default="")
    github_verify_remote.add_argument("--target-branch", default="")
    github_verify_remote.add_argument("--remote", default="")
    github_verify_remote.add_argument("--expected-remote-sha", default="")
    github_verify_remote.add_argument("--json", action="store_true")
    github_cleanup_worktree = github_knowledge_sub.add_parser(
        "cleanup-worktree",
        help="Inspect or remove a GitHub knowledge replay worktree.",
    )
    github_cleanup_worktree.add_argument("--work-id", required=True)
    github_cleanup_worktree.add_argument("--analysis-path", default="")
    github_cleanup_worktree.add_argument("--target-branch", default="")
    github_cleanup_worktree.add_argument("--force", action="store_true", help="Actually remove the replay worktree.")
    github_cleanup_worktree.add_argument("--prune", action="store_true", help="Run git worktree prune after cleanup.")
    github_cleanup_worktree.add_argument("--json", action="store_true")
    github_repair_plan = github_knowledge_sub.add_parser("repair-plan", help="Create a human review repair plan.")
    github_repair_plan.add_argument("--work-id", required=True)
    github_repair_plan.add_argument("--analysis-path", default="")
    github_repair_plan.add_argument("--output", default="")
    github_repair_plan.add_argument("--json", action="store_true")
    github_detect_rebase = github_knowledge_sub.add_parser(
        "detect-rebase",
        help="Detect small commit-history leakage candidates.",
    )
    github_detect_rebase.add_argument("--work-id", required=True)
    github_detect_rebase.add_argument("--analysis-path", default="")
    github_detect_rebase.add_argument("--git-repo", default="")
    github_detect_rebase.add_argument("--base", default="HEAD~30")
    github_detect_rebase.add_argument("--head", default="HEAD")
    github_detect_rebase.add_argument("--max-commits", type=int, default=80)
    github_detect_rebase.add_argument("--max-files", type=int, default=3)
    github_detect_rebase.add_argument("--all-history", action="store_true")
    github_detect_rebase.add_argument("--append", action="store_true")
    github_detect_rebase.add_argument("--json", action="store_true")
    github_rebase_plan = github_knowledge_sub.add_parser("rebase-plan", help="Create a high-risk rebase review plan.")
    github_rebase_plan.add_argument("--work-id", required=True)
    github_rebase_plan.add_argument("--analysis-path", default="")
    github_rebase_plan.add_argument("--output", default="")
    github_rebase_plan.add_argument("--json", action="store_true")
    github_rebase_review = github_knowledge_sub.add_parser(
        "rebase-review-intake",
        help="Ingest a Human Review OK/NG checklist into analysis JSON.",
    )
    github_rebase_review.add_argument("--work-id", required=True)
    github_rebase_review.add_argument("--analysis-path", default="")
    github_rebase_review.add_argument("--plan-path", default="")
    github_rebase_review.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    github_rebase_review.add_argument(
        "--ok-repair-goal",
        choices=[
            "auto",
            "absorb-into-existing-commit",
            "drop-empty-or-noise-commit",
            "split-into-independent-commit",
            "keep-with-evidence",
            "no-rewrite",
        ],
        default="auto",
    )
    github_rebase_review.add_argument("--allow-partial", action="store_true")
    github_rebase_review.add_argument("--json", action="store_true")
    github_message_plan = github_knowledge_sub.add_parser(
        "message-repair-plan",
        help="Create a high-risk commit message repair review plan after rebase verification.",
    )
    github_message_plan.add_argument("--work-id", required=True)
    github_message_plan.add_argument("--analysis-path", default="")
    github_message_plan.add_argument("--git-repo", default="")
    github_message_plan.add_argument("--source-ref", default="")
    github_message_plan.add_argument("--max-commits", type=int, default=200)
    github_message_plan.add_argument("--output", default="")
    github_message_plan.add_argument("--json", action="store_true")
    github_message_review = github_knowledge_sub.add_parser(
        "message-review-intake",
        help="Ingest a commit message repair OK/NG checklist into analysis JSON.",
    )
    github_message_review.add_argument("--work-id", required=True)
    github_message_review.add_argument("--analysis-path", default="")
    github_message_review.add_argument("--plan-path", default="")
    github_message_review.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    github_message_review.add_argument("--allow-partial", action="store_true")
    github_message_review.add_argument("--json", action="store_true")
    github_sync_plan = github_knowledge_sub.add_parser("sync-plan", help="Create an approval-gated GitHub sync plan.")
    github_sync_plan.add_argument("--work-id", required=True)
    github_sync_plan.add_argument("--analysis-path", default="")
    github_sync_plan.add_argument("--output", default="")
    github_sync_plan.add_argument("--json", action="store_true")
    github_sync_review = github_knowledge_sub.add_parser(
        "sync-review-plan",
        help="Create an OK/NG review checklist for GitHub Issue/PR/comment repair actions.",
    )
    github_sync_review.add_argument("--work-id", required=True)
    github_sync_review.add_argument("--analysis-path", default="")
    github_sync_review.add_argument("--output", default="")
    github_sync_review.add_argument("--json", action="store_true")
    github_sync_review_intake = github_knowledge_sub.add_parser(
        "sync-review-intake",
        help="Ingest a GitHub sync OK/NG checklist into analysis JSON.",
    )
    github_sync_review_intake.add_argument("--work-id", required=True)
    github_sync_review_intake.add_argument("--analysis-path", default="")
    github_sync_review_intake.add_argument("--plan-path", default="")
    github_sync_review_intake.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    github_sync_review_intake.add_argument("--allow-partial", action="store_true")
    github_sync_review_intake.add_argument("--json", action="store_true")
    github_sync_apply = github_knowledge_sub.add_parser("sync-apply", help="Execute one approved GitHub sync action.")
    github_sync_apply.add_argument("--work-id", required=True)
    github_sync_apply.add_argument("--action-id", required=True)
    github_sync_apply.add_argument("--analysis-path", default="")
    github_sync_apply.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    github_sync_apply.add_argument("--dry-run", action="store_true")
    github_sync_apply.add_argument("--json", action="store_true")
    github_rebase_package = github_knowledge_sub.add_parser(
        "rebase-package",
        help="Generate an approved small-commit rebase replay package.",
    )
    github_rebase_package.add_argument("--work-id", required=True)
    github_rebase_package.add_argument("--candidate-id", action="append", default=[])
    github_rebase_package.add_argument("--analysis-path", default="")
    github_rebase_package.add_argument("--output", default="")
    github_rebase_package.add_argument("--target-branch", default="")
    github_rebase_package.add_argument("--source-ref", default="")
    github_rebase_package.add_argument("--remote", default="origin")
    github_rebase_package.add_argument("--expected-remote-sha", default="")
    github_rebase_package.add_argument("--allow-push", action="store_true")
    github_rebase_package.add_argument("--push-allowed", dest="allow_push", action="store_true")
    github_rebase_package.add_argument("--apply-mode", choices=["direct", "git-3way", "auto-3way"], default="direct")
    github_rebase_package.add_argument("--json", action="store_true")
    github_message_package = github_knowledge_sub.add_parser(
        "message-repair-package",
        help="Generate an approved commit message repair replay package.",
    )
    github_message_package.add_argument("--work-id", required=True)
    github_message_package.add_argument("--candidate-id", action="append", default=[])
    github_message_package.add_argument("--analysis-path", default="")
    github_message_package.add_argument("--output", default="")
    github_message_package.add_argument("--target-branch", default="")
    github_message_package.add_argument("--source-ref", default="")
    github_message_package.add_argument("--remote", default="origin")
    github_message_package.add_argument("--expected-remote-sha", default="")
    github_message_package.add_argument("--allow-push", action="store_true")
    github_message_package.add_argument("--push-allowed", dest="allow_push", action="store_true")
    github_message_package.add_argument("--apply-mode", choices=["direct", "git-3way", "auto-3way"], default="auto-3way")
    github_message_package.add_argument("--json", action="store_true")
    github_rebase_apply = github_knowledge_sub.add_parser(
        "rebase-apply",
        help="Execute an approved generated rebase replay package.",
    )
    github_rebase_apply.add_argument("--work-id", required=True)
    github_rebase_apply.add_argument("--package-path", default="")
    github_rebase_apply.add_argument("--analysis-path", default="")
    github_rebase_apply.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    github_rebase_apply.add_argument("--remote", default="")
    github_rebase_apply.add_argument("--apply-mode", choices=["direct", "git-3way", "auto-3way"], default="")
    github_rebase_apply.add_argument("--push", action="store_true")
    github_rebase_apply.add_argument("--reuse-worktree", action="store_true")
    github_rebase_apply.add_argument("--dry-run", action="store_true")
    github_rebase_apply.add_argument("--json", action="store_true")
    github_publish_verified = github_knowledge_sub.add_parser(
        "publish-verified-replay",
        help="Push an already verified replay tip without regenerating the package.",
    )
    github_publish_verified.add_argument("--work-id", required=True)
    github_publish_verified.add_argument("--analysis-path", default="")
    github_publish_verified.add_argument("--target-branch", default="")
    github_publish_verified.add_argument("--remote", default="origin")
    github_publish_verified.add_argument("--expected-remote-sha", required=True)
    github_publish_verified.add_argument("--new-tip", default="")
    github_publish_verified.add_argument("--execution-index", type=int, default=-1)
    github_publish_verified.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    github_publish_verified.add_argument("--dry-run", action="store_true")
    github_publish_verified.add_argument("--json", action="store_true")
    github_rag_candidate = github_knowledge_sub.add_parser("rag-candidate", help="Create or publish a RAG candidate note.")
    github_rag_candidate.add_argument("--work-id", required=True)
    github_rag_candidate.add_argument("--analysis-path", default="")
    github_rag_candidate.add_argument("--output", default="")
    github_rag_candidate.add_argument("--topic", default="")
    github_rag_candidate.add_argument("--publish-rag", action="store_true")
    github_rag_candidate.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    github_rag_candidate.add_argument("--json", action="store_true")

    work_cmd = sub.add_parser("work", help="Check and cleanup completed temporary work directories.")
    work_sub = work_cmd.add_subparsers(dest="work_command")
    work_check = work_sub.add_parser("cleanup-check", help="Check whether a work directory can be removed.")
    work_check.add_argument("--work-id", required=True)
    work_check.add_argument("--recursive", action="store_true")
    work_check.add_argument("--required-artifact", action="append", default=[])
    work_check.add_argument("--json", action="store_true")
    work_apply = work_sub.add_parser("cleanup-apply", help="Remove a cleanup-ready work directory after Human Check.")
    work_apply.add_argument("--work-id", required=True)
    work_apply.add_argument("--recursive", action="store_true")
    work_apply.add_argument("--required-artifact", action="append", default=[])
    work_apply.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    work_apply.add_argument("--json", action="store_true")

    self_improvement_cmd = sub.add_parser("self-improvement", help="Manage Ariadne workflow feedback and Human Check review artifacts.")
    self_improvement_sub = self_improvement_cmd.add_subparsers(dest="self_improvement_command")
    self_improvement_init = self_improvement_sub.add_parser("init-feedback", help="Create work/feedback README.")
    self_improvement_init.add_argument("--json", action="store_true")
    self_improvement_create = self_improvement_sub.add_parser("create-feedback", help="Create a workflow feedback report.")
    self_improvement_create.add_argument("--target-workflow", required=True)
    self_improvement_create.add_argument("--reporter", default="Human")
    self_improvement_create.add_argument("--situation", required=True)
    self_improvement_create.add_argument("--friction", required=True)
    self_improvement_create.add_argument("--impact", default="")
    self_improvement_create.add_argument("--proposed-improvement", default="")
    self_improvement_create.add_argument("--evidence", action="append", default=[])
    self_improvement_create.add_argument("--priority", default="Medium", choices=["Low", "Medium", "High"])
    self_improvement_create.add_argument("--category", default="Workflow")
    self_improvement_create.add_argument("--runtime-trace-id", default="")
    self_improvement_create.add_argument("--runtime-log", default="")
    self_improvement_create.add_argument("--output", default="")
    self_improvement_create.add_argument("--json", action="store_true")
    self_improvement_review = self_improvement_sub.add_parser("review-feedback", help="Append human review result.")
    self_improvement_review.add_argument("--feedback", required=True)
    self_improvement_review.add_argument("--decision", required=True, choices=sorted(self_improvement.VALID_DECISIONS))
    self_improvement_review.add_argument("--reviewer", required=True)
    self_improvement_review.add_argument("--reason", required=True)
    self_improvement_review.add_argument("--next-action", default="")
    self_improvement_review.add_argument("--json", action="store_true")
    self_improvement_issue = self_improvement_sub.add_parser("issue-body", help="Create an Issue body from accepted feedback.")
    self_improvement_issue.add_argument("--feedback", required=True)
    self_improvement_issue.add_argument("--output", default="")
    self_improvement_issue.add_argument("--allow-unaccepted", action="store_true")
    self_improvement_issue.add_argument("--json", action="store_true")
    self_improvement_branch = self_improvement_sub.add_parser("branch-name", help="Generate a standard issue branch name.")
    self_improvement_branch.add_argument("--issue-number", required=True)
    self_improvement_branch.add_argument("--json", action="store_true")
    self_improvement_evidence = self_improvement_sub.add_parser("evidence-scaffold", help="Create self-improvement evidence directories.")
    self_improvement_evidence.add_argument("--work-id", required=True)
    self_improvement_evidence.add_argument("--json", action="store_true")

    review_cmd = sub.add_parser("review", help="Run Ariadne Review Council packet, finding, issue, and verdict checks.")
    review_sub = review_cmd.add_subparsers(dest="review_command")
    review_plan = review_sub.add_parser("plan", help="Plan required specialist reviewers before opening a session.")
    _add_review_packet_arguments(review_plan)

    review_start = review_sub.add_parser("start", help="Freeze a Review Packet and open a Review Council session.")
    _add_review_packet_arguments(review_start)

    review_handoff = review_sub.add_parser("handoff", help="Write per-reviewer Review Council handoff packets.")
    _add_review_lookup_arguments(review_handoff)
    review_handoff.add_argument("--reviewer", action="append", default=[])
    review_handoff.add_argument("--json", action="store_true")

    review_orchestrate = review_sub.add_parser("orchestrate", help="Evaluate LangGraph Review Council orchestration state.")
    _add_review_lookup_arguments(review_orchestrate)
    review_orchestrate.add_argument("--run-id", default="")
    review_orchestrate.add_argument("--json", action="store_true")

    review_next = review_sub.add_parser("next-action", help="Show the next operational Review Council action.")
    _add_review_lookup_arguments(review_next)
    review_next.add_argument("--json", action="store_true")

    review_summary = review_sub.add_parser("summary", help="Export a Review Council summary snapshot.")
    _add_review_lookup_arguments(review_summary)
    review_summary.add_argument("--summary-id", default="")
    review_summary.add_argument("--json", action="store_true")

    review_human_gate = review_sub.add_parser("human-gate", help="Check and record a Review Council Human Gate.")
    _add_review_lookup_arguments(review_human_gate)
    review_human_gate.add_argument("--gate", default="review-council-final-verdict")
    review_human_gate.add_argument("--human-check", default="pending")
    review_human_gate.add_argument("--reviewer", default="Human")
    review_human_gate.add_argument("--reason", default="")
    review_human_gate.add_argument("--json", action="store_true")

    review_specialist = review_sub.add_parser("run-specialist", help="Prepare a specialist reviewer execution packet.")
    _add_review_lookup_arguments(review_specialist)
    review_specialist.add_argument("--reviewer", required=True)
    review_specialist.add_argument("--json", action="store_true")

    review_execute_specialist = review_sub.add_parser(
        "execute-specialist",
        help="Execute an approved local specialist agent command and capture review evidence.",
    )
    _add_review_lookup_arguments(review_execute_specialist)
    review_execute_specialist.add_argument("--reviewer", required=True)
    review_execute_specialist.add_argument("--agent-command", default="")
    review_execute_specialist.add_argument("--timeout-seconds", type=int, default=1800)
    review_execute_specialist.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    review_execute_specialist.add_argument("--skip-draft-findings", action="store_true")
    review_execute_specialist.add_argument("--json", action="store_true")

    review_draft = review_sub.add_parser("draft-findings", help="Extract draft findings from a specialist review report.")
    _add_review_lookup_arguments(review_draft)
    review_draft.add_argument("--reviewer", required=True)
    review_draft.add_argument("--report", required=True)
    review_draft.add_argument("--category", default="other")
    review_draft.add_argument("--severity", default="medium", choices=["critical", "high", "medium", "low", "info"])
    review_draft.add_argument(
        "--verdict",
        default="needs-qa",
        choices=["pass", "warn", "fail", "unsupported", "needs-qa", "changes-required"],
    )
    review_draft.add_argument("--json", action="store_true")

    review_capture = review_sub.add_parser("capture-knowledge", help="Capture Review Council artifacts for Knowledge/RAG reuse.")
    _add_review_lookup_arguments(review_capture)
    review_capture.add_argument("--json", action="store_true")

    review_rag_build = review_sub.add_parser("rag-build", help="Export Review Council knowledge and optionally run RAG build.")
    _add_review_lookup_arguments(review_rag_build)
    review_rag_build.add_argument("--refresh-capture", action="store_true")
    review_rag_build.add_argument("--run", action="store_true")
    review_rag_build.add_argument("--output", default="")
    review_rag_build.add_argument("--normalized-dir", default="")
    review_rag_build.add_argument("--chunks-dir", default="")
    review_rag_build.add_argument("--optimized-chunks-dir", default="")
    review_rag_build.add_argument("--indexes-dir", default="")
    review_rag_build.add_argument("--embeddings-output", default="")
    review_rag_build.add_argument("--ingestion-evidence-dir", default="")
    review_rag_build.add_argument("--ingestion-policy", default="")
    review_rag_build.add_argument("--skip-optimization", action="store_true")
    review_rag_build.add_argument("--duckdb-migrate", action="store_true")
    review_rag_build.add_argument("--duckdb-path", default="")
    review_rag_build.add_argument("--duckdb-source-dir", default="")
    review_rag_build.add_argument("--duckdb-error-log", default="")
    review_rag_build.add_argument("--duckdb-evidence-output", default="")
    review_rag_build.add_argument("--duckdb-policy", default="")
    review_rag_build.add_argument("--project", default="")
    review_rag_build.add_argument("--repository", default="")
    review_rag_build.add_argument("--branch", default="")
    review_rag_build.add_argument("--commit", default="")
    review_rag_build.add_argument("--status", default="")
    review_rag_build.add_argument("--chunk-size", type=int, default=1800)
    review_rag_build.add_argument("--chunk-overlap", type=int, default=180)
    review_rag_build.add_argument("--embedding-dimensions", type=int, default=768)
    review_rag_build.add_argument("--clean-output", action="store_true")
    review_rag_build.add_argument("--json", action="store_true")

    review_finding = review_sub.add_parser("add-finding", help="Register one structured specialist review finding.")
    _add_review_lookup_arguments(review_finding)
    review_finding.add_argument("--finding-id", default="")
    review_finding.add_argument("--reviewer", required=True)
    review_finding.add_argument("--category", default="other")
    review_finding.add_argument("--severity", required=True, choices=["critical", "high", "medium", "low", "info"])
    review_finding.add_argument("--claim", required=True)
    review_finding.add_argument(
        "--verdict",
        required=True,
        choices=["pass", "warn", "fail", "unsupported", "needs-qa", "changes-required"],
    )
    review_finding.add_argument("--evidence-ref", action="append", default=[])
    review_finding.add_argument("--counterexample", default="")
    review_finding.add_argument("--reasoning-summary", default="")
    review_finding.add_argument("--requested-action", default="")
    review_finding.add_argument("--confidence", type=float, default=0.8)
    review_finding.add_argument("--required-test", action="append", default=[])
    review_finding.add_argument("--blocking", action="store_true")
    review_finding.add_argument("--non-blocking", action="store_true")
    review_finding.add_argument("--json", action="store_true")

    review_challenge = review_sub.add_parser("challenge", help="Record a Review Council challenge round.")
    _add_review_lookup_arguments(review_challenge)
    review_challenge.add_argument("--challenge-id", default="")
    review_challenge.add_argument("--challenger", required=True)
    review_challenge.add_argument("--mode", default="counterexample-check")
    review_challenge.add_argument("--issue-id", action="append", default=[])
    review_challenge.add_argument("--counterexample-found", action="store_true")
    review_challenge.add_argument("--summary", required=True)
    review_challenge.add_argument("--evidence-ref", action="append", default=[])
    review_challenge.add_argument("--json", action="store_true")

    review_evidence = review_sub.add_parser("evidence-gate", help="Verify Review Council evidence and required test references.")
    _add_review_lookup_arguments(review_evidence)
    review_evidence.add_argument("--evidence", action="append", default=[])
    review_evidence.add_argument("--required-test", action="append", default=[])
    review_evidence.add_argument("--test-spec", action="append", default=[])
    review_evidence.add_argument("--json", action="store_true")

    review_reinspect = review_sub.add_parser("reinspect", help="Update finding status after fixes, evidence, or risk acceptance.")
    _add_review_lookup_arguments(review_reinspect)
    review_reinspect.add_argument("--finding-id", action="append", default=[])
    review_reinspect.add_argument("--status", required=True, choices=["open", "accepted-risk", "fixed", "verified", "closed"])
    review_reinspect.add_argument("--reviewer", required=True)
    review_reinspect.add_argument("--summary", required=True)
    review_reinspect.add_argument("--evidence-ref", action="append", default=[])
    review_reinspect.add_argument("--json", action="store_true")

    for review_name in ["status", "issues", "inspect"]:
        review_item = review_sub.add_parser(review_name)
        _add_review_lookup_arguments(review_item)
        review_item.add_argument("--json", action="store_true")

    review_verdict = review_sub.add_parser("verdict", help="Evaluate Review Council verdict policy.")
    _add_review_lookup_arguments(review_verdict)
    review_verdict.add_argument("--evidence-verified", action="store_true")
    review_verdict.add_argument("--challenge-completed", action="store_true")
    review_verdict.add_argument("--target-revision-consistent", action="store_true")
    review_verdict.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    review_verdict.add_argument("--json", action="store_true")

    close_archive_cmd = sub.add_parser("close-archive", help="Prepare, audit, and prune report-only close archives.")
    close_archive_sub = close_archive_cmd.add_subparsers(dest="close_archive_command")
    for close_command in ("audit", "prepare", "prune"):
        close_item = close_archive_sub.add_parser(close_command)
        close_item.add_argument("--issue", default="")
        close_item.add_argument("--work-id", default="")
        close_item.add_argument("--category", choices=close_archive.CATEGORY_CHOICES, default="auto")
        close_item.add_argument("--archive-id", default="")
        close_item.add_argument("--source-work-dir", default="")
        close_item.add_argument("--archive-dir", default="")
        if close_command == "prepare":
            close_item.add_argument("--source-rag", action="append", default=[])
            close_item.add_argument("--no-auto-rag", action="store_true")
            close_item.add_argument("--require-rag", action="store_true")
        if close_command == "prune":
            close_item.add_argument("--execute", action="store_true")
            close_item.add_argument("--human-check", choices=["approved", "pending"], default="pending")
        close_item.add_argument("--json", action="store_true")

    iac_cmd = sub.add_parser("iac", help="Prepare and inspect infrastructure boilerplate templates.")
    iac_sub = iac_cmd.add_subparsers(dest="iac_command")
    iac_template_cmd = iac_sub.add_parser("template", help="List, copy, or health-check IaC templates.")
    iac_template_sub = iac_template_cmd.add_subparsers(dest="iac_template_command", required=True)
    iac_template_list = iac_template_sub.add_parser("list", help="List available IaC templates.")
    iac_template_list.add_argument("--json", action="store_true")
    iac_template_prepare = iac_template_sub.add_parser("prepare", help=f"Copy an IaC template to {work_path_pattern()}.")
    iac_template_prepare.add_argument("--template", default="opentelemetry-collector")
    iac_template_prepare.add_argument("--work-id", required=True)
    iac_template_prepare.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    iac_template_prepare.add_argument("--force", action="store_true", help="Refresh an existing copied template directory.")
    iac_template_prepare.add_argument("--json", action="store_true")
    iac_template_health = iac_template_sub.add_parser("health", help="Check a copied IaC template without starting services.")
    iac_template_health.add_argument("--template", default="opentelemetry-collector")
    iac_template_health.add_argument("--work-id", required=True)
    iac_template_health.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    iac_template_health.add_argument("--probe-tools", action="store_true", help="Run non-mutating tool version checks.")
    iac_template_health.add_argument("--json", action="store_true")

    integration_cmd = sub.add_parser("integration", help="Analyze or verify system integration quality.")
    integration_sub = integration_cmd.add_subparsers(dest="integration_command")
    integration_analyze = integration_sub.add_parser("analyze", help="Analyze system integration points and emulator candidates.")
    integration_analyze.add_argument("--work-id", required=True)
    integration_analyze.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    integration_analyze.add_argument("--target-repo", default="", help=DEFAULT_TARGET_REPO_HELP)
    integration_analyze.add_argument("--with-emulator", action="store_true", help="Include emulator suitability classification.")
    integration_analyze.add_argument("--json", action="store_true")
    integration_verify = integration_sub.add_parser("verify", help="Verify system integration evidence and emulator suitability.")
    integration_verify.add_argument("--work-id", required=True)
    integration_verify.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    integration_verify.add_argument("--target-repo", default="", help=DEFAULT_TARGET_REPO_HELP)
    integration_verify.add_argument("--with-emulator", action="store_true", help="Include emulator suitability classification.")
    integration_verify.add_argument("--json", action="store_true")
    integration_test_plan = integration_sub.add_parser("test-plan", help="Create Integration Test runbook and Context First plan.")
    integration_test_plan.add_argument("--work-id", required=True)
    integration_test_plan.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    integration_test_plan.add_argument("--target-repo", default="", help=DEFAULT_TARGET_REPO_HELP)
    integration_test_plan.add_argument("--json", action="store_true")
    integration_finalize = integration_sub.add_parser("finalize", help="Collect evidence, detect discomfort, and create final integration report.")
    integration_finalize.add_argument("--work-id", required=True)
    integration_finalize.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    integration_finalize.add_argument("--target-repo", default="", help=DEFAULT_TARGET_REPO_HELP)
    integration_finalize.add_argument("--json", action="store_true")
    integration_emulator = integration_sub.add_parser("emulator", help="Prepare or inspect emulator work-area templates.")
    integration_emulator_sub = integration_emulator.add_subparsers(dest="emulator_command", required=True)
    integration_emulator_prepare = integration_emulator_sub.add_parser("prepare", help=f"Copy emulator templates to {work_path_pattern('test-environment', 'emulator')}.")
    integration_emulator_prepare.add_argument("--work-id", required=True)
    integration_emulator_prepare.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    integration_emulator_prepare.add_argument("--target-repo", default="", help=DEFAULT_TARGET_REPO_HELP)
    integration_emulator_prepare.add_argument("--force", action="store_true", help="Refresh existing copied emulator template directories.")
    integration_emulator_prepare.add_argument("--json", action="store_true")
    integration_emulator_health = integration_emulator_sub.add_parser("health", help="Check copied emulator templates and write health evidence.")
    integration_emulator_health.add_argument("--work-id", required=True)
    integration_emulator_health.add_argument("--work-dir", default="", help=DEFAULT_WORK_DIR_HELP)
    integration_emulator_health.add_argument("--probe-docker", action="store_true", help="Run non-mutating docker version checks.")
    integration_emulator_health.add_argument("--json", action="store_true")

    doctor_cmd = sub.add_parser("doctor", help="Run workflow repository health checks.")
    doctor_cmd.add_argument("--json", action="store_true", help="Print doctor result as JSON.")
    doctor_cmd.add_argument("--fail-on-warning", action="store_true", help="Return non-zero when warnings are found.")
    doctor_cmd.add_argument("--skip-ut-spec-sync", action="store_true", help="Skip pytest UT specification sync check.")
    doctor_cmd.add_argument("--repair-encoding", action="store_true", help="Repair safe text-boundary findings before returning doctor status.")
    doctor_cmd.add_argument("--encoding-paths", nargs="+", default=None, help="Text-boundary paths to scan or repair.")
    doctor_cmd.add_argument("--encoding-extensions", nargs="+", default=None, help="Text extensions included in text-boundary scan or repair.")
    return parser


