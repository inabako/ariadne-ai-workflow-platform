from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.common import registry_store
from runtime.observability.logger import RuntimeEventLogger
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


def test_create_feedback_includes_runtime_log_analysis_for_trace(tmp_path: Path) -> None:
    event_logger = RuntimeEventLogger(repo_root=tmp_path, component="ctl", trace_id="trace123")
    event_logger.emit(
        "runtime_command_started",
        command="help search",
        input={"json": False, "repo_root": str(tmp_path), "work_id": ""},
        output={},
    )
    event_logger.emit(
        "runtime_command_completed",
        command="help search",
        input={"json": False, "repo_root": str(tmp_path), "work_id": ""},
        output={
            "status": "blocked",
            "exit_code": 2,
            "duration_ms": 29,
            "output_bytes": 562,
            "reason": "required_argument_missing",
        },
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        target_workflow="/self-improvement",
        reporter="Human",
        situation="runtime observation needs feedback context",
        friction="runtime log analysis was not included in feedback reports",
        impact="feedback review needed manual log inspection",
        proposed_improvement="include runtime log analysis in feedback reports",
        evidence=["logs/runtime/runtime-events.log"],
        priority="High",
        category="Observability",
        runtime_trace_id="trace123",
        runtime_log="",
        output="",
    )

    result = self_improvement.run_create_feedback(args)

    text = (tmp_path / result["feedback"]).read_text(encoding="utf-8-sig")
    assert "## Runtime Observation" in text
    assert "Trace ID: `trace123`" in text
    assert "Events: 2 / 2" in text
    assert "Commands: `help search`" in text
    assert "Statuses: blocked: 1" in text
    assert "Reasons: required_argument_missing: 1" in text
    assert "## Runtime Log Analysis" in text
    assert "Outcome: `blocked`" in text
    assert "seq=00002 event=runtime_command_completed command=help search status=blocked" in text


def test_init_feedback_preserves_existing_readme_and_template_reader(tmp_path: Path) -> None:
    readme = tmp_path / "work" / "feedback" / "README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text("# Existing\n", encoding="utf-8")

    result = self_improvement.run_init_feedback(argparse.Namespace(repo_root=str(tmp_path)))

    assert result == {"feedback_readme": "work/feedback/README.md"}
    assert readme.read_text(encoding="utf-8") == "# Existing\n"

    template = tmp_path / self_improvement.TEMPLATE_DIR / "sample.md"
    template.parent.mkdir(parents=True)
    template.write_text("# Template\n", encoding="utf-8")

    assert self_improvement.template_path(tmp_path, "sample.md") == template
    assert self_improvement.read_template(tmp_path, "sample.md") == "# Template\n"

    with pytest.raises(FileNotFoundError, match="Template does not exist"):
        self_improvement.read_template(tmp_path, "missing.md")


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


def test_review_feedback_requires_existing_feedback(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Feedback report does not exist"):
        self_improvement.run_review_feedback(
            argparse.Namespace(
                repo_root=str(tmp_path),
                feedback="work/feedback/missing.md",
                decision="accepted",
                reviewer="Human",
                reason="OK",
                next_action="Issue",
            )
        )


def test_feedback_decision_accepts_human_check_or_defaults_to_proposed() -> None:
    assert self_improvement.feedback_decision({"Human Check": "- Decision: rejected"}) == "rejected"
    assert self_improvement.feedback_decision({"Human Check": "- Decision: deferred"}) == "deferred"
    assert self_improvement.feedback_decision({}) == "proposed"


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


def test_issue_body_requires_existing_feedback(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Feedback report does not exist"):
        self_improvement.run_issue_body(
            argparse.Namespace(
                repo_root=str(tmp_path),
                feedback="work/feedback/missing.md",
                output="",
                allow_unaccepted=False,
            )
        )


def test_issue_body_can_render_unaccepted_feedback_to_explicit_output(tmp_path: Path) -> None:
    feedback = tmp_path / "work" / "feedback" / "sample.md"
    feedback.parent.mkdir(parents=True)
    feedback.write_text(
        """# Workflow Feedback

## Proposed Improvement

Keep draft feedback visible

## Review Status

Proposed
""",
        encoding="utf-8",
    )

    result = self_improvement.run_issue_body(
        argparse.Namespace(
            repo_root=str(tmp_path),
            feedback="work/feedback/sample.md",
            output="work/feedback/custom-issue.md",
            allow_unaccepted=True,
        )
    )

    assert result["issue_body"] == "work/feedback/custom-issue.md"
    assert result["decision"] == "proposed"
    assert "Keep-draft-feedback-visible" in result["recommended_title"]


def test_evidence_scaffold_registers_artifact_index(tmp_path: Path) -> None:
    result = self_improvement.run_evidence_scaffold(argparse.Namespace(repo_root=str(tmp_path), work_id="issue-42"))

    artifact_index = tmp_path / result["artifact_index"]
    manifest = tmp_path / "work" / "issue-42" / "context" / "context-manifest.json"
    data = json.loads(artifact_index.read_text(encoding="utf-8"))
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))

    assert "SELF-IMPROVEMENT-PROCESS" in {item["id"] for item in data["artifacts"]}
    assert "artifact-index" in {item["type"] for item in manifest_data["contexts"]}


def test_evidence_scaffold_updates_existing_artifact_index_without_rewriting_readmes(tmp_path: Path) -> None:
    args = argparse.Namespace(repo_root=str(tmp_path), work_id="issue-42")
    first = self_improvement.run_evidence_scaffold(args)
    process_readme = tmp_path / first["process_report"] / "README.md"
    evidence_readme = tmp_path / first["test_evidence"] / "README.md"
    process_readme.write_text("# Keep process note\n", encoding="utf-8")
    evidence_readme.write_text("# Keep evidence note\n", encoding="utf-8")

    second = self_improvement.run_evidence_scaffold(args)

    assert second["artifact_index"] == first["artifact_index"]
    assert process_readme.read_text(encoding="utf-8") == "# Keep process note\n"
    assert evidence_readme.read_text(encoding="utf-8") == "# Keep evidence note\n"
    artifact_index = json.loads((tmp_path / second["artifact_index"]).read_text(encoding="utf-8"))
    assert len(artifact_index["artifacts"]) == 2


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
    registry = registry_store.load_workflow_help(root)
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
