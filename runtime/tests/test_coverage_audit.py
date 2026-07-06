from __future__ import annotations

import json
import runpy
from pathlib import Path

from runtime.tools import coverage_audit


def test_static_runtime_audit_counts_cli_and_branch_markers(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    module = runtime_root / "workflow" / "sample.py"
    test_file = runtime_root / "tests" / "test_sample.py"
    module.parent.mkdir(parents=True)
    test_file.parent.mkdir(parents=True)
    module.write_text(
        "\n".join(
            [
                "import argparse",
                "",
                "def build_parser():",
                "    parser = argparse.ArgumentParser()",
                "    sub = parser.add_subparsers()",
                "    parser.add_argument('--flag', action='store_true')",
                "    sub.add_parser('run')",
                "    return parser",
                "",
                "def main(argv=None):",
                "    if argv:",
                "        return 0",
                "    return 1",
            ]
        ),
        encoding="utf-8",
    )
    test_file.write_text(
        "\n".join(
            [
                "def test_one():",
                "    assert True",
                "",
                "def helper():",
                "    return False",
            ]
        ),
        encoding="utf-8",
    )

    result = coverage_audit.static_runtime_audit(runtime_root)

    assert result["runtime_py_modules"] == 1
    assert result["runtime_test_files"] == 1
    assert result["runtime_test_functions"] == 1
    assert result["build_parser_count"] == 1
    assert result["main_count"] == 1
    assert result["add_argument_count"] == 1
    assert result["add_parser_count"] == 1
    assert result["branch_marker_count"] >= 1


def test_run_skip_run_writes_json_and_markdown(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    (repo_root / "work").mkdir()
    runtime_root = repo_root / "runtime"
    runtime_root.mkdir()
    (runtime_root / "tool.py").write_text("def main():\n    return 0\n", encoding="utf-8")
    args = coverage_audit.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "--output-dir",
            "work/coverage-audit/process-report",
            "--skip-run",
        ]
    )

    result = coverage_audit.run(args)

    json_path = repo_root / result["outputs"]["json"]
    markdown_path = repo_root / result["outputs"]["markdown"]
    assert json_path.exists()
    assert markdown_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["coverage"]["measurement_status"] == "skipped"
    assert saved["outputs"]["markdown"] == "work/coverage-audit/process-report/runtime-coverage-audit.md"


def test_run_coverage_measurement_removes_stale_json_before_commands(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runtime_root = tmp_path / "runtime"
    runtime_root.mkdir()
    coverage_json = runtime_root / ".coverage.json"
    coverage_json.write_text("stale", encoding="utf-8")
    commands: list[list[str]] = []

    def fake_run_command(command: list[str], cwd: Path) -> coverage_audit.CommandResult:
        commands.append(command)
        assert cwd == runtime_root
        assert not coverage_json.exists()
        if command[:3] == [command[0], "-m", "coverage"] and command[3] == "json":
            coverage_json.write_text(
                json.dumps(
                    {
                        "totals": {
                            "covered_lines": 1,
                            "missing_lines": 0,
                            "percent_covered": 100.0,
                        }
                    }
                ),
                encoding="utf-8",
            )
        return coverage_audit.CommandResult(command=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(coverage_audit, "run_command", fake_run_command)

    result = coverage_audit.run_coverage_measurement(runtime_root, ["-q"])

    assert result["measurement_status"] == "measured"
    assert result["coverage_json"] == ".coverage.json"
    assert len(commands) == 4


def test_coverage_audit_static_edges_and_blocked_measurement(monkeypatch, tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    runtime_root.mkdir()
    bad_module = runtime_root / "bad.py"
    bad_module.write_text("def broken(:\n", encoding="utf-8")
    no_main_module = runtime_root / "no_main.py"
    no_main_module.write_text("VALUE = 1\n", encoding="utf-8")

    assert coverage_audit.should_skip_python_path(tmp_path / "outside.py", runtime_root) is True
    assert coverage_audit.runtime_test_files(runtime_root) == []
    assert coverage_audit.parse_python(bad_module) is None
    assert coverage_audit.dotted_call_name(ast_node := __import__("ast").Constant(value=1)) == ""

    static = coverage_audit.static_runtime_audit(runtime_root)
    assert static["parse_errors"] == ["bad.py"]
    assert "no_main.py" not in static["main_modules"]

    calls: list[list[str]] = []

    def fake_run_command(command: list[str], cwd: Path) -> coverage_audit.CommandResult:
        calls.append(command)
        return coverage_audit.CommandResult(command=command, returncode=2, stdout="out", stderr="err")

    monkeypatch.setattr(coverage_audit, "run_command", fake_run_command)
    result = coverage_audit.run_coverage_measurement(runtime_root, ["-q"])

    assert result["measurement_status"] == "blocked"
    assert result["blocked_command"]["returncode"] == 2
    assert len(calls) == 1

    bad_test = runtime_root / "tests" / "test_bad.py"
    bad_test.parent.mkdir()
    bad_test.write_text("def broken(:\n", encoding="utf-8")
    assert coverage_audit.count_test_functions([bad_test]) == 0


def test_coverage_audit_command_and_format_edges(monkeypatch, tmp_path: Path) -> None:
    def fake_subprocess_run(command, cwd, text, capture_output, check):
        assert text is True
        assert capture_output is True
        assert check is False
        return __import__("subprocess").CompletedProcess(command, 3, stdout="out", stderr="err")

    monkeypatch.setattr(coverage_audit.subprocess, "run", fake_subprocess_run)

    result = coverage_audit.run_command(["tool"], tmp_path)

    assert result.returncode == 3
    assert result.stdout == "out"
    assert result.stderr == "err"
    assert coverage_audit.format_percent(12.345) == "12.35%"


def test_coverage_audit_render_main_and_script_load_paths(monkeypatch, tmp_path: Path, capsys) -> None:
    audit = {
        "generated_at": "now",
        "runtime_root": "runtime",
        "static": {
            "runtime_py_modules": 1,
            "runtime_test_files": 0,
            "runtime_test_functions": 0,
            "branch_marker_count": 0,
            "build_parser_count": 0,
            "main_count": 0,
            "add_argument_count": 0,
            "add_parser_count": 0,
            "parse_errors": [],
        },
        "coverage": {
            "measurement_status": "blocked",
            "blocked_command": {"command": ["pytest"], "returncode": 1},
            "totals": {"percent_covered": "unknown"},
        },
    }

    markdown = coverage_audit.render_markdown(audit)
    assert "measurement_status: `blocked`" in markdown
    assert "Blocked command" in markdown
    assert "| percent covered | n/a |" in markdown
    assert coverage_audit.resolve_output_dir(tmp_path, str(tmp_path / "absolute")).is_absolute()

    monkeypatch.setattr(
        coverage_audit,
        "run",
        lambda args: {"outputs": {"json": "out.json"}, "coverage": {"measurement_status": "skipped"}},
    )
    assert coverage_audit.main(["--repo-root", str(tmp_path), "--skip-run"]) == 0
    assert '"json": "out.json"' in capsys.readouterr().out

    monkeypatch.setattr(
        coverage_audit,
        "run",
        lambda args: {"outputs": {"json": "out.json"}, "coverage": {"measurement_status": "blocked"}},
    )
    assert coverage_audit.main(["--repo-root", str(tmp_path), "--skip-run"]) == 1

    def raise_error(args):
        raise RuntimeError("boom")

    monkeypatch.setattr(coverage_audit, "run", raise_error)
    assert coverage_audit.main(["--repo-root", str(tmp_path), "--skip-run"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(coverage_audit.__file__)))
    assert namespace["build_parser"]
