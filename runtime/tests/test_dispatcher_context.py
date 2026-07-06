from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

from runtime.workflow import dispatcher_context


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def make_args(repo_root: Path, **overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "repo_root": str(repo_root),
        "work_id": "issue-ctx",
        "workflow": "/docs-sync",
        "intent_summary": "",
        "tool": [],
        "tool_mode": "",
        "tool_purpose": "workflow execution",
        "runtime_mode": "standard",
        "target_dir": "",
        "required_context": [],
        "required_environment": "",
        "next_command": [],
        "stop_condition": [],
        "candidate_limit": 5,
        "force": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_registry_loaders_and_text_helpers_use_safe_defaults(tmp_path: Path) -> None:
    write_json(tmp_path / "runtime" / "registries" / "workflow_help.json", [])
    write_json(tmp_path / "runtime" / "registries" / "tool_candidates.json", [])

    assert dispatcher_context.load_workflow_help_registry(tmp_path) == {"commands": [], "extensions": []}
    assert dispatcher_context.load_tool_candidate_registry(tmp_path) == {"tools": []}
    assert dispatcher_context.normalize_command("docs-sync") == "/docs-sync"
    assert dispatcher_context.normalize_command("/docs-sync") == "/docs-sync"
    assert dispatcher_context.normalize_command("") == ""
    assert dispatcher_context.flatten_text({"a": ["Robot", None, 7]}) == "Robot  7"
    assert {"docs", "sync", "123"} <= dispatcher_context.tokenize("/docs_sync-123")
    assert dispatcher_context.workflow_names(
        {
            "command": "/docs-sync",
            "aliases": ["docs"],
            "workflow": "docs-sync",
            "skill": "docs-sync",
        }
    ) == ["/docs-sync", "docs", "docs-sync", "docs-sync"]


def test_select_workflow_record_requires_human_check_for_no_candidate() -> None:
    selection = dispatcher_context.select_workflow_record(
        {"commands": []},
        "/missing",
        "",
        candidate_limit=5,
    )

    assert selection["status"] == "human-check-required"
    assert selection["confidence"] == "unknown"
    assert selection["ambiguity_margin"] is None
    assert "was not found" in selection["human_check_reasons"][0]


def test_select_workflow_record_requires_human_check_for_ambiguous_candidate() -> None:
    registry = {
        "commands": [
            {
                "command": "/alpha-flow",
                "workflow": "alpha-flow",
                "overview": "shared robot maintenance",
            },
            {
                "command": "/beta-flow",
                "workflow": "beta-flow",
                "overview": "shared robot maintenance",
            },
        ]
    }

    selection = dispatcher_context.select_workflow_record(
        registry,
        "shared robot maintenance",
        "",
        candidate_limit=5,
    )

    assert selection["status"] == "human-check-required"
    assert selection["confidence"] == "low"
    assert selection["ambiguity_margin"] == 0
    assert "ambiguous" in selection["human_check_reasons"][0]


def test_select_workflow_record_requires_human_check_for_low_confidence() -> None:
    registry = {
        "commands": [
            {
                "command": "/alpha-flow",
                "workflow": "alpha-flow",
                "overview": "weak signal only",
            }
        ]
    }

    selection = dispatcher_context.select_workflow_record(
        registry,
        "weak",
        "",
        candidate_limit=5,
    )

    assert selection["status"] == "human-check-required"
    assert selection["confidence"] == "low"
    assert selection["ambiguity_margin"] == 29
    assert "confidence is too low" in selection["human_check_reasons"][0]


def test_workflow_candidate_boundary_paths_cover_empty_limits_and_medium_auto() -> None:
    registry = {
        "commands": [
            {
                "command": "/alpha-flow",
                "workflow": "alpha-flow",
                "overview": "alpha runbook",
            },
            {
                "command": "/beta-flow",
                "workflow": "beta-flow",
                "overview": "beta runbook",
            },
        ]
    }

    manual_without_candidate_list = dispatcher_context.select_workflow_record(
        registry,
        "/alpha-flow",
        "",
        candidate_limit=0,
    )
    assert manual_without_candidate_list["selection_mode"] == "manual"
    assert manual_without_candidate_list["candidates"] == []

    medium_auto = dispatcher_context.select_workflow_record(
        registry,
        "alpha flow",
        "",
        candidate_limit=5,
    )
    assert medium_auto["selection_mode"] == "auto"
    assert medium_auto["confidence"] == "medium"
    assert medium_auto["candidates"][0]["selected"] is True


def test_candidate_branch_edges_cover_no_command_and_unmatched_candidates(monkeypatch) -> None:
    score, reasons = dispatcher_context.candidate_score(
        {"overview": "unregistered text"},
        "unmatched",
        "",
    )
    assert score == 0
    assert reasons == ["no strong registry evidence"]

    registry = {
        "commands": [
            {
                "command": "/alpha-flow",
                "workflow": "alpha-flow",
                "overview": "alpha runbook",
            }
        ]
    }

    monkeypatch.setattr(
        dispatcher_context,
        "workflow_candidates",
        lambda registry, workflow, intent_summary, *, limit: [{"command": "/other-flow", "score": 10}],
    )
    manual = dispatcher_context.select_workflow_record(
        registry,
        "/alpha-flow",
        "",
        candidate_limit=5,
    )
    assert manual["selection_mode"] == "manual"
    assert "selected" not in manual["candidates"][0]

    monkeypatch.setattr(
        dispatcher_context,
        "workflow_candidates",
        lambda registry, workflow, intent_summary, *, limit: [{"command": "/missing-flow", "score": 60}],
    )
    missing_selected_record = dispatcher_context.select_workflow_record(
        registry,
        "missing flow",
        "",
        candidate_limit=5,
    )
    assert missing_selected_record["status"] == "human-check-required"
    assert missing_selected_record["record"] == {}


def test_tool_selection_edges_cover_manual_fallback_and_auto_human_check() -> None:
    registry = {
        "tools": [
            {
                "name": "docker",
                "aliases": ["compose"],
                "default_mode": "local",
                "purpose": "Container runtime validation",
                "workflows": ["/realtime-iac"],
                "keywords": ["docker", "compose"],
                "install_required": True,
                "mutation_capable": True,
                "human_check_required": True,
                "human_check_reasons": ["Docker host access requires confirmation."],
            },
            {
                "name": "note-tool",
                "default_mode": "read-only",
                "purpose": "rare evidence note",
                "workflows": [],
                "keywords": ["rare"],
            },
        ]
    }

    fallback = dispatcher_context.split_tool("unknown:mutation:change host", "local", "default", registry)
    assert fallback == {
        "name": "unknown",
        "mode": "mutation",
        "purpose": "change host",
        "required": True,
        "source": "dispatcher-input",
        "human_check_required": True,
    }

    docker = dispatcher_context.split_tool("compose:mutation:validate containers", "local", "default", registry)
    assert docker["name"] == "docker"
    assert docker["human_check_required"] is True
    assert "Tool `docker` is selected for mutation mode." in docker["human_check_reasons"]
    assert "Tool `docker` may require installation or runtime dependency setup." in docker["human_check_reasons"]

    skipped = dispatcher_context.select_tool_records(
        {"tools": []},
        "unknown-workflow",
        [],
        intent_summary="",
        default_mode="local",
        default_purpose="workflow execution",
        candidate_limit=5,
    )
    assert skipped["status"] == "skipped"
    assert skipped["candidate_selection"]["candidate_count"] == 0

    low_confidence = dispatcher_context.select_tool_records(
        registry,
        "unknown-workflow",
        [],
        intent_summary="rare",
        default_mode="local",
        default_purpose="",
        candidate_limit=5,
    )
    assert low_confidence["status"] == "human-check-required"
    assert low_confidence["tools"] == []
    assert "confidence is too low" in low_confidence["human_check_reasons"][0]


def test_tool_candidate_boundary_paths_cover_exact_phrase_manual_and_missing_record(monkeypatch) -> None:
    registry = {
        "tools": [
            {
                "name": "gh",
                "aliases": ["github-cli"],
                "default_mode": "read-only",
                "purpose": "GitHub metadata lookup",
                "workflows": ["/docs-sync"],
                "keywords": ["github metadata"],
            }
        ]
    }

    exact_score, exact_reasons = dispatcher_context.tool_candidate_score(
        registry["tools"][0],
        "github-cli:read-only:metadata",
        "/docs-sync",
        "",
    )
    assert exact_score == 100
    assert exact_reasons == ["exact tool name / alias match"]

    phrase_score, phrase_reasons = dispatcher_context.tool_candidate_score(
        registry["tools"][0],
        "metadata lookup",
        "unknown-workflow",
        "",
    )
    assert phrase_score >= 20
    assert "query phrase appears in tool registry text" in phrase_reasons

    manual = dispatcher_context.select_tool_records(
        registry,
        "/docs-sync",
        ["gh:read-only:metadata lookup"],
        intent_summary="",
        default_mode="local",
        default_purpose="workflow execution",
        candidate_limit=5,
    )
    assert manual["selection_mode"] == "manual"
    assert manual["candidate_selection"]["candidates_by_input"]["gh:read-only:metadata lookup"][0]["selected"] is True

    monkeypatch.setattr(dispatcher_context, "find_tool_record", lambda registry, tool_name: {})
    missing_record = dispatcher_context.select_tool_records(
        registry,
        "/docs-sync",
        [],
        intent_summary="github metadata",
        default_mode="local",
        default_purpose="workflow execution",
        candidate_limit=5,
    )
    assert missing_record["status"] == "skipped"
    assert missing_record["tools"] == []

    manual_unmatched_candidate = dispatcher_context.select_tool_records(
        registry,
        "/docs-sync",
        ["unknown:read-only:metadata"],
        intent_summary="github metadata",
        default_mode="local",
        default_purpose="workflow execution",
        candidate_limit=5,
    )
    assert manual_unmatched_candidate["selection_mode"] == "manual"
    candidate = manual_unmatched_candidate["candidate_selection"]["candidates_by_input"]["unknown:read-only:metadata"][0]
    assert candidate["name"] == "gh"
    assert "selected" not in candidate


def test_context_builders_preserve_existing_files_and_add_environment_context(tmp_path: Path) -> None:
    path = tmp_path / "context.json"
    write_json(path, {"kept": True})

    assert dispatcher_context.write_unless_exists(path, {"kept": False}, force=False) == {"kept": True}
    assert dispatcher_context.write_unless_exists(path, {"kept": False}, force=True) == {"kept": False}
    write_json(path, ["not", "a", "dict"])
    assert dispatcher_context.write_unless_exists(path, {"rewritten": True}, force=False) == {"rewritten": True}

    plan = dispatcher_context.execution_plan_context(
        "issue-ctx",
        "docs-sync",
        required_contexts=["workflow-selection"],
        required_environment="web-svg",
        next_commands=[],
        stop_conditions=[],
    )

    assert plan["required_dispatcher_contexts"] == ["workflow-selection", "environment-selection"]
    assert plan["next_commands"] == ["/docs-sync"]
    assert plan["stop_conditions"]


def test_run_init_marks_human_check_and_force_rewrites_context(tmp_path: Path) -> None:
    write_json(tmp_path / "runtime" / "registries" / "workflow_help.json", {"commands": [], "extensions": []})
    context_path = tmp_path / "work" / "issue-ctx" / "context" / "workflow-selection.json"
    write_json(context_path, {"workflow": "stale"})

    result = dispatcher_context.run_init(
        make_args(
            tmp_path,
            workflow="/missing",
            required_environment="web-svg",
            force=True,
        )
    )

    rewritten = json.loads(context_path.read_text(encoding="utf-8"))
    plan = json.loads((tmp_path / "work" / "issue-ctx" / "context" / "execution-plan.json").read_text(encoding="utf-8"))
    assert result["status"] == "human-check-required"
    assert result["written"] == [
        "work/issue-ctx/context/workflow-selection.json",
        "work/issue-ctx/context/tool-selection.json",
        "work/issue-ctx/context/runtime-context.json",
        "work/issue-ctx/context/execution-plan.json",
    ]
    assert rewritten["workflow"] == "missing"
    assert rewritten["human_check_required"] is True
    assert "environment-selection" in plan["required_dispatcher_contexts"]


def test_parser_and_main_status_paths(monkeypatch, capsys) -> None:
    parser = dispatcher_context.build_parser()
    parsed = parser.parse_args(
        [
            "--repo-root",
            "repo",
            "init",
            "--work-id",
            "issue-1",
            "--workflow",
            "/docs-sync",
            "--tool",
            "gh:read-only:metadata",
            "--candidate-limit",
            "3",
            "--force",
        ]
    )
    assert parsed.work_id == "issue-1"
    assert parsed.tool == ["gh:read-only:metadata"]
    assert parsed.candidate_limit == 3
    assert parsed.force is True

    monkeypatch.setattr(dispatcher_context, "run_init", lambda args: {"status": "ready"})
    assert dispatcher_context.main(["init", "--work-id", "issue-1", "--workflow", "/docs-sync"]) == 0
    assert '"status": "ready"' in capsys.readouterr().out

    monkeypatch.setattr(dispatcher_context, "run_init", lambda args: {"status": "failed"})
    assert dispatcher_context.main(["init", "--work-id", "issue-1", "--workflow", "/docs-sync"]) == 1

    def raise_error(args: argparse.Namespace) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(dispatcher_context, "run_init", raise_error)
    assert dispatcher_context.main(["init", "--work-id", "issue-1", "--workflow", "/docs-sync"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err


def test_module_can_be_loaded_as_script_path_without_running_main() -> None:
    namespace = runpy.run_path(str(Path(dispatcher_context.__file__)))

    assert namespace["build_parser"]
