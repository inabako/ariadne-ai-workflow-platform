from __future__ import annotations

from contextlib import contextmanager
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Iterator, Sequence


def run_git(
    args: Sequence[str],
    cwd: Path,
    dry_run: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = ["git", *args]
    if dry_run:
        return subprocess.CompletedProcess(command, 0, stdout="DRY-RUN: " + " ".join(command), stderr="")
    return subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        shell=False,
    )


@contextmanager
def github_token_git_env(token: str) -> Iterator[dict[str, str] | None]:
    if not token:
        yield None
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        if os.name == "nt":
            askpass = Path(temp_dir) / "git-askpass.cmd"
            askpass.write_text(
                "\r\n".join(
                    [
                        "@echo off",
                        "echo %~1 | findstr /I \"username\" >nul",
                        "if not errorlevel 1 (",
                        "  echo x-access-token",
                        ") else (",
                        "  echo %GITHUB_TOKEN%",
                        ")",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
        else:
            askpass = Path(temp_dir) / "git-askpass.sh"
            askpass.write_text(
                "\n".join(
                    [
                        "#!/bin/sh",
                        "case \"$1\" in",
                        "  *sername*) printf '%s\\n' 'x-access-token' ;;",
                        "  *) printf '%s\\n' \"$GITHUB_TOKEN\" ;;",
                        "esac",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            askpass.chmod(0o700)

        process_env = os.environ.copy()
        process_env["GITHUB_TOKEN"] = token
        process_env["GIT_ASKPASS"] = str(askpass)
        process_env["GIT_TERMINAL_PROMPT"] = "0"
        process_env["GCM_INTERACTIVE"] = "Never"
        yield process_env


def require_success(result: subprocess.CompletedProcess[str], action: str) -> None:
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{action} failed: {detail}")


def git_output(args: Sequence[str], cwd: Path) -> str:
    result = run_git(args, cwd)
    require_success(result, "git " + " ".join(args))
    return result.stdout.strip()


def is_git_repository(path: Path) -> bool:
    return (path / ".git").exists()


def current_branch(path: Path) -> str:
    return git_output(["rev-parse", "--abbrev-ref", "HEAD"], path)


def current_commit(path: Path) -> str:
    return git_output(["rev-parse", "HEAD"], path)


def local_branch_exists(path: Path, branch: str) -> bool:
    result = run_git(["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], path)
    return result.returncode == 0
