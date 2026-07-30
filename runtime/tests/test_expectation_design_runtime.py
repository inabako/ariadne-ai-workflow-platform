from __future__ import annotations

import json
from pathlib import Path

from runtime.constants import schemas
from runtime.ctl import ctl
from runtime.design.expectation import evaluator
from runtime.design.expectation.models import CriticalExpectation, Expectation, ExpectationWeight
from runtime.design.expectation.violation_detector import summarize_violations


def test_expectation_weight_normalization_and_critical_gate() -> None:
    expectations = [
        Expectation.from_mapping({"id": "EXP-1", "statement": "first", "confidence": 1.0}),
        Expectation.from_mapping({"id": "EXP-2", "statement": "second", "confidence": 1.0}),
    ]
    weights = evaluator.normalize_weights(
        [
            ExpectationWeight.from_mapping({"expectation_id": "EXP-1", "weight": 2.0 / 3.0}),
            ExpectationWeight.from_mapping({"expectation_id": "EXP-2", "weight": 1.0 / 3.0}),
        ],
        expectations,
    )
    evaluations = evaluator.candidate_evaluations(
        {
            "candidate_evaluations": [
                {
                    "candidate_id": "DESIGN-A",
                    "expectations": [
                        {"expectation_id": "EXP-1", "probability": 0.5, "confidence": 1.0, "evidence": ["test"]},
                        {"expectation_id": "EXP-2", "probability": 1.0, "confidence": 1.0},
                    ],
                }
            ]
        }
    )
    scores, violations = evaluator.score_candidates(
        evaluations,
        weights,
        [CriticalExpectation.from_mapping({"expectation_id": "EXP-1", "minimum_probability": 1.0})],
    )

    assert round(sum(item.weight for item in weights), 6) == 1.0
    assert scores[0].candidate_id == "DESIGN-A"
    assert scores[0].expectation_score == 0.666667
    assert scores[0].critical_violation_count == 1
    assert scores[0].recommendable is False
    assert violations[0].severity == "critical"


def test_expectation_violation_detection_classifies_design_risks() -> None:
    expectations = [
        Expectation.from_mapping({"id": "EXP-1", "statement": "critical", "confidence": 1.0}),
        Expectation.from_mapping({"id": "EXP-2", "statement": "major", "confidence": 1.0}),
        Expectation.from_mapping({"id": "EXP-3", "statement": "minor", "confidence": 1.0}),
        Expectation.from_mapping({"id": "EXP-4", "statement": "ambiguous", "confidence": 1.0}),
        Expectation.from_mapping({"id": "EXP-5", "statement": "positive", "confidence": 1.0}),
        Expectation.from_mapping({"id": "EXP-6", "statement": "missing", "confidence": 1.0}),
    ]
    weights = evaluator.normalize_weights(
        [ExpectationWeight.from_mapping({"expectation_id": item.expectation_id, "weight": 1.0}) for item in expectations],
        expectations,
    )
    evaluations = evaluator.candidate_evaluations(
        {
            "candidate_evaluations": [
                {
                    "candidate_id": "DESIGN-X",
                    "expectations": [
                        {"expectation_id": "EXP-1", "probability": 0.9, "confidence": 0.9, "evidence": ["prototype"]},
                        {"expectation_id": "EXP-2", "probability": 0.3, "confidence": 0.9, "evidence": ["prototype"]},
                        {"expectation_id": "EXP-3", "probability": 0.7, "confidence": 0.9, "evidence": ["prototype"]},
                        {"expectation_id": "EXP-4", "probability": 0.5, "confidence": 0.9, "evidence": ["prototype"]},
                        {"expectation_id": "EXP-5", "probability": 0.99, "confidence": 0.9, "evidence": ["prototype"]},
                    ],
                }
            ]
        }
    )
    scores, violations = evaluator.score_candidates(
        evaluations,
        weights,
        [CriticalExpectation.from_mapping({"expectation_id": "EXP-1", "minimum_probability": 0.95})],
        expectations,
    )
    severities = {item.severity for item in violations}
    summary = summarize_violations(violations)[0]

    assert scores[0].critical_violation_count == 1
    assert scores[0].recommendable is False
    assert {"critical", "major", "minor", "ambiguous", "unverified", "positive-surprise"} <= severities
    assert summary["critical"] == 1
    assert summary["major"] == 1
    assert summary["minor"] == 1
    assert summary["ambiguous"] == 1
    assert summary["unverified"] == 1
    assert summary["positive_surprise"] == 1


