from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import env_value, find_repo_root, load_env, local_timestamp, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.paths import (  # noqa: E402
    WINDOWS_DART_EXECUTABLES,
    WINDOWS_DEFAULT_MSYS2_ROOT,
    WINDOWS_FLUTTER_EXECUTABLES,
    WINDOWS_MSYS2_BASH,
)
from runtime.constants.workspace import process_report_dir_for_work_dir, work_dir_for_id  # noqa: E402


GITHUB_TOKEN_KEYS = ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_API_TOKEN", "GITHUB_API_KEY")
TOKEN_REDACTION_PATTERNS = (
    re.compile(r"github_pat_[A-Za-z0-9_*-]+"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_*-]+"),
)


@dataclass(frozen=True)
class Check:
    id: str
    label: str
    kind: str
    required: bool
    ok: bool
    detected: str
    install_hint: str
    install_command: str | None = None
    fallback_command: str | None = None
    action_command: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "kind": self.kind,
            "required": self.required,
            "ok": self.ok,
            "detected": self.detected,
            "install_hint": self.install_hint,
            "install_command": self.install_command,
            "fallback_command": self.fallback_command,
            "action_command": self.action_command,
        }


def run_command(command: Sequence[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def configure_utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def redact_github_secrets(text: str | None, repo_root: Path | None = None) -> str:
    safe = text or ""
    for pattern in TOKEN_REDACTION_PATTERNS:
        safe = pattern.sub("[REDACTED]", safe)
    if repo_root:
        settings = load_env(repo_root)
        for key in GITHUB_TOKEN_KEYS:
            value = settings.get(key, "").strip()
            if value:
                safe = safe.replace(value, "[REDACTED]")
    return safe


def which_check(
    executable: str,
    *,
    required: bool,
    install_hint: str,
    install_command: str | None = None,
    fallback_paths: Sequence[Path] | None = None,
) -> Check:
    path = shutil.which(executable)
    if path is None and fallback_paths:
        path = next((str(candidate) for candidate in fallback_paths if candidate.exists()), None)
    return Check(
        id=f"exe:{executable}",
        label=executable,
        kind="executable",
        required=required,
        ok=path is not None,
        detected=path or "",
        install_hint=install_hint,
        install_command=install_command,
    )


def path_check(path: Path, *, check_id: str, label: str, required: bool, install_hint: str, install_command: str | None = None) -> Check:
    return Check(
        id=check_id,
        label=label,
        kind="path",
        required=required,
        ok=path.exists(),
        detected=str(path) if path.exists() else "",
        install_hint=install_hint,
        install_command=install_command,
    )


def env_path_check(repo_root: Path, key: str, *, label: str, required: bool, install_hint: str) -> Check:
    settings = load_env(repo_root)
    value = settings.get(key, "").strip()
    path = Path(value) if value else None
    ok = bool(path and path.is_file())
    return Check(
        id=f"env-path:{key}",
        label=label,
        kind="env-path",
        required=required,
        ok=ok,
        detected=str(path) if ok and path else "",
        install_hint=install_hint,
    )


def python_module_check(module: str, *, required: bool, install_hint: str, install_command: str | None = None) -> Check:
    completed = run_command([sys.executable, "-c", f"import {module}"])
    return Check(
        id=f"python-module:{module}",
        label=module,
        kind="python-module",
        required=required,
        ok=completed.returncode == 0,
        detected=sys.executable if completed.returncode == 0 else "",
        install_hint=install_hint,
        install_command=install_command or f"{sys.executable} -m pip install {module}",
    )


def docker_compose_check(*, required: bool) -> Check:
    if shutil.which("docker") is None:
        return Check(
            id="docker-plugin:compose",
            label="Docker Compose",
            kind="docker-plugin",
            required=required,
            ok=False,
            detected="",
            install_hint="Install Docker Desktop with Compose support, then verify: docker compose version.",
            install_command="winget install --id Docker.DockerDesktop -e",
        )
    completed = run_command(["docker", "compose", "version"])
    return Check(
        id="docker-plugin:compose",
        label="Docker Compose",
        kind="docker-plugin",
        required=required,
        ok=completed.returncode == 0,
        detected=completed.stdout.strip() if completed.returncode == 0 else completed.stderr.strip(),
        install_hint="Install Docker Desktop with Compose support, then verify: docker compose version.",
        install_command="winget install --id Docker.DockerDesktop -e",
    )


def github_cli_version_check(*, required: bool) -> Check:
    if shutil.which("gh") is None:
        return Check(
            id="github-cli:version",
            label="gh --version",
            kind="github-cli",
            required=required,
            ok=False,
            detected="",
            install_hint="Install GitHub CLI, then verify with gh --version.",
            install_command="winget install --id GitHub.cli",
        )
    completed = run_command(["gh", "--version"])
    return Check(
        id="github-cli:version",
        label="gh --version",
        kind="github-cli",
        required=required,
        ok=completed.returncode == 0,
        detected=redact_github_secrets(
            completed.stdout.splitlines()[0].strip() if completed.returncode == 0 and completed.stdout else (completed.stderr or "").strip()
        ),
        install_hint="GitHub CLI must be callable as gh --version before GitHub metadata collection.",
        install_command="winget install --id GitHub.cli",
    )


def github_env_token_check(repo_root: Path, *, required: bool = False) -> Check:
    settings = load_env(repo_root)
    token = env_value(settings, *GITHUB_TOKEN_KEYS)
    detected = "configured (masked)" if token.strip() else ""
    return Check(
        id="env:github-token",
        label="GitHub token ENV",
        kind="secret-env",
        required=required,
        ok=bool(token.strip()),
        detected=detected,
        install_hint="Set GITHUB_TOKEN or GH_TOKEN in process ENV or repository .env. Do not store passwords.",
    )


def github_cli_auth_check(repo_root: Path, *, required: bool, hostname: str = "github.com") -> Check:
    action_command = (
        "uv run --project runtime python runtime/environment/preflight.py "
        "--profile github-cli --gh-login-from-env --human-check approved"
    )
    if hostname != "github.com":
        action_command += f" --github-hostname {hostname}"
    if shutil.which("gh") is None:
        return Check(
            id="github-cli:auth",
            label="gh auth status",
            kind="github-auth",
            required=required,
            ok=False,
            detected="gh is not installed",
            install_hint="Install GitHub CLI before checking GitHub authentication.",
            action_command=action_command,
        )
    completed = run_command(["gh", "auth", "status", "--hostname", hostname])
    if completed.returncode == 0:
        detected = redact_github_secrets(
            (completed.stdout or "").strip() or (completed.stderr or "").strip() or f"authenticated for {hostname}",
            repo_root,
        )
        return Check(
            id="github-cli:auth",
            label="gh auth status",
            kind="github-auth",
            required=required,
            ok=True,
            detected=detected,
            install_hint="GitHub CLI authentication is ready.",
            action_command=action_command,
        )
    token_check = github_env_token_check(repo_root)
    hint = (
        "GitHub CLI is installed but not authenticated. "
        "Set GITHUB_TOKEN or GH_TOKEN in process ENV or repository .env, then run the action command."
    )
    if not token_check.ok:
        hint += " Token ENV is not currently detected."
    return Check(
        id="github-cli:auth",
        label="gh auth status",
        kind="github-auth",
        required=required,
        ok=False,
        detected=redact_github_secrets(
            (completed.stderr or "").strip() or (completed.stdout or "").strip() or f"not authenticated for {hostname}",
            repo_root,
        ),
        install_hint=hint,
        action_command=action_command,
    )


def github_auth_status(checks: Sequence[Check]) -> str:
    missing_required = [check for check in checks if check.required and not check.ok]
    if not missing_required:
        return "ready"
    if all(check.kind == "github-auth" for check in missing_required):
        return "auth-required"
    return "install-list-required"


def gh_login_from_env(repo_root: Path, *, hostname: str) -> list[dict[str, Any]]:
    settings = load_env(repo_root)
    token = env_value(settings, *GITHUB_TOKEN_KEYS).strip()
    if not token:
        raise ValueError("GitHub token ENV is required. Set GITHUB_TOKEN or GH_TOKEN in process ENV or repository .env.")
    version = github_cli_version_check(required=True)
    if not version.ok:
        raise RuntimeError("GitHub CLI is required before gh auth login can run.")

    login_command = ["gh", "auth", "login", "--hostname", hostname, "--with-token"]
    setup_command = ["gh", "auth", "setup-git", "--hostname", hostname]
    login_completed = subprocess.run(
        login_command,
        input=token,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    executions = [
        {
            "id": "github-cli:auth-login",
            "label": "gh auth login --with-token",
            "command": "gh auth login --hostname <host> --with-token",
            "returncode": login_completed.returncode,
            "stdout": redact_github_secrets(login_completed.stdout, repo_root),
            "stderr": redact_github_secrets(login_completed.stderr, repo_root),
        }
    ]
    if login_completed.returncode != 0:
        return executions

    setup_completed = subprocess.run(
        setup_command,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    executions.append(
        {
            "id": "github-cli:auth-setup-git",
            "label": "gh auth setup-git",
            "command": "gh auth setup-git --hostname <host>",
            "returncode": setup_completed.returncode,
            "stdout": redact_github_secrets(setup_completed.stdout, repo_root),
            "stderr": redact_github_secrets(setup_completed.stderr, repo_root),
        }
    )
    return executions


def localty_protocol_check(args: argparse.Namespace, protocol_dir: Path | None, bash_path: Path) -> Check:
    verify_code = "from localty_protocol.telemetry import UDP_PORTS; print(UDP_PORTS)"
    use_msys2_python = args.profile in {"localty-msys2", "gui-pyqt"} and bash_path.exists()
    if use_msys2_python:
        env = {**os.environ, "MSYSTEM": "MINGW64", "CHERE_INVOKING": "1"}
        completed = run_command([str(bash_path), "-lc", f"python -c '{verify_code}'"], env=env)
        install_command = f"\"{bash_path}\" -lc \"python -m pip install 'localty-system-protocol>=0.1.0'\""
        detected_runtime = f"MSYS2 python via {bash_path}"
    else:
        completed = run_command([sys.executable, "-c", verify_code])
        install_command = f"{sys.executable} -m pip install \"localty-system-protocol>=0.1.0\""
        detected_runtime = sys.executable
    if completed.returncode == 0:
        return Check(
            id="python-package:localty-system-protocol",
            label="localty-system-protocol package",
            kind="python-package",
            required=True,
            ok=True,
            detected=f"{detected_runtime}: {completed.stdout.strip()}",
            install_hint="Published package is installed and localty_protocol.telemetry.UDP_PORTS is importable.",
            install_command=install_command,
        )

    fallback_ok = bool(protocol_dir and (protocol_dir / "pyproject.toml").exists())
    fallback_command = None
    if args.work_id:
        branch = args.support_branch or "develop"
        fallback_command = (
            f"{sys.executable} runtime/scm/prepare_support_repository.py "
            f"--work-id \"{args.work_id}\" "
            "--name \"localty-system-protocol\" "
            "--repository \"inabako/localty-system-protocol\" "
            f"--branch \"{branch}\""
        )

    if fallback_ok:
        return Check(
            id="python-package:localty-system-protocol",
            label="localty-system-protocol package",
            kind="python-package",
            required=True,
            ok=True,
            detected=f"fallback source repository: {protocol_dir}",
            install_hint=(
                "Published package import failed, but a local fallback source repository exists. "
                "Prefer pip install localty-system-protocol>=0.1.0 when available."
            ),
            install_command=install_command,
            fallback_command=fallback_command,
        )

    fallback_hint = " If pip cannot fetch the package, download the support repository with the fallback command."
    if not fallback_command:
        fallback_hint = " If pip cannot fetch the package, pass --work-id so the report can include the support repository fallback command."
    return Check(
        id="python-package:localty-system-protocol",
        label="localty-system-protocol package",
        kind="python-package",
        required=True,
        ok=False,
        detected=completed.stderr.strip() or completed.stdout.strip(),
        install_hint=(
            "Install the published protocol package first, then verify: "
            "python -c \"from localty_protocol.telemetry import UDP_PORTS; print(UDP_PORTS)\"."
            f"{fallback_hint}"
        ),
        install_command=install_command,
        fallback_command=fallback_command,
    )


def msys2_package_check(bash_path: Path, package: str, *, required: bool) -> Check:
    if not bash_path.exists():
        return Check(
            id=f"msys2-package:{package}",
            label=package,
            kind="msys2-package",
            required=required,
            ok=False,
            detected="",
            install_hint="Install MSYS2 first, then install required pacman packages.",
            install_command=f"pacman -S --needed --noconfirm {package}",
        )
    env = {**os.environ, "MSYSTEM": "MINGW64", "CHERE_INVOKING": "1"}
    completed = run_command([str(bash_path), "-lc", f"pacman -Q {package}"], env=env)
    return Check(
        id=f"msys2-package:{package}",
        label=package,
        kind="msys2-package",
        required=required,
        ok=completed.returncode == 0,
        detected=completed.stdout.strip(),
        install_hint=f"Install with MSYS2 pacman: pacman -S --needed --noconfirm {package}",
        install_command=f"pacman -S --needed --noconfirm {package}",
    )


def build_checks(args: argparse.Namespace, repo_root: Path) -> list[Check]:
    source_dir = Path(args.source_dir).resolve() if args.source_dir else None
    protocol_dir = Path(args.protocol_dir).resolve() if args.protocol_dir else (source_dir.parent / "localty-system-protocol" if source_dir else None)
    msys2_root = Path(args.msys2_root)
    bash_path = msys2_root / "usr" / "bin" / "bash.exe"

    checks: list[Check] = [
        which_check(
            "git",
            required=True,
            install_hint="Install Git for Windows and ensure git is on PATH.",
            install_command="winget install --id Git.Git -e",
        ),
        which_check(
            "uv",
            required=True,
            install_hint="Install uv with an approved installer or package manager and ensure uv is on PATH.",
        ),
        which_check("python", required=False, install_hint="Optional when uv provides Python. Install Python or use uv run --project runtime python."),
    ]

    if args.profile in {"corrective-action-fix", "localty-msys2", "gui-pyqt"}:
        checks.append(path_check(
            bash_path,
            check_id="path:msys2-bash",
            label="MSYS2 bash.exe",
            required=args.profile in {"localty-msys2", "gui-pyqt"},
            install_hint=f"Install MSYS2 to {WINDOWS_DEFAULT_MSYS2_ROOT} or pass --msys2-root.",
        ))

    if args.profile in {"localty-msys2", "gui-pyqt"}:
        if source_dir:
            checks.append(path_check(
                source_dir / "pyproject.toml",
                check_id="path:target-pyproject",
                label="target pyproject.toml",
                required=True,
                install_hint="Run preflight with --source-dir pointing at the GUI repository root.",
            ))
        checks.append(localty_protocol_check(args, protocol_dir, bash_path))
        for package in [
            "mingw-w64-x86_64-python",
            "mingw-w64-x86_64-python-pip",
            "mingw-w64-x86_64-python-gobject",
            "mingw-w64-x86_64-gstreamer",
            "mingw-w64-x86_64-gst-plugins-base",
            "mingw-w64-x86_64-gst-plugins-good",
            "mingw-w64-x86_64-gst-plugins-bad",
            "mingw-w64-x86_64-gst-plugins-ugly",
            "mingw-w64-x86_64-qt6-base",
            "mingw-w64-x86_64-python-pyqt6",
        ]:
            checks.append(msys2_package_check(bash_path, package, required=True))

    if args.profile == "corrective-action-fix":
        checks.append(python_module_check(
            "pytest",
            required=False,
            install_hint="Needed for local pytest execution. Prefer the runtime pyproject dev dependency group instead of global install.",
            install_command="uv run --project runtime --group dev pytest --version",
        ))

    if args.profile in {"github-cli", "github-knowledge-maintenance"}:
        hostname = getattr(args, "github_hostname", "github.com") or "github.com"
        checks.append(github_cli_version_check(required=True))
        checks.append(github_env_token_check(repo_root, required=False))
        checks.append(github_cli_auth_check(repo_root, required=True, hostname=hostname))

    if args.profile == "vscode-environment":
        checks.append(which_check(
            "code",
            required=True,
            install_hint="Install Visual Studio Code and ensure the code command is on PATH.",
            install_command="winget install --id Microsoft.VisualStudioCode -e",
        ))
        checks.append(which_check(
            "docker",
            required=True,
            install_hint="Required for local gateway and IaC validation tasks.",
            install_command="winget install --id Docker.DockerDesktop -e",
        ))
        checks.append(which_check(
            "go",
            required=True,
            install_hint="Required for future realtime gateway development.",
            install_command="winget install --id GoLang.Go -e",
        ))
        checks.append(which_check(
            "kubectl",
            required=False,
            install_hint="Recommended for future k3s migration checks.",
            install_command="winget install --id Kubernetes.kubectl -e",
        ))
        checks.append(which_check(
            "node",
            required=False,
            install_hint="Required only when the workspace uses Node.js tasks.",
            install_command="winget install --id OpenJS.NodeJS.LTS -e",
        ))
        checks.append(which_check(
            "java",
            required=False,
            install_hint="Required only when the workspace uses Java tasks.",
            install_command="winget install --id EclipseAdoptium.Temurin.21.JDK -e",
        ))
        checks.append(path_check(
            bash_path,
            check_id="path:msys2-bash",
            label="MSYS2 bash.exe",
            required=True,
            install_hint=f"Install MSYS2 to {WINDOWS_DEFAULT_MSYS2_ROOT} or pass --msys2-root.",
        ))
        checks.append(msys2_package_check(bash_path, "mingw-w64-x86_64-python", required=True))
        checks.append(msys2_package_check(bash_path, "mingw-w64-x86_64-gstreamer", required=True))
        checks.append(msys2_package_check(bash_path, "mingw-w64-x86_64-gst-plugins-base", required=True))
        if source_dir:
            checks.append(path_check(
                source_dir,
                check_id="path:target-workspace",
                label="target workspace directory",
                required=True,
                install_hint="Pass --source-dir pointing at the target workspace root.",
            ))

    if args.profile == "web-nextjs":
        checks.append(which_check(
            "node",
            required=True,
            install_hint="Install Node.js LTS. Prefer the target repository's documented version policy when available.",
            install_command="winget install --id OpenJS.NodeJS.LTS -e",
        ))
        checks.append(which_check(
            "npm",
            required=True,
            install_hint="Install npm with Node.js, then verify npm --version.",
            install_command="winget install --id OpenJS.NodeJS.LTS -e",
        ))
        checks.append(which_check(
            "npx",
            required=False,
            install_hint="Required when running Playwright through npx.",
            install_command="winget install --id OpenJS.NodeJS.LTS -e",
        ))
        if source_dir:
            checks.append(path_check(
                source_dir / "package.json",
                check_id="path:target-package-json",
                label="target package.json",
                required=False,
                install_hint="Pass --source-dir pointing at the Next.js / web app root when validating an existing app.",
            ))

    if args.profile == "docker-compose":
        checks.append(which_check(
            "docker",
            required=True,
            install_hint="Install Docker Desktop and ensure docker is on PATH.",
            install_command="winget install --id Docker.DockerDesktop -e",
        ))
        checks.append(docker_compose_check(required=True))
        checks.append(env_path_check(
            repo_root,
            "AIWF_TERRAFORM_EXE",
            label="AIWF_TERRAFORM_EXE",
            required=True,
            install_hint="Set AIWF_TERRAFORM_EXE in repo .env or process ENV to the full terraform.exe path.",
        ))

    if args.profile == "flutter":
        checks.append(which_check(
            "flutter",
            required=True,
            install_hint="Install Flutter SDK and add the Flutter SDK bin directory to PATH.",
            install_command="manual install required: https://docs.flutter.dev/get-started/install",
            fallback_paths=list(WINDOWS_FLUTTER_EXECUTABLES),
        ))
        checks.append(which_check(
            "dart",
            required=False,
            install_hint="Dart is normally bundled with Flutter. Verify Flutter SDK PATH when dart is missing.",
            install_command="manual install required: https://docs.flutter.dev/get-started/install",
            fallback_paths=list(WINDOWS_DART_EXECUTABLES),
        ))
        checks.append(which_check(
            "java",
            required=False,
            install_hint="Required for Android build toolchains when Android target is selected.",
            install_command="winget install --id EclipseAdoptium.Temurin.21.JDK -e",
        ))
        checks.append(which_check(
            "adb",
            required=False,
            install_hint="Required for Android emulator/device checks when Android target is selected.",
            install_command="Install Android Studio / Android SDK platform-tools.",
        ))
        checks.append(which_check(
            "chromedriver",
            required=False,
            install_hint="Required when running Flutter Web integration tests through flutter drive -d chrome.",
            install_command="Install ChromeDriver matching the installed Chrome version and ensure chromedriver is on PATH.",
        ))
        if source_dir:
            checks.append(path_check(
                source_dir / "pubspec.yaml",
                check_id="path:flutter-pubspec",
                label="target pubspec.yaml",
                required=False,
                install_hint="Pass --source-dir pointing at the Flutter application root when validating an existing app.",
            ))

    return checks


def markdown_report(result: dict[str, Any]) -> str:
    missing_required = [item for item in result["checks"] if item["required"] and not item["ok"]]
    missing_optional = [item for item in result["checks"] if not item["required"] and not item["ok"]]
    lines = [
        "# Environment Preflight",
        "",
        f"- profile: `{result['profile']}`",
        f"- status: `{result['status']}`",
        f"- created_at: `{result['created_at']}`",
        "",
        "## Missing Required",
        "",
    ]
    if missing_required:
        for item in missing_required:
            lines.extend([
                f"- `{item['label']}`",
                f"  - hint: {item['install_hint']}",
                f"  - command: `{item['install_command'] or 'manual install required'}`",
            ])
            if item.get("action_command"):
                lines.append(f"  - action: `{item['action_command']}`")
            if item.get("fallback_command"):
                lines.append(f"  - fallback: `{item['fallback_command']}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Missing Optional", ""])
    if missing_optional:
        for item in missing_optional:
            lines.extend([
                f"- `{item['label']}`",
                f"  - hint: {item['install_hint']}",
                f"  - command: `{item['install_command'] or 'manual install required'}`",
            ])
            if item.get("action_command"):
                lines.append(f"  - action: `{item['action_command']}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Checks", ""])
    for item in result["checks"]:
        mark = "OK" if item["ok"] else "MISSING"
        required = "required" if item["required"] else "optional"
        lines.append(f"- [{mark}] `{item['label']}` ({required})")
    return "\n".join(lines) + "\n"


def write_reports(repo_root: Path, work_id: str, result: dict[str, Any]) -> tuple[Path, Path]:
    process_dir = process_report_dir_for_work_dir(work_dir_for_id(repo_root, work_id))
    stamp = local_timestamp()
    json_path = process_dir / f"environment-preflight-{stamp}.json"
    md_path = process_dir / f"environment-preflight-{stamp}.md"
    write_json(json_path, result)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown_report(result), encoding="utf-8")
    return json_path, md_path


def install_missing(checks: list[Check]) -> list[dict[str, Any]]:
    executed: list[dict[str, Any]] = []
    for check in checks:
        if check.ok or not check.required or not check.install_command:
            continue
        if check.kind == "msys2-package":
            bash_path = WINDOWS_MSYS2_BASH
            env = {**os.environ, "MSYSTEM": "MINGW64", "CHERE_INVOKING": "1"}
            command_display = f"{bash_path} -lc {check.install_command!r}"
            completed = run_command([str(bash_path), "-lc", check.install_command], env=env)
        else:
            command_display = check.install_command
            completed = subprocess.run(check.install_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False)
        executed.append({
            "id": check.id,
            "label": check.label,
            "command": command_display,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        })
        if completed.returncode != 0:
            if check.fallback_command:
                fallback_completed = subprocess.run(check.fallback_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False)
                executed.append({
                    "id": check.id,
                    "label": f"{check.label} fallback",
                    "command": check.fallback_command,
                    "returncode": fallback_completed.returncode,
                    "stdout": fallback_completed.stdout,
                    "stderr": fallback_completed.stderr,
                })
                if fallback_completed.returncode == 0:
                    continue
            break
    return executed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check workflow environment dependencies and produce an install plan.")
    parser.add_argument(
        "--profile",
        choices=[
            "corrective-action-fix",
            "localty-msys2",
            "gui-pyqt",
            "web-nextjs",
            "docker-compose",
            "vscode-environment",
            "flutter",
            "github-cli",
            "github-knowledge-maintenance",
        ],
        default="corrective-action-fix",
    )
    parser.add_argument("--work-id", default="")
    parser.add_argument("--source-dir", default="")
    parser.add_argument("--protocol-dir", default="")
    parser.add_argument("--support-branch", default="develop")
    parser.add_argument("--msys2-root", default=str(WINDOWS_DEFAULT_MSYS2_ROOT))
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--gh-login-from-env", action="store_true")
    parser.add_argument("--github-hostname", default="github.com")
    parser.add_argument("--human-check", choices=["approved"], default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    configure_utf8_stdout()
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    checks = build_checks(args, repo_root)
    missing_required = [check for check in checks if check.required and not check.ok]
    install_executions: list[dict[str, Any]] = []
    auth_executions: list[dict[str, Any]] = []
    if args.install:
        if args.human_check != "approved":
            print("ERROR: --install requires --human-check approved", file=sys.stderr)
            return 1
        install_executions = install_missing(checks)
    if args.gh_login_from_env:
        if args.human_check != "approved":
            print("ERROR: --gh-login-from-env requires --human-check approved", file=sys.stderr)
            return 1
        auth_check = next((check for check in checks if check.id == "github-cli:auth"), None)
        if auth_check and auth_check.ok:
            auth_executions = [
                {
                    "id": "github-cli:auth-login",
                    "label": "gh auth login --with-token",
                    "command": "skipped: gh auth status already authenticated",
                    "returncode": 0,
                    "stdout": "",
                    "stderr": "",
                }
            ]
        else:
            try:
                auth_executions = gh_login_from_env(repo_root, hostname=args.github_hostname)
            except (RuntimeError, ValueError) as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 1
            checks = build_checks(args, repo_root)
            missing_required = [check for check in checks if check.required and not check.ok]

    status = github_auth_status(checks)
    result = {
        "schema_version": "1.0",
        "artifact_type": "environment-preflight",
        "profile": args.profile,
        "created_at": utc_now_iso(),
        "status": status,
        "next_flow_allowed": not missing_required,
        "checks": [check.to_dict() for check in checks],
        "install_executions": install_executions,
        "auth_executions": auth_executions,
    }
    output: dict[str, Any] = dict(result)
    if args.work_id:
        json_path, md_path = write_reports(repo_root, args.work_id, result)
        output["record_path"] = relative_to_repo(repo_root, json_path)
        output["markdown_path"] = relative_to_repo(repo_root, md_path)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if not missing_required else 2


if __name__ == "__main__":
    raise SystemExit(main())
