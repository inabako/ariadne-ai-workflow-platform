from __future__ import annotations

import argparse
import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Callable

from runtime.tools import coverage_audit
from runtime.tools import pytest_ut_spec_sync
from runtime.tools import text_encoding_convert
from runtime.tools import text_encoding_guard
from runtime.tools import utf8_bom


ToolMain = Callable[[list[str] | None], int]


def _capture(main: ToolMain, argv: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(argv)
    output = stdout.getvalue()
    error = stderr.getvalue()
    if error:
        output += error
    return code, output


def _path_args(args: argparse.Namespace) -> list[str]:
    values: list[str] = []
    if getattr(args, "paths", None):
        values.append("--paths")
        values.extend(args.paths)
    if getattr(args, "extensions", None):
        values.append("--extensions")
        values.extend(args.extensions)
    return values


def _spec_args(args: argparse.Namespace, repo_root: Path, command: str) -> list[str]:
    spec = getattr(args, "spec", "") or str(repo_root / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md")
    runtime_root = getattr(args, "runtime_root", "") or str(repo_root / "runtime")
    values = ["--spec", spec, "--runtime-root", runtime_root, command]
    if command == "check":
        values.extend(["--repo-root", str(repo_root)])
        if getattr(args, "report", ""):
            values.extend(["--report", args.report])
        if getattr(args, "markdown", ""):
            values.extend(["--markdown", args.markdown])
        if getattr(args, "work_dir", ""):
            values.extend(["--work-dir", args.work_dir])
        if getattr(args, "register_context", False):
            values.append("--register-context")
        if getattr(args, "required_context", False):
            values.append("--required-context")
    return values


def run_tools(args: argparse.Namespace, repo_root: Path, command: str) -> tuple[int, str]:
    if command == "coverage-audit":
        audit = coverage_audit.run(
            argparse.Namespace(
                repo_root=str(repo_root),
                output_dir=args.output_dir,
                skip_run=args.skip_run,
                pytest_args=args.pytest_args,
            )
        )
        status = audit["coverage"].get("measurement_status")
        code = 0 if status in {"measured", "skipped"} else 1
        return code, json.dumps(audit, ensure_ascii=False, indent=2) + "\n"
    if command == "spec-check":
        return _capture(pytest_ut_spec_sync.main, _spec_args(args, repo_root, "check"))
    if command == "spec-fix-inputs":
        return _capture(pytest_ut_spec_sync.main, _spec_args(args, repo_root, "fix-inputs"))
    if command == "bom-scan":
        values = ["--repo-root", str(repo_root), "scan", *_path_args(args)]
        if getattr(args, "fail_on_finding", False):
            values.append("--fail-on-finding")
        return _capture(utf8_bom.main, values)
    if command == "bom-strip":
        values = ["--repo-root", str(repo_root), "strip", *_path_args(args)]
        if getattr(args, "write", False):
            values.append("--write")
        if getattr(args, "backup_suffix", None) is not None:
            values.extend(["--backup-suffix", args.backup_suffix])
        if getattr(args, "fail_on_finding", False):
            values.append("--fail-on-finding")
        return _capture(utf8_bom.main, values)
    if command == "encoding-guard":
        values = ["--repo-root", str(repo_root), "scan", *_path_args(args)]
        if getattr(args, "fail_on_finding", False):
            values.append("--fail-on-finding")
        return _capture(text_encoding_guard.main, values)
    if command in {"encoding-inspect", "encoding-preview", "encoding-convert"}:
        tool_command = command.removeprefix("encoding-")
        values = ["--repo-root", str(repo_root), tool_command, *_path_args(args)]
        if getattr(args, "encodings", None):
            values.append("--encodings")
            values.extend(args.encodings)
        if command == "encoding-preview":
            values.extend(["--bytes", str(args.bytes), "--chars", str(args.chars)])
        if getattr(args, "fail_on_warning", False):
            values.append("--fail-on-warning")
        if command == "encoding-convert":
            values.extend(["--from-encoding", args.from_encoding, "--to-encoding", args.to_encoding])
            if getattr(args, "write", False):
                values.append("--write")
            values.extend(["--backup-suffix", args.backup_suffix])
            if getattr(args, "force", False):
                values.append("--force")
            if getattr(args, "fail_on_blocked", False):
                values.append("--fail-on-blocked")
        return _capture(text_encoding_convert.main, values)
    raise KeyError(command)
