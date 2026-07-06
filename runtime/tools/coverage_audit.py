from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso, write_json, write_markdown_bom  # noqa: E402


EXCLUDED_DIR_NAMES = {
    ".coverage_html",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "tests",
}


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit runtime pytest placement, CLI parser shape, and coverage.py measurement."
    )
    parser.add_argument("--repo-root", default="", help="Repository root. Defaults to auto-detection.")
    parser.add_argument(
        "--output-dir",
        default="work/coverage-audit/process-report",
        help="Output directory relative to repo root unless absolute.",
    )
    parser.add_argument("--skip-run", action="store_true", help="Skip pytest/coverage execution and emit static audit only.")
    parser.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        default=None,
        help="Arguments passed after `python -m pytest`. Defaults to `-q`.",
    )
    return parser


def should_skip_python_path(path: Path, runtime_root: Path) -> bool:
    try:
        relative_parts = path.relative_to(runtime_root).parts
    except ValueError:
        return True
    return any(part in EXCLUDED_DIR_NAMES for part in relative_parts)


def runtime_python_modules(runtime_root: Path) -> list[Path]:
    return sorted(
        path
        for path in runtime_root.rglob("*.py")
        if path.is_file() and not should_skip_python_path(path, runtime_root)
    )


def runtime_test_files(runtime_root: Path) -> list[Path]:
    tests_root = runtime_root / "tests"
    if not tests_root.exists():
        return []
    return sorted(path for path in tests_root.rglob("test_*.py") if path.is_file())


