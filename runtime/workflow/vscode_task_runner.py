from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def windows_registry_paths() -> list[str]:
    if os.name != "nt":
        return []
    try:
        import winreg
    except ImportError:  # pragma: no cover
        return []

    locations = [
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        (winreg.HKEY_CURRENT_USER, "Environment"),
    ]
    values: list[str] = []
    for hive, subkey in locations:
        try:
            with winreg.OpenKey(hive, subkey) as key:
                value, _ = winreg.QueryValueEx(key, "Path")
        except OSError:
            continue
        if value:
            values.append(os.path.expandvars(value))
    return values


def refreshed_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    path_parts = [part for value in windows_registry_paths() for part in value.split(os.pathsep) if part]
    path_parts.extend(part for part in env.get("PATH", "").split(os.pathsep) if part)
    if path_parts:
        env["PATH"] = os.pathsep.join(path_parts)
    if extra:
        env.update(extra)
    return env


def command_display(command: Sequence[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline([str(item) for item in command])
    import shlex

    return shlex.join(str(item) for item in command)


def run_process(command: Sequence[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> int:
    effective_cwd = cwd or repo_root()
    print(f"> {command_display(command)}", flush=True)
    completed = subprocess.run(
        [str(item) for item in command],
        cwd=str(effective_cwd),
        env=env,
        check=False,
    )
    return completed.returncode


def find_executable(name: str, env: dict[str, str], fallbacks: Sequence[Path] = ()) -> str | None:
    path = shutil.which(name, path=env.get("PATH"))
    if path:
        return path
    for fallback in fallbacks:
        if fallback.exists():
            return str(fallback)
    return None


def run_skill_info(args: argparse.Namespace) -> int:
    print(f"Codex Skill: {args.command_name}")
    print(f"Skill file: {args.skill}")
    return 0


def run_open_questions(args: argparse.Namespace) -> int:
    return run_process([
        sys.executable,
        "runtime/workflow/vscode_environment.py",
        "open-questions",
        "--work-id",
        args.work_id,
    ])


def run_preflight(args: argparse.Namespace) -> int:
    return run_process(
        [
            sys.executable,
            "runtime/environment/preflight.py",
            "--profile",
            "vscode-environment",
            "--work-id",
            args.work_id,
            "--source-dir",
            args.source_dir,
        ],
        env=refreshed_env(),
    )


def run_helper_help(_: argparse.Namespace) -> int:
    return run_process([sys.executable, "runtime/workflow/vscode_environment.py", "--help"])


def run_msys2_localty_smoke(_: argparse.Namespace) -> int:
    bash_path = Path(r"C:\msys64\usr\bin\bash.exe")
    if not bash_path.exists():
        print(f"ERROR: MSYS2 bash was not found: {bash_path}", file=sys.stderr)
        return 1
    return run_process(
        [str(bash_path), "-lc", "python --version; gst-launch-1.0 --version"],
        env=refreshed_env({"MSYSTEM": "MINGW64", "CHERE_INVOKING": "1"}),
    )


def run_docker_version(_: argparse.Namespace) -> int:
    env = refreshed_env()
    docker = find_executable("docker", env)
    if not docker:
        print("ERROR: docker executable was not found on PATH.", file=sys.stderr)
        return 1
    return run_process([docker, "version"], env=env)


def run_go_version(_: argparse.Namespace) -> int:
    env = refreshed_env()
    go = find_executable("go", env, [Path(r"C:\Program Files\Go\bin\go.exe")])
    if not go:
        print("ERROR: go executable was not found. Restart VSCode or install Go.", file=sys.stderr)
        return 1
    return run_process([go, "version"], env=env)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run VSCode task commands without inline PowerShell.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    skill_info = subparsers.add_parser("skill-info", help="Print a Codex workflow command and skill path.")
    skill_info.add_argument("--command", dest="command_name", required=True)
    skill_info.add_argument("--skill", required=True)
    skill_info.set_defaults(func=run_skill_info)

    open_questions = subparsers.add_parser("open-questions", help="Create VSCode environment open questions.")
    open_questions.add_argument("--work-id", default="vscode-environment")
    open_questions.set_defaults(func=run_open_questions)

    preflight = subparsers.add_parser("preflight", help="Run VSCode environment preflight.")
    preflight.add_argument("--work-id", default="vscode-environment")
    preflight.add_argument("--source-dir", required=True)
    preflight.set_defaults(func=run_preflight)

    helper_help = subparsers.add_parser("helper-help", help="Show vscode_environment.py help.")
    helper_help.set_defaults(func=run_helper_help)

    msys2 = subparsers.add_parser("msys2-localty-smoke", help="Run MSYS2 Python and GStreamer smoke checks.")
    msys2.set_defaults(func=run_msys2_localty_smoke)

    docker = subparsers.add_parser("docker-version", help="Run docker version.")
    docker.set_defaults(func=run_docker_version)

    go = subparsers.add_parser("go-version", help="Run go version with refreshed Windows PATH.")
    go.set_defaults(func=run_go_version)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
