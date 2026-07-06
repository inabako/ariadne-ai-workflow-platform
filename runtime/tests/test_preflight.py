from __future__ import annotations

import argparse
import json
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
    assert existing_path.to_dict()["detected"] == str(tmp_path)
    assert missing_path.to_dict()["detected"] == ""


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

    checks = preflight.build_checks(args, tmp_path)

    ids = {check.id for check in checks}
    assert "exe:docker" in ids
    assert "docker-plugin:compose" in ids
    assert next(check for check in checks if check.id == "exe:docker").required is True
    assert next(check for check in checks if check.id == "docker-plugin:compose").required is True


@pytest.mark.parametrize(
    ("profile", "expected_ids"),
    [
        ("corrective-action-fix", {"path:msys2-bash", "python-module:pytest"}),
        ("web-nextjs", {"exe:node", "exe:npm", "exe:npx", "path:target-package-json"}),
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
