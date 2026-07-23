from __future__ import annotations

import argparse
from typing import Any

from runtime.constants.paths import GENERATED_JSONIZED
from runtime.constants.workspace import (
    DEFAULT_TARGET_REPO_HELP,
    DEFAULT_WORK_DIR_HELP,
    process_report_path_pattern,
    work_path_pattern,
)
from runtime.environment import preflight
from runtime.rag import duckdb_store
from runtime.tools import text_encoding_convert
from runtime.tools import text_encoding_guard
from runtime.tools import utf8_bom
from runtime.workflow import close_archive
from runtime.workflow import context_first
from runtime.workflow import dispatcher_context
from runtime.workflow import flutter_multiplatform
from runtime.workflow import github_knowledge_maintenance
from runtime.workflow import validate_output_language
from runtime.workflow import validate_vscode_workspace
from runtime.workflow import self_improvement


def _add_preflight_arguments(sub: Any) -> None:
    preflight_cmd = sub.add_parser("preflight", help="Run environment tool/package preflight through the official runtime entrypoint.")
    preflight_cmd.add_argument(
        "--profile",
        choices=[
            "corrective-action-fix",
            "web-nextjs",
            "docker-compose",
            "localty-system",
            "gui-mode",
            "runtime-dev",
            "vscode-environment",
            "flutter",
            "github-cli",
            "github-knowledge-maintenance",
        ],
        default="corrective-action-fix",
    )
    preflight_cmd.add_argument("--work-id", default="")
    preflight_cmd.add_argument("--source-dir", default="")
    preflight_cmd.add_argument("--protocol-dir", default="")
    preflight_cmd.add_argument("--support-branch", default="develop")
    preflight_cmd.add_argument("--msys2-root", default=str(preflight.WINDOWS_DEFAULT_MSYS2_ROOT))
    preflight_cmd.add_argument("--repo-root", dest="preflight_repo_root", default="")
    preflight_cmd.add_argument("--install", action="store_true")
    preflight_cmd.add_argument("--gh-login-from-env", action="store_true")
    preflight_cmd.add_argument("--github-hostname", default="github.com")
    preflight_cmd.add_argument("--human-check", choices=["approved"], default=None)


def _add_tool_path_arguments(command: argparse.ArgumentParser, *, default_paths: list[str], default_extensions: list[str]) -> None:
    command.add_argument("--paths", nargs="+", default=default_paths)
    command.add_argument("--extensions", nargs="+", default=default_extensions)


def _add_tools_arguments(sub: Any) -> None:
    tools_cmd = sub.add_parser("tools", help="Run runtime maintenance tools through the official runtime entrypoint.")
    tools_sub = tools_cmd.add_subparsers(dest="tools_command")

    coverage = tools_sub.add_parser("coverage-audit", help="Audit runtime pytest placement, CLI parser shape, and coverage measurement.")
    coverage.add_argument("--output-dir", default="work/coverage-audit/process-report")
    coverage.add_argument("--skip-run", action="store_true")
    coverage.add_argument("--pytest-args", nargs=argparse.REMAINDER, default=None)

    spec_check = tools_sub.add_parser("spec-check", help="Check runtime pytest UT specification sync.")
    spec_check.add_argument("--spec", default="")
    spec_check.add_argument("--runtime-root", default="")
    spec_check.add_argument("--report", default="")
    spec_check.add_argument("--markdown", default="")
    spec_check.add_argument("--work-dir", default="")
    spec_check.add_argument("--register-context", action="store_true")
    spec_check.add_argument("--required-context", action="store_true")

    spec_fix = tools_sub.add_parser("spec-fix-inputs", help="Regenerate UT specification input sections.")
    spec_fix.add_argument("--spec", default="")
    spec_fix.add_argument("--runtime-root", default="")

    bom_scan = tools_sub.add_parser("bom-scan", help="Scan text files for UTF-8 BOM.")
    _add_tool_path_arguments(bom_scan, default_paths=["."], default_extensions=sorted(utf8_bom.TEXT_EXTENSIONS))
    bom_scan.add_argument("--fail-on-finding", action="store_true")

    bom_strip = tools_sub.add_parser("bom-strip", help="Remove UTF-8 BOM from matching text files.")
    _add_tool_path_arguments(bom_strip, default_paths=["."], default_extensions=sorted(utf8_bom.TEXT_EXTENSIONS))
    bom_strip.add_argument("--write", action="store_true")
    bom_strip.add_argument("--backup-suffix", default=".bom-bak")
    bom_strip.add_argument("--fail-on-finding", action="store_true")

    guard = tools_sub.add_parser("encoding-guard", help="Scan UTF-8 text for decode errors and irreversible loss markers.")
    _add_tool_path_arguments(guard, default_paths=["docs"], default_extensions=sorted(text_encoding_guard.TEXT_EXTENSIONS))
    guard.add_argument("--fail-on-finding", action="store_true")

    inspect = tools_sub.add_parser("encoding-inspect", help="Try candidate encodings with strict decoding.")
    _add_tool_path_arguments(inspect, default_paths=["docs"], default_extensions=sorted(text_encoding_convert.TEXT_EXTENSIONS))
    inspect.add_argument("--encodings", nargs="+", default=list(text_encoding_convert.DEFAULT_INSPECT_ENCODINGS))
    inspect.add_argument("--fail-on-warning", action="store_true")

    preview = tools_sub.add_parser("encoding-preview", help="Show hex bytes and short decode previews.")
    _add_tool_path_arguments(preview, default_paths=["docs"], default_extensions=sorted(text_encoding_convert.TEXT_EXTENSIONS))
    preview.add_argument("--encodings", nargs="+", default=list(text_encoding_convert.DEFAULT_INSPECT_ENCODINGS))
    preview.add_argument("--bytes", type=int, default=160)
    preview.add_argument("--chars", type=int, default=120)
    preview.add_argument("--fail-on-warning", action="store_true")

    convert = tools_sub.add_parser("encoding-convert", help="Safely convert text files to UTF-8.")
    _add_tool_path_arguments(convert, default_paths=["docs"], default_extensions=sorted(text_encoding_convert.TEXT_EXTENSIONS))
    convert.add_argument("--from-encoding", default="cp932")
    convert.add_argument("--to-encoding", default="utf-8")
    convert.add_argument("--write", action="store_true")
    convert.add_argument("--backup-suffix", default=".encoding-bak")
    convert.add_argument("--force", action="store_true")
    convert.add_argument("--fail-on-blocked", action="store_true")


