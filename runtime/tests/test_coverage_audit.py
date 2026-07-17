from __future__ import annotations

import json
import runpy
from pathlib import Path

from runtime.tools import coverage_audit, text_encoding_convert, text_encoding_guard, utf8_bom


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


def test_text_encoding_guard_does_not_flag_saved_mojibake_without_dataset(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    original = "\u3053\u308c\u306f\u65e5\u672c\u8a9e\u3067\u3059\n"
    damaged = original.encode("utf-8").decode("latin1")
    target = docs / "guide.md"
    target.write_text(damaged, encoding="utf-8")

    scan = text_encoding_guard.scan_files(repo, ["docs"], {".md"})

    assert scan["status"] == "ok"
    assert scan["findings"] == []
    assert text_encoding_guard.main(["--repo-root", str(repo), "scan", "--paths", "docs", "--fail-on-finding"]) == 0
    capsys.readouterr()
    assert target.read_text(encoding="utf-8") == damaged


def test_text_encoding_convert_inspects_and_converts_cp932_to_utf8(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    original = "\u65e5\u672c\u8a9e\u306e\u8aac\u660e\u3067\u3059\n"
    target = docs / "sjis.md"
    target.write_bytes(original.encode("cp932"))

    inspected = text_encoding_convert.inspect_files(repo, ["docs"], {".md"}, ("cp932", "shift_jis", "utf-8"))

    assert inspected["status"] == "ok"
    assert inspected["files"][0]["preferred_encoding"] == "cp932"
    args = text_encoding_convert.build_parser().parse_args(
        ["--repo-root", str(repo), "convert", "--paths", "docs", "--from-encoding", "cp932", "--write"]
    )
    result = text_encoding_convert.convert_files(args)

    assert result["status"] == "converted"
    assert result["converted"][0]["written"] is True
    assert (docs / "sjis.md.encoding-bak").exists()
    assert target.read_text(encoding="utf-8") == original


def test_text_encoding_convert_preview_shows_hex_and_decode_candidates(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    original = "\u3053\u308c\u306f\u65e5\u672c\u8a9e\u3067\u3059\n"
    saved_mojibake = original.encode("utf-8").decode("latin1")
    mojibake_path = docs / "mojibake.md"
    cp932_path = docs / "sjis.md"
    mojibake_path.write_text(saved_mojibake, encoding="utf-8")
    cp932_path.write_bytes(original.encode("cp932"))

    preview = text_encoding_convert.preview_files(
        repo,
        ["docs"],
        {".md"},
        ("cp932", "utf-8", "latin1"),
        max_bytes=12,
        max_chars=8,
    )

    by_path = {item["path"]: item for item in preview["files"]}
    assert preview["status"] == "ok"
    assert by_path["docs/mojibake.md"]["classification"] == "utf8-compatible-with-other-decoders"
    assert by_path["docs/mojibake.md"]["hex_truncated"] is True
    assert by_path["docs/sjis.md"]["classification"] == "non-utf8-candidate"
    assert by_path["docs/sjis.md"]["preferred_encoding"] == "cp932"
    assert any(item["encoding"] == "utf-8" and item["ok"] for item in by_path["docs/mojibake.md"]["previews"])

    assert (
        text_encoding_convert.main(
            [
                "--repo-root",
                str(repo),
                "preview",
                "--paths",
                "docs",
                "--extensions",
                ".md",
                "--bytes",
                "12",
                "--chars",
                "8",
            ]
        )
        == 0
    )
    assert '"artifact_type": "text-encoding-preview"' in capsys.readouterr().out


def test_text_encoding_convert_blocks_unsafe_cp932_conversion_for_utf8_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    original = "\u3053\u308c\u306fUTF-8\u306e\u672c\u6587\u3067\u3059\n"
    target = docs / "utf8.md"
    target.write_text(original, encoding="utf-8")

    args = text_encoding_convert.build_parser().parse_args(
        ["--repo-root", str(repo), "convert", "--paths", "docs", "--from-encoding", "cp932", "--write"]
    )
    result = text_encoding_convert.convert_files(args)

    assert result["status"] == "blocked"
    assert result["converted"] == []
    assert not (docs / "utf8.md.encoding-bak").exists()
    assert target.read_text(encoding="utf-8") == original


def test_text_encoding_guard_reports_lossy_damage_without_writing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    target = docs / "broken.md"
    lossy_text = "missing text " + "?" * 3 + "\n"
    target.write_text(lossy_text, encoding="utf-8")

    scan = text_encoding_guard.scan_files(repo, ["docs"], {".md"})

    assert scan["status"] == "finding"
    assert scan["findings"][0]["kind"] == "lossy-marker"
    assert text_encoding_guard.main(["--repo-root", str(repo), "scan", "--paths", "docs", "--fail-on-finding"]) == 1
    assert target.read_text(encoding="utf-8") == lossy_text


def test_utf8_bom_scan_and_strip_removes_only_bom(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    target = docs / "guide.md"
    target.write_bytes(utf8_bom.UTF8_BOM + "body\n".encode("utf-8"))

    scan = utf8_bom.scan_files(repo, ["docs"], {".md"})

    assert scan["status"] == "finding"
    assert scan["bom_files"] == [{"path": "docs/guide.md", "size_bytes": len(utf8_bom.UTF8_BOM) + 5}]
    assert utf8_bom.main(["--repo-root", str(repo), "scan", "--paths", "docs", "--fail-on-finding"]) == 1
    assert '"artifact_type": "utf8-bom-scan"' in capsys.readouterr().out

    dry_run_args = utf8_bom.build_parser().parse_args(["--repo-root", str(repo), "strip", "--paths", "docs"])
    dry_run = utf8_bom.strip_files(dry_run_args)

    assert dry_run["status"] == "candidate"
    assert dry_run["stripped"][0]["written"] is False
    assert target.read_bytes().startswith(utf8_bom.UTF8_BOM)

    write_args = utf8_bom.build_parser().parse_args(["--repo-root", str(repo), "strip", "--paths", "docs", "--write"])
    written = utf8_bom.strip_files(write_args)

    assert written["status"] == "stripped"
    assert written["stripped"][0]["written"] is True
    assert written["stripped"][0]["backup"] == "docs/guide.md.bom-bak"
    assert target.read_bytes() == b"body\n"
    assert (docs / "guide.md.bom-bak").read_bytes().startswith(utf8_bom.UTF8_BOM)


def test_utf8_bom_skips_binary_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    binary = docs / "data.txt"
    binary.write_bytes(utf8_bom.UTF8_BOM + b"\x00data")

    scan = utf8_bom.scan_files(repo, ["docs"], {".txt"})

    assert scan["status"] == "ok"
    assert scan["bom_files"] == []
    assert scan["files_skipped_binary"] == ["docs/data.txt"]


def test_utf8_bom_strip_can_disable_backup(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    target = docs / "guide.md"
    target.write_bytes(utf8_bom.UTF8_BOM + b"body\n")

    args = utf8_bom.build_parser().parse_args(
        ["--repo-root", str(repo), "strip", "--paths", "docs", "--write", "--backup-suffix="]
    )
    result = utf8_bom.strip_files(args)

    assert result["status"] == "stripped"
    assert result["stripped"][0]["backup"] == ""
    assert not (docs / "guide.md.bom-bak").exists()
    assert target.read_bytes() == b"body\n"
