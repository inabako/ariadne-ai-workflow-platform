from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any

from runtime.common import read_json, relative_to_repo, utc_now_iso, write_json, write_markdown
from runtime.constants.runtime_values import SCHEMA_VERSION
from runtime.constants.schemas import E2E_TEST_CONTRACT_SCHEMA, E2E_TEST_PLAN_SCHEMA, E2E_TEST_REPORT_SCHEMA
from runtime.constants.workspace import (
    resolve_work_dir,
    test_evidence_dir_for_work_dir,
    test_specifications_dir_for_work_dir,
)


ARTIFACT_PREFIX_BY_TEST_KIND = {
    "e2e": "e2e",
    "integration": "integration",
}
DEFAULT_COMMAND_TIMEOUT_SECONDS = 300
RUN_OUTPUT_PREVIEW_CHARS = 4000
TEST_KIND_CHOICES = tuple(ARTIFACT_PREFIX_BY_TEST_KIND)
CONTRACT_REQUIRED_LIST_FIELDS = [
    "preconditions",
    "expected_route",
    "expected_state_transitions",
    "expected_side_effects",
    "observable_endpoints",
    "timing_constraints",
    "ordering_constraints",
    "retry_expectations",
    "recovery_expectations",
    "failure_signals",
    "evidence_requirements",
    "human_review_points",
]
CONTRACT_OPTIONAL_LIST_FIELDS = ["required_stubs"]
CONTRACT_LIST_FIELDS = [
    *CONTRACT_REQUIRED_LIST_FIELDS[:9],
    *CONTRACT_OPTIONAL_LIST_FIELDS,
    *CONTRACT_REQUIRED_LIST_FIELDS[9:],
]
CONTRACT_SCALAR_FIELDS = ["objective", "trigger", "duplicate_handling"]
CONTRACT_REQUIRED_FIELDS = [*CONTRACT_SCALAR_FIELDS, *CONTRACT_REQUIRED_LIST_FIELDS]
DEFAULT_REVIEW_COUNCIL_REVIEWERS = [
    "ux",
    "accessibility",
    "frontend-architecture",
    "runtime-architecture",
]
CORE_EVIDENCE_PHASES = ["readiness", "run-result", "observation", "verification"]
REVIEW_EVIDENCE_PHASES = ["review-plan", "explanation"]
PACKAGE_EVIDENCE_PHASES = [
    *CORE_EVIDENCE_PHASES,
    "review-plan",
    "coverage",
    "explanation",
    "human-final-gate",
    "loop",
]
COMMAND_TRIGGER_PREFIXES = (
    ".\\",
    "./",
    "aiwfctl ",
    "curl ",
    "docker ",
    "kubectl ",
    "npm ",
    "npx ",
    "pnpm ",
    "pytest ",
    "python ",
    "uv ",
    "yarn ",
)
API_EXPECTATION_TERMS = ("api", "endpoint", "http", "rest", "graphql")
API_COMMAND_HINTS = ("api", "curl", "http", "pytest", "requests", "postman", "playwright")
UI_EXPECTATION_TERMS = ("ui", "browser", "screen", "page", "画面")
UI_COMMAND_HINTS = ("ui", "browser", "cypress", "playwright", "qtest", "selenium", "e2e")


def normalize_items(values: list[str] | tuple[str, ...] | None) -> list[str]:
    return [str(value).strip() for value in values or [] if str(value).strip()]


def normalize_test_kind(test_kind: str) -> str:
    normalized = (test_kind or "e2e").strip().lower()
    if normalized not in ARTIFACT_PREFIX_BY_TEST_KIND:
        raise ValueError(f"Unsupported test kind: {test_kind}")
    return normalized


def artifact_prefix(test_kind: str) -> str:
    return ARTIFACT_PREFIX_BY_TEST_KIND[normalize_test_kind(test_kind)]


def plan_json_path(work_dir: Path, test_kind: str) -> Path:
    return test_specifications_dir_for_work_dir(work_dir) / f"{artifact_prefix(test_kind)}-test-plan.json"


def plan_markdown_path(work_dir: Path, test_kind: str) -> Path:
    return test_specifications_dir_for_work_dir(work_dir) / f"{artifact_prefix(test_kind)}-test-plan.md"


def contract_json_path(work_dir: Path, test_kind: str) -> Path:
    return test_specifications_dir_for_work_dir(work_dir) / f"{artifact_prefix(test_kind)}-test-contract.json"


def contract_markdown_path(work_dir: Path, test_kind: str) -> Path:
    return test_specifications_dir_for_work_dir(work_dir) / f"{artifact_prefix(test_kind)}-test-contract.md"


def evidence_json_path(work_dir: Path, test_kind: str, phase: str) -> Path:
    return test_evidence_dir_for_work_dir(work_dir) / f"{artifact_prefix(test_kind)}-test" / f"{phase}.json"


def evidence_markdown_path(work_dir: Path, test_kind: str, phase: str) -> Path:
    return test_evidence_dir_for_work_dir(work_dir) / f"{artifact_prefix(test_kind)}-test" / f"{phase}.md"


def command_value(value: str) -> str:
    if not value:
        return '""'
    if any(char.isspace() for char in value) or '"' in value:
        return '"' + value.replace('"', '\\"') + '"'
    return value


def resolve_path(repo_root: Path, work_dir: Path, value: str) -> Path:
    raw = Path(value)
    if raw.is_absolute():
        return raw
    candidate = work_dir / raw
    if candidate.exists():
        return candidate
    return repo_root / raw


def relative_artifact(repo_root: Path, path: Path) -> str:
    return relative_to_repo(repo_root, path)


def build_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        f"# {plan['test_kind'].upper()} Test Plan",
        "",
        f"- Work ID: `{plan['work_id']}`",
        f"- Status: `{plan['status']}`",
        f"- Objective: {plan['objective']}",
        "",
        "## Scenarios",
    ]
    lines.extend(f"- {item}" for item in plan["scenarios"])
    lines.extend(["", "## Expectations"])
    lines.extend(f"- {item}" for item in plan["expectations"])
    lines.extend(["", "## Required Stubs"])
    lines.extend(f"- {item}" for item in plan["required_stubs"] or ["なし"])
    lines.extend(["", "## Commands"])
    lines.extend(f"- `{item}`" for item in plan["commands"] or ["Human Check後に定義"])
    lines.extend(["", "## Human Check"])
    lines.append("E2E / integration run before external effects requires `--human-check approved`.")
    return "\n".join(lines)