def _add_retrieval_arguments(sub: Any) -> None:
    retrieval_cmd = sub.add_parser("retrieval", help="Run workflow task plans through the official runtime entrypoint.")
    retrieval_sub = retrieval_cmd.add_subparsers(dest="retrieval_command")

    run = retrieval_sub.add_parser("run", help="Run a task plan sequentially or in parallel and write process reports.")
    run.add_argument("--work-id", required=True)
    run.add_argument("--task-file", required=True)
    run.add_argument("--mode", default="auto", choices=["auto", "sequential", "parallel"])
    run.add_argument("--max-workers", type=int, default=4)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--stop-on-failure", action="store_true")
    run.add_argument("--json", action="store_true")


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


def _add_rag_build_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--work-id", default="")
    command.add_argument("--work-dir", default="")
    command.add_argument("--source-dir", default="work/db/ariadne-knowledge-platform/rag/corrective-action-report")
    command.add_argument("--document-type", default="corrective-action-report")
    command.add_argument("--normalized-dir", default="work/db/ariadne-knowledge-platform/rag/normalized")
    command.add_argument("--chunks-dir", default="work/db/ariadne-knowledge-platform/rag/chunks")
    command.add_argument("--optimized-chunks-dir", default="work/db/ariadne-knowledge-platform/rag/optimized-chunks")
    command.add_argument("--indexes-dir", default="work/db/ariadne-knowledge-platform/rag/indexes")
    command.add_argument("--embeddings-output", default="work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl")
    command.add_argument("--output", default="work/db/ariadne-knowledge-platform/rag/retrieval/rag-build-run-latest.json")
    command.add_argument("--ingestion-evidence-dir", default="db/rag/evidence/ingestion")
    command.add_argument("--ingestion-policy", default="runtime/rag/policies/knowledge-ingestion-policy.json")
    command.add_argument("--skip-optimization", action="store_true")
    command.add_argument("--duckdb-migrate", action="store_true")
    command.add_argument("--duckdb-path", default=str(duckdb_store.DEFAULT_DB_PATH))
    command.add_argument("--duckdb-source-dir", default="")
    command.add_argument("--duckdb-error-log", default=str(duckdb_store.DEFAULT_ERROR_LOG))
    command.add_argument("--duckdb-evidence-output", default="db/rag/evidence/migration-summary.json")
    command.add_argument("--duckdb-policy", default="")
    command.add_argument("--project", default="")
    command.add_argument("--repository", default="")
    command.add_argument("--branch", default="")
    command.add_argument("--commit", default="")
    command.add_argument("--status", default="draft")
    command.add_argument("--chunk-size", type=int, default=1800)
    command.add_argument("--chunk-overlap", type=int, default=180)
    command.add_argument("--embedding-dimensions", type=int, default=768)
    command.add_argument("--clean-output", action="store_true")
    command.add_argument("--standardize-filenames", action="store_true")
    command.add_argument("--skip-standardize", action="store_true")
    command.add_argument("--replace-references", action="store_true")
    command.add_argument("--random-length", type=int, default=8, choices=range(5, 9))
    command.add_argument("--json", action="store_true")


