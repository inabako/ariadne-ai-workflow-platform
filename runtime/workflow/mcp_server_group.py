from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402


SCHEMA_VERSION = "1.0"
ARTIFACT_TYPE = "mcp-server-group-implementation-context"
DEFAULT_SCHEMA = ".github/schemas/mcp-server-group-implementation-context.schema.json"
COMPONENTS = {
    "local-model-mcp-server": {
        "template_path": "templates/boilerplates/mcp/local-model-mcp-server-template",
        "destination": "local-model-mcp-server",
        "role": "MCP Server capability provider",
    },
    "mcp-client": {
        "template_path": "templates/boilerplates/mcp/mcp-client-template",
        "destination": "mcp-client",
        "role": "Reusable MCP Client facade",
    },
    "local-ai-agent-runtime": {
        "template_path": "templates/boilerplates/mcp/local-ai-agent-runtime-template",
        "destination": "local-ai-agent-runtime",
        "role": "Agent Runtime job/workflow engine",
    },
    "discord-gateway": {
        "template_path": "templates/boilerplates/mcp/discord-gateway-template",
        "destination": "discord-gateway",
        "role": "Discord operation gateway",
    },
}
DEFAULT_COMPONENTS = ["local-model-mcp-server", "mcp-client"]


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def resolve_work_dir(repo_root: Path, work_id: str, work_dir: str = "") -> Path:
    if work_dir:
        return resolve_repo_path(repo_root, work_dir)
    if not work_id:
        raise ValueError("--work-id is required when --work-dir is not specified.")
    return repo_root / "work" / work_id


def parse_components(value: str | None) -> tuple[list[str], list[str]]:
    if not value:
        return list(DEFAULT_COMPONENTS), []
    selected: list[str] = []
    unknown: list[str] = []
    for raw in value.split(","):
        component = raw.strip().lower().replace("_", "-")
        if not component:
            continue
        if component not in COMPONENTS:
            unknown.append(component)
            continue
        if component not in selected:
            selected.append(component)
    return selected, unknown


