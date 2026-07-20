from __future__ import annotations

import argparse
import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from runtime.environment import preflight


def test_docker_compose_check_reports_missing_docker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight.shutil, "which", lambda name: None)

    check = preflight.docker_compose_check(required=True)

    assert check.id == "docker-plugin:compose"
    assert check.required is True
    assert check.ok is False
    assert "Docker Desktop" in check.install_hint
    assert check.install_command == "winget install --id Docker.DockerDesktop -e"


def test_basic_checks_report_detected_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(preflight.shutil, "which", lambda name: f"C:/tools/{name}.exe" if name == "git" else None)

    exe = preflight.which_check("git", required=True, install_hint="install git")
    missing = preflight.which_check("uv", required=True, install_hint="install uv", install_command="winget install uv")
    fallback_exe = tmp_path / "fallback-tool.cmd"
    fallback_exe.write_text("@echo off\n", encoding="utf-8")
    fallback = preflight.which_check(
        "fallback-tool",
        required=True,
        install_hint="install fallback tool",
        fallback_paths=[fallback_exe],
    )
    existing_path = preflight.path_check(
        tmp_path,
        check_id="path:repo",
        label="repo",
        required=True,
        install_hint="create repo",
    )
    missing_path = preflight.path_check(
        tmp_path / "missing",
        check_id="path:missing",
        label="missing",
        required=False,
        install_hint="create missing",
    )

    assert exe.ok is True
    assert exe.detected == "C:/tools/git.exe"
    assert missing.ok is False
    assert missing.install_command == "winget install uv"
    baseline_checks = preflight.build_checks(
        argparse.Namespace(
            profile="minimal",
            source_dir="",
            protocol_dir="",
            support_branch="develop",
            msys2_root=str(tmp_path / "msys64"),
            work_id="issue-1",
        ),
        tmp_path,
    )
    assert next(check for check in baseline_checks if check.id == "exe:git").install_command == "winget install --id Git.Git -e"
    assert fallback.ok is True
    assert fallback.detected == str(fallback_exe)
    assert existing_path.to_dict()["detected"] == str(tmp_path)
    assert missing_path.to_dict()["detected"] == ""


def test_preflight_parser_accepts_runtime_dev_profile() -> None:
    args = preflight.build_parser().parse_args(["--profile", "runtime-dev"])

    assert args.profile == "runtime-dev"


def test_uv_runtime_check_uses_repo_local_wrapper_when_uv_is_not_on_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(preflight.shutil, "which", lambda name: None)
    uv_cmd = tmp_path / "runtime" / "windows-script" / "uv.cmd"
    uv_cmd.parent.mkdir(parents=True)
    uv_cmd.write_text("@echo off\n", encoding="utf-8")

    check = preflight.uv_runtime_check(tmp_path)

    assert check.ok is True
    assert check.detected == str(uv_cmd)
    assert "register-uv-path.cmd" in (check.install_command or "")


def test_windows_aiwf_cmd_wraps_powershell_with_process_bypass() -> None:
    root = Path(__file__).resolve().parents[2]
    wrapper = root / "runtime" / "windows-script" / "aiwf.cmd"

    text = wrapper.read_text(encoding="utf-8")
    tools_cmd_files = list((root / "runtime" / "tools").glob("*.cmd"))

    assert "powershell -NoProfile -ExecutionPolicy Bypass -File" in text
    assert "%~dp0aiwf.ps1" in text
    assert tools_cmd_files == []


def test_env_path_check_reads_repo_env(tmp_path: Path) -> None:
    terraform = tmp_path / "terraform.exe"
    terraform.write_text("", encoding="utf-8")
    (tmp_path / ".env").write_text(f"AIWF_TERRAFORM_EXE={terraform}\n", encoding="utf-8")

    check = preflight.env_path_check(
        tmp_path,
        "AIWF_TERRAFORM_EXE",
        label="AIWF_TERRAFORM_EXE",
        required=True,
        install_hint="set env",
    )

    assert check.ok is True
    assert check.detected == str(terraform)


