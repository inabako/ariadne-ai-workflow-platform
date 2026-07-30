from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from runtime.ctl import ctl
from runtime.review.graph import build_langgraph_review_plan
from runtime.review.graph import langgraph_adapter
from runtime.review import council


def start_args(tmp_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        repo_root=str(tmp_path),
        work_id="issue-1",
        review_id="review-test",
        target="runtime review council",
        target_revision="abc123",
        intent="route specialist review findings through a common runtime gate",
        requirement=["review output must be structured"],
        changed_file=["runtime/review/council.py"],
        guardrail=["reviewers do not mutate source"],
        evidence=["work/issue-1/process-report/specialist-review-security.md"],
        scope=["runtime/review"],
        known_constraint=["LangGraph orchestration is out of MVP scope"],
        reviewer=["security", "runtime"],
    )


def test_start_review_freezes_packet_and_writes_artifacts(tmp_path: Path) -> None:
    result = council.start_review(start_args(tmp_path))

    assert result["status"] == "packet-frozen"
    assert result["review_id"] == "review-test"
    assert result["packet"]["required_reviewers"] == ["security", "runtime"]
    assert len(result["packet_hash"]) == 64
    assert (tmp_path / result["artifacts"]["session"]).exists()
    assert (tmp_path / result["artifacts"]["index"]).exists()
    assert (tmp_path / result["artifacts"]["report"]).exists()


def test_plan_review_selects_specialists_and_writes_plan_artifacts(tmp_path: Path) -> None:
    result = council.plan_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            work_id="issue-plan",
            review_id="review-plan",
            target="runtime review council",
            target_revision="abc123",
            intent="strengthen runtime logging authentication test verification",
            requirement=["reviewer selection must be explainable"],
            changed_file=["runtime/review/council.py"],
            guardrail=["reviewers do not mutate source"],
            evidence=["logs/runtime/runtime-events.log"],
            scope=["runtime/review"],
            known_constraint=[],
            reviewer=[],
        )
    )

    assert result["status"] == "planned"
    assert {"runtime", "security", "observability", "testing"}.issubset(set(result["required_reviewers"]))
    assert result["start_command"].startswith("aiwfctl review start")
    assert "--changed-file" in result["start_command"]
    assert (tmp_path / result["artifacts"]["plan_json"]).exists()
    assert (tmp_path / result["artifacts"]["plan_report"]).exists()


def test_handoff_review_writes_per_reviewer_packets(tmp_path: Path) -> None:
    council.start_review(start_args(tmp_path))

    result = council.handoff_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            reviewer=[],
        )
    )
    status = council.status_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="")
    )

    assert result["status"] == "handoff-ready"
    assert set(result["reviewers"]) == {"security", "runtime"}
    assert status["status"] == "handoff-ready"
    assert len(status["reviewer_handoffs"]) == 2
    for path in result["reviewer_handoffs"]:
        text = (tmp_path / path).read_text(encoding="utf-8")
        assert "aiwfctl review add-finding" in text
        assert "Review Council Handoff" in text


def test_orchestrate_review_waits_for_missing_reviewer(tmp_path: Path) -> None:
    council.start_review(start_args(tmp_path))
    council.handoff_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            reviewer=[],
        )
    )
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="info",
            claim="security review has no blocking issue",
            verdict="pass",
            evidence_ref=[],
            counterexample="",
            reasoning_summary="reviewed",
            requested_action="",
            confidence=0.8,
            required_test=[],
            blocking=False,
            non_blocking=True,
        )
    )

    result = council.orchestrate_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="", run_id="orc-test")
    )
    status = council.status_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="")
    )

    assert result["status"] == "orchestration-waiting"
    assert result["checks"]["missing_reviewers"] == ["runtime"]
    assert any(item["action"] == "register-specialist-finding" for item in result["next_actions"])
    assert (tmp_path / result["artifacts"]["orchestration_json"]).exists()
    assert status["status"] == "orchestration-waiting"


def test_next_action_prefers_specialist_run_for_missing_reviewer(tmp_path: Path) -> None:
    council.start_review(start_args(tmp_path))
    council.handoff_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            reviewer=[],
        )
    )
    council.orchestrate_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="", run_id="orc-next")
    )

    result = council.next_action_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="")
    )

    assert result["status"] == "action-required"
    assert result["selected_action"]["action"] == "register-specialist-finding"
    assert "aiwfctl review run-specialist" in result["selected_action"]["agent_command"]


