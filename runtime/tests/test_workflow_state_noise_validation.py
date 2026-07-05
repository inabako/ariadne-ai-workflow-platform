from __future__ import annotations

import argparse
import json
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


def test_workflow_state_rejects_invalid_status(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid workflow status"):
        workflow_state.update_state(
            tmp_path,
            workflow="docs-sync",
            work_id="issue-1",
            phase="analysis",
            status="waiting",
        )


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
