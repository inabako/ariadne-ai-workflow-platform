from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import pytest

from runtime.workflow import corrective_action_report, init_corrective_action_fix


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    return repo


def make_args(repo: Path, **overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "repository": "https://github.com/owner/ariadne-target.git",
        "target_branch": "feature/issue-123",
        "work_id": "",
        "base_work_id": "",
        "reuse_existing": False,
        "report_path": "",
        "intent_summary": "",
        "repo_root": str(repo),
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_init_corrective_action_fix_small_helpers(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    assert init_corrective_action_fix.branch_to_work_id("feature/issue-123") == "issue-123"
    assert init_corrective_action_fix.branch_to_work_id(r"fix\windows/path") == "fix-windows-path"
    assert init_corrective_action_fix.repository_name("https://github.com/owner/repo.git") == "repo"
    assert init_corrective_action_fix.repository_name("repo-only", "owner") == "repo-only"
    assert init_corrective_action_fix.repository_name(str(repo / "local-repo.git")) == "local-repo"

    report = repo / "rag" / "corrective-action-report" / "report.md"
    report.parent.mkdir(parents=True)
    report.write_text("# report\n", encoding="utf-8")
    explicit = init_corrective_action_fix.resolve_report_input(
        repo,
        make_args(repo, report_path=str(report)),
        "issue-123",
    )
    assert explicit["resolution"] == "argument"
    assert explicit["report_path"] == "rag/corrective-action-report/report.md"
    assert explicit["context_path"] == ""


def test_init_corrective_action_fix_report_context_from_work_dir_edges(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    empty_work = repo / "work" / "empty"
    empty_work.mkdir(parents=True)
    assert init_corrective_action_fix.report_context_from_work_dir(repo, empty_work) == {}

    bad_work = repo / "work" / "bad"
    (bad_work / "context").mkdir(parents=True)
    (bad_work / "context" / "corrective-action-report.json").write_text("[]", encoding="utf-8")
    (bad_work / "context" / "context-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "artifact_type": "context-manifest",
                "work_id": "bad",
                "contexts": [
                    {
                        "type": "corrective-action-report",
                        "path": "work/bad/context/corrective-action-report.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    assert init_corrective_action_fix.report_context_from_work_dir(repo, bad_work) == {}

    no_report_work = repo / "work" / "no-report"
    (no_report_work / "context").mkdir(parents=True)
    (no_report_work / "context" / "corrective-action-report.json").write_text(
        json.dumps({"artifact_type": "corrective-action-report"}),
        encoding="utf-8",
    )
    (no_report_work / "context" / "context-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "artifact_type": "context-manifest",
                "work_id": "no-report",
                "contexts": [
                    {
                        "type": "corrective-action-report",
                        "path": "work/no-report/context/corrective-action-report.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    assert init_corrective_action_fix.report_context_from_work_dir(repo, no_report_work) == {}


def test_init_corrective_action_fix_resolves_manifest_from_base_or_branch_work(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    report = repo / "rag" / "corrective-action-report" / "report.md"
    report.parent.mkdir(parents=True)
    report.write_text("---\nrepository: owner/repo\nbranch: develop\n---\n\n# report\n", encoding="utf-8")
    corrective_action_report.run_register(
        argparse.Namespace(
            repo_root=str(repo),
            command="register",
            report_path=str(report),
            repository="owner/repo",
            target_branch="develop",
            work_id="develop",
            work_dir="",
        )
    )

    from_base = init_corrective_action_fix.resolve_report_input(
        repo,
        make_args(repo, base_work_id="develop", target_branch="feature/issue-456"),
        "issue-456",
    )

    assert from_base["resolution"] == "manifest"
    assert from_base["report_path"] == "rag/corrective-action-report/report.md"
    assert from_base["context_path"] == "work/develop/context/corrective-action-report.json"

    from_branch = init_corrective_action_fix.resolve_report_input(
        repo,
        make_args(repo, base_work_id="", target_branch="develop"),
        "issue-789",
    )
    assert from_branch["resolution"] == "manifest"

    missing = init_corrective_action_fix.resolve_report_input(
        repo,
        make_args(repo, base_work_id="", target_branch="feature/issue-missing"),
        "issue-missing",
    )
    assert missing == {"report_path": "", "context_path": "", "resolution": "missing"}


def test_init_corrective_action_fix_write_report_context_skips_empty_and_registers(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    work_dir = repo / "work" / "issue-1"
    (work_dir / "context").mkdir(parents=True)

    init_corrective_action_fix.write_corrective_report_context(
        repo,
        work_dir,
        work_id="issue-1",
        repository="owner/repo",
        target_branch="feature/issue-1",
        report_rel="",
        report_resolution="missing",
        source_context_path="",
    )
    assert not (work_dir / "context" / "corrective-action-report.json").exists()

    report = repo / "rag" / "corrective-action-report" / "manual.md"
    report.parent.mkdir(parents=True)
    report.write_text("# report\n", encoding="utf-8")
    init_corrective_action_fix.write_corrective_report_context(
        repo,
        work_dir,
        work_id="issue-1",
        repository="owner/repo",
        target_branch="feature/issue-1",
        report_rel="rag/corrective-action-report/manual.md",
        report_resolution="argument",
        source_context_path="",
    )

    context = json.loads((work_dir / "context" / "corrective-action-report.json").read_text(encoding="utf-8"))
    manifest = json.loads((work_dir / "context" / "context-manifest.json").read_text(encoding="utf-8"))
    assert context["report_exists"] is True
    assert context["resolution"]["mode"] == "argument"
    assert "corrective-action-report" in {item["type"] for item in manifest["contexts"]}


def test_defensive_specimen_init_corrective_action_fix_accepts_absolute_report_paths(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    report = repo / "rag" / "corrective-action-report" / "absolute.md"
    report.parent.mkdir(parents=True)
    report.write_text("# report\n", encoding="utf-8")
    args = make_args(repo, report_path=str(report))

    resolved = init_corrective_action_fix.resolve_report_input(repo, args, "issue-abs")

    assert resolved["report_path"] == "rag/corrective-action-report/absolute.md"
    assert resolved["resolution"] == "argument"

    work_dir = repo / "work" / "issue-abs"
    (work_dir / "context").mkdir(parents=True)
    init_corrective_action_fix.write_corrective_report_context(
        repo,
        work_dir,
        work_id="issue-abs",
        repository="owner/repo",
        target_branch="feature/issue-abs",
        report_rel=str(report),
        report_resolution="argument",
        source_context_path="",
    )
    context = json.loads((work_dir / "context" / "corrective-action-report.json").read_text(encoding="utf-8"))
    assert context["report_filename"] == "absolute.md"
    assert context["report_exists"] is True


def test_defensive_specimen_report_context_from_manifest_accepts_absolute_path(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    base_work = repo / "work" / "base"
    context_dir = base_work / "context"
    context_dir.mkdir(parents=True)
    report = repo / "rag" / "corrective-action-report" / "manifest-absolute.md"
    report.parent.mkdir(parents=True)
    report.write_text("# report\n", encoding="utf-8")
    context_path = context_dir / "corrective-action-report.json"
    context_path.write_text(json.dumps({"report_path": str(report)}), encoding="utf-8")
    (context_dir / "context-manifest.json").write_text(
        json.dumps(
            {
                "contexts": [
                    {
                        "type": "corrective-action-report",
                        "path": "work/base/context/corrective-action-report.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    resolved = init_corrective_action_fix.report_context_from_work_dir(repo, base_work)

    assert resolved["report_path"] == "rag/corrective-action-report/manifest-absolute.md"


def test_init_corrective_action_fix_run_with_argument_report_and_reuse_existing(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    report = repo / "rag" / "corrective-action-report" / "manual.md"
    report.parent.mkdir(parents=True)
    report.write_text("# report\n", encoding="utf-8")

    args = make_args(
        repo,
        work_id="issue-777",
        report_path="rag/corrective-action-report/manual.md",
        intent_summary="Implement selected CAR findings.",
    )

    result = init_corrective_action_fix.run(args)

    assert result["work_id"] == "issue-777"
    assert result["repository"] == "https://github.com/owner/ariadne-target.git"
    assert result["report_resolution"] == "argument"
    work_dir = repo / result["work_dir"]
    agent = json.loads((work_dir / "context" / "agent-context.json").read_text(encoding="utf-8"))
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    report_context = json.loads((work_dir / "context" / "corrective-action-report.json").read_text(encoding="utf-8"))
    assert agent["intent"]["summary"] == "Implement selected CAR findings."
    assert "rag/corrective-action-report/manual.md" in agent["agent"]["input_artifacts"]
    assert any(item["id"] == "CORRECTIVE-ACTION-REPORT" for item in artifact_index["artifacts"])
    assert report_context["resolution"]["mode"] == "argument"

    with pytest.raises(FileExistsError, match="Work directory already exists"):
        init_corrective_action_fix.run(make_args(repo, work_id="issue-777"))

    reused = init_corrective_action_fix.run(make_args(repo, work_id="issue-777", reuse_existing=True))
    assert reused["work_id"] == "issue-777"


def test_init_corrective_action_fix_run_missing_report_has_no_report_artifact(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    result = init_corrective_action_fix.run(make_args(repo, target_branch="feature/no-report"))

    assert result["work_id"] == "feature-no-report"
    assert result["report_resolution"] == "missing"
    work_dir = repo / result["work_dir"]
    artifact_index = json.loads((work_dir / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    assert not any(item["id"] == "CORRECTIVE-ACTION-REPORT" for item in artifact_index["artifacts"])
    assert not (work_dir / "context" / "corrective-action-report.json").exists()


def test_init_corrective_action_fix_parser_and_main_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    repo = make_repo(tmp_path)
    parser = init_corrective_action_fix.build_parser()
    args = parser.parse_args(
        [
            "--repository",
            "owner/repo",
            "--target-branch",
            "feature/issue-1",
            "--work-id",
            "issue-1",
            "--base-work-id",
            "develop",
            "--reuse-existing",
            "--report-path",
            "rag/corrective-action-report/report.md",
            "--intent-summary",
            "intent",
            "--repo-root",
            str(repo),
        ]
    )
    assert args.repository == "owner/repo"
    assert args.target_branch == "feature/issue-1"
    assert args.work_id == "issue-1"
    assert args.base_work_id == "develop"
    assert args.reuse_existing is True
    assert args.report_path == "rag/corrective-action-report/report.md"
    assert args.intent_summary == "intent"

    monkeypatch.setattr(init_corrective_action_fix, "run", lambda args: {"work_id": "issue-1"})
    assert init_corrective_action_fix.main(["--repository", "owner/repo", "--target-branch", "develop"]) == 0
    assert '"work_id": "issue-1"' in capsys.readouterr().out

    def fail(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(init_corrective_action_fix, "run", fail)
    assert init_corrective_action_fix.main(["--repository", "owner/repo", "--target-branch", "develop"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err

    namespace = runpy.run_path(str(Path(init_corrective_action_fix.__file__)))
    assert namespace["build_parser"]
