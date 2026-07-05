from __future__ import annotations

import json
from pathlib import Path

from runtime.common import (
    ensure_work_tree,
    env_csv,
    env_value,
    extract_repository_config_from_text,
    load_artifact_index,
    parse_env_line,
    relative_to_repo,
    repository_to_clone_source,
    repository_to_github_slug,
    slugify,
    upsert_artifact,
    write_json,
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


def test_env_line_and_repository_slug_normalization() -> None:
    assert parse_env_line(" GITHUB_OWNER = 'inabako' ") == ("GITHUB_OWNER", "inabako")
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
