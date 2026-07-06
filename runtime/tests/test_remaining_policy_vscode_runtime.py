from __future__ import annotations

import argparse
import json
import runpy
import subprocess
import sys
import types
from pathlib import Path

import pytest

from runtime.workflow import human_gate_policy, vscode_task_runner


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    return repo


def write_human_gate_registry(repo: Path) -> None:
    path = repo / "runtime" / "registries" / "human_gates.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "gates": [
                    {
                        "id": "close-prune",
                        "requires_human_check": True,
                        "approved_value": "approved",
                        "reason": "削除操作には人間承認が必要です。",
                    },
                    {
                        "id": "read-only",
                        "requires_human_check": False,
                        "approved_value": "approved",
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_human_gate_policy_load_registry_defaults_when_missing(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    registry = human_gate_policy.load_registry(repo)

    assert registry["registry_version"] == "1.0"
    assert registry["gates"] == []


def test_human_gate_policy_load_registry_adds_defaults_for_partial_file(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    path = repo / "runtime" / "registries" / "human_gates.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")

    registry = human_gate_policy.load_registry(repo)

    assert registry == {"registry_version": "1.0", "gates": []}


def test_human_gate_policy_list_returns_registry_path_and_gates(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_human_gate_registry(repo)
    args = argparse.Namespace(repo_root=str(repo))

    result = human_gate_policy.run_list(args)

    assert result["status"] == "ok"
    assert result["registry"] == "runtime/registries/human_gates.json"
    assert result["gates"][0]["id"] == "close-prune"


def test_human_gate_policy_check_blocks_pending_human_approval(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_human_gate_registry(repo)
    args = argparse.Namespace(repo_root=str(repo), gate="close-prune", human_check="pending")

    result = human_gate_policy.run_check(args)

    assert result == {
        "status": "blocked",
        "gate": "close-prune",
        "required": "approved",
        "actual": "pending",
        "reason": "削除操作には人間承認が必要です。",
    }


def test_human_gate_policy_check_approves_when_value_matches(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_human_gate_registry(repo)
    args = argparse.Namespace(repo_root=str(repo), gate="close-prune", human_check="approved")

    result = human_gate_policy.run_check(args)

    assert result["status"] == "approved"
    assert result["gate"] == "close-prune"


def test_human_gate_policy_non_required_gate_does_not_block(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_human_gate_registry(repo)
    args = argparse.Namespace(repo_root=str(repo), gate="read-only", human_check="pending")

    result = human_gate_policy.run_check(args)

    assert result["status"] == "approved"
    assert result["actual"] == "pending"


def test_human_gate_policy_unknown_gate_raises_key_error(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_human_gate_registry(repo)

    with pytest.raises(KeyError, match="Unknown human gate"):
        human_gate_policy.find_gate(human_gate_policy.load_registry(repo), "missing")


def test_human_gate_policy_main_list_prints_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(tmp_path)
    write_human_gate_registry(repo)

    code = human_gate_policy.main(["--repo-root", str(repo), "list"])

    captured = capsys.readouterr()
    assert code == 0
    assert '"status": "ok"' in captured.out
    assert "runtime/registries/human_gates.json" in captured.out
    assert "close-prune" in captured.out


def test_human_gate_policy_main_check_returns_one_when_blocked(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = make_repo(tmp_path)
    write_human_gate_registry(repo)

    code = human_gate_policy.main(
        ["--repo-root", str(repo), "check", "--gate", "close-prune", "--human-check", "pending"]
    )

    captured = capsys.readouterr()
    assert code == 1
    assert '"status": "blocked"' in captured.out
    assert '"actual": "pending"' in captured.out


def test_human_gate_policy_main_reports_error_for_unknown_gate(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = make_repo(tmp_path)
    write_human_gate_registry(repo)

    code = human_gate_policy.main(["--repo-root", str(repo), "check", "--gate", "missing"])

    captured = capsys.readouterr()
    assert code == 1
    assert "Unknown human gate: missing" in captured.err

    namespace = runpy.run_path(str(Path(human_gate_policy.__file__)))
    assert namespace["build_parser"]


def test_vscode_task_runner_refreshed_env_merges_registry_and_extra(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vscode_task_runner, "windows_registry_paths", lambda: ["C:/Registry/bin"])
    monkeypatch.setenv("PATH", "C:/Current/bin")

    env = vscode_task_runner.refreshed_env({"CUSTOM": "yes"})

    assert env["CUSTOM"] == "yes"
    assert env["PATH"].split(vscode_task_runner.os.pathsep)[:2] == ["C:/Registry/bin", "C:/Current/bin"]


def test_vscode_task_runner_find_executable_uses_fallback(tmp_path: Path) -> None:
    fallback = tmp_path / "tool.exe"
    fallback.write_text("", encoding="utf-8")

    assert vscode_task_runner.find_executable("missing-tool", {"PATH": ""}, [fallback]) == str(fallback)
    assert vscode_task_runner.find_executable("missing-tool", {"PATH": ""}, []) is None


def test_vscode_task_runner_run_process_uses_cwd_and_returns_code(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(command, cwd, env, check):
        calls.append({"command": command, "cwd": cwd, "env": env, "check": check})
        return subprocess.CompletedProcess(command, 7)

    monkeypatch.setattr(vscode_task_runner.subprocess, "run", fake_run)

    code = vscode_task_runner.run_process(["tool", "arg"], env={"PATH": "x"}, cwd=tmp_path)

    assert code == 7
    assert calls == [
        {
            "command": ["tool", "arg"],
            "cwd": str(tmp_path),
            "env": {"PATH": "x"},
            "check": False,
        }
    ]


def test_vscode_task_runner_command_display_posix_quotes_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vscode_task_runner.os, "name", "posix")

    assert vscode_task_runner.command_display(["tool", "two words"]) == "tool 'two words'"


def test_vscode_task_runner_windows_registry_paths_returns_empty_on_non_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vscode_task_runner.os, "name", "posix")

    assert vscode_task_runner.windows_registry_paths() == []


def test_vscode_task_runner_run_open_questions_invokes_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run_process(command, env=None, cwd=None):
        calls.append(list(command))
        return 3

    monkeypatch.setattr(vscode_task_runner, "run_process", fake_run_process)

    code = vscode_task_runner.run_open_questions(argparse.Namespace(work_id="issue-42"))

    assert code == 3
    assert calls == [
        [
            vscode_task_runner.sys.executable,
            "runtime/workflow/vscode_environment.py",
            "open-questions",
            "--work-id",
            "issue-42",
        ]
    ]


def test_vscode_task_runner_run_preflight_uses_refreshed_env(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], dict[str, str] | None]] = []

    def fake_run_process(command, env=None, cwd=None):
        calls.append((list(command), env))
        return 0

    monkeypatch.setattr(vscode_task_runner, "refreshed_env", lambda extra=None: {"PATH": "refreshed"})
    monkeypatch.setattr(vscode_task_runner, "run_process", fake_run_process)

    code = vscode_task_runner.run_preflight(argparse.Namespace(work_id="vscode-env", source_dir="work/source"))

    assert code == 0
    assert calls == [
        (
            [
                vscode_task_runner.sys.executable,
                "runtime/environment/preflight.py",
                "--profile",
                "vscode-environment",
                "--work-id",
                "vscode-env",
                "--source-dir",
                "work/source",
            ],
            {"PATH": "refreshed"},
        )
    ]


def test_vscode_task_runner_run_helper_help_invokes_vscode_environment_help(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(vscode_task_runner, "run_process", lambda command, env=None, cwd=None: calls.append(list(command)) or 0)

    assert vscode_task_runner.run_helper_help(argparse.Namespace()) == 0
    assert calls == [[vscode_task_runner.sys.executable, "runtime/workflow/vscode_environment.py", "--help"]]


def test_vscode_task_runner_msys2_smoke_reports_missing_bash(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(vscode_task_runner.Path, "exists", lambda self: False)

    code = vscode_task_runner.run_msys2_localty_smoke(argparse.Namespace())

    captured = capsys.readouterr()
    assert code == 1
    assert "MSYS2 bash was not found" in captured.err


def test_vscode_task_runner_run_docker_version_reports_missing_docker(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(vscode_task_runner, "refreshed_env", lambda extra=None: {"PATH": ""})
    monkeypatch.setattr(vscode_task_runner, "find_executable", lambda name, env, fallbacks=(): None)

    code = vscode_task_runner.run_docker_version(argparse.Namespace())

    captured = capsys.readouterr()
    assert code == 1
    assert "docker executable was not found" in captured.err


def test_vscode_task_runner_run_docker_version_uses_found_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vscode_task_runner, "refreshed_env", lambda extra=None: {"PATH": "C:/Docker"})
    monkeypatch.setattr(vscode_task_runner, "find_executable", lambda name, env, fallbacks=(): "C:/Docker/docker.exe")
    calls: list[tuple[list[str], dict[str, str]]] = []

    def fake_run_process(command, env=None, cwd=None):
        calls.append((list(command), env))
        return 0

    monkeypatch.setattr(vscode_task_runner, "run_process", fake_run_process)

    assert vscode_task_runner.run_docker_version(argparse.Namespace()) == 0
    assert calls == [(["C:/Docker/docker.exe", "version"], {"PATH": "C:/Docker"})]


def test_vscode_task_runner_run_go_version_reports_missing_go(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(vscode_task_runner, "refreshed_env", lambda extra=None: {"PATH": ""})
    monkeypatch.setattr(vscode_task_runner, "find_executable", lambda name, env, fallbacks=(): None)

    code = vscode_task_runner.run_go_version(argparse.Namespace())

    captured = capsys.readouterr()
    assert code == 1
    assert "go executable was not found" in captured.err


def test_vscode_task_runner_run_go_version_uses_found_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vscode_task_runner, "refreshed_env", lambda extra=None: {"PATH": "C:/Go/bin"})
    monkeypatch.setattr(vscode_task_runner, "find_executable", lambda name, env, fallbacks=(): "C:/Go/bin/go.exe")
    calls: list[tuple[list[str], dict[str, str]]] = []

    def fake_run_process(command, env=None, cwd=None):
        calls.append((list(command), env))
        return 0

    monkeypatch.setattr(vscode_task_runner, "run_process", fake_run_process)

    assert vscode_task_runner.run_go_version(argparse.Namespace()) == 0
    assert calls == [(["C:/Go/bin/go.exe", "version"], {"PATH": "C:/Go/bin"})]


def test_vscode_task_runner_skill_info_prints_command_and_skill(capsys: pytest.CaptureFixture[str]) -> None:
    code = vscode_task_runner.run_skill_info(
        argparse.Namespace(command_name="/vscode-environment", skill="skills/vscode-environment/SKILL.md")
    )

    captured = capsys.readouterr()
    assert code == 0
    assert "Codex Skill: /vscode-environment" in captured.out
    assert "skills/vscode-environment/SKILL.md" in captured.out


def test_vscode_task_runner_main_dispatches_skill_info(capsys: pytest.CaptureFixture[str]) -> None:
    code = vscode_task_runner.main(
        [
            "skill-info",
            "--command",
            "/vscode-environment",
            "--skill",
            "skills/vscode-environment/SKILL.md",
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    assert "Codex Skill: /vscode-environment" in captured.out


def test_vscode_task_runner_windows_registry_and_remaining_edges(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    assert (vscode_task_runner.repo_root() / "runtime").exists()

    class FakeKey:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    fake_winreg = types.SimpleNamespace(
        HKEY_LOCAL_MACHINE="HKLM",
        HKEY_CURRENT_USER="HKCU",
    )
    calls: list[str] = []

    def fake_open_key(hive, subkey):
        calls.append(str(hive))
        if hive == "HKLM":
            raise OSError("missing")
        return FakeKey()

    query_values = iter(["", "%USERPROFILE%/bin"])

    def fake_query_value_ex(key, name):
        return (next(query_values), None)

    fake_winreg.OpenKey = fake_open_key
    fake_winreg.QueryValueEx = fake_query_value_ex
    monkeypatch.setitem(sys.modules, "winreg", fake_winreg)
    monkeypatch.setattr(vscode_task_runner.os, "name", "nt")
    monkeypatch.setattr(vscode_task_runner.os.path, "expandvars", lambda value: value.replace("%USERPROFILE%", "C:/Users/A"))

    assert vscode_task_runner.windows_registry_paths() == []
    assert calls == ["HKLM", "HKCU"]

    calls.clear()
    query_values = iter(["", "%USERPROFILE%/bin"])
    fake_winreg.OpenKey = lambda hive, subkey: FakeKey()
    assert vscode_task_runner.windows_registry_paths() == ["C:/Users/A/bin"]

    monkeypatch.setattr(vscode_task_runner.shutil, "which", lambda name, path=None: "C:/Tools/tool.exe")
    assert vscode_task_runner.find_executable("tool", {"PATH": "C:/Tools"}) == "C:/Tools/tool.exe"

    missing = tmp_path / "missing.exe"
    existing = tmp_path / "existing.exe"
    existing.write_text("", encoding="utf-8")
    monkeypatch.setattr(vscode_task_runner.shutil, "which", lambda name, path=None: None)
    assert vscode_task_runner.find_executable("tool", {"PATH": ""}, [missing, existing]) == str(existing)

    monkeypatch.setattr(vscode_task_runner, "windows_registry_paths", lambda: [])
    monkeypatch.setattr(vscode_task_runner.os, "environ", {"PATH": ""})
    assert vscode_task_runner.refreshed_env() == {"PATH": ""}

    command = vscode_task_runner.command_display(["tool.exe", "two words"])
    assert "two words" in command

    bash = tmp_path / "bash.exe"
    bash.write_text("", encoding="utf-8")
    monkeypatch.setattr(vscode_task_runner.Path, "exists", lambda self: True)
    calls_process: list[tuple[list[str], dict[str, str] | None]] = []

    def fake_run_process(command, env=None, cwd=None):
        calls_process.append((list(command), env))
        return 0

    monkeypatch.setattr(vscode_task_runner, "refreshed_env", lambda extra=None: {"PATH": "x", **(extra or {})})
    monkeypatch.setattr(vscode_task_runner, "run_process", fake_run_process)

    assert vscode_task_runner.run_msys2_localty_smoke(argparse.Namespace()) == 0
    assert calls_process[0][0][1:] == ["-lc", "python --version; gst-launch-1.0 --version"]
    assert calls_process[0][1]["MSYSTEM"] == "MINGW64"

    namespace = runpy.run_path(str(Path(vscode_task_runner.__file__)))
    assert namespace["build_parser"]
