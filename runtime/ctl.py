from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from runtime import registry_store  # noqa: E402
from runtime.common import find_repo_root, local_timestamp, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.rag import duckdb_store  # noqa: E402
from runtime.workflow import flutter_multiplatform  # noqa: E402
from runtime.workflow import mcp_server_group  # noqa: E402
from runtime.workflow import sdk_analysis  # noqa: E402
from runtime.workflow import system_integration  # noqa: E402
from runtime.workflow import workflow_doctor  # noqa: E402
from runtime.workflow import dispatcher_context  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402

ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def registry_path(repo_root: Path) -> Path:
    return registry_store.registry_db_path(repo_root)


def environment_registry_path(repo_root: Path) -> Path:
    return registry_store.registry_db_path(repo_root)


def load_registry(repo_root: Path) -> dict[str, Any]:
    data = registry_store.load_workflow_help(repo_root)
    if not isinstance(data, dict):
        raise ValueError("workflow help registry must be an object.")
    data.setdefault("commands", [])
    data.setdefault("extensions", [])
    return data


def load_environment_registry(repo_root: Path) -> dict[str, Any]:
    data = registry_store.load_environment_profiles(repo_root)
    if not isinstance(data, dict):
        raise ValueError("workflow environment profiles registry must be an object.")
    data.setdefault("environments", [])
    data.setdefault("profiles", [])
    data.setdefault("mappings", [])
    return data


def normalize_command(value: str) -> str:
    value = value.strip()
    if value and not value.startswith("/"):
        value = f"/{value}"
    return value


def command_key(command: dict[str, Any]) -> str:
    return str(command.get("command", "")).lower()


def extension_key(extension: dict[str, Any]) -> str:
    return str(extension.get("name", "")).lower()


def find_command(registry: dict[str, Any], value: str) -> dict[str, Any]:
    target = normalize_command(value).lower()
    for command in registry.get("commands", []):
        names = [command.get("command", ""), *command.get("aliases", [])]
        if target in {str(name).lower() for name in names}:
            return command
    raise KeyError(f"Unknown workflow command: {value}")


def find_extension(registry: dict[str, Any], value: str) -> dict[str, Any]:
    target = value.strip().lower().lstrip("/")
    for extension in registry.get("extensions", []):
        names = [extension.get("name", ""), *extension.get("aliases", [])]
        normalized_names = {str(name).lower().lstrip("/") for name in names}
        if target in normalized_names:
            return extension
    raise KeyError(f"Unknown workflow extension: {value}")


def find_help_item(registry: dict[str, Any], value: str) -> tuple[str, dict[str, Any]]:
    try:
        return "command", find_command(registry, value)
    except KeyError:
        return "extension", find_extension(registry, value)


def text_blob(command: dict[str, Any]) -> str:
    return json.dumps(command, ensure_ascii=False, sort_keys=True).lower()


def normalize_search_value(value: str) -> str:
    return " ".join(value.strip().lower().split())


