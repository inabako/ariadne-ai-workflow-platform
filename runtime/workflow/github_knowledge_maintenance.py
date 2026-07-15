from __future__ import annotations

import argparse
import json
import secrets
import string
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    default_github_owner,
    ensure_work_tree,
    find_repo_root,
    load_artifact_index,
    load_env,
    local_timestamp,
    normalize_repository_value,
    read_json,
    relative_to_repo,
    repository_to_github_slug,
    slugify,
    upsert_artifact,
    utc_now_iso,
    write_json,
    write_markdown_bom,
)
from runtime.workflow.context_first import (  # noqa: E402
    context_entry,
    context_path,
    load_manifest,
    manifest_path_for_work_dir,
    register_context,
)


SCAN_MODES = ["repository", "issue", "pull-request", "recent", "full"]
REPAIR_MODES = ["proposal", "apply"]
RAG_SOURCE_ID_ALPHABET = string.ascii_uppercase + string.digits


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GitHub repository knowledge maintenance workflow helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize GitHub knowledge maintenance context.")
    init_parser.add_argument("--repository", required=True, help="GitHub repository URL, slug, or repository name.")
    init_parser.add_argument("--target-branch", default="", help="Optional branch used as scan context.")
    init_parser.add_argument(
        "--scan-mode",
        nargs="+",
        choices=SCAN_MODES,
        default=["recent"],
        help="Scan modes to include in the collection plan.",
    )
    init_parser.add_argument("--repair-mode", choices=REPAIR_MODES, default="proposal")
    init_parser.add_argument("--rag-output", action="store_true", help="Prepare RAG candidate outputs.")
    init_parser.add_argument("--work-id", default=None)
    init_parser.add_argument("--reuse-existing", action="store_true")
    init_parser.add_argument("--intent-summary", default="")
    init_parser.add_argument("--repo-root", default=None)

    analysis_parser = subparsers.add_parser(
        "analysis-template", help="Create a GitHub knowledge analysis JSON scaffold."
    )
    analysis_parser.add_argument("--work-id", required=True)
    analysis_parser.add_argument("--analysis-path", default="")
    analysis_parser.add_argument("--repo-root", default=None)

    repair_parser = subparsers.add_parser("repair-plan", help="Create a human review repair plan from analysis JSON.")
    repair_parser.add_argument("--work-id", required=True)
    repair_parser.add_argument("--analysis-path", default="")
    repair_parser.add_argument("--output", default="")
    repair_parser.add_argument("--repo-root", default=None)

    sync_parser = subparsers.add_parser(
        "github-sync-plan", help="Create an approval-gated GitHub CLI/API sync plan from analysis JSON."
    )
    sync_parser.add_argument("--work-id", required=True)
    sync_parser.add_argument("--analysis-path", default="")
    sync_parser.add_argument("--output", default="")
    sync_parser.add_argument("--repo-root", default=None)

    rag_parser = subparsers.add_parser("rag-candidate", help="Create a RAG candidate note from analysis JSON.")
    rag_parser.add_argument("--work-id", required=True)
    rag_parser.add_argument("--analysis-path", default="")
    rag_parser.add_argument("--topic", default="")
    rag_parser.add_argument("--output", default="")
    rag_parser.add_argument("--publish-rag", action="store_true")
    rag_parser.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    rag_parser.add_argument("--repo-root", default=None)
    return parser


def repository_name(repository: str, default_owner: str = "") -> str:
    slug = repository_to_github_slug(repository, default_owner)
    if slug:
        name = slug.rsplit("/", 1)[-1]
    else:
        name = Path(repository.replace("\\", "/").rstrip("/")).name
    if name.endswith(".git"):
        name = name[:-4]
    return slugify(name)


def default_work_id(repository: str, scan_mode: list[str], default_owner: str = "") -> str:
    repo_name = repository_name(repository, default_owner)
    mode = "full" if "full" in scan_mode else scan_mode[0]
    return f"github-knowledge-{repo_name}-{mode}"


def rag_source_report_name(topic: str) -> str:
    timestamp = local_timestamp().replace("_", "")
    random_id = "".join(secrets.choice(RAG_SOURCE_ID_ALPHABET) for _ in range(6))
    return f"{timestamp}_{random_id}_{slugify(topic)}.md"


