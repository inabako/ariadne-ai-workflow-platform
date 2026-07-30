from __future__ import annotations

from .constants import (
    AMBIGUOUS_PROBABILITY_LOWER,
    AMBIGUOUS_PROBABILITY_UPPER,
    COUNT_DEFAULT,
    COUNT_INCREMENT,
    EXPECTATION_VIOLATION_SEVERITY_ORDER,
    EXPECTATION_VIOLATION_SEVERITY_ORDER_DEFAULT,
    LOW_CONFIDENCE_THRESHOLD,
    MAJOR_VIOLATION_THRESHOLD,
    MINOR_VIOLATION_THRESHOLD,
    POSITIVE_SURPRISE_THRESHOLD,
)
from .models import CriticalExpectation, Expectation, ExpectationEvaluation, ExpectationViolation


def _expectation_statement(expectations: dict[str, Expectation], expectation_id: str) -> str:
    expectation = expectations.get(expectation_id)
    return expectation.statement if expectation else expectation_id


def detect_expectation_violations(
    evaluations: dict[str, list[ExpectationEvaluation]],
    expectations: list[Expectation],
    critical_expectations: list[CriticalExpectation],
) -> list[ExpectationViolation]:
    expectation_by_id = {item.expectation_id: item for item in expectations}
    expected_ids = set(expectation_by_id)
    critical_by_id = {item.expectation_id: item for item in critical_expectations}
    expected_ids.update(critical_by_id)
    violations: list[ExpectationViolation] = []

    for candidate_id, items in sorted(evaluations.items()):
        evaluation_by_id = {item.expectation_id: item for item in items}
        missing_ids = sorted(expected_ids - set(evaluation_by_id))
        for expectation_id in missing_ids:
            if expectation_id in critical_by_id:
                violations.append(
                    ExpectationViolation(
                        candidate_id=candidate_id,
                        expectation_id=expectation_id,
                        severity="critical",
                        description="Critical expectation is not evaluated.",
                        user_impact="Human Gate cannot treat this candidate as recommendable.",
                        recommendation="Add evaluation evidence before recommendation.",
                    )
                )
            else:
                violations.append(
                    ExpectationViolation(
                        candidate_id=candidate_id,
                        expectation_id=expectation_id,
                        severity="unverified",
                        description="Expectation is not evaluated for this candidate.",
                        user_impact="The comparison is incomplete for this user expectation.",
                        recommendation="Add probability, confidence, and evidence before Human Gate approval.",
                    )
                )

        for item in sorted(items, key=lambda value: value.expectation_id):
            expectation_label = _expectation_statement(expectation_by_id, item.expectation_id)
            critical = critical_by_id.get(item.expectation_id)
            if critical and item.probability < critical.minimum_probability:
                violations.append(
                    ExpectationViolation(
                        candidate_id=candidate_id,
                        expectation_id=item.expectation_id,
                        severity="critical",
                        description=(
                            f"Probability {item.probability:.3f} is below "
                            f"minimum {critical.minimum_probability:.3f}."
                        ),
                        user_impact=critical.reason,
                        recommendation=critical.failure_action,
                    )
                )
                continue

            if item.requires_validation or item.evidence_quality == "assumption":
                violations.append(
                    ExpectationViolation(
                        candidate_id=candidate_id,
                        expectation_id=item.expectation_id,
                        severity="unverified",
                        description="Expectation evaluation depends on assumption or still requires validation.",
                        user_impact=f"{expectation_label} has not been supported by sufficient evidence.",
                        recommendation="Collect prototype, test, log, or human-review evidence.",
                    )
                )

            if (
                item.confidence < LOW_CONFIDENCE_THRESHOLD
                or AMBIGUOUS_PROBABILITY_LOWER <= item.probability <= AMBIGUOUS_PROBABILITY_UPPER
            ):
                violations.append(
                    ExpectationViolation(
                        candidate_id=candidate_id,
                        expectation_id=item.expectation_id,
                        severity="ambiguous",
                        description=(
                            f"Probability {item.probability:.3f} or confidence {item.confidence:.3f} "
                            "is too uncertain for a clean design judgment."
                        ),
                        user_impact=f"{expectation_label} may be interpreted differently by reviewers or users.",
                        recommendation="Clarify the interaction, add evidence, or split the expectation.",
                    )
                )
            elif item.probability < MAJOR_VIOLATION_THRESHOLD:
                violations.append(
                    ExpectationViolation(
                        candidate_id=candidate_id,
                        expectation_id=item.expectation_id,
                        severity="major",
                        description=f"Probability {item.probability:.3f} is below the major violation threshold.",
                        user_impact=f"{expectation_label} is unlikely to be satisfied.",
                        recommendation="Revise this candidate or explain why the expectation should be relaxed.",
                    )
                )
            elif item.probability < MINOR_VIOLATION_THRESHOLD:
                violations.append(
                    ExpectationViolation(
                        candidate_id=candidate_id,
                        expectation_id=item.expectation_id,
                        severity="minor",
                        description=f"Probability {item.probability:.3f} is below the minor violation threshold.",
                        user_impact=f"{expectation_label} may be partially satisfied but needs attention.",
                        recommendation="Improve the candidate or document the trade-off.",
                    )
                )
            elif (
                item.probability >= POSITIVE_SURPRISE_THRESHOLD
                and item.evidence_refs
                and item.expectation_id not in critical_by_id
            ):
                violations.append(
                    ExpectationViolation(
                        candidate_id=candidate_id,
                        expectation_id=item.expectation_id,
                        severity="positive-surprise",
                        description=f"Probability {item.probability:.3f} indicates a strong positive outcome.",
                        user_impact=f"{expectation_label} may create additional user value.",
                        recommendation="Keep this as a hypothesis for Human Review instead of treating it as fact.",
                    )
                )

    return sorted(
        violations,
        key=lambda item: (
            EXPECTATION_VIOLATION_SEVERITY_ORDER.get(item.severity, EXPECTATION_VIOLATION_SEVERITY_ORDER_DEFAULT),
            item.candidate_id,
            item.expectation_id,
        ),
    )


def summarize_violations(violations: list[ExpectationViolation]) -> list[dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for item in violations:
        summary = result.setdefault(
            item.candidate_id,
            {
                "candidate_id": item.candidate_id,
                "critical": COUNT_DEFAULT,
                "major": COUNT_DEFAULT,
                "minor": COUNT_DEFAULT,
                "ambiguous": COUNT_DEFAULT,
                "unverified": COUNT_DEFAULT,
                "positive_surprise": COUNT_DEFAULT,
            },
        )
        key = "positive_surprise" if item.severity == "positive-surprise" else item.severity
        summary[key] = int(summary.get(key, COUNT_DEFAULT)) + COUNT_INCREMENT
    return [result[candidate_id] for candidate_id in sorted(result)]
