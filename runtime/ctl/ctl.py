from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from time import perf_counter
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.constants.runtime_values import (  # noqa: E402
    MILLISECONDS_PER_SECOND,
    NON_NEGATIVE_INT_DEFAULT,
    SCHEMA_VERSION,
)
from runtime.common import gate_restart, registry_store  # noqa: E402
from runtime.ctl.ctl_help import (  # noqa: E402
    command_key,
    extension_key,
    explicit_search_terms,
    find_command,
    find_extension,
    find_help_item,
    format_arg_table,
    format_command_markdown,
    format_docs_for_list,
    format_extension_markdown,
    format_help_search_candidates,
    format_help_usage_warning,
    format_index_markdown,
    format_prerequisites_for_list,
    load_registry,
    normalize_command,
    normalize_search_value,
    registry_path,
    run_help_command,
    search_commands,
    search_extensions,
    search_score,
    text_blob,
)
from runtime.ctl.ctl_parser import build_parser  # noqa: E402
from runtime.common import find_repo_root, local_timestamp, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.paths import (  # noqa: E402
    DUCKDB_REFERENCE_CHECK_WORK_DIR,
    GENERATED_OPTIMIZED_CHUNKS,
    KNOWLEDGE_SOURCE_REPO,
    KNOWLEDGE_SOURCE_REPO_NAME,
)
from runtime.constants.schemas import ENVIRONMENT_SELECTION_SCHEMA  # noqa: E402
from runtime.constants.workspace import (  # noqa: E402
    context_file,
    context_path_pattern,
    implementation_path_pattern,
    manifest_path_for_work_dir,
    process_report_dir_for_work_dir,
    process_report_path_pattern,
    reports_path_pattern,
    requirements_path_pattern,
    test_evidence_path_pattern,
    work_dir_for_id,
    work_path_pattern,
)
from runtime.observability.command_event import RuntimeCommandEventContext  # noqa: E402
from runtime.observability.logger import RuntimeEventLogger  # noqa: E402
from runtime.observability.metrics import RuntimeMetricsCollector  # noqa: E402
from runtime.workflow import dispatcher_context  # noqa: E402
from runtime.workflow import flutter_multiplatform  # noqa: E402
from runtime.workflow import mcp_server_group  # noqa: E402
from runtime.workflow import workflow_doctor  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402

# Compatibility exports kept for older tests and callers that still access
# help/workflow helpers through runtime.ctl.ctl after the module split.
_COMPATIBILITY_EXPORTS = (
    command_key,
    extension_key,
    explicit_search_terms,
    find_command,
    find_extension,
    find_help_item,
    format_arg_table,
    format_command_markdown,
    format_docs_for_list,
    format_extension_markdown,
    format_help_search_candidates,
    format_help_usage_warning,
    format_index_markdown,
    format_prerequisites_for_list,
    load_registry,
    normalize_command,
    normalize_search_value,
    registry_path,
    run_help_command,
    search_commands,
    search_extensions,
    search_score,
    text_blob,
    implementation_path_pattern,
    process_report_path_pattern,
    reports_path_pattern,
    requirements_path_pattern,
    test_evidence_path_pattern,
    work_path_pattern,
    dispatcher_context,
    flutter_multiplatform,
    mcp_server_group,
    workflow_doctor,
)

ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def _github_knowledge_metrics_collector(
    repo_root: Path,
    *,
    work_id: str = "",
) -> RuntimeMetricsCollector:
    work_dir = work_dir_for_id(repo_root, work_id) if work_id else None
    return RuntimeMetricsCollector(
        repo_root=repo_root,
        work_dir=work_dir,
        workflow_id=work_id,
        workflow_name="/github-knowledge-maintenance",
        agent_name="aiwfctl",
    )


def _attach_work_dir_to_metrics(
    collector: RuntimeMetricsCollector,
    repo_root: Path,
    result: dict[str, Any],
) -> None:
    if collector.work_dir is not None:
        return
    work_id = str(result.get("work_id", "")).strip()
    if not work_id:
        return
    collector.workflow_id = work_id
    collector.work_dir = work_dir_for_id(repo_root, work_id)


