from __future__ import annotations

import argparse
import json
import runpy
import subprocess
from pathlib import Path

import pytest

from runtime.rag import jsonize_rag_tree
from runtime.scm import compare_requirements


def make_repo(tmp_path: Path, work_id: str = "issue-1") -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    work_dir = repo / "work" / work_id
    (repo / ".git").mkdir(parents=True)
    (work_dir / "context").mkdir(parents=True)
    (work_dir / "process-report").mkdir(parents=True)
    return repo, work_dir


def test_jsonize_rag_tree_should_convert_skips_uuid_json_and_readme_by_default(tmp_path: Path) -> None:
    assert jsonize_rag_tree.should_convert(tmp_path / "README.md", include_readme=False) is False
    assert jsonize_rag_tree.should_convert(tmp_path / "README.md", include_readme=True) is False

    readme = tmp_path / "README.md"
    readme.write_text("# readme\n", encoding="utf-8")
    uuid_json = tmp_path / "12345678-1234-1234-1234-123456789abc.json"
    uuid_json.write_text("{}", encoding="utf-8")
    legacy_json = tmp_path / "legacy.json"
    legacy_json.write_text("{}", encoding="utf-8")
    note = tmp_path / "note.md"
    note.write_text("# note\n", encoding="utf-8")

    assert jsonize_rag_tree.should_convert(readme, include_readme=False) is False
    assert jsonize_rag_tree.should_convert(readme, include_readme=True) is True
    assert jsonize_rag_tree.should_convert(uuid_json, include_readme=True) is False
    assert jsonize_rag_tree.should_convert(legacy_json, include_readme=True) is True
    assert jsonize_rag_tree.should_convert(note, include_readme=False) is True


