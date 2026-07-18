from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.workflow import vscode_environment


def namespace(**kwargs):
    return argparse.Namespace(**kwargs)


def test_vscode_environment_build_parser_parses_all_commands() -> None:
    parser = vscode_environment.build_parser()

    assert parser.parse_args(["init"]).command == "init"
    assert parser.parse_args(["requirements-template"]).command == "requirements-template"
    assert parser.parse_args(["validation-template", "--status", "conditional-pass"]).command == "validation-template"
    assert parser.parse_args(["draft-template"]).command == "draft-template"
    assert parser.parse_args(["open-questions"]).command == "open-questions"
    assert parser.parse_args(["rag-template", "--topic", "local env"]).command == "rag-template"


def test_vscode_environment_init_work_writes_state_and_runtime_context(tmp_path: Path) -> None:
    target = tmp_path / "target-workspace"
    target.mkdir()

    result = vscode_environment.init_work(
        namespace(
            work_id="vscode-env",
            target_dir=str(target),
            mode="target-workspace",
            repo_root=str(tmp_path),
            reuse_existing=False,
        )
    )

    base = tmp_path / "work" / "vscode-env"
    state = json.loads((base / "context" / "vscode-environment-state.json").read_text(encoding="utf-8-sig"))
    runtime_context = json.loads((base / "context" / "runtime-context.json").read_text(encoding="utf-8-sig"))
    manifest = json.loads((base / "context" / "context-manifest.json").read_text(encoding="utf-8-sig"))

    assert result["mode"] == "target-workspace"
    assert state["target_dir"] == str(target.resolve())
    assert runtime_context["tool_paths"] == ["runtime/tools"]
    assert runtime_context["encoding_contract"]["policy"] == "utf-8-first"
    assert runtime_context["encoding_contract"]["vscode_settings"]["files.encoding"] == "utf8"
    assert runtime_context["encoding_contract"]["vscode_settings"]["files.autoGuessEncoding"] is False
    assert runtime_context["encoding_contract"]["vscode_settings"]["terminal.integrated.env.windows"]["PYTHONUTF8"] == "1"
    assert runtime_context["encoding_contract"]["codex_config_note"]["standard_encoding_key_supported"] is False
    assert runtime_context["encoding_contract"]["codex_config_note"]["do_not_add_encoding_table_as_enforcement"] is True
    assert {entry["type"] for entry in manifest["contexts"]} >= {"vscode-environment-state", "runtime-context"}

    with pytest.raises(FileExistsError, match="Work directory already exists"):
        vscode_environment.init_work(
            namespace(
                work_id="vscode-env",
                target_dir="",
                mode="self-provision",
                repo_root=str(tmp_path),
                reuse_existing=False,
            )
        )


def test_vscode_environment_draft_template_and_discovery(tmp_path: Path) -> None:
    draft_dir = tmp_path / "work" / "requirements" / "devlop-edit-draft"
    result = vscode_environment.write_draft_template(namespace(draft_dir=str(draft_dir), repo_root=str(tmp_path)))
    second = vscode_environment.write_draft_template(namespace(draft_dir=str(draft_dir), repo_root=str(tmp_path)))
    (draft_dir / "README_custom.md").write_text("# custom\n", encoding="utf-8")
    (draft_dir / "notes.txt").write_text("legacy\n", encoding="utf-8")
    (draft_dir / "ignore.md").write_text("# ignore\n", encoding="utf-8")

    drafts = vscode_environment.discover_drafts(draft_dir)

    assert result["created"] is True
    assert second["created"] is False
    assert result["draft_path"].endswith("README.md")
    assert [path.name for path in drafts] == ["notes.txt", "README_custom.md"]
    assert "custom-design mode" in vscode_environment.draft_template_text()
    assert vscode_environment.discover_drafts(tmp_path / "missing-draft-dir") == []


def test_vscode_environment_open_questions_records_drafts(tmp_path: Path) -> None:
    draft_dir = tmp_path / "drafts"
    draft_dir.mkdir()
    (draft_dir / "README_terminal.md").write_text("# terminal\n", encoding="utf-8")
    (draft_dir / "legacy.txt").write_text("legacy\n", encoding="utf-8")

    result = vscode_environment.write_open_questions(
        namespace(work_id="vscode-env", draft_dir=str(draft_dir), repo_root=str(tmp_path))
    )

    open_questions = (tmp_path / result["open_questions_path"]).read_text(encoding="utf-8")
    state = json.loads((tmp_path / result["state_path"]).read_text(encoding="utf-8-sig"))

    assert "VSCODE-Q001" in open_questions
    assert result["draft_files"] == ["drafts/legacy.txt", "drafts/README_terminal.md"]
    assert state["status"] == "blocked"
    assert state["draft_files"] == result["draft_files"]


