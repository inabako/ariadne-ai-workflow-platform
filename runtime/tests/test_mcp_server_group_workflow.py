from __future__ import annotations

import argparse
from pathlib import Path

from runtime import ctl
from runtime.workflow import mcp_server_group


def write_template(repo_root: Path, template_name: str) -> None:
    template = repo_root / "templates" / "boilerplates" / template_name
    template.mkdir(parents=True)
    (template / "README.md").write_text(f"# {template_name}\n", encoding="utf-8")
    (template / "pyproject.toml").write_text("[project]\nname='template'\n", encoding="utf-8")


def write_all_templates(repo_root: Path) -> None:
    for template_name in [
        "local-model-mcp-server-template",
        "mcp-client-template",
        "local-ai-agent-runtime-template",
        "discord-gateway-template",
    ]:
        write_template(repo_root, template_name)


def test_parse_components_defaults_and_unknown() -> None:
    selected, unknown = mcp_server_group.parse_components("")
    assert selected == ["local-model-mcp-server", "mcp-client"]
    assert unknown == []

    selected, unknown = mcp_server_group.parse_components("mcp-client,unknown,discord_gateway")
    assert selected == ["mcp-client", "discord-gateway"]
    assert unknown == ["unknown"]


def test_analyze_creates_context_and_human_check_for_invalid_boundary(tmp_path: Path) -> None:
    write_all_templates(tmp_path)

    result = mcp_server_group.build_context(
        tmp_path,
        command="analyze",
        work_id="issue-1",
        components="discord-gateway",
    )

    assert result["status"] == "human-check-required"
    assert "Discord Gateway requires an explicit Agent Runtime endpoint" in result["human_checks"][0]
    assert (tmp_path / "work" / "issue-1" / "context" / "mcp-server-group-implementation-context.json").exists()
    assert (tmp_path / "work" / "issue-1" / "reports" / "mcp-server-group-implementation-report.md").exists()


def test_init_copies_selected_templates(tmp_path: Path) -> None:
    write_all_templates(tmp_path)

    result = mcp_server_group.build_context(
        tmp_path,
        command="init",
        work_id="issue-2",
        components="local-model-mcp-server,mcp-client,local-ai-agent-runtime",
    )

    output_root = tmp_path / "work" / "issue-2" / "implementation" / "mcp-server-group"
    assert result["status"] == "available"
    assert (output_root / "local-model-mcp-server" / "README.md").exists()
    assert (output_root / "mcp-client" / "README.md").exists()
    assert (output_root / "local-ai-agent-runtime" / "README.md").exists()


def test_ctl_parser_and_run_mcp_group_namespace(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, str] = {}

    def fake_run(args: argparse.Namespace) -> dict[str, object]:
        captured["command"] = args.command
        captured["components"] = args.components
        return {
            "artifact_type": "mcp-server-group-implementation-context",
            "status": "available",
            "stage": args.command,
            "work_dir": "work/issue-3",
            "components": [{"component": "mcp-client", "role": "Reusable MCP Client facade"}],
            "human_checks": [],
            "artifacts": {
                "context": "work/issue-3/context/mcp-server-group-implementation-context.json",
                "report": "work/issue-3/reports/mcp-server-group-implementation-report.md",
            },
        }

    monkeypatch.setattr(ctl.mcp_server_group, "run", fake_run)
    args = ctl.build_parser().parse_args(
        ["--repo-root", str(tmp_path), "mcp-group", "init", "--work-id", "issue-3", "--components", "mcp-client"]
    )

    code, output = ctl.run(args)

    assert code == 0
    assert captured["command"] == "init"
    assert captured["components"] == "mcp-client"
    assert "MCP Server Group Implementation" in output

