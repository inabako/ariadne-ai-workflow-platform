from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.workflow import corrective_action_report


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    return repo


def make_args(repo: Path, **overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "repo_root": str(repo),
        "command": "register",
        "report_path": "rag/corrective-action-report/report.md",
        "repository": "",
        "target_branch": "feature/demo",
        "work_id": "",
        "work_dir": "",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_corrective_action_report_parse_helpers() -> None:
    assert corrective_action_report.branch_to_work_id("feature/issue-1") == "feature-issue-1"
    assert corrective_action_report.branch_to_work_id(r"fix\windows/path") == "fix-windows-path"
    assert corrective_action_report.parse_scalar("") == ""
    assert corrective_action_report.parse_scalar("'quoted'") == "quoted"
    assert corrective_action_report.parse_scalar("[alpha, 'beta', \"gamma\"]") == ["alpha", "beta", "gamma"]

    text = "\n".join(
        [
            "---",
            "# ignored comment",
            "repository: owner/repo",
            "branch:",
            "  - develop",
            "  - main",
            "status:",
            "---",
            "# Body",
        ]
    )

    metadata = corrective_action_report.parse_front_matter(text)

    assert metadata["repository"] == "owner/repo"
    assert metadata["branch"] == ["develop", "main"]
    assert metadata["status"] == ""
    assert corrective_action_report.parse_front_matter("# no front matter") == {}


def test_corrective_action_report_count_section_items() -> None:
    text = "\n".join(
        [
            "# Report",
            "",
            "## Findings",
            "",
            "- first finding",
            "| F-001 | high | runtime | finding |",
            "| note | ignored |",
            "",
            "## RAG Capture Candidates",
            "- capture one",
            "| CAR-002 | candidate |",
            "",
            "## Next",
            "- outside",
        ]
    )

    assert corrective_action_report.count_section_items(text, "Findings") == 2
    assert corrective_action_report.count_section_items(text, "RAG Capture Candidates") == 2
    assert corrective_action_report.count_section_items(text, "Missing") == 0


def test_corrective_action_report_build_context_existing_and_missing_report(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    report = repo / "rag" / "corrective-action-report" / "report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "\n".join(
            [
                "---",
                "repository: front/repo",
                "branch: develop",
                "commit: abcdef0",
                "status: reviewed",
                "---",
                "# Corrective Action Report",
                "",
                "## Findings",
                "- finding",
                "",
                "## RAG Capture Candidates",
                "- capture",
            ]
        ),
        encoding="utf-8",
    )

    context = corrective_action_report.build_report_context(
        repo,
        make_args(repo, repository="", target_branch="", report_path="rag/corrective-action-report/report.md"),
        report,
    )

    assert context["repository"] == "front/repo"
    assert context["target_branch"] == "develop"
    assert context["target_commit"] == "abcdef0"
    assert context["status"] == "reviewed"
    assert context["report_exists"] is True
    assert context["rag_candidate"] is True
    assert context["docs_candidate"] is False
    assert context["finding_summary"] == {"finding_count": 1, "rag_capture_candidate_count": 1}

    missing = repo / "rag" / "corrective-action-report" / "missing.md"
    missing_context = corrective_action_report.build_report_context(
        repo,
        make_args(repo, repository="arg/repo", target_branch="arg-branch"),
        missing,
    )
    assert missing_context["repository"] == "arg/repo"
    assert missing_context["target_branch"] == "arg-branch"
    assert missing_context["status"] == "draft"
    assert missing_context["report_exists"] is False
    assert missing_context["finding_summary"]["finding_count"] == 0


def test_corrective_action_report_register_with_explicit_work_dir_and_show(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    report = repo / "rag" / "corrective-action-report" / "report.md"
    report.parent.mkdir(parents=True)
    report.write_text("---\nrepository: owner/repo\nbranch: develop\n---\n\n## Findings\n- one\n", encoding="utf-8")
    work_dir = repo / "custom-work"
    args = make_args(
        repo,
        report_path=str(report),
        repository="",
        target_branch="",
        work_id="",
        work_dir=str(work_dir),
    )

    result = corrective_action_report.run_register(args)

    assert result["status"] == "registered"
    assert result["work_id"] == "custom-work"
    assert result["work_dir"] == "custom-work"
    context_path = work_dir / "context" / "corrective-action-report.json"
    manifest_path = work_dir / "context" / "context-manifest.json"
    assert context_path.exists()
    assert manifest_path.exists()
    context = json.loads(context_path.read_text(encoding="utf-8"))
    assert context["repository"] == "owner/repo"

    shown = corrective_action_report.run_show(
        argparse.Namespace(
            repo_root=str(repo),
            command="show",
            target_branch="",
            work_id="",
            work_dir=str(work_dir),
        )
    )
    assert shown["status"] == "ok"
    assert shown["work_id"] == "custom-work"
    assert shown["context"]["artifact_type"] == "corrective-action-report"


def test_corrective_action_report_register_missing_report_and_show_missing(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    args = make_args(
        repo,
        report_path="rag/corrective-action-report/missing.md",
        repository="owner/repo",
        target_branch="feature/missing-report",
    )

    result = corrective_action_report.run_register(args)

    assert result["status"] == "registered-missing-report"
    assert result["work_id"] == "feature-missing-report"
    context = json.loads((repo / result["context_path"]).read_text(encoding="utf-8"))
    assert context["report_exists"] is False

    shown = corrective_action_report.run_show(
        argparse.Namespace(
            repo_root=str(repo),
            command="show",
            target_branch="feature/no-context",
            work_id="",
            work_dir="",
        )
    )
    assert shown["status"] == "missing"
    assert shown["work_id"] == "feature-no-context"
    assert shown["context"] == {}


def test_corrective_action_report_parser_and_main_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    repo = make_repo(tmp_path)
    parser = corrective_action_report.build_parser()
    register_args = parser.parse_args(
        [
            "--repo-root",
            str(repo),
            "register",
            "--report-path",
            "rag/corrective-action-report/report.md",
            "--repository",
            "owner/repo",
            "--target-branch",
            "develop",
            "--work-id",
            "develop",
        ]
    )
    assert register_args.handler is corrective_action_report.run_register
    assert register_args.repository == "owner/repo"

    show_args = parser.parse_args(["--repo-root", str(repo), "show", "--work-id", "develop"])
    assert show_args.handler is corrective_action_report.run_show

    monkeypatch.setattr(
        corrective_action_report,
        "run_register",
        lambda args: {"status": "registered", "context_path": "work/x/context/corrective-action-report.json"},
    )
    assert corrective_action_report.main(
        [
            "--repo-root",
            str(repo),
            "register",
            "--report-path",
            "rag/corrective-action-report/report.md",
        ]
    ) == 0
    assert '"status": "registered"' in capsys.readouterr().out

    monkeypatch.setattr(corrective_action_report, "run_show", lambda args: {"status": "failed"})
    assert corrective_action_report.main(["--repo-root", str(repo), "show", "--work-id", "x"]) == 1
    assert '"status": "failed"' in capsys.readouterr().out

    def fail(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(corrective_action_report, "run_show", fail)
    assert corrective_action_report.main(["--repo-root", str(repo), "show", "--work-id", "x"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(corrective_action_report.__file__)))
    assert namespace["build_parser"]