def parse_python(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8-sig"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None


def dotted_call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted_call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def count_test_functions(test_files: Sequence[Path]) -> int:
    count = 0
    for path in test_files:
        tree = parse_python(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                count += 1
    return count


def static_runtime_audit(runtime_root: Path) -> dict[str, Any]:
    modules = runtime_python_modules(runtime_root)
    tests = runtime_test_files(runtime_root)
    branch_node_types = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.Try,
        ast.With,
        ast.AsyncWith,
        ast.IfExp,
        ast.BoolOp,
        ast.ExceptHandler,
        ast.Match if hasattr(ast, "Match") else ast.If,
    )
    cli_modules: list[str] = []
    main_modules: list[str] = []
    parse_errors: list[str] = []
    branch_markers = 0
    add_argument_count = 0
    add_parser_count = 0

    for path in modules:
        tree = parse_python(path)
        rel_path = path.relative_to(runtime_root).as_posix()
        if tree is None:
            parse_errors.append(rel_path)
            continue
        has_build_parser = False
        has_main = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "build_parser":
                    has_build_parser = True
                if node.name == "main":
                    has_main = True
            if isinstance(node, branch_node_types):
                branch_markers += 1
            if isinstance(node, ast.Call):
                call_name = dotted_call_name(node.func)
                if call_name.endswith(".add_argument") or call_name == "add_argument":
                    add_argument_count += 1
                if call_name.endswith(".add_parser") or call_name == "add_parser":
                    add_parser_count += 1
        if has_build_parser:
            cli_modules.append(rel_path)
        if has_main:
            main_modules.append(rel_path)

    return {
        "runtime_py_modules": len(modules),
        "runtime_test_files": len(tests),
        "runtime_test_functions": count_test_functions(tests),
        "branch_marker_count": branch_markers,
        "build_parser_modules": cli_modules,
        "build_parser_count": len(cli_modules),
        "main_modules": main_modules,
        "main_count": len(main_modules),
        "add_argument_count": add_argument_count,
        "add_parser_count": add_parser_count,
        "parse_errors": parse_errors,
    }


def run_command(command: list[str], cwd: Path) -> CommandResult:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return CommandResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def command_payload(result: CommandResult) -> dict[str, Any]:
    return {
        "command": result.command,
        "returncode": result.returncode,
        "stdout_tail": result.stdout.splitlines()[-40:],
        "stderr_tail": result.stderr.splitlines()[-40:],
    }


def run_coverage_measurement(runtime_root: Path, pytest_args: Sequence[str]) -> dict[str, Any]:
    coverage_json_path = runtime_root / ".coverage.json"
    coverage_json_path.unlink(missing_ok=True)
    commands: list[CommandResult] = []
    for command in [
        [sys.executable, "-m", "coverage", "erase"],
        [sys.executable, "-m", "coverage", "run", "--branch", "-m", "pytest", *pytest_args],
        [sys.executable, "-m", "coverage", "report", "-m"],
        [sys.executable, "-m", "coverage", "json", "-o", str(coverage_json_path)],
    ]:
        result = run_command(command, runtime_root)
        commands.append(result)
        if not result.ok:
            return {
                "measurement_status": "blocked",
                "blocked_command": command_payload(result),
                "commands": [command_payload(item) for item in commands],
            }

    coverage_data = json.loads(coverage_json_path.read_text(encoding="utf-8"))
    totals = coverage_data.get("totals", {})
    return {
        "measurement_status": "measured",
        "commands": [command_payload(item) for item in commands],
        "totals": totals,
        "coverage_json": coverage_json_path.relative_to(runtime_root).as_posix(),
    }


def build_audit(
    repo_root: Path,
    output_dir: Path,
    *,
    skip_run: bool,
    pytest_args: Sequence[str],
) -> dict[str, Any]:
    runtime_root = repo_root / "runtime"
    static = static_runtime_audit(runtime_root)
    coverage = (
        {"measurement_status": "skipped", "reason": "--skip-run was specified"}
        if skip_run
        else run_coverage_measurement(runtime_root, pytest_args)
    )
    return {
        "schema_version": "1.0",
        "generated_at": utc_now_iso(),
        "repo_root": str(repo_root),
        "runtime_root": relative_to_repo(repo_root, runtime_root),
        "output_dir": relative_to_repo(repo_root, output_dir),
        "pytest_args": list(pytest_args),
        "static": static,
        "coverage": coverage,
    }


def format_percent(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}%"
    return "n/a"


def render_markdown(audit: dict[str, Any]) -> str:
    static = audit["static"]
    coverage = audit["coverage"]
    totals = coverage.get("totals", {}) if isinstance(coverage, dict) else {}
    lines = [
        "# Runtime coverage audit",
        "",
        f"- generated_at: `{audit['generated_at']}`",
        f"- runtime_root: `{audit['runtime_root']}`",
        f"- measurement_status: `{coverage.get('measurement_status', 'unknown')}`",
        "",
        "## Static audit",
        "",
        "| item | value |",
        "| --- | ---: |",
        f"| runtime Python modules | {static['runtime_py_modules']} |",
        f"| runtime pytest files | {static['runtime_test_files']} |",
        f"| runtime test functions | {static['runtime_test_functions']} |",
        f"| branch marker count | {static['branch_marker_count']} |",
        f"| build_parser modules | {static['build_parser_count']} |",
        f"| main modules | {static['main_count']} |",
        f"| add_argument calls | {static['add_argument_count']} |",
        f"| add_parser calls | {static['add_parser_count']} |",
        f"| parse errors | {len(static['parse_errors'])} |",
        "",
        "## Coverage totals",
        "",
        "| item | value |",
        "| --- | ---: |",
        f"| percent covered | {format_percent(totals.get('percent_covered'))} |",
        f"| covered lines | {totals.get('covered_lines', 'n/a')} |",
        f"| missing lines | {totals.get('missing_lines', 'n/a')} |",
        f"| num statements | {totals.get('num_statements', 'n/a')} |",
        f"| covered branches | {totals.get('covered_branches', 'n/a')} |",
        f"| missing branches | {totals.get('missing_branches', 'n/a')} |",
        f"| num branches | {totals.get('num_branches', 'n/a')} |",
        "",
    ]
    if coverage.get("measurement_status") == "blocked":
        lines.extend(
            [
                "## Blocked command",
                "",
                "```json",
                json.dumps(coverage.get("blocked_command", {}), ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def resolve_output_dir(repo_root: Path, value: str) -> Path:
    output_dir = Path(value)
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir
    return output_dir.resolve()


def write_outputs(output_dir: Path, audit: dict[str, Any]) -> tuple[Path, Path]:
    json_path = output_dir / "runtime-coverage-audit.json"
    markdown_path = output_dir / "runtime-coverage-audit.md"
    write_json(json_path, audit)
    write_markdown_bom(markdown_path, render_markdown(audit))
    return json_path, markdown_path


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    output_dir = resolve_output_dir(repo_root, args.output_dir)
    pytest_args = args.pytest_args if args.pytest_args is not None else ["-q"]
    audit = build_audit(repo_root, output_dir, skip_run=args.skip_run, pytest_args=pytest_args)
    json_path, markdown_path = write_outputs(output_dir, audit)
    audit["outputs"] = {
        "json": relative_to_repo(repo_root, json_path),
        "markdown": relative_to_repo(repo_root, markdown_path),
    }
    write_outputs(output_dir, audit)
    return audit


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        audit = run(args)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(audit["outputs"], ensure_ascii=False, indent=2))
    return 0 if audit["coverage"].get("measurement_status") in {"measured", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