def _add_rag_load_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--query", action="append", default=[])
    command.add_argument("--task", default="")
    command.add_argument("--workflow", default="")
    command.add_argument("--work-id", default="")
    command.add_argument("--context-file", action="append", default=[])
    command.add_argument("--work-dir", default="")
    command.add_argument("--dispatch-plan", default="")
    command.add_argument("--repository", default="")
    command.add_argument("--branch", default="")
    command.add_argument("--project", default="")
    command.add_argument("--tag", action="append", default=[])
    command.add_argument("--source-type", default="")
    command.add_argument("--category", default="")
    command.add_argument("--trust-level", default="")
    command.add_argument("--chunks-index", default="work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl")
    command.add_argument("--embeddings-index", default="work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl")
    command.add_argument("--retrieval-backend", choices=["file", "duckdb"], default="file")
    command.add_argument("--duckdb-path", default=str(duckdb_store.DEFAULT_DB_PATH))
    command.add_argument("--semantic-hint", default="")
    command.add_argument("--document-type", default="")
    command.add_argument("--environment", default="")
    command.add_argument("--knowledge-workflow", default="")
    command.add_argument("--min-reliability", type=float, default=None)
    command.add_argument("--min-freshness", type=float, default=None)
    command.add_argument("--output-dir", default="work/db/ariadne-knowledge-platform/rag/retrieval")
    command.add_argument("--search-mode", choices=["keyword", "semantic", "hybrid"], default="hybrid")
    command.add_argument("--top-k", type=int, default=5)
    command.add_argument("--max-chars", type=int, default=4000)
    command.add_argument("--max-queries", type=int, default=5)
    command.add_argument("--jobs", type=int, default=4)
    command.add_argument("--aggregate-max-chars", type=int, default=12000)
    command.add_argument("--build-if-missing", action="store_true")
    command.add_argument("--write-markdown", action="store_true")
    command.add_argument("--python", default="python")
    command.add_argument("--json", action="store_true")


def _add_rag_retrieve_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("query")
    command.add_argument("--chunks-index", default="work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl")
    command.add_argument("--embeddings-index", default="work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl")
    command.add_argument("--output-dir", default="work/db/ariadne-knowledge-platform/rag/retrieval")
    command.add_argument("--top-k", type=int, default=5)
    command.add_argument("--max-chars", type=int, default=4000)
    command.add_argument("--search-mode", choices=["keyword", "semantic", "hybrid"], default="hybrid")
    command.add_argument("--backend", choices=["file", "duckdb"], default="file")
    command.add_argument("--duckdb-path", default=str(duckdb_store.DEFAULT_DB_PATH))
    command.add_argument("--semantic-hint", default="")
    command.add_argument("--document-type", default="")
    command.add_argument("--environment", default="")
    command.add_argument("--workflow", default="")
    command.add_argument("--min-reliability", type=float, default=None)
    command.add_argument("--min-freshness", type=float, default=None)
    command.add_argument("--project", default="")
    command.add_argument("--repository", default="")
    command.add_argument("--branch", default="")
    command.add_argument("--tag", action="append", default=[])
    command.add_argument("--source-type", default="")
    command.add_argument("--category", default="")
    command.add_argument("--trust-level", default="")
    command.add_argument("--write-markdown", action="store_true")
    command.add_argument("--json", action="store_true")


