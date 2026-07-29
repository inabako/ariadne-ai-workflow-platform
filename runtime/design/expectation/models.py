from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def _probability(value: Any, *, field: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{field} must be between 0.0 and 1.0: {number}")
    return number


@dataclass(frozen=True)
class Expectation:
    expectation_id: str
    statement: str
    category: str
    success_conditions: tuple[str, ...]
    failure_conditions: tuple[str, ...]
    sources: tuple[str, ...]
    confidence: float

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "Expectation":
        return cls(
            expectation_id=str(data.get("expectation_id") or data.get("id") or ""),
            statement=str(data.get("statement", "")),
            category=str(data.get("category", "Functional Expectation")),
            success_conditions=_tuple(data.get("success_conditions", data.get("success_condition"))),
            failure_conditions=_tuple(data.get("failure_conditions", data.get("failure_condition"))),
            sources=_tuple(data.get("sources", data.get("source"))),
            confidence=_probability(data.get("confidence", 1.0), field="confidence"),
        )


@dataclass(frozen=True)
class UsageContext:
    context_id: str
    actor: str
    situation: str
    goal: str
    confidence: float
    evidence_refs: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "UsageContext":
        return cls(
            context_id=str(data.get("context_id") or data.get("id") or ""),
            actor=str(data.get("actor", "")),
            situation=str(data.get("situation", "")),
            goal=str(data.get("goal", "")),
            confidence=_probability(data.get("confidence", 1.0), field="confidence"),
            evidence_refs=_tuple(data.get("evidence_refs", data.get("evidence"))),
        )


@dataclass(frozen=True)
class ExpectationSet:
    expectations: tuple[Expectation, ...]
    conflicts: tuple[dict[str, Any], ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ExpectationSet":
        return cls(
            expectations=tuple(Expectation.from_mapping(item) for item in data.get("expectations", [])),
            conflicts=tuple(dict(item) for item in data.get("conflicts", [])),
        )


@dataclass(frozen=True)
class ExpectationWeight:
    expectation_id: str
    weight: float
    rationale: tuple[str, ...]
    decided_by: str

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ExpectationWeight":
        decided_by = data.get("decided_by", "")
        if isinstance(decided_by, dict):
            decided_by = decided_by.get("type", "")
        return cls(
            expectation_id=str(data.get("expectation_id") or data.get("id") or ""),
            weight=_probability(data.get("weight", 0.0), field="weight"),
            rationale=_tuple(data.get("rationale")),
            decided_by=str(decided_by or "ariadne-initial"),
        )


@dataclass(frozen=True)
class CriticalExpectation:
    expectation_id: str
    minimum_probability: float
    failure_action: str
    reason: str
    human_override_allowed: bool

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "CriticalExpectation":
        return cls(
            expectation_id=str(data.get("expectation_id") or data.get("id") or ""),
            minimum_probability=_probability(data.get("minimum_probability", 1.0), field="minimum_probability"),
            failure_action=str(data.get("failure_action", "reject-candidate")),
            reason=str(data.get("reason", "")),
            human_override_allowed=bool(data.get("human_override_allowed", False)),
        )


@dataclass(frozen=True)
class DesignCandidate:
    candidate_id: str
    concept: str
    target_users: tuple[str, ...]
    main_flow: tuple[str, ...]
    primary_expectations: tuple[str, ...]
    emotional_priority: tuple[str, ...]
    technical_notes: tuple[str, ...]
    implementation_cost_notes: tuple[str, ...]
    known_risks: tuple[str, ...]
    status: str

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "DesignCandidate":
        return cls(
            candidate_id=str(data.get("candidate_id") or data.get("id") or ""),
            concept=str(data.get("concept", "")),
            target_users=_tuple(data.get("target_users")),
            main_flow=_tuple(data.get("main_flow")),
            primary_expectations=_tuple(data.get("primary_expectations")),
            emotional_priority=_tuple(data.get("emotional_priority")),
            technical_notes=_tuple(data.get("technical_notes")),
            implementation_cost_notes=_tuple(data.get("implementation_cost_notes")),
            known_risks=_tuple(data.get("known_risks")),
            status=str(data.get("status", "draft")),
        )


@dataclass(frozen=True)
class FeasibilityReport:
    candidate_id: str
    status: str
    implementation_feasibility: str
    standard_components: str
    accessibility: str
    testability: str
    future_extensibility: str
    constraints: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "FeasibilityReport":
        return cls(
            candidate_id=str(data.get("candidate_id") or data.get("id") or ""),
            status=str(data.get("status", "constrained")),
            implementation_feasibility=str(data.get("implementation_feasibility", "needs-review")),
            standard_components=str(data.get("standard_components", "needs-review")),
            accessibility=str(data.get("accessibility", "needs-review")),
            testability=str(data.get("testability", "needs-review")),
            future_extensibility=str(data.get("future_extensibility", "needs-review")),
            constraints=_tuple(data.get("constraints")),
            evidence_refs=_tuple(data.get("evidence_refs", data.get("evidence"))),
        )


@dataclass(frozen=True)
class ExpectationEvaluation:
    candidate_id: str
    expectation_id: str
    probability: float
    confidence: float
    evidence_refs: tuple[str, ...]
    evidence_quality: str
    requires_validation: bool

    @classmethod
    def from_mapping(cls, candidate_id: str, data: dict[str, Any]) -> "ExpectationEvaluation":
        evidence_refs = _tuple(data.get("evidence_refs", data.get("evidence")))
        evidence_quality = str(data.get("evidence_quality") or ("provided" if evidence_refs else "assumption"))
        requires_validation = bool(data.get("requires_validation", not evidence_refs))
        return cls(
            candidate_id=str(data.get("candidate_id") or candidate_id),
            expectation_id=str(data.get("expectation_id") or data.get("id") or ""),
            probability=_probability(data.get("probability", 0.0), field="probability"),
            confidence=_probability(data.get("confidence", 1.0), field="confidence"),
            evidence_refs=evidence_refs,
            evidence_quality=evidence_quality,
            requires_validation=requires_validation,
        )


@dataclass(frozen=True)
class AxisEvaluation:
    candidate_id: str
    axis: str
    score: float
    rationale: str
    evidence_refs: tuple[str, ...]
    evidence_quality: str
    requires_validation: bool

    @classmethod
    def from_mapping(cls, candidate_id: str, axis: str, data: dict[str, Any]) -> "AxisEvaluation":
        evidence_refs = _tuple(data.get("evidence_refs", data.get("evidence")))
        evidence_quality = str(data.get("evidence_quality") or ("provided" if evidence_refs else "assumption"))
        requires_validation = bool(data.get("requires_validation", not evidence_refs))
        return cls(
            candidate_id=str(data.get("candidate_id") or candidate_id),
            axis=str(data.get("axis") or axis),
            score=_probability(data.get("score", 0.0), field="score"),
            rationale=str(data.get("rationale", "")),
            evidence_refs=evidence_refs,
            evidence_quality=evidence_quality,
            requires_validation=requires_validation,
        )


@dataclass(frozen=True)
class ExpectationViolation:
    candidate_id: str
    expectation_id: str
    severity: str
    description: str
    user_impact: str
    recommendation: str


@dataclass(frozen=True)
class PositiveSurpriseHypothesis:
    candidate_id: str
    expectation_id: str
    description: str
    evidence_refs: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "PositiveSurpriseHypothesis":
        return cls(
            candidate_id=str(data.get("candidate_id", "")),
            expectation_id=str(data.get("expectation_id", "")),
            description=str(data.get("description", data.get("claim", ""))),
            evidence_refs=_tuple(data.get("evidence_refs", data.get("evidence"))),
        )


@dataclass(frozen=True)
class CandidateScore:
    candidate_id: str
    expectation_score: float
    critical_violation_count: int
    unverified_count: int
    evidence_warning_count: int
    recommendable: bool


@dataclass(frozen=True)
class TradeOff:
    candidate_id: str
    gained_values: tuple[str, ...]
    lost_values: tuple[str, ...]
    affected_expectations: tuple[str, ...]
    implementation_impact: str
    future_impact: str
    human_decision_required: tuple[str, ...]
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class DesignComparison:
    work_id: str
    recommended_candidate: str
    human_decision_items: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "DesignComparison":
        return cls(
            work_id=str(data.get("work_id", "")),
            recommended_candidate=str(data.get("recommended_candidate", "")),
            human_decision_items=_tuple(data.get("human_decision_items")),
        )


@dataclass(frozen=True)
class HumanDecision:
    status: str
    selected_candidate: str
    decision_action: str
    decision_items: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "HumanDecision":
        return cls(
            status=str(data.get("status", "pending")),
            selected_candidate=str(data.get("selected_candidate", "")),
            decision_action=str(data.get("decision_action", "")),
            decision_items=_tuple(data.get("decision_items")),
        )


@dataclass(frozen=True)
class InteractionContract:
    contract_id: str
    related_expectations: tuple[str, ...]
    given: dict[str, Any]
    when: dict[str, Any]
    then: dict[str, Any]
    must_not: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "InteractionContract":
        return cls(
            contract_id=str(data.get("contract_id") or data.get("id") or ""),
            related_expectations=_tuple(data.get("related_expectations")),
            given=dict(data.get("given", {})),
            when=dict(data.get("when", {})),
            then=dict(data.get("then", {})),
            must_not=_tuple(data.get("must_not")),
        )


@dataclass(frozen=True)
class ExpectationVerification:
    candidate_id: str
    expectation_id: str
    design_probability: float
    verified_result: float | None
    evidence_refs: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ExpectationVerification":
        verified = data.get("verified_result")
        return cls(
            candidate_id=str(data.get("candidate_id", "")),
            expectation_id=str(data.get("expectation_id", "")),
            design_probability=_probability(data.get("design_probability", 0.0), field="design_probability"),
            verified_result=None if verified is None else _probability(verified, field="verified_result"),
            evidence_refs=_tuple(data.get("evidence_refs", data.get("evidence"))),
        )


@dataclass(frozen=True)
class ExpectationFeedback:
    candidate_id: str
    expectation_id: str
    predicted_probability: float
    observed_probability: float | None
    knowledge_candidate: bool

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ExpectationFeedback":
        observed = data.get("observed_probability")
        return cls(
            candidate_id=str(data.get("candidate_id", "")),
            expectation_id=str(data.get("expectation_id", "")),
            predicted_probability=_probability(data.get("predicted_probability", 0.0), field="predicted_probability"),
            observed_probability=None if observed is None else _probability(observed, field="observed_probability"),
            knowledge_candidate=bool(data.get("knowledge_candidate", False)),
        )
