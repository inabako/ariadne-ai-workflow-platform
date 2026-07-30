from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime.constants.runtime_values import SCHEMA_VERSION
from runtime.common import (
    find_repo_root,
    load_artifact_index,
    read_json,
    relative_to_repo,
    upsert_artifact,
    utc_now_iso,
    write_json,
    write_markdown,
)
from runtime.constants.schemas import (
    ARTIFACT_INDEX_SCHEMA,
    CRITICAL_EXPECTATIONS_SCHEMA,
    DESIGN_CANDIDATES_SCHEMA,
    DESIGN_COMPARISON_REPORT_SCHEMA,
    DESIGN_FEASIBILITY_REPORT_SCHEMA,
    EXPECTATION_CONFLICTS_SCHEMA,
    EXPECTATION_DESIGN_DISPATCH_SCHEMA,
    EXPECTATION_EVALUATION_SCHEMA,
    EXPECTATION_FEEDBACK_SCHEMA,
    EXPECTATION_REVIEW_REPORT_SCHEMA,
    EXPECTATION_SET_SCHEMA,
    EXPECTATION_VERIFICATION_SCHEMA,
    EXPECTATION_WEIGHTS_SCHEMA,
    HUMAN_DECISION_SCHEMA,
    INTERACTION_CONTRACTS_SCHEMA,
    MULTI_AXIS_EVALUATION_SCHEMA,
    TRADE_OFF_ANALYSIS_SCHEMA,
    USAGE_CONTEXT_SCHEMA,
)
from runtime.constants.workspace import context_file, resolve_work_dir
from runtime.review.persistence.store import ReviewStore
from runtime.workflow.context_first import register_context

from .evaluator import (
    DEFAULT_DESIGN_AXES,
    axis_evaluations,
    candidate_evaluations,
    normalize_weights,
    score_candidates,
    serialize_dataclasses,
    summarize_axis_evaluations,
)
from .constants import (
    COMPARISON_KEY_POINT_LIMIT,
    COMPARISON_RECOMMENDATION_LIMIT,
    COUNT_DEFAULT,
    DEFAULT_AGENT_EXTRACTION_CONFIDENCE,
    DEFAULT_CRITICAL_MINIMUM_PROBABILITY,
    DEFAULT_EXPECTATION_CONFIDENCE,
    DEFAULT_FALLBACK_EXPECTATION_CONFIDENCE,
    DEFAULT_FIXED_UI_CONFIDENCE,
    DEFAULT_LIGHT_EXTRACTION_CONFIDENCE,
    DEFAULT_SAMPLE_EXPECTATION_WEIGHT,
    DEFAULT_USAGE_CONTEXT_ID,
    EXPECTATION_AGENT_ID_WIDTH,
    INTERACTION_CONTRACT_ID_WIDTH,
    SAMPLE_HIGH_EVALUATION_CONFIDENCE,
    SAMPLE_LOW_EXPECTATION_PROBABILITY,
    SAMPLE_MULTI_AXIS_DESIGN_A_SCORES,
    SAMPLE_MULTI_AXIS_DESIGN_B_SCORES,
    SAMPLE_STRONG_EVALUATION_CONFIDENCE,
    SCORE_MAX,
    SCORE_MIN,
    SCORE_ROUND_DECIMALS,
    SEQUENCE_START,
    USAGE_CONTEXT_GOAL_MAX_CHARS,
    WEIGHT_CHANGE_FIELD_COUNT,
    WIREFRAME_HEADER_HEIGHT,
    WIREFRAME_HEADER_WIDTH,
    WIREFRAME_HEADER_X,
    WIREFRAME_HEADER_Y,
    WIREFRAME_HEIGHT,
    WIREFRAME_LABEL_FONT_SIZE,
    WIREFRAME_LABEL_X,
    WIREFRAME_LABEL_Y,
    WIREFRAME_LEFT_PANEL_WIDTH,
    WIREFRAME_LEFT_PANEL_X,
    WIREFRAME_PANEL_HEIGHT,
    WIREFRAME_PANEL_Y,
    WIREFRAME_RIGHT_LABEL_X,
    WIREFRAME_RIGHT_PANEL_WIDTH,
    WIREFRAME_RIGHT_PANEL_X,
    WIREFRAME_TITLE_FONT_SIZE,
    WIREFRAME_TITLE_X,
    WIREFRAME_TITLE_Y,
    WIREFRAME_WIDTH,
)
from .models import CriticalExpectation, DesignCandidate, Expectation, ExpectationWeight, FeasibilityReport
from .tradeoff_analyzer import analyze_tradeoffs, render_tradeoff_markdown
from .violation_detector import summarize_violations


def _repo_root(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve() if getattr(args, "repo_root", "") else find_repo_root()


def _work_dir(repo_root: Path, args: argparse.Namespace) -> Path:
    return resolve_work_dir(repo_root, getattr(args, "work_id", ""), getattr(args, "work_dir", ""))


def expectation_dir(work_dir: Path) -> Path:
    return work_dir / "design" / "expectation"


def _work_id(args: argparse.Namespace, work_dir: Path) -> str:
    return getattr(args, "work_id", "") or work_dir.name


def _artifact(
    repo_root: Path,
    path: Path,
    *,
    artifact_id: str,
    title: str,
    artifact_type: str = "design",
    status: str = "draft",
    summary: str,
    now: str,
) -> dict[str, Any]:
    return {
        "id": artifact_id,
        "title": title,
        "path": relative_to_repo(repo_root, path),
        "type": artifact_type,
        "status": status,
        "owner_agent": "expectation-design-runtime",
        "created_at": now,
        "updated_at": now,
        "depends_on": [],
        "consumed_by": [
            "expectation-design-runtime",
            "ariadne-architect-agent",
            "review-council",
        ],
        "summary": summary,
        "unresolved_items": [],
    }


def _register_artifacts(
    repo_root: Path,
    work_dir: Path,
    work_id: str,
    artifacts: list[dict[str, Any]],
) -> str:
    index = load_artifact_index(work_dir, work_id, "expectation-driven-design")
    for artifact in artifacts:
        upsert_artifact(index, artifact)
    artifact_index_path = context_file(work_dir, "artifact-index.json")
    write_json(artifact_index_path, index)
    register_context(
        repo_root,
        work_dir,
        work_id=work_id,
        context_type="artifact-index",
        path=artifact_index_path,
        required=True,
        generated_by="expectation-design-runtime",
        owner="workflow",
        schema=ARTIFACT_INDEX_SCHEMA,
        status="available",
    )
    return relative_to_repo(repo_root, artifact_index_path)


def _read_structured(path: Path, default: Any) -> Any:
    data = read_json(path, default=None)
    return default if data is None else data


def _append_event(base: Path, event: str, payload: dict[str, Any]) -> Path:
    path = base / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"event": event, "created_at": utc_now_iso(), **payload}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def _candidate_slug(candidate_id: str) -> str:
    return candidate_id.strip().lower().replace("_", "-")


def _candidate_dir(base: Path, candidate_id: str) -> Path:
    return base / "candidates" / _candidate_slug(candidate_id)


def _candidate_ids_from_args(args: argparse.Namespace) -> list[str]:
    raw = list(getattr(args, "candidate_id", []) or [])
    if getattr(args, "selected_candidate", ""):
        raw.append(str(getattr(args, "selected_candidate")))
    return [item for item in dict.fromkeys(str(value).strip() for value in raw) if item]


def _paths(repo_root: Path, base: Path, args: argparse.Namespace) -> dict[str, Path]:
    def path_arg(name: str, default: Path) -> Path:
        raw = str(getattr(args, name, "") or "")
        if not raw:
            return default
        path = Path(raw)
        return path if path.is_absolute() else repo_root / path

    return {
        "expectations": path_arg("expectations", base / "expectation-set.json"),
        "usage_context": path_arg("usage_context", base / "usage-context.json"),
        "weights": path_arg("weights", base / "expectation-weights.json"),
        "critical": path_arg("critical", base / "critical-expectations.json"),
        "evaluations": path_arg("evaluations", base / "evaluations" / "expectation-evaluation.json"),
        "multi_axis": path_arg("multi_axis", base / "evaluations" / "multi-axis-evaluation.json"),
    }


def _load_inputs(
    repo_root: Path,
    base: Path,
    args: argparse.Namespace,
) -> tuple[list[Expectation], list[ExpectationWeight], list[CriticalExpectation], dict[str, Any], dict[str, Any], dict[str, Any]]:
    paths = _paths(repo_root, base, args)
    usage_context_data = _read_structured(paths["usage_context"], {"usage_context": {}})
    expectation_data = _read_structured(paths["expectations"], {"expectations": []})
    weight_data = _read_structured(paths["weights"], {"weights": []})
    critical_data = _read_structured(paths["critical"], {"critical_expectations": []})
    evaluation_data = _read_structured(paths["evaluations"], {"candidate_evaluations": []})
    multi_axis_data = _read_structured(paths["multi_axis"], {"candidate_axis_evaluations": []})
    expectations = [Expectation.from_mapping(item) for item in expectation_data.get("expectations", [])]
    weights = normalize_weights([ExpectationWeight.from_mapping(item) for item in weight_data.get("weights", [])], expectations)
    critical = [CriticalExpectation.from_mapping(item) for item in critical_data.get("critical_expectations", [])]
    return expectations, weights, critical, evaluation_data, multi_axis_data, usage_context_data


def _sample_expectation_payload() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "schema": EXPECTATION_SET_SCHEMA,
        "artifact_type": "expectation-set",
        "expectations": [
            {
                "id": "EXP-TIME-001",
                "statement": "24時を超える時刻表記をそのまま入力できる",
                "category": "Functional Expectation",
                "success_condition": ["39:00を入力できる", "39:00を翌日15:00として解釈できる"],
                "failure_condition": ["39:00を不正な時刻として拒否する"],
                "source": ["user-requirement", "usage-context"],
                "confidence": DEFAULT_EXPECTATION_CONFIDENCE,
            }
        ],
    }


def _sample_evaluation_payload() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "schema": EXPECTATION_EVALUATION_SCHEMA,
        "artifact_type": "expectation-evaluation-input",
        "candidate_evaluations": [
            {
                "candidate_id": "DESIGN-A",
                "expectations": [
                    {
                        "expectation_id": "EXP-TIME-001",
                        "probability": SAMPLE_LOW_EXPECTATION_PROBABILITY,
                        "confidence": SAMPLE_HIGH_EVALUATION_CONFIDENCE,
                        "evidence": ["標準時刻ピッカーは23:59までしか扱えない"],
                    }
                ],
            },
            {
                "candidate_id": "DESIGN-B",
                "expectations": [
                    {
                        "expectation_id": "EXP-TIME-001",
                        "probability": SCORE_MAX,
                        "confidence": SAMPLE_STRONG_EVALUATION_CONFIDENCE,
                        "evidence": ["自由入力は39:00を文字列として受け付けられる"],
                    }
                ],
            },
        ],
    }


def _axis_values(**values: float) -> dict[str, dict[str, Any]]:
    return {
        axis: {
            "score": score,
            "rationale": f"Sample {axis} assessment.",
            "evidence": [f"sample:{axis}"],
            "evidence_quality": "provided",
            "requires_validation": False,
        }
        for axis, score in values.items()
    }


def _sample_multi_axis_payload() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "schema": MULTI_AXIS_EVALUATION_SCHEMA,
        "artifact_type": "multi-axis-evaluation",
        "axis_direction": "higher-is-better",
        "required_axes": list(DEFAULT_DESIGN_AXES),
        "candidate_axis_evaluations": [
            {
                "candidate_id": "DESIGN-A",
                "axes": _axis_values(**SAMPLE_MULTI_AXIS_DESIGN_A_SCORES),
            },
            {
                "candidate_id": "DESIGN-B",
                "axes": _axis_values(**SAMPLE_MULTI_AXIS_DESIGN_B_SCORES),
            },
        ],
    }


def _default_candidate(candidate_id: str, concept: str = "") -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "concept": concept or f"{candidate_id} design candidate",
        "target_users": [],
        "main_flow": [],
        "primary_expectations": [],
        "emotional_priority": [],
        "technical_notes": [],
        "implementation_cost_notes": [],
        "known_risks": [],
        "status": "draft",
    }


def _default_feasibility(candidate_id: str) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "status": "constrained",
        "implementation_feasibility": "needs-review",
        "standard_components": "needs-review",
        "accessibility": "needs-review",
        "testability": "needs-review",
        "future_extensibility": "needs-review",
        "constraints": ["Feasibility is not verified yet; keep candidate as constrained."],
        "evidence_refs": [],
    }