def _record_github_knowledge_metrics_result(
    collector: RuntimeMetricsCollector,
    repo_root: Path,
    *,
    command_name: str,
    result: dict[str, Any],
) -> None:
    _attach_work_dir_to_metrics(collector, repo_root, result)
    status = str(result.get("status", "")).strip()
    if status == "human-check-required":
        collector.human_check_required(reason=f"{command_name} requires human check")
    for key in (
        "analysis_path",
        "report_path",
        "plan_path",
        "rebase_plan",
        "message_repair_plan",
        "rebase_replay_package",
        "message_repair_package",
        "rag_candidate",
    ):
        path = str(result.get(key, "")).strip()
        if path:
            collector.evidence_generated(path=path)
    collector.workflow_completed(
        save_evidence=False,
        metadata={"ctl_command": f"github-knowledge {command_name}", "status": status or "completed"},
    )
    if collector.work_dir is not None:
        evidence_status = "human-check-required" if status == "human-check-required" else "available"
        collector.save_evidence_summary(status=evidence_status)


def environment_registry_path(repo_root: Path) -> Path:
    return registry_store.registry_db_path(repo_root)


def load_environment_registry(repo_root: Path) -> dict[str, Any]:
    data = registry_store.load_environment_profiles(repo_root)
    if not isinstance(data, dict):
        raise ValueError("workflow environment profiles registry must be an object.")
    data.setdefault("environments", [])
    data.setdefault("profiles", [])
    data.setdefault("mappings", [])
    return data


def profile_key(profile: dict[str, Any]) -> str:
    return str(profile.get("id", "")).lower()


def environment_key(environment: dict[str, Any]) -> str:
    return str(environment.get("name", "")).lower()


def environment_names(registry: dict[str, Any]) -> list[str]:
    return [str(environment.get("name", "")) for environment in sorted(registry.get("environments", []), key=environment_key)]


def find_public_environment(registry: dict[str, Any], value: str) -> dict[str, Any]:
    target = value.strip().lower().lstrip("/")
    for environment in registry.get("environments", []):
        if target == str(environment.get("name", "")).lower().lstrip("/"):
            return environment
    raise KeyError(f"Unknown environment: {value}")


def find_public_environment_by_backend(registry: dict[str, Any], backend: str) -> dict[str, Any] | None:
    target = backend.strip().lower()
    for environment in registry.get("environments", []):
        if target == str(environment.get("backend", "")).lower():
            return environment
    return None


def find_environment_profile(registry: dict[str, Any], value: str) -> dict[str, Any]:
    target = value.strip().lower().lstrip("/")
    for profile in registry.get("profiles", []):
        names = [profile.get("id", ""), *profile.get("aliases", [])]
        if target in {str(name).lower().lstrip("/") for name in names}:
            return profile
    raise KeyError(f"Unknown environment profile: {value}")


def profile_by_id(registry: dict[str, Any], profile_id: str) -> dict[str, Any]:
    for profile in registry.get("profiles", []):
        if profile.get("id") == profile_id:
            return profile
    raise KeyError(f"Unknown environment profile id: {profile_id}")


def environment_mapping_matches(mapping: dict[str, Any], target: str) -> bool:
    normalized_target = target.strip().lower().lstrip("/")
    subject = str(mapping.get("subject", "")).strip().lower().lstrip("/")
    subject_type = mapping.get("subject_type", "")
    if subject_type in {"command", "extension", "subworkflow"}:
        return normalized_target == subject
    if subject_type == "keyword":
        words = {word.lower() for word in subject.replace("/", " ").replace("-", " ").split() if word.strip()}
        target_words = {word.lower() for word in normalized_target.replace("/", " ").replace("-", " ").split() if word.strip()}
        return bool(words & target_words)
    return False


def environment_gate_restart(status: str, target: str, *, work_id: str = "") -> dict[str, Any]:
    command = f"aiwfctl env select {target or '<environment-name>'}"
    if work_id:
        command = f"{command} --work-id {work_id}"
    elif status == "human-check-required":
        command = f"{command} --work-id <work-id>"
    return gate_restart.build_status_gate_restart(
        "environment-selection-gate",
        status=status,
        restart_reason="environment-selection",
        repair_command=command if status == "human-check-required" else "",
    )