def github_operation_gate(
    *,
    work_id: str,
    repository: str,
    repair_mode: str,
    rag_output: bool,
) -> dict[str, Any]:
    mutation_allowed = repair_mode == "apply"
    reasons = []
    if mutation_allowed:
        reasons.append("repair-mode apply may execute GitHub mutation and requires item-level human approval.")
    if rag_output:
        reasons.append("RAG publication requires human approval before publication.")
    return {
        "schema_version": "1.0",
        "artifact_type": "github-operation-gate",
        "workflow": "github-knowledge-maintenance",
        "work_id": work_id,
        "created_at": utc_now_iso(),
        "repository": repository,
        "read_only_allowed": True,
        "mutation_allowed": mutation_allowed,
        "clone_allowed": False,
        "human_check_required": bool(reasons),
        "human_check_reasons": reasons,
        "rules": [
            "Read-only GitHub CLI/API collection may proceed.",
            "GitHub mutation requires human-reviewed sync plan and explicit approval.",
            "Clone requires separate human approval when API evidence is insufficient.",
        ],
    }


def github_tool_selection(
    *,
    work_id: str,
    repair_mode: str,
) -> dict[str, Any]:
    tools = [
        {
            "name": "gh",
            "mode": "read-only",
            "purpose": "Collect GitHub Issue, PR, label, comment, release, and metadata evidence.",
            "required": True,
            "source": "github-knowledge-maintenance",
            "human_check_required": False,
        },
        {
            "name": "github-api",
            "mode": "read-only",
            "purpose": "Collect GitHub metadata when gh output needs API-backed detail.",
            "required": False,
            "source": "github-knowledge-maintenance",
            "human_check_required": False,
        },
    ]
    if repair_mode == "apply":
        tools.append(
            {
                "name": "gh",
                "mode": "mutation",
                "purpose": "Apply human-approved GitHub documentation sync actions.",
                "required": False,
                "source": "github-knowledge-maintenance",
                "human_check_required": True,
            }
        )
    return {
        "schema_version": "1.0",
        "artifact_type": "tool-selection",
        "architecture": "context-first",
        "selected_at": utc_now_iso(),
        "selected_by": "dispatcher",
        "selection_mode": "manual",
        "work_id": work_id,
        "workflow": "github-knowledge-maintenance",
        "status": "selected",
        "tools": tools,
        "human_check_required": any(item["human_check_required"] for item in tools),
        "human_check_reasons": [
            f"Tool `{item['name']}` is selected for mutation mode."
            for item in tools
            if item["human_check_required"]
        ],
        "source": {
            "registry": "db/registries/registry.duckdb",
            "schema": ".github/schemas/tool-selection.schema.json",
        },
    }


def register_github_knowledge_contexts(repo_root: Path, work_dir: Path, work_id: str) -> None:
    context_dir = work_dir / "context"
    registrations = [
        ("agent-context", context_dir / "agent-context.json", True, ".github/schemas/agent-context.schema.json"),
        ("artifact-index", context_dir / "artifact-index.json", True, ".github/schemas/artifact-index.schema.json"),
        ("handoff-package", context_dir / "handoff-package.json", False, ".github/schemas/handoff-package.schema.json"),
        ("tool-selection", context_dir / "tool-selection.json", True, ".github/schemas/tool-selection.schema.json"),
        ("github-operation-gate", context_dir / "github-operation-gate.json", True, ".github/schemas/github-operation-gate.schema.json"),
        ("github-knowledge-analysis", context_dir / "github-knowledge-analysis.json", False, ".github/schemas/github-knowledge-analysis.schema.json"),
        ("qa-records", context_dir / "qa-records.json", False, ".github/schemas/qa-record.schema.json"),
        ("finding-records", context_dir / "finding-records.json", False, ".github/schemas/finding-record.schema.json"),
        ("decision-records", context_dir / "decision-records.json", False, ".github/schemas/decision-record.schema.json"),
        ("test-evidence", context_dir / "test-evidence.json", False, ".github/schemas/test-evidence.schema.json"),
    ]
    for context_type, path, required, schema in registrations:
        if not path.exists():
            continue
        register_context(
            repo_root,
            work_dir,
            work_id=work_id,
            context_type=context_type,
            path=path,
            required=required,
            generated_by="github-knowledge-maintenance",
            owner="workflow" if context_type not in {"tool-selection"} else "dispatcher",
            schema=schema,
        )