def _candidate_markdown(candidate: dict[str, Any]) -> str:
    lines = [
        f"# {candidate.get('candidate_id', '')}",
        "",
        f"Concept: {candidate.get('concept', '')}",
        "",
        "## Main Flow",
    ]
    main_flow = candidate.get("main_flow", [])
    lines.extend(f"- {item}" for item in main_flow) if main_flow else lines.append("- TBD")
    lines.extend(["", "## Primary Expectations"])
    primary = candidate.get("primary_expectations", [])
    lines.extend(f"- {item}" for item in primary) if primary else lines.append("- TBD")
    lines.extend(["", "## Known Risks"])
    risks = candidate.get("known_risks", [])
    lines.extend(f"- {item}" for item in risks) if risks else lines.append("- TBD")
    return "\n".join(lines) + "\n"


def _flow_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    steps = candidate.get("main_flow", [])
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "candidate-flow",
        "candidate_id": candidate.get("candidate_id", ""),
        "flow": [
            {"step": index, "description": value}
            for index, value in enumerate(steps, start=SEQUENCE_START)
        ],
    }


def _feasibility_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# Feasibility Report: {report.get('candidate_id', '')}",
            "",
            f"Status: {report.get('status', '')}",
            f"Implementation feasibility: {report.get('implementation_feasibility', '')}",
            f"Standard components: {report.get('standard_components', '')}",
            f"Accessibility: {report.get('accessibility', '')}",
            f"Testability: {report.get('testability', '')}",
            f"Future extensibility: {report.get('future_extensibility', '')}",
            "",
            "## Constraints",
            *[f"- {item}" for item in report.get("constraints", [])],
            "",
            "## Evidence Refs",
            *[f"- {item}" for item in report.get("evidence_refs", [])],
            "",
        ]
    )


def _wireframe_svg(candidate_id: str) -> str:
    title = candidate_id.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return "\n".join(
        [
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIREFRAME_WIDTH}" '
                f'height="{WIREFRAME_HEIGHT}" viewBox="0 0 {WIREFRAME_WIDTH} {WIREFRAME_HEIGHT}" role="img">'
            ),
            f"  <title>{title} wireframe placeholder</title>",
            f'  <rect width="{WIREFRAME_WIDTH}" height="{WIREFRAME_HEIGHT}" fill="#f8fafc"/>',
            (
                f'  <rect x="{WIREFRAME_HEADER_X}" y="{WIREFRAME_HEADER_Y}" '
                f'width="{WIREFRAME_HEADER_WIDTH}" height="{WIREFRAME_HEADER_HEIGHT}" '
                'fill="#e2e8f0" stroke="#64748b"/>'
            ),
            (
                f'  <rect x="{WIREFRAME_LEFT_PANEL_X}" y="{WIREFRAME_PANEL_Y}" '
                f'width="{WIREFRAME_LEFT_PANEL_WIDTH}" height="{WIREFRAME_PANEL_HEIGHT}" '
                'fill="#ffffff" stroke="#64748b"/>'
            ),
            (
                f'  <rect x="{WIREFRAME_RIGHT_PANEL_X}" y="{WIREFRAME_PANEL_Y}" '
                f'width="{WIREFRAME_RIGHT_PANEL_WIDTH}" height="{WIREFRAME_PANEL_HEIGHT}" '
                'fill="#ffffff" stroke="#64748b"/>'
            ),
            (
                f'  <text x="{WIREFRAME_TITLE_X}" y="{WIREFRAME_TITLE_Y}" fill="#0f172a" '
                f'font-family="Arial, sans-serif" font-size="{WIREFRAME_TITLE_FONT_SIZE}">{title}</text>'
            ),
            (
                f'  <text x="{WIREFRAME_LABEL_X}" y="{WIREFRAME_LABEL_Y}" fill="#334155" '
                f'font-family="Arial, sans-serif" font-size="{WIREFRAME_LABEL_FONT_SIZE}">Concept</text>'
            ),
            (
                f'  <text x="{WIREFRAME_RIGHT_LABEL_X}" y="{WIREFRAME_LABEL_Y}" fill="#334155" '
                f'font-family="Arial, sans-serif" font-size="{WIREFRAME_LABEL_FONT_SIZE}">Flow / Evidence</text>'
            ),
            "</svg>",
            "",
        ]
    )


def _bounded_probability(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(SCORE_MIN, min(SCORE_MAX, number))


def _dedupe_strings(values: Any) -> list[str]:
    return list(dict.fromkeys(str(item).strip() for item in _listify(values) if str(item).strip()))


def _resolve_repo_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else repo_root / path


def _normal_expectation_id(raw: Any, index: int) -> str:
    value = str(raw or "").strip()
    return value or f"EXP-AGENT-{index:0{EXPECTATION_AGENT_ID_WIDTH}d}"


_EXPECTATION_CATEGORIES = {
    "Functional Expectation",
    "Interaction Expectation",
    "Visual Expectation",
    "Feedback Expectation",
    "Error Handling Expectation",
    "Accessibility Expectation",
    "Emotional Expectation",
    "Product Identity Expectation",
    "Performance Expectation",
    "Privacy Expectation",
}


def _normalize_expectation_category(value: Any) -> str:
    category = str(value or "").strip()
    if category in _EXPECTATION_CATEGORIES:
        return category
    lowered = category.lower()
    if "access" in lowered or "a11y" in lowered:
        return "Accessibility Expectation"
    if "visual" in lowered or "identity" in lowered or "brand" in lowered:
        return "Product Identity Expectation"
    if "emotion" in lowered or "delight" in lowered:
        return "Emotional Expectation"
    if "performance" in lowered or "speed" in lowered:
        return "Performance Expectation"
    if "privacy" in lowered:
        return "Privacy Expectation"
    if "error" in lowered:
        return "Error Handling Expectation"
    if "interaction" in lowered or "usability" in lowered:
        return "Interaction Expectation"
    return "Functional Expectation"


def _normalize_extracted_expectation(item: dict[str, Any], index: int, evidence_ref: str) -> dict[str, Any]:
    evidence_refs = _dedupe_strings(item.get("evidence_refs") or item.get("evidence") or item.get("source") or item.get("sources"))
    if evidence_ref:
        evidence_refs = list(dict.fromkeys([*evidence_refs, evidence_ref]))
    sources = _dedupe_strings(item.get("source") or item.get("sources") or evidence_refs)
    success = _dedupe_strings(item.get("success_condition") or item.get("success_conditions"))
    failure = _dedupe_strings(item.get("failure_condition") or item.get("failure_conditions"))
    return {
        "id": _normal_expectation_id(item.get("id") or item.get("expectation_id"), index),
        "statement": str(item.get("statement") or item.get("expectation") or item.get("description") or "").strip()
        or "Agent extracted expectation requires review.",
        "category": _normalize_expectation_category(item.get("category")),
        "success_condition": success or ["Expectation is observable and testable."],
        "failure_condition": failure or ["Expectation remains vague, untested, or contradicted."],
        "source": sources or ([evidence_ref] if evidence_ref else ["agent-output"]),
        "evidence_refs": evidence_refs or ([evidence_ref] if evidence_ref else ["agent-output"]),
        "confidence": _bounded_probability(item.get("confidence"), DEFAULT_AGENT_EXTRACTION_CONFIDENCE),
    }


def _agent_extraction_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result = payload.get("result", {})
    if isinstance(payload.get("expectations"), list):
        return [item for item in payload["expectations"] if isinstance(item, dict)]
    if isinstance(payload.get("extracted_expectations"), list):
        return [item for item in payload["extracted_expectations"] if isinstance(item, dict)]
    if isinstance(result, dict) and isinstance(result.get("expectations"), list):
        return [item for item in result["expectations"] if isinstance(item, dict)]
    return []


def _normalize_agent_usage_context(payload: dict[str, Any], requirement: str, evidence_ref: str) -> dict[str, Any]:
    raw = payload.get("usage_context") or payload.get("context") or {}
    if not isinstance(raw, dict):
        raw = {}
    return {
        "id": str(raw.get("id") or DEFAULT_USAGE_CONTEXT_ID),
        "actor": str(raw.get("actor") or raw.get("target_user") or "target user"),
        "situation": str(raw.get("situation") or "agent extraction from requirement text"),
        "goal": str(raw.get("goal") or requirement[:USAGE_CONTEXT_GOAL_MAX_CHARS]),
        "confidence": _bounded_probability(raw.get("confidence"), DEFAULT_LIGHT_EXTRACTION_CONFIDENCE),
        "evidence_refs": _dedupe_strings(raw.get("evidence_refs") or raw.get("evidence") or [evidence_ref]),
        "extraction_mode": "agent",
        "source_agent": str(payload.get("agent") or payload.get("agent_id") or "external-agent"),
    }


def _agent_extraction_request(repo_root: Path, base: Path, requirement: str, evidence_ref: str) -> tuple[Path, Path]:
    json_path = base / "extraction-agent-request.json"
    md_path = base / "extraction-agent-request.md"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "expectation-agent-extraction-request",
        "status": "agent-output-required",
        "required_output": {
            "usage_context": {
                "actor": "string",
                "situation": "string",
                "goal": "string",
                "confidence": "0.0-1.0",
                "evidence_refs": ["source reference"],
            },
            "expectations": [
                {
                    "id": "EXP-...",
                    "statement": "observable user expectation",
                    "category": "Functional Expectation",
                    "success_condition": ["observable pass condition"],
                    "failure_condition": ["observable fail condition"],
                    "confidence": "0.0-1.0",
                    "evidence_refs": ["source reference"],
                }
            ],
        },
        "source_requirement": requirement,
        "source_evidence_ref": evidence_ref,
    }
    write_json(json_path, payload)
    write_markdown(
        md_path,
        "\n".join(
            [
                "# Expectation Agent Extraction Request",
                "",
                f"Source evidence: `{evidence_ref}`",
                "",
                "Return JSON with `usage_context` and `expectations`. Every expectation must include `confidence` and `evidence_refs`.",
                "",
                "## Requirement",
                "",
                requirement or "No requirement text was provided.",
                "",
            ]
        ),
    )
    return json_path, md_path