def _select_environment_without_gate(registry: dict[str, Any], target: str) -> dict[str, Any]:
    try:
        environment = find_public_environment(registry, target)
        profile = profile_by_id(registry, environment["backend"])
        return {
            "status": "selected",
            "target": target,
            "environment": environment,
            "mapping": {
                "subject_type": "environment",
                "subject": environment["name"],
                "profiles": [environment["backend"]],
                "selection_reason": environment.get("purpose", ""),
                "docs": profile.get("docs", []),
            },
            "profiles": [profile],
            "human_check_required": False,
            "human_check_reasons": [],
        }
    except KeyError:
        pass

    matches = [mapping for mapping in registry.get("mappings", []) if environment_mapping_matches(mapping, target)]
    explicit_matches = [mapping for mapping in matches if mapping.get("subject_type") != "keyword"]
    if explicit_matches:
        matches = explicit_matches
    elif matches:
        return {
            "status": "human-check-required",
            "target": target,
            "mapping": None,
            "profiles": [profile_by_id(registry, profile_id) for mapping in matches for profile_id in mapping.get("profiles", [])],
            "candidate_mappings": matches,
            "candidate_environments": [
                find_public_environment_by_backend(registry, profile_id)
                for mapping in matches
                for profile_id in mapping.get("profiles", [])
                if find_public_environment_by_backend(registry, profile_id)
            ],
            "human_check_required": True,
            "human_check_reasons": [
                "環境名ではなくtool名またはkeywordに一致しました。利用者向けEnvironment名を指定してください。",
            ],
        }
    if not matches:
        return {
            "status": "human-check-required",
            "target": target,
            "mapping": None,
            "profiles": [],
            "human_check_required": True,
            "human_check_reasons": [
                "実行環境を特定できません。workflow名、extension名、または利用者向けEnvironment名を明示してください。",
                "Windows / WSL / Docker のどれを使うべきか判断できません。",
            ],
        }
    if len(matches) > 1:
        return {
            "status": "human-check-required",
            "target": target,
            "mapping": None,
            "profiles": [profile_by_id(registry, profile_id) for mapping in matches for profile_id in mapping.get("profiles", [])],
            "candidate_environments": [
                find_public_environment_by_backend(registry, profile_id)
                for mapping in matches
                for profile_id in mapping.get("profiles", [])
                if find_public_environment_by_backend(registry, profile_id)
            ],
            "candidate_mappings": matches,
            "human_check_required": True,
            "human_check_reasons": [
                "複数の環境候補に一致しました。推奨環境を人間確認してください。",
            ],
        }
    mapping = matches[0]
    profiles = [profile_by_id(registry, profile_id) for profile_id in mapping.get("profiles", [])]
    environment = find_public_environment_by_backend(registry, profiles[0]["id"]) if profiles else None
    return {
        "status": "selected",
        "target": target,
        "environment": environment,
        "mapping": mapping,
        "profiles": profiles,
        "human_check_required": False,
        "human_check_reasons": [],
    }


def select_environment(registry: dict[str, Any], target: str) -> dict[str, Any]:
    record = _select_environment_without_gate(registry, target)
    record["gate_restart"] = environment_gate_restart(str(record.get("status", "")), target)
    return record


def environment_selection_record(registry: dict[str, Any], target: str) -> dict[str, Any]:
    selection = select_environment(registry, target)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "workflow-environment-selection",
        "created_at": utc_now_iso(),
        **selection,
    }


def environment_backend(environment: dict[str, Any]) -> str:
    return str(environment.get("backend", ""))


def environment_profile(registry: dict[str, Any], environment: dict[str, Any]) -> dict[str, Any]:
    return profile_by_id(registry, environment_backend(environment))


def format_env_usage() -> str:
    return "\n".join(
        [
            "Environment Management",
            "",
            "Commands",
            "  list      利用可能な環境一覧を表示する",
            "  show      指定した環境の詳細を表示する",
            "  select    作業に使用する環境を選択する",
            "  check     select と同じ。実行前確認用の別名",
            "",
            "Examples",
            "  aiwfctl env list",
            "  aiwfctl env show gui-mode",
            "  aiwfctl env select gui-mode",
            "  aiwfctl env select web-svg --work-id issue-123",
            "",
            "Rule",
            "  Environment名は gui-mode / web-svg / docker のような目的ベース名を指定します。",
            "  windows-msys2-gui などのBackend名は表示情報であり、利用者が直接指定する名前ではありません。",
        ]
    ) + "\n"