def test_run_specialist_review_writes_agent_packet(tmp_path: Path) -> None:
    prompt = tmp_path / ".ariadne" / "agents" / "security-reviewer-agent.prompt.md"
    prompt.parent.mkdir(parents=True)
    prompt.write_text("# Security Reviewer Agent\n", encoding="utf-8")
    council.start_review(start_args(tmp_path))

    result = council.run_specialist_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            reviewer="security",
        )
    )
    status = council.status_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="")
    )

    assert result["status"] == "ready"
    assert result["agent_id"] == "security-reviewer-agent"
    assert result["prompt_exists"] is True
    assert result["handoff_path"].endswith("reviewer-packet-security.md")
    assert "aiwfctl review add-finding" in result["required_output"]["finding_registration_command"]
    assert (tmp_path / result["artifacts"]["specialist_run_json"]).exists()
    assert status["status"] == "specialist-ready"


def test_execute_specialist_review_requires_human_check(tmp_path: Path) -> None:
    prompt = tmp_path / ".ariadne" / "agents" / "security-reviewer-agent.prompt.md"
    prompt.parent.mkdir(parents=True)
    prompt.write_text("# Security Reviewer Agent\n", encoding="utf-8")
    council.start_review(start_args(tmp_path))

    result = council.execute_specialist_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            reviewer="security",
            agent_command="fake-agent --packet {packet_report_q}",
            timeout_seconds=30,
            human_check="pending",
            skip_draft_findings=False,
        )
    )

    assert result["artifact_type"] == "review-council-specialist-execution"
    assert result["status"] == "human-check-required"
    assert result["human_check_required"] is True
    assert result["reason"] == "specialist_agent_execution_requires_human_check"
    assert (tmp_path / result["artifacts"]["specialist_execution_json"]).exists()


def test_execute_specialist_review_runs_command_and_drafts_findings(monkeypatch, tmp_path: Path) -> None:
    prompt = tmp_path / ".ariadne" / "agents" / "security-reviewer-agent.prompt.md"
    prompt.parent.mkdir(parents=True)
    prompt.write_text("# Security Reviewer Agent\n", encoding="utf-8")
    council.start_review(start_args(tmp_path))
    calls: list[dict[str, object]] = []

    def fake_run(command: str, **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append({"command": command, **kwargs})
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="\n".join(
                [
                    "# Security Review",
                    "",
                    "## Finding 1",
                    "Severity: medium",
                    "Verdict: needs-qa",
                    "Category: security",
                    "Claim: execution report requires human review",
                    "Evidence: work/issue-1/process-report/specialist-review-security.md",
                    "Required Test: specialist executor captures stdout",
                    "Requested Action: confirm specialist output",
                ]
            ),
            stderr="",
        )

    monkeypatch.setattr(council.subprocess, "run", fake_run)

    result = council.execute_specialist_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            reviewer="security",
            agent_command="fake-agent --packet {packet_report_q} --output {output_q}",
            timeout_seconds=30,
            human_check="approved",
            skip_draft_findings=False,
        )
    )
    session = council.inspect_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="")
    )

    assert result["status"] == "completed"
    assert result["exit_code"] == 0
    assert result["report_exists"] is True
    assert result["draft_findings"]["draft_count"] == 1
    assert (tmp_path / result["output_path"]).exists()
    assert (tmp_path / result["artifacts"]["stdout"]).read_text(encoding="utf-8").startswith("# Security Review")
    assert calls[0]["shell"] is True
    assert "Review Council Specialist Run" in str(calls[0]["input"])
    assert session["specialist_executions"][0]["status"] == "completed"
    assert session["finding_drafts"][0]["draft_count"] == 1


def test_draft_findings_extracts_structured_report_and_commands(tmp_path: Path) -> None:
    report = tmp_path / "work" / "issue-1" / "process-report" / "specialist-review-security.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "\n".join(
            [
                "# Security Review",
                "",
                "## Finding 1",
                "Severity: high",
                "Verdict: changes-required",
                "Category: security",
                "Claim: authorization evidence is missing",
                "Evidence: work/issue-1/process-report/specialist-review-security.md",
                "Required Test: authorization denial test",
                "Requested Action: add authorization evidence",
            ]
        ),
        encoding="utf-8",
    )
    council.start_review(start_args(tmp_path))

    result = council.draft_findings_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            reviewer="security",
            report="work/issue-1/process-report/specialist-review-security.md",
            category="other",
            severity="medium",
            verdict="needs-qa",
        )
    )
    status = council.status_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="")
    )

    assert result["artifact_type"] == "review-council-finding-draft"
    assert result["draft_count"] == 1
    draft = result["drafts"][0]
    assert draft["draft_id"] == "DFT-001"
    assert draft["severity"] == "high"
    assert draft["verdict"] == "changes-required"
    assert draft["blocking"] is True
    assert draft["evidence_refs"] == ["work/issue-1/process-report/specialist-review-security.md"]
    assert draft["required_tests"] == ["authorization denial test"]
    assert "aiwfctl review add-finding" in draft["registration_command"]
    assert "--blocking" in draft["registration_command"]
    assert (tmp_path / result["artifacts"]["finding_draft_json"]).exists()
    assert (tmp_path / result["artifacts"]["finding_draft_report"]).exists()
    assert status["status"] == "finding-draft-ready"
    assert status["finding_draft_count"] == 1