def _add_rag_stage_arguments(rag_sub: Any) -> None:
    normalize = rag_sub.add_parser("normalize", help="Normalize source RAG markdown documents.")
    normalize.add_argument("--source-dir", required=True)
    normalize.add_argument("--output-dir", required=True)
    normalize.add_argument("--document-type", default="corrective-action-report")
    normalize.add_argument("--project", default="")
    normalize.add_argument("--repository", default="")
    normalize.add_argument("--branch", default="")
    normalize.add_argument("--commit", default="")
    normalize.add_argument("--status", default="draft")
    normalize.add_argument("--clean-output", action="store_true")
    normalize.add_argument("--json", action="store_true")

    chunk = rag_sub.add_parser("chunk", help="Split normalized RAG documents into chunks.")
    chunk.add_argument("--input-dir", required=True)
    chunk.add_argument("--output-dir", required=True)
    chunk.add_argument("--chunk-size", type=int, default=1800)
    chunk.add_argument("--chunk-overlap", type=int, default=180)
    chunk.add_argument("--clean-output", action="store_true")
    chunk.add_argument("--json", action="store_true")

    index = rag_sub.add_parser("index", help="Build document and chunk JSONL indexes.")
    index.add_argument("--normalized-dir", required=True)
    index.add_argument("--chunks-dir", required=True)
    index.add_argument("--output-dir", required=True)
    index.add_argument("--json", action="store_true")

    embed = rag_sub.add_parser("embed", help="Create local sparse embeddings for chunk index rows.")
    embed.add_argument("--chunks-index", required=True)
    embed.add_argument("--output", required=True)
    embed.add_argument("--dimensions", type=int, default=768)
    embed.add_argument("--json", action="store_true")

    optimize = rag_sub.add_parser("optimize", help="Optimize chunk ingestion candidates and write evidence.")
    optimize.add_argument("--chunks-dir", default="work/db/ariadne-knowledge-platform/rag/chunks")
    optimize.add_argument("--output-dir", default="work/db/ariadne-knowledge-platform/rag/optimized-chunks")
    optimize.add_argument("--evidence-dir", default="db/rag/evidence/ingestion")
    optimize.add_argument("--policy", default="runtime/rag/policies/knowledge-ingestion-policy.json")
    optimize.add_argument("--clean-output", action="store_true")
    optimize.add_argument("--json", action="store_true")

    standardize = rag_sub.add_parser("standardize", help="Standardize corrective action report filenames.")
    standardize.add_argument("--source-dir", default="work/db/ariadne-knowledge-platform/rag/corrective-action-report")
    standardize.add_argument("--replace-references", action="store_true")
    standardize.add_argument("--random-length", type=int, default=8, choices=range(5, 9))
    standardize.add_argument("--json", action="store_true")

    jsonize = rag_sub.add_parser("jsonize", help="Convert a RAG tree into standard JSON source records.")
    jsonize.add_argument("--rag-dir", default="work/db/ariadne-knowledge-platform/rag")
    jsonize.add_argument("--output-dir", default=str(GENERATED_JSONIZED))
    jsonize.add_argument("--include-readme", action="store_true")
    jsonize.add_argument("--delete-source", action="store_true")
    jsonize.add_argument("--clean-output", action="store_true")
    jsonize.add_argument("--json", action="store_true")

    migrate = rag_sub.add_parser("migrate-retrieval", help="Migrate legacy retrieval artifacts into jsonized RAG records.")
    migrate.add_argument("--retrieval-dir", default="work/db/ariadne-knowledge-platform/rag/retrieval")
    migrate.add_argument("--jsonized-dir", default=str(GENERATED_JSONIZED))
    migrate.add_argument("--delete-source", action="store_true")
    migrate.add_argument("--delete-duplicate-markdown", action="store_true")
    migrate.add_argument("--repair-from-jsonized", action="store_true")
    migrate.add_argument("--prune-legacy-migrations", action="store_true")
    migrate.add_argument("--json", action="store_true")

    legacy = rag_sub.add_parser("migrate-legacy-root", help="Move legacy root RAG backups into the standard RAG tree.")
    legacy.add_argument("--legacy-dir", default="")
    legacy.add_argument("--target-rag-dir", default="work/db/ariadne-knowledge-platform/rag")
    legacy.add_argument("--keep-legacy-dir", action="store_true")
    legacy.add_argument("--json", action="store_true")


def _add_workflow_docs_sync_arguments(workflow_sub: Any) -> None:
    docs = workflow_sub.add_parser("docs-sync", help="Prepare documentation sync workflow artifacts.")
    docs_sub = docs.add_subparsers(dest="workflow_action")

    init = docs_sub.add_parser("init", help="Initialize docs-sync work context.")
    init.add_argument("--repository", required=True)
    init.add_argument("--target-branch", required=True)
    init.add_argument("--work-id", default=None)
    init.add_argument("--base-work-id", default="")
    init.add_argument("--reuse-existing", action="store_true")
    init.add_argument("--intent-summary", default="")
    init.add_argument("--json", action="store_true")

    analysis = docs_sub.add_parser("analysis-template", help="Create docs drift analysis JSON scaffold.")
    analysis.add_argument("--work-id", required=True)
    analysis.add_argument("--analysis-path", default="")
    analysis.add_argument("--allow-missing-scm-state", action="store_true")
    analysis.add_argument("--json", action="store_true")

    issue = docs_sub.add_parser("issue-body", help="Create a GitHub Issue body from docs drift analysis JSON.")
    issue.add_argument("--work-id", required=True)
    issue.add_argument("--analysis-path", default="")
    issue.add_argument("--output", default="")
    issue.add_argument("--json", action="store_true")


def _add_workflow_corrective_action_arguments(workflow_sub: Any) -> None:
    fix = workflow_sub.add_parser("corrective-action-fix", help="Initialize corrective action fix work context.")
    fix_sub = fix.add_subparsers(dest="workflow_action")
    init = fix_sub.add_parser("init", help="Initialize work/<id> for corrective action fix flow.")
    init.add_argument("--repository", required=True)
    init.add_argument("--target-branch", required=True)
    init.add_argument("--work-id", default=None)
    init.add_argument("--base-work-id", default="")
    init.add_argument("--reuse-existing", action="store_true")
    init.add_argument("--report-path", default="")
    init.add_argument("--intent-summary", default="")
    init.add_argument("--json", action="store_true")

    report = workflow_sub.add_parser("corrective-action-report", help="Register or show corrective action report context.")
    report_sub = report.add_subparsers(dest="workflow_action")
    register = report_sub.add_parser("register", help="Register a corrective action report artifact.")
    register.add_argument("--report-path", required=True)
    register.add_argument("--repository", default="")
    register.add_argument("--target-branch", default="")
    register.add_argument("--work-id", default="")
    register.add_argument("--work-dir", default="")
    register.add_argument("--json", action="store_true")

    show = report_sub.add_parser("show", help="Show corrective action report context.")
    show.add_argument("--target-branch", default="")
    show.add_argument("--work-id", default="")
    show.add_argument("--work-dir", default="")
    show.add_argument("--json", action="store_true")


