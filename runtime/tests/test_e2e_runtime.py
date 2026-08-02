from __future__ import annotations

import json
from pathlib import Path

from runtime.ctl import ctl
from runtime.testing import e2e_runtime


def write_minimal_template_registries(repo_root: Path) -> None:
    registry_dir = repo_root / "templates" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")
    (registry_dir / "tool_candidates.json").write_text('{"tools": []}', encoding="utf-8")
    (registry_dir / "human_gates.json").write_text('{"gates": []}', encoding="utf-8")
    (registry_dir / "workflow_environment_profiles.json").write_text(
        '{"environments": [], "profiles": [], "mappings": []}',
        encoding="utf-8",
    )


def create_ready_contract(
    repo_root: Path,
    work_id: str,
    *,
    test_kind: str = "e2e",
    trigger: str = 'python -c "print(\'ok\')"',
    stubs: list[str] | None = None,
) -> dict:
    return e2e_runtime.build_e2e_contract(
        repo_root,
        work_id=work_id,
        test_kind=test_kind,
        trigger=trigger,
        preconditions=["required inputs and stubs are prepared"],
        expected_route=["start -> execute command -> collect evidence"],
        expected_state_transitions=["pending -> running -> completed"],
        expected_side_effects=["no external side effect in local test"],
        observable_endpoints=["command stdout", "runtime evidence JSON"],
        timing_constraints=["command finishes within runtime timeout"],
        ordering_constraints=["plan and contract are created before readiness/run"],
        duplicate_handling="duplicate execution must not create conflicting evidence",
        retry_expectations=["rerun the same command after fixing blockers"],
        recovery_expectations=["use explain/loop evidence to decide the next fix"],
        required_stubs=stubs or [],
        failure_signals=["non-zero exit code", "missing evidence artifact"],
        evidence_requirements=["run-result.json", "observation.json", "verification.json"],
        human_review_points=["contract, execution result, and verification are reviewed"],
    )


def test_e2e_runtime_full_flow_counts_and_writes_artifacts(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-e2e"
    stub = repo_root / "work" / work_id / "stubs" / "api-response.json"
    stub.parent.mkdir(parents=True)
    stub.write_text('{"ok": true}\n', encoding="utf-8")

    plan = e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        objective="主要導線が完了できることを確認する。",
        scenarios=["ユーザーが登録から完了画面まで進む。"],
        expectations=["完了画面が表示される。"],
        required_stubs=["stubs/api-response.json"],
        commands=['python -c "print(\'e2e-ok\')"'],
    )
    contract = create_ready_contract(
        repo_root,
        work_id,
        trigger='python -c "print(\'e2e-ok\')"',
        stubs=["stubs/api-response.json"],
    )
    readiness = e2e_runtime.build_e2e_readiness(repo_root, work_id=work_id)
    run_result = e2e_runtime.build_e2e_run(repo_root, work_id=work_id, human_check="approved")
    observation = e2e_runtime.build_e2e_observation(repo_root, work_id=work_id)
    verification = e2e_runtime.build_e2e_verification(repo_root, work_id=work_id)
    explanation = e2e_runtime.build_e2e_explanation(repo_root, work_id=work_id)

    assert plan["artifact_type"] == "e2e-test-plan"
    assert contract["artifact_type"] == "e2e-test-contract"
    assert contract["status"] == "ready"
    assert readiness["status"] == "ready"
    assert run_result["status"] == "completed"
    assert run_result["command_results"][0]["exit_code"] == 0
    assert observation["observed_command_count"] == 1
    assert observation["failed_command_count"] == 0
    assert verification["status"] == "pass"
    assert verification["contract_status"] == "ready"
    assert verification["contract_evidence_requirement_count"] == 3
    assert any("e2e review-plan" in item for item in verification["next_actions"])
    assert explanation["status"] == "pass"
    assert (repo_root / "work" / work_id / "test-specifications" / "e2e-test-plan.json").exists()
    assert (repo_root / "work" / work_id / "test-specifications" / "e2e-test-contract.json").exists()
    assert (repo_root / "work" / work_id / "test-evidence" / "e2e-test" / "explanation.md").exists()


