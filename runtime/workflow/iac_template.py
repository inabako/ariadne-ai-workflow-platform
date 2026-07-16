from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, load_env, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402


SCHEMA_VERSION = "1.0"
SETUP_ARTIFACT_TYPE = "iac-template-setup-context"
HEALTH_ARTIFACT_TYPE = "iac-template-health-context"
DEFAULT_SETUP_SCHEMA = ".github/schemas/iac-template-setup-context.schema.json"
DEFAULT_HEALTH_SCHEMA = ".github/schemas/iac-template-health-context.schema.json"
TOOL_ENV_VARS: dict[str, list[str]] = {
    "terraform": ["AIWF_TERRAFORM_EXE"],
}

TEMPLATE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "opentelemetry-collector": {
        "name": "opentelemetry-collector",
        "display_name": "OpenTelemetry Collector",
        "template_path": "templates/boilerplates/infrastructure/opentelemetry-collector-template",
        "destination": "source/infrastructure/opentelemetry-collector",
        "evidence": "test-evidence/infrastructure/opentelemetry-collector",
        "required_files": [
            "README.md",
            "VERSION",
            ".env.example",
            "Makefile",
            "config/base.yaml",
            "distribution/builder-config.yaml",
            "manifests/catalog.yaml",
            "manifests/component.schema.json",
            "manifests/selection.schema.json",
            "scripts/otel_template.py",
            "terraform/versions.tf",
            "terraform/main.tf",
            "terraform/modules/collector/main.tf",
            "examples/minimal/selection.yaml",
        ],
        "required_dirs": [
            "receivers/otlp",
            "processors/memory-limiter",
            "processors/batch",
            "exporters/debug",
            "extensions/health-check",
            "pipelines",
            "tests/unit",
            "docs",
        ],
    }
}


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def resolve_work_dir(repo_root: Path, work_id: str, work_dir: str = "") -> Path:
    if work_dir:
        return resolve_repo_path(repo_root, work_dir)
    if not work_id:
        raise ValueError("--work-id is required when --work-dir is not specified.")
    return repo_root / "work" / work_id


def template_definition(name: str) -> dict[str, Any]:
    key = name.strip().lower()
    if key not in TEMPLATE_DEFINITIONS:
        raise KeyError(f"Unknown IaC template: {name}")
    return TEMPLATE_DEFINITIONS[key]