def _add_workflow_state_arguments(workflow_sub: Any) -> None:
    state = workflow_sub.add_parser("state", help="Read or update workflow-state.json.")
    state.add_argument("--work-dir", required=True)
    state_sub = state.add_subparsers(dest="workflow_action")
    state_sub.add_parser("show", help="Show workflow-state.json.").add_argument("--json", action="store_true")
    set_state = state_sub.add_parser("set", help="Update workflow-state.json.")
    set_state.add_argument("--workflow", required=True)
    set_state.add_argument("--work-id", required=True)
    set_state.add_argument("--phase", required=True)
    set_state.add_argument("--status", required=True, choices=["blocked", "complete", "failed", "in-progress", "not-started", "review-ready"])
    set_state.add_argument("--blocking-reason", default="")
    set_state.add_argument("--next-human-action", default="")
    set_state.add_argument("--json", action="store_true")


def _add_workflow_quality_arguments(workflow_sub: Any) -> None:
    noise = workflow_sub.add_parser("noise-reduction", help="Generate Noise Reduction artifacts.")
    noise_sub = noise.add_subparsers(dest="workflow_action")
    noise_run = noise_sub.add_parser("run", help="Generate Human Interview and readiness artifacts.")
    noise_run.add_argument("--draft", required=True)
    noise_run.add_argument("--output-dir", default="")
    noise_run.add_argument("--json", action="store_true")

    output_language = workflow_sub.add_parser("validate-output-language", help="Detect English-dominant Markdown artifacts.")
    output_language_sub = output_language.add_subparsers(dest="workflow_action")
    output_check = output_language_sub.add_parser("check", help="Check output language quality.")
    output_check.add_argument("--paths", nargs="+", default=validate_output_language.DEFAULT_PATHS)
    output_check.add_argument("--exclude", nargs="*", default=validate_output_language.DEFAULT_EXCLUDES)
    output_check.add_argument("--english-ratio-threshold", type=float, default=0.62)
    output_check.add_argument("--min-english-words", type=int, default=35)
    output_check.add_argument("--min-japanese-chars", type=int, default=20)
    output_check.add_argument("--fail-on-violation", action="store_true")
    output_check.add_argument("--json", action="store_true")

    vscode_check = workflow_sub.add_parser("validate-vscode-workspace", help="Validate VSCode workspace JSON files.")
    vscode_check_sub = vscode_check.add_subparsers(dest="workflow_action")
    vscode = vscode_check_sub.add_parser("check", help="Validate VSCode JSON files.")
    vscode.add_argument("--workspace", default=".")
    vscode.add_argument("files", nargs="*", default=validate_vscode_workspace.DEFAULT_FILES)
    vscode.add_argument("--json", action="store_true")


def _add_workflow_misc_arguments(workflow_sub: Any) -> None:
    capture = workflow_sub.add_parser("knowledge-capture", help="Prepare knowledge-capture reports for a completed issue.")
    capture.add_argument("--issue", required=True)
    capture.add_argument("--repository", default="")
    capture.add_argument("--branch", default="")
    capture.add_argument("--base-work-id", default="")
    capture.add_argument("--source-dir", default=None)
    capture.add_argument("--dry-run", action="store_true")
    capture.add_argument("--allow-legacy-scm-fallback", action="store_true")
    capture.add_argument("--json", action="store_true")

    handoff = workflow_sub.add_parser("iac-handoff", help="Create realtime IaC handoff and execution-plan context.")
    handoff_sub = handoff.add_subparsers(dest="workflow_action")
    create = handoff_sub.add_parser("create", help="Create Context First handoff artifacts.")
    create.add_argument("--work-id", required=True)
    create.add_argument("--force", action="store_true")
    create.add_argument("--target-repository", default="")
    create.add_argument("--target-branch", default="")
    create.add_argument("--validator-judgment", default="unknown", choices=["pass", "conditional-pass", "fail", "unknown"])
    create.add_argument("--source-artifact", action="append", default=[])
    create.add_argument("--validation-path", default="")
    create.add_argument("--handoff-path", default="")
    create.add_argument("--json", action="store_true")

    vscode_env = workflow_sub.add_parser("vscode-environment", help="Prepare VSCode environment workflow artifacts.")
    vscode_env_sub = vscode_env.add_subparsers(dest="workflow_action")
    init = vscode_env_sub.add_parser("init", help="Create the VSCode environment workflow work area.")
    init.add_argument("--work-id", default="vscode-environment")
    init.add_argument("--target-dir", default="")
    init.add_argument("--mode", choices=["self-provision", "target-workspace", "custom-design"], default="self-provision")
    init.add_argument("--reuse-existing", action="store_true")
    init.add_argument("--json", action="store_true")
    for name in ["requirements-template", "open-questions"]:
        command = vscode_env_sub.add_parser(name)
        command.add_argument("--work-id", default="vscode-environment")
        command.add_argument("--mode", choices=["self-provision", "target-workspace", "custom-design"], default="self-provision")
        if name == "open-questions":
            command.add_argument("--draft-dir", default="work/requirements/devlop-edit-draft")
        command.add_argument("--json", action="store_true")
    validation = vscode_env_sub.add_parser("validation-template")
    validation.add_argument("--work-id", default="vscode-environment")
    validation.add_argument("--mode", choices=["self-provision", "target-workspace", "custom-design"], default="self-provision")
    validation.add_argument("--status", choices=["pass", "conditional-pass", "fail"], default="fail")
    validation.add_argument("--json", action="store_true")
    draft = vscode_env_sub.add_parser("draft-template")
    draft.add_argument("--draft-dir", default="work/requirements/devlop-edit-draft")
    draft.add_argument("--json", action="store_true")
    rag = vscode_env_sub.add_parser("rag-template")
    rag.add_argument("--work-id", default="vscode-environment")
    rag.add_argument("--source-dir", default="work/db/ariadne-knowledge-platform/rag/workspace-environment")
    rag.add_argument("--topic", default="localty-vscode-environment")
    rag.add_argument("--repository", default="localty")
    rag.add_argument("--target-workspace", default="")
    rag.add_argument("--mode", choices=["self-provision", "target-workspace", "custom-design"], default="self-provision")
    rag.add_argument("--status", default="draft")
    rag.add_argument("--json", action="store_true")