def test_vscode_environment_rag_filename_and_template(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vscode_environment, "random_token", lambda length=6: "ABC123")

    filename = vscode_environment.rag_filename("Local Env !!")
    text = vscode_environment.rag_template_text(
        namespace(
            repository="owner/repo",
            status="draft",
            target_workspace="C:/repo",
            mode="custom-design",
            work_id="vscode-env",
        ),
        "work/db/ariadne-knowledge-platform/rag/workspace-environment/source.md",
    )

    assert filename.endswith("_ABC123_local-env.md")
    assert "repository: owner/repo" in text
    assert "target_workspace: `C:/repo`" in text


def test_vscode_environment_write_rag_template_requires_repo_local_source_dir(tmp_path: Path) -> None:
    result = vscode_environment.write_rag_template(
        namespace(
            work_id="vscode-env",
            source_dir="work/db/ariadne-knowledge-platform/rag/workspace-environment",
            topic="Local Env",
            repository="owner/repo",
            target_workspace="",
            mode="self-provision",
            status="draft",
            repo_root=str(tmp_path),
        )
    )

    assert result["document_type"] == "workspace-environment-pattern"
    assert (tmp_path / result["path"]).exists()

    with pytest.raises(ValueError, match="must be inside repo root"):
        vscode_environment.write_rag_template(
            namespace(
                work_id="vscode-env",
                source_dir=str(tmp_path.parent / "outside-rag"),
                topic="Local Env",
                repository="owner/repo",
                target_workspace="",
                mode="self-provision",
                status="draft",
                repo_root=str(tmp_path),
            )
        )


def test_vscode_environment_requirements_and_validation_templates(tmp_path: Path) -> None:
    req_result = vscode_environment.write_requirements_template(
        namespace(work_id="vscode-env", mode="custom-design", repo_root=str(tmp_path))
    )
    second_req = vscode_environment.write_requirements_template(
        namespace(work_id="vscode-env", mode="custom-design", repo_root=str(tmp_path))
    )
    validation_result = vscode_environment.write_validation_template(
        namespace(work_id="vscode-env", mode="custom-design", status="conditional-pass", repo_root=str(tmp_path))
    )

    requirements = (tmp_path / req_result["path"]).read_text(encoding="utf-8")
    validation_json = json.loads((tmp_path / validation_result["json_path"]).read_text(encoding="utf-8-sig"))
    validation_md = (tmp_path / validation_result["markdown_path"]).read_text(encoding="utf-8")

    assert "custom-design" in requirements
    assert second_req["path"] == req_result["path"]
    assert "terminal.integrated.env.windows" in requirements
    assert "UTF-8 First / Mojibake Prevention" in requirements
    assert '"files.encoding": "utf8"' in requirements
    assert "独自の `[encoding]` table" in requirements
    assert "aiwfctl doctor --fail-on-warning" in requirements
    assert validation_json["status"] == "conditional-pass"
    assert any("UTF-8 First" in item for item in validation_json["missing_required_items"])
    assert "Workspace共有Artifact検証" in validation_md
    assert "- 必須tool一覧" in validation_md


def test_vscode_environment_validation_markdown_empty_lists() -> None:
    rendered = vscode_environment.validation_markdown(
        {
            "status": "pass",
            "created_at": "2026-07-06T00:00:00Z",
            "missing_required_items": [],
            "open_questions": [],
        }
    )

    assert rendered.count("- なし") == 2


def test_vscode_environment_main_dispatch_success_and_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = vscode_environment.main(["requirements-template", "--work-id", "vscode-env", "--repo-root", str(tmp_path)])
    captured = capsys.readouterr()

    assert code == 0
    assert '"path"' in captured.out

    (tmp_path / "work" / "vscode-env").mkdir(parents=True, exist_ok=True)
    code = vscode_environment.main(["init", "--work-id", "vscode-env", "--repo-root", str(tmp_path)])
    captured = capsys.readouterr()

    assert code == 1
    assert "Work directory already exists" in captured.err


def test_vscode_environment_main_dispatches_remaining_commands_and_script_load(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    commands = [
        ["validation-template", "--work-id", "vscode-validation", "--repo-root", str(tmp_path)],
        ["draft-template", "--draft-dir", "work/requirements/custom-draft", "--repo-root", str(tmp_path)],
        ["open-questions", "--work-id", "vscode-questions", "--repo-root", str(tmp_path)],
        ["rag-template", "--work-id", "vscode-rag", "--repo-root", str(tmp_path), "--topic", "Local Env"],
    ]

    for command in commands:
        assert vscode_environment.main(command) == 0
        assert "{" in capsys.readouterr().out

    namespace = runpy.run_path(str(Path(vscode_environment.__file__)))
    assert namespace["build_parser"]
