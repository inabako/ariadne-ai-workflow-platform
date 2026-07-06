from __future__ import annotations

import argparse
import json
import os
import re
import runpy
from pathlib import Path

import pytest

from runtime.workflow import close_archive


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    return repo


def write_complete_archive(archive: Path) -> None:
    archive.mkdir(parents=True, exist_ok=True)
    for name in close_archive.REPORT_FILES:
        path = archive / name
        path.write_text("{}\n" if name == "metadata.json" else f"# {name}\n", encoding="utf-8")


def test_parser_and_path_derivation_helpers(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    parser = close_archive.build_parser()
    prepared = parser.parse_args(
        [
            "prepare",
            "--issue",
            "issue-11",
            "--category",
            "new-system-dev",
            "--source-rag",
            "rag/a.md, rag/b.md",
            "--source-rag",
            "'rag/c.md'",
            "--no-auto-rag",
            "--require-rag",
        ]
    )
    pruned = parser.parse_args(["prune", "--work-id", "issue-11", "--execute", "--human-check", "approved"])
    audited = parser.parse_args(["audit", "--work-id", "issue-11"])

    assert prepared.handler is close_archive.run_prepare
    assert pruned.handler is close_archive.run_prune
    assert audited.handler is close_archive.run_audit
    assert close_archive.split_cli_paths(prepared.source_rag) == ["rag/a.md", "rag/b.md", "rag/c.md"]

    with pytest.raises(ValueError, match="--work-id or --issue is required"):
        close_archive.resolve_work_id(argparse.Namespace(work_id="", issue=""))

    assert close_archive.derive_category("github-knowledge-localty-system-robot-recent", "auto") == "github"
    assert close_archive.derive_category("vscode-environment", "auto") == "vscode"
    assert close_archive.derive_category("vscode-custom", "auto") == "vscode"
    assert close_archive.derive_category("issue-1", "new-system-dev") == "new-system-dev"

    monkeypatch.setattr(close_archive, "timestamp_archive_id", lambda: "260707070707_TEST")
    assert close_archive.derive_archive_id("prepare", "vscode-environment", "vscode", "", "") == "260707070707_TEST"
    assert close_archive.derive_archive_id("audit", "issue-1", "improvement", "", "") == "issue-1"
    assert close_archive.derive_archive_id("audit", "x", "github", "MANUAL", "") == "MANUAL"
    assert close_archive.derive_archive_id("audit", "x", "github", "", str(tmp_path / "ARCH")) == "ARCH"
    with pytest.raises(ValueError, match="archive-id or --archive-dir"):
        close_archive.derive_archive_id("audit", "github-knowledge-x", "github", "", "")

    suffix = close_archive.random_suffix(6)
    assert len(suffix) == 6
    assert re.fullmatch(r"[A-Z0-9]{6}", suffix)
    namespace = runpy.run_path(str(Path(close_archive.__file__)))
    assert namespace["build_parser"]
    assert re.fullmatch(r"\d{12}_[A-Z0-9]{8}", namespace["timestamp_archive_id"]())


def test_resolve_paths_supports_issue_alias_explicit_dirs_and_repo_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    source = repo / "custom-source"
    archive = repo / "custom-archive"
    monkeypatch.setattr(close_archive, "find_repo_root", lambda: repo)

    resolved = close_archive.resolve_paths(
        argparse.Namespace(
            command="prepare",
            repo_root=None,
            issue="issue-42",
            work_id="",
            category="auto",
            archive_id="",
            source_work_dir=str(source),
            archive_dir=str(archive),
        )
    )

    assert resolved == (
        repo,
        source.resolve(),
        archive.resolve(),
        "issue-42",
        "improvement",
        "custom-archive",
    )


def test_archive_path_safety_and_prune_target_detection(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    write_complete_archive(archive)
    nested_parent = archive / "source"
    nested_git = nested_parent / ".git"
    nested_git.mkdir(parents=True)
    nested_cache = archive / "logs" / "__pycache__"
    nested_cache.mkdir(parents=True)
    pyc = archive / "logs" / "x.pyc"
    pyc.parent.mkdir(exist_ok=True)
    pyc.write_bytes(b"cache")
    keep_report = archive / "00-summary.md"

    close_archive.assert_inside(archive, archive)
    close_archive.assert_inside(archive, keep_report)
    with pytest.raises(ValueError, match="outside archive"):
        close_archive.assert_inside(archive, tmp_path / "outside")

    targets = close_archive.list_prune_targets(archive)

    assert nested_parent in targets
    assert nested_git not in targets
    assert archive / "logs" in targets
    assert nested_cache not in targets
    assert pyc not in targets
    assert keep_report not in targets
    assert close_archive.list_prune_targets(tmp_path / "missing") == []


def test_file_and_markdown_helpers(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    source = repo / "source"
    source.mkdir()
    sample = source / "sample.md"
    sample.write_text(
        "---\ntitle: 'Meta Title'\n---\n"
        "# Heading Title\n\n"
        "First paragraph line.\n"
        "Second line.\n\n"
        "## Detail\n"
        "### More\n"
        "- Bullet A\n"
        "* Bullet B\n"
        "1. Bullet C\n",
        encoding="utf-8",
    )
    (source / "nested").mkdir()
    (source / "nested" / "b.txt").write_text("b", encoding="utf-8")

    assert close_archive.read_sample(source / "missing.md") == ""
    assert close_archive.read_sample(sample, max_chars=5) == "---\nt"
    assert close_archive.collect_files(source, limit=1) == [source / "nested" / "b.txt"]
    assert close_archive.collect_files(source / "missing") == []
    assert close_archive.resolve_repo_path(repo, "rag/a.md") == repo / "rag" / "a.md"
    assert close_archive.resolve_repo_path(repo, str(sample.resolve())) == sample.resolve()
    assert close_archive.unique_paths([sample, sample.resolve()]) == [sample]
    assert close_archive.read_text_safe(source / "missing.md") == ""
    assert close_archive.read_text_safe(sample, max_chars=4) == "---\n"

    text = "See rag/a.md and [linked](rag/b.md) but not [outside](docs/c.md)"
    assert close_archive.extract_rag_references(text) == ["rag/a.md", "rag/b.md", "rag/b.md"]
    assert close_archive.first_heading("", "fallback") == "fallback"
    assert close_archive.strip_front_matter(sample.read_text(encoding="utf-8")).startswith("# Heading Title")
    assert close_archive.strip_front_matter("---\nno end") == "---\nno end"
    assert close_archive.metadata_title(sample.read_text(encoding="utf-8")) == "Meta Title"
    assert close_archive.metadata_title("# no front matter") == ""
    assert close_archive.first_paragraph(sample.read_text(encoding="utf-8"), max_chars=25) == "--- title: 'Meta Title' -"
    assert close_archive.markdown_headings(sample.read_text(encoding="utf-8")) == ["Detail", "More"]
    assert close_archive.markdown_bullets(sample.read_text(encoding="utf-8")) == ["Bullet A", "Bullet B", "Bullet C"]
    assert close_archive.has_mojibake("縺")
    assert not close_archive.has_mojibake("normal text")
    assert close_archive.bullet_paths(repo, []) == "- なし"
    assert close_archive.archive_title("issue-1", "improvement", "issue-1") == "improvement/issue-1 (issue-1)"
    assert close_archive.split_cli_paths(["", " 'rag/a.md' , \"rag/b.md\" "]) == ["rag/a.md", "rag/b.md"]
    assert close_archive.metadata_title("---\nsummary: no title\n---\n# Body") == ""
    assert close_archive.first_paragraph("# H\n\nBody after blank") == "Body after blank"
    assert close_archive.markdown_headings("\n".join(f"## H{i}" for i in range(10)), limit=2) == ["H0", "H1"]
    assert close_archive.markdown_bullets("\n".join(f"- B{i}" for i in range(20)), limit=3) == ["B0", "B1", "B2"]
    assert close_archive.format_rag_digest(
        [
            {
                "title": "Title",
                "path": "rag/a.md",
                "excerpt": "",
                "headings": [],
                "bullets": [],
                "has_mojibake": False,
            }
        ]
    ).startswith("### Title")


def test_rag_reference_and_candidate_discovery(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    rag = repo / "rag"
    github_rag = rag / "github-knowledge"
    vscode_rag = rag / "workspace-environment"
    github_rag.mkdir(parents=True)
    vscode_rag.mkdir(parents=True)
    (github_rag / "README.md").write_text("# ignored\n", encoding="utf-8")
    github_source = github_rag / "20260707000000_localty-system-robot.md"
    github_source.write_text("# Robot\n\nlocalty system robot issue data\n- one\n", encoding="utf-8")
    vscode_source = vscode_rag / "vscode-environment.md"
    vscode_source.write_text("# VSCode\n\nvscode environment terminal path\n", encoding="utf-8")
    source_work = repo / "work" / "github-knowledge-localty-system-robot-recent"
    source_work.mkdir(parents=True)
    (source_work / "note.md").write_text("ref rag/github-knowledge/20260707000000_localty-system-robot.md", encoding="utf-8")
    (source_work / "note.json").write_text('{"link":"rag/workspace-environment/vscode-environment.md"}', encoding="utf-8")
    (source_work / "skip.bin").write_text("rag/github-knowledge/missing.md", encoding="utf-8")

    refs = close_archive.collect_referenced_rag_sources(repo, source_work)
    assert refs == [vscode_source, github_source]
    assert close_archive.collect_referenced_rag_sources(repo, repo / "missing") == []
    assert close_archive.significant_tokens("github-knowledge-localty-system-robot-recent", "github") == [
        "localty",
        "system",
        "robot",
    ]
    assert close_archive.candidate_rag_files(repo, "github") == [github_source]
    assert close_archive.score_rag_candidate(github_source, repo, "github-knowledge-localty-system-robot-recent", "github") > 5
    assert close_archive.score_rag_candidate(vscode_source, repo, "vscode-environment", "vscode") > 5

    explicit_and_refs = close_archive.discover_rag_sources(
        repo,
        source_work,
        "github-knowledge-localty-system-robot-recent",
        "github",
        [f"{github_source}, {repo / 'missing.md'}"],
        auto_discovery=True,
    )
    assert explicit_and_refs == [github_source, vscode_source]
    explicit_only = close_archive.discover_rag_sources(
        repo,
        source_work,
        "github-knowledge-localty-system-robot-recent",
        "github",
        [str(github_source)],
        auto_discovery=False,
    )
    assert explicit_only == [github_source]


def test_rag_summary_formatting_and_report_builder(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    rag_source = repo / "rag" / "report.md"
    rag_source.parent.mkdir(parents=True)
    rag_source.write_text(
        "---\ntitle: Metadata Fallback\n---\n"
        "# RAG Main\n\n"
        "This source explains close archive behavior.\n\n"
        "## Section A\n"
        "- Keep report only\n"
        "- Remove source checkout\n"
        "縺\n",
        encoding="utf-8",
    )
    work = repo / "work" / "issue-9"
    (work / "process-report").mkdir(parents=True)
    (work / "process-report" / "knowledge-capture-report.md").write_text("Captured summary\n", encoding="utf-8")
    (work / "test-specifications").mkdir()
    (work / "test-specifications" / "spec.md").write_text("# spec\n", encoding="utf-8")
    (work / "test-evidence").mkdir()
    (work / "test-evidence" / "evidence.md").write_text("# evidence\n", encoding="utf-8")
    (work / "context").mkdir()
    (work / "context" / "manifest.json").write_text("{}\n", encoding="utf-8")

    summary = close_archive.summarize_rag_source(repo, rag_source)
    assert summary["title"] == "RAG Main"
    assert summary["excerpt"] == "This source explains close archive behavior."
    assert summary["headings"] == ["Section A"]
    assert summary["bullets"] == ["Keep report only", "Remove source checkout"]
    assert summary["has_mojibake"] is True
    assert close_archive.build_rag_context(repo, [rag_source, rag_source]) == [summary]

    assert "RAG source" in close_archive.format_rag_source_list([])
    assert "RAG source" in close_archive.format_rag_digest([])
    source_list = close_archive.format_rag_source_list([summary])
    digest = close_archive.format_rag_digest([summary])
    assert "`rag/report.md`: RAG Main" in source_list
    assert "This source explains close archive behavior." in digest
    assert "Keep report only" in digest

    reports = close_archive.build_reports(
        repo,
        "issue-9",
        "improvement",
        "issue-9",
        work,
        repo / "work" / "close" / "improvement" / "issue-9",
        [summary],
        auto_rag_enabled=False,
    )

    metadata = json.loads(reports["metadata.json"])
    assert "Captured summary" in reports["00-summary.md"]
    assert "rag/report.md" in reports["links.md"]
    assert metadata["rag_source_mode"] == "explicit-only"
    assert metadata["process_report_count"] == 1
    assert metadata["test_specification_count"] == 1
    assert metadata["test_evidence_count"] == 1
    assert metadata["rag_source_mojibake_warning_count"] == 1


def test_prepare_requires_rag_when_requested(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    result = close_archive.main(
        [
            "prepare",
            "--repo-root",
            str(repo),
            "--work-id",
            "issue-1",
            "--archive-dir",
            str(repo / "work" / "close" / "improvement" / "issue-1"),
            "--require-rag",
        ]
    )
    assert result == 1


def test_prepare_writes_rag_enriched_report_and_metadata(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    rag_dir = repo / "rag" / "github-knowledge"
    rag_dir.mkdir(parents=True)
    (rag_dir / "README.md").write_text("# README\n\n自動検出対象外です。\n", encoding="utf-8")
    source = rag_dir / "20260704000000_DEMO_localty-system-robot.md"
    source.write_text(
        "# localty-system-robot knowledge\n\n"
        "github-knowledge-localty-system-robot-recent の supervisor / worker 分離を記録します。\n\n"
        "## 要約\n\n"
        "- STOP behaviorを確認する。\n"
        "- communication lossを確認する。\n",
        encoding="utf-8",
    )

    result = close_archive.main(
        [
            "prepare",
            "--repo-root",
            str(repo),
            "--work-id",
            "github-knowledge-localty-system-robot-recent",
            "--category",
            "github",
            "--archive-id",
            "260704000000_TEST",
            "--require-rag",
        ]
    )
    assert result == 0

    archive = repo / "work" / "close" / "github" / "260704000000_TEST"
    summary = (archive / "00-summary.md").read_text(encoding="utf-8")
    metadata = json.loads((archive / "metadata.json").read_text(encoding="utf-8"))
    assert "RAGから抽出した要約" in summary
    assert "supervisor / worker" in summary
    assert metadata["rag_source_count"] == 1
    assert metadata["rag_sources"] == ["rag/github-knowledge/20260704000000_DEMO_localty-system-robot.md"]


def test_prune_requires_human_approval_for_execute(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    archive = repo / "work" / "close" / "improvement" / "issue-2"
    write_complete_archive(archive)
    extra = archive / "source"
    extra.mkdir()
    (extra / "temporary.txt").write_text("local only\n", encoding="utf-8")

    result = close_archive.main(
        [
            "prune",
            "--repo-root",
            str(repo),
            "--work-id",
            "issue-2",
            "--archive-dir",
            str(archive),
            "--execute",
        ]
    )
    assert result == 1
    assert extra.exists()


def test_prune_dry_run_keeps_targets(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    archive = repo / "work" / "close" / "improvement" / "issue-3"
    write_complete_archive(archive)
    extra = archive / "repository"
    extra.mkdir()

    result = close_archive.main(
        [
            "prune",
            "--repo-root",
            str(repo),
            "--work-id",
            "issue-3",
            "--archive-dir",
            str(archive),
        ]
    )
    assert result == 0
    assert extra.exists()


def test_audit_reports_readiness_and_prepare_no_auto_explicit_rag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(tmp_path)
    rag = repo / "rag" / "manual.md"
    rag.parent.mkdir(parents=True)
    rag.write_text("# Manual RAG\n\nmanual issue-4 source\n", encoding="utf-8")
    archive = repo / "work" / "close" / "improvement" / "issue-4"

    prepare_result = close_archive.main(
        [
            "prepare",
            "--repo-root",
            str(repo),
            "--work-id",
            "issue-4",
            "--archive-dir",
            str(archive),
            "--source-rag",
            "rag/manual.md",
            "--no-auto-rag",
        ]
    )
    assert prepare_result == 0
    prepared_stdout = json.loads(capsys.readouterr().out)
    assert prepared_stdout["status"] == "prepared"
    assert prepared_stdout["rag_sources"] == ["rag/manual.md"]

    audit_result = close_archive.main(
        [
            "audit",
            "--repo-root",
            str(repo),
            "--work-id",
            "issue-4",
            "--archive-dir",
            str(archive),
        ]
    )
    assert audit_result == 0
    audit_stdout = json.loads(capsys.readouterr().out)
    assert audit_stdout["report_only_ready"] is True
    assert audit_stdout["missing_report_files"] == []

    (archive / "tmp").mkdir()
    audit_with_extra = close_archive.run_audit(
        argparse.Namespace(
            command="audit",
            repo_root=str(repo),
            work_id="issue-4",
            issue="",
            category="auto",
            archive_id="",
            source_work_dir="",
            archive_dir=str(archive),
        )
    )
    assert audit_with_extra["report_only_ready"] is False
    assert audit_with_extra["prune_target_count"] == 1


def test_prune_execute_removes_targets_and_refuses_missing_reports(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    archive = repo / "work" / "close" / "improvement" / "issue-5"
    write_complete_archive(archive)
    extra_dir = archive / "source"
    extra_dir.mkdir()
    extra_file = archive / "debug.pyc"
    extra_file.write_bytes(b"cache")

    result = close_archive.run_prune(
        argparse.Namespace(
            command="prune",
            repo_root=str(repo),
            work_id="issue-5",
            issue="",
            category="auto",
            archive_id="",
            source_work_dir="",
            archive_dir=str(archive),
            execute=True,
            human_check="approved",
        )
    )

    assert result["status"] == "pruned"
    assert result["target_count"] == 2
    assert not extra_dir.exists()
    assert not extra_file.exists()
    assert len(result["removed"]) == 2

    incomplete = repo / "work" / "close" / "improvement" / "issue-6"
    incomplete.mkdir(parents=True)
    (incomplete / "extra.txt").write_text("remove me\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="report files are missing"):
        close_archive.run_prune(
            argparse.Namespace(
                command="prune",
                repo_root=str(repo),
                work_id="issue-6",
                issue="",
                category="auto",
                archive_id="",
                source_work_dir="",
                archive_dir=str(incomplete),
                execute=True,
                human_check="approved",
            )
        )


def test_prune_execute_skips_disappeared_target(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    archive = repo / "work" / "close" / "improvement" / "issue-5"
    write_complete_archive(archive)
    missing_target = archive / "source" / "repository"

    monkeypatch.setattr(close_archive, "list_prune_targets", lambda archive_dir: [missing_target])

    result = close_archive.run_prune(
        argparse.Namespace(
            command="prune",
            repo_root=str(repo),
            work_id="issue-5",
            issue="",
            category="auto",
            archive_id="",
            source_work_dir="",
            archive_dir=str(archive),
            execute=True,
            human_check="approved",
        )
    )

    assert result["status"] == "pruned"
    assert result["target_count"] == 1
    assert result["removed"] == []


def test_remove_helpers_retry_permission_errors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    target = tmp_path / "locked.txt"
    target.write_text("locked\n", encoding="utf-8")
    calls = {"unlink": 0, "chmod": []}
    original_unlink = Path.unlink

    def fake_unlink(path: Path, *args, **kwargs):
        if path == target and calls["unlink"] == 0:
            calls["unlink"] += 1
            raise PermissionError("locked")
        calls["unlink"] += 1
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fake_unlink)
    monkeypatch.setattr(close_archive.os, "chmod", lambda path, mode: calls["chmod"].append((Path(path), mode)))

    close_archive.remove_file(target)

    assert not target.exists()
    assert calls["unlink"] == 2
    assert calls["chmod"] == [(target, 0o700)]

    tree = tmp_path / "tree"
    tree.mkdir()
    failed = tree / "locked"
    failed.write_text("x", encoding="utf-8")
    rmtree_calls: list[Path] = []

    def fake_rmtree(path: Path, onerror):
        rmtree_calls.append(path)
        onerror(lambda failed_path: Path(failed_path).unlink(), str(failed), None)
        path.rmdir()

    monkeypatch.setattr(close_archive.shutil, "rmtree", fake_rmtree)
    monkeypatch.setattr(close_archive.os, "chmod", lambda path, mode: calls["chmod"].append((Path(path), mode)))

    close_archive.remove_tree(tree)

    assert rmtree_calls == [tree]
    assert not tree.exists()
