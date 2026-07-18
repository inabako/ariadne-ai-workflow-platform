from __future__ import annotations

import argparse
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import registry_store  # noqa: E402
from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402


TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u3040-\u30ff\u3400-\u9fff]+")


def workflow_help_registry_path(repo_root: Path) -> Path:
    return registry_store.registry_db_path(repo_root)


def tool_candidate_registry_path(repo_root: Path) -> Path:
    return registry_store.registry_db_path(repo_root)


def load_workflow_help_registry(repo_root: Path) -> dict[str, Any]:
    data = registry_store.load_workflow_help(repo_root)
    if not isinstance(data, dict):
        return {"commands": [], "extensions": []}
    data.setdefault("commands", [])
    data.setdefault("extensions", [])
    return data


def load_tool_candidate_registry(repo_root: Path) -> dict[str, Any]:
    data = registry_store.load_tool_candidates(repo_root)
    if not isinstance(data, dict):
        return {"tools": []}
    data.setdefault("tools", [])
    return data


def normalize_command(value: str) -> str:
    value = value.strip()
    return value if not value or value.startswith("/") else f"/{value}"


def workflow_names(item: dict[str, Any]) -> list[str]:
    return [
        str(name)
        for name in [item.get("command", ""), *item.get("aliases", []), item.get("workflow", ""), item.get("skill", "")]
        if str(name).strip()
    ]


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    return str(value)


def tokenize(value: str) -> set[str]:
    normalized = value.lower().replace("/", " ").replace("-", " ").replace("_", " ")
    return {match.group(0) for match in TOKEN_RE.finditer(normalized) if match.group(0).strip()}


def exact_workflow_match(item: dict[str, Any], workflow: str) -> bool:
    normalized = normalize_command(workflow).lower()
    plain = workflow.strip().lower().lstrip("/")
    names = workflow_names(item)
    normalized_names = {str(name).lower().lstrip("/") for name in names if str(name).strip()}
    slash_names = {normalize_command(str(name)).lower() for name in names if str(name).strip()}
    return normalized in slash_names or plain in normalized_names


def find_workflow_record(registry: dict[str, Any], workflow: str) -> dict[str, Any]:
    for item in registry.get("commands", []):
        if exact_workflow_match(item, workflow):
            return item
    return {}


def workflow_search_text(item: dict[str, Any]) -> str:
    fields = [
        item.get("command", ""),
        item.get("workflow", ""),
        item.get("skill", ""),
        item.get("aliases", []),
        item.get("overview", ""),
        item.get("prerequisites", []),
        item.get("arguments", []),
        item.get("details", []),
        item.get("examples", []),
        item.get("docs", []),
        item.get("related_runtime", []),
    ]
    return flatten_text(fields)


def candidate_score(item: dict[str, Any], query: str, intent_summary: str) -> tuple[int, list[str]]:
    reasons: list[str] = []
    if exact_workflow_match(item, query):
        return 100, ["exact command / alias / workflow match"]

    query_text = " ".join(part for part in [query, intent_summary] if part.strip())
    query_tokens = tokenize(query_text)
    name_tokens = tokenize(" ".join(workflow_names(item)))
    body_tokens = tokenize(workflow_search_text(item))
    score = 0

    name_overlap = sorted(query_tokens & name_tokens)
    body_overlap = sorted(query_tokens & body_tokens)
    if name_overlap:
        score += 18 * len(name_overlap)
        reasons.append(f"name token match: {', '.join(name_overlap[:5])}")
    if body_overlap:
        score += 4 * len(body_overlap)
        reasons.append(f"registry text match: {', '.join(body_overlap[:5])}")

    compact_query = query.strip().lower().lstrip("/")
    search_text = workflow_search_text(item).lower()
    if compact_query and compact_query in search_text:
        score += 25
        reasons.append("query phrase appears in registry text")

    command = str(item.get("command", ""))
    if command:
        command_tokens = tokenize(command)
        if command_tokens and command_tokens <= query_tokens:
            score += 30
            reasons.append("all command tokens appear in query")

    return min(score, 99), reasons or ["no strong registry evidence"]