def test_design_expectation_cli_initializes_compares_and_gates(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    parser = ctl.build_parser()

    init_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "init", "--work-id", "issue-1", "--sample", "--json"]
    )
    init_code, init_output = ctl.run(init_args)
    assert init_code == 0
    init_payload = json.loads(init_output)
    assert init_payload["status"] == "initialized"
    base = tmp_path / "work" / "issue-1" / "design" / "expectation"
    expectation_set = json.loads((base / "expectation-set.json").read_text(encoding="utf-8"))
    usage_context = json.loads((base / "usage-context.json").read_text(encoding="utf-8"))
    expectation_conflicts = json.loads((base / "expectation-conflicts.json").read_text(encoding="utf-8"))
    weights = json.loads((base / "expectation-weights.json").read_text(encoding="utf-8"))
    critical = json.loads((base / "critical-expectations.json").read_text(encoding="utf-8"))
    multi_axis = json.loads((base / "evaluations" / "multi-axis-evaluation.json").read_text(encoding="utf-8"))
    tradeoffs = json.loads((base / "evaluations" / "trade-off-analysis.json").read_text(encoding="utf-8"))
    comparison_packet = json.loads((base / "design-comparison-report.json").read_text(encoding="utf-8"))
    contracts = json.loads((base / "selected-design" / "interaction-contracts.json").read_text(encoding="utf-8"))
    human_decision = json.loads((base / "human-decision.json").read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "work" / "issue-1" / "context" / "context-manifest.json").read_text(encoding="utf-8"))
    artifact_index = json.loads((tmp_path / "work" / "issue-1" / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    context_types = {item["type"]: item for item in manifest["contexts"]}
    artifact_ids = {item["id"]: item for item in artifact_index["artifacts"]}
    assert expectation_set["schema"] == schemas.EXPECTATION_SET_SCHEMA
    assert usage_context["schema"] == schemas.USAGE_CONTEXT_SCHEMA
    assert expectation_conflicts["schema"] == schemas.EXPECTATION_CONFLICTS_SCHEMA
    assert weights["schema"] == schemas.EXPECTATION_WEIGHTS_SCHEMA
    assert critical["schema"] == schemas.CRITICAL_EXPECTATIONS_SCHEMA
    assert multi_axis["schema"] == schemas.MULTI_AXIS_EVALUATION_SCHEMA
    assert tradeoffs["schema"] == schemas.TRADE_OFF_ANALYSIS_SCHEMA
    assert comparison_packet["schema"] == schemas.DESIGN_COMPARISON_REPORT_SCHEMA
    assert multi_axis["required_axes"] == [
        "expectation_satisfaction",
        "usability",
        "product_identity",
        "delight",
        "accessibility",
        "implementation_cost",
        "maintenance_cost",
        "technical_feasibility",
    ]
    assert contracts["schema"] == schemas.INTERACTION_CONTRACTS_SCHEMA
    assert human_decision["schema"] == schemas.HUMAN_DECISION_SCHEMA
    assert context_types["workflow-specific-state"]["schema"] == schemas.EXPECTATION_SET_SCHEMA
    assert context_types["artifact-index"]["schema"] == schemas.ARTIFACT_INDEX_SCHEMA
    assert {"EDD-EXPECTATION-SET", "EDD-EXPECTATION-WEIGHTS", "EDD-CRITICAL-EXPECTATIONS"} <= set(artifact_ids)
    assert "EDD-MULTI-AXIS-EVALUATION" in artifact_ids
    assert "EDD-TRADE-OFF-ANALYSIS" in artifact_ids
    assert "EDD-DESIGN-COMPARISON-PACKET" in artifact_ids
    assert artifact_ids["EDD-EXPECTATION-SET"]["type"] == "design"
    assert artifact_ids["EDD-EXPECTATION-SET"]["path"].endswith("expectation-set.json")
    assert not (base / "expectation-set.yaml").exists()
    assert (base / "selected-design" / "implementation-notes.md").exists()
    assert (base / "verification" / "evidence-index.md").exists()

    candidate_alias_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "candidate",
            "generate",
            "--work-id",
            "issue-1",
            "--candidate-id",
            "DESIGN-ALIAS",
            "--json",
        ]
    )
    alias_code, alias_output = ctl.run(candidate_alias_args)
    assert alias_code == 0
    assert json.loads(alias_output)["status"] == "scaffolded"
    assert (base / "candidates" / "design-alias" / "concept.md").exists()

    compare_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "compare", "--work-id", "issue-1", "--json"]
    )
    compare_code, compare_output = ctl.run(compare_args)
    assert compare_code == 0
    compare_payload = json.loads(compare_output)
    assert compare_payload["status"] == "comparison-ready"
    assert compare_payload["candidate_count"] == 2
    assert [item["candidate_id"] for item in compare_payload["candidate_scores"]] == ["DESIGN-A", "DESIGN-B"]
    assert compare_payload["candidate_scores"][0]["critical_violation_count"] == 1
    assert compare_payload["multi_axis_summary"][1]["candidate_id"] == "DESIGN-B"
    assert compare_payload["multi_axis_summary"][1]["axis_average"] == 0.775
    assert compare_payload["tradeoffs"][1]["candidate_id"] == "DESIGN-B"
    assert compare_payload["comparison_report"]["recommended_candidate"] == "DESIGN-B"
    assert len(compare_payload["comparison_report"]["report_sections"]) == 15
    assert compare_payload["comparison_json"].endswith("design-comparison-report.json")
    assert compare_payload["tradeoffs_output"].endswith("trade-off-analysis.json")
    assert compare_payload["tradeoff_report"].endswith("trade-off-analysis.md")
    report_text = (tmp_path / compare_payload["report"]).read_text(encoding="utf-8")
    assert report_text.startswith("# Expectation-Driven Design Comparison")
    assert "## Usage Context" in report_text
    assert "## Major Expectations" in report_text
    assert "## Critical Expectations" in report_text
    assert "## Candidate Overview" in report_text
    assert "## Multi-Axis Evaluation" in report_text
    assert "## Violation Summary" in report_text
    assert "## Trade-off Analysis" in report_text
    assert "## Implementation Costs" in report_text
    assert "## Positive Surprise Hypotheses" in report_text
    assert "## Report Section Coverage" in report_text
    assert "Implementation Cost" in report_text
    assert "Multi-axis evaluation must be reviewed before Human Gate approval." in report_text
    assert "## Evidence And Validation" in report_text
    assert "## Unverified Items" in report_text
    assert "## Alternatives" in report_text
    assert "未検証Evidenceを追加調査へ回す" in report_text
    assert "DESIGN-A / EXP-TIME-001" in report_text
    assert "DESIGN-B を推奨候補として提示できます。" in report_text
    assert "Critical Expectation違反がありません。" in report_text
    artifact_index = json.loads((tmp_path / compare_payload["artifact_index"]).read_text(encoding="utf-8"))
    artifact_ids = {item["id"]: item for item in artifact_index["artifacts"]}
    assert artifact_ids["EDD-EVALUATION-RESULT"]["path"] == compare_payload["output"]
    assert artifact_ids["EDD-DESIGN-COMPARISON-PACKET"]["path"] == compare_payload["comparison_json"]
    assert artifact_ids["EDD-TRADE-OFF-ANALYSIS"]["path"] == compare_payload["tradeoffs_output"]
    assert artifact_ids["EDD-TRADE-OFF-REPORT"]["path"] == compare_payload["tradeoff_report"]
    assert artifact_ids["EDD-DESIGN-COMPARISON-REPORT"]["status"] == "in-review"
    violations = json.loads((tmp_path / compare_payload["violations_output"]).read_text(encoding="utf-8"))
    assert violations["violation_summary"][0]["critical"] == 1
    tradeoff_payload = json.loads((tmp_path / compare_payload["tradeoffs_output"]).read_text(encoding="utf-8"))
    comparison_json = json.loads((tmp_path / compare_payload["comparison_json"]).read_text(encoding="utf-8"))
    tradeoff_text = (tmp_path / compare_payload["tradeoff_report"]).read_text(encoding="utf-8")
    assert tradeoff_payload["schema"] == schemas.TRADE_OFF_ANALYSIS_SCHEMA
    assert tradeoff_payload["tradeoffs"][0]["affected_expectations"] == ["EXP-TIME-001"]
    assert comparison_json["schema"] == schemas.DESIGN_COMPARISON_REPORT_SCHEMA
    assert comparison_json["candidate_overviews"][1]["candidate_id"] == "DESIGN-B"
    assert comparison_json["implementation_costs"][1]["implementation_cost"] == 0.65
    assert "# Trade-off Analysis" in tradeoff_text
    assert "Gained values:" in tradeoff_text

    pending_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "gate", "--work-id", "issue-1", "--json"]
    )
    pending_code, pending_output = ctl.run(pending_args)
    assert pending_code == 2
    assert json.loads(pending_output)["status"] == "human-check-required"

    approved_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "gate",
            "--work-id",
            "issue-1",
            "--selected-candidate",
            "DESIGN-B",
            "--human-check",
            "approved",
            "--decision-action",
            "combine",
            "--combine-with",
            "DESIGN-C:memo input|context wording",
            "--weight-change",
            "EXP-TIME-001:1.0:0.9",
            "--decision-item",
            "Validate accessibility before implementation.",
            "--comment",
            "Human reviewed the comparison.",
            "--json",
        ]
    )
    approved_code, approved_output = ctl.run(approved_args)
    assert approved_code == 0
    approved_payload = json.loads(approved_output)
    assert approved_payload["status"] == "approved"
    assert approved_payload["decision_action"] == "combine"
    decision = json.loads((tmp_path / approved_payload["human_decision"]).read_text(encoding="utf-8"))
    assert decision["selected_candidate"] == "DESIGN-B"
    assert decision["schema"] == schemas.HUMAN_DECISION_SCHEMA
    assert decision["decision_action"] == "combine"
    assert decision["combine_with"] == [{"candidate_id": "DESIGN-C", "elements": ["memo input", "context wording"]}]
    assert decision["weight_changes"] == [{"expectation_id": "EXP-TIME-001", "before": 1.0, "after": 0.9}]
    assert decision["decision_items"] == ["Validate accessibility before implementation."]
    assert decision["source_comparison_packet"].endswith("design-comparison-report.json")
    summary_text = (tmp_path / approved_payload["human_gate_summary"]).read_text(encoding="utf-8")
    refinement_plan = json.loads((tmp_path / approved_payload["refinement_plan"]).read_text(encoding="utf-8"))
    assert "# Human Gate Summary" in summary_text
    assert "DESIGN-C: memo input, context wording" in summary_text
    assert refinement_plan["status"] == "ready-for-refinement"
    assert refinement_plan["selected_candidate"] == "DESIGN-B"
    assert refinement_plan["combine_with"] == decision["combine_with"]
    artifact_index = json.loads((tmp_path / approved_payload["artifact_index"]).read_text(encoding="utf-8"))
    artifact_ids = {item["id"]: item for item in artifact_index["artifacts"]}
    assert artifact_ids["EDD-HUMAN-DECISION"]["status"] == "approved"
    assert artifact_ids["EDD-HUMAN-DECISION"]["path"].endswith("human-decision.json")
    assert artifact_ids["EDD-HUMAN-GATE-SUMMARY"]["path"] == approved_payload["human_gate_summary"]
    assert artifact_ids["EDD-DESIGN-REFINEMENT-PLAN"]["path"] == approved_payload["refinement_plan"]

    candidate_compare_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "candidate", "compare", "--work-id", "issue-1", "--json"]
    )
    candidate_compare_code, candidate_compare_output = ctl.run(candidate_compare_args)
    assert candidate_compare_code == 0
    assert json.loads(candidate_compare_output)["status"] == "comparison-ready"