def test_orchestrate_review_routes_reinspection_for_blocking_issue(tmp_path: Path) -> None:
    args = start_args(tmp_path)
    args.reviewer = ["security"]
    args.evidence = []
    council.start_review(args)
    council.handoff_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            reviewer=[],
        )
    )
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="high",
            claim="authorization evidence is missing",
            verdict="changes-required",
            evidence_ref=[],
            counterexample="",
            reasoning_summary="missing evidence",
            requested_action="add evidence",
            confidence=0.9,
            required_test=[],
            blocking=False,
            non_blocking=False,
        )
    )

    result = council.orchestrate_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="", run_id="orc-blocked")
    )

    assert result["status"] == "orchestration-blocked"
    assert result["checks"]["open_review_issue_ids"] == ["RI-001"]
    assert any(item["action"] == "reinspect-review-issue" for item in result["next_actions"])
    assert any(item["node"] == "reinspection" and item["status"] == "ready" for item in result["node_results"])


def test_summary_review_exports_snapshot_and_next_actions(tmp_path: Path) -> None:
    args = start_args(tmp_path)
    args.reviewer = ["security"]
    args.evidence = []
    council.start_review(args)
    council.handoff_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            reviewer=[],
        )
    )
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="high",
            claim="authorization evidence is missing",
            verdict="changes-required",
            evidence_ref=[],
            counterexample="",
            reasoning_summary="missing evidence",
            requested_action="add evidence",
            confidence=0.9,
            required_test=[],
            blocking=False,
            non_blocking=False,
        )
    )
    council.orchestrate_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="", run_id="orc-summary")
    )

    result = council.summary_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            summary_id="summary-test",
        )
    )
    session = council.inspect_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="")
    )

    assert result["artifact_type"] == "review-council-summary"
    assert result["summary_id"] == "summary-test"
    assert result["snapshot"]["finding_count"] == 1
    assert result["snapshot"]["open_issue_count"] == 1
    assert result["snapshot"]["blocking_issue_count"] == 1
    assert result["reviewers"][0]["state"] == "completed"
    assert result["issues"][0]["issue_id"] == "RI-001"
    assert result["selected_action"]["action"] == "reinspect-review-issue"
    assert (tmp_path / result["artifacts"]["summary_json"]).exists()
    report = tmp_path / result["artifacts"]["summary_report"]
    assert report.exists()
    assert "Ariadne Review Council Summary" in report.read_text(encoding="utf-8")
    assert session["review_summaries"][0]["summary_id"] == "summary-test"
    assert session["status"] == "orchestration-blocked"


def test_human_gate_review_records_blocked_and_approved_decisions(tmp_path: Path) -> None:
    council.start_review(start_args(tmp_path))
    council.summary_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            summary_id="summary-human-gate",
        )
    )

    blocked = council.human_gate_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            gate="review-council-final-verdict",
            human_check="pending",
            reviewer="Human",
            reason="not reviewed yet",
        )
    )
    approved = council.human_gate_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            gate="review-council-final-verdict",
            human_check="approved",
            reviewer="Human",
            reason="summary reviewed",
        )
    )
    status = council.status_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="")
    )

    assert blocked["status"] == "blocked"
    assert blocked["gate_restart"]["repair_available"] is True
    assert "--human-check approved" in blocked["repair_command"]
    assert approved["status"] == "approved"
    assert approved["summary_artifacts"]["summary_json"].endswith("summary-human-gate.json")
    assert (tmp_path / approved["artifacts"]["human_gate_json"]).exists()
    assert (tmp_path / approved["artifacts"]["human_gate_report"]).exists()
    assert status["human_gate_count"] == 2
    assert status["human_check"] == "approved"


def test_human_gate_risk_acceptance_feeds_approved_with_risk_verdict(tmp_path: Path) -> None:
    council.start_review(start_args(tmp_path))
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="low",
            claim="audit trail wording could be clearer",
            verdict="warn",
            evidence_ref=["work/issue-1/test-evidence/runtime.md"],
            counterexample="",
            reasoning_summary="minor risk remains",
            requested_action="accept or clarify",
            confidence=0.8,
            required_test=[],
            blocking=False,
            non_blocking=True,
        )
    )
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="runtime",
            category="runtime",
            severity="info",
            claim="runtime found no blocking issue",
            verdict="pass",
            evidence_ref=["work/issue-1/test-evidence/runtime.md"],
            counterexample="",
            reasoning_summary="reviewed",
            requested_action="",
            confidence=0.8,
            required_test=[],
            blocking=False,
            non_blocking=True,
        )
    )
    pending = council.decide_verdict(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence_verified=True,
            challenge_completed=True,
            target_revision_consistent=True,
            human_check="pending",
        )
    )
    council.human_gate_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            gate="review-council-risk-acceptance",
            human_check="approved",
            reviewer="Human",
            reason="non-blocking risk accepted",
        )
    )
    approved = council.decide_verdict(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence_verified=True,
            challenge_completed=True,
            target_revision_consistent=True,
            human_check="pending",
        )
    )

    assert pending["verdict"] == "HUMAN_DECISION_REQUIRED"
    assert approved["verdict"] == "APPROVED_WITH_RISK"
    assert approved["human_check"] == "approved"