def missing_contract_fields(test_contract: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in CONTRACT_SCALAR_FIELDS:
        if not str(test_contract.get(field, "")).strip():
            missing.append(field)
    for field in CONTRACT_REQUIRED_LIST_FIELDS:
        if not normalize_items(test_contract.get(field, [])):
            missing.append(field)
    return missing


def looks_like_command(value: str) -> bool:
    normalized = value.strip().lower()
    return any(normalized.startswith(prefix) for prefix in COMMAND_TRIGGER_PREFIXES)


def contains_any(value: str, terms: tuple[str, ...]) -> bool:
    normalized = value.lower()
    return any(term in normalized for term in terms)


def build_responsibility_split() -> dict[str, str]:
    return {
        "contract_designer": "検証契約を作成し、観測可能な成功/失敗条件を固定する。",
        "readiness_checker": "契約、Stub、実行command、証跡要件の不足を確認する。",
        "runner": "契約に基づく実行commandだけを実行し、結果を記録する。",
        "observer": "経路、状態遷移、副作用、endpoint、失敗signalを観測する。",
        "verifier": "観測結果を契約と照合する。",
        "explainer": "契約との差分、不足、異常、再テスト理由を説明する。",
        "human_reviewer": "契約と証跡をもとに最終判断する。",
    }


def build_contract_consistency_checks(
    plan: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[list[dict[str, str]], list[str], list[str]]:
    if not plan or not contract:
        return [], [], []
    payload = contract.get("test_contract", {}) if isinstance(contract, dict) else {}
    commands = normalize_items(plan.get("commands", []))
    command_text = "\n".join(commands).lower()
    plan_stubs = set(normalize_items(plan.get("required_stubs", [])))
    contract_stubs = set(normalize_items(payload.get("required_stubs", [])))
    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    trigger = str(payload.get("trigger", "")).strip()
    if trigger and commands and looks_like_command(trigger):
        status = "pass" if trigger in commands else "blocker"
        message = "contract trigger is included in plan.commands."
        if status == "blocker":
            message = "contract trigger looks executable but is not included in plan.commands."
            blockers.append(message)
        checks.append({"name": "trigger_command_alignment", "status": status, "message": message})

    missing_contract_stubs = sorted(plan_stubs - contract_stubs)
    if missing_contract_stubs:
        message = "plan.required_stubs are missing from contract.required_stubs."
        blockers.append(f"{message}: {', '.join(missing_contract_stubs)}")
        checks.append({"name": "stub_alignment", "status": "blocker", "message": message})
    elif plan_stubs:
        checks.append({"name": "stub_alignment", "status": "pass", "message": "plan stubs are covered by contract."})

    extra_contract_stubs = sorted(contract_stubs - plan_stubs)
    if extra_contract_stubs:
        message = "contract.required_stubs include stubs that are not listed in plan.required_stubs."
        warnings.append(f"{message}: {', '.join(extra_contract_stubs)}")
        checks.append({"name": "contract_extra_stubs", "status": "warning", "message": message})

    plan_objective = str(plan.get("objective", "")).strip().lower()
    contract_objective = str(payload.get("objective", "")).strip().lower()
    if plan_objective and contract_objective and plan_objective != contract_objective:
        if plan_objective not in contract_objective and contract_objective not in plan_objective:
            message = "plan.objective and contract.objective differ; human review should confirm intent alignment."
            warnings.append(message)
            checks.append({"name": "objective_alignment", "status": "warning", "message": message})

    observable_text = "\n".join(
        [
            *normalize_items(payload.get("expected_route", [])),
            *normalize_items(payload.get("observable_endpoints", [])),
        ]
    )
    if commands and contains_any(observable_text, API_EXPECTATION_TERMS) and not contains_any(command_text, API_COMMAND_HINTS):
        message = "contract mentions API/endpoint observability, but plan.commands do not show an API-oriented command hint."
        warnings.append(message)
        checks.append({"name": "api_observability_alignment", "status": "warning", "message": message})
    if commands and contains_any(observable_text, UI_EXPECTATION_TERMS) and not contains_any(command_text, UI_COMMAND_HINTS):
        message = "contract mentions UI/browser observability, but plan.commands do not show a UI-oriented command hint."
        warnings.append(message)
        checks.append({"name": "ui_observability_alignment", "status": "warning", "message": message})

    return checks, warnings, blockers


def build_contract_markdown(contract: dict[str, Any]) -> str:
    payload = contract["test_contract"]
    lines = [
        f"# {contract['test_kind'].upper()} Test Contract",
        "",
        f"- Work ID: `{contract['work_id']}`",
        f"- Status: `{contract['status']}`",
        f"- Objective: {payload.get('objective', '')}",
        f"- Trigger: {payload.get('trigger', '')}",
        f"- Duplicate Handling: {payload.get('duplicate_handling', '')}",
        "",
    ]
    for field in CONTRACT_LIST_FIELDS:
        lines.extend([f"## {field.replace('_', ' ').title()}", ""])
        lines.extend(f"- {item}" for item in normalize_items(payload.get(field, [])) or ["未定義"])
        lines.append("")
    lines.extend(["## Missing Contract Fields", ""])
    lines.extend(f"- {item}" for item in contract.get("missing_contract_fields", []) or ["none"])
    lines.extend(["", "## Responsibility Split", ""])
    for role, description in contract.get("responsibility_split", {}).items():
        lines.append(f"- {role}: {description}")
    lines.extend(["", "## Human Review", ""])
    lines.append("テスト実装・実行・合否判定の前に、この検証契約を人間が確認します。")
    return "\n".join(lines)


def write_contract_artifacts(repo_root: Path, work_dir: Path, contract: dict[str, Any]) -> dict[str, str]:
    json_path = contract_json_path(work_dir, contract["test_kind"])
    markdown_path = contract_markdown_path(work_dir, contract["test_kind"])
    write_json(json_path, contract)
    write_markdown(markdown_path, build_contract_markdown(contract))
    return {
        "contract_json": relative_artifact(repo_root, json_path),
        "contract_markdown": relative_artifact(repo_root, markdown_path),
    }


def write_plan_artifacts(repo_root: Path, work_dir: Path, plan: dict[str, Any]) -> dict[str, str]:
    json_path = plan_json_path(work_dir, plan["test_kind"])
    markdown_path = plan_markdown_path(work_dir, plan["test_kind"])
    write_json(json_path, plan)
    write_markdown(markdown_path, build_plan_markdown(plan))
    return {
        "plan_json": relative_artifact(repo_root, json_path),
        "plan_markdown": relative_artifact(repo_root, markdown_path),
    }


def build_e2e_plan(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
    objective: str = "",
    scenarios: list[str] | None = None,
    targets: list[str] | None = None,
    expectations: list[str] | None = None,
    required_stubs: list[str] | None = None,
    commands: list[str] | None = None,
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    scenario_values = normalize_items(scenarios)
    expectation_values = normalize_items(expectations)
    command_values = normalize_items(commands)
    plan = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_PLAN_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-test-plan",
        "status": "planned",
        "test_kind": kind,
        "work_id": work_id,
        "objective": objective.strip() or "結合/E2Eで確認する目的をHuman Checkで確定する。",
        "scenarios": scenario_values or ["主要な成功経路を1つ以上定義する。"],
        "targets": normalize_items(targets),
        "expectations": expectation_values or ["実行結果と観測ログから期待結果を照合できること。"],
        "required_stubs": normalize_items(required_stubs),
        "commands": command_values,
        "human_review_required": True,
        "created_at": utc_now_iso(),
    }
    plan["artifacts"] = write_plan_artifacts(repo_root, resolved_work_dir, plan)
    plan["next_actions"] = [
        f"aiwfctl e2e contract --work-id {work_id} --test-kind {kind}",
        f"aiwfctl e2e readiness --work-id {work_id} --test-kind {kind}",
        f"aiwfctl e2e run --work-id {work_id} --test-kind {kind} --dry-run",
    ]
    write_json(plan_json_path(resolved_work_dir, kind), plan)
    return plan


def load_plan(repo_root: Path, work_id: str, work_dir: str, test_kind: str) -> tuple[Path, dict[str, Any]]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    path = plan_json_path(resolved_work_dir, kind)
    payload = read_json(path, default={})
    if not isinstance(payload, dict) or not payload:
        return resolved_work_dir, {}
    return resolved_work_dir, payload


def build_e2e_contract(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
    objective: str = "",
    trigger: str = "",
    preconditions: list[str] | None = None,
    expected_route: list[str] | None = None,
    expected_state_transitions: list[str] | None = None,
    expected_side_effects: list[str] | None = None,
    observable_endpoints: list[str] | None = None,
    timing_constraints: list[str] | None = None,
    ordering_constraints: list[str] | None = None,
    duplicate_handling: str = "",
    retry_expectations: list[str] | None = None,
    recovery_expectations: list[str] | None = None,
    required_stubs: list[str] | None = None,
    failure_signals: list[str] | None = None,
    evidence_requirements: list[str] | None = None,
    human_review_points: list[str] | None = None,
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir, plan = load_plan(repo_root, work_id, work_dir, kind)
    plan_objective = str(plan.get("objective", "")).strip() if plan else ""
    plan_expectations = normalize_items(plan.get("expectations", []) if plan else [])
    plan_stubs = normalize_items(plan.get("required_stubs", []) if plan else [])
    plan_commands = normalize_items(plan.get("commands", []) if plan else [])
    test_contract = {
        "objective": objective.strip() or plan_objective,
        "trigger": trigger.strip() or (plan_commands[0] if plan_commands else ""),
        "preconditions": normalize_items(preconditions),
        "expected_route": normalize_items(expected_route),
        "expected_state_transitions": normalize_items(expected_state_transitions),
        "expected_side_effects": normalize_items(expected_side_effects),
        "observable_endpoints": normalize_items(observable_endpoints),
        "timing_constraints": normalize_items(timing_constraints),
        "ordering_constraints": normalize_items(ordering_constraints),
        "duplicate_handling": duplicate_handling.strip(),
        "retry_expectations": normalize_items(retry_expectations),
        "recovery_expectations": normalize_items(recovery_expectations),
        "required_stubs": normalize_items(required_stubs) or plan_stubs,
        "failure_signals": normalize_items(failure_signals),
        "evidence_requirements": normalize_items(evidence_requirements) or plan_expectations,
        "human_review_points": normalize_items(human_review_points),
    }
    missing = missing_contract_fields(test_contract)
    contract = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_CONTRACT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-test-contract",
        "status": "ready" if not missing else "draft-with-gaps",
        "test_kind": kind,
        "work_id": work_id,
        "plan_path": relative_artifact(repo_root, plan_json_path(resolved_work_dir, kind)),
        "test_contract": test_contract,
        "missing_contract_fields": missing,
        "responsibility_split": {
            "contract_designer": "検証契約を作成し、観測可能な成功/失敗条件を固定する。",
            "readiness_checker": "契約、Stub、実行command、証跡要件の不足を確認する。",
            "runner": "契約に基づく実行commandだけを実行し、結果を記録する。",
            "observer": "経路、状態遷移、副作用、endpoint、失敗signalを観測する。",
            "verifier": "観測結果を契約と照合する。",
            "explainer": "契約との差分、不足、異常、再テスト理由を説明する。",
            "human_reviewer": "契約と証跡をもとに最終判断する。",
        },
        "human_review_required": True,
        "created_at": utc_now_iso(),
    }
    contract["artifacts"] = write_contract_artifacts(repo_root, resolved_work_dir, contract)
    contract["next_actions"] = [
        f"aiwfctl e2e readiness --work-id {work_id} --test-kind {kind}",
        f"aiwfctl e2e run --work-id {work_id} --test-kind {kind} --dry-run",
    ]
    write_json(contract_json_path(resolved_work_dir, kind), contract)
    return contract


def build_e2e_contract_scaffold(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
    force: bool = False,
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir, plan = load_plan(repo_root, work_id, work_dir, kind)
    json_path = contract_json_path(resolved_work_dir, kind)
    markdown_path = contract_markdown_path(resolved_work_dir, kind)
    artifacts = {
        "contract_json": relative_artifact(repo_root, json_path),
        "contract_markdown": relative_artifact(repo_root, markdown_path),
    }
    if json_path.exists() and not force:
        return {
            "schema_version": SCHEMA_VERSION,
            "schema": E2E_TEST_CONTRACT_SCHEMA,
            "artifact_type": f"{artifact_prefix(kind)}-test-contract-scaffold",
            "status": "blocked",
            "test_kind": kind,
            "work_id": work_id,
            "artifacts": artifacts,
            "blockers": [
                f"{artifacts['contract_json']} already exists. Use --force only when overwriting the scaffold is intentional."
            ],
            "next_actions": [f"aiwfctl e2e readiness --work-id {work_id} --test-kind {kind}"],
        }

    plan_commands = normalize_items(plan.get("commands", []) if plan else [])
    test_contract = {
        "objective": str(plan.get("objective", "")).strip() if plan else "",
        "trigger": plan_commands[0] if plan_commands else "",
        "preconditions": [],
        "expected_route": [],
        "expected_state_transitions": [],
        "expected_side_effects": [],
        "observable_endpoints": [],
        "timing_constraints": [],
        "ordering_constraints": [],
        "duplicate_handling": "",
        "retry_expectations": [],
        "recovery_expectations": [],
        "required_stubs": normalize_items(plan.get("required_stubs", []) if plan else []),
        "failure_signals": [],
        "evidence_requirements": normalize_items(plan.get("expectations", []) if plan else []),
        "human_review_points": [],
    }
    missing = missing_contract_fields(test_contract)
    contract = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_CONTRACT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-test-contract",
        "status": "draft-with-gaps",
        "test_kind": kind,
        "work_id": work_id,
        "plan_path": relative_artifact(repo_root, plan_json_path(resolved_work_dir, kind)),
        "scaffold": True,
        "scaffold_instructions": [
            "Fill every missing_contract_fields item before readiness/run.",
            "Keep success conditions, failure signals, evidence requirements, and human review points observable.",
            "Run aiwfctl e2e readiness after editing this contract.",
        ],
        "test_contract": test_contract,
        "missing_contract_fields": missing,
        "responsibility_split": build_responsibility_split(),
        "human_review_required": True,
        "created_at": utc_now_iso(),
        "next_actions": [f"aiwfctl e2e readiness --work-id {work_id} --test-kind {kind}"],
    }
    contract["artifacts"] = write_contract_artifacts(repo_root, resolved_work_dir, contract)
    write_json(json_path, contract)
    return contract


def load_contract(repo_root: Path, work_id: str, work_dir: str, test_kind: str) -> tuple[Path, dict[str, Any]]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    path = contract_json_path(resolved_work_dir, kind)
    payload = read_json(path, default={})
    if not isinstance(payload, dict) or not payload:
        return resolved_work_dir, {}
    return resolved_work_dir, payload


def build_e2e_readiness(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir, plan = load_plan(repo_root, work_id, work_dir, kind)
    _, contract = load_contract(repo_root, work_id, str(resolved_work_dir), kind)
    blockers: list[str] = []
    if not plan:
        blockers.append(f"{relative_artifact(repo_root, plan_json_path(resolved_work_dir, kind))} がありません。")
    if not contract:
        blockers.append(f"{relative_artifact(repo_root, contract_json_path(resolved_work_dir, kind))} is missing.")
    missing_contract = normalize_items(contract.get("missing_contract_fields", []) if contract else [])
    blockers.extend(f"test contract field missing: {item}" for item in missing_contract)
    contract_payload = contract.get("test_contract", {}) if contract else {}
    consistency_checks, consistency_warnings, consistency_blockers = build_contract_consistency_checks(plan, contract)
    blockers.extend(consistency_blockers)
    stub_checks = []
    stubs = sorted(
        {
            *normalize_items(plan.get("required_stubs") if plan else []),
            *normalize_items(contract_payload.get("required_stubs", []) if contract_payload else []),
        }
    )
    for stub in stubs:
        path = resolve_path(repo_root, resolved_work_dir, stub)
        stub_checks.append(
            {
                "stub": stub,
                "path": relative_artifact(repo_root, path),
                "exists": path.exists(),
            }
        )
    missing_stubs = [item["stub"] for item in stub_checks if not item["exists"]]
    blockers.extend(f"required stub missing: {item}" for item in missing_stubs)
    commands = normalize_items(plan.get("commands") if plan else [])
    if plan and not commands:
        blockers.append("E2E/integration run command が未定義です。")
    status = "ready" if not blockers else "blocked"
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-readiness",
        "status": status,
        "test_kind": kind,
        "work_id": work_id,
        "plan_path": relative_artifact(repo_root, plan_json_path(resolved_work_dir, kind)),
        "contract_path": relative_artifact(repo_root, contract_json_path(resolved_work_dir, kind)),
        "contract_status": contract.get("status", "missing") if contract else "missing",
        "missing_contract_fields": missing_contract,
        "contract_consistency_status": "blocker"
        if consistency_blockers
        else "warning"
        if consistency_warnings
        else "pass",
        "contract_consistency_checks": consistency_checks,
        "warnings": consistency_warnings,
        "stub_checks": stub_checks,
        "command_count": len(commands),
        "blockers": blockers,
        "generated_at": utc_now_iso(),
        "next_actions": [
            f"aiwfctl e2e plan --work-id {work_id} --test-kind {kind}"
            if not plan
            else f"aiwfctl e2e contract --work-id {work_id} --test-kind {kind}"
            if not contract or contract.get("status") != "ready"
            else f"aiwfctl e2e run --work-id {work_id} --test-kind {kind} --dry-run"
        ],
    }
    output_path = evidence_json_path(resolved_work_dir, kind, "readiness")
    result["artifacts"] = {"readiness_json": relative_artifact(repo_root, output_path)}
    write_json(output_path, result)
    return result


def truncate_text(value: str) -> str:
    return value if len(value) <= RUN_OUTPUT_PREVIEW_CHARS else value[:RUN_OUTPUT_PREVIEW_CHARS]


def execute_command(command: str, cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=DEFAULT_COMMAND_TIMEOUT_SECONDS,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": truncate_text(completed.stdout),
        "stderr": truncate_text(completed.stderr),
    }


def build_e2e_run(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
    dry_run: bool = False,
    human_check: str = "pending",
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir, plan = load_plan(repo_root, work_id, work_dir, kind)
    readiness = build_e2e_readiness(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), test_kind=kind)
    commands = normalize_items(plan.get("commands") if plan else [])
    blockers = list(readiness.get("blockers", []))
    if not dry_run and human_check != "approved":
        blockers.append("実行には --human-check approved が必要です。")
    results: list[dict[str, Any]] = []
    status = "dry-run" if dry_run else "blocked"
    if not dry_run and not blockers and human_check == "approved":
        status = "completed"
        for command in commands:
            try:
                command_result = execute_command(command, repo_root)
            except subprocess.TimeoutExpired as exc:
                command_result = {
                    "command": command,
                    "exit_code": 124,
                    "stdout": truncate_text(exc.stdout or ""),
                    "stderr": truncate_text(exc.stderr or "command timed out"),
                }
            results.append(command_result)
        if any(item["exit_code"] != 0 for item in results):
            status = "failed"
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-run-result",
        "status": status,
        "test_kind": kind,
        "work_id": work_id,
        "dry_run": dry_run,
        "human_check": human_check,
        "plan_path": relative_artifact(repo_root, plan_json_path(resolved_work_dir, kind)),
        "commands": commands,
        "command_results": results,
        "blockers": blockers,
        "generated_at": utc_now_iso(),
        "next_actions": [
            f"aiwfctl e2e observe --work-id {work_id} --test-kind {kind}",
            f"aiwfctl e2e verify --work-id {work_id} --test-kind {kind}",
        ],
    }
    output_path = evidence_json_path(resolved_work_dir, kind, "run-result")
    result["artifacts"] = {"run_result_json": relative_artifact(repo_root, output_path)}
    write_json(output_path, result)
    return result


def build_e2e_observation(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    run_path = evidence_json_path(resolved_work_dir, kind, "run-result")
    run_result = read_json(run_path, default={})
    command_results = run_result.get("command_results", []) if isinstance(run_result, dict) else []
    failed_commands = [item for item in command_results if item.get("exit_code") != 0]
    status = "observed" if run_result else "blocked"
    blockers = [] if run_result else [f"{relative_artifact(repo_root, run_path)} がありません。"]
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-observation",
        "status": status,
        "test_kind": kind,
        "work_id": work_id,
        "run_result_path": relative_artifact(repo_root, run_path),
        "observed_command_count": len(command_results),
        "failed_command_count": len(failed_commands),
        "observations": [
            {
                "command": item.get("command", ""),
                "exit_code": item.get("exit_code"),
                "status": "pass" if item.get("exit_code") == 0 else "fail",
            }
            for item in command_results
        ],
        "blockers": blockers,
        "generated_at": utc_now_iso(),
        "next_actions": [f"aiwfctl e2e verify --work-id {work_id} --test-kind {kind}"],
    }
    output_path = evidence_json_path(resolved_work_dir, kind, "observation")
    result["artifacts"] = {"observation_json": relative_artifact(repo_root, output_path)}
    write_json(output_path, result)
    return result


def build_e2e_verification(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir, plan = load_plan(repo_root, work_id, work_dir, kind)
    _, contract = load_contract(repo_root, work_id, str(resolved_work_dir), kind)
    run_result = read_json(evidence_json_path(resolved_work_dir, kind, "run-result"), default={})
    observation = read_json(evidence_json_path(resolved_work_dir, kind, "observation"), default={})
    expectation_count = len(normalize_items(plan.get("expectations") if plan else []))
    contract_payload = contract.get("test_contract", {}) if contract else {}
    evidence_requirements = normalize_items(
        contract_payload.get("evidence_requirements", []) if contract_payload else []
    )
    blockers = []
    if not contract:
        blockers.append("test contract is missing.")
    if contract and contract.get("status") != "ready":
        blockers.extend(
            f"test contract field missing: {item}"
            for item in normalize_items(contract.get("missing_contract_fields", []))
        )
    if not plan:
        blockers.append("test plan がありません。")
    if not run_result:
        blockers.append("run result がありません。")
    if not observation:
        blockers.append("observation がありません。")
    if run_result and run_result.get("status") not in {"completed", "dry-run"}:
        blockers.append(f"run status が {run_result.get('status')} です。")
    if observation and observation.get("failed_command_count", 0):
        blockers.append("失敗した command があります。")
    status = "pass" if not blockers and run_result.get("status") == "completed" else "human-check-required"
    if run_result and run_result.get("status") == "dry-run":
        status = "dry-run"
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-verification",
        "status": status,
        "test_kind": kind,
        "work_id": work_id,
        "contract_path": relative_artifact(repo_root, contract_json_path(resolved_work_dir, kind)),
        "contract_status": contract.get("status", "missing") if contract else "missing",
        "expectation_count": expectation_count,
        "contract_evidence_requirement_count": len(evidence_requirements),
        "verified_expectations": [
            {"expectation": item, "status": "human-review-required"}
            for item in normalize_items(plan.get("expectations") if plan else [])
        ],
        "contract_verification": [
            {"requirement": item, "status": "human-review-required"}
            for item in evidence_requirements
        ],
        "blockers": blockers,
        "generated_at": utc_now_iso(),
        "next_actions": [
            f"aiwfctl e2e explain --work-id {work_id} --test-kind {kind}",
            f"aiwfctl e2e review-plan --work-id {work_id} --test-kind {kind}",
            f"aiwfctl e2e coverage --work-id {work_id} --test-kind {kind}",
        ],
    }
    output_path = evidence_json_path(resolved_work_dir, kind, "verification")
    result["artifacts"] = {"verification_json": relative_artifact(repo_root, output_path)}
    write_json(output_path, result)
    return result


def build_explanation_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['test_kind'].upper()} Test Explanation",
        "",
        f"- Work ID: `{result['work_id']}`",
        f"- Status: `{result['status']}`",
        "",
        "## Summary",
        result["summary"],
        "",
        "## Blockers",
    ]
    lines.extend(f"- {item}" for item in result["blockers"] or ["なし"])
    lines.extend(["", "## Next Actions"])
    lines.extend(f"- `{item}`" for item in result["next_actions"])
    lines.extend(["", "## Human Check"])
    lines.append("最終的な公開・push・外部環境での実行可否は人間が確認します。")
    return "\n".join(lines)


