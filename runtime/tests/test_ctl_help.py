from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from runtime import ctl


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_ctl_parser_uses_aiwfctl_program_name() -> None:
    parser = ctl.build_parser()

    assert parser.prog == "aiwfctl"


def test_ctl_without_modifier_warns_and_does_not_show_list() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root())])

    code, output = ctl.run(args)

    assert code == 1
    assert "警告" in output
    assert "aiwfctl help list" in output
    assert "aiwfctl path shell" in output
    assert "## Workflow Commands" not in output


def test_ctl_help_without_modifier_warns_and_does_not_show_list() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help"])

    code, output = ctl.run(args)

    assert code == 1
    assert "警告" in output
    assert "list / show / search / open / markdown" in output
    assert "aiwfctl path shell" in output
    assert "## Workflow Commands" not in output


def test_ctl_warning_can_be_colored_yellow() -> None:
    output = ctl.format_root_usage_warning(color=True)

    assert "\033[33m" in output
    assert "\033[0m" in output
    assert "aiwfctl help list" in output
    assert "aiwfctl path shell" in output
    assert "aiwfctl env select web-svg" in output


def test_ctl_env_select_gui_mode_returns_windows_msys2_profile() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "select", "gui-mode"])

    code, output = ctl.run(args)

    assert code == 0
    assert "Selected Environment : gui-mode" in output
    assert "Backend              : windows-msys2-gui" in output
    assert "windows-msys2-gui" in output
    assert "Workflow Context     : 未登録" in output
    assert "Initialization" in output


def test_ctl_env_select_web_svg_returns_wsl_web_profile() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "select", "web-svg", "--json"])

    code, output = ctl.run(args)

    assert code == 0
    assert '"name": "web-svg"' in output
    assert '"backend": "wsl-ubuntu-web"' in output
    assert '"id": "wsl-ubuntu-web"' in output
    assert "Node.js" in output
    assert "Playwright" in output


def test_ctl_env_select_unknown_requires_human_check() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "select", "unknown-runtime"])

    code, output = ctl.run(args)

    assert code == 2
    assert "Unknown environment : unknown-runtime" in output
    assert "Available Environments" in output
    assert "実行環境を特定できません" in output


def test_ctl_env_without_subcommand_shows_environment_management() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env"])

    code, output = ctl.run(args)

    assert code == 0
    assert "Environment Management" in output
    assert "Commands" in output
    assert "aiwfctl env list" in output
    assert "aiwfctl env show gui-mode" in output
    assert "Backend名は表示情報" in output


def test_ctl_env_list_shows_public_environments_not_raw_profile_list() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "list"])

    code, output = ctl.run(args)

    assert code == 0
    assert "Available Environments" in output
    assert "gui-mode" in output
    assert "Backend : windows-msys2-gui" in output
    assert "web-svg" in output
    assert "docker" in output


def test_ctl_env_show_uses_public_environment_name() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "show", "gui-mode"])

    code, output = ctl.run(args)

    assert code == 0
    assert "Environment : gui-mode" in output
    assert "Backend" in output
    assert "windows-msys2-gui" in output
    assert "Recommended for" in output
    assert "Required Tools" in output
    assert "Example Commands" in output
    assert "Context Output" in output
    assert "work/<work-id>/context/environment-selection.json" in output
    assert '"schema_version": "1.0"' in output


def test_ctl_env_select_tool_name_requires_human_check_with_candidate() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "env", "select", "pyqt"])

    code, output = ctl.run(args)

    assert code == 2
    assert "Unknown environment : pyqt" in output
    assert "利用者向けEnvironment名を指定してください" in output
    assert "Available Environments" in output
    assert "gui-mode" in output