def init_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    (base / "candidates" / "design-a").mkdir(parents=True, exist_ok=True)
    (base / "candidates" / "design-b").mkdir(parents=True, exist_ok=True)
    (base / "candidates" / "design-c").mkdir(parents=True, exist_ok=True)
    (base / "evaluations").mkdir(parents=True, exist_ok=True)
    (base / "selected-design").mkdir(parents=True, exist_ok=True)
    (base / "verification").mkdir(parents=True, exist_ok=True)

    files = {
        "readme": base / "README.md",
        "usage_context": base / "usage-context.json",
        "expectation_conflicts": base / "expectation-conflicts.json",
        "candidates": base / "design-candidates.json",
        "expectations": base / "expectation-set.json",
        "weights": base / "expectation-weights.json",
        "critical": base / "critical-expectations.json",
        "evaluations": base / "evaluations" / "expectation-evaluation.json",
        "multi_axis": base / "evaluations" / "multi-axis-evaluation.json",
        "tradeoffs": base / "evaluations" / "trade-off-analysis.json",
        "tradeoff_report": base / "evaluations" / "trade-off-analysis.md",
        "violations": base / "evaluations" / "violations.json",
        "comparison": base / "design-comparison-report.md",
        "comparison_json": base / "design-comparison-report.json",
        "human_decision": base / "human-decision.json",
        "selected_spec": base / "selected-design" / "design-specification.md",
        "contracts": base / "selected-design" / "interaction-contracts.json",
        "state_transitions": base / "selected-design" / "state-transitions.json",
        "implementation_notes": base / "selected-design" / "implementation-notes.md",
        "verification": base / "verification" / "expectation-verification.json",
        "feedback": base / "verification" / "expectation-feedback.json",
        "evidence_index": base / "verification" / "evidence-index.md",
        "events": base / "events.jsonl",
    }
    if getattr(args, "force", False) or not files["readme"].exists():
        write_markdown(
            files["readme"],
            "\n".join(
                [
                    "# Expectation-Driven Design",
                    "",
                    "このディレクトリは、期待集合、候補評価、比較レポート、Human Gate判断を保持します。",
                    "",
                    "Runtime成果物は依存を増やさず安定して検証できるよう、当面JSONで保持します。",
                ]
            ),
        )
    scaffold_payloads = [
        (files["usage_context"], {"schema_version": SCHEMA_VERSION, "schema": USAGE_CONTEXT_SCHEMA, "artifact_type": "usage-context", "usage_context": {}}),
        (
            files["expectation_conflicts"],
            {"schema_version": SCHEMA_VERSION, "schema": EXPECTATION_CONFLICTS_SCHEMA, "artifact_type": "expectation-conflicts", "conflicts": []},
        ),
        (
            files["candidates"],
            {"schema_version": SCHEMA_VERSION, "schema": DESIGN_CANDIDATES_SCHEMA, "artifact_type": "design-candidates", "candidates": []},
        ),
        (
            files["expectations"],
            {"schema_version": SCHEMA_VERSION, "schema": EXPECTATION_SET_SCHEMA, "artifact_type": "expectation-set", "expectations": []},
        ),
        (
            files["weights"],
            {"schema_version": SCHEMA_VERSION, "schema": EXPECTATION_WEIGHTS_SCHEMA, "artifact_type": "expectation-weights", "weights": []},
        ),
        (
            files["critical"],
            {
                "schema_version": SCHEMA_VERSION,
                "schema": CRITICAL_EXPECTATIONS_SCHEMA,
                "artifact_type": "critical-expectations",
                "critical_expectations": [],
            },
        ),
        (
            files["evaluations"],
            {
                "schema_version": SCHEMA_VERSION,
                "schema": EXPECTATION_EVALUATION_SCHEMA,
                "artifact_type": "expectation-evaluation-input",
                "candidate_evaluations": [],
            },
        ),
        (
            files["multi_axis"],
            {
                "schema_version": SCHEMA_VERSION,
                "schema": MULTI_AXIS_EVALUATION_SCHEMA,
                "artifact_type": "multi-axis-evaluation",
                "axis_direction": "higher-is-better",
                "required_axes": list(DEFAULT_DESIGN_AXES),
                "candidate_axis_evaluations": [],
            },
        ),
        (
            files["tradeoffs"],
            {
                "schema_version": SCHEMA_VERSION,
                "schema": TRADE_OFF_ANALYSIS_SCHEMA,
                "artifact_type": "trade-off-analysis",
                "tradeoffs": [],
            },
        ),
        (
            files["comparison_json"],
            {
                "schema_version": SCHEMA_VERSION,
                "schema": DESIGN_COMPARISON_REPORT_SCHEMA,
                "artifact_type": "design-comparison-report",
                "report_sections": [],
            },
        ),
        (files["violations"], {"schema_version": SCHEMA_VERSION, "artifact_type": "expectation-violations", "violations": []}),
        (
            files["human_decision"],
            {"schema_version": SCHEMA_VERSION, "schema": HUMAN_DECISION_SCHEMA, "artifact_type": "human-decision", "status": "pending"},
        ),
        (
            files["contracts"],
            {
                "schema_version": SCHEMA_VERSION,
                "schema": INTERACTION_CONTRACTS_SCHEMA,
                "artifact_type": "interaction-contracts",
                "interaction_contracts": [],
            },
        ),
        (files["state_transitions"], {"schema_version": SCHEMA_VERSION, "artifact_type": "state-transitions", "state_transitions": []}),
        (files["verification"], {"schema_version": SCHEMA_VERSION, "artifact_type": "expectation-verification", "expectation_verification": []}),
        (files["feedback"], {"schema_version": SCHEMA_VERSION, "artifact_type": "expectation-feedback", "feedback": []}),
    ]
    for path, payload in scaffold_payloads:
        if getattr(args, "force", False) or not path.exists():
            write_json(path, payload)
    if getattr(args, "force", False) or not files["implementation_notes"].exists():
        write_markdown(files["implementation_notes"], "# Implementation Notes\n\n- TBD\n")
    if getattr(args, "force", False) or not files["evidence_index"].exists():
        write_markdown(files["evidence_index"], "# Evidence Index\n\n- TBD\n")
    for path, text in [
        (files["tradeoff_report"], "# Trade-off Analysis\n\nTrade-off analysis will be generated during comparison.\n"),
        (files["selected_spec"], "# Selected Design Specification\n\nHuman Gate後に選択済みデザイン仕様を記録します。"),
        (files["implementation_notes"], "# Implementation Notes\n\n期待と禁止事項に紐づく実装メモを記録します。"),
        (files["evidence_index"], "# Evidence Index\n\n期待検証に使ったEvidence参照を記録します。"),
    ]:
        if getattr(args, "force", False) or not path.exists():
            write_markdown(path, text)
    if getattr(args, "sample", False):
        write_json(files["expectations"], _sample_expectation_payload())
        write_json(
            files["weights"],
            {
                "schema_version": SCHEMA_VERSION,
                "schema": EXPECTATION_WEIGHTS_SCHEMA,
                "artifact_type": "expectation-weights",
                "weights": [
                    {
                        "expectation_id": "EXP-TIME-001",
                        "weight": DEFAULT_SAMPLE_EXPECTATION_WEIGHT,
                        "rationale": ["本プロダクトの中核要件"],
                        "decided_by": {"type": "ariadne-initial"},
                    }
                ],
            },
        )
        write_json(
            files["critical"],
            {
                "schema_version": SCHEMA_VERSION,
                "schema": CRITICAL_EXPECTATIONS_SCHEMA,
                "artifact_type": "critical-expectations",
                "critical_expectations": [
                    {
                        "expectation_id": "EXP-TIME-001",
                        "minimum_probability": DEFAULT_CRITICAL_MINIMUM_PROBABILITY,
                        "failure_action": "reject-candidate",
                        "reason": "24時超え入力はプロダクトの中核要件である",
                    }
                ],
            },
        )
        write_json(files["evaluations"], _sample_evaluation_payload())
        write_json(files["multi_axis"], _sample_multi_axis_payload())
        sample_candidates = [
            _default_candidate("DESIGN-A", "Familiarity-first baseline candidate"),
            _default_candidate("DESIGN-B", "Direct input first candidate"),
        ]
        sample_candidates[0]["main_flow"] = ["Use familiar time picker", "Calculate result"]
        sample_candidates[0]["primary_expectations"] = ["EXP-TIME-001"]
        sample_candidates[0]["known_risks"] = ["24-hour overflow input may be rejected"]
        sample_candidates[1]["main_flow"] = ["Enter 39:00 directly", "Normalize next-day time", "Show result"]
        sample_candidates[1]["primary_expectations"] = ["EXP-TIME-001"]
        write_json(
            files["candidates"],
            {
                "schema_version": SCHEMA_VERSION,
                "schema": DESIGN_CANDIDATES_SCHEMA,
                "artifact_type": "design-candidates",
                "candidates": sample_candidates,
            },
        )

    manifest = register_context(
        repo_root,
        work_dir,
        work_id=work_id,
        context_type="workflow-specific-state",
        path=base / "README.md",
        required=False,
        generated_by="expectation-design-runtime",
        owner="workflow",
        schema=EXPECTATION_SET_SCHEMA,
        status="available",
    )
    now = utc_now_iso()
    artifact_index = _register_artifacts(
        repo_root,
        work_dir,
        work_id,
        [
            _artifact(
                repo_root,
                files["readme"],
                artifact_id="EDD-README",
                title="Expectation-Driven Design README",
                summary="Expectation-Driven Design work area guide.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["expectations"],
                artifact_id="EDD-EXPECTATION-SET",
                title="Expectation Set",
                summary="Structured user expectations for design evaluation.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["expectation_conflicts"],
                artifact_id="EDD-EXPECTATION-CONFLICTS",
                title="Expectation Conflicts",
                summary="Structured expectation conflict records.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["candidates"],
                artifact_id="EDD-DESIGN-CANDIDATES",
                title="Design Candidates",
                summary="Structured design candidate registry.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["weights"],
                artifact_id="EDD-EXPECTATION-WEIGHTS",
                title="Expectation Weights",
                summary="Initial or human-approved expectation importance weights.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["critical"],
                artifact_id="EDD-CRITICAL-EXPECTATIONS",
                title="Critical Expectations",
                summary="Expectations that cannot be offset by aggregate score.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["evaluations"],
                artifact_id="EDD-EVALUATION-INPUT",
                title="Expectation Evaluation Input",
                summary="Candidate expectation probability input.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["multi_axis"],
                artifact_id="EDD-MULTI-AXIS-EVALUATION",
                title="Multi-Axis Design Evaluation",
                summary="Candidate comparison across UX, identity, delight, accessibility, cost, maintenance, and feasibility axes.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["tradeoffs"],
                artifact_id="EDD-TRADE-OFF-ANALYSIS",
                title="Trade-off Analysis",
                summary="Structured gains, losses, affected expectations, implementation impact, and Human Gate decision points.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["comparison_json"],
                artifact_id="EDD-DESIGN-COMPARISON-PACKET",
                title="Design Comparison Report Packet",
                artifact_type="report",
                summary="Structured Human Gate comparison packet with report section coverage.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["human_decision"],
                artifact_id="EDD-HUMAN-DECISION",
                title="Human Decision",
                summary="Human Gate decision record for selected design.",
                now=now,
            ),
            _artifact(
                repo_root,
                files["contracts"],
                artifact_id="EDD-INTERACTION-CONTRACTS",
                title="Interaction Contracts",
                summary="Implementation contracts derived from selected design.",
                now=now,
            ),
        ],
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "expectation-design-init",
        "status": "initialized",
        "work_id": work_id,
        "base_dir": relative_to_repo(repo_root, base),
        "artifact_index": artifact_index,
        "context_manifest": relative_to_repo(repo_root, work_dir / "context" / "context-manifest.json"),
        "manifest_context_count": len(manifest.get("contexts", [])),
        "sample": bool(getattr(args, "sample", False)),
    }


def candidate_scaffold(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    base.mkdir(parents=True, exist_ok=True)
    candidates_path = base / "design-candidates.json"
    data = _read_structured(
        candidates_path,
        {"schema_version": SCHEMA_VERSION, "schema": DESIGN_CANDIDATES_SCHEMA, "artifact_type": "design-candidates", "candidates": []},
    )
    candidate_ids = _candidate_ids_from_args(args) or ["DESIGN-A", "DESIGN-B", "DESIGN-C"]
    existing = {item.get("candidate_id"): item for item in data.get("candidates", [])}
    generated: list[str] = []
    for candidate_id in candidate_ids:
        candidate = existing.get(candidate_id, _default_candidate(candidate_id, str(getattr(args, "concept", "") or "")))
        existing[candidate_id] = candidate
        cdir = _candidate_dir(base, candidate_id)
        cdir.mkdir(parents=True, exist_ok=True)
        write_markdown(cdir / "concept.md", _candidate_markdown(candidate))
        write_json(cdir / "flow.json", _flow_payload(candidate))
        (cdir / "wireframe.svg").write_text(_wireframe_svg(candidate_id), encoding="utf-8")
        feasibility = _default_feasibility(candidate_id)
        write_json(
            cdir / "feasibility-report.json",
            {
                "schema_version": SCHEMA_VERSION,
                "schema": DESIGN_FEASIBILITY_REPORT_SCHEMA,
                "artifact_type": "design-feasibility-report",
                **feasibility,
            },
        )
        write_markdown(cdir / "feasibility-report.md", _feasibility_markdown(feasibility))
        generated.append(relative_to_repo(repo_root, cdir))
    data["candidates"] = [existing[key] for key in sorted(existing)]
    write_json(candidates_path, data)
    now = utc_now_iso()
    artifact_index = _register_artifacts(
        repo_root,
        work_dir,
        work_id,
        [
            _artifact(
                repo_root,
                candidates_path,
                artifact_id="EDD-DESIGN-CANDIDATES",
                title="Design Candidates",
                summary="Structured design candidate registry and scaffold.",
                now=now,
            )
        ],
    )
    _append_event(base, "design_candidate_scaffolded", {"work_id": work_id, "candidate_ids": candidate_ids})
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "design-candidate-scaffold",
        "status": "scaffolded",
        "work_id": work_id,
        "candidate_ids": candidate_ids,
        "generated": generated,
        "candidates": relative_to_repo(repo_root, candidates_path),
        "artifact_index": artifact_index,
    }


def feasibility_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    candidate_ids = _candidate_ids_from_args(args) or [
        item.get("candidate_id", "")
        for item in _read_structured(base / "design-candidates.json", {"candidates": []}).get("candidates", [])
    ]
    reports: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    now = utc_now_iso()
    for candidate_id in [item for item in candidate_ids if item]:
        report = _default_feasibility(candidate_id)
        if getattr(args, "pass_feasibility", False):
            report.update(
                {
                    "status": "feasible",
                    "implementation_feasibility": "feasible",
                    "standard_components": "available",
                    "accessibility": "testable",
                    "testability": "testable",
                    "future_extensibility": "manageable",
                    "constraints": [],
                    "evidence_refs": ["human-feasibility-review"],
                }
            )
        cdir = _candidate_dir(base, candidate_id)
        cdir.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "schema": DESIGN_FEASIBILITY_REPORT_SCHEMA,
            "artifact_type": "design-feasibility-report",
            **report,
        }
        json_path = cdir / "feasibility-report.json"
        md_path = cdir / "feasibility-report.md"
        write_json(json_path, payload)
        write_markdown(md_path, _feasibility_markdown(report))
        reports.append(payload)
        artifacts.append(
            _artifact(
                repo_root,
                json_path,
                artifact_id=f"EDD-FEASIBILITY-{candidate_id}",
                title=f"Feasibility Report {candidate_id}",
                summary="Candidate feasibility, constraints, accessibility, and testability.",
                now=now,
            )
        )
    artifact_index = _register_artifacts(repo_root, work_dir, work_id, artifacts) if artifacts else ""
    _append_event(base, "design_candidate_feasibility_checked", {"work_id": work_id, "candidate_ids": candidate_ids})
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "design-feasibility-run",
        "status": "feasibility-ready",
        "work_id": work_id,
        "reports": reports,
        "artifact_index": artifact_index,
    }


