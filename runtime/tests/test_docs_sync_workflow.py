from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.workflow import docs_sync


def make_work_dir(tmp_path: Path, work_id: str = "docs-develop") -> tuple[Path, Path]:
    repo_root = tmp_path
    work_dir = repo_root / "work" / work_id
    (work_dir / "context").mkdir(parents=True)
    return repo_root, work_dir


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def sample_analysis() -> dict[str, object]:
    return {
        "summary": "Docs drift summary.",
        "repository": "owner/repo",
        "target_branch": "develop",
        "source_commit": "abc123",
        "docs_root": "work/docs-develop/source/repository/docs",
        "guardrails": ["Docs-only change.", "Do not edit implementation."],
        "issue_recommendation": {
            "title": "docs: align runtime docs",
            "labels": ["documentation"],
            "acceptance_summary": "Docs match runtime behavior.",
        },
        "drift_items": [
            {
                "id": "DOCS-1",
                "title": "Runtime command drift",
                "severity": "medium",
                "status": "open",
                "area": "runtime",
                "implementation_evidence": [
                    {"path": "runtime/ctl.py", "symbol": "main", "reason": "CLI behavior changed."}
                ],
                "docs_evidence": [
                    {"path": "docs/reference/runtime.md", "reason": "Old command remains."}
                ],
                "expected_doc_updates": ["Update command spelling."],
                "acceptance_criteria": ["Docs mention current command."],
                "issue_body_note": "Keep this docs-only.",
            }
        ],
        "open_questions": [{"id": "Q-1", "question": "Any STOP behavior docs?", "blocks": True}],
    }


def test_docs_sync_build_parser_and_name_helpers() -> None:
    parser = docs_sync.build_parser()

    assert parser.parse_args(["init", "--repository", "owner/repo", "--target-branch", "feature/a"]).command == "init"
    assert parser.parse_args(["analysis-template", "--work-id", "docs-develop"]).command == "analysis-template"
    assert parser.parse_args(["issue-body", "--work-id", "docs-develop"]).command == "issue-body"
    assert docs_sync.branch_to_work_id("feature/docs update") == "feature-docs-update"
    assert docs_sync.repository_name("https://github.com/owner/Repo.Name.git") == "Repo.Name"
    assert docs_sync.repository_name("C:/src/My Repo.git") == "My-Repo"


def test_register_docs_sync_contexts_registers_only_existing_contexts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(work_dir / "context" / "agent-context.json", {})
    write_json(work_dir / "context" / "scm-state.json", {})
    calls: list[dict[str, object]] = []

    def fake_register_context(repo_root_arg, work_dir_arg, **kwargs):
        calls.append({"repo_root": repo_root_arg, "work_dir": work_dir_arg, **kwargs})

    monkeypatch.setattr(docs_sync, "register_context", fake_register_context)

    docs_sync.register_docs_sync_contexts(repo_root, work_dir, work_dir.name)

    assert [call["context_type"] for call in calls] == ["agent-context", "scm-state"]
    assert all(call["owner"] == "workflow" for call in calls)


def test_init_work_creates_contexts_and_rejects_unapproved_reuse(tmp_path: Path) -> None:
    result = docs_sync.init_work(
        argparse.Namespace(
            command="init",
            repository="owner/repo",
            target_branch="feature/docs",
            work_id="docs-feature",
            base_work_id="base-work",
            reuse_existing=False,
            intent_summary="Sync docs intentionally.",
            repo_root=str(tmp_path),
        )
    )
    work_dir = tmp_path / "work" / "docs-feature"
    agent_context = json.loads((work_dir / "context" / "agent-context.json").read_text(encoding="utf-8-sig"))
    manifest = json.loads((work_dir / "context" / "context-manifest.json").read_text(encoding="utf-8-sig"))

    assert result["base_work_id"] == "base-work"
    assert agent_context["intent"]["summary"] == "Sync docs intentionally."
    assert {"agent-context", "artifact-index"} <= {item["type"] for item in manifest["contexts"]}

    with pytest.raises(FileExistsError, match="Work directory already exists"):
        docs_sync.init_work(
            argparse.Namespace(
                command="init",
                repository="owner/repo",
                target_branch="feature/docs",
                work_id="docs-feature",
                base_work_id="",
                reuse_existing=False,
                intent_summary="",
                repo_root=str(tmp_path),
            )
        )