def test_jsonize_rag_tree_reads_jsonl_with_parse_errors(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text('{"ok": true}\n\n{bad json}\n', encoding="utf-8")

    rows = jsonize_rag_tree.read_jsonl(path)

    assert rows[0] == {"ok": True}
    assert rows[1]["line_number"] == 3
    assert rows[1]["raw"] == "{bad json}"
    assert "parse_error" in rows[1]


def test_jsonize_rag_tree_run_converts_supported_sources_and_excludes_output_dir(tmp_path: Path) -> None:
    repo, _ = make_repo(tmp_path)
    rag = repo / "rag"
    rag.mkdir()
    (rag / "README.md").write_text("# README\n", encoding="utf-8")
    (rag / "note.md").write_text("# Note\n\n日本語メモ。\n", encoding="utf-8")
    (rag / "data.json").write_text('{"kind": "legacy"}', encoding="utf-8")
    (rag / "rows.jsonl").write_text('{"row": 1}\nnot-json\n', encoding="utf-8")
    output = rag / "jsonized"
    output.mkdir()
    (output / "already.json").write_text('{"should": "not be re-jsonized"}', encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        rag_dir="rag",
        output_dir="rag/jsonized",
        include_readme=False,
        delete_source=False,
        clean_output=False,
    )

    result = jsonize_rag_tree.run(args)

    assert result["converted_count"] == 3
    source_paths = {item["source_path"] for item in result["artifacts"]}
    assert source_paths == {"rag/data.json", "rag/note.md", "rag/rows.jsonl"}
    payloads = [json.loads((repo / item["json_path"]).read_text(encoding="utf-8")) for item in result["artifacts"]]
    assert {payload["source_format"] for payload in payloads} == {"json", "jsonl", "text"}
    assert all(payload["artifact_type"] == "rag-jsonized-source" for payload in payloads)


def test_jsonize_rag_tree_delete_source_removes_converted_files(tmp_path: Path) -> None:
    repo, _ = make_repo(tmp_path)
    source = repo / "rag" / "note.txt"
    source.parent.mkdir()
    source.write_text("temporary note\n", encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        rag_dir="rag",
        output_dir="rag/jsonized",
        include_readme=False,
        delete_source=True,
        clean_output=False,
    )

    result = jsonize_rag_tree.run(args)

    assert result["converted_count"] == 1
    assert result["deleted_source"] is True
    assert not source.exists()


def test_jsonize_rag_tree_parser_payload_clean_missing_main_and_script_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parser = jsonize_rag_tree.build_parser()
    parsed = parser.parse_args(
        [
            "--rag-dir",
            "custom-rag",
            "--output-dir",
            "custom-jsonized",
            "--include-readme",
            "--delete-source",
            "--clean-output",
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert parsed.rag_dir == "custom-rag"
    assert parsed.include_readme is True
    assert parsed.delete_source is True
    assert parsed.clean_output is True

    invalid_json = tmp_path / "bad.json"
    invalid_json.write_text("{bad", encoding="utf-8")
    source_format, payload, text = jsonize_rag_tree.source_payload(invalid_json)
    assert source_format == "json"
    assert payload["raw"] == "{bad"
    assert "parse_error" in payload
    assert text == "{bad"

    repo, _ = make_repo(tmp_path, work_id="issue-clean")
    rag = repo / "rag"
    output = repo / "rag" / "jsonized"
    rag.mkdir()
    output.mkdir()
    (rag / "README.md").write_text("# readme\n", encoding="utf-8")
    stale = output / "stale.json"
    keep = output / "keep.txt"
    stale.write_text("{}", encoding="utf-8")
    keep.write_text("keep", encoding="utf-8")
    args = argparse.Namespace(
        repo_root=str(repo),
        rag_dir="rag",
        output_dir="rag/jsonized",
        include_readme=True,
        delete_source=False,
        clean_output=True,
    )

    result = jsonize_rag_tree.run(args)

    assert result["converted_count"] == 1
    assert not stale.exists()
    assert keep.exists()

    with pytest.raises(FileNotFoundError, match="RAG directory not found"):
        jsonize_rag_tree.run(
            argparse.Namespace(
                repo_root=str(repo),
                rag_dir="missing",
                output_dir="rag/jsonized",
                include_readme=False,
                delete_source=False,
                clean_output=False,
            )
        )

    assert jsonize_rag_tree.main(["--repo-root", str(repo), "--rag-dir", "rag", "--output-dir", "rag/jsonized"]) == 0
    assert '"converted_count"' in capsys.readouterr().out

    monkeypatch.setattr(jsonize_rag_tree, "run", lambda args: (_ for _ in ()).throw(RuntimeError("boom")))
    assert jsonize_rag_tree.main(["--repo-root", str(repo)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(jsonize_rag_tree.__file__)))
    assert namespace["build_parser"]


def test_compare_requirements_safe_git_returns_error_text(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        compare_requirements,
        "run_git",
        lambda args, cwd: subprocess.CompletedProcess(["git", *args], 128, stdout="", stderr="fatal: bad revision"),
    )

    assert compare_requirements.safe_git(["log"], tmp_path) == "fatal: bad revision"


def test_compare_requirements_first_lines_limits_and_reports_read_errors(tmp_path: Path) -> None:
    path = tmp_path / "requirements.md"
    path.write_text("\n".join(f"line-{index}" for index in range(50)), encoding="utf-8")

    assert compare_requirements.first_lines(path, max_lines=3) == "line-0\nline-1\nline-2"
    assert "Could not read requirement file" in compare_requirements.first_lines(tmp_path)


def test_compare_requirements_writes_reports_and_artifact_index(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo, work_dir = make_repo(tmp_path)
    source = work_dir / "source" / "repository"
    source.mkdir(parents=True)
    requirement = repo / "work" / "requirements" / "req.md"
    requirement.parent.mkdir(parents=True)
    requirement.write_text("# Requirement\n\nRepository: inabako/example\n", encoding="utf-8")
    (work_dir / "context" / "artifact-index.json").write_text(
        json.dumps(
            {
                "artifacts": [
                    {
                        "id": "REQ-1",
                        "type": "requirement",
                        "path": "work/requirements/req.md",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(compare_requirements, "current_branch", lambda path: "develop")
    monkeypatch.setattr(compare_requirements, "current_commit", lambda path: "abc123")

    def fake_safe_git(args: list[str], cwd: Path) -> str:
        if args == ["status", "--short"]:
            return " M app.py"
        if args == ["log", "--oneline", "-5"]:
            return "abc123 feat: demo"
        if args == ["ls-files"]:
            return "app.py\nREADME.md"
        raise AssertionError(args)

    monkeypatch.setattr(compare_requirements, "safe_git", fake_safe_git)
    args = argparse.Namespace(
        work_id="issue-1",
        repo_root=str(repo),
        source_dir=str(source),
        requirements=None,
    )

    result = compare_requirements.compare_requirements(args)

    json_report = json.loads((repo / result["json_report"]).read_text(encoding="utf-8"))
    markdown = (repo / result["markdown_report"]).read_text(encoding="utf-8-sig")
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    assert json_report["branch"] == "develop"
    assert json_report["commit"] == "abc123"
    assert json_report["tracked_file_count"] == 2
    assert "work/requirements/req.md" in markdown
    assert "Repository: inabako/example" in markdown
    assert any(artifact["id"].startswith("REQ-COMPARE-MD-") for artifact in artifact_index["artifacts"])
    assert any(artifact["id"].startswith("REQ-COMPARE-JSON-") for artifact in artifact_index["artifacts"])


def test_compare_requirements_requires_work_and_source_dirs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "work").mkdir()
    args = argparse.Namespace(
        work_id="missing",
        repo_root=str(repo),
        source_dir=None,
        requirements=[],
    )

    with pytest.raises(FileNotFoundError, match="Work directory does not exist"):
        compare_requirements.compare_requirements(args)