def test_ctl_env_select_writes_workflow_context(tmp_path: Path) -> None:
    root = tmp_path
    source = repo_root()
    runtime_dir = root / "runtime" / "registries"
    schema_runtime = root / "runtime" / "tools"
    runtime_dir.mkdir(parents=True)
    schema_runtime.mkdir(parents=True)
    (runtime_dir / "workflow_environment_profiles.json").write_text(
        (source / "runtime" / "registries" / "workflow_environment_profiles.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (root / "runtime" / "workflow").mkdir(parents=True)
    (root / "runtime" / "workflow" / "workflow_doctor.py").write_text("", encoding="utf-8")
    (root / "runtime" / "tools" / "aiwfctl.cmd").write_text("", encoding="utf-8")
    (root / "runtime" / "registries" / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")
    args = ctl.build_parser().parse_args(
        ["--repo-root", str(root), "env", "select", "gui-mode", "--work-id", "issue-123"]
    )

    code, output = ctl.run(args)

    assert code == 0
    context_path = root / "work" / "issue-123" / "context" / "environment-selection.json"
    manifest_path = root / "work" / "issue-123" / "context" / "context-manifest.json"
    assert context_path.exists()
    assert manifest_path.exists()
    assert "work/issue-123/context/environment-selection.json" in output
    assert "work/issue-123/context/context-manifest.json" in output
    data = json.loads(context_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.0"
    assert data["artifact_type"] == "environment-selection-context"
    datetime.fromisoformat(data["selected_at"])
    assert data["selected_by"] in {"dispatcher", "human", "workflow"}
    assert data["selection_mode"] in {"manual", "auto", "human-check"}
    assert data["selected_by"] == "dispatcher"
    assert data["selection_mode"] == "manual"
    assert data["environment"] == "gui-mode"
    assert data["backend"] == "windows-msys2-gui"
    assert data["work_id"] == "issue-123"
    assert data["source"]["schema"] == ".github/schemas/environment-selection.schema.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["artifact_type"] == "context-manifest"
    assert manifest["architecture"] == "context-first"
    assert manifest["contexts"][0]["type"] == "environment-selection"
    assert manifest["contexts"][0]["owner"] == "dispatcher"


def test_ctl_env_select_warns_before_overwriting_different_context(tmp_path: Path) -> None:
    root = tmp_path
    source = repo_root()
    runtime_dir = root / "runtime" / "registries"
    runtime_tools = root / "runtime" / "tools"
    runtime_dir.mkdir(parents=True)
    runtime_tools.mkdir(parents=True)
    (runtime_dir / "workflow_environment_profiles.json").write_text(
        (source / "runtime" / "registries" / "workflow_environment_profiles.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (root / "runtime" / "workflow").mkdir(parents=True)
    (root / "runtime" / "workflow" / "workflow_doctor.py").write_text("", encoding="utf-8")
    (root / "runtime" / "tools" / "aiwfctl.cmd").write_text("", encoding="utf-8")
    (root / "runtime" / "registries" / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")
    context_path = root / "work" / "issue-123" / "context" / "environment-selection.json"
    context_path.parent.mkdir(parents=True)
    context_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "artifact_type": "environment-selection-context",
                "selected_at": "2026-07-05T00:00:00+00:00",
                "selected_by": "dispatcher",
                "selection_mode": "manual",
                "environment": "web-svg",
                "backend": "wsl-ubuntu-web",
                "reason": "previous",
                "work_id": "issue-123",
                "status": "selected",
                "human_check_required": False,
                "context_path": "work/issue-123/context/environment-selection.json",
                "source": {
                    "registry": "runtime/registries/workflow_environment_profiles.json",
                    "schema": ".github/schemas/environment-selection.schema.json",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    args = ctl.build_parser().parse_args(
        ["--repo-root", str(root), "env", "select", "gui-mode", "--work-id", "issue-123"]
    )

    code, output = ctl.run(args)

    assert code == 0
    assert "Warnings" in output
    assert "既存contextのenvironment `web-svg`" in output
    data = json.loads(context_path.read_text(encoding="utf-8"))
    assert data["environment"] == "gui-mode"
    assert data["backend"] == "windows-msys2-gui"
    assert data["warnings"]


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
    assert "runtime-context.json" in output


def test_realtime_iac_help_declares_docker_context_gate() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/realtime-iac"])

    code, output = ctl.run(args)

    assert code == 0
    assert "aiwfctl env select docker" in output
    assert "environment-selection.environment" in output


def test_robotics_new_system_iac_help_declares_execution_plan_handoff() -> None:
    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root()), "help", "show", "/robotics-new-system-iac"])

    code, output = ctl.run(args)

    assert code == 0
    assert "execution-plan.json" in output
    assert "realtime-iac-handoff.json" in output
    assert "iac_handoff_context.py" in output


def test_ctl_context_init_creates_phase3_contexts(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "/docs-sync",
                        "workflow": "docs-sync",
                        "overview": "docs only sync",
                        "aliases": [],
                    }
                ],
                "extensions": [],
            }
        ),
        encoding="utf-8",
    )
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "context",
            "init",
            "--work-id",
            "issue-9001",
            "--workflow",
            "/docs-sync",
            "--tool",
            "gh:read-only:GitHub metadata collection",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    assert "workflow-selection" in output
    assert "tool-selection" in output
    assert (tmp_path / "work" / "issue-9001" / "context" / "workflow-selection.json").exists()
    assert (tmp_path / "work" / "issue-9001" / "context" / "tool-selection.json").exists()


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


def test_environment_profile_registry_referenced_docs_exist() -> None:
    root = repo_root()
    registry = ctl.load_environment_registry(root)

    assert registry["environments"], "public environment registry is empty"
    for environment in registry["environments"]:
        assert environment.get("name"), "environment missing name"
        assert environment.get("backend"), f"{environment['name']} missing backend"
        ctl.profile_by_id(registry, environment["backend"])
    assert registry["profiles"], "environment profile registry is empty"
    for profile in registry["profiles"]:
        assert profile.get("id"), "environment profile missing id"
        for value in profile.get("docs", []):
            assert (root / value).exists(), f"{profile['id']} references missing {value}"
    for mapping in registry["mappings"]:
        assert mapping.get("profiles"), f"{mapping['subject']} missing profiles"
        for profile_id in mapping["profiles"]:
            ctl.profile_by_id(registry, profile_id)
        for value in mapping.get("docs", []):
            assert (root / value).exists(), f"{mapping['subject']} references missing {value}"


def test_ctl_registry_and_search_helper_edge_cases(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text("[]", encoding="utf-8")
    (registry_dir / "workflow_environment_profiles.json").write_text("[]", encoding="utf-8")

    try:
        ctl.load_registry(tmp_path)
    except ValueError as exc:
        assert "workflow help registry" in str(exc)
    else:
        raise AssertionError("non-object workflow help registry should fail")

    try:
        ctl.load_environment_registry(tmp_path)
    except ValueError as exc:
        assert "environment profiles registry" in str(exc)
    else:
        raise AssertionError("non-object environment profile registry should fail")

    registry = {
        "commands": [{"command": "/b"}, {"command": "/a", "aliases": ["/alias-a"], "overview": "alpha"}],
        "extensions": [{"name": "z-ext"}, {"name": "a-ext", "aliases": ["alias-ext"], "overview": "alpha"}],
    }

    assert ctl.normalize_command("docs-sync") == "/docs-sync"
    assert ctl.normalize_command(" /already ") == "/already"
    assert ctl.find_command(registry, "alias-a")["command"] == "/a"
    assert ctl.find_help_item(registry, "alias-ext")[0] == "extension"
    assert [item["command"] for item in ctl.search_commands(registry, [" "])] == ["/a", "/b"]
    assert [item["name"] for item in ctl.search_extensions(registry, [" "])] == ["a-ext", "z-ext"]
    assert ctl.profile_key({"id": "B"}) == "b"

    try:
        ctl.find_extension(registry, "missing")
    except KeyError as exc:
        assert "Unknown workflow extension" in str(exc)
    else:
        raise AssertionError("unknown extension should fail")


def test_ctl_environment_selection_mapping_branches() -> None:
    registry = {
        "environments": [
            {"name": "env-a", "backend": "p1", "purpose": "A"},
            {"name": "env-b", "backend": "p2", "purpose": "B"},
        ],
        "profiles": [
            {"id": "p1", "aliases": ["profile-a"], "docs": ["docs/a.md"], "primary_tools": ["Git"]},
            {"id": "p2", "aliases": [], "docs": ["docs/b.md"], "primary_tools": ["Docker"]},
        ],
        "mappings": [
            {"subject_type": "command", "subject": "/mapped", "profiles": ["p1"], "selection_reason": "mapped"},
            {"subject_type": "keyword", "subject": "gui pyqt", "profiles": ["p1"], "selection_reason": "keyword-a"},
            {"subject_type": "keyword", "subject": "gui web", "profiles": ["p2"], "selection_reason": "keyword-b"},
            {"subject_type": "unknown", "subject": "never", "profiles": ["p1"]},
        ],
    }

    assert ctl.find_public_environment_by_backend(registry, "missing") is None
    assert ctl.find_environment_profile(registry, "profile-a")["id"] == "p1"
    assert not ctl.environment_mapping_matches({"subject_type": "unknown", "subject": "x"}, "x")

    mapped = ctl.select_environment(registry, "/mapped")
    assert mapped["status"] == "selected"
    assert mapped["environment"]["name"] == "env-a"
    assert mapped["profiles"][0]["id"] == "p1"

    keyword = ctl.select_environment(registry, "please use gui")
    assert keyword["status"] == "human-check-required"
    assert {item["name"] for item in keyword["candidate_environments"]} == {"env-a", "env-b"}

    try:
        ctl.profile_by_id(registry, "missing")
    except KeyError as exc:
        assert "Unknown environment profile id" in str(exc)
    else:
        raise AssertionError("unknown profile id should fail")


def test_ctl_environment_formatting_and_context_warning_helpers(tmp_path: Path) -> None:
    profile = {
        "id": "p1",
        "title": "Profile One",
        "environment": "Windows",
        "shell": "PowerShell",
        "os": "Windows",
        "summary": "summary",
        "primary_tools": ["Git", "Python"],
        "run_command": "run",
        "preflight_profile": "",
        "applies_when": [],
        "verification": [],
        "human_check_required_when": [],
        "docs": [],
    }
    formatted_profile = ctl.format_environment_profile(profile)
    assert "Profile One" in formatted_profile
    assert "Git, Python" in formatted_profile

    human_check = ctl.format_environment_human_check(
        {
            "target": "gui",
            "status": "human-check-required",
            "human_check_reasons": ["choose explicitly"],
            "candidate_environments": [{"name": "gui-mode", "backend": "windows", "purpose": "GUI"}],
        }
    )
    assert "Environment Human Check Required" in human_check
    assert "gui-mode" in human_check

    context = {
        "work_id": "issue-2",
        "environment": "gui-mode",
        "backend": "windows-msys2-gui",
    }
    assert not ctl.environment_context_warnings({}, context)
    assert ctl.environment_context_warnings("broken", context)
    warnings = ctl.environment_context_warnings(
        {"work_id": "issue-1", "environment": "web-svg", "backend": "wsl-ubuntu-web"},
        context,
    )
    assert len(warnings) == 3

    record = {
        "status": "selected",
        "target": "gui-mode",
        "environment": {"name": "gui-mode", "backend": "windows-msys2-gui", "recommended_for": []},
        "mapping": {"selection_reason": "manual"},
        "profiles": [profile],
        "human_check_required": False,
        "created_at": "2026-07-07T00:00:00+00:00",
    }
    context_record = ctl.environment_context_record(
        record,
        work_id="issue-7",
        selected_by="human",
        selection_mode="auto",
    )
    assert context_record["selected_by"] == "human"
    assert context_record["selection_mode"] == "auto"
    assert context_record["context_path"] == "work/issue-7/context/environment-selection.json"

    output_json = tmp_path / "environment-selection.json"
    output_md = tmp_path / "environment-selection.md"
    assert ctl.write_environment_selection(tmp_path, record.copy(), output=str(output_json)) == [
        "environment-selection.json"
    ]
    assert json.loads(output_json.read_text(encoding="utf-8"))["target"] == "gui-mode"
    assert ctl.write_environment_selection(tmp_path, record.copy(), output=str(output_md)) == [
        "environment-selection.md"
    ]
    assert "Selected Environment" in output_md.read_text(encoding="utf-8")


def test_ctl_help_formatting_empty_lists_and_open_search_paths(tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    registry = {
        "description": "minimal help",
        "commands": [
            {
                "command": "/alpha",
                "workflow": "alpha",
                "overview": "alpha overview",
                "arguments": [],
                "docs": [],
                "examples": [],
                "details": [],
                "prerequisites": [],
                "related_runtime": [],
            }
        ],
        "extensions": [],
    }
    (registry_dir / "workflow_help.json").write_text(json.dumps(registry), encoding="utf-8")

    assert "なし" in ctl.format_arg_table("empty", [])
    assert ctl.format_prerequisites_for_list([])
    assert ctl.format_docs_for_list([])

    open_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "help", "open", "--query", "alpha"])
    code, output = ctl.run(open_args)
    assert code == 0
    assert "# AI Workflow Help" in output
    assert "/alpha" in output

    markdown_args = ctl.build_parser().parse_args(
        ["--repo-root", str(tmp_path), "help", "markdown", "--output", "work/help/out.md"]
    )
    code, output = ctl.run(markdown_args)
    assert code == 0
    assert "wrote: work/help/out.md" in output
    assert (tmp_path / "work" / "help" / "out.md").exists()

    search_args = ctl.build_parser().parse_args(["--repo-root", str(tmp_path), "help", "search", "missing"])
    code, output = ctl.run(search_args)
    assert code == 1
    assert "workflow help" in output


def test_ctl_color_mode_and_main_output(monkeypatch, capsys) -> None:
    class TtyStream:
        def isatty(self) -> bool:
            return True

    class NonTtyStream:
        def isatty(self) -> bool:
            return False

    monkeypatch.setenv("AIWFCTL_COLOR", "always")
    assert ctl.should_use_color(NonTtyStream())
    monkeypatch.setenv("AIWFCTL_COLOR", "never")
    assert not ctl.should_use_color(TtyStream())
    monkeypatch.delenv("AIWFCTL_COLOR", raising=False)
    monkeypatch.setenv("NO_COLOR", "1")
    assert not ctl.should_use_color(TtyStream())
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert ctl.should_use_color(TtyStream())
    assert not ctl.should_use_color(NonTtyStream())

    code = ctl.main(["--repo-root", str(repo_root()), "help", "search", "svg"])
    captured = capsys.readouterr()
    assert code == 0
    assert "# AI Workflow Help" in captured.out


def test_ctl_run_manual_error_and_json_branches(monkeypatch, tmp_path: Path) -> None:
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text(
        json.dumps({"commands": [], "extensions": []}),
        encoding="utf-8",
    )
    (registry_dir / "workflow_environment_profiles.json").write_text(
        json.dumps({"environments": [], "profiles": [], "mappings": []}),
        encoding="utf-8",
    )

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="unknown"))
    assert code == 1
    assert "Unknown command: unknown" in output

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="env", env_command="unknown"))
    assert code == 1
    assert "Unknown env command: unknown" in output

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="context", context_command=None))
    assert code == 1
    assert "Context Management" in output

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="context", context_command="unknown"))
    assert code == 1
    assert "Unknown context command: unknown" in output

    code, output = ctl.run(SimpleNamespace(repo_root=str(tmp_path), command="help", help_command="unknown"))
    assert code == 1
    assert "Unknown help command: unknown" in output

    monkeypatch.setattr(
        ctl.dispatcher_context,
        "run_init",
        lambda args: {
            "status": "human-check-required",
            "work_id": "issue-1",
            "workflow": "/docs-sync",
            "manifest_path": "work/issue-1/context/context-manifest.json",
            "contexts": ["workflow-selection"],
            "written": ["work/issue-1/context/workflow-selection.json"],
        },
    )
    code, output = ctl.run(
        SimpleNamespace(repo_root=str(tmp_path), command="context", context_command="init", json=True)
    )
    assert code == 2
    assert '"status": "human-check-required"' in output