def workflow_candidates(
    registry: dict[str, Any],
    query: str,
    intent_summary: str,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for item in registry.get("commands", []):
        score, reasons = candidate_score(item, query, intent_summary)
        if score <= 0:
            continue
        candidates.append(
            {
                "command": str(item.get("command", "")),
                "workflow": str(item.get("workflow", "")),
                "skill": str(item.get("skill", "")),
                "score": score,
                "reasons": reasons,
                "docs": item.get("docs", []),
            }
        )
    return sorted(candidates, key=lambda item: (-int(item["score"]), item["command"]))[:limit]


def select_workflow_record(
    registry: dict[str, Any],
    workflow: str,
    intent_summary: str,
    *,
    candidate_limit: int,
) -> dict[str, Any]:
    exact = find_workflow_record(registry, workflow)
    candidates = workflow_candidates(registry, workflow, intent_summary, limit=candidate_limit)
    if exact:
        selected = exact
        selected_command = str(exact.get("command", ""))
        for candidate in candidates:
            if candidate.get("command") == selected_command:
                candidate["selected"] = True
                break
        return {
            "record": selected,
            "selection_mode": "manual",
            "confidence": "high",
            "status": "selected",
            "human_check_required": False,
            "human_check_reasons": [],
            "candidates": candidates,
            "ambiguity_margin": None,
        }

    top = candidates[0] if candidates else {}
    second = candidates[1] if len(candidates) >= 2 else {}
    top_score = int(top.get("score", 0))
    second_score = int(second.get("score", 0))
    margin = top_score - second_score
    selected = {}
    for item in registry.get("commands", []):
        if str(item.get("command", "")) == str(top.get("command", "")):
            selected = item
            break

    can_auto_select = bool(selected) and top_score >= 50 and margin >= 10
    if can_auto_select:
        for candidate in candidates:
            if candidate.get("command") == top.get("command"):
                candidate["selected"] = True
        confidence = "medium" if top_score < 80 else "high"
        return {
            "record": selected,
            "selection_mode": "auto",
            "confidence": confidence,
            "status": "selected",
            "human_check_required": False,
            "human_check_reasons": [],
            "candidates": candidates,
            "ambiguity_margin": margin,
        }

    reasons = []
    if not candidates:
        reasons.append(f"Workflow `{workflow}` was not found in workflow_help registry.")
    elif margin < 10:
        reasons.append("Workflow candidate selection is ambiguous. Human selection is required.")
    else:
        reasons.append("Workflow candidate confidence is too low. Human selection is required.")
    return {
        "record": selected if can_auto_select else {},
        "selection_mode": "human-check",
        "confidence": "low" if candidates else "unknown",
        "status": "human-check-required",
        "human_check_required": True,
        "human_check_reasons": reasons,
        "candidates": candidates,
        "ambiguity_margin": margin if candidates else None,
    }


def default_tool_mode_for_workflow(workflow_name: str) -> str:
    if workflow_name in {"github-knowledge-maintenance", "docs-sync"}:
        return "read-only"
    return "local"


def tool_names(item: dict[str, Any]) -> list[str]:
    return [str(name) for name in [item.get("name", ""), *item.get("aliases", [])] if str(name).strip()]


def exact_tool_match(item: dict[str, Any], tool_name: str) -> bool:
    plain = tool_name.strip().lower()
    return plain in {name.lower() for name in tool_names(item)}


def find_tool_record(registry: dict[str, Any], tool_name: str) -> dict[str, Any]:
    for item in registry.get("tools", []):
        if exact_tool_match(item, tool_name):
            return item
    return {}


def tool_search_text(item: dict[str, Any]) -> str:
    fields = [
        item.get("name", ""),
        item.get("aliases", []),
        item.get("purpose", ""),
        item.get("workflows", []),
        item.get("keywords", []),
        item.get("runtime_paths", []),
    ]
    return flatten_text(fields)


def tool_candidate_score(item: dict[str, Any], query: str, workflow_name: str, intent_summary: str) -> tuple[int, list[str]]:
    reasons: list[str] = []
    raw_query = query.strip()
    tool_query = raw_query.split(":", 1)[0].strip()
    if tool_query and exact_tool_match(item, tool_query):
        return 100, ["exact tool name / alias match"]

    score = 0
    workflow_key = normalize_command(workflow_name).lower()
    workflow_plain = workflow_name.strip().lower().lstrip("/")
    workflows = {str(value).lower() for value in item.get("workflows", [])}
    workflows_plain = {value.lstrip("/") for value in workflows}
    if workflow_key in workflows or workflow_plain in workflows_plain:
        score += 55
        reasons.append(f"workflow match: {workflow_name}")

    query_text = " ".join(part for part in [raw_query, workflow_name, intent_summary] if part.strip())
    query_tokens = tokenize(query_text)
    name_overlap = sorted(query_tokens & tokenize(" ".join(tool_names(item))))
    body_overlap = sorted(query_tokens & tokenize(tool_search_text(item)))
    if name_overlap:
        score += 20 * len(name_overlap)
        reasons.append(f"name token match: {', '.join(name_overlap[:5])}")
    if body_overlap:
        score += 4 * len(body_overlap)
        reasons.append(f"registry text match: {', '.join(body_overlap[:5])}")

    compact_query = raw_query.lower()
    search_text = tool_search_text(item).lower()
    if compact_query and compact_query in search_text:
        score += 20
        reasons.append("query phrase appears in tool registry text")
    return min(score, 99), reasons or ["no strong tool registry evidence"]


def tool_candidates(
    registry: dict[str, Any],
    query: str,
    workflow_name: str,
    intent_summary: str,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for item in registry.get("tools", []):
        score, reasons = tool_candidate_score(item, query, workflow_name, intent_summary)
        if score <= 0:
            continue
        candidates.append(
            {
                "name": str(item.get("name", "")),
                "default_mode": str(item.get("default_mode", "local")),
                "purpose": str(item.get("purpose", "")),
                "score": score,
                "reasons": reasons,
                "install_required": bool(item.get("install_required", False)),
                "mutation_capable": bool(item.get("mutation_capable", False)),
                "human_check_required": bool(item.get("human_check_required", False)),
                "runtime_paths": item.get("runtime_paths", []),
            }
        )
    return sorted(candidates, key=lambda item: (-int(item["score"]), item["name"]))[:limit]


def tool_record_to_selection(
    item: dict[str, Any],
    *,
    mode: str,
    purpose: str,
    source: str,
) -> dict[str, Any]:
    human_reasons = list(item.get("human_check_reasons", []))
    human_check_required = bool(item.get("human_check_required", False))
    if mode == "mutation":
        human_check_required = True
        human_reasons.append(f"Tool `{item.get('name', '')}` is selected for mutation mode.")
    if item.get("install_required"):
        human_check_required = True
        human_reasons.append(f"Tool `{item.get('name', '')}` may require installation or runtime dependency setup.")
    return {
        "name": str(item.get("name", "")),
        "mode": mode or str(item.get("default_mode", "local")),
        "purpose": purpose or str(item.get("purpose", "")),
        "required": True,
        "source": source,
        "human_check_required": human_check_required,
        "human_check_reasons": sorted(set(reason for reason in human_reasons if reason)),
        "install_required": bool(item.get("install_required", False)),
        "mutation_capable": bool(item.get("mutation_capable", False)),
        "runtime_paths": item.get("runtime_paths", []),
    }


def split_tool(
    raw_tool: str,
    default_mode: str,
    default_purpose: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    parts = [part.strip() for part in raw_tool.split(":", 2)]
    name = parts[0]
    mode = parts[1] if len(parts) >= 2 and parts[1] else default_mode
    purpose = parts[2] if len(parts) >= 3 and parts[2] else default_purpose
    record = find_tool_record(registry or {}, name)
    if record:
        return tool_record_to_selection(
            record,
            mode=mode or str(record.get("default_mode", default_mode)),
            purpose=purpose or str(record.get("purpose", default_purpose)),
            source="dispatcher-input",
        )
    return {
        "name": name,
        "mode": mode,
        "purpose": purpose,
        "required": True,
        "source": "dispatcher-input",
        "human_check_required": mode == "mutation",
    }


def select_tool_records(
    registry: dict[str, Any],
    workflow_name: str,
    tools: list[str],
    *,
    intent_summary: str,
    default_mode: str,
    default_purpose: str,
    candidate_limit: int,
) -> dict[str, Any]:
    if tools:
        tool_records = [split_tool(raw_tool, default_mode, default_purpose, registry) for raw_tool in tools]
        candidates_by_input = {
            raw_tool: tool_candidates(registry, raw_tool, workflow_name, intent_summary, limit=candidate_limit)
            for raw_tool in tools
        }
        for raw_tool, candidates in candidates_by_input.items():
            tool_name = raw_tool.split(":", 1)[0].strip()
            for candidate in candidates:
                if candidate.get("name", "").lower() == tool_name.lower():
                    candidate["selected"] = True
                    break
        return {
            "selection_mode": "manual",
            "status": "selected" if tool_records else "skipped",
            "tools": tool_records,
            "candidate_selection": {
                "mode": "manual",
                "candidate_count": sum(len(items) for items in candidates_by_input.values()),
                "candidates_by_input": candidates_by_input,
            },
            "human_check_reasons": [],
        }

    query = " ".join(part for part in [workflow_name, intent_summary, default_purpose] if part.strip())
    candidates = tool_candidates(registry, query, workflow_name, intent_summary, limit=candidate_limit)
    if not candidates:
        return {
            "selection_mode": "auto",
            "status": "skipped",
            "tools": [],
            "candidate_selection": {
                "mode": "auto",
                "candidate_count": 0,
                "ambiguity_margin": None,
                "candidates": [],
            },
            "human_check_reasons": [],
        }

    top_score = int(candidates[0].get("score", 0))
    second_score = int(candidates[1].get("score", 0)) if len(candidates) >= 2 else 0
    margin = top_score - second_score
    selected_candidates = [item for item in candidates if int(item.get("score", 0)) >= 55]
    if top_score < 55:
        return {
            "selection_mode": "human-check",
            "status": "human-check-required",
            "tools": [],
            "candidate_selection": {
                "mode": "auto",
                "candidate_count": len(candidates),
                "ambiguity_margin": margin,
                "candidates": candidates,
            },
            "human_check_reasons": ["Tool candidate confidence is too low. Human selection is required."],
        }
    tool_records: list[dict[str, Any]] = []
    for candidate in selected_candidates:
        record = find_tool_record(registry, str(candidate.get("name", "")))
        if not record:
            continue
        candidate["selected"] = True
        tool_records.append(
            tool_record_to_selection(
                record,
                mode=str(record.get("default_mode", default_mode)),
                purpose=str(record.get("purpose", default_purpose)),
                source="tool-candidate-registry",
            )
        )
    return {
        "selection_mode": "auto",
        "status": "selected" if tool_records else "skipped",
        "tools": tool_records,
        "candidate_selection": {
            "mode": "auto",
            "candidate_count": len(candidates),
            "ambiguity_margin": margin,
            "candidates": candidates,
        },
        "human_check_reasons": [],
    }


def write_unless_exists(path: Path, data: dict[str, Any], *, force: bool) -> dict[str, Any]:
    if path.exists() and not force:
        existing = read_json(path, default={})
        if isinstance(existing, dict):
            return existing
    write_json(path, data)
    return data


def workflow_selection_context(
    repo_root: Path,
    work_id: str,
    workflow: str,
    selection: dict[str, Any],
    *,
    intent_summary: str,
) -> dict[str, Any]:
    workflow_record = selection.get("record", {})
    command = str(workflow_record.get("command") or normalize_command(workflow))
    workflow_name = str(workflow_record.get("workflow") or workflow.strip().lstrip("/"))
    return {
        "schema_version": "1.0",
        "artifact_type": "workflow-selection",
        "architecture": "context-first",
        "selected_at": utc_now_iso(),
        "selected_by": "dispatcher",
        "selection_mode": selection.get("selection_mode", "manual"),
        "work_id": work_id,
        "workflow": workflow_name,
        "command": command,
        "intent_summary": intent_summary or str(workflow_record.get("overview", "")),
        "status": selection.get("status", "selected" if workflow_record else "human-check-required"),
        "confidence": selection.get("confidence", "high" if workflow_record else "unknown"),
        "human_check_required": bool(selection.get("human_check_required", not bool(workflow_record))),
        "human_check_reasons": selection.get(
            "human_check_reasons",
            [] if workflow_record else [f"Workflow `{workflow}` was not found in workflow_help registry."],
        ),
        "candidate_selection": {
            "input": workflow,
            "intent_summary": intent_summary,
            "candidate_count": len(selection.get("candidates", [])),
            "ambiguity_margin": selection.get("ambiguity_margin"),
            "candidates": selection.get("candidates", []),
        },
        "source": {
            "registry": relative_to_repo(repo_root, workflow_help_registry_path(repo_root)),
            "schema": ".github/schemas/workflow-selection.schema.json",
        },
    }


def tool_selection_context(
    repo_root: Path,
    work_id: str,
    workflow_name: str,
    tools: list[str],
    *,
    intent_summary: str,
    default_mode: str,
    default_purpose: str,
    candidate_limit: int,
) -> dict[str, Any]:
    registry = load_tool_candidate_registry(repo_root)
    selection = select_tool_records(
        registry,
        workflow_name,
        tools,
        intent_summary=intent_summary,
        default_mode=default_mode,
        default_purpose=default_purpose,
        candidate_limit=candidate_limit,
    )
    tool_records = selection["tools"]
    human_check_reasons = [
        reason
        for item in tool_records
        for reason in item.get("human_check_reasons", [])
        if str(reason).strip()
    ]
    human_check_reasons.extend(selection.get("human_check_reasons", []))
    human_check_reasons = sorted(set(human_check_reasons))
    human_check_required = any(item.get("human_check_required") for item in tool_records) or bool(
        human_check_reasons
    )
    return {
        "schema_version": "1.0",
        "artifact_type": "tool-selection",
        "architecture": "context-first",
        "selected_at": utc_now_iso(),
        "selected_by": "dispatcher",
        "selection_mode": selection["selection_mode"],
        "work_id": work_id,
        "workflow": workflow_name,
        "status": "human-check-required" if human_check_required and selection["status"] != "skipped" else selection["status"],
        "tools": tool_records,
        "human_check_required": human_check_required,
        "human_check_reasons": human_check_reasons,
        "candidate_selection": selection["candidate_selection"],
        "source": {
            "registry": relative_to_repo(repo_root, tool_candidate_registry_path(repo_root)),
            "workflow_registry": relative_to_repo(repo_root, workflow_help_registry_path(repo_root)),
            "schema": ".github/schemas/tool-selection.schema.json",
        },
    }


def runtime_context(
    work_id: str,
    workflow_name: str,
    *,
    runtime_mode: str,
    target_dir: str,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact_type": "runtime-context",
        "architecture": "context-first",
        "workflow": workflow_name,
        "work_id": work_id,
        "mode": runtime_mode or "standard",
        "target_dir": target_dir,
        "created_at": utc_now_iso(),
        "runtime": {
            "host_os": platform.system() or "unknown",
            "default_shell": "PowerShell" if platform.system().lower().startswith("win") else "shell",
            "terminal_scope": "current workspace terminal",
        },
        "tool_paths": [
            "runtime/tools",
        ],
        "verification_commands": [
            "uv run --project runtime python runtime/common/ctl.py --repo-root . context show --work-dir work/<work-id>",
            "uv run --project runtime python runtime/workflow/workflow_doctor.py --fail-on-warning",
        ],
        "human_check_required_when": [
            "The selected workflow needs external mutation, install, network, device, Docker, or personal environment changes.",
            "The runtime cannot be inferred from repository evidence and registered Context.",
        ],
    }


def execution_plan_context(
    work_id: str,
    workflow_name: str,
    *,
    required_contexts: list[str],
    required_environment: str,
    next_commands: list[str],
    stop_conditions: list[str],
) -> dict[str, Any]:
    contexts = required_contexts or ["workflow-selection", "tool-selection", "runtime-context"]
    if required_environment and "environment-selection" not in contexts:
        contexts.append("environment-selection")
    return {
        "schema_version": "1.0",
        "artifact_type": "execution-plan",
        "architecture": "context-first",
        "work_id": work_id,
        "source_workflow": "dispatcher",
        "target_workflow": workflow_name,
        "created_at": utc_now_iso(),
        "status": "ready-for-human-check",
        "required_dispatcher_contexts": contexts,
        "required_environment": required_environment,
        "handoff_context": "",
        "validation_context": "",
        "source_artifacts": [],
        "stop_conditions": stop_conditions
        or [
            "Do not continue when required Dispatcher Context is missing.",
            "Do not infer environment, tools, runtime, or execution order when Context is contradictory.",
        ],
        "next_commands": next_commands or [normalize_command(workflow_name)],
    }


def register_dispatcher_context(
    repo_root: Path,
    work_dir: Path,
    work_id: str,
    *,
    context_type: str,
    path: Path,
    schema: str,
    required: bool = True,
) -> dict[str, Any]:
    return register_context(
        repo_root,
        work_dir,
        work_id=work_id,
        context_type=context_type,
        path=path,
        required=required,
        generated_by="dispatcher-context",
        owner="dispatcher",
        schema=schema,
    )


def run_init(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    registry = load_workflow_help_registry(repo_root)
    selection = select_workflow_record(
        registry,
        args.workflow,
        args.intent_summary,
        candidate_limit=getattr(args, "candidate_limit", 5),
    )
    work_dir = repo_root / "work" / args.work_id
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True, exist_ok=True)
    workflow_context = workflow_selection_context(
        repo_root,
        args.work_id,
        args.workflow,
        selection,
        intent_summary=args.intent_summary,
    )
    workflow_name = str(workflow_context["workflow"])
    default_tool_mode = args.tool_mode or default_tool_mode_for_workflow(workflow_name)
    tool_context = tool_selection_context(
        repo_root,
        args.work_id,
        workflow_name,
        args.tool,
        intent_summary=args.intent_summary,
        default_mode=default_tool_mode,
        default_purpose=args.tool_purpose,
        candidate_limit=getattr(args, "candidate_limit", 5),
    )
    runtime = runtime_context(
        args.work_id,
        workflow_name,
        runtime_mode=args.runtime_mode,
        target_dir=args.target_dir,
    )
    plan = execution_plan_context(
        args.work_id,
        workflow_name,
        required_contexts=args.required_context,
        required_environment=args.required_environment,
        next_commands=args.next_command,
        stop_conditions=args.stop_condition,
    )
    artifacts = [
        (
            "workflow-selection",
            context_dir / "workflow-selection.json",
            workflow_context,
            ".github/schemas/workflow-selection.schema.json",
        ),
        (
            "tool-selection",
            context_dir / "tool-selection.json",
            tool_context,
            ".github/schemas/tool-selection.schema.json",
        ),
        (
            "runtime-context",
            context_dir / "runtime-context.json",
            runtime,
            ".github/schemas/runtime-context.schema.json",
        ),
        (
            "execution-plan",
            context_dir / "execution-plan.json",
            plan,
            ".github/schemas/execution-plan.schema.json",
        ),
    ]
    written: list[str] = []
    for context_type, path, data, schema in artifacts:
        before_exists = path.exists()
        write_unless_exists(path, data, force=args.force)
        if args.force or not before_exists:
            written.append(relative_to_repo(repo_root, path))
        register_dispatcher_context(
            repo_root,
            work_dir,
            args.work_id,
            context_type=context_type,
            path=path,
            schema=schema,
        )
    manifest_path = context_dir / "context-manifest.json"
    return {
        "status": "ready"
        if not (workflow_context.get("human_check_required") or tool_context.get("human_check_required"))
        else "human-check-required",
        "work_id": args.work_id,
        "workflow": workflow_name,
        "contexts": [item[0] for item in artifacts],
        "written": written,
        "manifest_path": relative_to_repo(repo_root, manifest_path),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create Phase 3 Context First Dispatcher Context artifacts.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create workflow/tool/runtime/execution-plan Dispatcher Context.")
    add_init_arguments(init)
    init.set_defaults(handler=run_init)
    return parser


def add_init_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--intent-summary", default="")
    parser.add_argument("--tool", action="append", default=[], help="Tool name or name:mode:purpose. Can be repeated.")
    parser.add_argument("--tool-mode", choices=["read-only", "mutation", "local", "generated"], default="")
    parser.add_argument("--tool-purpose", default="workflow execution")
    parser.add_argument("--runtime-mode", default="standard")
    parser.add_argument("--target-dir", default="")
    parser.add_argument("--required-context", action="append", default=[])
    parser.add_argument("--required-environment", default="")
    parser.add_argument("--next-command", action="append", default=[])
    parser.add_argument("--stop-condition", action="append", default=[])
    parser.add_argument("--candidate-limit", type=int, default=5)
    parser.add_argument("--force", action="store_true")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
