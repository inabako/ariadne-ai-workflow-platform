from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import (
    AxisEvaluation,
    CandidateScore,
    CriticalExpectation,
    Expectation,
    ExpectationEvaluation,
    ExpectationViolation,
    ExpectationWeight,
)
from .constants import (
    DEFAULT_EXPECTATION_CONFIDENCE,
    SCORE_MIN,
    SCORE_ROUND_DECIMALS,
)
from .violation_detector import detect_expectation_violations


DEFAULT_DESIGN_AXES = (
    "expectation_satisfaction",
    "usability",
    "product_identity",
    "delight",
    "accessibility",
    "implementation_cost",
    "maintenance_cost",
    "technical_feasibility",
)


def normalize_weights(weights: list[ExpectationWeight], expectations: list[Expectation]) -> list[ExpectationWeight]:
    if not weights:
        if not expectations:
            return []
        even = DEFAULT_EXPECTATION_CONFIDENCE / len(expectations)
        return [
            ExpectationWeight(
                expectation_id=item.expectation_id,
                weight=even,
                rationale=("No explicit weights were provided; normalized evenly.",),
                decided_by="ariadne-initial",
            )
            for item in expectations
        ]
    total = sum(item.weight for item in weights)
    if total <= SCORE_MIN:
        raise ValueError(f"weight total must be greater than {SCORE_MIN:.1f}")
    return [
        ExpectationWeight(
            expectation_id=item.expectation_id,
            weight=item.weight / total,
            rationale=item.rationale,
            decided_by=item.decided_by,
        )
        for item in weights
    ]


def candidate_evaluations(data: dict[str, Any]) -> dict[str, list[ExpectationEvaluation]]:
    result: dict[str, list[ExpectationEvaluation]] = {}
    for candidate in data.get("candidate_evaluations", []):
        candidate_id = str(candidate.get("candidate_id", ""))
        result[candidate_id] = [
            ExpectationEvaluation.from_mapping(candidate_id, item)
            for item in candidate.get("expectations", [])
        ]
    return result


def axis_evaluations(data: dict[str, Any]) -> dict[str, list[AxisEvaluation]]:
    result: dict[str, list[AxisEvaluation]] = {}
    for candidate in data.get("candidate_axis_evaluations", []):
        candidate_id = str(candidate.get("candidate_id", ""))
        axes = candidate.get("axes", candidate.get("evaluation_axes", {}))
        if isinstance(axes, dict):
            result[candidate_id] = [
                AxisEvaluation.from_mapping(candidate_id, axis, item if isinstance(item, dict) else {"score": item})
                for axis, item in sorted(axes.items())
            ]
        else:
            result[candidate_id] = [
                AxisEvaluation.from_mapping(candidate_id, str(item.get("axis", "")), item)
                for item in axes
                if isinstance(item, dict)
            ]
    return result


def summarize_axis_evaluations(
    evaluations: dict[str, list[AxisEvaluation]],
    required_axes: tuple[str, ...] = DEFAULT_DESIGN_AXES,
) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for candidate_id, items in sorted(evaluations.items()):
        by_axis = {item.axis: item for item in items}
        missing_axes = [axis for axis in required_axes if axis not in by_axis]
        warning_count = sum(1 for item in items if item.evidence_quality == "assumption" or item.requires_validation)
        average = round(sum(item.score for item in items) / len(items), SCORE_ROUND_DECIMALS) if items else SCORE_MIN
        summary.append(
            {
                "candidate_id": candidate_id,
                "axis_average": average,
                "axis_count": len(items),
                "missing_axes": missing_axes,
                "evidence_warning_count": warning_count,
            }
        )
    return summary


def score_candidates(
    evaluations: dict[str, list[ExpectationEvaluation]],
    weights: list[ExpectationWeight],
    critical_expectations: list[CriticalExpectation],
    expectations: list[Expectation] | None = None,
) -> tuple[list[CandidateScore], list[ExpectationViolation]]:
    weight_by_id = {item.expectation_id: item.weight for item in weights}
    expectation_inputs = expectations or [
        Expectation(
            expectation_id=item.expectation_id,
            statement=item.expectation_id,
            category="Functional Expectation",
            success_conditions=(),
            failure_conditions=(),
            sources=(),
            confidence=DEFAULT_EXPECTATION_CONFIDENCE,
        )
        for item in weights
    ]
    violations = detect_expectation_violations(evaluations, expectation_inputs, critical_expectations)
    critical_counts: dict[str, int] = {}
    for violation in violations:
        if violation.severity == "critical":
            critical_counts[violation.candidate_id] = critical_counts.get(violation.candidate_id, 0) + 1
    scores: list[CandidateScore] = []
    for candidate_id, items in sorted(evaluations.items()):
        expectation_score = sum(weight_by_id.get(item.expectation_id, SCORE_MIN) * item.probability for item in items)
        evidence_warning_count = sum(1 for item in items if item.evidence_quality == "assumption" or item.requires_validation)
        unverified_count = sum(
            1
            for violation in violations
            if violation.candidate_id == candidate_id and violation.severity == "unverified"
        )
        critical_violation_count = critical_counts.get(candidate_id, 0)
        scores.append(
            CandidateScore(
                candidate_id=candidate_id,
                expectation_score=round(expectation_score, SCORE_ROUND_DECIMALS),
                critical_violation_count=critical_violation_count,
                unverified_count=unverified_count,
                evidence_warning_count=evidence_warning_count,
                recommendable=critical_violation_count == 0,
            )
        )
    return scores, violations


def serialize_dataclasses(items: list[Any]) -> list[dict[str, Any]]:
    return [asdict(item) for item in items]