def _add_visual_work_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--issue-id", required=True, help="Issue/work ID such as SYS-0001, FEAT-0001, or FIX-0001.")
    command.add_argument("--work-dir", default=None, help="Explicit work directory. Default: work/<issue-id>.")
    command.add_argument("--svg-input-dir", default=None, help="Shared SVG inbox. Default: work/requirements/svg-input.")


def _add_gui_arguments(sub: Any) -> None:
    gui_cmd = sub.add_parser("gui", help="Run SVG-based GaC/UaC GUI mode.")
    gui_sub = gui_cmd.add_subparsers(dest="gui_command")

    init = gui_sub.add_parser("init-input", help="Create work/requirements/svg-input/ and its naming guide.")
    init.add_argument("--svg-input-dir", default=None)
    init.add_argument("--force", action="store_true")
    init.add_argument("--json", action="store_true")

    inspect = gui_sub.add_parser("inspect-input", help="Validate shared SVG inbox prefixes and XML.")
    inspect.add_argument("--svg-input-dir", default=None)
    inspect.add_argument("--json", action="store_true")

    run = gui_sub.add_parser("run", help="Generate GUI design, PyQt6, and QTest candidates when SVG exists.")
    _add_visual_work_arguments(run)
    run.add_argument(
        "--mode",
        default="auto",
        choices=[
            "auto",
            "system-development",
            "feature-development",
            "corrective-improvement",
            "generic-gui",
        ],
    )
    run.add_argument("--force", action="store_true")
    run.add_argument("--input-prefix", choices=["SYS", "FEAT", "FIX", "GUI"], default=None)
    run.add_argument("--skip-context-check", action="store_true")
    run.add_argument("--json", action="store_true")

    validate = gui_sub.add_parser("validate", help="Validate GUI mode completion and generated source policies.")
    _add_visual_work_arguments(validate)
    validate.add_argument("--json", action="store_true")

    self_test = gui_sub.add_parser("self-test", help="Run deterministic GUI mode runtime checks.")
    self_test.add_argument("--json", action="store_true")