def test_python_module_check_uses_current_interpreter(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command, cwd=None, env=None):
        calls.append(list(command))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(preflight, "run_command", fake_run)

    check = preflight.python_module_check("pytest", required=False, install_hint="install pytest")

    assert check.ok is True
    assert check.detected == sys.executable
    assert calls == [[sys.executable, "-c", "import pytest"]]


def test_runtime_pytest_check_uses_uv_project_command(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    uv_cmd = tmp_path / "runtime" / "windows-script" / "uv.cmd"
    uv_cmd.parent.mkdir(parents=True)
    uv_cmd.write_text("@echo off\n", encoding="utf-8")
    monkeypatch.setattr(preflight.shutil, "which", lambda name: None)
    calls: list[list[str]] = []

    def fake_run(command, cwd=None, env=None):
        calls.append(list(command))
        assert cwd == tmp_path
        return subprocess.CompletedProcess(command, 0, stdout="pytest 9.9.9\n", stderr="")

    monkeypatch.setattr(preflight, "run_command", fake_run)

    check = preflight.runtime_pytest_check(tmp_path, required=True)

    assert check.ok is True
    assert check.detected == "pytest 9.9.9"
    assert calls == [[str(uv_cmd), "run", "--project", "runtime", "--group", "dev", "pytest", "--version"]]


def test_docker_compose_check_uses_compose_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight.shutil, "which", lambda name: "C:/Program Files/Docker/docker.exe")

    def fake_run(command: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        assert command == ["docker", "compose", "version"]
        return subprocess.CompletedProcess(command, 0, stdout="Docker Compose version v2.99.0\n", stderr="")

    monkeypatch.setattr(preflight, "run_command", fake_run)

    check = preflight.docker_compose_check(required=True)

    assert check.ok is True
    assert check.detected == "Docker Compose version v2.99.0"


def test_docker_compose_check_reports_compose_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight.shutil, "which", lambda name: "C:/Program Files/Docker/docker.exe")
    monkeypatch.setattr(
        preflight,
        "run_command",
        lambda command, cwd=None, env=None: subprocess.CompletedProcess(command, 1, stdout="", stderr="compose missing\n"),
    )

    check = preflight.docker_compose_check(required=True)

    assert check.ok is False
    assert check.detected == "compose missing"


def test_github_cli_checks_split_version_auth_and_env_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(preflight.shutil, "which", lambda name: f"C:/tools/{name}.exe")
    monkeypatch.setattr(preflight, "load_env", lambda repo_root: {"GITHUB_TOKEN": "secret-token"})

    def fake_run(command, cwd=None, env=None):
        calls.append(list(command))
        if command == ["gh", "--version"]:
            return subprocess.CompletedProcess(command, 0, stdout="gh version 2.99.0\n", stderr="")
        if command == ["gh", "auth", "status", "--hostname", "github.com"]:
            return subprocess.CompletedProcess(command, 1, stdout="", stderr="not logged in ghp_exampletoken\n")
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(preflight, "run_command", fake_run)

    checks = preflight.build_checks(
        argparse.Namespace(
            profile="github-cli",
            source_dir="",
            protocol_dir="",
            support_branch="develop",
            msys2_root=str(tmp_path / "msys64"),
            work_id="github/original/recent",
            github_hostname="github.com",
        ),
        tmp_path,
    )

    version = next(check for check in checks if check.id == "github-cli:version")
    token = next(check for check in checks if check.id == "env:github-token")
    auth = next(check for check in checks if check.id == "github-cli:auth")
    assert ["gh", "--version"] in calls
    assert ["gh", "auth", "status", "--hostname", "github.com"] in calls
    assert version.ok is True
    assert token.ok is True
    assert token.detected == "configured (masked)"
    assert auth.ok is False
    assert "ghp_exampletoken" not in auth.detected
    assert auth.kind == "github-auth"
    assert auth.install_command is None
    assert "--gh-login-from-env" in (auth.action_command or "")
    assert preflight.github_auth_status(checks) == "auth-required"


