from __future__ import annotations

from .models import AxisEvaluation, CandidateScore, ExpectationEvaluation, ExpectationViolation, TradeOff


GAIN_THRESHOLD = 0.8
LOSS_THRESHOLD = 0.6

AXIS_LABELS = {
    "expectation_satisfaction": "Expectation satisfaction",
    "usability": "Usability",
    "product_identity": "Product identity",
    "delight": "Delight",
    "accessibility": "Accessibility",
    "implementation_cost": "Implementation cost efficiency",
    "maintenance_cost": "Maintenance cost efficiency",
    "technical_feasibility": "Technical feasibility",
}


def _axis_label(axis: str) -> str:
    return AXIS_LABELS.get(axis, axis.replace("_", " ").title())


def _impact(axis_by_name: dict[str, AxisEvaluation]) -> tuple[str, str]:
    implementation_cost = axis_by_name.get("implementation_cost")
    maintenance_cost = axis_by_name.get("maintenance_cost")
    technical_feasibility = axis_by_name.get("technical_feasibility")
    implementation_parts: list[str] = []
    future_parts: list[str] = []

    if implementation_cost and implementation_cost.score < LOSS_THRESHOLD:
        implementation_parts.append("implementation effort or delivery cost is a visible constraint")
    elif implementation_cost and implementation_cost.score >= GAIN_THRESHOLD:
        implementation_parts.append("implementation effort is comparatively light")

    if technical_feasibility and technical_feasibility.score < LOSS_THRESHOLD:
        implementation_parts.append("technical feasibility needs review before selection")
    elif technical_feasibility and technical_feasibility.score >= GAIN_THRESHOLD:
        implementation_parts.append("technical feasibility is comparatively strong")

    if maintenance_cost and maintenance_cost.score < LOSS_THRESHOLD:
        future_parts.append("maintenance burden may grow after implementation")
    elif maintenance_cost and maintenance_cost.score >= GAIN_THRESHOLD:
        future_parts.append("maintenance cost is expected to stay manageable")

    if not implementation_parts:
        implementation_parts.append("implementation impact is moderate or not fully evaluated")
    if not future_parts:
        future_parts.append("future impact is moderate or not fully evaluated")
    return "; ".join(implementation_parts), "; ".join(future_parts)


def analyze_tradeoffs(
    scores: list[CandidateScore],
    evaluations: dict[str, list[ExpectationEvaluation]],
    axes: dict[str, list[AxisEvaluation]],
    violations: list[ExpectationViolation],
) -> list[TradeOff]:
    score_by_candidate = {item.candidate_id: item for item in scores}
    violations_by_candidate: dict[str, list[ExpectationViolation]] = {}
    for violation in violations:
        violations_by_candidate.setdefault(violation.candidate_id, []).append(violation)

    candidate_ids = sorted(set(score_by_candidate) | set(evaluations) | set(axes) | set(violations_by_candidate))
    tradeoffs: list[TradeOff] = []
    for candidate_id in candidate_ids:
        axis_by_name = {item.axis: item for item in axes.get(candidate_id, [])}
        gained_values: list[str] = []
        lost_values: list[str] = []
        evidence_refs: list[str] = []
        human_decision_required: list[str] = []

        score = score_by_candidate.get(candidate_id)
        if score:
            if score.expectation_score >= GAIN_THRESHOLD:
                gained_values.append(f"High weighted expectation score ({score.expectation_score:.3f})")
            elif score.expectation_score < LOSS_THRESHOLD:
                lost_values.append(f"Low weighted expectation score ({score.expectation_score:.3f})")

        for axis, item in sorted(axis_by_name.items()):
            evidence_refs.extend(item.evidence_refs)
            label = _axis_label(axis)
            if item.score >= GAIN_THRESHOLD:
                gained_values.append(f"{label} is strong ({item.score:.2f})")
            elif item.score < LOSS_THRESHOLD:
                lost_values.append(f"{label} is weak or costly ({item.score:.2f})")
                if axis in {"accessibility", "implementation_cost", "maintenance_cost", "technical_feasibility"}:
                    human_decision_required.append(f"Review {label.lower()} trade-off")
            if item.requires_validation or item.evidence_quality == "assumption":
                human_decision_required.append(f"Validate {label.lower()} evidence")

        affected_expectations: list[str] = []
        for item in violations_by_candidate.get(candidate_id, []):
            affected_expectations.append(item.expectation_id)
            if item.severity == "positive-surprise":
                gained_values.append(f"Positive surprise hypothesis for {item.expectation_id}")
                human_decision_required.append(f"Review positive surprise hypothesis {item.expectation_id}")
                continue
            if item.severity in {"critical", "major"}:
                lost_values.append(f"{item.severity.title()} expectation risk for {item.expectation_id}")
                human_decision_required.append(f"Resolve {item.severity} risk for {item.expectation_id}")
            elif item.severity in {"minor", "ambiguous", "unverified"}:
                lost_values.append(f"{item.severity.title()} concern for {item.expectation_id}")
                human_decision_required.append(f"Decide handling for {item.severity} item {item.expectation_id}")

        if not gained_values:
            gained_values.append("No clear gained value has been identified yet")
        if not lost_values:
            lost_values.append("No clear lost value has been identified yet")
        if not human_decision_required:
            human_decision_required.append("Confirm candidate selection at Human Gate")

        implementation_impact, future_impact = _impact(axis_by_name)
        tradeoffs.append(
            TradeOff(
                candidate_id=candidate_id,
                gained_values=tuple(dict.fromkeys(gained_values)),
                lost_values=tuple(dict.fromkeys(lost_values)),
                affected_expectations=tuple(dict.fromkeys(affected_expectations)),
                implementation_impact=implementation_impact,
                future_impact=future_impact,
                human_decision_required=tuple(dict.fromkeys(human_decision_required)),
                evidence_refs=tuple(dict.fromkeys(evidence_refs)),
            )
        )
    return tradeoffs


def render_tradeoff_markdown(tradeoffs: list[dict[str, object]]) -> str:
    lines = ["# Trade-off Analysis", ""]
    if not tradeoffs:
        lines.append("No trade-off analysis is available.")
        return "\n".join(lines)
    for item in tradeoffs:
        lines.extend(
            [
                f"## {item.get('candidate_id', '')}",
                "",
                "Gained values:",
            ]
        )
        lines.extend(f"- {value}" for value in item.get("gained_values", []))
        lines.append("")
        lines.append("Lost values:")
        lines.extend(f"- {value}" for value in item.get("lost_values", []))
        lines.extend(
            [
                "",
                f"Implementation impact: {item.get('implementation_impact', '')}",
                f"Future impact: {item.get('future_impact', '')}",
                "",
                "Human decision required:",
            ]
        )
        lines.extend(f"- {value}" for value in item.get("human_decision_required", []))
        affected = ", ".join(str(value) for value in item.get("affected_expectations", [])) or "none"
        evidence = ", ".join(str(value) for value in item.get("evidence_refs", [])) or "none"
        lines.extend(["", f"Affected expectations: {affected}", f"Evidence refs: {evidence}", ""])
    return "\n".join(lines).rstrip() + "\n"
