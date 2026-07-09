from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.workflow import self_improvement


def test_parser_and_branch_name() -> None:
    parser = self_improvement.build_parser()

    assert parser.parse_args(["init-feedback"]).command == "init-feedback"
    result = self_improvement.run_branch_name(argparse.Namespace(issue_number="42"))
    assert result["branch"] == "feature/issue-42"
    assert result["work_id"] == "issue-42"
    with pytest.raises(ValueError, match="numeric"):
        self_improvement.run_branch_name(argparse.Namespace(issue_number="abc"))


def test_init_and_create_feedback(tmp_path: Path) -> None:
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        target_workflow="/docs-sync",
        reporter="Human",
        situation="docs整備中",
        friction="参照docsが不明",
        impact="判断負荷が増えた",
        proposed_improvement="入口を足す",
        evidence=["docs/README.md"],
        priority="High",
        category="Docs",
        output="",
    )

    result = self_improvement.run_create_feedback(args)
    feedback = tmp_path / result["feedback"]
    readme = tmp_path / "work" / "feedback" / "README.md"

    assert readme.exists()
    assert feedback.exists()
    text = feedback.read_text(encoding="utf-8-sig")
    assert "参照docsが不明" in text
    assert "Proposed" in text
    assert "High" in text


def test_review_feedback_updates_status_and_human_check(tmp_path: Path) -> None:
    feedback = tmp_path / "work" / "feedback" / "sample.md"
    feedback.parent.mkdir(parents=True)
    feedback.write_text(
        "# Workflow Feedback\n\n## Review Status\n\nProposed\n\n## Human Check\n\n- Decision:\n",
        encoding="utf-8",
    )

    result = self_improvement.run_review_feedback(
        argparse.Namespace(
            repo_root=str(tmp_path),
            feedback="work/feedback/sample.md",
            decision="accepted",
            reviewer="Human",
            reason="改善価値がある",
            next_action="Issue化する",
        )
    )

    text = feedback.read_text(encoding="utf-8-sig")
    assert result["decision"] == "accepted"
    assert "Accepted" in text
    assert "Reviewer: Human" in text
    assert "改善価値がある" in text


def test_issue_body_requires_accepted_feedback_and_renders_fit_check(tmp_path: Path) -> None:
    feedback = tmp_path / "work" / "feedback" / "sample.md"
    feedback.parent.mkdir(parents=True)
    feedback.write_text(
        """# Workflow Feedback

## Target Workflow

/docs-sync

## Situation

docs整備中

## Friction

参照docsが不明

## Impact

判断負荷が増えた

## Proposed Improvement

docs入口を追加する

## Evidence

- docs/README.md

## Review Status

Proposed

## Priority

Medium

## Category

Docs
""",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="accepted"):
        self_improvement.run_issue_body(
            argparse.Namespace(repo_root=str(tmp_path), feedback="work/feedback/sample.md", output="", allow_unaccepted=False)
        )

    self_improvement.run_review_feedback(
        argparse.Namespace(
            repo_root=str(tmp_path),
            feedback="work/feedback/sample.md",
            decision="accepted",
            reviewer="Human",
            reason="OK",
            next_action="Issue化",
        )
    )
    result = self_improvement.run_issue_body(
        argparse.Namespace(repo_root=str(tmp_path), feedback="work/feedback/sample.md", output="", allow_unaccepted=False)
    )

    body = tmp_path / result["issue_body"]
    text = body.read_text(encoding="utf-8-sig")
    assert "Ariadne Fit Check" in text
    assert "docs入口を追加する" in text
    assert "work/feedback/sample.md" in text


def test_evidence_scaffold_registers_artifact_index(tmp_path: Path) -> None:
    result = self_improvement.run_evidence_scaffold(argparse.Namespace(repo_root=str(tmp_path), work_id="issue-42"))

    artifact_index = tmp_path / result["artifact_index"]
    manifest = tmp_path / "work" / "issue-42" / "context" / "context-manifest.json"
    data = json.loads(artifact_index.read_text(encoding="utf-8"))
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))

    assert "SELF-IMPROVEMENT-PROCESS" in {item["id"] for item in data["artifacts"]}
    assert "artifact-index" in {item["type"] for item in manifest_data["contexts"]}


def test_main_prints_json(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(self_improvement, "run_init_feedback", lambda args: {"feedback_readme": "work/feedback/README.md"})
    namespace = runpy.run_path(str(Path(self_improvement.__file__)))
    assert namespace["build_parser"]

    code = self_improvement.main(["init-feedback"])
    captured = capsys.readouterr()

    assert code == 0
    assert "feedback_readme" in captured.out


def test_workflow_skills_declare_feedback_output_contract() -> None:
    root = Path(__file__).resolve().parents[2]
    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    missing: list[str] = []

    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8-sig")
        if skill_file.parent.name == "self-improvement":
            required = [
                "work/feedback/",
                "Proposed",
                "通常workflow",
                "通常workflowの中から `/self-improvement` を自動実行しません",
            ]
        else:
            required = [
                "## Workflow Feedback Output",
                "work/feedback/",
                "Review Status",
                "Proposed",
                "Do not run `/self-improvement` automatically",
            ]
        for needle in required:
            if needle not in text:
                missing.append(f"{skill_file}: {needle}")

    assert not missing


def test_workflow_help_declares_feedback_capture_for_all_commands() -> None:
    root = Path(__file__).resolve().parents[2]
    registry = json.loads((root / "runtime" / "registries" / "workflow_help.json").read_text(encoding="utf-8-sig"))
    missing: list[str] = []

    for command in registry["commands"]:
        details = "\n".join(command.get("details", []))
        if "work/feedback/" not in details:
            missing.append(f"{command['command']}: work/feedback/")
        if "/self-improvement" not in details:
            missing.append(f"{command['command']}: /self-improvement")

    self_improvement_help = next(command for command in registry["commands"] if command["command"] == "/self-improvement")
    assert "docs/reference/workflow-feedback.md" in self_improvement_help["docs"]
    assert not missing