def test_design_expectation_requires_json_source_artifacts(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    parser = ctl.build_parser()
    init_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "init", "--work-id", "issue-json-only", "--sample", "--json"]
    )
    code, _ = ctl.run(init_args)
    assert code == 0
    base = tmp_path / "work" / "issue-json-only" / "design" / "expectation"
    assert (base / "expectation-set.json").exists()
    assert (base / "expectation-weights.json").exists()
    assert (base / "critical-expectations.json").exists()
    assert not (base / "expectation-set.yaml").exists()
    assert not (base / "evaluations" / "multi-axis-evaluation.yaml").exists()
    assert not (base / "evaluations" / "trade-off-analysis.yaml").exists()
    assert not (base / "design-comparison-report.yaml").exists()

    compare_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "compare", "--work-id", "issue-json-only", "--json"]
    )
    compare_code, compare_output = ctl.run(compare_args)

    assert compare_code == 0
    payload = json.loads(compare_output)
    assert payload["status"] == "comparison-ready"
    assert payload["candidate_count"] == 2


def test_design_expectation_remaining_workflow_commands_generate_artifacts(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    parser = ctl.build_parser()
    init_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "init", "--work-id", "issue-full", "--sample", "--json"]
    )
    assert ctl.run(init_args)[0] == 0
    base = tmp_path / "work" / "issue-full" / "design" / "expectation"

    scaffold_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "candidate-scaffold",
            "--work-id",
            "issue-full",
            "--candidate-id",
            "DESIGN-A",
            "--candidate-id",
            "DESIGN-B",
            "--json",
        ]
    )
    scaffold_code, scaffold_output = ctl.run(scaffold_args)
    assert scaffold_code == 0
    scaffold_payload = json.loads(scaffold_output)
    assert scaffold_payload["status"] == "scaffolded"
    assert (base / "candidates" / "design-a" / "concept.md").exists()
    assert (base / "candidates" / "design-a" / "flow.json").exists()
    assert (base / "candidates" / "design-a" / "wireframe.svg").exists()

    candidate_generate_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "candidate",
            "generate",
            "--work-id",
            "issue-full",
            "--candidate-id",
            "DESIGN-C",
            "--json",
        ]
    )
    assert ctl.run(candidate_generate_args)[0] == 0
    assert (base / "candidates" / "design-c" / "concept.md").exists()

    feasibility_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "feasibility",
            "--work-id",
            "issue-full",
            "--candidate-id",
            "DESIGN-A",
            "--pass-feasibility",
            "--json",
        ]
    )
    feasibility_code, feasibility_output = ctl.run(feasibility_args)
    assert feasibility_code == 0
    feasibility_payload = json.loads(feasibility_output)
    assert feasibility_payload["reports"][0]["status"] == "feasible"

    extract_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "extract",
            "--work-id",
            "issue-full",
            "--requirement",
            "The app must accept 39:00 time input and keep accessibility testable.",
            "--json",
        ]
    )
    extract_code, extract_output = ctl.run(extract_args)
    assert extract_code == 0
    extract_payload = json.loads(extract_output)
    expectation_set = json.loads((tmp_path / extract_payload["expectations"]).read_text(encoding="utf-8"))
    assert {item["id"] for item in expectation_set["expectations"]} == {"EXP-TIME-001", "EXP-A11Y-001"}
    assert all(item["confidence"] > 0 for item in expectation_set["expectations"])
    assert all(item["evidence_refs"] for item in expectation_set["expectations"])

    review_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "review", "--work-id", "issue-full", "--json"]
    )
    review_code, review_output = ctl.run(review_args)
    assert review_code == 2
    review_payload = json.loads(review_output)
    assert review_payload["status"] == "ready-for-human-check"
    review_report = json.loads((tmp_path / review_payload["review_report"]).read_text(encoding="utf-8"))
    assert review_report["schema"] == schemas.EXPECTATION_REVIEW_REPORT_SCHEMA

    multi_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "multi-axis", "--work-id", "issue-full", "--json"]
    )
    multi_code, multi_output = ctl.run(multi_args)
    assert multi_code == 0
    assert json.loads(multi_output)["status"] == "evaluated"

    pending_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "gate", "--work-id", "issue-full", "--json"]
    )
    assert ctl.run(pending_args)[0] == 2
    approved_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "gate",
            "--work-id",
            "issue-full",
            "--selected-candidate",
            "DESIGN-B",
            "--human-check",
            "approved",
            "--json",
        ]
    )
    assert ctl.run(approved_args)[0] == 0

    for command in ["refine", "contracts", "verify", "feedback", "dispatch"]:
        args = parser.parse_args(
            ["--repo-root", str(tmp_path), "design", "expectation", command, "--work-id", "issue-full", "--json"]
        )
        code, output = ctl.run(args)
        assert code == 0, output

    contracts = json.loads((base / "selected-design" / "interaction-contracts.json").read_text(encoding="utf-8"))
    verification = json.loads((base / "verification" / "expectation-verification.json").read_text(encoding="utf-8"))
    feedback = json.loads((base / "verification" / "expectation-feedback.json").read_text(encoding="utf-8"))
    dispatch = json.loads((base / "review-council-dispatch.json").read_text(encoding="utf-8"))
    events = (base / "events.jsonl").read_text(encoding="utf-8")
    assert contracts["schema"] == schemas.INTERACTION_CONTRACTS_SCHEMA
    assert contracts["interaction_contracts"][0]["must_not"]
    assert verification["schema"] == schemas.EXPECTATION_VERIFICATION_SCHEMA
    assert verification["expectation_verification"][0]["verified_result"] is None
    assert feedback["schema"] == schemas.EXPECTATION_FEEDBACK_SCHEMA
    assert feedback["feedback"][0]["knowledge_candidate"] is True
    assert dispatch["schema"] == schemas.EXPECTATION_DESIGN_DISPATCH_SCHEMA
    assert "accessibility" in dispatch["reviewers"]
    assert "expectation_extracted" in events
    assert "design_candidate_evaluated" in events
    assert "design_human_gate_required" in events
    assert "human_decision_recorded" in events