def test_challenge_review_generates_counterexample_plan_for_open_issues(tmp_path: Path) -> None:
    args = start_args(tmp_path)
    args.reviewer = ["security"]
    args.evidence = []
    council.start_review(args)
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="high",
            claim="authorization evidence is missing",
            verdict="changes-required",
            evidence_ref=[],
            counterexample="",
            reasoning_summary="missing evidence",
            requested_action="add evidence",
            confidence=0.9,
            required_test=[],
            blocking=False,
            non_blocking=False,
        )
    )

    result = council.challenge_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            challenge_id="",
            challenger="runtime-quality",
            mode="counterexample-check",
            issue_id=[],
            counterexample_found=False,
            summary="reviewed open issues",
            evidence_ref=[],
        )
    )

    assert result["target_issue_ids"] == ["RI-001"]
    assert result["finding_ids"] == ["FND-001"]
    assert result["challenge_plan"]["counterexample_checks"][0]["issue_id"] == "RI-001"


def test_reinspection_records_issue_linkage_and_evidence_results(tmp_path: Path) -> None:
    args = start_args(tmp_path)
    args.reviewer = ["security"]
    args.evidence = []
    evidence = tmp_path / "work" / "issue-1" / "process-report" / "fix-evidence.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("# Fix Evidence\n", encoding="utf-8")
    council.start_review(args)
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="high",
            claim="authorization evidence is missing",
            verdict="changes-required",
            evidence_ref=[],
            counterexample="",
            reasoning_summary="missing evidence",
            requested_action="add evidence",
            confidence=0.9,
            required_test=[],
            blocking=False,
            non_blocking=False,
        )
    )

    result = council.reinspect_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id=["FND-001"],
            status="verified",
            reviewer="security",
            summary="evidence added",
            evidence_ref=["work/issue-1/process-report/fix-evidence.md"],
        )
    )

    assert result["issue_ids"] == ["RI-001"]
    assert result["previous_statuses"] == {"FND-001": "open"}
    assert result["evidence_results"][0]["exists"] is True


def test_evidence_gate_records_artifact_level_results(tmp_path: Path) -> None:
    evidence = tmp_path / "work" / "issue-1" / "process-report" / "specialist-review-security.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("# Security Review\n", encoding="utf-8")
    spec = tmp_path / "work" / "issue-1" / "test-specifications" / "unit-test-cases.md"
    spec.parent.mkdir(parents=True)
    spec.write_text("authorization denial test\n", encoding="utf-8")
    args = start_args(tmp_path)
    args.reviewer = ["security"]
    council.start_review(args)
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="info",
            claim="security review passed",
            verdict="pass",
            evidence_ref=["work/issue-1/process-report/specialist-review-security.md"],
            counterexample="",
            reasoning_summary="reviewed",
            requested_action="",
            confidence=0.8,
            required_test=["authorization denial test"],
            blocking=False,
            non_blocking=True,
        )
    )

    result = council.evidence_gate(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence=[],
            required_test=[],
            test_spec=[],
        )
    )

    assert result["status"] == "verified"
    assert result["evidence_results"][0]["exists"] is True
    assert result["artifact_checks"]
    assert result["missing_artifacts"] == []


def test_orchestrate_review_suggests_verdict_after_challenge_and_evidence(tmp_path: Path) -> None:
    args = start_args(tmp_path)
    args.reviewer = ["security"]
    args.evidence = []
    council.start_review(args)
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="runtime",
            severity="info",
            claim="runtime review passed",
            verdict="pass",
            evidence_ref=[],
            counterexample="",
            reasoning_summary="reviewed",
            requested_action="",
            confidence=0.8,
            required_test=[],
            blocking=False,
            non_blocking=True,
        )
    )
    council.challenge_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            challenge_id="",
            challenger="runtime-quality",
            mode="counterexample-check",
            issue_id=[],
            counterexample_found=False,
            summary="no counterexample found",
            evidence_ref=[],
        )
    )
    council.evidence_gate(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence=[],
            required_test=[],
            test_spec=[],
        )
    )

    result = council.orchestrate_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="", run_id="orc-verdict")
    )

    assert result["status"] == "orchestration-waiting"
    assert result["checks"]["challenge_completed"] is True
    assert result["checks"]["evidence_verified"] is True
    assert any(item["action"] == "decide-verdict" for item in result["next_actions"])
    assert any(item["node"] == "verdict-policy" and item["status"] == "ready" for item in result["node_results"])


