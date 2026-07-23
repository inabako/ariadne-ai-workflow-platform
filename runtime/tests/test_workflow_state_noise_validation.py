from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.workflow import noise_reduction, validate_output_language, validate_vscode_workspace, workflow_state


def test_workflow_state_update_writes_state_and_history(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-1"

    first = workflow_state.update_state(
        work_dir,
        workflow="docs-sync",
        work_id="issue-1",
        phase="analysis",
        status="in-progress",
        artifacts={"analysis": "work/issue-1/process-report/analysis.md"},
    )
    second = workflow_state.update_state(
        work_dir,
        workflow="docs-sync",
        work_id="issue-1",
        phase="review",
        status="review-ready",
    )

    assert first["artifacts"]["analysis"].endswith("analysis.md")
    assert second["phase"] == "review"
    assert second["status"] == "review-ready"
    assert second["history"]
    assert (work_dir / "context" / "workflow-state.json").exists()


def test_defensive_specimen_workflow_state_does_not_record_blank_previous_state(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-blank"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    (context_dir / "workflow-state.json").write_text(json.dumps({"phase": "", "status": "", "history": []}), encoding="utf-8")

    state = workflow_state.update_state(
        work_dir,
        workflow="docs-sync",
        work_id="issue-blank",
        phase="analysis",
        status="in-progress",
    )

    assert state["history"] == []


def test_workflow_state_rejects_invalid_status(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid workflow status"):
        workflow_state.update_state(
            tmp_path,
            workflow="docs-sync",
            work_id="issue-1",
            phase="analysis",
            status="waiting",
        )


def test_workflow_state_gate_restart_uses_ctl_command(tmp_path: Path) -> None:
    state = workflow_state.update_state(
        tmp_path / "work" / "issue-ctl",
        workflow="docs-sync",
        work_id="issue-ctl",
        phase="review",
        status="blocked",
    )

    repair_command = state["gate_restart"]["repair_command"]
    assert "runtime/ctl/ctl.py --repo-root . workflow state set" in repair_command
    assert "runtime/workflow/workflow_state.py" not in repair_command


def test_workflow_state_run_show_reports_missing_state(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    work_dir = repo / "work" / "issue-1"
    (repo / ".git").mkdir(parents=True)
    work_dir.mkdir(parents=True)
    args = argparse.Namespace(repo_root=str(repo), work_dir="work/issue-1")

    result = workflow_state.run_show(args)

    assert result["status"] == "missing"
    assert result["state_path"] == "work/issue-1/context/workflow-state.json"
    assert result["state"] == {}


def test_workflow_state_run_set_updates_relative_work_dir(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work" / "issue-1").mkdir(parents=True)
    args = argparse.Namespace(
        repo_root=str(repo),
        work_dir="work/issue-1",
        workflow="docs-sync",
        work_id="issue-1",
        phase="review",
        status="review-ready",
        blocking_reason="",
        next_human_action="確認してください",
    )

    result = workflow_state.run_set(args)

    assert result["status"] == "updated"
    assert result["state_path"] == "work/issue-1/context/workflow-state.json"
    assert result["state"]["next_human_action"] == "確認してください"


def test_workflow_state_main_show_prints_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = tmp_path / "repo"
    work_dir = repo / "work" / "issue-1"
    (repo / ".git").mkdir(parents=True)
    (work_dir / "context").mkdir(parents=True)
    (work_dir / "context" / "workflow-state.json").write_text(
        json.dumps({"status": "in-progress"}),
        encoding="utf-8",
    )

    code = workflow_state.main(["--repo-root", str(repo), "--work-dir", "work/issue-1", "show"])

    captured = capsys.readouterr()
    assert code == 0
    assert '"status": "ok"' in captured.out
    assert '"in-progress"' in captured.out

    namespace = runpy.run_path(str(Path(workflow_state.__file__)))
    assert namespace["build_parser"]


def test_noise_reduction_blocks_when_critical_items_are_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    draft = repo / "work" / "requirements" / "draft" / "draft.md"
    draft.parent.mkdir(parents=True)
    draft.write_text("新しい仕組みをいい感じに作る。TODO: SYS_GATE の意味確認。\n", encoding="utf-8")
    args = argparse.Namespace(repo_root=str(repo), draft=str(draft), output_dir="work/noise-output")

    result = noise_reduction.run(args)

    assert result["status"] == "blocked"
    assert result["readiness"] == "BLOCK"
    output_dir = repo / "work" / "noise-output"
    assert (output_dir / "unknown-words-report.md").exists()
    assert (output_dir / "human-interview-sheet.md").exists()
    assert (output_dir / "context" / "workflow-state.json").exists()


def test_noise_reduction_can_reach_warning_when_only_unknown_terms_remain(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    draft = repo / "draft.md"
    draft.write_text(
        "Repository: inabako/example\n"
        "Target branch: develop\n"
        "安全とsafetyを確認する。\n"
        "非常停止stopを定義する。\n"
        "通信断communication lossを扱う。\n"
        "SYS_GATE は要確認。\n",
        encoding="utf-8",
    )

    reports, summary = noise_reduction.build_reports(repo, draft, repo / "out")

    assert summary["readiness"] == "WARNING"
    assert "SYS_GATE" in reports["unknown-words-report.md"]
    assert "Requirement Review Draft May Start | yes" in reports["readiness-report.md"]


def test_noise_reduction_passes_and_uses_default_output_dir(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    draft = repo / "work" / "requirements" / "draft" / "clean.md"
    draft.parent.mkdir(parents=True)
    draft.write_text(
        "repository: inabako/example\n"
        "target branch: develop\n"
        "safety requirements are defined.\n"
        "stop behavior is defined.\n"
        "communication loss behavior is defined.\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(repo_root=str(repo), draft="work/requirements/draft/clean.md", output_dir="")

    result = noise_reduction.run(args)

    output_dir = draft.parent / "clean-noise-reduction"
    readiness = (output_dir / "readiness-report.md").read_text(encoding="utf-8")
    assert result["status"] == "ready"
    assert result["readiness"] == "PASS"
    assert output_dir.exists()
    assert "Status | PASS" in readiness
    assert "Requirement Review Draft May Start | yes" in readiness


def test_noise_reduction_helpers_cover_duplicate_unknown_and_missing_draft(tmp_path: Path) -> None:
    unknowns = noise_reduction.unknown_terms("SYS_GATE SYS_GATE\nTODO: SYS_GATE\n")

    assert [item[1] for item in unknowns].count("SYS_GATE") == 2
    assert noise_reduction.determine_readiness([], []) == "PASS"
    with pytest.raises(FileNotFoundError, match="Draft not found"):
        noise_reduction.resolve_draft(tmp_path, "missing.md")


def test_noise_reduction_parser_main_and_script_load_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parser = noise_reduction.build_parser()
    parsed = parser.parse_args(
        [
            "run",
            "--draft",
            "draft.md",
            "--output-dir",
            "out",
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert parsed.draft == "draft.md"
    assert parsed.output_dir == "out"
    assert parsed.repo_root == str(tmp_path)

    monkeypatch.setattr(noise_reduction, "run", lambda args: {"status": "ready", "readiness": "PASS"})
    assert noise_reduction.main(["run", "--draft", "draft.md", "--repo-root", str(tmp_path)]) == 0
    assert '"status": "ready"' in capsys.readouterr().out

    def raise_error(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(noise_reduction, "run", raise_error)
    assert noise_reduction.main(["run", "--draft", "draft.md", "--repo-root", str(tmp_path)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(noise_reduction.__file__)))
    assert namespace["build_parser"]


def test_validate_output_language_detects_english_dominant_markdown(tmp_path: Path) -> None:
    path = tmp_path / "report.md"
    path.write_text(
        "This document explains architecture decisions, implementation details, testing strategy, "
        "deployment operations, troubleshooting procedure, runtime behavior, validation evidence, "
        "maintenance policy, monitoring design, and rollback process.\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(min_english_words=10, min_japanese_chars=20, english_ratio_threshold=0.62)

    finding = validate_output_language.analyze(path, args)

    assert finding is not None
    assert finding.english_words >= 10


def test_validate_output_language_ignores_code_blocks_and_allowed_terms(tmp_path: Path) -> None:
    path = tmp_path / "report.md"
    path.write_text(
        "これは日本語の説明です。workflowとruntimeとGitHubは許可語として扱います。\n\n"
        "```text\n"
        "This huge English code block should not dominate prose language detection.\n"
        "```\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(min_english_words=5, min_japanese_chars=5, english_ratio_threshold=0.62)

    assert validate_output_language.analyze(path, args) is None

    mixed = tmp_path / "mixed.md"
    mixed.write_text(
        "これは十分な日本語本文です。安全確認と運用確認を行います。" * 4
        + " architecture implementation deployment troubleshooting observability rollback monitoring validation",
        encoding="utf-8",
    )
    assert validate_output_language.analyze(
        mixed,
        argparse.Namespace(min_english_words=5, min_japanese_chars=10, english_ratio_threshold=0.9),
    ) is None


def test_validate_output_language_iter_markdown_skips_missing_non_md_and_excluded_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    rag_chunks = repo / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "chunks"
    work_source = repo / "work" / "issue-1" / "source"
    docs.mkdir(parents=True)
    rag_chunks.mkdir(parents=True)
    work_source.mkdir(parents=True)
    included = docs / "guide.md"
    excluded_rag = rag_chunks / "chunk.md"
    excluded_work = work_source / "README.md"
    non_md = docs / "note.txt"
    included.write_text("# ガイド\n", encoding="utf-8")
    excluded_rag.write_text("# chunk\n", encoding="utf-8")
    excluded_work.write_text("# source\n", encoding="utf-8")
    non_md.write_text("not markdown\n", encoding="utf-8")

    results = validate_output_language.iter_markdown(
        ["docs", "work", "missing", str(non_md)],
        repo,
        validate_output_language.DEFAULT_EXCLUDES,
    )

    assert results == [included.resolve()]
    assert validate_output_language.iter_markdown(["docs"], repo, ["docs/guide.md"]) == []
    assert validate_output_language.is_excluded(tmp_path / "outside.md", repo, ["outside.md"])
    assert validate_output_language.analyze(docs, argparse.Namespace(min_english_words=1, min_japanese_chars=1, english_ratio_threshold=0.5)) is None


def test_validate_output_language_strip_non_prose_removes_frontmatter_urls_tables_and_inline_code() -> None:
    text = "\n".join(
        [
            "---",
            "title: English metadata should be ignored",
            "---",
            "これは本文です。",
            "`inline English code`",
            "```text",
            "large English code block",
            "```",
            "https://example.com/english/path",
            "| --- | --- |",
        ]
    )

    prose = validate_output_language.strip_non_prose(text)

    assert "English metadata" not in prose
    assert "inline English code" not in prose
    assert "large English code block" not in prose
    assert "https://example.com" not in prose
    assert "これは本文です" in prose


def test_validate_output_language_main_returns_zero_when_only_warnings(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "english.md").write_text(
        "Architecture decisions implementation details testing strategy deployment operations "
        "troubleshooting procedure runtime behavior validation evidence maintenance policy monitoring design.\n",
        encoding="utf-8",
    )

    code = validate_output_language.main(
        [
            "--repo-root",
            str(repo),
            "--paths",
            "docs",
            "--min-english-words",
            "5",
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    assert "found likely English-dominant" in captured.out
    assert "english.md" in captured.out


def test_validate_output_language_main_fails_on_violation(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "english.md").write_text(
        "Architecture decisions implementation details testing strategy deployment operations "
        "troubleshooting procedure runtime behavior validation evidence maintenance policy monitoring design.\n",
        encoding="utf-8",
    )

    code = validate_output_language.main(
        [
            "--repo-root",
            str(repo),
            "--paths",
            "docs",
            "--min-english-words",
            "5",
            "--fail-on-violation",
        ]
    )

    captured = capsys.readouterr()
    assert code == 1
    assert "english_ratio=" in captured.out

    json_code = validate_output_language.main(
        [
            "--repo-root",
            str(repo),
            "--paths",
            "docs",
            "--min-english-words",
            "5",
            "--fail-on-violation",
            "--json",
        ]
    )
    json_output = json.loads(capsys.readouterr().out)
    assert json_code == 1
    assert json_output["gate_restart"]["gate"] == "output-language-gate"
    assert json_output["gate_restart"]["next_on_fail"] == "stay-at-gate"


def test_validate_output_language_main_prints_absolute_external_path_and_script_load(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    external = tmp_path / "external.md"
    external.write_text(
        "Architecture decisions implementation details testing strategy deployment operations "
        "troubleshooting procedure runtime behavior validation evidence maintenance policy monitoring design.\n",
        encoding="utf-8",
    )

    code = validate_output_language.main(
        [
            "--repo-root",
            str(repo),
            "--paths",
            str(external),
            "--min-english-words",
            "5",
            "--fail-on-violation",
        ]
    )

    captured = capsys.readouterr()
    assert code == 1
    assert str(external) in captured.out

    namespace = runpy.run_path(str(Path(validate_output_language.__file__)))
    assert namespace["build_parser"]


def test_validate_output_language_main_reports_ok_for_japanese_dominant(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "guide.md").write_text("これは日本語中心の説明です。workflow runtime GitHub は許可語です。\n", encoding="utf-8")

    code = validate_output_language.main(["--repo-root", str(repo), "--paths", "docs"])

    captured = capsys.readouterr()
    assert code == 0
    assert "Output language check OK" in captured.out


def test_validate_vscode_workspace_accepts_utf8_sig_json(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    settings = workspace / ".vscode" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text('\ufeff{"terminal.integrated.defaultProfile.windows": "PowerShell"}', encoding="utf-8")

    assert validate_vscode_workspace.main(["--workspace", str(workspace), ".vscode/settings.json"]) == 0


def test_validate_vscode_workspace_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / ".vscode" / "settings.json"
    path.parent.mkdir(parents=True)
    path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        validate_vscode_workspace.validate_file(path)