def test_e2e_review_plan_bridges_verification_to_review_council(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-e2e-review-plan"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        objective="Review E2E evidence before human final confirmation.",
        expectations=["verification evidence is available"],
        commands=["echo ok"],
    )
    create_ready_contract(repo_root, work_id, trigger="echo ok")
    e2e_runtime.build_e2e_run(repo_root, work_id=work_id, dry_run=True, human_check="approved")
    e2e_runtime.build_e2e_observation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_verification(repo_root, work_id=work_id)

    review_plan = e2e_runtime.build_e2e_review_plan(
        repo_root,
        work_id=work_id,
        review_id="review-e2e",
        changed_files=["src/app.py"],
    )

    assert review_plan["artifact_type"] == "e2e-test-review-plan"
    assert review_plan["status"] == "review-ready"
    assert review_plan["required_reviewers"] == [
        "ux",
        "accessibility",
        "frontend-architecture",
        "runtime-architecture",
    ]
    assert "work/issue-e2e-review-plan/test-evidence/e2e-test/verification.json" in review_plan["evidence_paths"]
    assert "--reviewer ux" in review_plan["review_plan_command"]
    assert "--reviewer runtime-architecture" in review_plan["review_plan_command"]
    assert "--changed-file src/app.py" in review_plan["review_plan_command"]
    assert "aiwfctl review evidence-gate" in review_plan["review_evidence_gate_command"]
    assert (repo_root / "work" / work_id / "test-evidence" / "e2e-test" / "review-plan.md").exists()


def test_e2e_coverage_reports_contract_and_evidence_completion(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-e2e-coverage"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        objective="Confirm coverage is visible before the final gate.",
        expectations=["run-result.json", "observation.json", "verification.json"],
        commands=["echo ok"],
    )
    create_ready_contract(repo_root, work_id, trigger="echo ok")
    e2e_runtime.build_e2e_run(repo_root, work_id=work_id, human_check="approved")
    e2e_runtime.build_e2e_observation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_verification(repo_root, work_id=work_id)

    coverage = e2e_runtime.build_e2e_coverage(repo_root, work_id=work_id)

    assert coverage["artifact_type"] == "e2e-coverage"
    assert coverage["status"] == "pass"
    assert coverage["missing_contract_fields"] == []
    assert all(item["exists"] for item in coverage["evidence_coverage"] if item["required"])
    assert all(item["covered"] for item in coverage["evidence_requirement_coverage"])
    assert (repo_root / "work" / work_id / "test-evidence" / "e2e-test" / "coverage.md").exists()


