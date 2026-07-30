from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl


def latest_runtime_event(repo: Path) -> dict[str, object]:
    line = (repo / "logs" / "runtime" / "runtime-events.log").read_text(encoding="utf-8").splitlines()[-1]
    return json.loads(line.split(" | ", 3)[3])


def test_ctl_tools_bom_scan_runs_utf8_bom_tool_and_writes_runtime_log(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "clean.md").write_text("# clean\n", encoding="utf-8")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "tools",
            "bom-scan",
            "--paths",
            "docs",
            "--extensions",
            ".md",
        ]
    )

    code, output = ctl.run(args)

    result = json.loads(output)
    assert code == 0
    assert result["artifact_type"] == "utf8-bom-scan"
    assert result["status"] == "ok"
    completed = latest_runtime_event(repo)
    assert completed["command"] == "tools bom-scan"
    assert completed["operation_id"] == "tools:bom-scan"


def test_ctl_tools_coverage_audit_skip_run_writes_outputs_and_runtime_log(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    runtime_dir = repo / "runtime"
    runtime_dir.mkdir(parents=True)
    (repo / ".git").mkdir()
    (runtime_dir / "sample.py").write_text("def main():\n    return 0\n", encoding="utf-8")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "tools",
            "coverage-audit",
            "--skip-run",
        ]
    )

    code, output = ctl.run(args)

    result = json.loads(output)
    assert code == 0
    assert result["coverage"]["measurement_status"] == "skipped"
    assert (repo / result["outputs"]["json"]).exists()
    assert (repo / result["outputs"]["markdown"]).exists()
    completed = latest_runtime_event(repo)
    assert completed["command"] == "tools coverage-audit"
    assert completed["operation_id"] == "tools:coverage-audit"


def test_ctl_tools_encoding_guard_preserves_finding_exit_code(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "broken.md").write_text("bad ??? text\n", encoding="utf-8")
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo),
            "tools",
            "encoding-guard",
            "--paths",
            "docs",
            "--extensions",
            ".md",
            "--fail-on-finding",
        ]
    )

    code, output = ctl.run(args)

    result = json.loads(output)
    assert code == 1
    assert result["artifact_type"] == "text-encoding-guard"
    assert result["status"] == "finding"
    completed = latest_runtime_event(repo)
    assert completed["command"] == "tools encoding-guard"
    assert completed["output"]["status"] == "failed"