def test_review_knowledge_capture_writes_rag_candidates_after_verdict(tmp_path: Path) -> None:
    args = start_args(tmp_path)
    args.reviewer = ["security"]
    args.evidence = []
    council.start_review(args)
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="runtime",
            severity="info",
            claim="runtime review passed",
            verdict="pass",
            evidence_ref=[],
            counterexample="",
            reasoning_summary="reviewed",
            requested_action="",
            confidence=0.8,
            required_test=[],
            blocking=False,
            non_blocking=True,
        )
    )
    council.challenge_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            challenge_id="",
            challenger="runtime-quality",
            mode="counterexample-check",
            issue_id=[],
            counterexample_found=False,
            summary="no counterexample found",
            evidence_ref=[],
        )
    )
    council.evidence_gate(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence=[],
            required_test=[],
            test_spec=[],
        )
    )
    council.decide_verdict(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence_verified=False,
            challenge_completed=False,
            target_revision_consistent=True,
            human_check="pending",
        )
    )

    result = council.capture_review_knowledge(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="")
    )
    orchestration = council.orchestrate_review(
        argparse.Namespace(repo_root=str(tmp_path), review_id="review-test", work_id="", work_dir="", run_id="orc-captured")
    )

    assert result["status"] == "captured"
    assert result["rag_candidates"]
    assert (tmp_path / result["artifacts"]["knowledge_capture_json"]).exists()
    assert orchestration["checks"]["knowledge_captured"] is True


def test_review_rag_build_writes_source_markdown_and_manifest(tmp_path: Path) -> None:
    council.start_review(start_args(tmp_path))
    council.summary_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            summary_id="summary-rag",
        )
    )

    result = council.rag_build_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            refresh_capture=False,
            run=False,
            output="",
            clean_output=False,
            skip_optimization=False,
            duckdb_migrate=False,
        )
    )
    source = tmp_path / result["source_document"]
    manifest = tmp_path / result["artifacts"]["rag_build_json"]

    assert result["artifact_type"] == "review-council-rag-build"
    assert result["status"] == "ready"
    assert result["document_type"] == "review-council"
    assert result["source_dir"].endswith("rag/review-council/issue-1/review-test")
    assert source.exists()
    assert "type: review-council" in source.read_text(encoding="utf-8")
    assert manifest.exists()
    assert "runtime/ctl/ctl.py --repo-root . rag build" in result["build_command"]
    assert "runtime/rag/rag_build.py" not in result["build_command"]
    assert "--source-dir" in result["build_command"]


def test_review_rag_build_can_run_existing_pipeline(monkeypatch, tmp_path: Path) -> None:
    council.start_review(start_args(tmp_path))
    called = {}

    def fake_run(args: argparse.Namespace) -> dict[str, object]:
        called["args"] = args
        return {
            "status": "completed",
            "rag_build_run": "work/db/ariadne-knowledge-platform/rag/retrieval/review.json",
            "document_count": 1,
            "chunk_count": 1,
        }

    monkeypatch.setattr(council.rag_build, "run", fake_run)

    result = council.rag_build_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            refresh_capture=True,
            run=True,
            output="work/db/ariadne-knowledge-platform/rag/retrieval/review.json",
            normalized_dir="",
            chunks_dir="",
            optimized_chunks_dir="",
            indexes_dir="",
            embeddings_output="",
            ingestion_evidence_dir="",
            ingestion_policy="",
            clean_output=False,
            skip_optimization=True,
            duckdb_migrate=True,
            duckdb_path="",
            duckdb_source_dir="",
            duckdb_error_log="",
            duckdb_evidence_output="",
            duckdb_policy="",
            project="",
            repository="",
            branch="",
            commit="",
            status="",
            chunk_size=1800,
            chunk_overlap=180,
            embedding_dimensions=768,
        )
    )

    run_args = called["args"]
    assert result["status"] == "completed"
    assert result["rag_build_run"]["document_count"] == 1
    assert run_args.document_type == "review-council"
    assert run_args.source_dir == result["source_dir"]
    assert run_args.duckdb_migrate is True
    assert run_args.skip_optimization is True