def build_e2e_explanation(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    verification = read_json(evidence_json_path(resolved_work_dir, kind, "verification"), default={})
    blockers = verification.get("blockers", []) if isinstance(verification, dict) else []
    status = verification.get("status", "human-check-required") if isinstance(verification, dict) else "human-check-required"
    summary = (
        "実行結果は期待条件と照合済みです。"
        if status == "pass"
        else "不足または未確認の証跡があります。Human Checkで不足分を確認してください。"
    )
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-explanation",
        "status": status,
        "test_kind": kind,
        "work_id": work_id,
        "summary": summary,
        "blockers": blockers,
        "generated_at": utc_now_iso(),
        "next_actions": [
            f"aiwfctl e2e run --work-id {work_id} --test-kind {kind} --human-check approved",
            f"aiwfctl e2e verify --work-id {work_id} --test-kind {kind}",
        ],
    }
    json_path = evidence_json_path(resolved_work_dir, kind, "explanation")
    markdown_path = evidence_markdown_path(resolved_work_dir, kind, "explanation")
    result["artifacts"] = {
        "explanation_json": relative_artifact(repo_root, json_path),
        "explanation_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, result)
    write_markdown(markdown_path, build_explanation_markdown(result))
    return result


def load_evidence(work_dir: Path, test_kind: str, phase: str) -> dict[str, Any]:
    payload = read_json(evidence_json_path(work_dir, test_kind, phase), default={})
    return payload if isinstance(payload, dict) else {}


def collect_loop_problems(
    *,
    explicit_problems: list[str],
    readiness: dict[str, Any],
    run_result: dict[str, Any],
    observation: dict[str, Any],
    verification: dict[str, Any],
) -> list[dict[str, Any]]:
    problems: list[dict[str, Any]] = []
    for problem in normalize_items(explicit_problems):
        problems.append({"source": "explicit", "severity": "high", "summary": problem})
    for source, payload in [
        ("readiness", readiness),
        ("run-result", run_result),
        ("verification", verification),
    ]:
        for blocker in normalize_items(payload.get("blockers", []) if payload else []):
            problems.append({"source": source, "severity": "high", "summary": blocker})
    for item in run_result.get("command_results", []) if run_result else []:
        if item.get("exit_code") != 0:
            problems.append(
                {
                    "source": "run-result",
                    "severity": "high",
                    "summary": f"command failed: {item.get('command', '')}",
                    "exit_code": item.get("exit_code"),
                    "stderr": truncate_text(str(item.get("stderr", ""))),
                }
            )
    if observation and observation.get("failed_command_count", 0):
        problems.append(
            {
                "source": "observation",
                "severity": "high",
                "summary": f"failed command count: {observation.get('failed_command_count')}",
            }
        )
    return problems


def build_review_plan_command(
    *,
    work_id: str,
    review_id: str,
    intent: str,
    evidence_paths: list[str],
    reviewers: list[str],
    changed_files: list[str],
) -> str:
    parts = [
        "aiwfctl",
        "review",
        "plan",
        "--work-id",
        command_value(work_id),
        "--intent",
        command_value(intent),
    ]
    if review_id:
        parts.extend(["--review-id", command_value(review_id)])
    for evidence in evidence_paths:
        parts.extend(["--evidence", command_value(evidence)])
    for reviewer in reviewers:
        parts.extend(["--reviewer", command_value(reviewer)])
    for changed_file in changed_files:
        parts.extend(["--changed-file", command_value(changed_file)])
    return " ".join(parts)


def build_review_evidence_gate_command(
    *,
    work_id: str,
    review_id: str,
    evidence_paths: list[str],
    required_tests: list[str],
    test_specs: list[str],
) -> str:
    parts = ["aiwfctl", "review", "evidence-gate", "--work-id", command_value(work_id)]
    if review_id:
        parts.extend(["--review-id", command_value(review_id)])
    for evidence in evidence_paths:
        parts.extend(["--evidence", command_value(evidence)])
    for required_test in required_tests:
        parts.extend(["--required-test", command_value(required_test)])
    for test_spec in test_specs:
        parts.extend(["--test-spec", command_value(test_spec)])
    return " ".join(parts)


def existing_e2e_review_evidence_paths(repo_root: Path, work_dir: Path, test_kind: str) -> list[str]:
    candidates = [
        plan_json_path(work_dir, test_kind),
        contract_json_path(work_dir, test_kind),
        evidence_json_path(work_dir, test_kind, "readiness"),
        evidence_json_path(work_dir, test_kind, "run-result"),
        evidence_json_path(work_dir, test_kind, "observation"),
        evidence_json_path(work_dir, test_kind, "verification"),
        evidence_json_path(work_dir, test_kind, "explanation"),
    ]
    return [relative_artifact(repo_root, path) for path in candidates if path.exists()]


def evidence_requirement_covered(requirement: str, evidence_paths: list[str]) -> bool:
    normalized = requirement.strip().lower()
    if not normalized:
        return True
    return any(normalized in path.lower() or Path(path).name.lower() in normalized for path in evidence_paths)


def build_e2e_review_plan_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['test_kind'].upper()} Review Council Bridge",
        "",
        f"- Work ID: `{result['work_id']}`",
        f"- Status: `{result['status']}`",
        "",
        "## Responsibility Model",
        "",
        "E2E runtime は検証契約、実行結果、観測結果、照合結果を保存します。Review Council はその証跡を読み、UX、Accessibility、Frontend Architecture、Runtime Architecture などの専門観点で指摘、反例、追加evidence要件を構造化します。最終判断は Human Review で行います。",
        "",
        "## Required Reviewers",
    ]
    lines.extend(f"- `{item}`" for item in result.get("required_reviewers", []))
    lines.extend(["", "## Evidence"])
    lines.extend(f"- `{item}`" for item in result.get("evidence_paths", []) or ["none"])
    lines.extend(["", "## Review Commands"])
    lines.append(f"- `{result.get('review_plan_command', '')}`")
    lines.append(f"- `{result.get('review_start_command', '')}`")
    lines.append(f"- `{result.get('review_evidence_gate_command', '')}`")
    lines.extend(["", "## Review Focus"])
    lines.extend(f"- {item}" for item in result.get("review_focus", []))
    return "\n".join(lines)