def test_design_expectation_agent_extraction_and_review_council_sync(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    parser = ctl.build_parser()
    init_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "init", "--work-id", "issue-agent", "--sample", "--json"]
    )
    assert ctl.run(init_args)[0] == 0
    base = tmp_path / "work" / "issue-agent" / "design" / "expectation"

    request_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "extract",
            "--work-id",
            "issue-agent",
            "--mode",
            "agent",
            "--requirement",
            "Keep keyboard accessibility and over-24-hour time input.",
            "--json",
        ]
    )
    request_code, request_output = ctl.run(request_args)
    request_payload = json.loads(request_output)
    assert request_code == 2
    assert request_payload["status"] == "human-check-required"
    assert (tmp_path / request_payload["agent_request"]).exists()

    agent_output = base / "agent-output.json"
    agent_output.write_text(
        json.dumps(
            {
                "agent_id": "expectation-extractor-agent",
                "usage_context": {
                    "actor": "scheduler",
                    "situation": "editing next-day time records",
                    "goal": "enter 39:00 without losing accessibility",
                    "confidence": 0.82,
                    "evidence_refs": ["requirements.md:1"],
                },
                "expectations": [
                    {
                        "id": "EXP-AGENT-TIME",
                        "statement": "Users can preserve 39:00 as an over-24-hour time value.",
                        "category": "usability",
                        "success_conditions": ["39:00 remains accepted"],
                        "failure_conditions": ["39:00 is rejected"],
                        "confidence": 0.91,
                        "evidence_refs": ["requirements.md:1"],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    extract_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "extract",
            "--work-id",
            "issue-agent",
            "--agent-output",
            str(agent_output),
            "--json",
        ]
    )
    extract_code, extract_output = ctl.run(extract_args)
    extract_payload = json.loads(extract_output)
    assert extract_code == 0
    expectation_set = json.loads((tmp_path / extract_payload["expectations"]).read_text(encoding="utf-8"))
    assert expectation_set["expectations"][0]["id"] == "EXP-AGENT-TIME"
    assert expectation_set["expectations"][0]["category"] == "Interaction Expectation"
    assert expectation_set["expectations"][0]["confidence"] == 0.91
    assert str(agent_output.relative_to(tmp_path)).replace("\\", "/") in expectation_set["expectations"][0]["evidence_refs"]

    compare_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "compare", "--work-id", "issue-agent", "--json"]
    )
    assert ctl.run(compare_args)[0] == 0
    dispatch_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "dispatch",
            "--work-id",
            "issue-agent",
            "--review-id",
            "review-design",
            "--json",
        ]
    )
    dispatch_code, dispatch_output = ctl.run(dispatch_args)
    dispatch_payload = json.loads(dispatch_output)
    assert dispatch_code == 0
    dispatch_packet = json.loads((tmp_path / dispatch_payload["dispatch"]).read_text(encoding="utf-8"))
    assert dispatch_packet["review_id"] == "review-design"
    assert "frontend-architecture" in dispatch_packet["reviewers"]
    assert "aiwfctl review start" in dispatch_packet["review_start_command"]

    review_summary = base / "review-summary.json"
    review_summary.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "artifact_type": "review-council-summary",
                "review_id": "review-design",
                "work_id": "issue-agent",
                "snapshot": {
                    "verdict": "HUMAN_DECISION_REQUIRED",
                    "missing_reviewers": [],
                    "open_issue_count": 1,
                    "blocking_issue_count": 1,
                },
                "findings": [
                    {
                        "finding_id": "FND-001",
                        "reviewer": "accessibility",
                        "category": "accessibility",
                        "severity": "high",
                        "verdict": "changes-required",
                        "blocking": True,
                        "status": "open",
                        "claim": "Keyboard focus evidence is missing for the selected design.",
                        "requested_action": "Add keyboard focus evidence.",
                        "evidence_refs": ["work/issue-agent/design/expectation/design-comparison-report.json"],
                        "required_tests": ["keyboard focus test"],
                    }
                ],
                "issues": [
                    {
                        "issue_id": "RI-001",
                        "category": "accessibility",
                        "severity": "high",
                        "blocking": True,
                        "status": "open",
                        "claim": "Keyboard focus evidence is missing for the selected design.",
                        "finding_ids": ["FND-001"],
                        "required_evidence": ["focus order evidence"],
                        "required_tests": ["keyboard focus test"],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    sync_args = parser.parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "design",
            "expectation",
            "council-sync",
            "--work-id",
            "issue-agent",
            "--review-summary",
            str(review_summary),
            "--json",
        ]
    )
    sync_code, sync_output = ctl.run(sync_args)
    sync_payload = json.loads(sync_output)
    assert sync_code == 2
    assert sync_payload["status"] == "review-blocked"
    comparison = json.loads((base / "design-comparison-report.json").read_text(encoding="utf-8"))
    report = (base / "design-comparison-report.md").read_text(encoding="utf-8")
    assert comparison["review_council_feedback"]["review_id"] == "review-design"
    assert "review_council_feedback" in comparison["report_sections"]
    assert any("RI-001" in item for item in comparison["human_decision_items"])
    assert "## Review Council Feedback" in report
    assert "Keyboard focus evidence is missing" in report

    pending_args = parser.parse_args(
        ["--repo-root", str(tmp_path), "design", "expectation", "gate", "--work-id", "issue-agent", "--json"]
    )
    pending_code, pending_output = ctl.run(pending_args)
    pending_payload = json.loads(pending_output)
    assert pending_code == 2
    assert any("RI-001" in item for item in pending_payload["decision_required"])