def test_add_finding_groups_issue_and_verdict_blocks_on_required_change(tmp_path: Path) -> None:
    council.start_review(start_args(tmp_path))

    finding = council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="high",
            claim="remote command path lacks authorization evidence",
            verdict="changes-required",
            evidence_ref=["docs/security.md"],
            counterexample="",
            reasoning_summary="authorization evidence is missing",
            requested_action="add authorization evidence and tests",
            confidence=0.9,
            required_test=["authorization denial test"],
            blocking=False,
            non_blocking=False,
        )
    )

    assert finding["finding"]["finding_id"] == "FND-001"
    assert finding["issues"][0]["issue_id"] == "RI-001"
    assert finding["issues"][0]["blocking"] is True

    verdict = council.decide_verdict(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence_verified=True,
            challenge_completed=True,
            target_revision_consistent=True,
            human_check="pending",
        )
    )

    assert verdict["verdict"] == "HUMAN_DECISION_REQUIRED"
    assert verdict["checks"]["missing_required_reviewers"] == 1
    assert verdict["checks"]["blocking_issues"] == 1


def test_verdict_approves_after_required_reviewers_and_gates_pass(tmp_path: Path) -> None:
    council.start_review(start_args(tmp_path))
    for reviewer in ["security", "runtime"]:
        council.add_finding(
            argparse.Namespace(
                repo_root=str(tmp_path),
                review_id="review-test",
                work_id="",
                work_dir="",
                finding_id="",
                reviewer=reviewer,
                category="runtime",
                severity="info",
                claim=f"{reviewer} found no blocking issue",
                verdict="pass",
                evidence_ref=["work/issue-1/test-evidence/runtime.md"],
                counterexample="",
                reasoning_summary="review packet is consistent",
                requested_action="",
                confidence=0.8,
                required_test=[],
                blocking=False,
                non_blocking=True,
            )
        )

    verdict = council.decide_verdict(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence_verified=True,
            challenge_completed=True,
            target_revision_consistent=True,
            human_check="pending",
        )
    )

    assert verdict["verdict"] == "APPROVED"
    assert verdict["checks"]["missing_required_reviewers"] == 0


def test_ctl_review_parser_and_json_flow(tmp_path: Path) -> None:
    parser = ctl.build_parser()
    plan_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "review",
            "plan",
            "--work-id",
            "issue-ctl-plan",
            "--review-id",
            "review-ctl-plan",
            "--intent",
            "plan runtime review for security logging changes",
            "--changed-file",
            "runtime/review/council.py",
            "--json",
        ]
    )
    plan_code, plan_output = ctl.run(plan_args)
    assert plan_code == 0
    plan_payload = json.loads(plan_output)
    assert plan_payload["review_id"] == "review-ctl-plan"
    assert "runtime" in plan_payload["required_reviewers"]

    args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "review",
            "start",
            "--work-id",
            "issue-ctl",
            "--review-id",
            "review-ctl",
            "--intent",
            "freeze review packet",
            "--reviewer",
            "security",
            "--json",
        ]
    )

    code, output = ctl.run(args)

    assert code == 0
    payload = json.loads(output)
    assert payload["review_id"] == "review-ctl"
    assert payload["packet"]["required_reviewers"] == ["security"]
    handoff_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "review", "handoff", "--review-id", "review-ctl", "--json"]
    )
    handoff_code, handoff_output = ctl.run(handoff_args)
    assert handoff_code == 0
    assert json.loads(handoff_output)["status"] == "handoff-ready"
    orchestrate_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "review", "orchestrate", "--review-id", "review-ctl", "--run-id", "orc-ctl", "--json"]
    )
    orchestrate_code, orchestrate_output = ctl.run(orchestrate_args)
    assert orchestrate_code == 0
    assert json.loads(orchestrate_output)["run_id"] == "orc-ctl"
    next_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "review", "next-action", "--review-id", "review-ctl", "--json"]
    )
    next_code, next_output = ctl.run(next_args)
    assert next_code == 0
    assert json.loads(next_output)["status"] == "action-required"
    summary_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "review",
            "summary",
            "--review-id",
            "review-ctl",
            "--summary-id",
            "summary-ctl",
            "--json",
        ]
    )
    summary_code, summary_output = ctl.run(summary_args)
    assert summary_code == 0
    summary_payload = json.loads(summary_output)
    assert summary_payload["artifact_type"] == "review-council-summary"
    assert summary_payload["summary_id"] == "summary-ctl"
    assert "summary_json" in summary_payload["artifacts"]
    human_gate_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "review",
            "human-gate",
            "--review-id",
            "review-ctl",
            "--gate",
            "review-council-final-verdict",
            "--human-check",
            "approved",
            "--reviewer",
            "Human",
            "--reason",
            "summary reviewed",
            "--json",
        ]
    )
    human_gate_code, human_gate_output = ctl.run(human_gate_args)
    assert human_gate_code == 0
    human_gate_payload = json.loads(human_gate_output)
    assert human_gate_payload["artifact_type"] == "review-council-human-gate"
    assert human_gate_payload["status"] == "approved"
    specialist_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "review",
            "run-specialist",
            "--review-id",
            "review-ctl",
            "--reviewer",
            "security",
            "--json",
        ]
    )
    specialist_code, specialist_output = ctl.run(specialist_args)
    assert specialist_code == 0
    assert json.loads(specialist_output)["artifact_type"] == "review-council-specialist-run"
    execute_specialist_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "review",
            "execute-specialist",
            "--review-id",
            "review-ctl",
            "--reviewer",
            "security",
            "--agent-command",
            "fake-agent",
            "--json",
        ]
    )
    execute_specialist_code, execute_specialist_output = ctl.run(execute_specialist_args)
    assert execute_specialist_code == 2
    execute_specialist_payload = json.loads(execute_specialist_output)
    assert execute_specialist_payload["artifact_type"] == "review-council-specialist-execution"
    assert execute_specialist_payload["status"] == "human-check-required"
    draft_report = tmp_path / "work" / "issue-ctl" / "process-report" / "specialist-review-security.md"
    draft_report.parent.mkdir(parents=True, exist_ok=True)
    draft_report.write_text(
        "## Finding 1\nSeverity: medium\nVerdict: needs-qa\nClaim: logging evidence needs human review\n",
        encoding="utf-8",
    )
    draft_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "review",
            "draft-findings",
            "--review-id",
            "review-ctl",
            "--reviewer",
            "security",
            "--report",
            "work/issue-ctl/process-report/specialist-review-security.md",
            "--json",
        ]
    )
    draft_code, draft_output = ctl.run(draft_args)
    assert draft_code == 0
    draft_payload = json.loads(draft_output)
    assert draft_payload["artifact_type"] == "review-council-finding-draft"
    assert draft_payload["draft_count"] == 1
    assert "aiwfctl review add-finding" in draft_payload["drafts"][0]["registration_command"]
    status_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "review", "status", "--review-id", "review-ctl", "--json"]
    )
    status_code, status_output = ctl.run(status_args)
    assert status_code == 0
    status_payload = json.loads(status_output)
    assert status_payload["status"] == "finding-draft-ready"
    assert status_payload["finding_draft_count"] == 1
    rag_build_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "review", "rag-build", "--review-id", "review-ctl", "--json"]
    )
    rag_build_code, rag_build_output = ctl.run(rag_build_args)
    assert rag_build_code == 0
    rag_build_payload = json.loads(rag_build_output)
    assert rag_build_payload["artifact_type"] == "review-council-rag-build"
    assert (tmp_path / rag_build_payload["source_document"]).exists()