def init_work(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    repository = normalize_repository_value(args.repository)
    repo_name = repository_name(repository, default_github_owner(settings))
    work_id = args.work_id or default_work_id(repository, args.scan_mode, default_github_owner(settings))
    work_dir = repo_root / "work" / work_id
    if work_dir.exists() and not args.reuse_existing:
        raise FileExistsError(
            f"Work directory already exists: {work_dir}. Confirm reuse, then rerun with --reuse-existing."
        )

    work_dir = ensure_work_tree(repo_root, work_id)
    context_dir = work_dir / "context"
    now = utc_now_iso()
    intent_summary = args.intent_summary or (
        f"{repository} のGitHub knowledge assetsを、Git historyを消さずsource codeを変更せずに保守する。"
    )
    scan_modes = sorted(set(args.scan_mode), key=args.scan_mode.index)

    agent_context = {
        "schema_version": "1.0",
        "project": {
            "name": repo_name,
            "repository": repository,
            "environment": "",
        },
        "workflow": {
            "name": "github-knowledge-maintenance",
            "phase": "initialization",
            "risk_level": "low",
            "command": "/github-knowledge-maintenance",
        },
        "agent": {
            "name": "runtime-workflow",
            "role": "GitHub repository knowledge maintenance initialization",
            "input_artifacts": [],
            "output_artifacts": [
                relative_to_repo(repo_root, context_dir / "agent-context.json"),
                relative_to_repo(repo_root, context_dir / "artifact-index.json"),
            ],
        },
        "intent": {
            "summary": intent_summary,
            "non_goals": [
                "Git historyを消したり、過去の証跡を隠したりしない。",
                "target repositoryのcommit source、source code、README本文、configuration contentを変更しない。",
                "既存commit messageを書き換える場合は、人間がitem単位でhigh-risk pathを明示承認した場合に限る。",
                "GitHub CLI/APIの証跡が不足し、人間が承認した場合を除き、repositoryをcloneしない。",
            ],
            "success_criteria": [
                "GitHub metadata collection planが明示されている。",
                "Knowledge assetsとnarrative gapsがJSONに記録されている。",
                "人間レビュー可能なrepair proposalsが準備されている。",
                "Commit repair proposalsに、GitHub commit-list viewだけで意味が分かるsemantic subjectが含まれている。",
                "PR title repair proposalsに、GitHub PR-list viewだけで意味が分かるsemantic titleが含まれている。",
                "承認済みGitHub documentation sync actionsがdraft proposalsと分離されている。",
                "要求された場合、Knowledge DB candidatesとRAG candidatesが生成されている。",
            ],
        },
        "assumptions": [
            f"work_id={work_id}",
            f"target_repository={repository}",
            f"target_branch={args.target_branch}",
            f"scan_mode={','.join(scan_modes)}",
            f"repair_mode={args.repair_mode}",
            f"rag_output={bool(args.rag_output)}",
        ],
        "constraints": [
            "Git historyは歴史的証跡であり、消してはいけない。",
            "既存commit-message/body rewriteは、item単位の明示的な人間承認、before/after SHA mapping、rollback plan、必要時のreview済みforce-push commandがある場合のみ許可する。",
            "Commit message repairでは、GitHub commit-list subjectをbodyとは別に評価する。",
            "このworkflowではcommit sourceとsource filesを変更しない。",
            "GitHub mutationには明示的な人間承認が必要。",
            "Repair mode 'proposal' では gh edit/comment commandを実行しない。",
            "Repair mode 'apply' でも、各mutation前にitem単位の人間承認が必要。",
            "Cloneには明示的な人間承認と記録済み理由が必要。",
        ],
    }
    write_json(context_dir / "agent-context.json", agent_context)
    for filename, value in [
        ("qa-records.json", []),
        ("finding-records.json", []),
        ("decision-records.json", []),
        ("test-evidence.json", []),
    ]:
        write_json(context_dir / filename, value)

    write_json(
        context_dir / "handoff-package.json",
        {
            "schema_version": "1.0",
            "from_agent": "runtime-workflow",
            "to_agent": "repository-discovery-agent",
            "workflow": "github-knowledge-maintenance",
            "phase": "initialization",
            "intent": intent_summary,
            "summary": f"Initialized GitHub knowledge maintenance work area {work_id}.",
            "decisions": [],
            "artifacts": [],
            "open_questions": [
                "Confirm whether GitHub mutation is allowed for this run.",
                "Confirm whether clone is allowed if GitHub API evidence is incomplete.",
            ],
            "risks": [],
            "required_next_actions": [
                "Create the analysis scaffold.",
                "gh issue/pr/api commandでGitHub metadataを収集する。",
                "knowledge assets、narrative gaps、semantic subject gaps、PR title gaps、repair proposalsをJSONへ記録する。",
            ],
            "stop_conditions": [
                "人間承認が記録されるまでGitHubまたはGit mutation前で停止する。",
                "既存commit-message rewriteは、before/after SHA mappingとrollback planがreviewされるまで停止する。",
                "提案semantic subjectがGitHub commit-list viewでまだ曖昧な場合、commit-message rewrite前で停止する。",
                "人間承認と理由が記録されるまでclone前で停止する。",
            ],
        },
    )
    write_json(
        context_dir / "tool-selection.json",
        github_tool_selection(work_id=work_id, repair_mode=args.repair_mode),
    )
    write_json(
        context_dir / "github-operation-gate.json",
        github_operation_gate(
            work_id=work_id,
            repository=repository,
            repair_mode=args.repair_mode,
            rag_output=bool(args.rag_output),
        ),
    )

    index = load_artifact_index(work_dir, repo_name, "github-knowledge-maintenance")
    upsert_artifact(
        index,
        {
            "id": "AGENT-CONTEXT",
            "title": "GitHub Knowledge Maintenance Context",
            "path": relative_to_repo(repo_root, context_dir / "agent-context.json"),
            "type": "other",
            "status": "draft",
            "owner_agent": "runtime-workflow",
            "created_at": now,
            "updated_at": now,
            "depends_on": [],
            "consumed_by": ["repository-discovery-agent", "github-metadata-collector"],
            "summary": "GitHub repository knowledge maintenanceのworkflow context。",
            "unresolved_items": [],
        },
    )
    write_json(context_dir / "artifact-index.json", index)
    register_github_knowledge_contexts(repo_root, work_dir, work_id)
    return {
        "work_id": work_id,
        "work_dir": relative_to_repo(repo_root, work_dir),
        "repository": repository,
        "target_branch": args.target_branch,
        "scan_mode": scan_modes,
        "repair_mode": args.repair_mode,
        "rag_output": bool(args.rag_output),
    }


def default_analysis(work_dir: Path) -> dict[str, Any]:
    context = read_json(work_dir / "context" / "agent-context.json", default={}) or {}
    assumptions = context.get("assumptions", [])
    assumption_map = {}
    for item in assumptions:
        if isinstance(item, str) and "=" in item:
            key, value = item.split("=", 1)
            assumption_map[key] = value
    return {
        "schema_version": "1.0",
        "workflow": "github-knowledge-maintenance",
        "work_id": work_dir.name,
        "repository": context.get("project", {}).get("repository", ""),
        "target_branch": assumption_map.get("target_branch", ""),
        "scan_mode": [mode for mode in assumption_map.get("scan_mode", "recent").split(",") if mode],
        "repair_mode": assumption_map.get("repair_mode", "proposal"),
        "rag_output": assumption_map.get("rag_output", "False").lower() == "true",
        "generated_at": utc_now_iso(),
        "summary": "TBD: GitHub repository knowledge maintenanceの調査結果を要約する。",
        "collection_plan": [
            {
                "id": "COLLECT-000",
                "source_type": "api",
                "command": "gh --version; if missing, request human approval then run: winget install --id GitHub.cli",
                "purpose": "Issue、PR、comment、label、branch、tag、release metadataを収集する前にGitHub CLIが利用可能であることを確認する。",
                "status": "planned",
            },
            {
                "id": "COLLECT-001",
                "source_type": "issue",
                "command": "gh issue list --repo <owner/repo> --state all --limit 100",
                "purpose": "Issueのintentとmaintenance contextを収集する。",
                "status": "planned",
            },
            {
                "id": "COLLECT-002",
                "source_type": "pull-request",
                "command": "gh pr list --repo <owner/repo> --state all --limit 100",
                "purpose": "PRのimplementation narrativeとreview contextを収集する。",
                "status": "planned",
            },
        ],
        "metadata_sources": [],
        "knowledge_assets": [],
        "narrative_gaps": [],
        "repair_proposals": [],
        "github_sync_actions": [],
        "knowledge_db_candidates": [],
        "rag_candidates": [],
        "open_questions": [],
        "guardrails": [
            "Git historyを消したり、歴史的証跡を隠したりしない。",
            "commit sourceまたはtarget repositoryのsource filesを変更しない。",
            "既存commit-message/body rewriteには、item単位の明示的な人間承認、before/after SHA mapping、rollback plan、必要時のreview済みforce-push commandが必要。",
            "GitHub commit-list subjectが曖昧なままの場合、bodyのみのcommit repairを承認しない。",
            "Commit repair proposalsには `type(scope): responsibility/result` 形式のsemantic subjectを含める。",
            "PR title repair proposalsには、bodyを開かなくてもGitHub PR-list viewで意味が分かるsemantic titleを含める。",
            "source codeを変更しない。",
            "人間承認なしに gh edit/comment/api mutation commandを実行しない。",
            "GitHub CLI/API収集を優先し、cloneは明示承認がある場合のみ行う。",
        ],
    }


def analysis_path_for(work_dir: Path, raw_path: str) -> Path:
    return Path(raw_path).resolve() if raw_path else work_dir / "context" / "github-knowledge-analysis.json"


def register_artifact(repo_root: Path, work_dir: Path, artifact_id: str, title: str, path: Path, artifact_type: str) -> None:
    context = read_json(work_dir / "context" / "agent-context.json", default={}) or {}
    project_name = context.get("project", {}).get("name", work_dir.name)
    index = load_artifact_index(work_dir, project_name, "github-knowledge-maintenance")
    now = utc_now_iso()
    upsert_artifact(
        index,
        {
            "id": artifact_id,
            "title": title,
            "path": relative_to_repo(repo_root, path),
            "type": artifact_type,
            "status": "draft",
            "owner_agent": "github-knowledge-maintenance",
            "created_at": now,
            "updated_at": now,
            "depends_on": [],
            "consumed_by": ["documentation-repair-agent", "knowledge-db-registrar"],
            "summary": title,
            "unresolved_items": [],
        },
    )
    write_json(work_dir / "context" / "artifact-index.json", index)
    if path.name == "github-knowledge-analysis.json":
        register_context(
            repo_root,
            work_dir,
            work_id=work_dir.name,
            context_type="github-knowledge-analysis",
            path=path,
            required=True,
            generated_by="github-knowledge-maintenance",
            owner="workflow",
            schema=".github/schemas/github-knowledge-analysis.schema.json",
        )


def create_analysis_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = repo_root / "work" / args.work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    output_path = analysis_path_for(work_dir, args.analysis_path)
    analysis = default_analysis(work_dir)
    write_json(output_path, analysis)
    register_artifact(repo_root, work_dir, "GITHUB-KNOWLEDGE-ANALYSIS", "GitHub Knowledge Analysis", output_path, "report")
    return {
        "analysis_path": relative_to_repo(repo_root, output_path),
        "knowledge_asset_count": 0,
        "narrative_gap_count": 0,
    }


def markdown_list(items: list[str]) -> str:
    if not items:
        return "- なし"
    return "\n".join(f"- {item}" for item in items)


FIELD_LABELS = {
    "asset_ref": "知識資産",
    "gap_type": "不足種別",
    "severity": "重要度",
    "evidence": "根拠",
    "why_it_matters": "なぜ重要か",
    "target": "対象",
    "proposal_type": "提案種別",
    "reason": "理由",
    "before_summary": "現状",
    "after_summary": "対応後",
    "approval_required": "承認要否",
    "draft_body": "提案本文",
    "asset_type": "知識種別",
    "source_ref": "参照元",
    "intent": "意図",
    "reuse_value": "再利用価値",
    "candidate_type": "候補種別",
    "knowledge_value": "知識価値",
    "limits": "制約",
    "question": "確認事項",
    "blocks": "ブロック有無",
}


def markdown_value(value: Any) -> str:
    if isinstance(value, bool):
        return "はい" if value else "いいえ"
    return str(value)


def field_list(items: list[dict[str, Any]], fields: list[str]) -> str:
    if not items:
        return "- なし"
    lines: list[str] = []
    for item in items:
        title = item.get("title") or item.get("id") or "Untitled"
        lines.append(f"### {title}")
        lines.append("")
        for field in fields:
            label = FIELD_LABELS.get(field, field)
            value = item.get(field, "")
            if isinstance(value, list):
                value_text = markdown_list([markdown_value(entry) for entry in value])
                lines.extend([f"{label}:", "", value_text, ""])
            else:
                lines.append(f"- {label}: {markdown_value(value)}")
        lines.append("")
    return "\n".join(lines).rstrip()


def load_analysis(repo_root: Path, work_id: str, raw_path: str) -> tuple[Path, Path, dict[str, Any]]:
    work_dir = repo_root / "work" / work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    path = analysis_path_for(work_dir, raw_path)
    if not path.exists():
        raise FileNotFoundError(f"GitHub knowledge analysis does not exist: {path}")
    analysis = read_json(path)
    if not isinstance(analysis, dict):
        raise ValueError(f"GitHub knowledge analysis must be a JSON object: {path}")
    return work_dir, path, analysis


def require_github_operation_gate(
    repo_root: Path,
    work_dir: Path,
    *,
    require_mutation_gate: bool = False,
    require_rag_gate: bool = False,
) -> dict[str, Any]:
    manifest_path = manifest_path_for_work_dir(work_dir)
    manifest = load_manifest(work_dir)
    gate_entry = context_entry(manifest, "github-operation-gate")
    tool_entry = context_entry(manifest, "tool-selection")
    missing = []
    if gate_entry is None:
        missing.append("github-operation-gate")
    if require_mutation_gate and tool_entry is None:
        missing.append("tool-selection")
    if missing:
        raise RuntimeError(
            "Context First gate: github-knowledge-maintenance requires "
            + ", ".join(missing)
            + f" before this operation. Re-run init or repair the manifest: {manifest_path}"
        )

    gate_path = context_path(repo_root, gate_entry) if gate_entry else work_dir / "context" / "github-operation-gate.json"
    gate = read_json(gate_path, default={}) or {}
    tool_path = context_path(repo_root, tool_entry) if tool_entry else work_dir / "context" / "tool-selection.json"
    tool_selection = read_json(tool_path, default={}) or {}
    reasons = []
    if require_mutation_gate and not bool(gate.get("mutation_allowed")):
        reasons.append("github-operation-gate does not allow mutation.")
    if require_mutation_gate and not bool(tool_selection.get("human_check_required")):
        reasons.append("tool-selection must mark GitHub mutation as Human Check required.")
    if require_rag_gate and not bool(gate.get("human_check_required")):
        reasons.append("github-operation-gate must require Human Check for RAG publication.")
    if reasons:
        raise RuntimeError("Context First gate: " + " ".join(reasons))

    return {
        "status": "ready",
        "manifest_path": relative_to_repo(repo_root, manifest_path),
        "github_operation_gate": relative_to_repo(repo_root, gate_path),
        "tool_selection": relative_to_repo(repo_root, tool_path) if tool_entry else "",
        "require_mutation_gate": require_mutation_gate,
        "require_rag_gate": require_rag_gate,
    }


def build_repair_plan(analysis: dict[str, Any]) -> str:
    proposals = analysis.get("repair_proposals", []) or []
    gaps = analysis.get("narrative_gaps", []) or []
    return "\n".join(
        [
            "# GitHub ナレッジ修復計画",
            "",
            "## 意図",
            "",
            analysis.get("summary", "Maintain GitHub repository knowledge assets."),
            "",
            "## Repository",
            "",
            f"- Repository: `{analysis.get('repository', '')}`",
            f"- 対象 branch: `{analysis.get('target_branch', '')}`",
            f"- 修復 mode: `{analysis.get('repair_mode', 'proposal')}`",
            "",
            "## ガードレール",
            "",
            markdown_list(analysis.get("guardrails", []) or []),
            "",
            "## Narrative Gap",
            "",
            field_list(gaps, ["asset_ref", "gap_type", "severity", "evidence", "why_it_matters"]),
            "",
            "## 修復提案",
            "",
            field_list(proposals, ["target", "proposal_type", "reason", "before_summary", "after_summary", "draft_body", "approval_required"]),
            "",
            "## Semantic Commit / PR Title チェック",
            "",
            "commit message/body 補修では、GitHub の commit list に表示される subject を body と別に確認します。",
            "PR title 補修では、GitHub の PR list に表示される title を body と別に確認します。",
            "",
            "良い形式:",
            "",
            "```text",
            "type(scope): 変更の責務または成果",
            "```",
            "",
            "避ける subject:",
            "",
            "- repository 名だけを scope にした subject",
            "- PR title が `Develop` や branch 名だけで終わる title",
            "- file 名だけの subject",
            "- `対応`、`修正`、`更新` だけで終わる subject",
            "- body を読まないと何が変わったか分からない subject/title",
            "",
            "Human Review では、subject/title が GitHub list view だけで意味を持つか確認します。",
            "",
            "## Human Review チェックリスト",
            "",
            "- 各修復理由を確認する。",
            "- 対象の Issue、PR、comment、CAR、README、docs、ADR を確認する。",
            "- 修正前後の要約を確認する。",
            "- commit message/body 補修では semantic subject が `type(scope): responsibility/result` になっていることを確認する。",
            "- semantic subject が GitHub commit list だけで意味を持つことを確認する。",
            "- PR title 補修では current title、proposed title、exact `gh pr edit --title` command を確認する。",
            "- PR title が GitHub PR list だけで意味を持つことを確認する。",
            "- commit source や対象 repository の source file を変更しないことを確認する。",
            "- 既存 commit message/body を直接修正する場合は、明示承認、before/after SHA mapping、rollback plan を確認する。",
            "- rewrite 後は `git log --format=\"%H %s\"` または GitHub API で subject 表示を確認する。",
            "- 実行前に正確な Git / GitHub CLI/API command を確認する。",
        ]
    )


def create_repair_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    output_path = (
        Path(args.output).resolve()
        if args.output
        else work_dir / "process-report" / f"github-knowledge-repair-plan-{local_timestamp()}.md"
    )
    write_markdown_bom(output_path, build_repair_plan(analysis))
    register_artifact(repo_root, work_dir, "GITHUB-KNOWLEDGE-REPAIR-PLAN", "GitHub Knowledge Repair Plan", output_path, "report")
    return {
        "repair_plan": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "proposal_count": len(analysis.get("repair_proposals", []) or []),
    }


def build_sync_plan(analysis: dict[str, Any]) -> str:
    actions = analysis.get("github_sync_actions", []) or []
    lines = [
        "# GitHub Documentation Sync 計画",
        "",
        "この計画自体は承認ではありません。人間レビューで承認された command だけを実行します。",
        "",
        "## Repository",
        "",
        f"- Repository: `{analysis.get('repository', '')}`",
        f"- 対象 branch: `{analysis.get('target_branch', '')}`",
        "",
        "## GitHub 同期アクション案",
        "",
    ]
    if not actions:
        lines.append("- なし")
    for action in actions:
        lines.extend(
            [
                f"### {action.get('id', 'SYNC-XXX')}: {action.get('title', 'Untitled')}",
                "",
                f"- 対象種別: `{action.get('target_type', '')}`",
                f"- 対象 ID: `{action.get('target_id', '')}`",
                f"- 操作: `{action.get('operation', '')}`",
                f"- 承認状態: `{action.get('approval_status', 'pending')}`",
                "",
                "理由:",
                "",
                action.get("reason", ""),
                "",
                "Command 案:",
                "",
                "```powershell",
                action.get("draft_command", "# Update github-knowledge-analysis.json with the exact gh command."),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Stop Rules",
            "",
            "- `pending` の command は実行しない。",
            "- この GitHub documentation sync plan では commit message rewrite を実行しない。",
            "- `git rebase`、`git commit --amend`、force push は、別の commit-message rewrite review plan で明示承認された場合だけ扱う。",
            "- commit message rewrite を扱う場合は、semantic subject の GitHub commit-list 表示を別途検証する。",
            "- 対象または command がこの計画と異なる場合は、analysis JSON を更新して再レビューする。",
        ]
    )
    return "\n".join(lines)


def create_sync_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    context_gate = require_github_operation_gate(
        repo_root,
        work_dir,
        require_mutation_gate=str(analysis.get("repair_mode", "proposal")) == "apply",
    )
    output_path = (
        Path(args.output).resolve()
        if args.output
        else work_dir / "process-report" / f"github-documentation-sync-plan-{local_timestamp()}.md"
    )
    write_markdown_bom(output_path, build_sync_plan(analysis))
    register_artifact(repo_root, work_dir, "GITHUB-DOCUMENTATION-SYNC-PLAN", "GitHub Documentation Sync Plan", output_path, "report")
    return {
        "sync_plan": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "action_count": len(analysis.get("github_sync_actions", []) or []),
        "context_gate": context_gate,
    }


def build_rag_candidate(analysis: dict[str, Any], topic: str) -> str:
    title = topic or f"github-knowledge-{repository_name(analysis.get('repository', 'repository'))}"
    return "\n".join(
        [
            "---",
            "schema_version: '1.0'",
            "document_type: github-repository-knowledge",
            f"repository: {analysis.get('repository', '')}",
            f"branch: {analysis.get('target_branch', '')}",
            "status: candidate",
            f"created_at: {utc_now_iso()}",
            "source: github-knowledge-maintenance",
            "---",
            "",
            f"# {title}",
            "",
            "## 要約",
            "",
            analysis.get("summary", ""),
            "",
            "## 知識資産",
            "",
            field_list(analysis.get("knowledge_assets", []) or [], ["asset_type", "source_ref", "intent", "reuse_value"]),
            "",
            "## Narrative Gap",
            "",
            field_list(analysis.get("narrative_gaps", []) or [], ["asset_ref", "gap_type", "severity", "why_it_matters"]),
            "",
            "## 修復提案",
            "",
            field_list(analysis.get("repair_proposals", []) or [], ["target", "proposal_type", "reason", "approval_required"]),
            "",
            "## RAG 候補",
            "",
            field_list(analysis.get("rag_candidates", []) or [], ["candidate_type", "source_ref", "knowledge_value", "limits"]),
            "",
            "## Open Questions",
            "",
            field_list(analysis.get("open_questions", []) or [], ["question", "reason", "blocks"]),
        ]
    )


def create_rag_candidate(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    if args.publish_rag and args.human_check != "approved":
        raise PermissionError("RAG publication requires --human-check approved.")
    context_gate = require_github_operation_gate(
        repo_root,
        work_dir,
        require_rag_gate=bool(args.publish_rag),
    )
    topic = args.topic or f"github-knowledge-{repository_name(analysis.get('repository', 'repository'))}"
    if args.output:
        output_path = Path(args.output).resolve()
    elif args.publish_rag:
        output_path = repo_root / "rag" / "github-knowledge" / rag_source_report_name(topic)
    else:
        output_path = work_dir / "process-report" / f"github-knowledge-rag-candidate-{local_timestamp()}.md"
    write_markdown_bom(output_path, build_rag_candidate(analysis, topic))
    register_artifact(repo_root, work_dir, "GITHUB-KNOWLEDGE-RAG-CANDIDATE", "GitHub Knowledge RAG Candidate", output_path, "report")
    return {
        "rag_candidate": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "published": bool(args.publish_rag),
        "context_gate": context_gate,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "init":
        return init_work(args)
    if args.command == "analysis-template":
        return create_analysis_template(args)
    if args.command == "repair-plan":
        return create_repair_plan(args)
    if args.command == "github-sync-plan":
        return create_sync_plan(args)
    if args.command == "rag-candidate":
        return create_rag_candidate(args)
    raise ValueError(f"Unsupported command: {args.command}")


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