def build_e2e_review_plan(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
    review_id: str = "",
    reviewers: list[str] | None = None,
    changed_files: list[str] | None = None,
    intent: str = "",
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir, plan = load_plan(repo_root, work_id, work_dir, kind)
    _, contract = load_contract(repo_root, work_id, str(resolved_work_dir), kind)
    verification = load_evidence(resolved_work_dir, kind, "verification")
    contract_payload = contract.get("test_contract", {}) if contract else {}
    evidence_paths = existing_e2e_review_evidence_paths(repo_root, resolved_work_dir, kind)
    normalized_reviewers = normalize_items(reviewers) or DEFAULT_REVIEW_COUNCIL_REVIEWERS
    normalized_changed_files = normalize_items(changed_files)
    required_tests = sorted(
        dict.fromkeys(
            [
                *normalize_items(plan.get("expectations", []) if plan else []),
                *normalize_items(contract_payload.get("evidence_requirements", []) if contract_payload else []),
            ]
        )
    )
    test_specs = [
        relative_artifact(repo_root, path)
        for path in [plan_json_path(resolved_work_dir, kind), contract_json_path(resolved_work_dir, kind)]
        if path.exists()
    ]
    blockers: list[str] = []
    if not verification:
        blockers.append(f"{relative_artifact(repo_root, evidence_json_path(resolved_work_dir, kind, 'verification'))} is missing.")
    if not contract:
        blockers.append(f"{relative_artifact(repo_root, contract_json_path(resolved_work_dir, kind))} is missing.")
    review_intent = intent.strip() or (
        f"{artifact_prefix(kind).upper()} verification evidence を Review Council で確認し、"
        "UX、Accessibility、Frontend Architecture、Runtime Architecture の観点で追加リスクを構造化する。"
    )
    review_plan_command = build_review_plan_command(
        work_id=work_id,
        review_id=review_id,
        intent=review_intent,
        evidence_paths=evidence_paths,
        reviewers=normalized_reviewers,
        changed_files=normalized_changed_files,
    )
    review_start_command = review_plan_command.replace("aiwfctl review plan", "aiwfctl review start", 1)
    review_evidence_gate_command = build_review_evidence_gate_command(
        work_id=work_id,
        review_id=review_id,
        evidence_paths=evidence_paths,
        required_tests=required_tests,
        test_specs=test_specs,
    )
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-test-review-plan",
        "status": "review-ready" if not blockers else "blocked",
        "test_kind": kind,
        "work_id": work_id,
        "review_id": review_id,
        "required_reviewers": normalized_reviewers,
        "review_focus": [
            "UX: user-visible route and recovery behavior",
            "Accessibility: keyboard/screen-reader/error-state observability",
            "Frontend Architecture: UI state, side effects, and testability",
            "Runtime Architecture: trace/log/evidence completeness and replayability",
        ],
        "evidence_paths": evidence_paths,
        "required_tests": required_tests,
        "test_specs": test_specs,
        "changed_files": normalized_changed_files,
        "verification_status": verification.get("status", "missing") if verification else "missing",
        "verification_blockers": normalize_items(verification.get("blockers", []) if verification else []),
        "review_plan_command": review_plan_command,
        "review_start_command": review_start_command,
        "review_evidence_gate_command": review_evidence_gate_command,
        "blockers": blockers,
        "generated_at": utc_now_iso(),
        "next_actions": [
            review_plan_command,
            review_start_command,
            f"aiwfctl review handoff --work-id {work_id}",
            review_evidence_gate_command,
            f"aiwfctl e2e coverage --work-id {work_id} --test-kind {kind}",
            f"aiwfctl e2e explain --work-id {work_id} --test-kind {kind}",
            f"aiwfctl e2e final-gate --work-id {work_id} --test-kind {kind}",
        ],
    }
    json_path = evidence_json_path(resolved_work_dir, kind, "review-plan")
    markdown_path = evidence_markdown_path(resolved_work_dir, kind, "review-plan")
    result["artifacts"] = {
        "review_plan_json": relative_artifact(repo_root, json_path),
        "review_plan_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, result)
    write_markdown(markdown_path, build_e2e_review_plan_markdown(result))
    return result


def build_e2e_coverage_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['test_kind'].upper()} Evidence Coverage",
        "",
        f"- Work ID: `{result['work_id']}`",
        f"- Status: `{result['status']}`",
        "",
        "## Contract",
        "",
        f"- Contract Status: `{result.get('contract_status', 'missing')}`",
        f"- Missing Contract Fields: `{len(result.get('missing_contract_fields', []))}`",
        "",
        "## Evidence",
        "",
    ]
    for item in result.get("evidence_coverage", []):
        mark = "ok" if item.get("exists") else "missing"
        lines.append(f"- {item.get('phase')}: `{mark}` - `{item.get('path')}`")
    lines.extend(["", "## Requirement Coverage", ""])
    requirement_coverage = result.get("evidence_requirement_coverage", [])
    if requirement_coverage:
        for item in requirement_coverage:
            mark = "covered" if item.get("covered") else "human-review-required"
            lines.append(f"- {item.get('requirement')}: `{mark}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {item}" for item in result.get("blockers", []) or ["none"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- `{item}`" for item in result.get("next_actions", []))
    return "\n".join(lines)


def build_e2e_coverage(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir, plan = load_plan(repo_root, work_id, work_dir, kind)
    _, contract = load_contract(repo_root, work_id, str(resolved_work_dir), kind)
    contract_payload = contract.get("test_contract", {}) if contract else {}
    evidence_paths = existing_e2e_review_evidence_paths(repo_root, resolved_work_dir, kind)
    expected_paths = [
        ("plan", plan_json_path(resolved_work_dir, kind)),
        ("contract", contract_json_path(resolved_work_dir, kind)),
        *[(phase, evidence_json_path(resolved_work_dir, kind, phase)) for phase in CORE_EVIDENCE_PHASES],
        *[(phase, evidence_json_path(resolved_work_dir, kind, phase)) for phase in REVIEW_EVIDENCE_PHASES],
    ]
    evidence_coverage = [
        {
            "phase": phase,
            "path": relative_artifact(repo_root, path),
            "exists": path.exists(),
            "required": phase in {"plan", "contract", *CORE_EVIDENCE_PHASES},
        }
        for phase, path in expected_paths
    ]
    missing_required = [item["path"] for item in evidence_coverage if item["required"] and not item["exists"]]
    evidence_requirements = normalize_items(contract_payload.get("evidence_requirements", []) if contract_payload else [])
    requirement_coverage = [
        {
            "requirement": requirement,
            "covered": evidence_requirement_covered(requirement, evidence_paths),
        }
        for requirement in evidence_requirements
    ]
    unresolved_requirements = [
        item["requirement"] for item in requirement_coverage if not item["covered"]
    ]
    missing_contract = normalize_items(contract.get("missing_contract_fields", []) if contract else [])
    blockers: list[str] = []
    if missing_required:
        blockers.extend(f"required evidence missing: {item}" for item in missing_required)
    if missing_contract:
        blockers.extend(f"test contract field missing: {item}" for item in missing_contract)
    status = "pass" if not blockers else "human-check-required"
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-coverage",
        "status": status,
        "test_kind": kind,
        "work_id": work_id,
        "contract_status": contract.get("status", "missing") if contract else "missing",
        "missing_contract_fields": missing_contract,
        "evidence_coverage": evidence_coverage,
        "evidence_requirement_coverage": requirement_coverage,
        "unresolved_evidence_requirements": unresolved_requirements,
        "blockers": blockers,
        "generated_at": utc_now_iso(),
        "next_actions": [
            f"aiwfctl e2e review-plan --work-id {work_id} --test-kind {kind}",
            f"aiwfctl e2e explain --work-id {work_id} --test-kind {kind}",
            f"aiwfctl e2e final-gate --work-id {work_id} --test-kind {kind}",
        ],
    }
    json_path = evidence_json_path(resolved_work_dir, kind, "coverage")
    markdown_path = evidence_markdown_path(resolved_work_dir, kind, "coverage")
    result["artifacts"] = {
        "coverage_json": relative_artifact(repo_root, json_path),
        "coverage_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, result)
    write_markdown(markdown_path, build_e2e_coverage_markdown(result))
    return result


def build_e2e_final_gate_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['test_kind'].upper()} Human Final Gate",
        "",
        f"- Work ID: `{result['work_id']}`",
        f"- Status: `{result['status']}`",
        f"- Human Decision: `{result['human_decision']}`",
        f"- Reviewer: `{result.get('reviewer', '')}`",
        f"- Approved At: `{result.get('approved_at', '') or '-'}`",
        f"- Review Reference: `{result.get('review_reference', '') or '-'}`",
        "",
        "## Decision Inputs",
        "",
    ]
    for key, value in result.get("decision_inputs", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Decision Reason", "", result.get("decision_reason", "") or "none"])
    lines.extend(["", "## Notes", "", result.get("note", "") or "none"])
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {item}" for item in result.get("blockers", []) or ["none"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- `{item}`" for item in result.get("next_actions", []))
    return "\n".join(lines)


def build_e2e_final_gate(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
    human_decision: str = "pending",
    reviewer: str = "",
    decision_reason: str = "",
    review_reference: str = "",
    note: str = "",
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    verification = load_evidence(resolved_work_dir, kind, "verification")
    review_plan = load_evidence(resolved_work_dir, kind, "review-plan")
    explanation = load_evidence(resolved_work_dir, kind, "explanation")
    coverage = load_evidence(resolved_work_dir, kind, "coverage") or build_e2e_coverage(
        repo_root,
        work_id=work_id,
        work_dir=str(resolved_work_dir),
        test_kind=kind,
    )
    blockers: list[str] = []
    recovery_actions: list[str] = []
    if not verification:
        blockers.append("verification evidence is missing.")
        recovery_actions.append(f"aiwfctl e2e verify --work-id {work_id} --test-kind {kind}")
    elif verification.get("status") != "pass":
        blockers.append(f"verification status is {verification.get('status')}.")
        recovery_actions.append(f"aiwfctl e2e loop --work-id {work_id} --test-kind {kind}")
    if not review_plan:
        blockers.append("review-plan evidence is missing.")
        recovery_actions.append(f"aiwfctl e2e review-plan --work-id {work_id} --test-kind {kind}")
    elif review_plan.get("status") != "review-ready":
        blockers.append(f"review-plan status is {review_plan.get('status')}.")
        recovery_actions.append(f"aiwfctl e2e review-plan --work-id {work_id} --test-kind {kind}")
    if not explanation:
        blockers.append("explanation evidence is missing.")
        recovery_actions.append(f"aiwfctl e2e explain --work-id {work_id} --test-kind {kind}")
    if coverage.get("status") != "pass":
        blockers.extend(normalize_items(coverage.get("blockers", [])))
        recovery_actions.append(f"aiwfctl e2e coverage --work-id {work_id} --test-kind {kind}")
    decision = human_decision.strip().lower() or "pending"
    if decision not in {"pending", "approved", "rejected"}:
        raise ValueError(f"Unsupported human decision: {human_decision}")
    if decision == "rejected":
        blockers.append("human reviewer rejected the E2E final gate.")
    if decision == "approved" and not reviewer.strip():
        blockers.append("reviewer is required when human decision is approved.")
        recovery_actions.append(
            f"aiwfctl e2e final-gate --work-id {work_id} --test-kind {kind} --human-decision approved --reviewer <name>"
        )
    status = "human-check-required"
    if decision == "approved" and not blockers:
        status = "pass"
    elif decision == "rejected" or blockers:
        status = "blocked"
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-human-final-gate",
        "status": status,
        "test_kind": kind,
        "work_id": work_id,
        "human_decision": decision,
        "reviewer": reviewer.strip(),
        "decision_reason": decision_reason.strip(),
        "review_reference": review_reference.strip(),
        "approved_at": utc_now_iso() if decision == "approved" and not blockers else "",
        "note": note.strip(),
        "decision_inputs": {
            "verification": relative_artifact(repo_root, evidence_json_path(resolved_work_dir, kind, "verification")),
            "review_plan": relative_artifact(repo_root, evidence_json_path(resolved_work_dir, kind, "review-plan")),
            "coverage": relative_artifact(repo_root, evidence_json_path(resolved_work_dir, kind, "coverage")),
            "explanation": relative_artifact(repo_root, evidence_json_path(resolved_work_dir, kind, "explanation")),
        },
        "blockers": blockers,
        "generated_at": utc_now_iso(),
        "next_actions": [],
    }
    if status == "human-check-required":
        result["next_actions"].append(
            f"aiwfctl e2e final-gate --work-id {work_id} --test-kind {kind} --human-decision approved --reviewer <name>"
        )
    if status == "blocked":
        result["next_actions"].extend(list(dict.fromkeys(recovery_actions)))
    json_path = evidence_json_path(resolved_work_dir, kind, "human-final-gate")
    markdown_path = evidence_markdown_path(resolved_work_dir, kind, "human-final-gate")
    result["artifacts"] = {
        "human_final_gate_json": relative_artifact(repo_root, json_path),
        "human_final_gate_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, result)
    write_markdown(markdown_path, build_e2e_final_gate_markdown(result))
    return result


def build_evidence_snapshot(repo_root: Path, path: Path, *, phase: str, required: bool) -> dict[str, Any]:
    payload = read_json(path, default={})
    exists = isinstance(payload, dict) and bool(payload)
    return {
        "phase": phase,
        "path": relative_artifact(repo_root, path),
        "required": required,
        "exists": exists,
        "artifact_type": payload.get("artifact_type", "") if exists else "",
        "status": payload.get("status", "missing") if exists else "missing",
        "generated_at": payload.get("generated_at", payload.get("created_at", "")) if exists else "",
    }


def build_e2e_evidence_package_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['test_kind'].upper()} Evidence Package",
        "",
        f"- Work ID: `{result['work_id']}`",
        f"- Status: `{result['status']}`",
        f"- Release Ready: `{str(result.get('release_ready', False)).lower()}`",
        f"- Trace ID: `{result.get('trace_id', '') or '-'}`",
        "",
        "## Summary",
        "",
        result.get("handoff_summary", ""),
        "",
        "## Artifacts",
        "",
    ]
    for item in result.get("artifact_statuses", []):
        mark = "ok" if item.get("exists") else "missing"
        lines.append(f"- {item.get('phase')}: `{mark}` / `{item.get('status')}` - `{item.get('path')}`")
    runtime_links = result.get("runtime_links", {})
    if runtime_links:
        lines.extend(["", "## Runtime Links", ""])
        for key, value in runtime_links.items():
            if value:
                lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {item}" for item in result.get("blockers", []) or ["none"])
    lines.extend(["", "## Human Review Items", ""])
    lines.extend(f"- {item}" for item in result.get("human_review_items", []) or ["none"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- `{item}`" for item in result.get("next_actions", []))
    return "\n".join(lines)


def build_e2e_evidence_package(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
    trace_id: str = "",
    output: str = "",
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir = resolve_work_dir(repo_root, work_id, work_dir)
    required_phase_names = {"readiness", "run-result", "observation", "verification", "review-plan", "coverage", "explanation"}
    artifact_statuses = [
        build_evidence_snapshot(repo_root, plan_json_path(resolved_work_dir, kind), phase="plan", required=True),
        build_evidence_snapshot(repo_root, contract_json_path(resolved_work_dir, kind), phase="contract", required=True),
    ]
    artifact_statuses.extend(
        build_evidence_snapshot(
            repo_root,
            evidence_json_path(resolved_work_dir, kind, phase),
            phase=phase,
            required=phase in required_phase_names,
        )
        for phase in PACKAGE_EVIDENCE_PHASES
    )
    by_phase = {item["phase"]: item for item in artifact_statuses}
    missing_required = [item for item in artifact_statuses if item["required"] and not item["exists"]]
    blockers = [f"required artifact missing: {item['path']}" for item in missing_required]
    for phase, expected_status in [
        ("verification", "pass"),
        ("review-plan", "review-ready"),
        ("coverage", "pass"),
    ]:
        item = by_phase.get(phase, {})
        if item.get("exists") and item.get("status") != expected_status:
            blockers.append(f"{phase} status is {item.get('status')}; expected {expected_status}.")
    final_gate = load_evidence(resolved_work_dir, kind, "human-final-gate")
    loop = load_evidence(resolved_work_dir, kind, "loop")
    human_review_items: list[str] = []
    if not final_gate:
        human_review_items.append("human-final-gate evidence is missing.")
    elif final_gate.get("status") != "pass":
        human_review_items.append(f"human-final-gate status is {final_gate.get('status')}.")
    if final_gate and final_gate.get("human_decision") != "approved":
        human_review_items.append(f"human decision is {final_gate.get('human_decision', 'missing')}.")
    if loop and loop.get("status") != "pass":
        blockers.append(f"unresolved loop status is {loop.get('status')}.")
    status = "pass"
    if blockers:
        status = "blocked"
    elif human_review_items:
        status = "human-check-required"
    evidence_paths = [item["path"] for item in artifact_statuses if item["exists"]]
    normalized_trace_id = trace_id.strip()
    runtime_links = {}
    if normalized_trace_id:
        runtime_log_output = f"work/{work_id}/test-evidence/{artifact_prefix(kind)}-test/runtime-log-export.json"
        runtime_links = {
            "trace_id": normalized_trace_id,
            "trace_show_command": f"aiwfctl trace show {normalized_trace_id} --problems",
            "log_grep_command": f"aiwfctl log grep --trace-id {normalized_trace_id}",
            "log_export_command": f"aiwfctl log export --trace-id {normalized_trace_id} --output {runtime_log_output}",
            "runtime_log_export": runtime_log_output,
        }
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{artifact_prefix(kind)}-evidence-package",
        "status": status,
        "test_kind": kind,
        "work_id": work_id,
        "trace_id": normalized_trace_id,
        "release_ready": status == "pass",
        "handoff_summary": (
            "E2E/integration evidence is packaged for handoff."
            if status == "pass"
            else "E2E/integration evidence package has missing or pending items."
        ),
        "artifact_statuses": artifact_statuses,
        "evidence_paths": evidence_paths,
        "runtime_links": runtime_links,
        "loop_status": loop.get("status", "missing") if loop else "missing",
        "blockers": blockers,
        "human_review_items": human_review_items,
        "generated_at": utc_now_iso(),
        "next_actions": [],
    }
    if status == "blocked":
        result["next_actions"].extend(
            [
                f"aiwfctl e2e coverage --work-id {work_id} --test-kind {kind}",
                f"aiwfctl e2e explain --work-id {work_id} --test-kind {kind}",
                f"aiwfctl e2e loop --work-id {work_id} --test-kind {kind}",
            ]
        )
    elif status == "human-check-required":
        result["next_actions"].append(
            f"aiwfctl e2e final-gate --work-id {work_id} --test-kind {kind} --human-decision approved --reviewer <name>"
        )
    json_path = evidence_json_path(resolved_work_dir, kind, "evidence-package")
    markdown_path = evidence_markdown_path(resolved_work_dir, kind, "evidence-package")
    result["artifacts"] = {
        "evidence_package_json": relative_artifact(repo_root, json_path),
        "evidence_package_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, result)
    write_markdown(markdown_path, build_e2e_evidence_package_markdown(result))
    if output.strip():
        output_path = Path(output.strip())
        resolved_output_path = output_path if output_path.is_absolute() else repo_root / output_path
        result["output_path"] = relative_artifact(repo_root, resolved_output_path)
        result["written"] = True
        write_json(resolved_output_path, result)
        write_json(json_path, result)
    return result


def build_loop_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['test_kind'].upper()} Test Fix Loop",
        "",
        f"- Work ID: `{result['work_id']}`",
        f"- Status: `{result['status']}`",
        f"- Loop State: `{result['loop_state']}`",
        "",
        "## Problems",
    ]
    problems = result.get("problems", [])
    if problems:
        lines.extend(f"- [{item.get('source', '')}] {item.get('summary', '')}" for item in problems)
    else:
        lines.append("- なし")
    lines.extend(["", "## Fix Instruction", result.get("fix_instruction", {}).get("summary", "") or "なし"])
    fix_commands = result.get("fix_instruction", {}).get("commands", [])
    if fix_commands:
        lines.extend(["", "## Fix Commands"])
        lines.extend(f"- `{item}`" for item in fix_commands)
    lines.extend(["", "## Runtime Links"])
    for key, value in result.get("integration_points", {}).items():
        if value:
            lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Next Actions"])
    lines.extend(f"- `{item}`" for item in result.get("next_actions", []))
    lines.extend(["", "## Retest Commands"])
    lines.extend(f"- `{item}`" for item in result.get("retest_commands", []))
    lines.extend(["", "## Human Check"])
    lines.append("修正適用、外部環境実行、pushはHuman Check後に進めます。")
    return "\n".join(lines)


def build_e2e_loop(
    repo_root: Path,
    *,
    work_id: str,
    work_dir: str = "",
    test_kind: str = "e2e",
    trace_id: str = "",
    review_id: str = "",
    issue_number: str = "",
    fix_summary: str = "",
    fix_commands: list[str] | None = None,
    reviewers: list[str] | None = None,
    changed_files: list[str] | None = None,
    problems: list[str] | None = None,
) -> dict[str, Any]:
    kind = normalize_test_kind(test_kind)
    resolved_work_dir, plan = load_plan(repo_root, work_id, work_dir, kind)
    readiness = build_e2e_readiness(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), test_kind=kind)
    run_result = load_evidence(resolved_work_dir, kind, "run-result")
    observation = load_evidence(resolved_work_dir, kind, "observation")
    if run_result and not observation:
        observation = build_e2e_observation(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), test_kind=kind)
    verification = load_evidence(resolved_work_dir, kind, "verification")
    if run_result and observation and not verification:
        verification = build_e2e_verification(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), test_kind=kind)
    explanation = build_e2e_explanation(repo_root, work_id=work_id, work_dir=str(resolved_work_dir), test_kind=kind)
    evidence_paths = [
        relative_artifact(repo_root, path)
        for path in [
            plan_json_path(resolved_work_dir, kind),
            evidence_json_path(resolved_work_dir, kind, "readiness"),
            evidence_json_path(resolved_work_dir, kind, "run-result"),
            evidence_json_path(resolved_work_dir, kind, "observation"),
            evidence_json_path(resolved_work_dir, kind, "verification"),
            evidence_json_path(resolved_work_dir, kind, "explanation"),
        ]
        if path.exists()
    ]
    loop_problems = collect_loop_problems(
        explicit_problems=normalize_items(problems),
        readiness=readiness,
        run_result=run_result,
        observation=observation,
        verification=verification,
    )
    if not run_result:
        loop_problems.append({"source": "run-result", "severity": "medium", "summary": "run result がありません。"})
    if run_result and not observation:
        loop_problems.append({"source": "observation", "severity": "medium", "summary": "observation がありません。"})
    if run_result and observation and not verification:
        loop_problems.append({"source": "verification", "severity": "medium", "summary": "verification がありません。"})
    normalized_fix_commands = normalize_items(fix_commands)
    normalized_reviewers = normalize_items(reviewers) or ["frontend-architecture", "accessibility", "ux"]
    normalized_changed_files = normalize_items(changed_files)
    test_prefix = artifact_prefix(kind)
    retest_commands = [
        f"aiwfctl e2e run --work-id {work_id} --test-kind {kind} --dry-run",
        f"aiwfctl e2e run --work-id {work_id} --test-kind {kind} --human-check approved",
        f"aiwfctl e2e observe --work-id {work_id} --test-kind {kind}",
        f"aiwfctl e2e verify --work-id {work_id} --test-kind {kind}",
        f"aiwfctl e2e loop --work-id {work_id} --test-kind {kind}",
    ]
    intent = fix_summary.strip() or f"{test_prefix.upper()} test findings の修正方針を確認し、再テスト可能な状態へ戻す。"
    review_plan = build_review_plan_command(
        work_id=work_id,
        review_id=review_id,
        intent=intent,
        evidence_paths=evidence_paths,
        reviewers=normalized_reviewers,
        changed_files=normalized_changed_files,
    )
    next_actions: list[str] = []
    if trace_id:
        next_actions.append(f"aiwfctl trace show {trace_id} --problems")
    next_actions.extend(
        [
            review_plan,
            f"aiwfctl scm compare --work-id {work_id}",
            f"aiwfctl scm commit --work-id {work_id} --message \"fix(test): address {test_prefix} findings\" --dry-run",
            *normalized_fix_commands,
            *retest_commands,
        ]
    )
    loop_state = "passed-no-fix-needed" if not loop_problems and verification.get("status") == "pass" else "fix-instruction-ready"
    status = "pass" if loop_state == "passed-no-fix-needed" else "fix-required"
    result = {
        "schema_version": SCHEMA_VERSION,
        "schema": E2E_TEST_REPORT_SCHEMA,
        "artifact_type": f"{test_prefix}-test-loop",
        "status": status,
        "loop_state": loop_state,
        "test_kind": kind,
        "work_id": work_id,
        "generated_at": utc_now_iso(),
        "problem_count": len(loop_problems),
        "problems": loop_problems,
        "fix_instruction": {
            "summary": intent,
            "commands": normalized_fix_commands,
            "human_check_required": True,
        },
        "integration_points": {
            "trace_id": trace_id,
            "review_id": review_id,
            "issue_number": issue_number,
            "scm_compare_command": f"aiwfctl scm compare --work-id {work_id}",
            "review_plan_command": review_plan,
        },
        "evidence_paths": evidence_paths,
        "source_status": {
            "plan": plan.get("status", "") if plan else "missing",
            "readiness": readiness.get("status", ""),
            "run_result": run_result.get("status", "missing") if run_result else "missing",
            "observation": observation.get("status", "missing") if observation else "missing",
            "verification": verification.get("status", "missing") if verification else "missing",
            "explanation": explanation.get("status", ""),
        },
        "next_actions": next_actions,
        "retest_commands": retest_commands,
    }
    json_path = evidence_json_path(resolved_work_dir, kind, "loop")
    markdown_path = evidence_markdown_path(resolved_work_dir, kind, "loop")
    result["artifacts"] = {
        "loop_json": relative_artifact(repo_root, json_path),
        "loop_markdown": relative_artifact(repo_root, markdown_path),
    }
    write_json(json_path, result)
    write_markdown(markdown_path, build_loop_markdown(result))
    return result


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(getattr(args, "repo_root", "") or ".").resolve()
    command = getattr(args, "e2e_command", "")
    common = {
        "work_id": getattr(args, "work_id", ""),
        "work_dir": getattr(args, "work_dir", ""),
        "test_kind": getattr(args, "test_kind", "e2e"),
    }
    if command == "plan":
        return build_e2e_plan(
            repo_root,
            **common,
            objective=getattr(args, "objective", ""),
            scenarios=getattr(args, "scenario", []),
            targets=getattr(args, "target", []),
            expectations=getattr(args, "expectation", []),
            required_stubs=getattr(args, "stub", []),
            commands=getattr(args, "run_command", []),
        )
    if command == "contract":
        if getattr(args, "contract_mode", "create") == "scaffold":
            return build_e2e_contract_scaffold(
                repo_root,
                **common,
                force=getattr(args, "force", False),
            )
        return build_e2e_contract(
            repo_root,
            **common,
            objective=getattr(args, "objective", ""),
            trigger=getattr(args, "trigger", ""),
            preconditions=getattr(args, "precondition", []),
            expected_route=getattr(args, "expected_route", []),
            expected_state_transitions=getattr(args, "expected_state_transition", []),
            expected_side_effects=getattr(args, "expected_side_effect", []),
            observable_endpoints=getattr(args, "observable_endpoint", []),
            timing_constraints=getattr(args, "timing_constraint", []),
            ordering_constraints=getattr(args, "ordering_constraint", []),
            duplicate_handling=getattr(args, "duplicate_handling", ""),
            retry_expectations=getattr(args, "retry_expectation", []),
            recovery_expectations=getattr(args, "recovery_expectation", []),
            required_stubs=getattr(args, "stub", []),
            failure_signals=getattr(args, "failure_signal", []),
            evidence_requirements=getattr(args, "evidence_requirement", []),
            human_review_points=getattr(args, "human_review_point", []),
        )
    if command == "readiness":
        return build_e2e_readiness(repo_root, **common)
    if command == "run":
        return build_e2e_run(
            repo_root,
            **common,
            dry_run=getattr(args, "dry_run", False),
            human_check=getattr(args, "human_check", "pending"),
        )
    if command == "observe":
        return build_e2e_observation(repo_root, **common)
    if command == "verify":
        return build_e2e_verification(repo_root, **common)
    if command == "explain":
        return build_e2e_explanation(repo_root, **common)
    if command == "review-plan":
        return build_e2e_review_plan(
            repo_root,
            **common,
            review_id=getattr(args, "review_id", ""),
            reviewers=getattr(args, "reviewer", []),
            changed_files=getattr(args, "changed_file", []),
            intent=getattr(args, "intent", ""),
        )
    if command == "coverage":
        return build_e2e_coverage(repo_root, **common)
    if command == "final-gate":
        return build_e2e_final_gate(
            repo_root,
            **common,
            human_decision=getattr(args, "human_decision", "pending"),
            reviewer=getattr(args, "reviewer", ""),
            decision_reason=getattr(args, "decision_reason", ""),
            review_reference=getattr(args, "review_reference", ""),
            note=getattr(args, "note", ""),
        )
    if command == "evidence-package":
        return build_e2e_evidence_package(
            repo_root,
            **common,
            trace_id=getattr(args, "trace_id", ""),
            output=getattr(args, "output", ""),
        )
    if command == "loop":
        return build_e2e_loop(
            repo_root,
            **common,
            trace_id=getattr(args, "trace_id", ""),
            review_id=getattr(args, "review_id", ""),
            issue_number=getattr(args, "issue_number", ""),
            fix_summary=getattr(args, "fix_summary", ""),
            fix_commands=getattr(args, "fix_command", []),
            reviewers=getattr(args, "reviewer", []),
            changed_files=getattr(args, "changed_file", []),
            problems=getattr(args, "problem", []),
        )
    raise ValueError(f"Unknown e2e command: {command}")


def format_result(result: dict[str, Any]) -> str:
    title = str(result.get("artifact_type", "e2e-result")).replace("-", " ").title()
    lines = [
        title,
        "",
        f"Status   : {result.get('status', '')}",
        f"Work ID  : {result.get('work_id', '')}",
        f"Test Kind: {result.get('test_kind', '')}",
    ]
    artifacts = result.get("artifacts", {})
    if artifacts:
        lines.extend(["", "Artifacts"])
        lines.extend(f"  - {key}: {value}" for key, value in artifacts.items())
    blockers = result.get("blockers", [])
    if blockers:
        lines.extend(["", "Blockers"])
        lines.extend(f"  - {item}" for item in blockers)
    next_actions = result.get("next_actions", [])
    if next_actions:
        lines.extend(["", "Next Actions"])
        lines.extend(f"  - {item}" for item in next_actions)
    return "\n".join(lines).rstrip()
