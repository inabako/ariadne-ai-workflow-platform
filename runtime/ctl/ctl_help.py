from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime.common import registry_store, relative_to_repo
from runtime.ctl.help_constants import (
    BLOB_ALL_TERMS_BASE_SCORE,
    BLOB_TERM_MATCH_SCORE,
    EMPTY_QUERY_SCORE,
    EXPLICIT_TERM_ALL_TERMS_SCORE,
    EXPLICIT_TERM_EXACT_MATCH_SCORE,
    EXPLICIT_TERM_PARTIAL_MATCH_SCORE,
    EXPLICIT_TERM_SINGLE_MATCH_SCORE,
    MIN_SEARCH_MATCH_SCORE,
)


ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def colorize_warning(message: str, color: bool = False) -> str:
    if not color:
        return message
    return f"{ANSI_YELLOW}{message}{ANSI_RESET}"


def registry_path(repo_root: Path) -> Path:
    return registry_store.registry_db_path(repo_root)


def load_registry(repo_root: Path) -> dict[str, Any]:
    data = registry_store.load_workflow_help(repo_root)
    if not isinstance(data, dict):
        raise ValueError("workflow help registry must be an object.")
    data.setdefault("commands", [])
    data.setdefault("extensions", [])
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
        return EMPTY_QUERY_SCORE
    query = normalize_search_value(" ".join(terms))
    blob = text_blob(item)
    score = 0
    if all(term in blob for term in terms):
        score += BLOB_ALL_TERMS_BASE_SCORE + (BLOB_TERM_MATCH_SCORE * len(terms))
    for search_term in explicit_search_terms(item):
        if search_term == query:
            score += EXPLICIT_TERM_EXACT_MATCH_SCORE
        elif query and (query in search_term or search_term in query):
            score += EXPLICIT_TERM_PARTIAL_MATCH_SCORE
        elif all(term in search_term for term in terms):
            score += EXPLICIT_TERM_ALL_TERMS_SCORE
        else:
            score += EXPLICIT_TERM_SINGLE_MATCH_SCORE * sum(1 for term in terms if term in search_term)
    return score


def search_commands(registry: dict[str, Any], keywords: list[str]) -> list[dict[str, Any]]:
    if not [term for term in keywords if term.strip()]:
        return sorted(registry.get("commands", []), key=command_key)
    matches: list[tuple[int, dict[str, Any]]] = []
    for command in registry.get("commands", []):
        score = search_score(command, keywords)
        if score > MIN_SEARCH_MATCH_SCORE:
            matches.append((score, command))
    return [item for _, item in sorted(matches, key=lambda entry: (-entry[0], command_key(entry[1])))]


def search_extensions(registry: dict[str, Any], keywords: list[str]) -> list[dict[str, Any]]:
    if not [term for term in keywords if term.strip()]:
        return sorted(registry.get("extensions", []), key=extension_key)
    matches: list[tuple[int, dict[str, Any]]] = []
    for extension in registry.get("extensions", []):
        score = search_score(extension, keywords)
        if score > MIN_SEARCH_MATCH_SCORE:
            matches.append((score, extension))
    return [item for _, item in sorted(matches, key=lambda entry: (-entry[0], extension_key(entry[1])))]


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


def format_help_list(registry: dict[str, Any]) -> str:
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
                    "  種別: workflow extension",
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
    return "\n".join(output_parts).rstrip() + "\n"


def run_help_command(args: Any, repo_root: Path, registry: dict[str, Any], *, color: bool = False) -> tuple[int, str]:
    help_command = getattr(args, "help_command", None)
    if help_command is None:
        return 1, format_help_usage_warning(color=color)

    if help_command == "list":
        return 0, format_help_list(registry)

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
