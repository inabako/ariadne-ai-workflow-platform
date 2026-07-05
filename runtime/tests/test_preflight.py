from __future__ import annotations

import argparse
import subprocess
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


def test_docker_compose_check_uses_compose_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight.shutil, "which", lambda name: "C:/Program Files/Docker/docker.exe")

    def fake_run(command: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        assert command == ["docker", "compose", "version"]
        return subprocess.CompletedProcess(command, 0, stdout="Docker Compose version v2.99.0\n", stderr="")

    monkeypatch.setattr(preflight, "run_command", fake_run)

    check = preflight.docker_compose_check(required=True)

    assert check.ok is True
    assert check.detected == "Docker Compose version v2.99.0"


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


def test_install_requires_human_approval_before_running_commands(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()

    code = preflight.main(["--repo-root", str(repo), "--install"])

    captured = capsys.readouterr()
    assert code == 1
    assert "--install requires --human-check approved" in captured.err


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