def test_expectation_design_schema_files_are_registered() -> None:
    root = Path(__file__).resolve().parents[2]
    for schema_path in [
        schemas.EXPECTATION_SET_SCHEMA,
        schemas.EXPECTATION_WEIGHTS_SCHEMA,
        schemas.CRITICAL_EXPECTATIONS_SCHEMA,
        schemas.DESIGN_CANDIDATES_SCHEMA,
        schemas.DESIGN_COMPARISON_REPORT_SCHEMA,
        schemas.DESIGN_FEASIBILITY_REPORT_SCHEMA,
        schemas.EXPECTATION_DESIGN_DISPATCH_SCHEMA,
        schemas.EXPECTATION_EVALUATION_SCHEMA,
        schemas.EXPECTATION_CONFLICTS_SCHEMA,
        schemas.EXPECTATION_FEEDBACK_SCHEMA,
        schemas.EXPECTATION_REVIEW_REPORT_SCHEMA,
        schemas.HUMAN_DECISION_SCHEMA,
        schemas.INTERACTION_CONTRACTS_SCHEMA,
        schemas.MULTI_AXIS_EVALUATION_SCHEMA,
        schemas.EXPECTATION_VERIFICATION_SCHEMA,
        schemas.TRADE_OFF_ANALYSIS_SCHEMA,
        schemas.USAGE_CONTEXT_SCHEMA,
    ]:
        payload = json.loads((root / schema_path).read_text(encoding="utf-8"))
        assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert payload["type"] == "object"
