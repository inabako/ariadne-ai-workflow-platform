from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from runtime.common import find_repo_root, read_json, relative_to_repo  # noqa: E402


def registry_path(repo_root: Path) -> Path:
    return repo_root / "runtime" / "registries" / "workflow_help.json"


def load_registry(repo_root: Path) -> dict[str, Any]:
    data = read_json(registry_path(repo_root), default={})
    if not isinstance(data, dict):
        raise ValueError("workflow help registry must be a JSON object.")
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


def search_commands(registry: dict[str, Any], keywords: list[str]) -> list[dict[str, Any]]:
    terms = [term.lower() for term in keywords if term.strip()]
    if not terms:
        return sorted(registry.get("commands", []), key=command_key)
    matches = []
    for command in registry.get("commands", []):
        blob = text_blob(command)
        if all(term in blob for term in terms):
            matches.append(command)
    return sorted(matches, key=command_key)


def search_extensions(registry: dict[str, Any], keywords: list[str]) -> list[dict[str, Any]]:
    terms = [term.lower() for term in keywords if term.strip()]
    if not terms:
        return sorted(registry.get("extensions", []), key=extension_key)
    matches = []
    for extension in registry.get("extensions", []):
        blob = text_blob(extension)
        if all(term in blob for term in terms):
            matches.append(extension)
    return sorted(matches, key=extension_key)


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aiwfctl", description="Intent-Driven Robotics AI Workflow control helper.")
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
    return parser


def repo_root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve() if args.repo_root else find_repo_root()


def run(args: argparse.Namespace) -> tuple[int, str]:
    repo_root = repo_root_from_args(args)
    registry = load_registry(repo_root)
    command = args.command or "help"
    help_command = getattr(args, "help_command", None) or "list"
    if command != "help":
        return 1, f"Unknown command: {command}\n"

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
        return 0, format_index_markdown(registry, repo_root, command_matches, extension_matches)

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
    code, output = run(args)
    print(output, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
