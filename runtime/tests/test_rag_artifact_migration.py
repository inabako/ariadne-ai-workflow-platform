from __future__ import annotations

import argparse
import json
import re
import runpy
from pathlib import Path

import pytest

from runtime.rag import migrate_retrieval_artifacts, standardize_corrective_report_names


UUID_JSON_RE = re.compile(r"^[0-9a-f-]{36}\.json$")
STANDARD_REPORT_RE = re.compile(r"^\d{14}_[0-9A-HJKMNP-TV-Z]{5,8}_[A-Za-z0-9._-]+\.md$")


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    return repo


def test_migrate_retrieval_artifacts_renames_legacy_json_and_rewrites_references(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    retrieval = repo / "rag" / "retrieval"
    retrieval.mkdir(parents=True)
    legacy_context = retrieval / "old_context-pack.json"
    legacy_result = retrieval / "old_retrieval-result.json"
    legacy_context.write_text(
        json.dumps(
            {
                "artifact_type": "rag-context-pack",
                "context_pack_id": "legacy-context",
                "retrieval_result": "rag/retrieval/old_retrieval-result.json",
                "context": "旧context",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    legacy_result.write_text(
        json.dumps(
            {
                "artifact_type": "rag-retrieval-result",
                "retrieval_id": "legacy-result",
                "context_pack": "rag/retrieval/old_context-pack.json",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(repo),
        retrieval_dir="rag/retrieval",
        jsonized_dir="rag/jsonized",
        delete_source=False,
        delete_duplicate_markdown=False,
        repair_from_jsonized=False,
        prune_legacy_migrations=False,
    )

    result = migrate_retrieval_artifacts.run(args)

    assert result["json_migrated_count"] == 2
    assert result["updated_reference_count"] >= 2
    targets = [Path(item["target"]).name for item in result["written"]]
    assert all(UUID_JSON_RE.match(name) for name in targets)
    migrated_context = json.loads((repo / result["written"][0]["target"]).read_text(encoding="utf-8"))
    all_payloads = [
        json.loads((repo / item["target"]).read_text(encoding="utf-8"))
        for item in result["written"]
    ]
    assert any(payload.get("context_pack_id") != "legacy-context" for payload in all_payloads)
    assert any(payload.get("retrieval_id") != "legacy-result" for payload in all_payloads)
    assert all("legacy_artifact_paths" in payload for payload in all_payloads)
    payloads_without_legacy_paths = [
        {key: value for key, value in payload.items() if key != "legacy_artifact_paths"}
        for payload in all_payloads
    ]
    assert "rag/retrieval/old_" not in json.dumps(payloads_without_legacy_paths, ensure_ascii=False)
    assert migrated_context["schema_version"] == "1.0"


def test_migrate_retrieval_artifacts_deletes_duplicate_markdown_for_migrated_companion(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    retrieval = repo / "rag" / "retrieval"
    retrieval.mkdir(parents=True)
    legacy_json = retrieval / "demo_context-pack.json"
    legacy_md = retrieval / "demo_context-pack.md"
    legacy_json.write_text(
        json.dumps({"artifact_type": "rag-context-pack", "context": "demo"}, ensure_ascii=False),
        encoding="utf-8",
    )
    legacy_md.write_text("# duplicate markdown\n", encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        retrieval_dir="rag/retrieval",
        jsonized_dir="rag/jsonized",
        delete_source=False,
        delete_duplicate_markdown=True,
        repair_from_jsonized=False,
        prune_legacy_migrations=False,
    )

    result = migrate_retrieval_artifacts.run(args)

    assert result["json_migrated_count"] == 1
    assert result["markdown_jsonized_count"] == 0
    assert result["deleted"] == ["rag/retrieval/demo_context-pack.md"]
    assert not legacy_md.exists()


def test_migrate_retrieval_artifacts_repairs_from_jsonized_wrapper(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    retrieval = repo / "rag" / "retrieval"
    jsonized = repo / "rag" / "jsonized"
    retrieval.mkdir(parents=True)
    jsonized.mkdir(parents=True)
    wrapper = jsonized / "wrapper.json"
    wrapper.write_text(
        json.dumps(
            {
                "source_path": "rag/retrieval/missing_rag-load-dispatch.json",
                "source_format": "json",
                "payload": {"artifact_type": "rag-load-dispatch", "query": "docker"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(repo),
        retrieval_dir="rag/retrieval",
        jsonized_dir="rag/jsonized",
        delete_source=False,
        delete_duplicate_markdown=False,
        repair_from_jsonized=True,
        prune_legacy_migrations=False,
    )

    result = migrate_retrieval_artifacts.run(args)

    assert result["json_migrated_count"] == 1
    target = repo / result["written"][0]["target"]
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["artifact_type"] == "rag-load-dispatch"
    assert payload["dispatch_id"] == target.stem
    assert payload["legacy_artifact_paths"] == ["rag/retrieval/missing_rag-load-dispatch.json"]


def test_migrate_retrieval_artifacts_jsonizes_non_duplicate_markdown(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    retrieval = repo / "rag" / "retrieval"
    retrieval.mkdir(parents=True)
    markdown = retrieval / "manual-note.md"
    markdown.write_text("# Manual Note\n\n人間が確認した内容です。\n", encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        retrieval_dir="rag/retrieval",
        jsonized_dir="rag/jsonized",
        delete_source=False,
        delete_duplicate_markdown=True,
        repair_from_jsonized=False,
        prune_legacy_migrations=False,
    )

    result = migrate_retrieval_artifacts.run(args)

    assert result["markdown_jsonized_count"] == 1
    target = repo / result["markdown_written"][0]["target"]
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["artifact_type"] == "rag-retrieval-markdown-source"
    assert payload["source_path"] == "rag/retrieval/manual-note.md"
    assert "人間が確認" in payload["content"]
    assert markdown.exists()


def test_migrate_retrieval_artifacts_parser_and_helper_edges(tmp_path: Path) -> None:
    parser = migrate_retrieval_artifacts.build_parser()
    args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "--retrieval-dir",
            "custom/retrieval",
            "--jsonized-dir",
            "custom/jsonized",
            "--delete-source",
            "--delete-duplicate-markdown",
            "--repair-from-jsonized",
            "--prune-legacy-migrations",
        ]
    )

    assert args.repo_root == str(tmp_path)
    assert args.retrieval_dir == "custom/retrieval"
    assert args.jsonized_dir == "custom/jsonized"
    assert args.delete_source is True
    assert args.delete_duplicate_markdown is True
    assert args.repair_from_jsonized is True
    assert args.prune_legacy_migrations is True

    assert migrate_retrieval_artifacts.artifact_type_from_name(Path("x_context-pack.json")) == "rag-context-pack"
    assert (
        migrate_retrieval_artifacts.artifact_type_from_name(Path("x_retrieval-result.json"))
        == "rag-retrieval-result"
    )
    assert (
        migrate_retrieval_artifacts.artifact_type_from_name(Path("x_rag-load-dispatch.json"))
        == "rag-load-dispatch"
    )
    assert migrate_retrieval_artifacts.artifact_type_from_name(Path("x.json")) == "rag-retrieval-artifact"
    assert migrate_retrieval_artifacts.companion_json_for_markdown(Path("x_context-pack.md")) == Path(
        "x_context-pack.json"
    )
    assert migrate_retrieval_artifacts.companion_json_for_markdown(Path("x_rag-load-dispatch.md")) == Path(
        "x_rag-load-dispatch.json"
    )
    assert migrate_retrieval_artifacts.companion_json_for_markdown(Path("x.md")) is None

    assert migrate_retrieval_artifacts.replace_refs("old", {"old": "new"}) == "new"
    assert migrate_retrieval_artifacts.replace_refs(["old", {"k": "old"}, 1], {"old": "new"}) == [
        "new",
        {"k": "new"},
        1,
    ]

    non_object = tmp_path / "array.json"
    non_object.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="Expected JSON object"):
        migrate_retrieval_artifacts.read_json(non_object)


def test_migrate_retrieval_artifacts_missing_retrieval_dir_fails(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    args = argparse.Namespace(
        repo_root=str(repo),
        retrieval_dir="rag/retrieval",
        jsonized_dir="rag/jsonized",
        delete_source=False,
        delete_duplicate_markdown=False,
        repair_from_jsonized=False,
        prune_legacy_migrations=False,
    )

    with pytest.raises(FileNotFoundError, match="RAG retrieval directory not found"):
        migrate_retrieval_artifacts.run(args)


def test_migrate_retrieval_artifacts_delete_source_and_generic_artifact(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    retrieval = repo / "rag" / "retrieval"
    retrieval.mkdir(parents=True)
    generic = retrieval / "legacy-generic.json"
    generic.write_text(json.dumps({"note": "legacy"}, ensure_ascii=False), encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        retrieval_dir="rag/retrieval",
        jsonized_dir="rag/jsonized",
        delete_source=True,
        delete_duplicate_markdown=False,
        repair_from_jsonized=False,
        prune_legacy_migrations=False,
    )

    result = migrate_retrieval_artifacts.run(args)

    assert result["json_migrated_count"] == 1
    assert result["deleted"] == ["rag/retrieval/legacy-generic.json"]
    assert not generic.exists()
    target = repo / result["written"][0]["target"]
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["artifact_type"] == "rag-retrieval-artifact"
    assert payload["artifact_id"] == target.stem
    assert payload["legacy_artifact_paths"] == ["rag/retrieval/legacy-generic.json"]


def test_migrate_retrieval_artifacts_jsonized_repair_skips_invalid_wrappers(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    retrieval = repo / "rag" / "retrieval"
    jsonized = repo / "rag" / "jsonized"
    retrieval.mkdir(parents=True)
    jsonized.mkdir(parents=True)
    wrappers = {
        "outside.json": {
            "source_path": "docs/not-retrieval.json",
            "source_format": "json",
            "payload": {"artifact_type": "rag-context-pack"},
        },
        "markdown.json": {
            "source_path": "rag/retrieval/from-md.md",
            "source_format": "markdown",
            "payload": {"artifact_type": "rag-context-pack"},
        },
        "uuid.json": {
            "source_path": "rag/retrieval/12345678-1234-1234-1234-123456789abc.json",
            "source_format": "json",
            "payload": {"artifact_type": "rag-context-pack"},
        },
        "nondict-payload.json": {
            "source_path": "rag/retrieval/legacy_context-pack.json",
            "source_format": "json",
            "payload": [],
        },
    }
    for name, payload in wrappers.items():
        (jsonized / name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        retrieval_dir="rag/retrieval",
        jsonized_dir="rag/jsonized",
        delete_source=False,
        delete_duplicate_markdown=False,
        repair_from_jsonized=True,
        prune_legacy_migrations=False,
    )

    result = migrate_retrieval_artifacts.run(args)

    assert result["json_migrated_count"] == 0
    assert result["written"] == []


def test_migrate_retrieval_artifacts_prunes_legacy_migration_outputs(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    retrieval = repo / "rag" / "retrieval"
    retrieval.mkdir(parents=True)
    fresh_source = retrieval / "fresh_context-pack.json"
    fresh_source.write_text(
        json.dumps(
            {
                "artifact_type": "rag-context-pack",
                "legacy_artifact_paths": ["docs/not-a-legacy-retrieval.json"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    stale = retrieval / "12345678-1234-1234-1234-123456789abc.json"
    stale.write_text(
        json.dumps(
            {
                "artifact_type": "rag-context-pack",
                "legacy_artifact_paths": ["rag/retrieval/old_context-pack.json"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    keep = retrieval / "87654321-4321-4321-4321-cba987654321.json"
    keep.write_text(
        json.dumps(
            {
                "artifact_type": "rag-context-pack",
                "legacy_artifact_paths": ["docs/already-uuid.json"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(repo),
        retrieval_dir="rag/retrieval",
        jsonized_dir="rag/jsonized",
        delete_source=False,
        delete_duplicate_markdown=False,
        repair_from_jsonized=False,
        prune_legacy_migrations=True,
    )

    result = migrate_retrieval_artifacts.run(args)

    assert result["pruned"] == ["rag/retrieval/12345678-1234-1234-1234-123456789abc.json"]
    assert result["json_migrated_count"] == 1
    assert not stale.exists()
    assert keep.exists()


def test_migrate_retrieval_artifacts_delete_markdown_source_and_skip_readme(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    retrieval = repo / "rag" / "retrieval"
    retrieval.mkdir(parents=True)
    markdown = retrieval / "manual-note.md"
    readme = retrieval / "README.md"
    markdown.write_text("# Manual\n", encoding="utf-8")
    readme.write_text("# Keep\n", encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        retrieval_dir="rag/retrieval",
        jsonized_dir="rag/jsonized",
        delete_source=True,
        delete_duplicate_markdown=False,
        repair_from_jsonized=False,
        prune_legacy_migrations=False,
    )

    result = migrate_retrieval_artifacts.run(args)

    assert result["markdown_jsonized_count"] == 1
    assert result["deleted"] == ["rag/retrieval/manual-note.md"]
    assert not markdown.exists()
    assert readme.exists()


def test_migrate_retrieval_artifacts_main_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(
        migrate_retrieval_artifacts,
        "run",
        lambda args: {"retrieval_dir": "rag/retrieval", "json_migrated_count": 0},
    )

    assert migrate_retrieval_artifacts.main(["--repo-root", str(tmp_path)]) == 0
    assert '"json_migrated_count": 0' in capsys.readouterr().out

    def fail(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(migrate_retrieval_artifacts, "run", fail)
    assert migrate_retrieval_artifacts.main(["--repo-root", str(tmp_path)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(migrate_retrieval_artifacts.__file__)))
    assert namespace["build_parser"]


def test_standardize_report_names_renames_legacy_report_and_updates_references(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    report_dir = repo / "rag" / "corrective-action-report"
    report_dir.mkdir(parents=True)
    legacy = report_dir / "20260606111000_localty-system-gui.md"
    legacy.write_text(
        "---\n"
        "created_at: 2026-06-06T11:10:00+00:00\n"
        "repository: https://github.com/inabako/localty-system-gui.git\n"
        "---\n"
        "# 20260606111000_localty-system-gui.md\n\n"
        "source: rag/corrective-action-report/20260606111000_localty-system-gui.md\n",
        encoding="utf-8",
    )
    index = repo / "rag" / "indexes" / "documents.jsonl"
    index.parent.mkdir(parents=True)
    index.write_text("rag/corrective-action-report/20260606111000_localty-system-gui.md\n", encoding="utf-8")
    monkeypatch.setattr(standardize_corrective_report_names, "random_token", lambda length: "ABCDE")
    args = argparse.Namespace(
        repo_root=str(repo),
        source_dir="rag/corrective-action-report",
        replace_references=True,
        random_length=5,
    )

    result = standardize_corrective_report_names.run(args)

    assert result["renamed_count"] == 1
    new_rel = result["renames"][0]["new"]
    new_path = repo / new_rel
    assert new_path.exists()
    assert new_path.name == "20260606111000_ABCDE_localty-system-gui.git.md"
    assert STANDARD_REPORT_RE.match(new_path.name)
    assert not legacy.exists()
    assert "20260606111000_localty-system-gui.md" not in new_path.read_text(encoding="utf-8")
    assert new_rel in index.read_text(encoding="utf-8")
    assert result["updated_reference_count"] >= 1


def test_standardize_report_names_skips_already_standard_and_readme(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    report_dir = repo / "rag" / "corrective-action-report"
    report_dir.mkdir(parents=True)
    readme = report_dir / "README.md"
    standard = report_dir / "20260701000000_ABCDE_localty-system.md"
    readme.write_text("# README\n", encoding="utf-8")
    standard.write_text("# already standard\n", encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        source_dir="rag/corrective-action-report",
        replace_references=True,
        random_length=5,
    )

    result = standardize_corrective_report_names.run(args)

    assert result["renamed_count"] == 0
    assert readme.exists()
    assert standard.exists()


def test_standardize_report_names_rejects_source_dir_outside_repo(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    args = argparse.Namespace(
        repo_root=str(repo),
        source_dir=str(outside),
        replace_references=False,
        random_length=5,
    )

    with pytest.raises(ValueError, match="Source directory must be inside repo root"):
        standardize_corrective_report_names.run(args)


def test_standardize_report_names_parser_and_helper_fallbacks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    parser = standardize_corrective_report_names.build_parser()
    args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "--source-dir",
            "custom/reports",
            "--replace-references",
            "--random-length",
            "6",
        ]
    )
    assert args.repo_root == str(tmp_path)
    assert args.source_dir == "custom/reports"
    assert args.replace_references is True
    assert args.random_length == 6

    assert standardize_corrective_report_names.sanitize_name("`https://github.com/owner/repo.git`") == "repo.git"
    assert standardize_corrective_report_names.sanitize_name(" !!! ") == "unknown-repository"

    report = tmp_path / "20260707112233_legacy-report.md"
    report.write_text("created_at: invalid-date\n", encoding="utf-8")
    assert standardize_corrective_report_names.datetime_from_text(report, report.read_text(encoding="utf-8")).strftime(
        "%Y%m%d%H%M%S"
    ) == "20260707112233"

    naive = tmp_path / "naive.md"
    naive.write_text("created_at: 2026-07-07T11:22:33\n", encoding="utf-8")
    assert standardize_corrective_report_names.datetime_from_text(naive, naive.read_text(encoding="utf-8")).tzinfo is not None

    mtime = tmp_path / "mtime-only.md"
    mtime.write_text("# no date\n", encoding="utf-8")
    assert standardize_corrective_report_names.datetime_from_text(mtime, "").year >= 2000

    uuid_name = tmp_path / "20260707112233_12345678-1234-1234-1234-123456789abc_owner.repo.md"
    assert standardize_corrective_report_names.repository_from_text(uuid_name, "") == "owner.repo"
    monkeypatch.setattr(standardize_corrective_report_names, "TARGET_PROJECT_RE", re.compile(r"target:\s*`(?P<value>[^`]+)`"))
    assert (
        standardize_corrective_report_names.repository_from_text(
            tmp_path / "target-project.md",
            "target: `owner/target-repo`",
        )
        == "target-repo"
    )
    assert standardize_corrective_report_names.repository_from_text(tmp_path / "20260707112233_repo-extra.md", "") == "repo-extra"

    monkeypatch.setattr(standardize_corrective_report_names, "random_token", lambda length: "ABCDEFGH"[:length])
    assert standardize_corrective_report_names.replacement_name(report, report.read_text(encoding="utf-8"), 5).endswith(
        "_ABCDE_legacy-report.md"
    )
    monkeypatch.undo()
    assert len(standardize_corrective_report_names.random_token(8)) == 8
    assert set(standardize_corrective_report_names.random_token(8)) <= set(standardize_corrective_report_names.CROCKFORD_BASE32)


def test_standardize_report_names_missing_dir_and_target_collision(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    args = argparse.Namespace(
        repo_root=str(repo),
        source_dir="rag/corrective-action-report",
        replace_references=False,
        random_length=5,
    )
    with pytest.raises(FileNotFoundError, match="Corrective report directory not found"):
        standardize_corrective_report_names.run(args)

    report_dir = repo / "rag" / "corrective-action-report"
    report_dir.mkdir(parents=True)
    source = report_dir / "20260707112233_legacy.md"
    source.write_text("repository: owner/repo\n", encoding="utf-8")
    monkeypatch.setattr(standardize_corrective_report_names, "random_token", lambda length: "ABCDE")
    target = report_dir / "20260707112233_ABCDE_repo.md"
    target.write_text("# already exists\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Target already exists"):
        standardize_corrective_report_names.run(args)


def test_standardize_report_names_replace_text_references_updates_supported_files(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    old_rel = "rag/corrective-action-report/old.md"
    new_rel = "rag/corrective-action-report/new.md"
    files = [
        repo / "rag" / "indexes" / "documents.jsonl",
        repo / "rag" / "normalized" / "doc.json",
        repo / "rag" / "corrective-action-report" / "note.md",
        repo / "README.md",
        repo / "skills" / "skill.md",
        repo / ".github" / "prompts" / "prompt.md",
        repo / "runtime" / "docs" / "note.md",
    ]
    for path in files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"path={old_rel}; file=old.md\n", encoding="utf-8")

    updated = standardize_corrective_report_names.replace_text_references(repo, {old_rel: new_rel})

    assert sorted(updated) == sorted(
        [
            "README.md",
            ".github/prompts/prompt.md",
            "rag/corrective-action-report/note.md",
            "rag/indexes/documents.jsonl",
            "rag/normalized/doc.json",
            "runtime/docs/note.md",
            "skills/skill.md",
        ]
    )
    for path in files:
        assert new_rel in path.read_text(encoding="utf-8")
        assert "new.md" in path.read_text(encoding="utf-8")


def test_standardize_report_names_main_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(
        standardize_corrective_report_names,
        "run",
        lambda args: {"source_dir": "rag/corrective-action-report", "renamed_count": 0},
    )
    assert standardize_corrective_report_names.main(["--repo-root", str(tmp_path)]) == 0
    assert '"renamed_count": 0' in capsys.readouterr().out

    def fail(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(standardize_corrective_report_names, "run", fail)
    assert standardize_corrective_report_names.main(["--repo-root", str(tmp_path)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(standardize_corrective_report_names.__file__)))
    assert namespace["build_parser"]