def explicit_search_terms(item: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    for key in ["search_terms", "_search_terms"]:
        raw_terms = item.get(key, [])
        if not isinstance(raw_terms, list):
            continue
        for raw in raw_terms:
            if isinstance(raw, str):
                term = normalize_search_value(raw)
            elif isinstance(raw, dict):
                term = normalize_search_value(str(raw.get("term", "")))
            else:
                term = ""
            if term:
                terms.append(term)
    return terms


def search_score(item: dict[str, Any], keywords: list[str]) -> int:
    terms = [normalize_search_value(term) for term in keywords if term.strip()]
    if not terms:
        return 1
    query = normalize_search_value(" ".join(terms))
    blob = text_blob(item)
    score = 0
    if all(term in blob for term in terms):
        score += 40 + (10 * len(terms))
    for search_term in explicit_search_terms(item):
        if search_term == query:
            score += 120
        elif query and (query in search_term or search_term in query):
            score += 90
        elif all(term in search_term for term in terms):
            score += 75
        else:
            score += 25 * sum(1 for term in terms if term in search_term)
    return score


def search_commands(registry: dict[str, Any], keywords: list[str]) -> list[dict[str, Any]]:
    if not [term for term in keywords if term.strip()]:
        return sorted(registry.get("commands", []), key=command_key)
    matches: list[tuple[int, dict[str, Any]]] = []
    for command in registry.get("commands", []):
        score = search_score(command, keywords)
        if score > 0:
            matches.append((score, command))
    return [item for _, item in sorted(matches, key=lambda entry: (-entry[0], command_key(entry[1])))]


def search_extensions(registry: dict[str, Any], keywords: list[str]) -> list[dict[str, Any]]:
    if not [term for term in keywords if term.strip()]:
        return sorted(registry.get("extensions", []), key=extension_key)
    matches: list[tuple[int, dict[str, Any]]] = []
    for extension in registry.get("extensions", []):
        score = search_score(extension, keywords)
        if score > 0:
            matches.append((score, extension))
    return [item for _, item in sorted(matches, key=lambda entry: (-entry[0], extension_key(entry[1])))]


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


def select_environment(registry: dict[str, Any], target: str) -> dict[str, Any]:
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


def environment_selection_record(registry: dict[str, Any], target: str) -> dict[str, Any]:
    selection = select_environment(registry, target)
    return {
        "schema_version": "1.0",
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
        "schema_version": "1.0",
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
            "  work/<work-id>/context/environment-selection.json",
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
    runtime_tools = repo_root / "runtime" / "tools"
    path_entries = [Path(entry).resolve() for entry in os.environ.get("PATH", "").split(os.pathsep) if entry.strip()]
    runtime_tools_in_path = runtime_tools.resolve() in path_entries
    tool_names = ["aiwfctl"]
    for tool in profile.get("primary_tools", []):
        normalized = str(tool).strip()
        if normalized in {"Git", "uv", "Python", "Docker", "node", "npm"}:
            tool_names.append(normalized.lower() if normalized != "Python" else "python")
    tool_names = sorted(set(tool_names))
    checks = {
        "repo_root": str(repo_root),
        "runtime_tools": relative_to_repo(repo_root, runtime_tools),
        "runtime_tools_exists": runtime_tools.exists(),
        "runtime_tools_in_path": runtime_tools_in_path,
        "aiwfctl_cmd_exists": (runtime_tools / "aiwfctl.cmd").exists(),
        "workflow_doctor_exists": (repo_root / "runtime" / "workflow" / "workflow_doctor.py").exists(),
        "tool_presence": {tool: bool(shutil.which(tool)) for tool in tool_names},
        "path_hint": "aiwfctl path shell",
    }
    checks["status"] = "ready" if checks["runtime_tools_exists"] and checks["aiwfctl_cmd_exists"] and checks["workflow_doctor_exists"] else "human-check-required"
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
        "schema_version": "1.0",
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
            "schema": ".github/schemas/environment-selection.schema.json",
        },
        "initialization": record.get("initialization", {}),
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
        f"  runtime/tools exists: {str(checks.get('runtime_tools_exists', False)).lower()}",
        f"  runtime/tools in PATH: {str(checks.get('runtime_tools_in_path', False)).lower()}",
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
        base = repo_root / "work" / work_id / "process-report"
        stamp = local_timestamp()
        json_path = base / f"environment-selection-{stamp}.json"
        md_path = base / f"environment-selection-{stamp}.md"
        context_path = repo_root / "work" / work_id / "context" / "environment-selection.json"
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
                "schema": ".github/schemas/environment-selection.schema.json",
                "warnings": warnings,
            }
        )
        record["context"] = context
        write_json(json_path, record)
        write_json(context_path, context)
        manifest = register_context(
            repo_root,
            repo_root / "work" / work_id,
            work_id=work_id,
            context_type="environment-selection",
            path=context_path,
            required=True,
            generated_by="environment-dispatcher",
            owner="dispatcher",
            schema=".github/schemas/environment-selection.schema.json",
            status="available" if not context.get("human_check_required") else "human-check-required",
        )
        record["context_manifest"] = {
            "path": relative_to_repo(repo_root, repo_root / "work" / work_id / "context" / "context-manifest.json"),
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
                relative_to_repo(repo_root, repo_root / "work" / work_id / "context" / "context-manifest.json"),
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


def format_arg_table(title: str, args: list[dict[str, Any]]) -> str:
    lines = [f"### {title}", "", "| 引数 | 必須 | 設定する内容 | 例 |", "| --- | --- | --- | --- |"]
    if not args:
        lines.append("| なし | - | - | - |")
        return "\n".join(lines)
    for item in args:
        required = "yes" if item.get("required") else "no"
        examples = "<br>".join(str(value) for value in item.get("examples", [])) or "-"
        lines.append(
            "| `{}` | {} | {} | {} |".format(
                item.get("name", ""),
                required,
                str(item.get("description", "")).replace("\n", "<br>"),
                examples,
            )
        )
    return "\n".join(lines)


def format_command_markdown(command: dict[str, Any], repo_root: Path) -> str:
    docs = command.get("docs", [])
    doc_lines = "\n".join(f"- `{doc}`" for doc in docs) or "- なし"
    examples = "\n".join(f"```text\n{example}\n```" for example in command.get("examples", [])) or "なし"
    details = "\n".join(f"- {item}" for item in command.get("details", [])) or "- なし"
    prerequisites = "\n".join(f"- {item}" for item in command.get("prerequisites", [])) or "- なし"
    related = "\n".join(f"- `{item}`" for item in command.get("related_runtime", [])) or "- なし"
    lines = [
        f"## {command.get('command', '')}",
        "",
        f"- workflow: `{command.get('workflow', '')}`",
        f"- skill: `{command.get('skill', '')}`",
        f"- prompt: `{command.get('prompt_path', '')}`",
        f"- skill file: `{command.get('skill_path', '')}`",
        "",
        "### 概要",
        "",
        str(command.get("overview", "")),
        "",
        "### 前提条件",
        "",
        prerequisites,
        "",
        "### 処理の詳細",
        "",
        details,
        "",
        format_arg_table("必須/任意引数", command.get("arguments", [])),
        "",
        "### 使用例",
        "",
        examples,
        "",
        "### 関連runtime",
        "",
        related,
        "",
        "### 関連docs",
        "",
        doc_lines,
    ]
    source = registry_path(repo_root)
    lines.extend(["", f"_source: `{relative_to_repo(repo_root, source)}`_"])
    return "\n".join(lines).rstrip()


def format_extension_markdown(extension: dict[str, Any], repo_root: Path) -> str:
    docs = extension.get("docs", [])
    doc_lines = "\n".join(f"- `{doc}`" for doc in docs) or "- なし"
    examples = "\n".join(f"```text\n{example}\n```" for example in extension.get("examples", [])) or "なし"
    details = "\n".join(f"- {item}" for item in extension.get("details", [])) or "- なし"
    prerequisites = "\n".join(f"- {item}" for item in extension.get("prerequisites", [])) or "- なし"
    related = "\n".join(f"- `{item}`" for item in extension.get("related_runtime", [])) or "- なし"
    parents = "\n".join(f"- `{item}`" for item in extension.get("parent_workflows", [])) or "- なし"
    prefixes = "\n".join(f"- `{item}`" for item in extension.get("prefixes", [])) or "- なし"
    lines = [
        f"## {extension.get('name', '')}",
        "",
        "- 種別: workflow extension",
        f"- standalone command: `{str(extension.get('standalone_command', False)).lower()}`",
        f"- trigger: `{extension.get('trigger', '')}`",
        f"- input directory: `{extension.get('input_directory', '')}`",
        f"- output: `{extension.get('output', '')}`",
        "",
        "### 概要",
        "",
        str(extension.get("overview", "")),
        "",
        "### 前提条件",
        "",
        prerequisites,
        "",
        "### 親workflow",
        "",
        parents,
        "",
        "### 対応prefix",
        "",
        prefixes,
        "",
        "### 処理の詳細",
        "",
        details,
        "",
        "### 使用例",
        "",
        examples,
        "",
        "### 関連runtime",
        "",
        related,
        "",
        "### 関連docs",
        "",
        doc_lines,
    ]
    source = registry_path(repo_root)
    lines.extend(["", f"_source: `{relative_to_repo(repo_root, source)}`_"])
    return "\n".join(lines).rstrip()


def format_prerequisites_for_list(prerequisites: list[str]) -> str:
    if not prerequisites:
        return "  前提: なし"
    return "\n".join(["  前提:", *(f"    - {item}" for item in prerequisites)])


def format_docs_for_list(docs: list[str]) -> str:
    if not docs:
        return "  docs: なし"
    return "\n".join(["  docs:", *(f"    - {item}" for item in docs)])


def format_index_markdown(
    registry: dict[str, Any],
    repo_root: Path,
    commands: list[dict[str, Any]] | None = None,
    extensions: list[dict[str, Any]] | None = None,
) -> str:
    commands = commands if commands is not None else sorted(registry.get("commands", []), key=command_key)
    extensions = extensions if extensions is not None else sorted(registry.get("extensions", []), key=extension_key)
    rows = ["| Command | 概要 | 必須引数 |", "| --- | --- | --- |"]
    for command in commands:
        required = [
            str(arg.get("name", ""))
            for arg in command.get("arguments", [])
            if arg.get("required")
        ]
        rows.append(
            "| `{}` | {} | {} |".format(
                command.get("command", ""),
                command.get("overview", ""),
                ", ".join(f"`{item}`" for item in required) or "なし",
            )
        )
    extension_rows = ["| Extension | 概要 | Trigger |", "| --- | --- | --- |"]
    for extension in extensions:
        extension_rows.append(
            "| `{}` | {} | `{}` |".format(
                extension.get("name", ""),
                extension.get("overview", ""),
                extension.get("trigger", ""),
            )
        )
    lines = [
        "# AI Workflow Help",
        "",
        str(registry.get("description", "")),
        "",
        "## Commands",
        "",
        *rows,
        "",
        "## Workflow Extensions",
        "",
        *extension_rows,
        "",
        "## Details",
        "",
    ]
    for command in commands:
        lines.append(format_command_markdown(command, repo_root))
        lines.append("")
    for extension in extensions:
        lines.append(format_extension_markdown(extension, repo_root))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_help_search_candidates(
    commands: list[dict[str, Any]],
    extensions: list[dict[str, Any]],
    *,
    keywords: list[str],
) -> str:
    query = " ".join(keyword for keyword in keywords if str(keyword).strip())
    lines = [
        "Workflow Help Search Candidates",
        "",
        f"Query: {query}",
        "",
    ]
    if commands:
        lines.append("Commands")
        for index, command in enumerate(commands, start=1):
            name = str(command.get("command", ""))
            lines.extend(
                [
                    f"{index}. {name}",
                    f"   overview: {command.get('overview', '')}",
                    f"   show: aiwfctl help show {name}",
                ]
            )
        lines.append("")
    if extensions:
        lines.append("Extensions")
        for index, extension in enumerate(extensions, start=1):
            name = str(extension.get("name", ""))
            lines.extend(
                [
                    f"{index}. {name}",
                    f"   overview: {extension.get('overview', '')}",
                    f"   show: aiwfctl help show {name}",
                ]
            )
        lines.append("")
    lines.extend(
        [
            "Next:",
            "  Run `aiwfctl help show <candidate>` to open the full help.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


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
    env_select.add_argument("--work-id", default="", help="Write selection artifacts under work/<work-id>/process-report/.")
    env_select.add_argument("--output", default="", help="Write selection artifact to an explicit .md or .json path.")
    env_select.add_argument("--selected-by", choices=["dispatcher", "human", "workflow"], default="dispatcher")
    env_select.add_argument("--selection-mode", choices=["manual", "auto", "human-check"], default="manual")

    env_check = env_sub.add_parser("check", help="Alias of env select for pre-execution checks.")
    env_check.add_argument("target")
    env_check.add_argument("--json", action="store_true", help="Print selection as JSON.")
    env_check.add_argument("--work-id", default="", help="Write selection artifacts under work/<work-id>/process-report/.")
    env_check.add_argument("--output", default="", help="Write selection artifact to an explicit .md or .json path.")
    env_check.add_argument("--selected-by", choices=["dispatcher", "human", "workflow"], default="dispatcher")
    env_check.add_argument("--selection-mode", choices=["manual", "auto", "human-check"], default="manual")

    context_cmd = sub.add_parser("context", help="Create and inspect Context First Dispatcher Context.")
    context_sub = context_cmd.add_subparsers(dest="context_command")
    context_init = context_sub.add_parser("init", help="Create workflow/tool/runtime/execution-plan context.")
    dispatcher_context.add_init_arguments(context_init)
    context_init.add_argument("--json", action="store_true", help="Print result as JSON.")

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
    sdk_analyze.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    sdk_analyze.add_argument(
        "--knowledge-dir",
        default="",
        help="Knowledge JSON output directory. Default: work/db/ariadne-knowledge-platform/rag/jsonized",
    )
    sdk_analyze.add_argument("--no-knowledge", action="store_true", help="Do not write Knowledge JSON.")
    sdk_analyze.add_argument("--skip-sdk-analysis", action="store_true")
    sdk_analyze.add_argument("--max-files", type=int, default=200)
    sdk_analyze.add_argument("--max-bytes", type=int, default=120_000)
    sdk_analyze.add_argument("--json", action="store_true")
    sdk_discover = sdk_sub.add_parser("discover", help="Create external source discovery plan from work/requirements/sdk.")
    sdk_discover.add_argument("--work-id", required=True)
    sdk_discover.add_argument("--source", default="", help="SDK program directory. Default: work/requirements/sdk")
    sdk_discover.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    sdk_discover.add_argument("--max-files", type=int, default=200)
    sdk_discover.add_argument("--max-bytes", type=int, default=120_000)
    sdk_discover.add_argument("--json", action="store_true")

    flutter_cmd = sub.add_parser("flutter", help="Analyze Flutter multi-platform targets and build dispatch.")
    flutter_sub = flutter_cmd.add_subparsers(dest="flutter_command")
    for name in ["analyze", "init", "verify", "build", "run-workflow"]:
        flutter_item = flutter_sub.add_parser(name)
        flutter_item.add_argument("--work-id", required=True)
        flutter_item.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
        flutter_item.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
        flutter_item.add_argument("--targets", default="", help="Comma-separated Flutter targets: android,ios,web,windows,macos,linux")
        flutter_item.add_argument("--mode", choices=flutter_multiplatform.BUILD_MODES, default="debug")
        flutter_item.add_argument("--force", action="store_true", help="Refresh copied boilerplate during init.")
        flutter_item.add_argument("--execute", action="store_true", help="Run verification/build commands and capture evidence.")
        flutter_item.add_argument("--human-check", choices=["approved"], default="", help="Required for release execution.")
        flutter_item.add_argument("--timeout-seconds", type=int, default=600)
        flutter_item.add_argument("--json", action="store_true")
    flutter_finalize = flutter_sub.add_parser("finalize", help="Judge Flutter verification/build evidence completion.")
    flutter_finalize.add_argument("--work-id", required=True)
    flutter_finalize.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    flutter_finalize.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
    flutter_finalize.add_argument("--json", action="store_true")

    mcp_group_cmd = sub.add_parser("mcp-group", help="Prepare MCP server group implementation templates and boundary checks.")
    mcp_group_sub = mcp_group_cmd.add_subparsers(dest="mcp_group_command")
    for name in ["analyze", "init", "run-workflow"]:
        mcp_group_item = mcp_group_sub.add_parser(name)
        mcp_group_item.add_argument("--work-id", required=True)
        mcp_group_item.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
        mcp_group_item.add_argument(
            "--components",
            default="",
            help="Comma-separated components: local-model-mcp-server,mcp-client,local-ai-agent-runtime,discord-gateway",
        )
        mcp_group_item.add_argument("--force", action="store_true", help="Refresh copied template directories during init.")
        mcp_group_item.add_argument("--json", action="store_true")

    integration_cmd = sub.add_parser("integration", help="Analyze or verify system integration quality.")
    integration_sub = integration_cmd.add_subparsers(dest="integration_command")
    integration_analyze = integration_sub.add_parser("analyze", help="Analyze system integration points and emulator candidates.")
    integration_analyze.add_argument("--work-id", required=True)
    integration_analyze.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    integration_analyze.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
    integration_analyze.add_argument("--with-emulator", action="store_true", help="Include emulator suitability classification.")
    integration_analyze.add_argument("--json", action="store_true")
    integration_verify = integration_sub.add_parser("verify", help="Verify system integration evidence and emulator suitability.")
    integration_verify.add_argument("--work-id", required=True)
    integration_verify.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    integration_verify.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
    integration_verify.add_argument("--with-emulator", action="store_true", help="Include emulator suitability classification.")
    integration_verify.add_argument("--json", action="store_true")
    integration_test_plan = integration_sub.add_parser("test-plan", help="Create Integration Test runbook and Context First plan.")
    integration_test_plan.add_argument("--work-id", required=True)
    integration_test_plan.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    integration_test_plan.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
    integration_test_plan.add_argument("--json", action="store_true")
    integration_finalize = integration_sub.add_parser("finalize", help="Collect evidence, detect discomfort, and create final integration report.")
    integration_finalize.add_argument("--work-id", required=True)
    integration_finalize.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    integration_finalize.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
    integration_finalize.add_argument("--json", action="store_true")
    integration_emulator = integration_sub.add_parser("emulator", help="Prepare or inspect emulator work-area templates.")
    integration_emulator_sub = integration_emulator.add_subparsers(dest="emulator_command", required=True)
    integration_emulator_prepare = integration_emulator_sub.add_parser("prepare", help="Copy emulator templates to work/<work-id>/test-environment/emulator.")
    integration_emulator_prepare.add_argument("--work-id", required=True)
    integration_emulator_prepare.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    integration_emulator_prepare.add_argument("--target-repo", default="", help="Target repository. Default: work/<work-id>/source/repository")
    integration_emulator_prepare.add_argument("--force", action="store_true", help="Refresh existing copied emulator template directories.")
    integration_emulator_prepare.add_argument("--json", action="store_true")
    integration_emulator_health = integration_emulator_sub.add_parser("health", help="Check copied emulator templates and write health evidence.")
    integration_emulator_health.add_argument("--work-id", required=True)
    integration_emulator_health.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    integration_emulator_health.add_argument("--probe-docker", action="store_true", help="Run non-mutating docker version checks.")
    integration_emulator_health.add_argument("--json", action="store_true")

    doctor_cmd = sub.add_parser("doctor", help="Run workflow repository health checks.")
    doctor_cmd.add_argument("--json", action="store_true", help="Print doctor result as JSON.")
    doctor_cmd.add_argument("--fail-on-warning", action="store_true", help="Return non-zero when warnings are found.")
    doctor_cmd.add_argument("--skip-ut-spec-sync", action="store_true", help="Skip pytest UT specification sync check.")
    return parser


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


def format_help_usage_warning(color: bool = False) -> str:
    return "\n".join(
        [
            colorize_warning("警告: aiwfctl help の後続修飾子が指定されていません。", color),
            "",
            "help の後に、list / show / search / open / markdown のいずれかを指定してください。",
            "",
            "使用例:",
            "  aiwfctl help list",
            "  aiwfctl help show /vscode-environment",
            "  aiwfctl help search vscode",
            "  aiwfctl help open",
            "  aiwfctl help markdown --output work/help/ai-workflow-help.md",
            "",
            "PATH登録やsession更新を行う場合:",
            "  aiwfctl path shell",
            "",
            "実行環境を選択する場合:",
            "  aiwfctl env select web-svg",
            "  aiwfctl context init --work-id issue-123 --workflow /docs-sync",
            "  aiwfctl knowledge search --query \"PyQt GUI smoke test\"",
            "  aiwfctl flutter analyze --work-id issue-123",
            "  aiwfctl doctor",
        ]
    ) + "\n"


def knowledge_namespace(args: argparse.Namespace, repo_root: Path) -> argparse.Namespace:
    values = vars(args).copy()
    values["repo_root"] = str(repo_root)
    values["command"] = values.pop("knowledge_command", "")
    return argparse.Namespace(**values)


def format_knowledge_usage() -> str:
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
            "  aiwfctl knowledge migrate --source rag/optimized-chunks",
            "  aiwfctl knowledge rebuild --source-repo work/db/ariadne-knowledge-platform --reset",
            "  aiwfctl knowledge ingest --file rag/optimized-chunks/<id>.json",
            "  aiwfctl knowledge search --query \"PyQt GUI smoke test\" --limit 10",
            "  aiwfctl knowledge export-context --query \"PyQt GUI smoke test\" --output work/<work-id>/context/knowledge.json",
            "  aiwfctl knowledge verify --query workflow --query runtime --work-dir db/rag/evidence --work-id duckdb-reference-check",
            "",
            "DuckDBファイルは生成read modelです。source of truthはfile-based RAG artifactです。",
            "外部Knowledge正本は ariadne-knowledge-platform を work/db/ariadne-knowledge-platform にcloneして使います。",
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


def run(args: argparse.Namespace, color: bool = False) -> tuple[int, str]:
    repo_root = repo_root_from_args(args)
    registry = load_registry(repo_root)
    command = args.command
    help_command = getattr(args, "help_command", None)
    if command is None:
        return 1, format_root_usage_warning(color=color)
    if command == "env":
        environment_registry = load_environment_registry(repo_root)
        env_command = getattr(args, "env_command", None)
        if env_command is None:
            return 0, format_env_usage()
        if env_command == "list":
            return 0, format_environment_list(environment_registry)
        if env_command == "show":
            try:
                environment = find_public_environment(environment_registry, args.environment)
            except KeyError as exc:
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

    if command == "context":
        context_command = getattr(args, "context_command", None)
        if context_command is None:
            return 1, (
                "Context Management\n\n"
                "Usage:\n"
                "  aiwfctl context init --work-id <work-id> --workflow <workflow>\n\n"
                "Example:\n"
                "  aiwfctl context init --work-id issue-123 --workflow /docs-sync --tool gh:read-only:GitHub metadata collection\n"
            )
        if context_command == "init":
            result = dispatcher_context.run_init(args)
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
        return 1, f"Unknown context command: {context_command}\n"

    if command == "knowledge":
        knowledge_command = getattr(args, "knowledge_command", None)
        if knowledge_command is None:
            return 1, format_knowledge_usage()
        try:
            result = duckdb_store.run(knowledge_namespace(args, repo_root))
        except Exception as exc:
            return 1, f"Knowledge command failed: {exc}\n"
        if getattr(args, "json", False):
            return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        return 0, format_knowledge_result(result)

    if command == "sdk":
        sdk_command = getattr(args, "sdk_command", None)
        if sdk_command is None:
            return 1, (
                "SDK Analysis\n\n"
                "Usage:\n"
                "  aiwfctl sdk analyze --work-id <work-id>\n"
                "  aiwfctl sdk discover --work-id <work-id>\n"
                "  aiwfctl sdk analyze --work-id <work-id> --source work/requirements/sdk\n\n"
                "Outputs:\n"
                "  work/<work-id>/reports/sdk-analysis-report.md\n"
                "  work/<work-id>/context/sdk-analysis-context.json\n"
                "  work/<work-id>/requirements/sdk-integration-requirements.md\n"
                "  work/<work-id>/reports/sdk-external-discovery-report.md\n"
                "  work/<work-id>/context/sdk-external-discovery.json\n"
                "  work/<work-id>/requirements/sdk-external-requirements.md\n"
            )
        try:
            sdk_args = argparse.Namespace(**vars(args))
            sdk_args.command = sdk_command
            sdk_args.repo_root = str(repo_root)
            result = sdk_analysis.run(sdk_args)
        except Exception as exc:
            return 1, f"SDK analysis failed: {exc}\n"
        if getattr(args, "json", False):
            return 0, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        return 0, sdk_analysis.format_result(result) + "\n"

    if command == "flutter":
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
                "  work/<work-id>/context/flutter-development-context.json\n"
                "  work/<work-id>/reports/flutter-multiplatform-report.md\n"
                "  work/<work-id>/evidence/flutter/common/verification-plan.md\n"
            )
        try:
            flutter_args = argparse.Namespace(**vars(args))
            flutter_args.command = flutter_command
            flutter_args.repo_root = str(repo_root)
            result = flutter_multiplatform.run(flutter_args)
        except Exception as exc:
            return 1, f"Flutter multi-platform failed: {exc}\n"
        code = 0 if result.get("status") not in {"human-check-required", "failed"} else 2
        if getattr(args, "json", False):
            return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        return code, flutter_multiplatform.format_result(result) + "\n"

    if command == "mcp-group":
        mcp_group_command = getattr(args, "mcp_group_command", None)
        if mcp_group_command is None:
            return 1, (
                "MCP Server Group Implementation\n\n"
                "Usage:\n"
                "  aiwfctl mcp-group analyze --work-id <work-id>\n"
                "  aiwfctl mcp-group init --work-id <work-id> --components local-model-mcp-server,mcp-client\n"
                "  aiwfctl mcp-group run-workflow --work-id <work-id> --components local-model-mcp-server,mcp-client,local-ai-agent-runtime,discord-gateway\n\n"
                "Outputs:\n"
                "  work/<work-id>/context/mcp-server-group-implementation-context.json\n"
                "  work/<work-id>/reports/mcp-server-group-implementation-report.md\n"
                "  work/<work-id>/implementation/mcp-server-group/<component>/\n"
            )
        try:
            mcp_args = argparse.Namespace(**vars(args))
            mcp_args.command = mcp_group_command
            mcp_args.repo_root = str(repo_root)
            result = mcp_server_group.run(mcp_args)
        except Exception as exc:
            return 1, f"MCP server group implementation failed: {exc}\n"
        code = 0 if result.get("status") != "human-check-required" else 2
        if getattr(args, "json", False):
            return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        return code, mcp_server_group.format_result(result) + "\n"

    if command == "integration":
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
                "  work/<work-id>/reports/system-integration-report.md\n"
                "  work/<work-id>/context/integration-context.json\n"
                "  work/<work-id>/context/emulator-context.json\n"
                "  work/<work-id>/context/emulator-health-context.json\n"
                "  work/<work-id>/test-evidence/emulator/health-summary.md\n"
                "  work/<work-id>/context/integration-test-plan-context.json\n"
                "  work/<work-id>/test-evidence/integration-test/integration-test-runbook.md\n"
                "  work/<work-id>/context/integration-finalization-context.json\n"
                "  work/<work-id>/reports/system-integration-final-report.md\n"
            )
        try:
            integration_args = argparse.Namespace(**vars(args))
            integration_args.command = integration_command
            integration_args.repo_root = str(repo_root)
            result = system_integration.run(integration_args)
        except Exception as exc:
            return 1, f"System integration failed: {exc}\n"
        code = 0 if result.get("status") != "human-check-required" else 2
        if getattr(args, "json", False):
            return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        return code, system_integration.format_result(result) + "\n"

    if command == "doctor":
        result = workflow_doctor.run(
            argparse.Namespace(
                repo_root=str(repo_root),
                fail_on_warning=args.fail_on_warning,
                skip_ut_spec_sync=args.skip_ut_spec_sync,
            )
        )
        code = 1 if result.get("status") == "fail" else 0
        if getattr(args, "json", False):
            return code, json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        lines = [
            "Workflow Doctor",
            "",
            f"Status        : {result.get('status', '')}",
            f"Warning Count : {result.get('warning_count', 0)}",
        ]
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

    if command != "help":
        return 1, f"Unknown command: {command}\n"
    if help_command is None:
        return 1, format_help_usage_warning(color=color)

    if help_command == "list":
        rows = []
        for item in sorted(registry.get("commands", []), key=command_key):
            required = [arg.get("name", "") for arg in item.get("arguments", []) if arg.get("required")]
            prerequisites = item.get("prerequisites", [])
            docs = item.get("docs", [])
            rows.append(
                "\n".join(
                    [
                        str(item.get("command", "")),
                        f"  概要: {item.get('overview', '')}",
                        format_prerequisites_for_list(prerequisites),
                        f"  必須: {', '.join(required) or 'なし'}",
                        format_docs_for_list(docs),
                    ]
                )
            )
        extension_rows = []
        for item in sorted(registry.get("extensions", []), key=extension_key):
            prerequisites = item.get("prerequisites", [])
            docs = item.get("docs", [])
            extension_rows.append(
                "\n".join(
                    [
                        str(item.get("name", "")),
                        f"  種別: workflow extension",
                        f"  概要: {item.get('overview', '')}",
                        format_prerequisites_for_list(prerequisites),
                        f"  起動条件: {item.get('trigger', '')}",
                        f"  単独実行: {str(item.get('standalone_command', False)).lower()}",
                        format_docs_for_list(docs),
                    ]
                )
            )
        output_parts = ["## Workflow Commands", "\n\n".join(rows)]
        if extension_rows:
            output_parts.extend(["", "## Workflow Extensions", "\n\n".join(extension_rows)])
        return 0, "\n".join(output_parts).rstrip() + "\n"

    if help_command == "show":
        item_type, item = find_help_item(registry, args.name)
        if item_type == "extension":
            return 0, format_extension_markdown(item, repo_root) + "\n"
        return 0, format_command_markdown(item, repo_root) + "\n"

    if help_command == "search":
        command_matches = search_commands(registry, args.keywords)
        extension_matches = search_extensions(registry, args.keywords)
        if not command_matches and not extension_matches:
            return 1, "該当するworkflow helpはありません。\n"
        return 0, format_help_search_candidates(command_matches, extension_matches, keywords=args.keywords)

    if help_command == "open":
        keywords = getattr(args, "query", [])
        commands = search_commands(registry, keywords) if keywords else None
        extensions = search_extensions(registry, keywords) if keywords else None
        return 0, format_index_markdown(registry, repo_root, commands, extensions)

    if help_command == "markdown":
        keywords = getattr(args, "query", [])
        commands = search_commands(registry, keywords) if keywords else None
        extensions = search_extensions(registry, keywords) if keywords else None
        output = Path(args.output)
        output = output if output.is_absolute() else repo_root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(format_index_markdown(registry, repo_root, commands, extensions), encoding="utf-8")
        return 0, f"wrote: {relative_to_repo(repo_root, output)}\n"

    return 1, f"Unknown help command: {help_command}\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    code, output = run(args, color=should_use_color(sys.stdout))
    print(output, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
