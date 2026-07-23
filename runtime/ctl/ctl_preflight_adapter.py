from __future__ import annotations

import argparse
import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from runtime.environment import preflight


def _argv(args: argparse.Namespace, repo_root: Path) -> list[str]:
    values: list[str] = ["--repo-root", str(repo_root)]
    values.extend(["--profile", args.profile])
    if getattr(args, "work_id", ""):
        values.extend(["--work-id", args.work_id])
    if getattr(args, "source_dir", ""):
        values.extend(["--source-dir", args.source_dir])
    if getattr(args, "protocol_dir", ""):
        values.extend(["--protocol-dir", args.protocol_dir])
    if getattr(args, "support_branch", ""):
        values.extend(["--support-branch", args.support_branch])
    if getattr(args, "msys2_root", ""):
        values.extend(["--msys2-root", args.msys2_root])
    if getattr(args, "preflight_repo_root", ""):
        values.extend(["--repo-root", args.preflight_repo_root])
    if getattr(args, "github_hostname", ""):
        values.extend(["--github-hostname", args.github_hostname])
    if getattr(args, "install", False):
        values.append("--install")
    if getattr(args, "gh_login_from_env", False):
        values.append("--gh-login-from-env")
    if getattr(args, "human_check", None):
        values.extend(["--human-check", args.human_check])
    return values


def run_preflight(args: argparse.Namespace, repo_root: Path) -> tuple[int, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = preflight.main(_argv(args, repo_root))
    output = stdout.getvalue()
    error = stderr.getvalue()
    if error:
        output += error
    return code, output