def test_challenge_and_evidence_gate_are_saved_for_verdict(tmp_path: Path) -> None:
    evidence = tmp_path / "work" / "issue-1" / "process-report" / "specialist-review-security.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("# Security Review\n", encoding="utf-8")
    spec = tmp_path / "work" / "issue-1" / "test-specifications" / "unit-test-cases.md"
    spec.parent.mkdir(parents=True)
    spec.write_text("authorization denial test\n", encoding="utf-8")
    council.start_review(start_args(tmp_path))

    for reviewer in ["security", "runtime"]:
        council.add_finding(
            argparse.Namespace(
                repo_root=str(tmp_path),
                review_id="review-test",
                work_id="",
                work_dir="",
                finding_id="",
                reviewer=reviewer,
                category="security",
                severity="info",
                claim=f"{reviewer} reviewed the authorization evidence",
                verdict="pass",
                evidence_ref=["work/issue-1/process-report/specialist-review-security.md"],
                counterexample="",
                reasoning_summary="evidence is present",
                requested_action="",
                confidence=0.8,
                required_test=["authorization denial test"],
                blocking=False,
                non_blocking=True,
            )
        )

    challenge = council.challenge_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            challenge_id="",
            challenger="runtime-quality",
            mode="counterexample-check",
            issue_id=[],
            counterexample_found=False,
            summary="no counterexample found",
            evidence_ref=[],
        )
    )
    gate = council.evidence_gate(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence=[],
            required_test=[],
            test_spec=[],
        )
    )
    verdict = council.decide_verdict(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence_verified=False,
            challenge_completed=False,
            target_revision_consistent=True,
            human_check="pending",
        )
    )

    assert challenge["status"] == "completed"
    assert gate["status"] == "verified"
    assert verdict["verdict"] == "APPROVED"
    assert verdict["checks"]["evidence_verified"] is True
    assert verdict["checks"]["challenge_completed"] is True


