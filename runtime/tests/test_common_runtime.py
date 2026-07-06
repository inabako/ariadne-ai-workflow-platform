from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.common import (
    default_github_owner,
    ensure_work_tree,
    env_csv,
    env_value,
    extract_repository_config_from_files,
    extract_repository_config_from_text,
    find_repo_root,
    load_artifact_index,
    load_env,
    load_env_file,
    make_receipt_id,
    parse_env_line,
    read_json,
    relative_to_repo,
    requirement_files_from_artifact_index,
    resolve_github_repo,
    repository_to_clone_source,
    repository_to_github_slug,
    slugify,
    upsert_artifact,
    write_json,
    write_markdown_bom,
)


def test_slugify_and_relative_to_repo_are_stable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    nested = repo / "docs" / "Ariadne.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("# doc\n", encoding="utf-8")

    assert slugify(" Ariadne AI Workflow! ") == "Ariadne-AI-Workflow"
    assert slugify("   ") == "workflow"
    assert relative_to_repo(repo, nested) == "docs/Ariadne.md"


def test_ensure_work_tree_creates_standard_directories(tmp_path: Path) -> None:
    work_dir = ensure_work_tree(tmp_path, "issue-1")

    assert work_dir == tmp_path / "work" / "issue-1"
    for name in ["design-document", "process-report", "test-evidence", "test-specifications", "source", "context"]:
        assert (work_dir / name).is_dir()


def test_artifact_index_upsert_replaces_existing_artifact(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-1"
    index = load_artifact_index(work_dir, "demo", "docs-sync")

    upsert_artifact(index, {"id": "DOC-1", "path": "old.md", "status": "draft"})
    upsert_artifact(index, {"id": "DOC-1", "path": "new.md", "status": "approved"})

    assert index["project"] == "demo"
    assert index["workflow"] == "docs-sync"
    assert index["artifacts"] == [{"id": "DOC-1", "path": "new.md", "status": "approved"}]


def test_write_json_writes_utf8_json_with_parent_dirs(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "data.json"

    write_json(path, {"message": "日本語OK"})

    assert json.loads(path.read_text(encoding="utf-8"))["message"] == "日本語OK"


def test_common_root_receipt_json_and_markdown_edges(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (repo / ".git").mkdir()
    (repo / "work").mkdir()

    assert find_repo_root(nested) == repo
    assert find_repo_root(tmp_path / "outside").name == "ariadne-ai-workflow-platform"
    assert make_receipt_id("ai wf").startswith("AI-WF-")
    assert read_json(tmp_path / "missing.json", default={"ok": True}) == {"ok": True}

    outside = tmp_path / "outside.md"
    outside.write_text("# outside\n", encoding="utf-8")
    assert relative_to_repo(repo, outside) == str(outside.resolve())

    markdown = tmp_path / "docs" / "note.md"
    write_markdown_bom(markdown, "body\n\n")
    assert markdown.read_text(encoding="utf-8-sig") == "body\n"


def test_env_line_and_repository_slug_normalization() -> None:
    assert parse_env_line(" GITHUB_OWNER = 'inabako' ") == ("GITHUB_OWNER", "inabako")
    assert parse_env_line(" = value ") is None
    assert parse_env_line("# comment") is None
    assert env_value({"A": "", "B": "value"}, "A", "B", default="fallback") == "value"
    assert env_csv({"LABELS": "bug, docs , , workflow"}, "LABELS") == ["bug", "docs", "workflow"]
    assert repository_to_github_slug("[repo](https://github.com/inabako/ariadne-ai-workflow-platform.git)") == (
        "inabako/ariadne-ai-workflow-platform"
    )
    assert repository_to_github_slug("ariadne-ai-workflow-platform", "inabako") == "inabako/ariadne-ai-workflow-platform"
    assert repository_to_clone_source("ariadne-ai-workflow-platform", "inabako") == (
        "https://github.com/inabako/ariadne-ai-workflow-platform.git"
    )
    assert repository_to_clone_source("https://github.com/inabako/example.git") == "https://github.com/inabako/example.git"
    assert repository_to_github_slug("", "inabako") is None


def test_env_file_process_and_github_resolution_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert load_env_file(tmp_path / "missing.env") == {}

    env_path = tmp_path / ".env"
    env_path.write_text(
        "\ufeff# comment\n"
        "GITHUB_OWNER=inabako\n"
        "QUOTED=\"hello world\"\n"
        "EMPTY=\n"
        " = ignored\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PROCESS_ONLY", "yes")

    settings = load_env(tmp_path)
    file_only = load_env(tmp_path, include_process=False)

    assert settings["PROCESS_ONLY"] == "yes"
    assert settings["GITHUB_OWNER"] == "inabako"
    assert settings["QUOTED"] == "hello world"
    assert file_only["GITHUB_OWNER"] == "inabako"
    assert "PROCESS_ONLY" not in file_only
    assert default_github_owner(settings) == "inabako"
    assert resolve_github_repo(settings, "example") == "inabako/example"
    assert resolve_github_repo({}, "https://example.test/repo.git") == "https://example.test/repo.git"
    with pytest.raises(ValueError, match="GitHub repository is required"):
        resolve_github_repo({})


def test_extract_repository_config_from_markdown_text() -> None:
    text = """
| Field | Value |
| --- | --- |
| Repository | https://github.com/inabako/example.git |
| Target Branch | develop |
| Remote | upstream |
"""

    config = extract_repository_config_from_text(text)

    assert config == {
        "repository": "https://github.com/inabako/example.git",
        "target_branch": "develop",
        "remote": "upstream",
    }


def test_requirement_config_files_and_artifact_index_edges(tmp_path: Path) -> None:
    markdown = tmp_path / "req.md"
    markdown.write_text(
        "| A |\n"
        "| --- | --- |\n"
        "GitHub Owner: inabako\n"
        "GitHub Repo: owner/already-qualified\n"
        "Branch: main\n",
        encoding="utf-8",
    )

    config = extract_repository_config_from_files([tmp_path / "missing.md", markdown])

    assert config["repository"] == "owner/already-qualified"
    assert config["target_branch"] == "main"

    repo_root = tmp_path / "repo"
    work_dir = repo_root / "work" / "issue-1"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    write_json(
        context_dir / "artifact-index.json",
        {
            "artifacts": [
                {"type": "note", "path": "ignored.md"},
                {"type": "requirement"},
                {"type": "requirement", "path": "work/requirements/req.md"},
                {"type": "requirement", "path": str((tmp_path / "absolute.md").resolve())},
            ]
        },
    )

    paths = requirement_files_from_artifact_index(repo_root, work_dir)

    assert paths == [repo_root / "work/requirements/req.md", (tmp_path / "absolute.md").resolve()]
