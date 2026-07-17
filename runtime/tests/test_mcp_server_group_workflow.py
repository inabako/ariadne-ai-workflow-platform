from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from runtime import ctl
from runtime.workflow import mcp_server_group


def write_template(repo_root: Path, template_name: str) -> None:
    template = repo_root / "templates" / "boilerplates" / "mcp" / template_name
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

    selected, unknown = mcp_server_group.parse_components("mcp-client,,mcp_client, local-model-mcp-server ")
    assert selected == ["mcp-client", "local-model-mcp-server"]
    assert unknown == []


def test_resolve_work_dir_requires_work_id_without_explicit_work_dir(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="--work-id is required"):
        mcp_server_group.resolve_work_dir(tmp_path, "")


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


def test_analyze_reports_unknown_only_selection_as_human_check(tmp_path: Path) -> None:
    write_all_templates(tmp_path)

    result = mcp_server_group.build_context(
        tmp_path,
        command="analyze",
        work_id="issue-unknown",
        components="unknown,also_unknown",
    )

    assert result["status"] == "human-check-required"
    assert result["selected_components"] == []
    assert result["unknown_components"] == ["unknown", "also-unknown"]
    assert "No known MCP components were selected." in result["human_checks"]
    assert "Unknown components: unknown, also-unknown" in result["human_checks"]


def test_analyze_flags_agent_runtime_without_mcp_client(tmp_path: Path) -> None:
    write_all_templates(tmp_path)

    result = mcp_server_group.build_context(
        tmp_path,
        command="analyze",
        work_id="issue-runtime",
        components="local-ai-agent-runtime",
    )

    assert result["status"] == "human-check-required"
    assert "Agent Runtime should use an MCP Client boundary before calling MCP Servers." in result["human_checks"]


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


def test_init_reports_existing_copies_and_force_refreshes_template(tmp_path: Path) -> None:
    write_all_templates(tmp_path)

    first = mcp_server_group.build_context(
        tmp_path,
        command="init",
        work_id="issue-force",
        components="mcp-client",
    )
    assert first["template_copies"][0]["status"] == "copied"

    output_readme = (
        tmp_path / "work" / "issue-force" / "implementation" / "mcp-server-group" / "mcp-client" / "README.md"
    )
    output_readme.write_text("# stale copy\n", encoding="utf-8")

    second = mcp_server_group.build_context(
        tmp_path,
        command="init",
        work_id="issue-force",
        components="mcp-client",
    )
    assert second["template_copies"][0]["status"] == "exists"
    assert output_readme.read_text(encoding="utf-8") == "# stale copy\n"

    refreshed = mcp_server_group.build_context(
        tmp_path,
        command="init",
        work_id="issue-force",
        components="mcp-client",
        force=True,
    )
    assert refreshed["template_copies"][0]["status"] == "copied"
    assert output_readme.read_text(encoding="utf-8") == "# mcp-client-template\n"


def test_init_reports_missing_template_without_copying(tmp_path: Path) -> None:
    write_template(tmp_path, "mcp-client-template")

    result = mcp_server_group.build_context(
        tmp_path,
        command="init",
        work_id="issue-missing",
        components="local-model-mcp-server,mcp-client",
    )

    copies = {item["component"]: item["status"] for item in result["template_copies"]}
    assert copies == {"local-model-mcp-server": "missing-template", "mcp-client": "copied"}


def test_explicit_work_dir_can_be_relative_or_absolute(tmp_path: Path) -> None:
    write_all_templates(tmp_path)

    relative = mcp_server_group.build_context(
        tmp_path,
        command="analyze",
        work_id="issue-relative",
        work_dir="custom/workdir",
        components="local-model-mcp-server",
    )
    assert relative["work_dir"] == "custom/workdir"

    absolute_dir = tmp_path / "absolute-workdir"
    absolute = mcp_server_group.build_context(
        tmp_path,
        command="analyze",
        work_id="issue-absolute",
        work_dir=str(absolute_dir),
        components="local-model-mcp-server",
    )
    assert absolute["work_dir"] == "absolute-workdir"


def test_format_result_includes_human_checks_and_artifacts() -> None:
    output = mcp_server_group.format_result(
        {
            "status": "human-check-required",
            "stage": "analyze",
            "work_dir": "work/issue-4",
            "components": [{"component": "discord-gateway", "role": "Discord operation gateway"}],
            "human_checks": ["Confirm runtime endpoint."],
            "artifacts": {
                "context": "work/issue-4/context/mcp-server-group-implementation-context.json",
                "report": "work/issue-4/reports/mcp-server-group-implementation-report.md",
            },
        }
    )

    assert "MCP Server Group Implementation" in output
    assert "discord-gateway: Discord operation gateway" in output
    assert "Confirm runtime endpoint." in output
    assert "context: work/issue-4/context/mcp-server-group-implementation-context.json" in output


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


def test_run_uses_explicit_repo_root_and_delegates_to_build_context(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_build_context(
        repo_root: Path,
        *,
        command: str,
        work_id: str,
        work_dir: str = "",
        components: str = "",
        force: bool = False,
    ) -> dict[str, object]:
        captured["repo_root"] = repo_root
        captured["command"] = command
        captured["work_id"] = work_id
        captured["work_dir"] = work_dir
        captured["components"] = components
        captured["force"] = force
        return {"status": "available"}

    monkeypatch.setattr(mcp_server_group, "build_context", fake_build_context)
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        command="run-workflow",
        work_id="issue-run",
        work_dir="custom/work",
        components="mcp-client",
        force=True,
    )

    result = mcp_server_group.run(args)

    assert result == {"status": "available"}
    assert captured == {
        "repo_root": tmp_path.resolve(),
        "command": "run-workflow",
        "work_id": "issue-run",
        "work_dir": "custom/work",
        "components": "mcp-client",
        "force": True,
    }