def test_gh_login_from_env_uses_token_stdin_and_sanitizes_report(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    commands: list[tuple[list[str], str | None]] = []
    monkeypatch.setattr(preflight.shutil, "which", lambda name: f"C:/tools/{name}.exe")
    monkeypatch.setattr(preflight, "load_env", lambda repo_root: {"GH_TOKEN": "secret-token"})
    monkeypatch.setattr(
        preflight,
        "run_command",
        lambda command, cwd=None, env=None: subprocess.CompletedProcess(command, 0, stdout="gh version 2.99.0\n", stderr=""),
    )

    def fake_subprocess_run(command, input=None, text=None, stdout=None, stderr=None, check=None, **kwargs):
        commands.append((list(command), input))
        return subprocess.CompletedProcess(command, 0, stdout="ok secret-token github_pat_example\n", stderr="")

    monkeypatch.setattr(preflight.subprocess, "run", fake_subprocess_run)

    executions = preflight.gh_login_from_env(tmp_path, hostname="github.com")

    assert commands == [
        (["gh", "auth", "login", "--hostname", "github.com", "--with-token"], "secret-token"),
        (["gh", "auth", "setup-git", "--hostname", "github.com"], None),
    ]
    assert "secret-token" not in json.dumps(executions)
    assert "github_pat_example" not in json.dumps(executions)
    assert executions[0]["command"] == "gh auth login --hostname <host> --with-token"


def test_main_gh_login_from_env_requires_human_approval(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = preflight.main(["--repo-root", str(tmp_path), "--profile", "github-cli", "--gh-login-from-env"])

    captured = capsys.readouterr()
    assert code == 1
    assert "--gh-login-from-env requires --human-check approved" in captured.err

    ready_auth = preflight.Check(
        id="github-cli:auth",
        label="gh auth status",
        kind="github-auth",
        required=True,
        ok=True,
        detected="authenticated",
        install_hint="ready",
    )

    def fail_login(repo_root, hostname):
        raise AssertionError("login should be skipped when gh auth status is ready")

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(preflight, "build_checks", lambda args, repo_root: [ready_auth])
        monkeypatch.setattr(preflight, "gh_login_from_env", fail_login)
        code = preflight.main(
            ["--repo-root", str(tmp_path), "--profile", "github-cli", "--gh-login-from-env", "--human-check", "approved"]
        )
    finally:
        monkeypatch.undo()

    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["status"] == "ready"
    assert output["auth_executions"][0]["command"].startswith("skipped:")


def test_localty_protocol_check_uses_msys2_python_when_available(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    bash_path = tmp_path / "usr" / "bin" / "bash.exe"
    bash_path.parent.mkdir(parents=True)
    bash_path.write_text("", encoding="utf-8")
    calls: list[tuple[list[str], dict[str, str] | None]] = []

    def fake_run(command, cwd=None, env=None):
        calls.append((list(command), env))
        return subprocess.CompletedProcess(command, 0, stdout="{\"telemetry\": 10000}\n", stderr="")

    monkeypatch.setattr(preflight, "run_command", fake_run)
    args = argparse.Namespace(profile="gui-pyqt", work_id="issue-1", support_branch="develop")

    check = preflight.localty_protocol_check(args, protocol_dir=None, bash_path=bash_path)

    assert check.ok is True
    assert "MSYS2 python" in check.detected
    assert calls[0][0][0] == str(bash_path)
    assert calls[0][1]["MSYSTEM"] == "MINGW64"


def test_localty_protocol_check_uses_fallback_repository(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    protocol_dir = tmp_path / "localty-system-protocol"
    protocol_dir.mkdir()
    (protocol_dir / "pyproject.toml").write_text("[project]\nname='localty-system-protocol'\n", encoding="utf-8")
    monkeypatch.setattr(
        preflight,
        "run_command",
        lambda command, cwd=None, env=None: subprocess.CompletedProcess(command, 1, stdout="", stderr="missing package"),
    )
    args = argparse.Namespace(profile="corrective-action-fix", work_id="issue-9", support_branch="main")

    check = preflight.localty_protocol_check(args, protocol_dir=protocol_dir, bash_path=tmp_path / "missing-bash.exe")

    assert check.ok is True
    assert "fallback source repository" in check.detected
    assert "prepare_support_repository.py" in (check.fallback_command or "")
    assert "--branch \"main\"" in (check.fallback_command or "")


def test_localty_protocol_check_reports_missing_without_work_id(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        preflight,
        "run_command",
        lambda command, cwd=None, env=None: subprocess.CompletedProcess(command, 1, stdout="missing stdout", stderr=""),
    )
    args = argparse.Namespace(profile="corrective-action-fix", work_id="", support_branch="develop")

    check = preflight.localty_protocol_check(args, protocol_dir=None, bash_path=tmp_path / "missing-bash.exe")

    assert check.ok is False
    assert check.fallback_command is None
    assert "pass --work-id" in check.install_hint
    assert check.detected == "missing stdout"


def test_localty_protocol_check_reports_missing_with_fallback_command(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        preflight,
        "run_command",
        lambda command, cwd=None, env=None: subprocess.CompletedProcess(command, 1, stdout="", stderr="missing package"),
    )
    args = argparse.Namespace(profile="corrective-action-fix", work_id="issue-9", support_branch="")

    check = preflight.localty_protocol_check(args, protocol_dir=None, bash_path=tmp_path / "missing-bash.exe")

    assert check.ok is False
    assert check.fallback_command is not None
    assert "--branch \"develop\"" in check.fallback_command
    assert "download the support repository" in check.install_hint


def test_msys2_package_check_missing_bash_and_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    missing = preflight.msys2_package_check(tmp_path / "missing-bash.exe", "mingw-pkg", required=True)
    assert missing.ok is False
    assert missing.install_command == "pacman -S --needed --noconfirm mingw-pkg"

    bash_path = tmp_path / "usr" / "bin" / "bash.exe"
    bash_path.parent.mkdir(parents=True)
    bash_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        preflight,
        "run_command",
        lambda command, cwd=None, env=None: subprocess.CompletedProcess(command, 0, stdout="mingw-pkg 1.0\n", stderr=""),
    )

    check = preflight.msys2_package_check(bash_path, "mingw-pkg", required=False)

    assert check.ok is True
    assert check.detected == "mingw-pkg 1.0"


def test_docker_compose_profile_declares_required_docker_checks(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(preflight.shutil, "which", lambda name: f"C:/tools/{name}.exe")
    monkeypatch.setattr(
        preflight,
        "run_command",
        lambda command, cwd=None, env=None: subprocess.CompletedProcess(command, 0, stdout="compose ok\n", stderr=""),
    )
    args = argparse.Namespace(
        profile="docker-compose",
        source_dir="",
        protocol_dir="",
        support_branch="develop",
        msys2_root=r"C:\msys64",
        work_id="issue-1",
    )
    terraform = tmp_path / "terraform.exe"
    terraform.write_text("", encoding="utf-8")
    (tmp_path / ".env").write_text(f"AIWF_TERRAFORM_EXE={terraform}\n", encoding="utf-8")

    checks = preflight.build_checks(args, tmp_path)

    ids = {check.id for check in checks}
    assert "exe:docker" in ids
    assert "docker-plugin:compose" in ids
    assert "env-path:AIWF_TERRAFORM_EXE" in ids
    assert next(check for check in checks if check.id == "exe:docker").required is True
    assert next(check for check in checks if check.id == "docker-plugin:compose").required is True
    assert next(check for check in checks if check.id == "env-path:AIWF_TERRAFORM_EXE").detected == str(terraform)


@pytest.mark.parametrize(
    ("profile", "expected_ids"),
    [
        ("corrective-action-fix", {"path:msys2-bash", "python-module:pytest"}),
        ("web-nextjs", {"exe:node", "exe:npm", "exe:npx", "path:target-package-json"}),
        (
            "runtime-dev",
            {
                "exe:uv",
                "exe:py",
                "path:runtime-windows-script-uv",
                "path:runtime-windows-script-aiwfctl",
                "path:runtime-windows-script-aiwf-cmd",
                "path:runtime-windows-script-aiwf-ps1",
                "runtime:pytest",
            },
        ),
        ("vscode-environment", {"exe:code", "exe:docker", "exe:go", "path:msys2-bash", "path:target-workspace"}),
    ],
)
def test_build_checks_profiles_add_expected_checks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    profile: str,
    expected_ids: set[str],
) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    windows_script_dir = tmp_path / "runtime" / "windows-script"
    windows_script_dir.mkdir(parents=True)
    (windows_script_dir / "uv.cmd").write_text("@echo off\n", encoding="utf-8")
    (windows_script_dir / "aiwfctl.cmd").write_text("@echo off\n", encoding="utf-8")
    (windows_script_dir / "aiwf.cmd").write_text("@echo off\n", encoding="utf-8")
    (windows_script_dir / "aiwf.ps1").write_text("Write-Output 'ok'\n", encoding="utf-8")
    monkeypatch.setattr(preflight.shutil, "which", lambda name: f"C:/tools/{name}.exe")
    monkeypatch.setattr(
        preflight,
        "run_command",
        lambda command, cwd=None, env=None: subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr=""),
    )
    args = argparse.Namespace(
        profile=profile,
        source_dir=str(source_dir),
        protocol_dir="",
        support_branch="develop",
        msys2_root=str(tmp_path / "msys64"),
        work_id="issue-1",
    )

    checks = preflight.build_checks(args, tmp_path)

    assert expected_ids <= {check.id for check in checks}


def test_build_checks_localty_gui_and_profiles_without_source_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(preflight.shutil, "which", lambda name: f"C:/tools/{name}.exe")
    monkeypatch.setattr(preflight, "localty_protocol_check", lambda args, protocol_dir, bash_path: preflight.Check(
        id="python-package:localty-system-protocol",
        label="localty-system-protocol package",
        kind="python-package",
        required=True,
        ok=True,
        detected="ok",
        install_hint="ok",
    ))
    monkeypatch.setattr(preflight, "msys2_package_check", lambda bash_path, package, required: preflight.Check(
        id=f"msys2-package:{package}",
        label=package,
        kind="msys2-package",
        required=required,
        ok=True,
        detected="ok",
        install_hint="ok",
    ))

    gui_args = argparse.Namespace(
        profile="gui-pyqt",
        source_dir=str(tmp_path / "gui"),
        protocol_dir="",
        support_branch="develop",
        msys2_root=str(tmp_path / "msys64"),
        work_id="issue-1",
    )
    (tmp_path / "gui").mkdir()
    gui_checks = preflight.build_checks(gui_args, tmp_path)
    gui_ids = {check.id for check in gui_checks}
    assert "path:target-pyproject" in gui_ids
    assert any(item.startswith("msys2-package:") for item in gui_ids)

    localty_args = argparse.Namespace(**{**vars(gui_args), "profile": "localty-msys2", "source_dir": ""})
    assert "path:target-pyproject" not in {check.id for check in preflight.build_checks(localty_args, tmp_path)}

    vscode_args = argparse.Namespace(**{**vars(gui_args), "profile": "vscode-environment", "source_dir": ""})
    assert "path:target-workspace" not in {check.id for check in preflight.build_checks(vscode_args, tmp_path)}

    web_args = argparse.Namespace(**{**vars(gui_args), "profile": "web-nextjs", "source_dir": ""})
    assert "path:target-package-json" not in {check.id for check in preflight.build_checks(web_args, tmp_path)}


def test_install_requires_human_approval_before_running_commands(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()

    code = preflight.main(["--repo-root", str(repo), "--install"])

    captured = capsys.readouterr()
    assert code == 1
    assert "--install requires --human-check approved" in captured.err


def test_install_missing_runs_required_commands_and_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_subprocess_run(command, text, stdout, stderr, shell, check):
        calls.append(command)
        return subprocess.CompletedProcess(command, 1 if "install primary" in command else 0, stdout="out", stderr="err")

    monkeypatch.setattr(preflight.subprocess, "run", fake_subprocess_run)
    checks = [
        preflight.Check(
            id="required",
            label="required",
            kind="executable",
            required=True,
            ok=False,
            detected="",
            install_hint="install",
            install_command="install primary",
            fallback_command="install fallback",
        ),
        preflight.Check(
            id="optional",
            label="optional",
            kind="executable",
            required=False,
            ok=False,
            detected="",
            install_hint="install optional",
            install_command="install optional",
        ),
    ]

    executed = preflight.install_missing(checks)

    assert calls == ["install primary", "install fallback"]
    assert [item["label"] for item in executed] == ["required", "required fallback"]


def test_install_missing_breaks_without_fallback_or_when_fallback_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_subprocess_run(command, text, stdout, stderr, shell, check):
        calls.append(command)
        return subprocess.CompletedProcess(command, 1, stdout="out", stderr="err")

    monkeypatch.setattr(preflight.subprocess, "run", fake_subprocess_run)
    checks = [
        preflight.Check(
            id="first",
            label="first",
            kind="executable",
            required=True,
            ok=False,
            detected="",
            install_hint="install",
            install_command="first install",
        ),
        preflight.Check(
            id="second",
            label="second",
            kind="executable",
            required=True,
            ok=False,
            detected="",
            install_hint="install",
            install_command="second install",
        ),
    ]

    executed = preflight.install_missing(checks)

    assert calls == ["first install"]
    assert len(executed) == 1

    calls.clear()
    checks[0] = preflight.Check(
        id="first",
        label="first",
        kind="executable",
        required=True,
        ok=False,
        detected="",
        install_hint="install",
        install_command="first install",
        fallback_command="fallback install",
    )
    executed = preflight.install_missing(checks)

    assert calls == ["first install", "fallback install"]
    assert len(executed) == 2


def test_install_missing_runs_msys2_package_with_bash(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command, cwd=None, env=None):
        calls.append(list(command))
        return subprocess.CompletedProcess(command, 0, stdout="installed", stderr="")

    monkeypatch.setattr(preflight, "run_command", fake_run)
    check = preflight.Check(
        id="msys",
        label="msys",
        kind="msys2-package",
        required=True,
        ok=False,
        detected="",
        install_hint="install",
        install_command="pacman -S pkg",
    )

    executed = preflight.install_missing([check])

    assert executed[0]["command"].endswith("-lc 'pacman -S pkg'")
    assert calls[0][-1] == "pacman -S pkg"


def test_markdown_report_includes_fallback_command() -> None:
    result = {
        "profile": "localty-msys2",
        "status": "install-list-required",
        "created_at": "2026-07-06T00:00:00+00:00",
        "checks": [
            preflight.Check(
                id="python-package:localty-system-protocol",
                label="localty-system-protocol package",
                kind="python-package",
                required=True,
                ok=False,
                detected="missing",
                install_hint="Install the published package first.",
                install_command="python -m pip install localty-system-protocol",
                fallback_command="python runtime/scm/prepare_support_repository.py --work-id issue-1",
            ).to_dict()
        ],
    }

    markdown = preflight.markdown_report(result)

    assert "## Missing Required" in markdown
    assert "localty-system-protocol package" in markdown
    assert "fallback:" in markdown
    assert "prepare_support_repository.py" in markdown


def test_markdown_report_includes_missing_optional_items() -> None:
    result = {
        "profile": "web-nextjs",
        "status": "ready",
        "created_at": "2026-07-06T00:00:00+00:00",
        "checks": [
            preflight.Check(
                id="exe:npx",
                label="npx",
                kind="executable",
                required=False,
                ok=False,
                detected="",
                install_hint="Install Node.js.",
                install_command=None,
            ).to_dict(),
            preflight.Check(
                id="exe:node",
                label="node",
                kind="executable",
                required=True,
                ok=True,
                detected="C:/node.exe",
                install_hint="Install Node.js.",
            ).to_dict(),
        ],
    }

    markdown = preflight.markdown_report(result)

    assert "## Missing Optional" in markdown
    assert "`npx`" in markdown
    assert "manual install required" in markdown


def test_markdown_report_iterates_multiple_required_missing_items() -> None:
    result = {
        "profile": "docker-compose",
        "status": "install-list-required",
        "created_at": "2026-07-06T00:00:00+00:00",
        "checks": [
            preflight.Check(
                id="exe:docker",
                label="docker",
                kind="executable",
                required=True,
                ok=False,
                detected="",
                install_hint="Install Docker.",
                install_command="install docker",
            ).to_dict(),
            preflight.Check(
                id="docker-plugin:compose",
                label="Docker Compose",
                kind="docker-plugin",
                required=True,
                ok=False,
                detected="",
                install_hint="Install Compose.",
                install_command="install compose",
            ).to_dict(),
        ],
    }

    markdown = preflight.markdown_report(result)

    assert "`docker`" in markdown
    assert "`Docker Compose`" in markdown


def test_markdown_report_reports_none_when_all_checks_ready() -> None:
    result = {
        "profile": "docker-compose",
        "status": "ready",
        "created_at": "2026-07-06T00:00:00+00:00",
        "checks": [
            preflight.Check(
                id="exe:git",
                label="git",
                kind="executable",
                required=True,
                ok=True,
                detected="C:/git.exe",
                install_hint="install git",
            ).to_dict()
        ],
    }

    markdown = preflight.markdown_report(result)

    assert "## Missing Required" in markdown
    assert markdown.count("- none") == 2
    assert "[OK]" in markdown


def test_write_reports_creates_json_and_markdown(tmp_path: Path) -> None:
    result = {
        "profile": "docker-compose",
        "status": "ready",
        "created_at": "2026-07-06T00:00:00+00:00",
        "checks": [],
    }

    json_path, md_path = preflight.write_reports(tmp_path, "issue-1", result)

    assert json_path.exists()
    assert md_path.exists()
    assert json.loads(json_path.read_text(encoding="utf-8-sig"))["profile"] == "docker-compose"
    assert "# Environment Preflight" in md_path.read_text(encoding="utf-8")


def test_main_writes_report_and_returns_ready(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(
        preflight,
        "build_checks",
        lambda args, repo_root: [
            preflight.Check(
                id="exe:git",
                label="git",
                kind="executable",
                required=True,
                ok=True,
                detected="C:/git.exe",
                install_hint="install git",
            )
        ],
    )

    code = preflight.main(["--repo-root", str(tmp_path), "--work-id", "issue-1"])

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert code == 0
    assert output["status"] == "ready"
    assert output["record_path"].startswith("work/issue-1/process-report/")
    assert output["gate_restart"]["gate"] == "environment-preflight-gate"
    assert output["gate_restart"]["repair_available"] is False


def test_main_returns_two_when_required_check_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(
        preflight,
        "build_checks",
        lambda args, repo_root: [
            preflight.Check(
                id="exe:uv",
                label="uv",
                kind="executable",
                required=True,
                ok=False,
                detected="",
                install_hint="install uv",
                install_command="install uv",
            )
        ],
    )

    code = preflight.main(["--repo-root", str(tmp_path)])

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert code == 2
    assert output["status"] == "install-list-required"
    assert output["gate_restart"]["restart_from"] == "environment-preflight-gate"
    assert output["gate_restart"]["repair_available"] is True
    assert "--install --human-check approved" in output["gate_restart"]["repair_command"]


def test_main_runs_install_after_human_approval_and_module_script_load(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing = preflight.Check(
        id="exe:uv",
        label="uv",
        kind="executable",
        required=True,
        ok=False,
        detected="",
        install_hint="install uv",
        install_command="install uv",
    )
    monkeypatch.setattr(preflight, "build_checks", lambda args, repo_root: [missing])
    monkeypatch.setattr(preflight, "install_missing", lambda checks: [{"id": "exe:uv", "returncode": 0}])

    code = preflight.main(["--repo-root", str(tmp_path), "--install", "--human-check", "approved"])

    output = json.loads(capsys.readouterr().out)
    assert code == 2
    assert output["install_executions"] == [{"id": "exe:uv", "returncode": 0}]
    assert output["gate_restart"]["next_on_fail"] == "stay-at-gate"

    namespace = runpy.run_path(str(Path(preflight.__file__)))
    assert namespace["build_parser"]
