from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence


def run_git(args: Sequence[str], cwd: Path, dry_run: bool = False) -> subprocess.CompletedProcess[str]:
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
        shell=False,
    )


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