def test_reinspection_closes_blocking_finding_before_verdict(tmp_path: Path) -> None:
    args = start_args(tmp_path)
    args.reviewer = ["security"]
    args.evidence = []
    council.start_review(args)
    finding = council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="high",
            claim="authorization evidence missing",
            verdict="changes-required",
            evidence_ref=[],
            counterexample="",
            reasoning_summary="evidence is missing",
            requested_action="add evidence",
            confidence=0.9,
            required_test=[],
            blocking=False,
            non_blocking=False,
        )
    )

    assert finding["issues"][0]["blocking"] is True

    reinspection = council.reinspect_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id=["FND-001"],
            status="verified",
            reviewer="security",
            summary="evidence was added and verified",
            evidence_ref=[],
        )
    )
    council.challenge_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            challenge_id="",
            challenger="runtime-quality",
            mode="counterexample-check",
            issue_id=[],
            counterexample_found=False,
            summary="no counterexample found",
            evidence_ref=[],
        )
    )
    gate = council.evidence_gate(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence=[],
            required_test=[],
            test_spec=[],
        )
    )
    verdict = council.decide_verdict(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence_verified=False,
            challenge_completed=False,
            target_revision_consistent=True,
            human_check="pending",
        )
    )

    assert reinspection["status"] == "verified"
    assert gate["status"] == "verified"
    assert verdict["verdict"] == "APPROVED"


def test_challenge_counterexample_blocks_verdict(tmp_path: Path) -> None:
    args = start_args(tmp_path)
    args.reviewer = ["security"]
    args.evidence = []
    council.start_review(args)
    council.add_finding(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            finding_id="",
            reviewer="security",
            category="security",
            severity="info",
            claim="security review passed",
            verdict="pass",
            evidence_ref=[],
            counterexample="",
            reasoning_summary="no finding",
            requested_action="",
            confidence=0.8,
            required_test=[],
            blocking=False,
            non_blocking=True,
        )
    )
    council.challenge_review(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            challenge_id="",
            challenger="runtime-quality",
            mode="counterexample-check",
            issue_id=[],
            counterexample_found=True,
            summary="a counterexample still exists",
            evidence_ref=[],
        )
    )
    council.evidence_gate(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence=[],
            required_test=[],
            test_spec=[],
        )
    )

    verdict = council.decide_verdict(
        argparse.Namespace(
            repo_root=str(tmp_path),
            review_id="review-test",
            work_id="",
            work_dir="",
            evidence_verified=False,
            challenge_completed=False,
            target_revision_consistent=True,
            human_check="pending",
        )
    )

    assert verdict["verdict"] == "HUMAN_DECISION_REQUIRED"
    assert verdict["checks"]["challenge_blockers"] == 1


def test_langgraph_adapter_returns_dependency_free_plan(tmp_path: Path) -> None:
    session = council.start_review(start_args(tmp_path))

    plan = build_langgraph_review_plan(session)

    assert plan["adapter"] == "langgraph"
    assert plan["review_id"] == "review-test"
    assert "reviewer:security" in plan["nodes"]
    assert "reinspection" in plan["nodes"]
    assert ["challenge-round", "evidence-gate"] in plan["edges"]


def test_langgraph_adapter_invokes_compiled_state_graph(monkeypatch, tmp_path: Path) -> None:
    class FakeApp:
        def __init__(self, graph: "FakeStateGraph") -> None:
            self.graph = graph

        def invoke(self, state: dict[str, object]) -> dict[str, object]:
            node = self.graph.start_node
            current = dict(state)
            for _ in range(20):
                current = self.graph.nodes[node](current)
                if node in self.graph.conditional_edges:
                    router, mapping = self.graph.conditional_edges[node]
                    node = mapping[router(current)]
                else:
                    node = self.graph.edges[node]
                if node == self.graph.end:
                    break
            return current

    class FakeStateGraph:
        start = "__start__"
        end = "__end__"

        def __init__(self, state_type: object) -> None:
            self.nodes: dict[str, object] = {}
            self.edges: dict[str, str] = {}
            self.conditional_edges: dict[str, object] = {}
            self.start_node = ""

        def add_node(self, name: str, func: object) -> None:
            self.nodes[name] = func

        def add_edge(self, source: str, target: str) -> None:
            if source == self.start:
                self.start_node = target
            else:
                self.edges[source] = target

        def add_conditional_edges(self, source: str, router: object, mapping: dict[str, str]) -> None:
            self.conditional_edges[source] = (router, mapping)

        def compile(self) -> FakeApp:
            return FakeApp(self)

    session = council.start_review(start_args(tmp_path))
    monkeypatch.setattr(langgraph_adapter, "langgraph_available", lambda: True)
    monkeypatch.setattr(
        langgraph_adapter,
        "_langgraph_graph_api",
        lambda: (FakeStateGraph, FakeStateGraph.start, FakeStateGraph.end),
    )

    result = langgraph_adapter.evaluate_langgraph_review_state(session, run_id="orc-langgraph")

    assert result["execution_mode"] == "langgraph"
    assert result["graph_execution"]["compiled"] is True
    assert result["graph_execution"]["trace"] == [
        "review-intake",
        "packet-freeze",
        "risk-classification",
        "specialist-reviewers",
        "finalize",
    ]
    assert result["next_actions"][0]["action"] == "create-reviewer-handoffs"