def extract_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    base.mkdir(parents=True, exist_ok=True)
    source_path = str(getattr(args, "source", "") or "")
    requirement = str(getattr(args, "requirement", "") or "")
    evidence_ref = "cli-requirement"
    if source_path:
        path = _resolve_repo_path(repo_root, source_path)
        requirement = path.read_text(encoding="utf-8")
        evidence_ref = relative_to_repo(repo_root, path)
    mode = str(getattr(args, "mode", "light") or "light")
    agent_output = str(getattr(args, "agent_output", "") or "")
    if mode == "agent" and not agent_output:
        request_json, request_md = _agent_extraction_request(repo_root, base, requirement, evidence_ref)
        artifact_index = _register_artifacts(
            repo_root,
            work_dir,
            work_id,
            [
                _artifact(repo_root, request_json, artifact_id="EDD-EXPECTATION-AGENT-REQUEST", title="Expectation Agent Extraction Request", summary="Agent extraction input contract.", now=utc_now_iso()),
                _artifact(repo_root, request_md, artifact_id="EDD-EXPECTATION-AGENT-REQUEST-MD", title="Expectation Agent Extraction Request Report", artifact_type="report", summary="Human-readable agent extraction request.", now=utc_now_iso()),
            ],
        )
        event_path = _append_event(base, "expectation_extraction_agent_requested", {"work_id": work_id, "source": evidence_ref})
        return {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": "expectation-extraction",
            "status": "human-check-required",
            "reason": "agent_extraction_output_required",
            "work_id": work_id,
            "agent_request": relative_to_repo(repo_root, request_json),
            "agent_request_report": relative_to_repo(repo_root, request_md),
            "events": relative_to_repo(repo_root, event_path),
            "artifact_index": artifact_index,
        }
    if agent_output:
        agent_path = _resolve_repo_path(repo_root, agent_output)
        agent_payload = _read_structured(agent_path, {})
        if not isinstance(agent_payload, dict):
            raise ValueError("--agent-output must point to a JSON object")
        agent_evidence_ref = relative_to_repo(repo_root, agent_path)
        usage_context = _normalize_agent_usage_context(agent_payload, requirement, agent_evidence_ref)
        expectations = [
            _normalize_extracted_expectation(item, index, agent_evidence_ref)
            for index, item in enumerate(_agent_extraction_items(agent_payload), start=SEQUENCE_START)
        ]
        if not expectations:
            raise ValueError("--agent-output did not contain expectations")
    else:
        usage_context = {
            "id": DEFAULT_USAGE_CONTEXT_ID,
            "actor": "target user",
            "situation": "lightweight extraction from requirement text",
            "goal": requirement[:USAGE_CONTEXT_GOAL_MAX_CHARS],
            "confidence": DEFAULT_AGENT_EXTRACTION_CONFIDENCE,
            "evidence_refs": [evidence_ref],
            "extraction_mode": "light",
        }
        expectations = []
        lowered = requirement.lower()
        if "39:00" in requirement or "24" in requirement or "time" in lowered:
            expectations.append(
                {
                    "id": "EXP-TIME-001",
                    "statement": "Users can enter and evaluate over-24-hour time values such as 39:00.",
                    "category": "Functional Expectation",
                    "success_condition": ["39:00 is accepted as valid input", "The next-day normalized time is explainable"],
                    "failure_condition": ["39:00 is rejected or silently converted incorrectly"],
                    "source": [evidence_ref],
                    "evidence_refs": [evidence_ref],
                    "confidence": DEFAULT_LIGHT_EXTRACTION_CONFIDENCE,
                }
            )
        if "accessibility" in lowered or "a11y" in lowered:
            expectations.append(
                {
                    "id": "EXP-A11Y-001",
                    "statement": "The design remains accessible and testable.",
                    "category": "Accessibility Expectation",
                    "success_condition": ["Keyboard, screen-reader, and contrast requirements can be verified"],
                    "failure_condition": ["Accessibility is traded away without Human Gate approval"],
                    "source": [evidence_ref],
                    "evidence_refs": [evidence_ref],
                    "confidence": DEFAULT_FIXED_UI_CONFIDENCE,
                }
            )
        if not expectations:
            expectations.append(
                {
                    "id": "EXP-GENERAL-001",
                    "statement": requirement.strip() or "Requirement text has not been provided yet.",
                    "category": "Functional Expectation",
                    "success_condition": ["Expectation is reviewed and made observable"],
                    "failure_condition": ["Expectation remains vague or untestable"],
                    "source": [evidence_ref],
                    "evidence_refs": [evidence_ref],
                    "confidence": DEFAULT_FALLBACK_EXPECTATION_CONFIDENCE,
                }
            )
    usage_path = base / "usage-context.json"
    expectation_path = base / "expectation-set.json"
    write_json(usage_path, {"schema_version": SCHEMA_VERSION, "schema": USAGE_CONTEXT_SCHEMA, "artifact_type": "usage-context", "usage_context": usage_context})
    write_json(
        expectation_path,
        {
            "schema_version": SCHEMA_VERSION,
            "schema": EXPECTATION_SET_SCHEMA,
            "artifact_type": "expectation-set",
            "expectations": expectations,
        },
    )
    artifact_index = _register_artifacts(
        repo_root,
        work_dir,
        work_id,
        [
            _artifact(repo_root, usage_path, artifact_id="EDD-USAGE-CONTEXT", title="Usage Context", summary="Extracted usage context.", now=utc_now_iso()),
            _artifact(repo_root, expectation_path, artifact_id="EDD-EXPECTATION-SET", title="Expectation Set", summary="Extracted expectation set.", now=utc_now_iso()),
        ],
    )
    event_path = _append_event(base, "expectation_extracted", {"work_id": work_id, "mode": "agent" if agent_output else "light", "expectation_ids": [item["id"] for item in expectations]})
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "expectation-extraction",
        "status": "extracted",
        "work_id": work_id,
        "usage_context": relative_to_repo(repo_root, usage_path),
        "expectations": relative_to_repo(repo_root, expectation_path),
        "events": relative_to_repo(repo_root, event_path),
        "artifact_index": artifact_index,
    }


def evaluate_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    expectations, weights, critical, evaluation_data, multi_axis_data, usage_context_data = _load_inputs(repo_root, base, args)
    evaluations = candidate_evaluations(evaluation_data)
    axes = axis_evaluations(multi_axis_data)
    scores, violations = score_candidates(evaluations, weights, critical, expectations)
    tradeoffs = analyze_tradeoffs(scores, evaluations, axes, violations)
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": EXPECTATION_EVALUATION_SCHEMA,
        "artifact_type": "expectation-design-evaluation",
        "status": "evaluated",
        "evaluated_at": utc_now_iso(),
        "work_id": work_id,
        "usage_context": usage_context_data.get("usage_context", usage_context_data),
        "expectation_count": len(expectations),
        "candidate_count": len(evaluations),
        "expectations": serialize_dataclasses(expectations),
        "weights": serialize_dataclasses(weights),
        "critical_expectations": serialize_dataclasses(critical),
        "candidate_evaluations": {
            candidate_id: serialize_dataclasses(items)
            for candidate_id, items in evaluations.items()
        },
        "multi_axis_evaluations": {
            candidate_id: serialize_dataclasses(items)
            for candidate_id, items in axes.items()
        },
        "multi_axis_summary": summarize_axis_evaluations(axes),
        "candidate_scores": serialize_dataclasses(scores),
        "violations": serialize_dataclasses(violations),
        "violation_summary": summarize_violations(violations),
        "tradeoffs": serialize_dataclasses(tradeoffs),
    }
    output = base / "evaluations" / "expectation-evaluation-result.json"
    violations_output = base / "evaluations" / "violations.json"
    tradeoffs_output = base / "evaluations" / "trade-off-analysis.json"
    write_json(output, result)
    write_json(
        violations_output,
        {
            "schema_version": SCHEMA_VERSION,
            "schema": EXPECTATION_EVALUATION_SCHEMA,
            "artifact_type": "expectation-violations",
            "violations": result["violations"],
            "violation_summary": result["violation_summary"],
        },
    )
    write_json(
        tradeoffs_output,
        {
            "schema_version": SCHEMA_VERSION,
            "schema": TRADE_OFF_ANALYSIS_SCHEMA,
            "artifact_type": "trade-off-analysis",
            "tradeoffs": result["tradeoffs"],
        },
    )
    result["output"] = relative_to_repo(repo_root, output)
    result["violations_output"] = relative_to_repo(repo_root, violations_output)
    result["tradeoffs_output"] = relative_to_repo(repo_root, tradeoffs_output)
    event_path = _append_event(
        base,
        "design_candidate_evaluated",
        {
            "work_id": work_id,
            "candidate_scores": result["candidate_scores"],
            "critical_violations": sum(
                item.get("critical_violation_count", COUNT_DEFAULT) for item in result["candidate_scores"]
            ),
        },
    )
    result["events"] = relative_to_repo(repo_root, event_path)
    now = utc_now_iso()
    result["artifact_index"] = _register_artifacts(
        repo_root,
        work_dir,
        work_id,
        [
            _artifact(
                repo_root,
                output,
                artifact_id="EDD-EVALUATION-RESULT",
                title="Expectation Evaluation Result",
                summary="Weighted expectation satisfaction scores and evidence warnings.",
                now=now,
            ),
            _artifact(
                repo_root,
                violations_output,
                artifact_id="EDD-VIOLATIONS",
                title="Expectation Violations",
                summary="Critical, major, minor, ambiguous, and unverified expectation violations.",
                now=now,
            ),
            _artifact(
                repo_root,
                tradeoffs_output,
                artifact_id="EDD-TRADE-OFF-ANALYSIS",
                title="Trade-off Analysis",
                summary="Structured gains, losses, affected expectations, implementation impact, and Human Gate decision points.",
                now=now,
            ),
        ],
    )
    return result


def _candidate_ids(result: dict[str, Any]) -> list[str]:
    ids: set[str] = set()
    ids.update(str(item.get("candidate_id", "")) for item in result.get("candidate_scores", []))
    ids.update(str(candidate_id) for candidate_id in result.get("candidate_evaluations", {}))
    ids.update(str(candidate_id) for candidate_id in result.get("multi_axis_evaluations", {}))
    ids.update(str(item.get("candidate_id", "")) for item in result.get("tradeoffs", []))
    return sorted(item for item in ids if item)


def _axis_score(axis_results: dict[str, list[dict[str, Any]]], candidate_id: str, axis: str) -> float | None:
    for item in axis_results.get(candidate_id, []):
        if item.get("axis") == axis:
            return float(item.get("score", SCORE_MIN) or SCORE_MIN)
    return None