def format_environment_list(registry: dict[str, Any]) -> str:
    lines = ["Available Environments", ""]
    for environment in sorted(registry.get("environments", []), key=environment_key):
        lines.extend(
            [
                str(environment.get("name", "")),
                f"  Backend : {environment.get('backend', '')}",
                f"  Purpose : {environment.get('purpose', '')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def format_public_environment_detail(registry: dict[str, Any], environment: dict[str, Any]) -> str:
    profile = environment_profile(registry, environment)
    recommended = "\n".join(f"  - {item}" for item in environment.get("recommended_for", [])) or "  - なし"
    tools = "\n".join(f"  - {item}" for item in profile.get("primary_tools", [])) or "  - なし"
    examples = "\n".join(f"  {item}" for item in environment.get("example_commands", [])) or "  なし"
    notes = "\n".join(f"  - {item}" for item in environment.get("notes", [])) or "  - なし"
    docs = "\n".join(f"  - {item}" for item in profile.get("docs", [])) or "  - なし"
    context_example = {
        "schema_version": SCHEMA_VERSION,
        "selected_at": "...",
        "selected_by": "dispatcher",
        "selection_mode": "manual",
        "environment": environment.get("name", ""),
        "backend": environment.get("backend", ""),
        "reason": environment.get("purpose", ""),
        "work_id": "issue-123",
    }
    return "\n".join(
        [
            f"Environment : {environment.get('name', '')}",
            "",
            "Backend",
            f"  {environment.get('backend', '')}",
            "",
            "Purpose",
            f"  {environment.get('purpose', '')}",
            "",
            "Recommended for",
            recommended,
            "",
            "Required Tools",
            tools,
            "",
            "Example Commands",
            examples,
            "",
            "Notes",
            notes,
            "",
            "Context Output",
            "",
            "Path",
            f"  {context_path_pattern('environment-selection.json')}",
            "",
            "JSON",
            *[f"  {line}" for line in json.dumps(context_example, ensure_ascii=False, indent=2).splitlines()],
            "",
            "Docs",
            docs,
        ]
    ) + "\n"


def format_unknown_environment(registry: dict[str, Any], target: str, record: dict[str, Any] | None = None) -> str:
    candidate_environments = []
    if record:
        candidate_environments = [
            environment for environment in record.get("candidate_environments", []) if isinstance(environment, dict)
        ]
    names = [str(environment.get("name", "")) for environment in candidate_environments] or environment_names(registry)
    lines = [
        "Error",
        f"  Unknown environment : {target}",
        "",
        "Reason",
        f"  {target} appears to be a tool/framework/workflow hint, not necessarily a public Environment name.",
        "",
        "Available Environments",
        "",
    ]
    if candidate_environments:
        for environment in candidate_environments:
            lines.extend(
                [
                    f"  {environment.get('name', '')}",
                    f"    Reason: {environment.get('purpose', '')}",
                ]
            )
    else:
        lines.extend(f"  {name}" for name in names)
    lines.extend(
        [
            "",
            "Action Required",
            "  Human Check:",
            f"    aiwfctl env select {names[0]} --work-id <work-id>" if names else "    aiwfctl env list",
        ]
    )
    if record and record.get("human_check_reasons"):
        lines.extend(["", "Human Check"])
        lines.extend(f"  - {reason}" for reason in record.get("human_check_reasons", []))
    return "\n".join(lines).rstrip() + "\n"


def run_environment_quick_checks(repo_root: Path, profile: dict[str, Any]) -> dict[str, Any]:
    runtime_windows_script = repo_root / "runtime" / "windows-script"
    path_entries = [Path(entry).resolve() for entry in os.environ.get("PATH", "").split(os.pathsep) if entry.strip()]
    runtime_windows_script_in_path = runtime_windows_script.resolve() in path_entries
    tool_names = ["aiwfctl"]
    for tool in profile.get("primary_tools", []):
        normalized = str(tool).strip()
        if normalized in {"Git", "uv", "Python", "Docker", "node", "npm"}:
            tool_names.append(normalized.lower() if normalized != "Python" else "python")
    tool_names = sorted(set(tool_names))
    checks = {
        "repo_root": str(repo_root),
        "runtime_windows_script": relative_to_repo(repo_root, runtime_windows_script),
        "runtime_windows_script_exists": runtime_windows_script.exists(),
        "runtime_windows_script_in_path": runtime_windows_script_in_path,
        "aiwfctl_cmd_exists": (runtime_windows_script / "aiwfctl.cmd").exists(),
        "workflow_doctor_exists": (repo_root / "runtime" / "workflow" / "workflow_doctor.py").exists(),
        "tool_presence": {tool: bool(shutil.which(tool)) for tool in tool_names},
        "path_hint": "aiwfctl path shell",
    }
    checks["status"] = (
        "ready"
        if checks["runtime_windows_script_exists"] and checks["aiwfctl_cmd_exists"] and checks["workflow_doctor_exists"]
        else "human-check-required"
    )
    return checks


def enrich_environment_selection(repo_root: Path, registry: dict[str, Any], record: dict[str, Any], *, work_id: str = "") -> dict[str, Any]:
    profiles = record.get("profiles", [])
    if profiles:
        record["initialization"] = {
            "status": "checked",
            "scope": "repo-local current session",
            "checks": run_environment_quick_checks(repo_root, profiles[0]),
        }
    else:
        record["initialization"] = {
            "status": "human-check-required",
            "scope": "repo-local current session",
            "checks": {},
        }
    if not record.get("environment") and profiles:
        record["environment"] = find_public_environment_by_backend(registry, str(profiles[0].get("id", "")))
    record["workflow_context"] = {
        "status": "pending" if work_id else "not-written",
        "path": f"work/{work_id}/context/environment-selection.json" if work_id else "",
        "reason": "" if work_id else "--work-id が未指定のため固定contextは書き込みません。",
    }
    return record


def environment_context_record(
    record: dict[str, Any],
    *,
    work_id: str,
    selected_by: str = "dispatcher",
    selection_mode: str = "manual",
) -> dict[str, Any]:
    environment = record.get("environment") or {}
    profiles = record.get("profiles", [])
    profile = profiles[0] if profiles else {}
    mapping = record.get("mapping") or {}
    backend = str(environment.get("backend", "") or profile.get("id", ""))
    status = str(record.get("status", ""))
    mode = "human-check" if record.get("human_check_required") else selection_mode
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "environment-selection-context",
        "selected_at": record.get("created_at", utc_now_iso()),
        "selected_by": selected_by,
        "selection_mode": mode,
        "environment": str(environment.get("name", record.get("target", ""))),
        "backend": backend,
        "reason": str(mapping.get("selection_reason", "")),
        "work_id": work_id,
        "status": status,
        "human_check_required": bool(record.get("human_check_required", False)),
        "human_check_reasons": record.get("human_check_reasons", []),
        "recommended_for": environment.get("recommended_for", []),
        "required_tools": profile.get("primary_tools", []),
        "preflight_profile": profile.get("preflight_profile", ""),
        "context_path": f"work/{work_id}/context/environment-selection.json",
        "source": {
            "registry": registry_store.REGISTRY_DB_PATH.as_posix(),
            "schema": ENVIRONMENT_SELECTION_SCHEMA,
        },
        "initialization": record.get("initialization", {}),
        "gate_restart": record.get("gate_restart")
        or environment_gate_restart(status, str(environment.get("name", record.get("target", ""))), work_id=work_id),
    }


def environment_context_warnings(existing: Any, new_context: dict[str, Any]) -> list[str]:
    if existing is None or existing == {}:
        return []
    if not isinstance(existing, dict):
        return ["既存のenvironment-selection.jsonがJSON objectではありません。上書き前に内容確認が必要です。"]
    warnings = []
    if existing.get("work_id") and existing.get("work_id") != new_context.get("work_id"):
        warnings.append(
            f"既存contextのwork_id `{existing.get('work_id')}` と今回のwork_id `{new_context.get('work_id')}` が異なります。"
        )
    if existing.get("environment") and existing.get("environment") != new_context.get("environment"):
        warnings.append(
            f"既存contextのenvironment `{existing.get('environment')}` と今回のenvironment `{new_context.get('environment')}` が異なります。"
        )
    if existing.get("backend") and existing.get("backend") != new_context.get("backend"):
        warnings.append(
            f"既存contextのbackend `{existing.get('backend')}` と今回のbackend `{new_context.get('backend')}` が異なります。"
        )
    return warnings


def format_environment_profile(profile: dict[str, Any]) -> str:
    docs = "\n".join(f"    - {doc}" for doc in profile.get("docs", [])) or "    - なし"
    applies = "\n".join(f"    - {item}" for item in profile.get("applies_when", [])) or "    - なし"
    tools = ", ".join(profile.get("primary_tools", [])) or "なし"
    verification = "\n".join(f"    - {item}" for item in profile.get("verification", [])) or "    - なし"
    human = "\n".join(f"    - {item}" for item in profile.get("human_check_required_when", [])) or "    - なし"
    lines = [
        f"{profile.get('id', '')}",
        f"  名称: {profile.get('title', '')}",
        f"  環境: {profile.get('environment', '')}",
        f"  Shell: {profile.get('shell', '')}",
        f"  OS: {profile.get('os', '')}",
        f"  概要: {profile.get('summary', '')}",
        f"  主要ツール: {tools}",
        f"  実行コマンド: {profile.get('run_command', '')}",
        f"  preflight: {profile.get('preflight_profile', 'なし') or 'なし'}",
        "  該当条件:",
        applies,
        "  実行前確認:",
        verification,
        "  Human Check条件:",
        human,
        "  docs:",
        docs,
    ]
    return "\n".join(lines)


def format_environment_selection(record: dict[str, Any]) -> str:
    environment = record.get("environment") or {}
    profiles = record.get("profiles", [])
    backend = str(environment.get("backend", ""))
    if not backend and profiles:
        backend = str(profiles[0].get("id", ""))
    mapping = record.get("mapping") or {}
    if record.get("human_check_required"):
        return format_environment_human_check(record)
    context = record.get("workflow_context", {})
    init = record.get("initialization", {})
    checks = init.get("checks", {}) if isinstance(init, dict) else {}
    lines = [
        f"Selected Environment : {environment.get('name', record.get('target', ''))}",
        f"Backend              : {backend}",
        f"Reason               : {mapping.get('selection_reason', '')}",
        f"Work ID              : {record.get('work_id', '') or 'なし'}",
        f"Workflow Context     : {context.get('path', '') or '未登録'}",
        "",
        "Initialization",
        f"  status              : {init.get('status', 'not-run') if isinstance(init, dict) else 'not-run'}",
        f"  runtime/windows-script exists: {str(checks.get('runtime_windows_script_exists', False)).lower()}",
        f"  runtime/windows-script in PATH: {str(checks.get('runtime_windows_script_in_path', False)).lower()}",
        f"  aiwfctl.cmd exists  : {str(checks.get('aiwfctl_cmd_exists', False)).lower()}",
        f"  doctor script exists: {str(checks.get('workflow_doctor_exists', False)).lower()}",
    ]
    warnings = context.get("warnings", []) if isinstance(context, dict) else []
    if warnings:
        lines.extend(["", "Warnings"])
        lines.extend(f"  - {warning}" for warning in warnings)
    return "\n".join(lines).rstrip() + "\n"


def format_environment_human_check(record: dict[str, Any]) -> str:
    lines = [
        "Environment Human Check Required",
        "",
        f"Target : {record.get('target', '')}",
        f"Status : {record.get('status', '')}",
        "",
        "Reasons",
    ]
    lines.extend(f"  - {reason}" for reason in record.get("human_check_reasons", []))
    candidates = [
        environment for environment in record.get("candidate_environments", []) if isinstance(environment, dict)
    ]
    if candidates:
        lines.extend(["", "Candidate Environments"])
        for environment in candidates:
            lines.extend(
                [
                    f"  {environment.get('name', '')}",
                    f"    Backend : {environment.get('backend', '')}",
                    f"    Purpose : {environment.get('purpose', '')}",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def environment_selection_markdown(record: dict[str, Any]) -> str:
    return format_environment_selection(record)


def write_environment_selection(
    repo_root: Path,
    record: dict[str, Any],
    *,
    work_id: str = "",
    output: str = "",
    selected_by: str = "dispatcher",
    selection_mode: str = "manual",
) -> list[str]:
    written: list[str] = []
    if work_id:
        record["work_id"] = work_id
        work_path = work_dir_for_id(repo_root, work_id)
        base = process_report_dir_for_work_dir(work_path)
        stamp = local_timestamp()
        json_path = base / f"environment-selection-{stamp}.json"
        md_path = base / f"environment-selection-{stamp}.md"
        context_path = context_file(work_path, "environment-selection.json")
        context = environment_context_record(
            record,
            work_id=work_id,
            selected_by=selected_by,
            selection_mode=selection_mode,
        )
        existing_context = read_json(context_path, default={}) if context_path.exists() else {}
        warnings = environment_context_warnings(existing_context, context)
        if warnings:
            context["warnings"] = warnings
        record.setdefault("workflow_context", {})
        record["workflow_context"].update(
            {
                "status": "written",
                "path": relative_to_repo(repo_root, context_path),
                "schema": ENVIRONMENT_SELECTION_SCHEMA,
                "warnings": warnings,
            }
        )
        record["context"] = context
        write_json(json_path, record)
        write_json(context_path, context)
        manifest = register_context(
            repo_root,
            work_dir_for_id(repo_root, work_id),
            work_id=work_id,
            context_type="environment-selection",
            path=context_path,
            required=True,
            generated_by="environment-dispatcher",
            owner="dispatcher",
            schema=ENVIRONMENT_SELECTION_SCHEMA,
            status="available" if not context.get("human_check_required") else "human-check-required",
        )
        record["context_manifest"] = {
            "path": relative_to_repo(repo_root, manifest_path_for_work_dir(work_dir_for_id(repo_root, work_id))),
            "context_count": len(manifest.get("contexts", [])),
        }
        write_json(json_path, record)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(environment_selection_markdown(record), encoding="utf-8")
        written.extend(
            [
                relative_to_repo(repo_root, json_path),
                relative_to_repo(repo_root, md_path),
                relative_to_repo(repo_root, context_path),
                relative_to_repo(repo_root, manifest_path_for_work_dir(work_dir_for_id(repo_root, work_id))),
            ]
        )
    if output:
        output_path = Path(output)
        output_path = output_path if output_path.is_absolute() else repo_root / output_path
        if output_path.suffix.lower() == ".json":
            write_json(output_path, record)
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(environment_selection_markdown(record), encoding="utf-8")
        written.append(relative_to_repo(repo_root, output_path))
    return written


def repo_root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve() if args.repo_root else find_repo_root()


def colorize_warning(line: str, color: bool = False) -> str:
    if not color:
        return line
    return f"{ANSI_YELLOW}{line}{ANSI_RESET}"


def should_use_color(stream: Any = sys.stdout) -> bool:
    color_mode = os.environ.get("AIWFCTL_COLOR", "").strip().lower()
    if color_mode in {"always", "1", "true", "yes"}:
        return True
    if color_mode in {"never", "0", "false", "no"}:
        return False
    if os.environ.get("NO_COLOR") is not None:
        return False
    return bool(getattr(stream, "isatty", lambda: False)())


def format_root_usage_warning(color: bool = False) -> str:
    return "\n".join(
        [
            colorize_warning("警告: aiwfctl の後続修飾子が指定されていません。", color),
            "",
            "次のように、実行したい操作を指定してください。",
            "",
            "使用例:",
            "  aiwfctl help list",
            "  aiwfctl help show /vscode-environment",
            "  aiwfctl help search svg gui",
            "  aiwfctl env list",
            "  aiwfctl env select web-svg",
            "  aiwfctl env select gui-mode",
            "  aiwfctl context init --work-id issue-123 --workflow /docs-sync",
            "  aiwfctl knowledge search --query \"PyQt GUI smoke test\"",
            "  aiwfctl sdk analyze --work-id issue-123",
            "  aiwfctl flutter analyze --work-id issue-123",
            "  aiwfctl doctor",
            "  aiwfctl path check",
            "  aiwfctl path register",
            "  aiwfctl path shell",
            "",
            "まず一覧を見たい場合:",
            "  aiwfctl help list",
            "",
            "PATH登録と更新済みPowerShell session起動を行う場合:",
            "  aiwfctl path shell",
        ]
    ) + "\n"


def format_knowledge_usage() -> str:
    source_repo = KNOWLEDGE_SOURCE_REPO.as_posix()
    optimized_chunks = GENERATED_OPTIMIZED_CHUNKS.as_posix()
    reference_work_dir = DUCKDB_REFERENCE_CHECK_WORK_DIR.as_posix()
    return "\n".join(
        [
            "Knowledge Management",
            "",
            "Usage:",
            "  aiwfctl knowledge init",
            "  aiwfctl knowledge source status",
            "  aiwfctl knowledge source clone",
            "  aiwfctl knowledge source pull",
            "  aiwfctl knowledge source import-local --clean",
            f"  aiwfctl knowledge rebuild --source-repo {source_repo} --reset",
            f"  aiwfctl knowledge migrate --source {optimized_chunks}",
            f"  aiwfctl knowledge ingest --file {optimized_chunks}/<chunk-id>.json",
            "  aiwfctl knowledge search --query \"PyQt GUI smoke test\" --limit 10",
            f"  aiwfctl knowledge export-context --query \"PyQt GUI smoke test\" --output {context_path_pattern('knowledge.json')}",
            f"  aiwfctl knowledge verify --query workflow --query runtime --work-dir {reference_work_dir} --work-id duckdb-reference-check",
            "",
            "DuckDBファイルは生成read modelです。source of truthはfile-based RAG artifactです。",
            f"外部Knowledge正本は {KNOWLEDGE_SOURCE_REPO_NAME} を {source_repo} にcloneして使います。",
        ]
    ) + "\n"


def format_knowledge_result(result: dict[str, Any]) -> str:
    artifact_type = result.get("artifact_type", "")
    if artifact_type == "rag-knowledge-source":
        source = result.get("source_repository", {}) if isinstance(result.get("source_repository"), dict) else {}
        return "\n".join(
            [
                "Knowledge Source Repository",
                "",
                f"Status : {result.get('status', '')}",
                f"Action : {result.get('action', '')}",
                f"Path   : {source.get('path', '')}",
                f"URL    : {source.get('url', '')}",
                f"Git    : {source.get('is_git_repo', False)}",
                f"Branch : {source.get('branch', '')}",
                f"Commit : {source.get('commit', '')}",
                f"Dirty  : {source.get('dirty', False)}",
                f"Imported Files : {result.get('imported_file_count', '')}",
            ]
        ).rstrip() + "\n"
    if artifact_type == "rag-duckdb-search-result":
        lines = [
            "Knowledge Search",
            "",
            f"Status          : {result.get('status', '')}",
            f"Query           : {result.get('query', '')}",
            f"Candidate Count : {result.get('candidate_count', 0)}",
            f"Result Count    : {result.get('result_count', 0)}",
            "",
            "Results",
        ]
        results = result.get("results", [])
        if not results:
            lines.append("  - なし")
        for item in results:
            lines.extend(
                [
                    f"  - {item.get('knowledge_id', '')}",
                    f"    title: {item.get('title', '')}",
                    f"    score: {item.get('final_score', 0)}",
                    f"    source_path: {item.get('source_path', '')}",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"
    if artifact_type == "rag-duckdb-context-export":
        return "\n".join(
            [
                "Knowledge Context Export",
                "",
                f"Status          : {result.get('status', '')}",
                f"Output          : {result.get('output', '')}",
                f"Candidate Count : {result.get('candidate_count', 0)}",
                f"Result Count    : {result.get('result_count', 0)}",
            ]
        ).rstrip() + "\n"
    if artifact_type in {"rag-duckdb-migration-summary", "rag-duckdb-rebuild-summary"}:
        return "\n".join(
            [
                "Knowledge Rebuild" if artifact_type == "rag-duckdb-rebuild-summary" else "Knowledge Migration",
                "",
                f"Status          : {result.get('status', '')}",
                f"Source          : {result.get('source', '')}",
                f"Source Repo     : {(result.get('source_repository') or {}).get('path', '') if isinstance(result.get('source_repository'), dict) else ''}",
                f"Target Files    : {result.get('target_file_count', 0)}",
                f"Registered      : {result.get('registered_count', 0)}",
                f"Updated         : {result.get('updated_count', 0)}",
                f"Skipped         : {result.get('skipped_count', 0)}",
                f"Failed          : {result.get('failed_count', 0)}",
                f"Error Log       : {result.get('error_log', '') or 'なし'}",
            ]
        ).rstrip() + "\n"
    if artifact_type == "rag-duckdb-reference-check":
        lines = [
            "Knowledge Reference Check",
            "",
            f"Status       : {result.get('status', '')}",
            f"Output       : {result.get('output', '')}",
            f"Manifest     : {result.get('context_manifest', '') or '未登録'}",
            f"Query Count  : {result.get('query_count', 0)}",
            f"Passed       : {result.get('passed_count', 0)}",
            f"Failed       : {result.get('failed_count', 0)}",
            "",
            "Checks",
        ]
        for check in result.get("checks", []):
            lines.extend(
                [
                    f"  - {check.get('query', '')}",
                    f"    status: {check.get('status', '')}",
                    f"    results: {check.get('result_count', 0)}",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"
    return json.dumps(result, ensure_ascii=False, indent=2) + "\n"


def _run_impl(args: argparse.Namespace, color: bool = False) -> tuple[int, str]:
    from runtime.ctl import ctl_dispatch

    return ctl_dispatch.run_impl(args, helpers=sys.modules[__name__], color=color)


def _elapsed_ms(started: float) -> int:
    return max(int((perf_counter() - started) * MILLISECONDS_PER_SECOND), NON_NEGATIVE_INT_DEFAULT)


def run(args: argparse.Namespace, color: bool = False) -> tuple[int, str]:
    repo_root = repo_root_from_args(args)
    event_context = RuntimeCommandEventContext.from_args(args, repo_root)
    begin_trace = args.command == "trace" and getattr(args, "trace_command", "") == "begin"
    trace_id = str(getattr(args, "trace_id", "") or "") if begin_trace else ""
    event_logger = RuntimeEventLogger(
        repo_root=repo_root,
        component="ctl",
        workflow=event_context.workflow,
        trace_id=trace_id or None,
        use_active_trace=not (begin_trace and bool(getattr(args, "force", False))),
    )
    setattr(args, "_runtime_trace_id", event_logger.trace_id)
    started = perf_counter()
    started_event = event_context.emit_started(event_logger)
    setattr(args, "_runtime_sequence", started_event.get("sequence", 0))
    try:
        code, output = _run_impl(args, color=color)
    except Exception as exc:
        event_context.emit_failed(event_logger, exc, duration_ms=_elapsed_ms(started))
        raise
    event_context.emit_completed(event_logger, code=code, output=output, duration_ms=_elapsed_ms(started))
    return code, output


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    code, output = run(args, color=should_use_color(sys.stdout))
    print(output, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