def component_records(repo_root: Path, components: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for component in components:
        definition = COMPONENTS[component]
        template_path = repo_root / definition["template_path"]
        records.append(
            {
                "component": component,
                "role": definition["role"],
                "template_path": definition["template_path"],
                "template_exists": template_path.exists(),
                "destination": f"work/<work-id>/implementation/mcp-server-group/{definition['destination']}",
            }
        )
    return records


def boundary_checks(components: list[str], unknown: list[str]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    checks.append(
        {
            "check": "component-selection",
            "status": "pass" if components else "human-check-required",
            "detail": "At least one known MCP component is selected." if components else "No known MCP components were selected.",
        }
    )
    if unknown:
        checks.append(
            {
                "check": "unknown-components",
                "status": "human-check-required",
                "detail": f"Unknown components: {', '.join(unknown)}",
            }
        )
    if "discord-gateway" in components and "local-ai-agent-runtime" not in components:
        checks.append(
            {
                "check": "discord-runtime-boundary",
                "status": "human-check-required",
                "detail": "Discord Gateway requires an explicit Agent Runtime endpoint or local-ai-agent-runtime component.",
            }
        )
    if "local-ai-agent-runtime" in components and "mcp-client" not in components:
        checks.append(
            {
                "check": "runtime-mcp-client-boundary",
                "status": "human-check-required",
                "detail": "Agent Runtime should use an MCP Client boundary before calling MCP Servers.",
            }
        )
    if "mcp-client" in components and "local-model-mcp-server" not in components:
        checks.append(
            {
                "check": "client-server-boundary",
                "status": "planned",
                "detail": "MCP Client selected without local server template; external MCP Server endpoint must be specified later.",
            }
        )
    checks.append(
        {
            "check": "state-source-boundary",
            "status": "pass",
            "detail": "MCP Server, MCP Client, Agent Runtime, and Discord Gateway state ownership must remain separated.",
        }
    )
    return checks


def copy_templates(repo_root: Path, work_dir: Path, components: list[str], *, force: bool = False) -> list[dict[str, str]]:
    output_root = work_dir / "implementation" / "mcp-server-group"
    output_root.mkdir(parents=True, exist_ok=True)
    copies: list[dict[str, str]] = []
    for component in components:
        definition = COMPONENTS[component]
        source = repo_root / definition["template_path"]
        destination = output_root / definition["destination"]
        status = "missing-template"
        if source.exists():
            if destination.exists() and force:
                shutil.rmtree(destination)
            if destination.exists():
                status = "exists"
            else:
                shutil.copytree(source, destination)
                status = "copied"
        copies.append(
            {
                "component": component,
                "source": relative_to_repo(source, repo_root),
                "destination": relative_to_repo(destination, repo_root),
                "status": status,
            }
        )
    return copies


def render_report(context: dict[str, Any]) -> str:
    lines = [
        "# MCP Server Group Implementation Report",
        "",
        f"- work_id: `{context['work_id']}`",
        f"- status: `{context['status']}`",
        f"- command: `{context['stage']}`",
        "",
        "## Components",
    ]
    for component in context["components"]:
        lines.append(
            f"- `{component['component']}`: {component['role']} / template: `{component['template_path']}` / exists: `{component['template_exists']}`"
        )
    lines.extend(["", "## Boundary Checks"])
    for check in context["boundary_checks"]:
        lines.append(f"- `{check['check']}`: `{check['status']}` - {check['detail']}")
    if context.get("template_copies"):
        lines.extend(["", "## Template Copies"])
        for copy in context["template_copies"]:
            lines.append(f"- `{copy['component']}`: `{copy['status']}` -> `{copy['destination']}`")
    lines.extend(
        [
            "",
            "## Handoff",
            "- Keep Discord Gateway, Agent Runtime, MCP Client, and MCP Server in separate repositories or top-level services unless a human approves a monorepo layout.",
            "- Do not pass Discord library objects into Agent Runtime.",
            "- Do not let Agent Runtime call MCP Server directly; use MCP Client boundary.",
            "- Do not treat MCP Server as a job scheduler or completion evaluator.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(repo_root: Path, work_dir: Path, context: dict[str, Any]) -> None:
    context_path = work_dir / "context" / "mcp-server-group-implementation-context.json"
    report_path = work_dir / "reports" / "mcp-server-group-implementation-report.md"
    manifest_path = work_dir / "context" / "context-manifest.json"
    context["artifacts"] = {
        "context": relative_to_repo(context_path, repo_root),
        "report": relative_to_repo(report_path, repo_root),
        "manifest": relative_to_repo(manifest_path, repo_root),
    }
    write_json(context_path, context)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(context), encoding="utf-8")
    register_context(
        repo_root,
        work_dir,
        work_id=context["work_id"],
        context_type=ARTIFACT_TYPE,
        path=context_path,
        required=True,
        generated_by="mcp-server-group-implementation",
        schema=DEFAULT_SCHEMA,
        owner="mcp-server-group-implementation",
        status=context["status"],
    )


def build_context(
    repo_root: Path,
    *,
    command: str,
    work_id: str,
    work_dir: str = "",
    components: str = "",
    force: bool = False,
) -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    selected, unknown = parse_components(components)
    checks = boundary_checks(selected, unknown)
    copies: list[dict[str, str]] = []
    if command in {"init", "run-workflow"}:
        copies = copy_templates(repo_root, work_path, selected, force=force)
    context: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "generated_at": utc_now_iso(),
        "stage": command,
        "status": "human-check-required" if any(item["status"] == "human-check-required" for item in checks) else "available",
        "work_id": work_id,
        "work_dir": relative_to_repo(work_path, repo_root),
        "selected_components": selected,
        "unknown_components": unknown,
        "components": component_records(repo_root, selected),
        "boundary_checks": checks,
        "template_copies": copies,
        "human_checks": [item["detail"] for item in checks if item["status"] == "human-check-required"],
        "next_actions": [
            "Confirm repository layout for each selected component.",
            "Confirm Runtime API endpoint and MCP Server endpoint contracts.",
            "Run each copied template's tests before feature implementation.",
        ],
    }
    write_outputs(repo_root, work_path, context)
    return context


def format_result(result: dict[str, Any]) -> str:
    lines = [
        "MCP Server Group Implementation",
        "",
        f"Status : {result.get('status', '')}",
        f"Stage  : {result.get('stage', '')}",
        f"Work   : {result.get('work_dir', '')}",
        "",
        "Components",
    ]
    for component in result.get("components", []):
        lines.append(f"  - {component.get('component', '')}: {component.get('role', '')}")
    human_checks = result.get("human_checks", [])
    if human_checks:
        lines.extend(["", "Human Check"])
        lines.extend(f"  - {item}" for item in human_checks)
    artifacts = result.get("artifacts", {})
    lines.extend(["", "Artifacts", f"  - context: {artifacts.get('context', '')}", f"  - report : {artifacts.get('report', '')}"])
    return "\n".join(lines).rstrip()


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if getattr(args, "repo_root", "") else find_repo_root()
    return build_context(
        repo_root,
        command=args.command,
        work_id=args.work_id,
        work_dir=getattr(args, "work_dir", ""),
        components=getattr(args, "components", ""),
        force=getattr(args, "force", False),
    )
