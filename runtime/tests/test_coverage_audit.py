from __future__ import annotations

import json
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