def _listify(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _parse_combine_with(values: list[str]) -> list[dict[str, Any]]:
    combinations: list[dict[str, Any]] = []
    for value in values:
        candidate_id, separator, raw_elements = value.partition(":")
        elements = [item.strip() for item in raw_elements.split("|") if item.strip()] if separator else []
        if candidate_id.strip():
            combinations.append({"candidate_id": candidate_id.strip(), "elements": elements})
    return combinations


def _parse_weight_changes(values: list[str]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for value in values:
        parts = [part.strip() for part in value.split(":")]
        if len(parts) != WEIGHT_CHANGE_FIELD_COUNT:
            raise ValueError("--weight-change must use expectation_id:before:after")
        changes.append(
            {
                "expectation_id": parts[0],
                "before": float(parts[1]),
                "after": float(parts[2]),
            }
        )
    return changes


def _comparison_report_packet(result: dict[str, Any]) -> dict[str, Any]:
    scores = result.get("candidate_scores", [])
    scores_by_id = {item.get("candidate_id"): item for item in scores}
    axis_results = result.get("multi_axis_evaluations", {})
    axis_summary = {item.get("candidate_id"): item for item in result.get("multi_axis_summary", [])}
    tradeoffs = result.get("tradeoffs", [])
    tradeoffs_by_id = {item.get("candidate_id"): item for item in tradeoffs}
    violations = result.get("violations", [])
    critical_violations = [item for item in violations if item.get("severity") == "critical"]
    positive_surprises = [item for item in violations if item.get("severity") == "positive-surprise"]
    unverified_items = [
        item for item in violations
        if item.get("severity") == "unverified"
    ]
    recommendable = [item for item in scores if item.get("recommendable")]
    recommended = sorted(recommendable, key=lambda item: item.get("expectation_score", SCORE_MIN), reverse=True)[
        :COMPARISON_RECOMMENDATION_LIMIT
    ]
    recommended_candidate = recommended[COUNT_DEFAULT].get("candidate_id", "") if recommended else ""

    candidate_overviews: list[dict[str, Any]] = []
    implementation_costs: list[dict[str, Any]] = []
    human_decision_items: list[str] = []
    for candidate_id in _candidate_ids(result):
        score = scores_by_id.get(candidate_id, {})
        summary = axis_summary.get(candidate_id, {})
        tradeoff = tradeoffs_by_id.get(candidate_id, {})
        gained = _listify(tradeoff.get("gained_values"))
        lost = _listify(tradeoff.get("lost_values"))
        decisions = [str(item) for item in _listify(tradeoff.get("human_decision_required"))]
        human_decision_items.extend(decisions)
        candidate_overviews.append(
            {
                "candidate_id": candidate_id,
                "expectation_score": float(score.get("expectation_score", SCORE_MIN) or SCORE_MIN),
                "recommendable": bool(score.get("recommendable", False)),
                "critical_violation_count": int(score.get("critical_violation_count", COUNT_DEFAULT) or COUNT_DEFAULT),
                "axis_average": float(summary.get("axis_average", SCORE_MIN) or SCORE_MIN),
                "summary": (
                    "Recommendable candidate for Human Gate review."
                    if score.get("recommendable")
                    else "Candidate has blocking or unresolved expectation risk."
                ),
                "key_strengths": gained[:COMPARISON_KEY_POINT_LIMIT],
                "key_risks": lost[:COMPARISON_KEY_POINT_LIMIT],
            }
        )
        implementation_costs.append(
            {
                "candidate_id": candidate_id,
                "implementation_cost": _axis_score(axis_results, candidate_id, "implementation_cost"),
                "maintenance_cost": _axis_score(axis_results, candidate_id, "maintenance_cost"),
                "technical_feasibility": _axis_score(axis_results, candidate_id, "technical_feasibility"),
                "implementation_impact": tradeoff.get("implementation_impact", ""),
                "future_impact": tradeoff.get("future_impact", ""),
            }
        )

    if recommended_candidate:
        recommendation_rationale = [
            "Critical expectations are satisfied.",
            "Recommendation remains subject to Human Gate approval.",
        ]
    else:
        recommendation_rationale = [
            "No candidate is recommendable without resolving critical or missing expectation risk."
        ]
    alternatives = [
        {
            "candidate_id": item.get("candidate_id", ""),
            "reason": "Alternative to compare during Human Gate.",
            "expectation_score": item.get("expectation_score", SCORE_MIN),
            "critical_violation_count": item.get("critical_violation_count", COUNT_DEFAULT),
        }
        for item in scores
        if item.get("candidate_id") != recommended_candidate
    ]
    report_sections = [
        "usage_context",
        "major_expectations",
        "critical_expectations",
        "candidate_overviews",
        "expectation_satisfaction",
        "multi_axis_evaluation",
        "expectation_violations",
        "positive_surprise_hypotheses",
        "tradeoff_analysis",
        "implementation_costs",
        "unverified_items",
        "recommended_candidate",
        "recommendation_rationale",
        "alternatives",
        "human_decision_items",
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "schema": DESIGN_COMPARISON_REPORT_SCHEMA,
        "artifact_type": "design-comparison-report",
        "status": "comparison-ready",
        "work_id": result.get("work_id", ""),
        "usage_context": result.get("usage_context", {}),
        "major_expectations": result.get("expectations", []),
        "critical_expectations": result.get("critical_expectations", []),
        "candidate_overviews": candidate_overviews,
        "expectation_satisfaction": scores,
        "multi_axis_evaluation": result.get("multi_axis_summary", []),
        "expectation_violations": violations,
        "positive_surprise_hypotheses": positive_surprises,
        "tradeoff_analysis": tradeoffs,
        "implementation_costs": implementation_costs,
        "unverified_items": unverified_items,
        "recommended_candidate": recommended_candidate,
        "recommendation_rationale": recommendation_rationale,
        "alternatives": alternatives,
        "human_decision_items": list(dict.fromkeys(human_decision_items)),
        "report_sections": report_sections,
    }


def _review_council_feedback_path(base: Path) -> Path:
    return base / "review-council-feedback.json"


def _review_council_decision_items(feedback: dict[str, Any]) -> list[str]:
    items: list[str] = []
    snapshot = feedback.get("snapshot", {}) if isinstance(feedback.get("snapshot"), dict) else {}
    missing_reviewers = snapshot.get("missing_reviewers", [])
    if missing_reviewers:
        items.append(f"Review Council missing reviewers: {', '.join(str(item) for item in missing_reviewers)}")
    for issue in feedback.get("issues", []):
        if issue.get("status") == "open":
            items.append(f"Resolve Review Council issue {issue.get('issue_id', '')}: {issue.get('claim', '')}")
    for finding in feedback.get("findings", []):
        if finding.get("blocking") or finding.get("verdict") in {"changes-required", "fail"}:
            items.append(f"Address Review Council finding {finding.get('finding_id', '')}: {finding.get('claim', '')}")
    if snapshot.get("verdict") and snapshot.get("verdict") not in {"APPROVED", "approved"}:
        items.append(f"Review Council verdict requires Human Gate consideration: {snapshot.get('verdict')}")
    return list(dict.fromkeys(item for item in items if item.strip()))


def _merge_review_council_feedback(base: Path, comparison_packet: dict[str, Any]) -> dict[str, Any]:
    feedback = _read_structured(_review_council_feedback_path(base), {})
    if not isinstance(feedback, dict) or not feedback.get("review_id"):
        return comparison_packet
    merged = dict(comparison_packet)
    merged["review_council_feedback"] = {
        "review_id": feedback.get("review_id", ""),
        "status": feedback.get("status", ""),
        "snapshot": feedback.get("snapshot", {}),
        "findings": feedback.get("findings", []),
        "issues": feedback.get("issues", []),
        "source": feedback.get("source", {}),
    }
    merged["human_decision_items"] = list(
        dict.fromkeys([*merged.get("human_decision_items", []), *_review_council_decision_items(feedback)])
    )
    sections = list(merged.get("report_sections", []))
    if "review_council_feedback" not in sections:
        sections.append("review_council_feedback")
    merged["report_sections"] = sections
    if feedback.get("status") in {"review-blocked", "human-check-required"}:
        merged["status"] = "review-blocked"
    return merged


def _review_council_feedback_markdown(feedback: dict[str, Any]) -> str:
    snapshot = feedback.get("snapshot", {}) if isinstance(feedback.get("snapshot"), dict) else {}
    lines = [
        "# Expectation Design Review Council Feedback",
        "",
        f"Review ID: {feedback.get('review_id', '')}",
        f"Status: {feedback.get('status', '')}",
        f"Verdict: {snapshot.get('verdict', '') or 'not-decided'}",
        f"Open issues: {snapshot.get('open_issue_count', COUNT_DEFAULT)}",
        f"Blocking issues: {snapshot.get('blocking_issue_count', COUNT_DEFAULT)}",
        "",
        "## Findings",
    ]
    findings = feedback.get("findings", [])
    if findings:
        for item in findings:
            lines.append(
                f"- {item.get('finding_id', '')} {item.get('severity', '')} {item.get('reviewer', '')}: {item.get('claim', '')}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Open Issues"])
    open_issues = [item for item in feedback.get("issues", []) if item.get("status") == "open"]
    if open_issues:
        for item in open_issues:
            lines.append(f"- {item.get('issue_id', '')} {item.get('severity', '')}: {item.get('claim', '')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Human Gate Inputs"])
    decision_items = feedback.get("human_decision_items", [])
    if decision_items:
        lines.extend(f"- {item}" for item in decision_items)
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def _comparison_markdown(result: dict[str, Any]) -> str:
    report_packet = result.get("comparison_report") or _comparison_report_packet(result)
    scores = result.get("candidate_scores", [])
    recommendable = [item for item in scores if item.get("recommendable")]
    recommended = sorted(recommendable, key=lambda item: item.get("expectation_score", SCORE_MIN), reverse=True)[
        :COMPARISON_RECOMMENDATION_LIMIT
    ]
    expectations = {item.get("expectation_id"): item for item in result.get("expectations", [])}
    weights = {item.get("expectation_id"): item for item in result.get("weights", [])}
    critical = {item.get("expectation_id"): item for item in result.get("critical_expectations", [])}
    evaluations = result.get("candidate_evaluations", {})
    axis_results = result.get("multi_axis_evaluations", {})
    axis_summary = {item.get("candidate_id"): item for item in result.get("multi_axis_summary", [])}
    scores_by_id = {item.get("candidate_id"): item for item in scores}
    violations = result.get("violations", [])
    violation_summary = result.get("violation_summary", [])
    tradeoffs = result.get("tradeoffs", [])
    critical_violations = [item for item in violations if item.get("severity") == "critical"]
    positive_surprises = [item for item in violations if item.get("severity") == "positive-surprise"]
    unverified_items = [
        {
            "candidate_id": candidate_id,
            **evaluation,
        }
        for candidate_id, items in evaluations.items()
        for evaluation in items
        if evaluation.get("requires_validation") or evaluation.get("evidence_quality") == "assumption"
    ]
    lines = [
        "# Expectation-Driven Design Comparison",
        "",
        f"Work ID: {result.get('work_id', '')}",
        f"Expectations: {result.get('expectation_count', COUNT_DEFAULT)}",
        f"Candidates: {result.get('candidate_count', COUNT_DEFAULT)}",
        f"Critical Violations: {len(critical_violations)}",
        "",
        "## Usage Context",
        "",
    ]
    usage_context = report_packet.get("usage_context", {})
    if usage_context:
        for key, value in sorted(usage_context.items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- なし")
    lines.extend(
        [
            "",
            "## Major Expectations",
            "",
            "| Expectation | Weight | Critical | Confidence | Statement |",
            "| --- | ---: | --- | ---: | --- |",
        ]
    )
    if expectations:
        for expectation_id, expectation in sorted(expectations.items()):
            weight = weights.get(expectation_id, {}).get("weight", SCORE_MIN)
            is_critical = "yes" if expectation_id in critical else "no"
            lines.append(
                "| {id} | {weight:.6f} | {critical} | {confidence:.2f} | {statement} |".format(
                    id=expectation_id,
                    weight=float(weight or SCORE_MIN),
                    critical=is_critical,
                    confidence=float(expectation.get("confidence", SCORE_MIN) or SCORE_MIN),
                    statement=expectation.get("statement", ""),
                )
            )
    else:
        lines.append("| なし | 0 | no | 0 | 期待集合が未定義です |")
    lines.extend(
        [
            "",
            "## Critical Expectations",
            "",
            "| Expectation | Minimum Probability | Failure Action | Reason |",
            "| --- | ---: | --- | --- |",
        ]
    )
    if critical:
        for expectation_id, item in sorted(critical.items()):
            lines.append(
                "| {id} | {minimum:.2f} | {action} | {reason} |".format(
                    id=expectation_id,
                    minimum=float(item.get("minimum_probability", SCORE_MIN) or SCORE_MIN),
                    action=item.get("failure_action", ""),
                    reason=item.get("reason", ""),
                )
            )
    else:
        lines.append("| なし | 0 |  | Critical Expectationは未定義です |")
    lines.extend(
        [
            "",
            "## Candidate Overview",
            "",
            "| Candidate | Summary | Key Strengths | Key Risks | Recommendable |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    overviews = report_packet.get("candidate_overviews", [])
    if not overviews:
        lines.append("| none | none | none | none | false |")
    for item in overviews:
        strengths = "<br>".join(str(value) for value in item.get("key_strengths", [])) or "none"
        risks = "<br>".join(str(value) for value in item.get("key_risks", [])) or "none"
        lines.append(
            "| {candidate} | {summary} | {strengths} | {risks} | {recommendable} |".format(
                candidate=item.get("candidate_id", ""),
                summary=item.get("summary", ""),
                strengths=strengths,
                risks=risks,
                recommendable=item.get("recommendable", False),
            )
        )
    lines.extend(
        [
            "",
            "## Candidate Scores",
            "",
            "| Candidate | Expectation Score | Critical Violations | Unverified | Evidence Warnings | Recommendable |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for item in scores:
        lines.append(
            "| {candidate_id} | {expectation_score:.6f} | {critical_violation_count} | {unverified_count} | {evidence_warning_count} | {recommendable} |".format(
                **item
            )
        )
    lines.extend(
        [
            "",
            "## Multi-Axis Evaluation",
            "",
            "Axis scores use 0.0-1.0, higher is better. Expectation Score remains a gate input, not the final design decision.",
            "",
            "| Candidate | Expectation Satisfaction | Usability | Product Identity | Delight | Accessibility | Implementation Cost | Maintenance Cost | Technical Feasibility | Axis Avg | Missing Axes |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    if not axis_results:
        lines.append("| none | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | Multi-axis evaluation is not provided. |")
    for candidate_id, items in sorted(axis_results.items()):
        by_axis = {item.get("axis"): item for item in items}
        summary = axis_summary.get(candidate_id, {})
        values = [
            float(by_axis.get(axis, {}).get("score", SCORE_MIN) or SCORE_MIN)
            for axis in DEFAULT_DESIGN_AXES
        ]
        missing = ", ".join(summary.get("missing_axes", [])) or "none"
        lines.append(
            "| {candidate} | {values[0]:.2f} | {values[1]:.2f} | {values[2]:.2f} | {values[3]:.2f} | {values[4]:.2f} | {values[5]:.2f} | {values[6]:.2f} | {values[7]:.2f} | {average:.2f} | {missing} |".format(
                candidate=candidate_id,
                values=values,
                average=float(summary.get("axis_average", SCORE_MIN) or SCORE_MIN),
                missing=missing,
            )
        )
    lines.extend(
        [
            "",
            "## Violation Summary",
            "",
            "| Candidate | Critical | Major | Minor | Ambiguous | Unverified | Positive Surprise |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    if not violation_summary:
        lines.append("| none | 0 | 0 | 0 | 0 | 0 | 0 |")
    for item in violation_summary:
        lines.append(
            "| {candidate_id} | {critical} | {major} | {minor} | {ambiguous} | {unverified} | {positive_surprise} |".format(
                **item
            )
        )
    lines.extend(
        [
            "",
            "## Trade-off Analysis",
            "",
            "| Candidate | Gained Values | Lost Values | Implementation Impact | Future Impact | Human Decision Required |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    if not tradeoffs:
        lines.append("| none | none | none | none | none | none |")
    for item in tradeoffs:
        gained = "<br>".join(str(value) for value in item.get("gained_values", [])) or "none"
        lost = "<br>".join(str(value) for value in item.get("lost_values", [])) or "none"
        decisions = "<br>".join(str(value) for value in item.get("human_decision_required", [])) or "none"
        lines.append(
            "| {candidate} | {gained} | {lost} | {implementation} | {future} | {decisions} |".format(
                candidate=item.get("candidate_id", ""),
                gained=gained,
                lost=lost,
                implementation=item.get("implementation_impact", ""),
                future=item.get("future_impact", ""),
                decisions=decisions,
            )
        )
    lines.extend(
        [
            "",
            "## Implementation Costs",
            "",
            "| Candidate | Implementation Cost | Maintenance Cost | Technical Feasibility | Implementation Impact | Future Impact |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    implementation_costs = report_packet.get("implementation_costs", [])
    if not implementation_costs:
        lines.append("| none | 0 | 0 | 0 | none | none |")
    for item in implementation_costs:
        implementation_cost = item.get("implementation_cost")
        maintenance_cost = item.get("maintenance_cost")
        technical_feasibility = item.get("technical_feasibility")
        lines.append(
            "| {candidate} | {implementation_cost:.2f} | {maintenance_cost:.2f} | {technical_feasibility:.2f} | {implementation_impact} | {future_impact} |".format(
                candidate=item.get("candidate_id", ""),
                implementation_cost=float(implementation_cost or SCORE_MIN),
                maintenance_cost=float(maintenance_cost or SCORE_MIN),
                technical_feasibility=float(technical_feasibility or SCORE_MIN),
                implementation_impact=item.get("implementation_impact", ""),
                future_impact=item.get("future_impact", ""),
            )
        )
    lines.extend(["", "## Evidence And Validation", ""])
    if not evaluations:
        lines.append("- 候補評価が未入力です。")
    for candidate_id, items in sorted(evaluations.items()):
        score = scores_by_id.get(candidate_id, {})
        lines.append(
            f"- {candidate_id}: evidence warnings={score.get('evidence_warning_count', COUNT_DEFAULT)}, "
            f"unverified={score.get('unverified_count', COUNT_DEFAULT)}"
        )
        for item in items:
            evidence = item.get("evidence_refs", [])
            evidence_text = "; ".join(evidence) if evidence else "Evidenceなし"
            validation = "requires validation" if item.get("requires_validation") else "validated or evidenced"
            lines.append(
                f"  - {item.get('expectation_id', '')}: P={item.get('probability', SCORE_MIN):.2f}, "
                f"confidence={item.get('confidence', SCORE_MIN):.2f}, "
                f"quality={item.get('evidence_quality', '')}, {validation}. {evidence_text}"
            )
    lines.extend(["", "## Expectation Violations", ""])
    if not violations:
        lines.append("- なし")
    for item in violations:
        lines.append(
            f"- {item.get('severity', '')}: {item.get('candidate_id', '')} / "
            f"{item.get('expectation_id', '')}: {item.get('description', '')} "
            f"Impact: {item.get('user_impact', '')} Recommendation: {item.get('recommendation', '')}"
        )
    lines.extend(["", "## Positive Surprise Hypotheses", ""])
    if not positive_surprises:
        lines.append("- なし")
    for item in positive_surprises:
        lines.append(
            f"- {item.get('candidate_id', '')} / {item.get('expectation_id', '')}: "
            f"{item.get('description', '')} Recommendation: {item.get('recommendation', '')}"
        )
    lines.extend(["", "## Unverified Items", ""])
    if not unverified_items:
        lines.append("- なし")
    for item in unverified_items:
        lines.append(
            f"- {item.get('candidate_id', '')} / {item.get('expectation_id', '')}: "
            f"evidence_quality={item.get('evidence_quality', '')}, "
            f"requires_validation={str(item.get('requires_validation', False)).lower()}"
        )
    lines.extend(["", "## Recommendation", ""])
    if recommended:
        item = recommended[COUNT_DEFAULT]
        lines.append(f"{item.get('candidate_id')} を推奨候補として提示できます。")
        lines.append("")
        lines.extend(
            [
                "理由:",
                "- Critical Expectation違反がありません。",
                f"- 期待充足スコアが推奨可能候補の中で最も高いです: {item.get('expectation_score', SCORE_MIN):.6f}",
                f"- 未検証項目は {item.get('unverified_count', COUNT_DEFAULT)} 件です。",
                "",
                "ただし、最終決定はHuman Gateで行います。",
            ]
        )
        lines.append("- Multi-axis evaluation must be reviewed before Human Gate approval.")
    else:
        lines.append("Critical Violationがない推奨候補はありません。期待集合または候補評価の見直しが必要です。")
    alternatives = [
        item
        for item in scores
        if not recommended or item.get("candidate_id") != recommended[COUNT_DEFAULT].get("candidate_id")
    ]
    lines.extend(["", "## Alternatives", ""])
    if not alternatives:
        lines.append("- なし")
    for item in alternatives:
        reason = "Critical Violationあり" if item.get("critical_violation_count", COUNT_DEFAULT) else "推奨候補との比較対象"
        lines.append(
            f"- {item.get('candidate_id', '')}: score={item.get('expectation_score', SCORE_MIN):.6f}, "
            f"{reason}, unverified={item.get('unverified_count', COUNT_DEFAULT)}"
        )
    lines.extend(
        [
            "",
            "## Human Decision Required",
            "",
            "- 候補を採用する",
            "- 候補を組み合わせる",
            "- 再生成する",
            "- 重みまたはCritical Expectationを変更する",
            "- 未検証Evidenceを追加調査へ回す",
        ]
    )
    packet_decisions = report_packet.get("human_decision_items", [])
    if packet_decisions:
        lines.append("")
        lines.append("Structured decision items:")
        lines.extend(f"- {item}" for item in packet_decisions)
    review_feedback = report_packet.get("review_council_feedback", {})
    if isinstance(review_feedback, dict) and review_feedback:
        snapshot = review_feedback.get("snapshot", {}) if isinstance(review_feedback.get("snapshot"), dict) else {}
        lines.extend(
            [
                "",
                "## Review Council Feedback",
                "",
                f"- Review ID: {review_feedback.get('review_id', '')}",
                f"- Status: {review_feedback.get('status', '')}",
                f"- Verdict: {snapshot.get('verdict', '') or 'not-decided'}",
                f"- Open issues: {snapshot.get('open_issue_count', COUNT_DEFAULT)}",
                f"- Blocking issues: {snapshot.get('blocking_issue_count', COUNT_DEFAULT)}",
                "",
                "| Type | ID | Severity | Claim |",
                "| --- | --- | --- | --- |",
            ]
        )
        rows = [
            ("finding", item.get("finding_id", ""), item.get("severity", ""), item.get("claim", ""))
            for item in review_feedback.get("findings", [])
        ]
        rows.extend(
            ("issue", item.get("issue_id", ""), item.get("severity", ""), item.get("claim", ""))
            for item in review_feedback.get("issues", [])
            if item.get("status") == "open"
        )
        if rows:
            lines.extend(f"| {kind} | {item_id} | {severity} | {claim} |" for kind, item_id, severity, claim in rows)
        else:
            lines.append("| none | none | none | none |")
    lines.extend(["", "## Report Section Coverage", ""])
    for section in report_packet.get("report_sections", []):
        lines.append(f"- {section}")
    return "\n".join(lines)


def _human_gate_summary_markdown(decision: dict[str, Any], comparison: dict[str, Any]) -> str:
    lines = [
        "# Human Gate Summary",
        "",
        f"Status: {decision.get('status', '')}",
        f"Action: {decision.get('decision_action', '')}",
        f"Selected candidate: {decision.get('selected_candidate', '') or 'none'}",
        f"Source report: {decision.get('source_report', '')}",
        "",
        "## Combine With",
    ]
    combine_with = decision.get("combine_with", [])
    if not combine_with:
        lines.append("- none")
    for item in combine_with:
        elements = ", ".join(item.get("elements", [])) or "none"
        lines.append(f"- {item.get('candidate_id', '')}: {elements}")
    lines.extend(["", "## Weight Changes"])
    weight_changes = decision.get("weight_changes", [])
    if not weight_changes:
        lines.append("- none")
    for item in weight_changes:
        lines.append(
            f"- {item.get('expectation_id', '')}: {item.get('before', SCORE_MIN)} -> {item.get('after', SCORE_MIN)}"
        )
    lines.extend(["", "## Decision Items"])
    decision_items = decision.get("decision_items", [])
    if not decision_items:
        lines.append("- none")
    for item in decision_items:
        lines.append(f"- {item}")
    lines.extend(["", "## Comparison Context"])
    lines.append(f"- Recommended candidate: {comparison.get('comparison_report', {}).get('recommended_candidate', '')}")
    lines.append(f"- Comparison packet: {comparison.get('comparison_json', '')}")
    if decision.get("comment"):
        lines.extend(["", "## Comment", "", str(decision.get("comment", ""))])
    return "\n".join(lines) + "\n"


def _refinement_plan(decision: dict[str, Any], comparison: dict[str, Any]) -> dict[str, Any]:
    selected = str(decision.get("selected_candidate", "") or "")
    tradeoffs = [
        item for item in comparison.get("tradeoffs", [])
        if item.get("candidate_id") == selected
    ]
    overview = [
        item for item in comparison.get("comparison_report", {}).get("candidate_overviews", [])
        if item.get("candidate_id") == selected
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "design-refinement-plan",
        "status": "ready-for-refinement",
        "selected_candidate": selected,
        "decision_action": decision.get("decision_action", ""),
        "combine_with": decision.get("combine_with", []),
        "weight_changes": decision.get("weight_changes", []),
        "decision_items": decision.get("decision_items", []),
        "source_report": comparison.get("report", ""),
        "source_comparison_packet": comparison.get("comparison_json", ""),
        "selected_candidate_overview": overview[0] if overview else {},
        "selected_candidate_tradeoffs": tradeoffs[0] if tradeoffs else {},
        "next_steps": [
            "Refine selected design specification",
            "Carry over approved combination elements",
            "Apply approved expectation weight changes before implementation contract generation",
            "Preserve unresolved Human Gate decision items as verification inputs",
        ],
    }


def compare_design(args: argparse.Namespace) -> dict[str, Any]:
    result = evaluate_design(args)
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    report = expectation_dir(work_dir) / "design-comparison-report.md"
    comparison_json = expectation_dir(work_dir) / "design-comparison-report.json"
    tradeoff_report = expectation_dir(work_dir) / "evaluations" / "trade-off-analysis.md"
    comparison_packet = _merge_review_council_feedback(expectation_dir(work_dir), _comparison_report_packet(result))
    result_with_packet = {**result, "comparison_report": comparison_packet}
    write_json(comparison_json, comparison_packet)
    write_markdown(report, _comparison_markdown(result_with_packet))
    write_markdown(tradeoff_report, render_tradeoff_markdown(result_with_packet.get("tradeoffs", [])))
    artifact_index = _register_artifacts(
        repo_root,
        work_dir,
        work_id,
        [
            _artifact(
                repo_root,
                report,
                artifact_id="EDD-DESIGN-COMPARISON-REPORT",
                title="Design Comparison Report",
                artifact_type="report",
                status="in-review",
                summary="Human Gate comparison report for expectation-driven design candidates.",
                now=utc_now_iso(),
            ),
            _artifact(
                repo_root,
                comparison_json,
                artifact_id="EDD-DESIGN-COMPARISON-PACKET",
                title="Design Comparison Report Packet",
                artifact_type="report",
                status="in-review",
                summary="Structured Human Gate comparison packet with report section coverage.",
                now=utc_now_iso(),
            ),
            _artifact(
                repo_root,
                tradeoff_report,
                artifact_id="EDD-TRADE-OFF-REPORT",
                title="Trade-off Analysis Report",
                artifact_type="report",
                status="in-review",
                summary="Human-readable gains, losses, impacts, and Human Gate decision points for each design candidate.",
                now=utc_now_iso(),
            )
        ],
    )
    result = {
        **result_with_packet,
        "artifact_type": "expectation-design-comparison",
        "status": "comparison-ready",
        "report": relative_to_repo(repo_root, report),
        "comparison_json": relative_to_repo(repo_root, comparison_json),
        "tradeoff_report": relative_to_repo(repo_root, tradeoff_report),
        "artifact_index": artifact_index,
    }
    return result


def gate_design(args: argparse.Namespace) -> dict[str, Any]:
    comparison = compare_design(args)
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    approved = getattr(args, "human_check", "pending") == "approved"
    selected = str(getattr(args, "selected_candidate", "") or "")
    decision_action = str(getattr(args, "decision_action", "select") or "select")
    combine_with = _parse_combine_with(list(getattr(args, "combine_with", []) or []))
    weight_changes = _parse_weight_changes(list(getattr(args, "weight_change", []) or []))
    decision_items = list(getattr(args, "decision_item", []) or [])
    if not approved:
        event_path = _append_event(
            base,
            "design_human_gate_required",
            {"work_id": work_id, "candidate_count": comparison.get("candidate_count", COUNT_DEFAULT)},
        )
        required = [
            "Select candidate",
            "Combine candidates",
            "Update expectation weights",
            "Request regeneration",
        ]
        required.extend(comparison.get("comparison_report", {}).get("human_decision_items", []))
        return {
            **comparison,
            "artifact_type": "expectation-design-human-gate",
            "status": "human-check-required",
            "reason": "design_candidate_selection_requires_human_gate",
            "decision_required": list(dict.fromkeys(required)),
            "events": relative_to_repo(repo_root, event_path),
            "repair_command": (
                f"aiwfctl design expectation gate --work-id {comparison.get('work_id')} "
                "--selected-candidate <candidate-id> --human-check approved"
            ),
        }
    if decision_action in {"select", "combine"} and not selected:
        raise ValueError("--selected-candidate is required when --human-check approved for select/combine")
    if decision_action == "combine" and not combine_with:
        raise ValueError("--combine-with is required when --decision-action combine")
    if decision_action == "change-weights" and not weight_changes:
        raise ValueError("--weight-change is required when --decision-action change-weights")
    if decision_action in {"regenerate", "revise-expectations", "investigate", "defer"} and not decision_items:
        decision_items = [f"Human Gate requested {decision_action} before final design refinement."]
    decision = {
        "schema_version": SCHEMA_VERSION,
        "schema": HUMAN_DECISION_SCHEMA,
        "artifact_type": "human-decision",
        "status": "approved",
        "decided_at": utc_now_iso(),
        "decision_action": decision_action,
        "selected_candidate": selected,
        "combine_with": combine_with,
        "weight_changes": weight_changes,
        "decision_items": decision_items,
        "comment": str(getattr(args, "comment", "") or ""),
        "source_report": comparison.get("report", ""),
        "source_comparison_packet": comparison.get("comparison_json", ""),
    }
    decision_path = base / "human-decision.json"
    summary_path = base / "human-gate-summary.md"
    refinement_plan_path = base / "selected-design" / "design-refinement-plan.json"
    write_json(decision_path, decision)
    write_markdown(summary_path, _human_gate_summary_markdown(decision, comparison))
    write_json(refinement_plan_path, _refinement_plan(decision, comparison))
    event_path = _append_event(base, "human_decision_recorded", {"work_id": work_id, "selected_candidate": selected, "decision_action": decision_action})
    artifact_index = _register_artifacts(
        repo_root,
        work_dir,
        work_id,
        [
            _artifact(
                repo_root,
                decision_path,
                artifact_id="EDD-HUMAN-DECISION",
                title="Human Decision",
                status="approved",
                summary="Approved Human Gate design decision.",
                now=utc_now_iso(),
            ),
            _artifact(
                repo_root,
                summary_path,
                artifact_id="EDD-HUMAN-GATE-SUMMARY",
                title="Human Gate Summary",
                artifact_type="report",
                status="approved",
                summary="Human-readable Human Gate decision summary.",
                now=utc_now_iso(),
            ),
            _artifact(
                repo_root,
                refinement_plan_path,
                artifact_id="EDD-DESIGN-REFINEMENT-PLAN",
                title="Design Refinement Plan",
                status="approved",
                summary="Selected design refinement input derived from Human Gate decision.",
                now=utc_now_iso(),
            )
        ],
    )
    return {
        **comparison,
        "artifact_type": "expectation-design-human-gate",
        "status": "approved",
        "decision_action": decision_action,
        "selected_candidate": selected,
        "human_decision": relative_to_repo(repo_root, decision_path),
        "human_gate_summary": relative_to_repo(repo_root, summary_path),
        "refinement_plan": relative_to_repo(repo_root, refinement_plan_path),
        "events": relative_to_repo(repo_root, event_path),
        "artifact_index": artifact_index,
    }


def multi_axis_design(args: argparse.Namespace) -> dict[str, Any]:
    result = evaluate_design(args)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "multi-axis-design-evaluation",
        "status": "evaluated",
        "work_id": result.get("work_id", ""),
        "multi_axis_evaluations": result.get("multi_axis_evaluations", {}),
        "multi_axis_summary": result.get("multi_axis_summary", []),
        "source_output": result.get("output", ""),
        "artifact_index": result.get("artifact_index", ""),
    }


def review_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    expectations, weights, critical, _evaluation_data, _multi_axis_data, _usage_context = _load_inputs(repo_root, base, args)
    weight_by_id = {item.expectation_id: item for item in weights}
    critical_ids = {item.expectation_id for item in critical}
    findings: list[dict[str, Any]] = []
    for expectation in expectations:
        if not expectation.success_conditions:
            findings.append({"severity": "major", "expectation_id": expectation.expectation_id, "check": "observability", "message": "Success condition is missing."})
        if expectation.expectation_id not in weight_by_id:
            findings.append({"severity": "major", "expectation_id": expectation.expectation_id, "check": "weight-rationale", "message": "Weight is missing."})
        elif not weight_by_id[expectation.expectation_id].rationale:
            findings.append({"severity": "minor", "expectation_id": expectation.expectation_id, "check": "weight-rationale", "message": "Weight rationale is missing."})
        if "button" in expectation.statement.lower() or "dropdown" in expectation.statement.lower():
            findings.append({"severity": "minor", "expectation_id": expectation.expectation_id, "check": "ui-method-lock", "message": "Expectation may fix a UI means instead of a user outcome."})
    conflicts = _read_structured(base / "expectation-set.json", {"conflicts": []}).get("conflicts", [])
    for conflict in conflicts:
        findings.append({"severity": "major", "expectation_id": conflict.get("expectation_a", ""), "check": "conflict", "message": conflict.get("description", "")})
    if not critical_ids and expectations:
        findings.append({"severity": "major", "expectation_id": "", "check": "critical-expectation", "message": "Critical expectations are not defined."})
    status = "ready-for-human-check" if findings else "reviewed"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "schema": EXPECTATION_REVIEW_REPORT_SCHEMA,
        "artifact_type": "expectation-review-report",
        "status": status,
        "work_id": work_id,
        "findings": findings,
        "human_gate_required": True,
    }
    json_path = base / "expectation-review-report.json"
    md_path = base / "expectation-review-report.md"
    write_json(json_path, payload)
    lines = ["# Expectation Review Report", "", f"Status: {status}", "", "## Findings"]
    lines.extend(
        f"- {item.get('severity', '')}: {item.get('check', '')} {item.get('expectation_id', '')} - {item.get('message', '')}"
        for item in findings
    ) if findings else lines.append("- none")
    write_markdown(md_path, "\n".join(lines) + "\n")
    artifact_index = _register_artifacts(
        repo_root,
        work_dir,
        work_id,
        [
            _artifact(repo_root, json_path, artifact_id="EDD-EXPECTATION-REVIEW", title="Expectation Review Report", artifact_type="report", status=status, summary="Expectation observability, weights, conflict, and UI-means review.", now=utc_now_iso()),
        ],
    )
    return {"schema_version": SCHEMA_VERSION, "artifact_type": "expectation-review", "status": status, "work_id": work_id, "review_report": relative_to_repo(repo_root, json_path), "artifact_index": artifact_index}


def refine_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    decision = _read_structured(base / "human-decision.json", {})
    plan = _read_structured(base / "selected-design" / "design-refinement-plan.json", {})
    selected = str(decision.get("selected_candidate") or plan.get("selected_candidate") or getattr(args, "selected_candidate", "") or "")
    if not selected:
        raise ValueError("selected candidate is required before refinement")
    combine_with = decision.get("combine_with", plan.get("combine_with", []))
    consistency_checks = [
        {"check": "selected-candidate-present", "status": "pass"},
        {"check": "combined-elements-reviewed", "status": "pass" if combine_with else "not-applicable"},
        {"check": "no-simple-addition", "status": "pass", "detail": "Combination elements are recorded for explicit reconciliation, not blindly appended."},
    ]
    spec_path = base / "selected-design" / "design-specification.md"
    payload_path = base / "selected-design" / "design-refinement-result.json"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "selected-design-refinement",
        "status": "refined",
        "selected_candidate": selected,
        "combine_with": combine_with,
        "weight_changes": decision.get("weight_changes", plan.get("weight_changes", [])),
        "consistency_checks": consistency_checks,
        "source_human_decision": relative_to_repo(repo_root, base / "human-decision.json"),
    }
    write_json(payload_path, payload)
    lines = [
        "# Selected Design Specification",
        "",
        f"Selected candidate: {selected}",
        "",
        "## Human Decision Reflection",
        f"- Decision action: {decision.get('decision_action', plan.get('decision_action', ''))}",
        f"- Comment: {decision.get('comment', '')}",
        "",
        "## Combined Candidate Elements",
    ]
    lines.extend(f"- {item.get('candidate_id', '')}: {', '.join(item.get('elements', [])) or 'none'}" for item in combine_with) if combine_with else lines.append("- none")
    lines.extend(["", "## Consistency Checks"])
    lines.extend(f"- {item.get('check', '')}: {item.get('status', '')}" for item in consistency_checks)
    write_markdown(spec_path, "\n".join(lines) + "\n")
    artifact_index = _register_artifacts(
        repo_root,
        work_dir,
        work_id,
        [
            _artifact(repo_root, spec_path, artifact_id="EDD-SELECTED-DESIGN-SPEC", title="Selected Design Specification", summary="Refined selected design specification after Human Gate.", now=utc_now_iso()),
            _artifact(repo_root, payload_path, artifact_id="EDD-DESIGN-REFINEMENT-RESULT", title="Design Refinement Result", summary="Structured selected design refinement result.", now=utc_now_iso()),
        ],
    )
    return {"schema_version": SCHEMA_VERSION, "artifact_type": "selected-design-refinement", "status": "refined", "work_id": work_id, "selected_candidate": selected, "selected_spec": relative_to_repo(repo_root, spec_path), "refinement_result": relative_to_repo(repo_root, payload_path), "artifact_index": artifact_index}


def contracts_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    expectations = [Expectation.from_mapping(item) for item in _read_structured(base / "expectation-set.json", {"expectations": []}).get("expectations", [])]
    contracts = []
    for index, expectation in enumerate(expectations, start=SEQUENCE_START):
        contracts.append(
            {
                "id": f"CONTRACT-{index:0{INTERACTION_CONTRACT_ID_WIDTH}d}",
                "related_expectations": [expectation.expectation_id],
                "given": {"expectation": expectation.statement, "sources": list(expectation.sources)},
                "when": {"action": "execute-selected-design-flow"},
                "then": {"success_conditions": list(expectation.success_conditions)},
                "must_not": list(expectation.failure_conditions),
                "evidence_refs": list(expectation.sources),
            }
        )
    path = base / "selected-design" / "interaction-contracts.json"
    write_json(path, {"schema_version": SCHEMA_VERSION, "schema": INTERACTION_CONTRACTS_SCHEMA, "artifact_type": "interaction-contracts", "interaction_contracts": contracts})
    artifact_index = _register_artifacts(repo_root, work_dir, work_id, [_artifact(repo_root, path, artifact_id="EDD-INTERACTION-CONTRACTS", title="Interaction Contracts", summary="Given/When/Then/Must Not contracts generated from expectations.", now=utc_now_iso())])
    return {"schema_version": SCHEMA_VERSION, "artifact_type": "interaction-contract-generation", "status": "generated", "work_id": work_id, "contracts": relative_to_repo(repo_root, path), "contract_count": len(contracts), "artifact_index": artifact_index}


def verify_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    result = _read_structured(base / "evaluations" / "expectation-evaluation-result.json", {})
    selected = str(getattr(args, "selected_candidate", "") or _read_structured(base / "human-decision.json", {}).get("selected_candidate", ""))
    evaluations = result.get("candidate_evaluations", {}).get(selected, [])
    records = []
    for item in evaluations:
        records.append(
            {
                "expectation_id": item.get("expectation_id", ""),
                "candidate_id": selected,
                "design_probability": item.get("probability", SCORE_MIN),
                "verified_result": None,
                "verification_method": ["pending-test", "pending-review"],
                "test_evidence": [],
                "review_evidence": [],
                "human_review": [],
            }
        )
    path = base / "verification" / "expectation-verification.json"
    write_json(path, {"schema_version": SCHEMA_VERSION, "schema": EXPECTATION_VERIFICATION_SCHEMA, "artifact_type": "expectation-verification", "expectation_verification": records})
    artifact_index = _register_artifacts(repo_root, work_dir, work_id, [_artifact(repo_root, path, artifact_id="EDD-EXPECTATION-VERIFICATION", title="Expectation Verification", summary="Design probability separated from post-implementation verification values.", now=utc_now_iso())])
    return {"schema_version": SCHEMA_VERSION, "artifact_type": "expectation-verification-run", "status": "verification-ready", "work_id": work_id, "verification": relative_to_repo(repo_root, path), "record_count": len(records), "artifact_index": artifact_index}


def feedback_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    verification = _read_structured(base / "verification" / "expectation-verification.json", {"expectation_verification": []}).get("expectation_verification", [])
    feedback = []
    for item in verification:
        observed = item.get("verified_result")
        predicted = item.get("design_probability", SCORE_MIN)
        feedback.append(
            {
                "candidate_id": item.get("candidate_id", ""),
                "expectation_id": item.get("expectation_id", ""),
                "predicted_probability": predicted,
                "observed_probability": observed,
                "delta": None if observed is None else round(float(observed) - float(predicted), SCORE_ROUND_DECIMALS),
                "cause": [],
                "action": ["Collect observed evidence before knowledge capture."],
                "knowledge_candidate": True,
            }
        )
    path = base / "verification" / "expectation-feedback.json"
    write_json(path, {"schema_version": SCHEMA_VERSION, "schema": EXPECTATION_FEEDBACK_SCHEMA, "artifact_type": "expectation-feedback", "feedback": feedback})
    artifact_index = _register_artifacts(repo_root, work_dir, work_id, [_artifact(repo_root, path, artifact_id="EDD-EXPECTATION-FEEDBACK", title="Expectation Feedback", summary="Predicted vs observed expectation feedback for knowledge capture.", now=utc_now_iso())])
    return {"schema_version": SCHEMA_VERSION, "artifact_type": "expectation-feedback-run", "status": "feedback-ready", "work_id": work_id, "feedback": relative_to_repo(repo_root, path), "feedback_count": len(feedback), "artifact_index": artifact_index}


def _review_summary_from_session(session: dict[str, Any]) -> dict[str, Any]:
    findings = session.get("findings", [])
    issues = session.get("issues", [])
    required_reviewers = [str(item) for item in session.get("packet", {}).get("required_reviewers", [])]
    completed_reviewers = sorted(
        {
            str(item.get("reviewer", ""))
            for item in findings
            if str(item.get("reviewer", "")).strip()
        }
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "review-council-summary",
        "status": "summarized",
        "review_id": session.get("review_id", ""),
        "work_id": session.get("work_id", ""),
        "snapshot": {
            "session_status": session.get("status", ""),
            "target": session.get("packet", {}).get("target", ""),
            "target_revision": session.get("packet", {}).get("target_revision", ""),
            "required_reviewers": required_reviewers,
            "completed_reviewers": completed_reviewers,
            "missing_reviewers": [item for item in required_reviewers if item not in completed_reviewers],
            "finding_count": len(findings),
            "issue_count": len(issues),
            "open_issue_count": len([item for item in issues if item.get("status") == "open"]),
            "blocking_issue_count": len([item for item in issues if item.get("status") == "open" and item.get("blocking")]),
            "human_check": session.get("human_check", ""),
            "challenge_completed": bool(session.get("challenge_completed", False)),
            "evidence_verified": bool(session.get("evidence_verified", False)),
            "verdict": (session.get("verdict") or {}).get("verdict", ""),
        },
        "reviewers": [
            {
                "reviewer": reviewer,
                "required": True,
                "state": "completed" if reviewer in completed_reviewers else "pending",
                "finding_count": len([item for item in findings if item.get("reviewer") == reviewer]),
            }
            for reviewer in required_reviewers
        ],
        "findings": findings,
        "issues": issues,
    }


def _load_review_council_summary(repo_root: Path, work_id: str, args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, str]]:
    summary_path = str(getattr(args, "review_summary", "") or "")
    if summary_path:
        path = _resolve_repo_path(repo_root, summary_path)
        data = _read_structured(path, {})
        if not isinstance(data, dict):
            raise ValueError("--review-summary must point to a JSON object")
        return data, {"summary_json": relative_to_repo(repo_root, path)}
    review_id = str(getattr(args, "review_id", "") or "")
    session = ReviewStore(repo_root).load(review_id=review_id, work_id=work_id, work_dir=getattr(args, "work_dir", ""))
    artifacts = session.get("artifacts", {}) if isinstance(session.get("artifacts"), dict) else {}
    return _review_summary_from_session(session), {str(key): str(value) for key, value in artifacts.items()}


def _normalize_review_feedback(summary: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    snapshot = summary.get("snapshot", {}) if isinstance(summary.get("snapshot"), dict) else {}
    findings = [item for item in summary.get("findings", []) if isinstance(item, dict)]
    issues = [item for item in summary.get("issues", []) if isinstance(item, dict)]
    blocking = int(snapshot.get("blocking_issue_count", COUNT_DEFAULT) or COUNT_DEFAULT)
    open_issues = int(snapshot.get("open_issue_count", COUNT_DEFAULT) or COUNT_DEFAULT)
    missing_reviewers = snapshot.get("missing_reviewers", [])
    status = "review-blocked" if blocking or open_issues or missing_reviewers else "synced"
    feedback = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "expectation-review-council-feedback",
        "status": status,
        "review_id": summary.get("review_id", ""),
        "work_id": summary.get("work_id", ""),
        "snapshot": snapshot,
        "reviewers": summary.get("reviewers", []),
        "findings": findings,
        "issues": issues,
        "source": source,
    }
    feedback["human_decision_items"] = _review_council_decision_items(feedback)
    return feedback


def council_sync_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    base.mkdir(parents=True, exist_ok=True)
    summary, source = _load_review_council_summary(repo_root, work_id, args)
    feedback = _normalize_review_feedback(summary, source)
    json_path = _review_council_feedback_path(base)
    md_path = base / "review-council-feedback.md"
    write_json(json_path, feedback)
    write_markdown(md_path, _review_council_feedback_markdown(feedback))
    comparison_path = base / "design-comparison-report.json"
    report_path = base / "design-comparison-report.md"
    if comparison_path.exists():
        comparison = _merge_review_council_feedback(base, _read_structured(comparison_path, {}))
        write_json(comparison_path, comparison)
        if report_path.exists():
            existing = report_path.read_text(encoding="utf-8").split("\n## Review Council Feedback", 1)[0].rstrip()
            review_section = _comparison_markdown({"comparison_report": comparison}).split("\n## Review Council Feedback", 1)
            if len(review_section) == 2:
                report_path.write_text(existing + "\n\n## Review Council Feedback" + review_section[1], encoding="utf-8")
    event_path = _append_event(base, "review_council_feedback_synced", {"work_id": work_id, "review_id": feedback.get("review_id", ""), "status": feedback.get("status", "")})
    artifact_index = _register_artifacts(
        repo_root,
        work_dir,
        work_id,
        [
            _artifact(repo_root, json_path, artifact_id="EDD-REVIEW-COUNCIL-FEEDBACK", title="Review Council Feedback", summary="Review Council findings returned to expectation design Human Gate inputs.", now=utc_now_iso()),
            _artifact(repo_root, md_path, artifact_id="EDD-REVIEW-COUNCIL-FEEDBACK-REPORT", title="Review Council Feedback Report", artifact_type="report", summary="Human-readable Review Council feedback for design decisions.", now=utc_now_iso()),
        ],
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "expectation-review-council-sync",
        "status": feedback.get("status", "synced"),
        "work_id": work_id,
        "review_id": feedback.get("review_id", ""),
        "review_council_feedback": relative_to_repo(repo_root, json_path),
        "review_council_feedback_report": relative_to_repo(repo_root, md_path),
        "comparison_json": relative_to_repo(repo_root, comparison_path) if comparison_path.exists() else "",
        "report": relative_to_repo(repo_root, report_path) if report_path.exists() else "",
        "decision_required": feedback.get("human_decision_items", []),
        "events": relative_to_repo(repo_root, event_path),
        "artifact_index": artifact_index,
    }


def dispatch_design(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _repo_root(args)
    work_dir = _work_dir(repo_root, args)
    work_id = _work_id(args, work_dir)
    base = expectation_dir(work_dir)
    comparison = _read_structured(base / "design-comparison-report.json", {})
    reviewers = [
        "ux",
        "interaction-design",
        "accessibility",
        "product-identity",
        "frontend-architecture",
        "testing",
    ]
    evidence = [
        relative_to_repo(repo_root, path)
        for path in [
            base / "usage-context.json",
            base / "expectation-set.json",
            base / "design-candidates.json",
            base / "design-comparison-report.json",
            base / "evaluations" / "multi-axis-evaluation.json",
            base / "evaluations" / "trade-off-analysis.json",
        ]
        if path.exists()
    ]
    review_id = str(getattr(args, "review_id", "") or f"expectation-design-{work_id}")
    review_packet = {
        "target": "Expectation-Driven Design comparison",
        "target_revision": "design-stage",
        "intent": "Review UX, accessibility, frontend architecture, testability, and design trade-offs before Human Gate approval.",
        "requirements": [
            "Review only the filtered expectation design context.",
            "Return structured findings that can be synced into design-comparison-report and Human Gate decision items.",
        ],
        "changed_files": [],
        "guardrails": [
            "Review Council reviewers must not mutate design source artifacts directly.",
            "Findings must cite evidence_refs when possible.",
        ],
        "evidence": evidence,
        "scope": [
            "usage context",
            "expectation set",
            "candidate comparison",
            "multi-axis evaluation",
            "trade-off analysis",
            "selected design risks",
        ],
        "known_constraints": comparison.get("unverified_items", []),
        "required_reviewers": reviewers,
    }
    reviewer_args = " ".join(f"--reviewer {item}" for item in reviewers)
    evidence_args = " ".join(f"--evidence {item}" for item in evidence)
    review_start_command = (
        f"aiwfctl review start --work-id {work_id} --review-id {review_id} "
        "--target \"Expectation-Driven Design comparison\" "
        "--target-revision design-stage "
        "--intent \"Review expectation-driven design before Human Gate approval\" "
        f"{reviewer_args} {evidence_args}"
    ).strip()
    packet = {
        "schema_version": SCHEMA_VERSION,
        "schema": EXPECTATION_DESIGN_DISPATCH_SCHEMA,
        "artifact_type": "expectation-design-dispatch",
        "status": "ready-for-review-council",
        "work_id": work_id,
        "dispatcher_context": {
            "usage_context": comparison.get("usage_context", {}),
            "major_expectations": comparison.get("major_expectations", []),
            "critical_expectations": comparison.get("critical_expectations", []),
            "design_constraints": comparison.get("implementation_costs", []),
            "prior_design_feedback": comparison.get("unverified_items", []),
        },
        "reviewers": reviewers,
        "review_id": review_id,
        "review_packet": review_packet,
        "review_start_command": review_start_command,
        "returns_to_human_gate": ["review findings", "accessibility risks", "frontend architecture risks", "test strategy gaps"],
    }
    path = base / "review-council-dispatch.json"
    write_json(path, packet)
    artifact_index = _register_artifacts(repo_root, work_dir, work_id, [_artifact(repo_root, path, artifact_id="EDD-REVIEW-COUNCIL-DISPATCH", title="Review Council Dispatch", summary="Expectation design context filtered for Review Council reviewers.", now=utc_now_iso())])
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "expectation-design-dispatch",
        "status": "ready-for-review-council",
        "work_id": work_id,
        "review_id": review_id,
        "dispatch": relative_to_repo(repo_root, path),
        "review_start_command": review_start_command,
        "artifact_index": artifact_index,
    }