def test_default_analysis_uses_scm_state_and_fallback_docs_root(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(work_dir / "context" / "agent-context.json", {"project": {"repository": "owner/context-repo"}})
    write_json(
        work_dir / "context" / "scm-state.json",
        {
            "repository": "owner/scm-repo",
            "target_branch": "main",
            "current_commit": "abc123",
            "source_dir": str(repo_root / "source-checkout"),
        },
    )

    analysis = docs_sync.default_analysis(work_dir, repo_root)

    assert analysis["repository"] == "owner/scm-repo"
    assert analysis["target_branch"] == "main"
    assert analysis["docs_root"] == "source-checkout/docs"
    assert analysis["guardrails"][0] == "Docs-only change."


def test_require_docs_sync_scm_state_covers_manifest_fallback_allowed_and_error(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    manifest_path = work_dir / "context" / "context-manifest.json"
    scm_path = work_dir / "context" / "scm-state.json"
    write_json(
        manifest_path,
        {
            "contexts": [
                {
                    "type": "scm-state",
                    "path": "work/docs-develop/context/scm-state.json",
                }
            ]
        },
    )

    manifest_gate = docs_sync.require_docs_sync_scm_state(repo_root, work_dir, allow_missing=False)
    assert manifest_gate["mode"] == "manifest"

    manifest_path.unlink()
    write_json(scm_path, {"repository": "owner/repo"})
    fallback_gate = docs_sync.require_docs_sync_scm_state(repo_root, work_dir, allow_missing=False)
    assert fallback_gate["mode"] == "fallback-registered"

    scm_path.unlink()
    manifest_path.unlink()
    allowed_gate = docs_sync.require_docs_sync_scm_state(repo_root, work_dir, allow_missing=True)
    assert allowed_gate["status"] == "allowed-missing"

    with pytest.raises(RuntimeError, match="docs-sync analysis requires scm-state"):
        docs_sync.require_docs_sync_scm_state(repo_root, work_dir, allow_missing=False)


def test_create_analysis_template_with_allow_missing_and_explicit_output(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    write_json(work_dir / "context" / "agent-context.json", {"project": {"name": "repo", "repository": "owner/repo"}})
    output = tmp_path / "analysis.json"

    result = docs_sync.create_analysis_template(
        argparse.Namespace(
            command="analysis-template",
            work_id=work_dir.name,
            analysis_path=str(output),
            repo_root=str(repo_root),
            allow_missing_scm_state=True,
        )
    )

    assert result["context_gate"]["status"] == "allowed-missing"
    assert result["analysis_path"] == "analysis.json"
    assert output.exists()


def test_create_analysis_template_reports_missing_work_dir(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        docs_sync.create_analysis_template(
            argparse.Namespace(
                command="analysis-template",
                work_id="missing",
                analysis_path="",
                repo_root=str(tmp_path),
                allow_missing_scm_state=True,
            )
        )


def test_markdown_helpers_and_issue_body_render_full_and_empty_sections() -> None:
    full = docs_sync.build_issue_body(sample_analysis())
    no_note = sample_analysis()
    no_note["drift_items"][0].pop("issue_body_note")
    no_note_body = docs_sync.build_issue_body(no_note)
    empty = docs_sync.build_issue_body({"summary": "No drift yet.", "drift_items": [], "open_questions": []})

    assert docs_sync.markdown_list([]) == "- None"
    assert docs_sync.evidence_lines([]) == "- None"
    assert "runtime/ctl.py" in docs_sync.evidence_lines(sample_analysis()["drift_items"][0]["implementation_evidence"])
    assert "DOCS-1" in full
    assert "Keep this docs-only." in full
    assert "Keep this docs-only." not in no_note_body
    assert "Q-1" in full
    assert "No drift items recorded" in empty
    assert "## Acceptance Summary" in empty


def test_create_issue_body_writes_markdown_and_registers_artifact(tmp_path: Path) -> None:
    repo_root, work_dir = make_work_dir(tmp_path)
    analysis_path = work_dir / "context" / "docs-drift-analysis.json"
    output_path = tmp_path / "issue-body.md"
    write_json(work_dir / "context" / "agent-context.json", {"project": {"name": "repo"}})
    write_json(analysis_path, sample_analysis())

    result = docs_sync.create_issue_body(
        argparse.Namespace(
            command="issue-body",
            work_id=work_dir.name,
            analysis_path="",
            output=str(output_path),
            repo_root=str(repo_root),
        )
    )

    assert result["drift_item_count"] == 1
    assert result["recommended_title"] == "docs: align runtime docs"
    assert result["issue_body"] == "issue-body.md"
    assert "Docs drift summary." in output_path.read_text(encoding="utf-8-sig")
    manifest = json.loads((work_dir / "context" / "context-manifest.json").read_text(encoding="utf-8-sig"))
    assert "docs-drift-analysis" in {item["type"] for item in manifest["contexts"]}


def test_create_issue_body_reports_missing_work_and_analysis(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        docs_sync.create_issue_body(
            argparse.Namespace(command="issue-body", work_id="missing", analysis_path="", output="", repo_root=str(tmp_path))
        )

    _, work_dir = make_work_dir(tmp_path)
    with pytest.raises(FileNotFoundError, match="Docs drift analysis does not exist"):
        docs_sync.create_issue_body(
            argparse.Namespace(command="issue-body", work_id=work_dir.name, analysis_path="", output="", repo_root=str(tmp_path))
        )


def test_run_dispatches_and_main_prints_json(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(docs_sync, "init_work", lambda args: {"command": "init"})
    monkeypatch.setattr(docs_sync, "create_analysis_template", lambda args: {"command": "analysis-template"})
    monkeypatch.setattr(docs_sync, "create_issue_body", lambda args: {"command": "issue-body"})

    assert docs_sync.run(argparse.Namespace(command="init")) == {"command": "init"}
    assert docs_sync.run(argparse.Namespace(command="analysis-template")) == {"command": "analysis-template"}
    assert docs_sync.run(argparse.Namespace(command="issue-body")) == {"command": "issue-body"}
    with pytest.raises(ValueError, match="Unsupported command"):
        docs_sync.run(argparse.Namespace(command="unknown"))

    namespace = runpy.run_path(str(Path(docs_sync.__file__)))
    assert namespace["build_parser"]

    code = docs_sync.main(["analysis-template", "--work-id", "docs-develop"])
    captured = capsys.readouterr()

    assert code == 0
    assert '"command": "analysis-template"' in captured.out
