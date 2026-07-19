from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.workflow import context_first, knowledge_capture


def make_args(repo_root: Path, issue: str = "issue-77", **overrides) -> argparse.Namespace:
    defaults = {
        "issue": issue,
        "repository": "",
        "branch": "",
        "base_work_id": "",
        "repo_root": str(repo_root),
        "source_dir": "",
        "dry_run": True,
        "allow_legacy_scm_fallback": False,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def make_work_with_manifest(repo_root: Path, issue: str = "issue-77") -> Path:
    work_dir = repo_root / "work" / issue
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    scm_state = context_dir / "scm-state.json"
    scm_state.write_text(
        json.dumps(
            {
                "repository": "owner/repo",
                "github_repo": "owner/github-repo",
                "working_branch": f"feature/{issue}",
                "base_work_id": "develop",
            }
        ),
        encoding="utf-8",
    )
    context_first.register_context(
        repo_root,
        work_dir,
        work_id=issue,
        context_type="scm-state",
        path=scm_state,
        required=True,
        generated_by="runtime-scm",
        owner="workflow",
        schema=".github/schemas/scm-state.schema.json",
    )
    return work_dir


def test_parser_and_small_helpers(tmp_path: Path) -> None:
    parsed = knowledge_capture.build_parser().parse_args(
        [
            "--issue",
            "issue-1",
            "--repository",
            "owner/repo",
            "--branch",
            "feature/issue-1",
            "--base-work-id",
            "develop",
            "--repo-root",
            str(tmp_path),
            "--source-dir",
            "work/issue-1/source/repository",
            "--dry-run",
            "--allow-legacy-scm-fallback",
        ]
    )

    assert parsed.issue == "issue-1"
    assert parsed.dry_run is True
    assert parsed.allow_legacy_scm_fallback is True
    assert knowledge_capture.close_archive_target(tmp_path, "issue-1") == tmp_path / "work" / "close" / "improvement" / "issue-1"
    assert knowledge_capture.list_files(tmp_path / "missing") == []
    assert knowledge_capture.is_scaffold_file(Path("README.md"))
    assert not knowledge_capture.is_scaffold_file(Path("evidence.md"))
    assert knowledge_capture.read_text_sample(tmp_path / "missing.md") == ""
    assert knowledge_capture.markdown_path_list(tmp_path, []) == "- なし"

    files = []
    for index in range(32):
        path = tmp_path / f"f{index}.md"
        path.write_text("x", encoding="utf-8")
        files.append(path)
    rendered = knowledge_capture.markdown_path_list(tmp_path, files, limit=30)
    assert "- ... 2 more" in rendered


def test_path_file_docs_candidate_and_scaffold_helpers(tmp_path: Path) -> None:
    docs_root = tmp_path / "docs" / "evidence" / "issue-1"
    scaffold = knowledge_capture.scaffold_evidence_docs(docs_root, dry_run=True)
    assert scaffold[0]["planned"] is True
    assert not (docs_root / "README.md").exists()

    created = knowledge_capture.scaffold_evidence_docs(docs_root, dry_run=False)
    assert created[0]["created"] is True
    second = knowledge_capture.scaffold_evidence_docs(docs_root, dry_run=False)
    assert second[0]["created"] is False
    assert (docs_root / "integration" / "qtest" / "README.md").exists()

    status = knowledge_capture.path_status(docs_root)
    assert status["file_count"] >= 1
    assert status["evidence_file_count"] == 0
    evidence = docs_root / "ut" / "result.md"
    evidence.write_text("Docker Desktop and PyQt6 camera evidence\n", encoding="utf-8")
    status = knowledge_capture.path_status(docs_root)
    assert evidence in status["evidence_files"]

    file_status = knowledge_capture.file_status(evidence)
    assert file_status["exists"] is True
    assert file_status["size"] > 0
    assert knowledge_capture.file_status(docs_root / "missing.md")["exists"] is False

    candidates = knowledge_capture.find_docs_candidates([evidence, evidence])
    assert [candidate["topic"] for candidate in candidates] == ["camera", "Docker", "Docker Desktop", "PyQt6"]

    relative = knowledge_capture.relative_status(tmp_path, knowledge_capture.path_status(docs_root / "ut"))
    assert relative["path"] == "docs/evidence/issue-1/ut"
    assert all(isinstance(path, str) for path in relative["files"])


def test_latest_issue_title_and_pr_text_helpers(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-2"
    report_dir = work_dir / "process-report"
    report_dir.mkdir(parents=True)
    (report_dir / "github-issue-1.json").write_text(json.dumps({"title": ""}), encoding="utf-8")
    (report_dir / "github-issue-2.json").write_text(json.dumps({"title": "Issue title"}), encoding="utf-8")
    base_report_dir = tmp_path / "work" / "develop" / "process-report"
    base_report_dir.mkdir(parents=True)
    (base_report_dir / "github-issue-3.json").write_text(json.dumps({"title": "Base title"}), encoding="utf-8")

    assert knowledge_capture.latest_issue_title(tmp_path, work_dir) == "Issue title"
    assert knowledge_capture.latest_issue_title(tmp_path, work_dir, "develop") == "Base title"
    assert knowledge_capture.latest_issue_title(tmp_path, tmp_path / "missing") == ""
    titleless_work = tmp_path / "work" / "issue-titleless"
    titleless_report = titleless_work / "process-report"
    titleless_report.mkdir(parents=True)
    (titleless_report / "github-issue-1.json").write_text(json.dumps({"title": ""}), encoding="utf-8")
    assert knowledge_capture.latest_issue_title(tmp_path, titleless_work) == ""
    assert knowledge_capture.build_pr_title("issue-2", "owner/repo", "Existing title") == "Existing title"
    assert "owner/repo" in knowledge_capture.build_pr_title("issue-2", "owner/repo")
    assert "target repository" in knowledge_capture.build_pr_title("issue-2", "")

    docs_status = {
        key: {"relative_path": f"docs/evidence/issue-2/{key}"}
        for key in ["test_specifications", "ut", "integration", "human_check"]
    }
    assert "# Pull Request" in knowledge_capture.build_pr_description("issue-2", "owner/repo", "feature/issue-2", docs_status)
    assert "# Merge Comment" in knowledge_capture.build_merge_comment("issue-2")


def test_context_fallback_modes_and_errors(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-3"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    fallback = context_dir / "scm-state.json"
    fallback.write_text(json.dumps({"repository": "fallback/repo"}), encoding="utf-8")

    data, resolution = knowledge_capture.read_context_with_fallback(
        tmp_path,
        work_dir,
        context_type="scm-state",
        fallback_relative_path="context/scm-state.json",
        require_manifest=False,
    )
    assert data["repository"] == "fallback/repo"
    assert resolution["mode"] == "fallback"
    assert resolution["manifest_path"] == ""

    with pytest.raises(RuntimeError, match="context-manifest missing"):
        knowledge_capture.read_context_with_fallback(
            tmp_path,
            work_dir,
            context_type="scm-state",
            fallback_relative_path="context/scm-state.json",
            require_manifest=True,
        )

    context_first.register_context(
        tmp_path,
        work_dir,
        work_id="issue-3",
        context_type="other-context",
        path=context_dir / "other.json",
        required=False,
        generated_by="test",
        owner="workflow",
        schema="",
    )
    with pytest.raises(RuntimeError, match="scm-state not registered"):
        knowledge_capture.read_context_with_fallback(
            tmp_path,
            work_dir,
            context_type="scm-state",
            fallback_relative_path="context/scm-state.json",
            require_manifest=True,
        )

    fallback.write_text("[]", encoding="utf-8")
    data, resolution = knowledge_capture.read_context_with_fallback(
        tmp_path,
        work_dir,
        context_type="scm-state",
        fallback_relative_path="context/scm-state.json",
        require_manifest=True,
        allow_legacy_fallback=True,
    )
    assert data == {}
    assert resolution["found"] is True


def test_knowledge_capture_generates_reports_json_and_context(tmp_path: Path) -> None:
    issue = "issue-88"
    work_dir = make_work_with_manifest(tmp_path, issue)
    source_dir = work_dir / "source" / "repository"
    docs_root = source_dir / "docs" / "evidence" / issue
    (docs_root / "test_specifications").mkdir(parents=True)
    (docs_root / "test_specifications" / "unit-test-cases.md").write_text("unit cases\n", encoding="utf-8")
    (docs_root / "ut").mkdir()
    (docs_root / "ut" / "pytest.md").write_text("pytest evidence\n", encoding="utf-8")
    (work_dir / "process-report").mkdir()
    (work_dir / "process-report" / "github-issue-1.json").write_text(json.dumps({"title": "Fix telemetry"}), encoding="utf-8")
    (work_dir / "process-report" / "report.md").write_text("Docker Desktop and MSYS2 operations note\n", encoding="utf-8")
    (work_dir / "test-specifications").mkdir()
    (work_dir / "test-specifications" / "spec.md").write_text("Packet Monitor spec\n", encoding="utf-8")
    (tmp_path / "work" / "develop" / "process-report").mkdir(parents=True)

    result = knowledge_capture.knowledge_capture(make_args(tmp_path, issue, dry_run=False))

    assert result["repository"] == "owner/github-repo"
    assert result["branch"] == f"feature/{issue}"
    assert result["issue_title"] == "Fix telemetry"
    assert result["pull_request_title"] == "Fix telemetry"
    assert result["rag_candidate_count"] >= 3
    assert {candidate["topic"] for candidate in result["docs_candidates"]} >= {"Docker", "Docker Desktop", "MSYS2", "Packet Monitor"}
    assert result["docs_status"]["test_specifications"]["evidence_file_count"] == 1
    assert result["archive"]["status"] == "report-only-ready"
    assert result["base_work_reset"]["base_work_id"] == "develop"
    assert result["base_work_reset"]["source_exists"] is True
    assert result["context_resolution"]["scm_state"]["mode"] == "manifest"

    process_report_dir = work_dir / "process-report"
    assert (process_report_dir / "pull-request-title.md").read_text(encoding="utf-8") == "Fix telemetry\n"
    assert (process_report_dir / "knowledge-capture-report.md").exists()
    json_files = list(process_report_dir.glob("knowledge-capture-*.json"))
    assert len(json_files) == 1
    manifest = json.loads((work_dir / "context" / "context-manifest.json").read_text(encoding="utf-8"))
    assert "knowledge-capture" in {item["type"] for item in manifest["contexts"]}


def test_knowledge_capture_dry_run_close_archive_fallback_and_missing_work(tmp_path: Path) -> None:
    issue = "issue-99"
    close_work = tmp_path / "work" / "close" / "improvement" / issue
    context_dir = close_work / "context"
    context_dir.mkdir(parents=True)
    (context_dir / "scm-state.json").write_text(
        json.dumps({"repository": "archived/repo", "current_branch": "archived-branch"}),
        encoding="utf-8",
    )

    result = knowledge_capture.knowledge_capture(make_args(tmp_path, issue, dry_run=True))

    assert result["archive"]["status"] == "already-archived"
    assert result["context_resolution"]["manifest_scm_state_required"] is False
    assert result["context_resolution"]["legacy_scm_fallback_allowed"] is True
    assert result["repository"] == "archived/repo"
    assert result["branch"] == "archived-branch"
    assert result["scaffold_status"][0]["planned"] is True
    assert not (close_work / "process-report" / "pull-request-title.md").exists()

    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        knowledge_capture.knowledge_capture(make_args(tmp_path, "issue-missing"))


def test_main_outputs_json_and_reports_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    issue = "issue-main"
    work_dir = make_work_with_manifest(tmp_path, issue)
    (work_dir / "source" / "repository" / "docs").mkdir(parents=True)

    assert knowledge_capture.main(["--issue", issue, "--repo-root", str(tmp_path), "--dry-run"]) == 0
    assert f'"issue": "{issue}"' in capsys.readouterr().out

    def raise_error(args):
        raise RuntimeError("boom")

    monkeypatch.setattr(knowledge_capture, "knowledge_capture", raise_error)
    assert knowledge_capture.main(["--issue", issue, "--repo-root", str(tmp_path)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(knowledge_capture.__file__)))
    assert namespace["build_parser"]
