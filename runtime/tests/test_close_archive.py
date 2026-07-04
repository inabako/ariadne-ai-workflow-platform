from __future__ import annotations

import json
from pathlib import Path

from runtime.workflow import close_archive


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    return repo


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
    archive.mkdir(parents=True)
    for name in close_archive.REPORT_FILES:
        path = archive / name
        path.write_text("{}\n" if name == "metadata.json" else f"# {name}\n", encoding="utf-8")
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
    archive.mkdir(parents=True)
    for name in close_archive.REPORT_FILES:
        path = archive / name
        path.write_text("{}\n" if name == "metadata.json" else f"# {name}\n", encoding="utf-8")
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
