from __future__ import annotations

from pathlib import Path

from runtime import ctl


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_ctl_parser_uses_aiwfctl_program_name() -> None:
    parser = ctl.build_parser()

    assert parser.prog == "aiwfctl"


def test_ctl_help_list_contains_workflow_commands() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "list"])

    code, output = ctl.run(args)

    assert code == 0
    assert "/requirement-discovery" in output
    assert "/corrective-action-fix" in output
    assert "必須" in output
    assert " / 必須:" not in output
    assert "\n  概要:" in output
    assert "\n  前提:\n    - " in output
    assert all(" / " not in line for line in output.splitlines() if line.startswith("  前提:"))
    assert "\n  必須:" in output
    assert "\n  docs:\n    - docs/workflows/requirement-discovery.md" in output
    assert "docs/workflows/corrective-action-fix.md" in output
    assert "## Workflow Extensions" in output
    assert "gac-uac-gui-mode" in output
    assert "web-svg-layout-mode" in output
    assert "docs/workflows/gui-mode.md" in output


def test_ctl_help_show_includes_arguments_and_details() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/docs-sync"])

    code, output = ctl.run(args)

    assert code == 0
    assert "## /docs-sync" in output
    assert "`repository`" in output
    assert "`branch`" in output
    assert "前提条件" in output
    assert "処理の詳細" in output


def test_corrective_action_fix_help_declares_report_source() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/corrective-action-fix"])

    code, output = ctl.run(args)

    assert code == 0
    assert "/corrective-action-report" in output
    assert "`report`" in output
    assert "| `report` | no |" in output
    assert "未指定の場合、このflow内でCorrective Action Reportを作成する" in output


def test_vscode_environment_help_declares_repo_local_tools_path() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/vscode-environment"])

    code, output = ctl.run(args)

    assert code == 0
    assert "self-provision mode" in output
    assert "target-workspace mode" in output
    assert "custom-design mode" in output
    assert "runtime/tools" in output
    assert "terminal.integrated.env.windows.Path" in output


def test_ctl_help_search_finds_svg_gui_workflows() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "search", "svg", "gui"])

    code, output = ctl.run(args)

    assert code == 0
    assert "/robotics-new-system" in output
    assert "/corrective-action-fix" in output
    assert "gac-uac-gui-mode" in output


def test_ctl_help_show_includes_svg_extension_details() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "gui-mode"])

    code, output = ctl.run(args)

    assert code == 0
    assert "## gac-uac-gui-mode" in output
    assert "workflow extension" in output
    assert "前提条件" in output
    assert "SYS_" in output
    assert "FEAT_" in output
    assert "FIX_" in output
    assert "standalone command: `false`" in output


def test_ctl_help_markdown_writes_searchable_file(tmp_path: Path) -> None:
    output_path = tmp_path / "help.md"
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root()),
            "help",
            "markdown",
            "--output",
            str(output_path),
            "--query",
            "rag",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    assert "wrote:" in output
    text = output_path.read_text(encoding="utf-8")
    assert "# AI Workflow Help" in text
    assert "/rag-load" in text


def test_workflow_help_registry_referenced_files_exist() -> None:
    root = repo_root()
    registry = ctl.load_registry(root)

    for command in registry["commands"]:
        assert command.get("prerequisites"), f"{command['command']} missing prerequisites"
        for key in ["skill_path", "prompt_path"]:
            value = command.get(key, "")
            assert value, f"{command['command']} missing {key}"
            assert (root / value).exists(), f"{command['command']} references missing {value}"
        for value in command.get("docs", []):
            assert (root / value).exists(), f"{command['command']} references missing {value}"
        for value in command.get("related_runtime", []):
            assert (root / value).exists(), f"{command['command']} references missing {value}"
    for extension in registry["extensions"]:
        assert extension.get("prerequisites"), f"{extension['name']} missing prerequisites"
        for value in extension.get("docs", []):
            assert (root / value).exists(), f"{extension['name']} references missing {value}"
        for value in extension.get("related_runtime", []):
            assert (root / value).exists(), f"{extension['name']} references missing {value}"