def list_templates(repo_root: Path) -> dict[str, Any]:
    templates = []
    for definition in TEMPLATE_DEFINITIONS.values():
        source = repo_root / definition["template_path"]
        templates.append(
            {
                "name": definition["name"],
                "display_name": definition["display_name"],
                "template_path": definition["template_path"],
                "exists": source.exists(),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "iac-template-catalog",
        "generated_at": utc_now_iso(),
        "templates": templates,
    }


def copy_template(repo_root: Path, work_path: Path, definition: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    source = repo_root / definition["template_path"]
    destination = work_path / definition["destination"]
    evidence_dir = work_path / definition["evidence"]
    evidence_dir.mkdir(parents=True, exist_ok=True)
    if not source.exists() or not source.is_dir():
        return {
            "template": definition["name"],
            "status": "missing-template",
            "template_path": relative_to_repo(repo_root, source),
            "destination": relative_to_repo(repo_root, destination),
            "evidence_dir": relative_to_repo(repo_root, evidence_dir),
            "message": "Template directory was not found.",
        }
    if destination.exists() and not force:
        return {
            "template": definition["name"],
            "status": "existing",
            "template_path": relative_to_repo(repo_root, source),
            "destination": relative_to_repo(repo_root, destination),
            "evidence_dir": relative_to_repo(repo_root, evidence_dir),
            "message": "Destination already exists. Use --force to refresh the copied template.",
        }
    if destination.exists() and force:
        try:
            destination.resolve().relative_to(work_path.resolve())
        except ValueError as exc:
            raise ValueError(f"Refusing to remove destination outside work directory: {destination}") from exc
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    copied_files = [
        path.relative_to(destination).as_posix()
        for path in sorted(destination.rglob("*"), key=lambda item: item.relative_to(destination).as_posix().lower())
        if path.is_file()
    ]
    return {
        "template": definition["name"],
        "status": "copied",
        "template_path": relative_to_repo(repo_root, source),
        "destination": relative_to_repo(repo_root, destination),
        "evidence_dir": relative_to_repo(repo_root, evidence_dir),
        "copied_file_count": len(copied_files),
        "message": "IaC template was copied to the work area.",
    }


def prepare_template(
    repo_root: Path,
    *,
    template: str,
    work_id: str,
    work_dir: str = "",
    force: bool = False,
) -> dict[str, Any]:
    definition = template_definition(template)
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    result = copy_template(repo_root, work_path, definition, force=force)
    status = result["status"]
    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": SETUP_ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "workflow": "realtime-iac",
        "generated_at": utc_now_iso(),
        "template": definition["name"],
        "template_path": definition["template_path"],
        "prepared": result,
        "rules": {
            "template_source_is_read_only": True,
            "edit_only_work_copy": True,
            "do_not_run_terraform_in_prepare": True,
            "do_not_start_collector_in_prepare": True,
        },
    }
    context_path = work_path / "context" / "iac-template-context.json"
    write_json(context_path, context)
    manifest = register_context(
        repo_root,
        work_path,
        work_id=work_id,
        context_type="iac-template-setup",
        path=context_path,
        required=False,
        generated_by="realtime-iac",
        owner="realtime-iac",
        schema=DEFAULT_SETUP_SCHEMA,
        status=status,
    )
    context["artifacts"] = {"context": relative_to_repo(repo_root, context_path)}
    context["manifest_path"] = relative_to_repo(repo_root, work_path / "context" / "context-manifest.json")
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(context_path, context)
    return context


def resolve_tool_path(name: str, settings: dict[str, str] | None = None) -> str:
    for key in TOOL_ENV_VARS.get(name, []):
        value = (settings or {}).get(key, "").strip()
        if value and Path(value).is_file():
            return str(Path(value))
    path = shutil.which(name)
    if path:
        return path
    return ""


def tool_preflight(*, repo_root: Path | None = None, probe: bool = False) -> dict[str, Any]:
    settings = load_env(repo_root) if repo_root else {}
    tools = {}
    for name in ["docker", "terraform", "make", "python"]:
        path = resolve_tool_path(name, settings)
        item: dict[str, Any] = {"path": path, "available": bool(path), "version_status": "not-probed"}
        if path and probe:
            command = [path, "--version"] if name != "docker" else [path, "version", "--format", "{{.Client.Version}}"]
            try:
                completed = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                item["version_status"] = "error"
                item["error"] = str(exc)
            else:
                item["version_status"] = "pass" if completed.returncode == 0 else "fail"
                item["output"] = (completed.stdout or completed.stderr).strip()[:500]
        tools[name] = item
    return tools


def health_checks(destination: Path, definition: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for relative_path in definition["required_files"]:
        path = destination / relative_path
        checks.append(
            {
                "kind": "file",
                "path": relative_path,
                "status": "ready" if path.is_file() else "missing",
            }
        )
    for relative_path in definition["required_dirs"]:
        path = destination / relative_path
        checks.append(
            {
                "kind": "directory",
                "path": relative_path,
                "status": "ready" if path.is_dir() else "missing",
            }
        )
    return checks


def render_health_summary(context: dict[str, Any]) -> str:
    lines = [
        "# IaC Template Health Summary",
        "",
        f"- status: `{context.get('status', '')}`",
        f"- template: `{context.get('template', '')}`",
        f"- work_id: `{context.get('work_id', '')}`",
        f"- destination: `{context.get('destination', '')}`",
        "",
        "## Checks",
        "",
    ]
    for check in context.get("checks", []):
        lines.append(f"- {check.get('kind')}: `{check.get('path')}` -> `{check.get('status')}`")
    lines.extend(["", "## Tool Preflight", ""])
    for name, item in context.get("tools", {}).items():
        lines.append(f"- {name}: available=`{item.get('available')}` version_status=`{item.get('version_status')}`")
    lines.extend(["", "## Human Check", ""])
    human_checks = context.get("human_checks", [])
    lines.extend(f"- {item}" for item in human_checks) if human_checks else lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def health_template(
    repo_root: Path,
    *,
    template: str,
    work_id: str,
    work_dir: str = "",
    probe_tools: bool = False,
) -> dict[str, Any]:
    definition = template_definition(template)
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    destination = work_path / definition["destination"]
    evidence_dir = work_path / definition["evidence"]
    evidence_dir.mkdir(parents=True, exist_ok=True)
    checks = health_checks(destination, definition)
    missing = [check["path"] for check in checks if check["status"] != "ready"]
    human_checks = []
    if not destination.exists():
        human_checks.append("Template work directory is missing. Run prepare before health.")
    if missing:
        human_checks.append("Template work directory is missing required files or directories.")
    tools = tool_preflight(repo_root=repo_root, probe=probe_tools)
    if not tools["docker"]["available"]:
        human_checks.append("docker CLI was not found on PATH.")
    if not tools["terraform"]["available"]:
        human_checks.append("terraform CLI was not found on PATH.")
    status = "ready"
    if not destination.exists() or missing:
        status = "human-check-required"
    elif human_checks:
        status = "warning"
    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": HEALTH_ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "workflow": "realtime-iac",
        "generated_at": utc_now_iso(),
        "template": definition["name"],
        "destination": relative_to_repo(repo_root, destination),
        "evidence_dir": relative_to_repo(repo_root, evidence_dir),
        "checks": checks,
        "tools": tools,
        "human_checks": list(dict.fromkeys(human_checks)),
        "rules": {
            "health_check_is_non_mutating": True,
            "do_not_run_terraform_in_health": True,
            "do_not_start_collector_in_health": True,
            "probe_tools_only_checks_versions": True,
        },
    }
    context_path = work_path / "context" / "iac-template-health-context.json"
    evidence_path = evidence_dir / "health-summary.md"
    context["artifacts"] = {
        "context": relative_to_repo(repo_root, context_path),
        "evidence": relative_to_repo(repo_root, evidence_path),
    }
    evidence_path.write_text(render_health_summary(context), encoding="utf-8")
    write_json(context_path, context)
    manifest = register_context(
        repo_root,
        work_path,
        work_id=work_id,
        context_type="iac-template-health",
        path=context_path,
        required=False,
        generated_by="realtime-iac",
        owner="realtime-iac",
        schema=DEFAULT_HEALTH_SCHEMA,
        status=status,
    )
    context["manifest_path"] = relative_to_repo(repo_root, work_path / "context" / "context-manifest.json")
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(context_path, context)
    return context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare and inspect reusable IaC boilerplate templates.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)
    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--json", action="store_true")
    for name in ["prepare", "health"]:
        item = sub.add_parser(name)
        item.add_argument("--template", default="opentelemetry-collector")
        item.add_argument("--work-id", required=True)
        item.add_argument("--work-dir", default="")
        item.add_argument("--json", action="store_true")
        if name == "prepare":
            item.add_argument("--force", action="store_true")
        else:
            item.add_argument("--probe-tools", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    if args.command == "list":
        result = list_templates(repo_root)
    elif args.command == "prepare":
        result = prepare_template(repo_root, template=args.template, work_id=args.work_id, work_dir=args.work_dir, force=args.force)
    elif args.command == "health":
        result = health_template(repo_root, template=args.template, work_id=args.work_id, work_dir=args.work_dir, probe_tools=args.probe_tools)
    else:
        parser.error(f"Unknown command: {args.command}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in {None, "copied", "existing", "ready", "warning"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