def _add_web_svg_arguments(sub: Any) -> None:
    web_cmd = sub.add_parser("web-svg", help="Run SVG-based web layout mode.")
    web_sub = web_cmd.add_subparsers(dest="web_svg_command")

    init = web_sub.add_parser("init-input", help="Create Web SVG inbox README.")
    init.add_argument("--svg-input-dir", default=None)
    init.add_argument("--force", action="store_true")
    init.add_argument("--json", action="store_true")

    run = web_sub.add_parser("run", help="Generate web layout and browser test candidates when SVG exists.")
    _add_visual_work_arguments(run)
    run.add_argument(
        "--mode",
        default="auto",
        choices=["auto", "new-app", "existing-app-feature", "corrective-fix", "generic-web-ui"],
    )
    run.add_argument("--force", action="store_true")
    run.add_argument(
        "--input-prefix",
        choices=["WEB_SYS", "WEB_FEAT", "WEB_FIX", "WEB", "NEXT_SYS", "NEXT_FEAT", "NEXT_FIX", "NEXT"],
        default=None,
    )
    run.add_argument("--skip-context-check", action="store_true")
    run.add_argument("--json", action="store_true")

    validate = web_sub.add_parser("validate", help="Validate Web SVG layout completion and generated source policies.")
    _add_visual_work_arguments(validate)
    validate.add_argument("--json", action="store_true")


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

    intake_cmd = sub.add_parser("intake", help="Accept requirement documents and initialize workflow context.")
    intake_sub = intake_cmd.add_subparsers(dest="intake_command")
    intake_run = intake_sub.add_parser("run", help="Move or copy submitted requirement documents into work/<receipt-id>.")
    intake_run.add_argument(
        "requirements",
        nargs="*",
        help="Requirement definition document paths to intake. When omitted, work/requirements/ is used.",
    )
    intake_run.add_argument(
        "--requirements-dir",
        default=None,
        help="Directory used when requirement paths are omitted. Default: work/requirements/",
    )
    intake_run.add_argument("--receipt-id", help="Explicit receipt ID. Auto-generated when omitted.")
    intake_run.add_argument(
        "--id-prefix",
        default=None,
        help="Prefix used for generated receipt IDs. Defaults to SYS for new systems and FEAT for maintenance.",
    )
    intake_run.add_argument("--project-name", default="unknown-project")
    intake_run.add_argument("--project-repository", default="")
    intake_run.add_argument(
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
    intake_run.add_argument("--phase", default="intake")
    intake_run.add_argument("--intent-summary", default="Requirement document intake")
    intake_run.add_argument("--risk-level", default="unknown", choices=["low", "medium", "high", "critical", "unknown"])
    intake_run.add_argument("--copy", action="store_true", help="Copy requirement documents instead of moving them.")
    intake_run.add_argument("--json", action="store_true", help="Print result as JSON.")

    scm_cmd = sub.add_parser("scm", help="Prepare repositories, compare requirements, branch, commit, and push.")
    scm_sub = scm_cmd.add_subparsers(dest="scm_command")

    scm_prepare = scm_sub.add_parser("prepare", help="Prepare target repository and branch for workflow execution.")
    scm_prepare.add_argument("--work-id", required=True)
    scm_prepare.add_argument("--repository", default=None, help="GitHub URL, git URL, owner/name, or local repository path.")
    scm_prepare.add_argument("--target-branch", default=None)
    scm_prepare.add_argument("--remote", default=None)
    scm_prepare.add_argument("--requirements", nargs="*", help="Requirement files used to resolve repository settings.")
    scm_prepare.add_argument("--source-dir", default=None, help=DEFAULT_TARGET_REPO_HELP)
    scm_prepare.add_argument("--no-pull", action="store_true", help="Fetch only; do not pull after checkout.")
    scm_prepare.add_argument("--dry-run", action="store_true")
    scm_prepare.add_argument("--json", action="store_true")

    scm_support = scm_sub.add_parser("support", help="Prepare a support repository under work/<work-id>/source/.")
    scm_support.add_argument("--work-id", required=True)
    scm_support.add_argument("--name", required=True)
    scm_support.add_argument("--repository", required=True)
    scm_support.add_argument("--branch", default=None)
    scm_support.add_argument("--remote", default=None)
    scm_support.add_argument("--source-dir", default=None)
    scm_support.add_argument("--no-pull", action="store_true")
    scm_support.add_argument("--dry-run", action="store_true")
    scm_support.add_argument("--json", action="store_true")

    scm_compare = scm_sub.add_parser("compare", help="Create a comparison report between requirements and repository state.")
    scm_compare.add_argument("--work-id", required=True)
    scm_compare.add_argument("--source-dir", default=None)
    scm_compare.add_argument("--requirements", nargs="*", help="Requirement files. Defaults to requirement artifacts.")
    scm_compare.add_argument("--json", action="store_true")

    scm_branch = scm_sub.add_parser("branch", help="Create or switch to feature/issue-<number> branch.")
    scm_branch.add_argument("--work-id", required=True)
    scm_branch.add_argument("--issue-number", required=True)
    scm_branch.add_argument("--repository", default=None, help="GitHub URL, git URL, owner/name, or local repository path.")
    scm_branch.add_argument("--github-repo", default=None, help="GitHub repository in owner/name format.")
    scm_branch.add_argument("--base-branch", default=None, help="Remote base branch used to create the issue branch.")
    scm_branch.add_argument("--branch-prefix", default=None)
    scm_branch.add_argument("--remote", default=None)
    scm_branch.add_argument("--source-dir", default=None)
    scm_branch.add_argument("--local-only", action="store_true", help="Only create/switch the local branch. Does not create GitHub branch.")
    scm_branch.add_argument("--link-to-issue", action="store_true", help="Create the remote branch as a GitHub linked branch for the issue.")
    scm_branch.add_argument("--dry-run", action="store_true")
    scm_branch.add_argument("--json", action="store_true")

    scm_commit = scm_sub.add_parser("commit", help="Commit workflow changes with semantic commit validation.")
    scm_commit.add_argument("--work-id", required=True)
    scm_commit.add_argument("--message", required=True)
    scm_commit.add_argument("--source-dir", default=None)
    scm_commit.add_argument("--all", action="store_true", help="Run git add -A before commit.")
    scm_commit.add_argument("--allow-empty", action="store_true")
    scm_commit.add_argument("--dry-run", action="store_true")
    scm_commit.add_argument("--json", action="store_true")

    scm_push = scm_sub.add_parser("push", help="Push the current issue branch after human approval.")
    scm_push.add_argument("--work-id", required=True)
    scm_push.add_argument("--source-dir", default=None)
    scm_push.add_argument("--remote", default=None)
    scm_push.add_argument("--branch", default=None)
    scm_push.add_argument("--set-upstream", action="store_true")
    scm_push.add_argument("--human-check", required=True, choices=["approved"])
    scm_push.add_argument("--dry-run", action="store_true")
    scm_push.add_argument("--json", action="store_true")

    scm_bootstrap = scm_sub.add_parser("bootstrap", help="Initialize and push the first commit to a precreated GitHub repository.")
    scm_bootstrap.add_argument("--work-id", required=True)
    scm_bootstrap.add_argument("--github-repo", default=None, help="GitHub repository in owner/name format.")
    scm_bootstrap.add_argument("--initial-branch", default=None)
    scm_bootstrap.add_argument("--remote", default=None)
    scm_bootstrap.add_argument("--message", default="chore: bootstrap realtime iac repository")
    scm_bootstrap.add_argument("--source-dir", default=None)
    scm_bootstrap.add_argument("--push", action="store_true")
    scm_bootstrap.add_argument("--human-check", choices=["approved"], default=None)
    scm_bootstrap.add_argument("--dry-run", action="store_true")
    scm_bootstrap.add_argument("--json", action="store_true")

    github_cmd = sub.add_parser("github", help="Create GitHub Issue and Pull Request drafts or approved mutations.")
    github_sub = github_cmd.add_subparsers(dest="github_command")

    github_issue = github_sub.add_parser("issue", help="Create or draft a GitHub Issue for workflow changes.")
    github_issue.add_argument("--work-id", required=True)
    github_issue.add_argument("--github-repo", default=None, help="GitHub repository in owner/name format.")
    github_issue.add_argument("--title", required=True)
    github_issue.add_argument("--flow-label", choices=["iac", "improvement", "initial-development", "new-feature"], default=None)
    github_issue.add_argument("--title-prefix", default=None)
    github_issue.add_argument("--body-file", default=None)
    github_issue.add_argument("--label", action="append", default=[])
    github_issue.add_argument("--assignee", action="append", default=[])
    github_issue.add_argument("--create", action="store_true", help="Actually create the issue using GitHub REST API.")
    github_issue.add_argument("--json", action="store_true")

    github_pr = github_sub.add_parser("pr", help="Create or draft a GitHub Pull Request for an issue branch.")
    github_pr.add_argument("--work-id", required=True)
    github_pr.add_argument("--github-repo", default=None, help="GitHub repository in owner/name format.")
    github_pr.add_argument("--base", default="develop")
    github_pr.add_argument("--head", default=None)
    github_pr.add_argument("--title-file", default=None)
    github_pr.add_argument("--body-file", default=None)
    github_pr.add_argument("--create", action="store_true")
    github_pr.add_argument("--human-check", choices=["approved"], default=None)
    github_pr.add_argument("--json", action="store_true")

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

    rag_cmd = sub.add_parser("rag", help="Build, load, retrieve, and maintain file-based RAG artifacts.")
    rag_sub = rag_cmd.add_subparsers(dest="rag_command")

    rag_build_cmd = rag_sub.add_parser("build", help="Run the RAG build pipeline.")
    _add_rag_build_arguments(rag_build_cmd)

    rag_load = rag_sub.add_parser("load", help="Build a RAG dispatch plan and retrieve context packs.")
    _add_rag_load_arguments(rag_load)

    rag_retrieve = rag_sub.add_parser("retrieve", help="Retrieve one RAG context pack for a query.")
    _add_rag_retrieve_arguments(rag_retrieve)

    _add_rag_stage_arguments(rag_sub)

    workflow_cmd = sub.add_parser("workflow", help="Run workflow support helpers through the official runtime entrypoint.")
    workflow_sub = workflow_cmd.add_subparsers(dest="workflow_command")
    _add_workflow_docs_sync_arguments(workflow_sub)
    _add_workflow_corrective_action_arguments(workflow_sub)
    _add_workflow_state_arguments(workflow_sub)
    _add_workflow_quality_arguments(workflow_sub)
    _add_workflow_misc_arguments(workflow_sub)

    _add_gui_arguments(sub)
    _add_web_svg_arguments(sub)

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

    _add_preflight_arguments(sub)
    _add_tools_arguments(sub)
    _add_retrieval_arguments(sub)

    doctor_cmd = sub.add_parser("doctor", help="Run workflow repository health checks.")
    doctor_cmd.add_argument("--json", action="store_true", help="Print doctor result as JSON.")
    doctor_cmd.add_argument("--fail-on-warning", action="store_true", help="Return non-zero when warnings are found.")
    doctor_cmd.add_argument("--skip-ut-spec-sync", action="store_true", help="Skip pytest UT specification sync check.")
    doctor_cmd.add_argument("--repair-encoding", action="store_true", help="Repair safe text-boundary findings before returning doctor status.")
    doctor_cmd.add_argument("--encoding-paths", nargs="+", default=None, help="Text-boundary paths to scan or repair.")
    doctor_cmd.add_argument("--encoding-extensions", nargs="+", default=None, help="Text extensions included in text-boundary scan or repair.")
    return parser