def test_e2e_final_gate_records_human_approval_after_review(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-e2e-final-gate"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        objective="Confirm final human gate is recorded after review.",
        expectations=["run-result.json", "observation.json", "verification.json"],
        commands=["echo ok"],
    )
    create_ready_contract(repo_root, work_id, trigger="echo ok")
    e2e_runtime.build_e2e_run(repo_root, work_id=work_id, human_check="approved")
    e2e_runtime.build_e2e_observation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_verification(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_review_plan(repo_root, work_id=work_id, review_id="review-final")
    e2e_runtime.build_e2e_coverage(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_explanation(repo_root, work_id=work_id)

    final_gate = e2e_runtime.build_e2e_final_gate(
        repo_root,
        work_id=work_id,
        human_decision="approved",
        reviewer="Human",
        note="Evidence and Review Council bridge were checked.",
    )

    assert final_gate["artifact_type"] == "e2e-human-final-gate"
    assert final_gate["status"] == "pass"
    assert final_gate["human_decision"] == "approved"
    assert final_gate["approved_at"]
    assert final_gate["decision_inputs"]["review_plan"] == f"work/{work_id}/test-evidence/e2e-test/review-plan.json"
    assert (repo_root / "work" / work_id / "test-evidence" / "e2e-test" / "human-final-gate.md").exists()


def test_e2e_final_gate_guides_missing_prerequisite_commands(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-e2e-final-guidance"
    e2e_runtime.build_e2e_plan(repo_root, work_id=work_id, commands=["echo ok"])
    create_ready_contract(repo_root, work_id, trigger="echo ok")

    final_gate = e2e_runtime.build_e2e_final_gate(
        repo_root,
        work_id=work_id,
        human_decision="approved",
        reviewer="Human",
    )

    assert final_gate["status"] == "blocked"
    assert "verification evidence is missing." in final_gate["blockers"]
    assert "review-plan evidence is missing." in final_gate["blockers"]
    assert "explanation evidence is missing." in final_gate["blockers"]
    assert any("e2e verify" in item for item in final_gate["next_actions"])
    assert any("e2e review-plan" in item for item in final_gate["next_actions"])
    assert any("e2e explain" in item for item in final_gate["next_actions"])


def test_e2e_evidence_package_summarizes_artifacts_for_handoff(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-e2e-package"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        objective="Package E2E evidence for handoff.",
        expectations=["run-result.json", "observation.json", "verification.json"],
        commands=["echo ok"],
    )
    create_ready_contract(repo_root, work_id, trigger="echo ok")
    e2e_runtime.build_e2e_run(repo_root, work_id=work_id, human_check="approved")
    e2e_runtime.build_e2e_observation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_verification(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_review_plan(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_coverage(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_explanation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_final_gate(
        repo_root,
        work_id=work_id,
        human_decision="approved",
        reviewer="Human",
    )

    package = e2e_runtime.build_e2e_evidence_package(repo_root, work_id=work_id)

    assert package["artifact_type"] == "e2e-evidence-package"
    assert package["status"] == "pass"
    assert package["release_ready"] is True
    assert package["loop_status"] == "missing"
    assert "work/issue-e2e-package/test-evidence/e2e-test/human-final-gate.json" in package["evidence_paths"]
    assert any(item["phase"] == "coverage" and item["status"] == "pass" for item in package["artifact_statuses"])
    assert (repo_root / "work" / work_id / "test-evidence" / "e2e-test" / "evidence-package.md").exists()


def test_e2e_evidence_package_links_trace_and_detects_unresolved_loop(tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-e2e-package-loop"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        expectations=["run-result.json", "observation.json", "verification.json"],
        commands=["echo ok"],
    )
    create_ready_contract(repo_root, work_id, trigger="echo ok")
    e2e_runtime.build_e2e_run(repo_root, work_id=work_id, human_check="approved")
    e2e_runtime.build_e2e_observation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_verification(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_review_plan(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_coverage(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_explanation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_final_gate(
        repo_root,
        work_id=work_id,
        human_decision="approved",
        reviewer="Human",
    )
    e2e_runtime.build_e2e_loop(
        repo_root,
        work_id=work_id,
        problems=["open issue remains"],
    )

    package = e2e_runtime.build_e2e_evidence_package(
        repo_root,
        work_id=work_id,
        trace_id="trace-package",
        output=f"docs/evidence/{work_id}/e2e-package.json",
    )

    assert package["status"] == "blocked"
    assert package["release_ready"] is False
    assert package["trace_id"] == "trace-package"
    assert package["runtime_links"]["log_export_command"].endswith(
        f"--output work/{work_id}/test-evidence/e2e-test/runtime-log-export.json"
    )
    assert package["output_path"] == f"docs/evidence/{work_id}/e2e-package.json"
    assert (repo_root / "docs" / "evidence" / work_id / "e2e-package.json").exists()
    assert any("unresolved loop status" in item for item in package["blockers"])


def test_e2e_runtime_run_requires_human_check_before_execution(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-e2e-human-check"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        objective="Human Checkなしでは実行しない。",
        commands=['python -c "print(\'should-not-run\')"'],
    )
    create_ready_contract(repo_root, work_id, trigger='python -c "print(\'should-not-run\')"')

    result = e2e_runtime.build_e2e_run(repo_root, work_id=work_id)

    assert result["status"] == "blocked"
    assert result["command_results"] == []
    assert any("--human-check approved" in item for item in result["blockers"])
    saved = json.loads(
        (repo_root / "work" / work_id / "test-evidence" / "e2e-test" / "run-result.json").read_text(
            encoding="utf-8"
        )
    )
    assert saved["status"] == "blocked"

    monkeypatch.setattr(
        e2e_runtime,
        "execute_command",
        lambda command, cwd: (_ for _ in ()).throw(AssertionError("dry-run must not execute commands")),
    )
    dry_run = e2e_runtime.build_e2e_run(repo_root, work_id=work_id, dry_run=True, human_check="approved")

    assert dry_run["status"] == "dry-run"
    assert dry_run["command_results"] == []


def test_e2e_runtime_reports_missing_plan_and_stub_readiness(tmp_path: Path) -> None:
    missing = e2e_runtime.build_e2e_readiness(tmp_path, work_id="missing-plan")

    assert missing["status"] == "blocked"
    assert any("e2e-test-plan.json" in item for item in missing["blockers"])

    work_id = "issue-missing-stub"
    e2e_runtime.build_e2e_plan(
        tmp_path,
        work_id=work_id,
        objective="Stub不足を検出する。",
        required_stubs=["stubs/missing.json"],
        commands=['python -c "print(\'ok\')"'],
    )
    e2e_runtime.build_e2e_contract(
        tmp_path,
        work_id=work_id,
        trigger='python -c "print(\'ok\')"',
        preconditions=["input prepared"],
        expected_route=["start -> command"],
        expected_state_transitions=["pending -> completed"],
        expected_side_effects=["none"],
        observable_endpoints=["stdout"],
        timing_constraints=["within timeout"],
        ordering_constraints=["readiness before run"],
        duplicate_handling="no duplicate side effects",
        retry_expectations=["rerun after stub is added"],
        recovery_expectations=["add missing stub and rerun readiness"],
        required_stubs=["stubs/missing.json"],
        failure_signals=["missing stub"],
        evidence_requirements=["readiness.json"],
        human_review_points=["stub readiness reviewed"],
    )
    result = e2e_runtime.build_e2e_readiness(tmp_path, work_id=work_id)

    assert result["status"] == "blocked"
    assert result["stub_checks"][0]["exists"] is False
    assert any("required stub missing" in item for item in result["blockers"])


def test_e2e_contract_requires_all_verification_fields(tmp_path: Path) -> None:
    work_id = "issue-contract-gaps"
    e2e_runtime.build_e2e_plan(
        tmp_path,
        work_id=work_id,
        objective="Ensure a contract is fixed before E2E execution.",
        commands=['python -c "print(\'ok\')"'],
    )

    contract = e2e_runtime.build_e2e_contract(tmp_path, work_id=work_id)
    readiness = e2e_runtime.build_e2e_readiness(tmp_path, work_id=work_id)

    assert contract["status"] == "draft-with-gaps"
    assert "expected_route" in contract["missing_contract_fields"]
    assert "duplicate_handling" in contract["missing_contract_fields"]
    assert readiness["status"] == "blocked"
    assert any("test contract field missing" in item for item in readiness["blockers"])


def test_e2e_contract_scaffold_writes_draft_and_protects_existing(tmp_path: Path) -> None:
    work_id = "issue-contract-scaffold"
    e2e_runtime.build_e2e_plan(
        tmp_path,
        work_id=work_id,
        objective="Create an editable E2E contract scaffold.",
        expectations=["run-result evidence is reviewable"],
        commands=["echo ok"],
    )

    scaffold = e2e_runtime.build_e2e_contract_scaffold(tmp_path, work_id=work_id)
    protected = e2e_runtime.build_e2e_contract_scaffold(tmp_path, work_id=work_id)

    assert scaffold["artifact_type"] == "e2e-test-contract"
    assert scaffold["status"] == "draft-with-gaps"
    assert scaffold["scaffold"] is True
    assert scaffold["test_contract"]["objective"] == "Create an editable E2E contract scaffold."
    assert scaffold["test_contract"]["trigger"] == "echo ok"
    assert "expected_route" in scaffold["missing_contract_fields"]
    assert protected["status"] == "blocked"
    assert "already exists" in protected["blockers"][0]
    assert (tmp_path / "work" / work_id / "test-specifications" / "e2e-test-contract.md").exists()


def test_e2e_readiness_reports_contract_plan_consistency(tmp_path: Path) -> None:
    work_id = "issue-contract-consistency"
    e2e_runtime.build_e2e_plan(
        tmp_path,
        work_id=work_id,
        objective="Run a UI E2E route.",
        commands=["pytest runtime/tests/test_unit.py"],
    )
    e2e_runtime.build_e2e_contract(
        tmp_path,
        work_id=work_id,
        objective="Run a UI E2E route.",
        trigger="npm run e2e",
        preconditions=["app is started"],
        expected_route=["user opens UI and completes a screen flow"],
        expected_state_transitions=["pending -> completed"],
        expected_side_effects=["none"],
        observable_endpoints=["UI screen"],
        timing_constraints=["within timeout"],
        ordering_constraints=["contract before readiness"],
        duplicate_handling="idempotent",
        retry_expectations=["rerun after fix"],
        recovery_expectations=["use loop evidence"],
        failure_signals=["non-zero exit code"],
        evidence_requirements=["run-result.json"],
        human_review_points=["verify UI route evidence"],
    )

    readiness = e2e_runtime.build_e2e_readiness(tmp_path, work_id=work_id)

    assert readiness["status"] == "blocked"
    assert readiness["contract_consistency_status"] == "blocker"
    assert any(item["name"] == "trigger_command_alignment" for item in readiness["contract_consistency_checks"])
    assert any("not included in plan.commands" in item for item in readiness["blockers"])
    assert any("UI/browser observability" in item for item in readiness["warnings"])


def test_aiwfctl_e2e_command_routes_and_writes_json(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    write_minimal_template_registries(repo_root)
    work_id = "issue-e2e-cli"

    plan_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "e2e",
            "plan",
            "--work-id",
            work_id,
            "--test-kind",
            "integration",
            "--objective",
            "結合試験を証跡化する。",
            "--scenario",
            "APIからUIまでの疎通を確認する。",
            "--expectation",
            "終了コード0で完了する。",
            "--run-command",
            'python -c "print(\'integration-ok\')"',
            "--json",
        ]
    )
    plan_code, plan_output = ctl.run(plan_args)

    assert plan_code == 0
    plan = json.loads(plan_output)
    assert plan["artifact_type"] == "integration-test-plan"
    assert plan["artifacts"]["plan_json"] == f"work/{work_id}/test-specifications/integration-test-plan.json"

    contract_args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "e2e",
            "contract",
            "--work-id",
            work_id,
            "--test-kind",
            "integration",
            "--trigger",
            'python -c "print(\'integration-ok\')"',
            "--precondition",
            "inputs prepared",
            "--expected-route",
            "api -> ui",
            "--expected-state-transition",
            "pending -> completed",
            "--expected-side-effect",
            "none",
            "--observable-endpoint",
            "stdout",
            "--timing-constraint",
            "within timeout",
            "--ordering-constraint",
            "plan before readiness",
            "--duplicate-handling",
            "idempotent evidence overwrite",
            "--retry-expectation",
            "rerun after fix",
            "--recovery-expectation",
            "use loop evidence",
            "--failure-signal",
            "non-zero exit code",
            "--evidence-requirement",
            "run-result.json",
            "--human-review-point",
            "contract reviewed",
            "--json",
        ]
    )
    contract_code, contract_output = ctl.run(contract_args)

    assert contract_code == 0
    contract = json.loads(contract_output)
    assert contract["artifact_type"] == "integration-test-contract"
    assert contract["status"] == "ready"
    assert contract["artifacts"]["contract_json"] == f"work/{work_id}/test-specifications/integration-test-contract.json"

    dry_run_args = ctl.build_parser().parse_args(
        ["--repo-root", str(repo_root), "e2e", "run", "--work-id", work_id, "--test-kind", "integration", "--dry-run", "--json"]
    )
    run_code, run_output = ctl.run(dry_run_args)

    assert run_code == 0
    run_result = json.loads(run_output)
    assert run_result["status"] == "dry-run"
    assert run_result["artifacts"]["run_result_json"] == f"work/{work_id}/test-evidence/integration-test/run-result.json"


def test_aiwfctl_e2e_review_plan_routes_review_council_bridge(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    write_minimal_template_registries(repo_root)
    work_id = "issue-e2e-review-cli"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        commands=["echo ok"],
    )
    create_ready_contract(repo_root, work_id, trigger="echo ok")
    e2e_runtime.build_e2e_run(repo_root, work_id=work_id, dry_run=True, human_check="approved")
    e2e_runtime.build_e2e_observation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_verification(repo_root, work_id=work_id)
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "e2e",
            "review-plan",
            "--work-id",
            work_id,
            "--review-id",
            "review-cli",
            "--reviewer",
            "accessibility",
            "--changed-file",
            "src/app.py",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["artifact_type"] == "e2e-test-review-plan"
    assert result["status"] == "review-ready"
    assert result["required_reviewers"] == ["accessibility"]
    assert "--review-id review-cli" in result["review_plan_command"]
    assert result["artifacts"]["review_plan_json"] == f"work/{work_id}/test-evidence/e2e-test/review-plan.json"


def test_aiwfctl_e2e_final_gate_routes_human_decision(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    write_minimal_template_registries(repo_root)
    work_id = "issue-e2e-final-cli"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        commands=["echo ok"],
        expectations=["run-result.json", "observation.json", "verification.json"],
    )
    create_ready_contract(repo_root, work_id, trigger="echo ok")
    e2e_runtime.build_e2e_run(repo_root, work_id=work_id, human_check="approved")
    e2e_runtime.build_e2e_observation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_verification(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_review_plan(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_explanation(repo_root, work_id=work_id)
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "e2e",
            "final-gate",
            "--work-id",
            work_id,
            "--human-decision",
            "approved",
            "--reviewer",
            "Human",
            "--decision-reason",
            "reviewed evidence",
            "--review-reference",
            "review-cli",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["artifact_type"] == "e2e-human-final-gate"
    assert result["status"] == "pass"
    assert result["decision_reason"] == "reviewed evidence"
    assert result["review_reference"] == "review-cli"
    assert result["artifacts"]["human_final_gate_json"] == f"work/{work_id}/test-evidence/e2e-test/human-final-gate.json"


def test_aiwfctl_e2e_evidence_package_routes_handoff_bundle(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    write_minimal_template_registries(repo_root)
    work_id = "issue-e2e-package-cli"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        commands=["echo ok"],
        expectations=["run-result.json", "observation.json", "verification.json"],
    )
    create_ready_contract(repo_root, work_id, trigger="echo ok")
    e2e_runtime.build_e2e_run(repo_root, work_id=work_id, human_check="approved")
    e2e_runtime.build_e2e_observation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_verification(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_review_plan(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_coverage(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_explanation(repo_root, work_id=work_id)
    e2e_runtime.build_e2e_final_gate(
        repo_root,
        work_id=work_id,
        human_decision="approved",
        reviewer="Human",
    )
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "e2e",
            "evidence-package",
            "--work-id",
            work_id,
            "--trace-id",
            "trace-cli",
            "--output",
            f"docs/evidence/{work_id}/package.json",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    result = json.loads(output)
    assert result["artifact_type"] == "e2e-evidence-package"
    assert result["release_ready"] is True
    assert result["runtime_links"]["trace_show_command"] == "aiwfctl trace show trace-cli --problems"
    assert result["output_path"] == f"docs/evidence/{work_id}/package.json"
    assert result["artifacts"]["evidence_package_json"] == f"work/{work_id}/test-evidence/e2e-test/evidence-package.json"


def test_e2e_loop_bundles_problem_fix_review_scm_and_retest(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path
    work_id = "issue-e2e-loop"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        objective="失敗時の修正ループを作る。",
        expectations=["終了コード0で完了する。"],
        commands=["run failing e2e"],
    )
    create_ready_contract(repo_root, work_id, trigger="run failing e2e")
    monkeypatch.setattr(
        e2e_runtime,
        "execute_command",
        lambda command, cwd: {"command": command, "exit_code": 1, "stdout": "", "stderr": "assertion failed"},
    )
    run_result = e2e_runtime.build_e2e_run(repo_root, work_id=work_id, human_check="approved")

    loop = e2e_runtime.build_e2e_loop(
        repo_root,
        work_id=work_id,
        trace_id="trace-loop",
        review_id="review-loop",
        issue_number="5",
        fix_summary="失敗したE2E導線を修正する。",
        fix_commands=["aiwfctl scm compare --work-id issue-e2e-loop"],
        reviewers=["frontend-architecture"],
        changed_files=["src/app.py"],
    )

    assert run_result["status"] == "failed"
    assert loop["artifact_type"] == "e2e-test-loop"
    assert loop["status"] == "fix-required"
    assert loop["problem_count"] >= 1
    assert any(item["source"] == "run-result" for item in loop["problems"])
    assert loop["integration_points"]["trace_id"] == "trace-loop"
    assert "aiwfctl trace show trace-loop --problems" in loop["next_actions"]
    assert "aiwfctl review plan" in loop["integration_points"]["review_plan_command"]
    assert "--review-id review-loop" in loop["integration_points"]["review_plan_command"]
    assert "--changed-file src/app.py" in loop["integration_points"]["review_plan_command"]
    assert any("aiwfctl scm commit" in item and "--dry-run" in item for item in loop["next_actions"])
    assert loop["retest_commands"][-1] == "aiwfctl e2e loop --work-id issue-e2e-loop --test-kind e2e"
    assert (repo_root / "work" / work_id / "test-evidence" / "e2e-test" / "loop.md").exists()


def test_aiwfctl_e2e_loop_routes_explicit_problem(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    write_minimal_template_registries(repo_root)
    work_id = "issue-e2e-loop-cli"
    e2e_runtime.build_e2e_plan(
        repo_root,
        work_id=work_id,
        objective="CLIからloopを作る。",
        commands=['python -c "print(\'ok\')"'],
    )
    create_ready_contract(repo_root, work_id, trigger='python -c "print(\'ok\')"')
    args = ctl.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "e2e",
            "loop",
            "--work-id",
            work_id,
            "--problem",
            "期待結果が未確認",
            "--fix-summary",
            "未確認の期待結果を再確認する。",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 2
    result = json.loads(output)
    assert result["artifact_type"] == "e2e-test-loop"
    assert result["status"] == "fix-required"
    assert result["problem_count"] >= 1
    assert result["artifacts"]["loop_json"] == f"work/{work_id}/test-evidence/e2e-test/loop.json"
