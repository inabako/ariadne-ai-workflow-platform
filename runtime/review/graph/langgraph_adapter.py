from __future__ import annotations

import importlib.util
from typing import Any, Callable


def langgraph_available() -> bool:
    return importlib.util.find_spec("langgraph") is not None


def _langgraph_graph_api() -> tuple[Any, str, str] | None:
    try:
        from langgraph.graph import END, START, StateGraph
    except Exception:
        return None
    return StateGraph, START, END


def build_langgraph_review_plan(session: dict[str, Any]) -> dict[str, Any]:
    packet = session.get("packet", {})
    reviewers = [str(item) for item in packet.get("required_reviewers", []) if str(item).strip()]
    reviewer_nodes = [f"reviewer:{reviewer}" for reviewer in reviewers]
    nodes = [
        "review-intake",
        "packet-freeze",
        "risk-classification",
        *reviewer_nodes,
        "finding-normalization",
        "issue-ledger",
        "reinspection",
        "challenge-round",
        "evidence-gate",
        "verdict-policy",
        "knowledge-capture",
    ]
    edges = [
        ["review-intake", "packet-freeze"],
        ["packet-freeze", "risk-classification"],
    ]
    edges.extend(["risk-classification", node] for node in reviewer_nodes)
    edges.extend([node, "finding-normalization"] for node in reviewer_nodes)
    edges.extend(
        [
            ["finding-normalization", "issue-ledger"],
            ["issue-ledger", "reinspection"],
            ["reinspection", "issue-ledger"],
            ["issue-ledger", "challenge-round"],
            ["challenge-round", "evidence-gate"],
            ["evidence-gate", "verdict-policy"],
            ["verdict-policy", "knowledge-capture"],
        ]
    )
    return {
        "schema_version": "1.0",
        "artifact_type": "review-council-langgraph-plan",
        "adapter": "langgraph",
        "available": langgraph_available(),
        "review_id": session.get("review_id", ""),
        "work_id": session.get("work_id", ""),
        "nodes": nodes,
        "edges": edges,
        "execution_mode": "langgraph" if langgraph_available() else "runtime-runbook",
        "real_execution": langgraph_available(),
        "runbook": [
            {"step": index + 1, "node": node, "mode": "state-evaluation"}
            for index, node in enumerate(nodes)
        ],
        "note": "LangGraph is confined to orchestration planning; Review Council contracts remain in runtime/review/domain.",
    }


def _completed_reviewers(session: dict[str, Any]) -> set[str]:
    return {
        str(item.get("reviewer", ""))
        for item in session.get("findings", [])
        if str(item.get("reviewer", "")).strip()
    }


def _open_review_issues(session: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in session.get("issues", [])
        if item.get("status") == "open" and (item.get("blocking") or item.get("severity") in {"critical", "high"})
    ]


def _challenge_blockers(session: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in session.get("challenge_rounds", [])
        if item.get("counterexample_found") and item.get("status") in {"completed", "human-check-required"}
    ]


def _node(node_id: str, status: str, reason: str = "") -> dict[str, Any]:
    return {
        "node": node_id,
        "status": status,
        "reason": reason,
    }


def _command_review_id(session: dict[str, Any]) -> str:
    return str(session.get("review_id", ""))


def _append_trace(state: dict[str, Any], node: str) -> dict[str, Any]:
    trace = list(state.get("graph_execution_trace", []))
    trace.append(node)
    state["graph_execution_trace"] = trace
    return state


def _graph_node(node: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def run(state: dict[str, Any]) -> dict[str, Any]:
        return _append_trace(dict(state), node)

    return run


def _route_after_reviewers(state: dict[str, Any]) -> str:
    session = state.get("session", {})
    packet = session.get("packet", {})
    required = {str(item) for item in packet.get("required_reviewers", []) if str(item).strip()}
    missing = required - _completed_reviewers(session)
    return "specialist-reviewers" if missing else "finding-normalization"


def _route_after_issue_ledger(state: dict[str, Any]) -> str:
    return "reinspection" if _open_review_issues(state.get("session", {})) else "challenge-round"


def _route_after_challenge(state: dict[str, Any]) -> str:
    session = state.get("session", {})
    if _challenge_blockers(session) or not bool(session.get("challenge_completed", False)):
        return "finalize"
    return "evidence-gate"


def _route_after_evidence(state: dict[str, Any]) -> str:
    session = state.get("session", {})
    evidence_gate = session.get("evidence_gate") or {}
    if evidence_gate.get("status") == "blocked" or not bool(session.get("evidence_verified", False)):
        return "finalize"
    return "verdict-policy"


def _route_after_verdict(state: dict[str, Any]) -> str:
    session = state.get("session", {})
    verdict = session.get("verdict") or {}
    return "knowledge-capture" if str(verdict.get("verdict", "")) else "finalize"


def _compile_langgraph_review_app() -> Any:
    api = _langgraph_graph_api()
    if api is None:
        raise RuntimeError("LangGraph is not installed.")
    StateGraph, START, END = api
    graph = StateGraph(dict)
    for node in [
        "review-intake",
        "packet-freeze",
        "risk-classification",
        "specialist-reviewers",
        "finding-normalization",
        "issue-ledger",
        "reinspection",
        "challenge-round",
        "evidence-gate",
        "verdict-policy",
        "knowledge-capture",
    ]:
        graph.add_node(node, _graph_node(node))

    def finalize(state: dict[str, Any]) -> dict[str, Any]:
        state = _append_trace(dict(state), "finalize")
        result = _evaluate_review_state_rules(state.get("session", {}), run_id=str(state.get("run_id", "")))
        result["execution_mode"] = "langgraph"
        result["graph_execution"] = {
            "engine": "langgraph",
            "compiled": True,
            "trace": state.get("graph_execution_trace", []),
        }
        state["result"] = result
        return state

    graph.add_node("finalize", finalize)
    graph.add_edge(START, "review-intake")
    graph.add_edge("review-intake", "packet-freeze")
    graph.add_edge("packet-freeze", "risk-classification")
    graph.add_conditional_edges(
        "risk-classification",
        _route_after_reviewers,
        {
            "specialist-reviewers": "specialist-reviewers",
            "finding-normalization": "finding-normalization",
        },
    )
    graph.add_edge("specialist-reviewers", "finalize")
    graph.add_edge("finding-normalization", "issue-ledger")
    graph.add_conditional_edges(
        "issue-ledger",
        _route_after_issue_ledger,
        {
            "reinspection": "reinspection",
            "challenge-round": "challenge-round",
        },
    )
    graph.add_edge("reinspection", "finalize")
    graph.add_conditional_edges(
        "challenge-round",
        _route_after_challenge,
        {
            "finalize": "finalize",
            "evidence-gate": "evidence-gate",
        },
    )
    graph.add_conditional_edges(
        "evidence-gate",
        _route_after_evidence,
        {
            "finalize": "finalize",
            "verdict-policy": "verdict-policy",
        },
    )
    graph.add_conditional_edges(
        "verdict-policy",
        _route_after_verdict,
        {
            "finalize": "finalize",
            "knowledge-capture": "knowledge-capture",
        },
    )
    graph.add_edge("knowledge-capture", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


def _evaluate_with_langgraph(session: dict[str, Any], *, run_id: str) -> dict[str, Any]:
    app = _compile_langgraph_review_app()
    state = app.invoke({"session": session, "run_id": run_id, "graph_execution_trace": []})
    result = state.get("result")
    if not isinstance(result, dict):
        raise RuntimeError("LangGraph review execution did not produce a result.")
    result["available"] = True
    result["plan"]["available"] = True
    result["plan"]["execution_mode"] = "langgraph"
    result["plan"]["real_execution"] = True
    return result


def _evaluate_review_state_rules(session: dict[str, Any], *, run_id: str = "") -> dict[str, Any]:
    packet = session.get("packet", {})
    required_reviewers = {
        str(item)
        for item in packet.get("required_reviewers", [])
        if str(item).strip()
    }
    completed_reviewers = _completed_reviewers(session)
    missing_reviewers = sorted(required_reviewers - completed_reviewers)
    open_review_issues = _open_review_issues(session)
    challenge_blockers = _challenge_blockers(session)
    evidence_gate = session.get("evidence_gate") or {}
    evidence_blocked = evidence_gate.get("status") == "blocked"
    evidence_verified = bool(session.get("evidence_verified", False))
    challenge_completed = bool(session.get("challenge_completed", False))
    verdict = session.get("verdict") or {}
    verdict_value = str(verdict.get("verdict", ""))
    knowledge_capture = session.get("review_knowledge_capture") or {}
    knowledge_captured = bool(knowledge_capture.get("status") == "captured")
    handoffs = [str(item) for item in session.get("reviewer_handoffs", []) if str(item).strip()]

    node_results = [
        _node("review-intake", "completed", "review session exists"),
        _node("packet-freeze", "completed", "Review Packet is frozen"),
        _node("risk-classification", "completed", "required reviewers are recorded"),
    ]
    for reviewer in sorted(required_reviewers):
        status = "completed" if reviewer in completed_reviewers else "waiting"
        reason = "structured finding registered" if status == "completed" else "specialist finding is required"
        node_results.append(_node(f"reviewer:{reviewer}", status, reason))

    node_results.append(
        _node(
            "finding-normalization",
            "completed" if session.get("findings") else "waiting",
            "findings are normalized when registered" if session.get("findings") else "no findings are registered yet",
        )
    )
    node_results.append(
        _node(
            "issue-ledger",
            "blocked" if open_review_issues else "completed",
            "blocking or high review issues remain" if open_review_issues else "issue ledger is current",
        )
    )
    node_results.append(
        _node(
            "reinspection",
            "ready" if open_review_issues else ("completed" if session.get("reinspections") else "waiting"),
            "open issues require reinspection" if open_review_issues else "no reinspection is currently required",
        )
    )
    node_results.append(
        _node(
            "challenge-round",
            "blocked"
            if challenge_blockers
            else ("completed" if challenge_completed else ("waiting" if missing_reviewers or open_review_issues else "ready")),
            "counterexample remains"
            if challenge_blockers
            else (
                "challenge completed"
                if challenge_completed
                else (
                    "specialist findings or reinspection must complete first"
                    if missing_reviewers or open_review_issues
                    else "challenge round is required"
                )
            ),
        )
    )
    node_results.append(
        _node(
            "evidence-gate",
            "blocked" if evidence_blocked else ("completed" if evidence_verified else ("ready" if challenge_completed else "waiting")),
            "evidence gate is blocked"
            if evidence_blocked
            else ("evidence verified" if evidence_verified else ("evidence gate is required" if challenge_completed else "challenge round must complete first")),
        )
    )
    node_results.append(
        _node(
            "verdict-policy",
            "completed" if verdict_value else ("ready" if evidence_verified and challenge_completed else "waiting"),
            verdict_value or "verdict requires completed challenge and verified evidence",
        )
    )
    node_results.append(
        _node(
            "knowledge-capture",
            "completed" if knowledge_captured else ("ready" if verdict_value else "waiting"),
            "Review Council artifacts are captured for Knowledge/RAG"
            if knowledge_captured
            else ("verdict is ready for knowledge capture" if verdict_value else "verdict must complete first"),
        )
    )

    review_id = _command_review_id(session)
    next_actions: list[dict[str, Any]] = []
    if required_reviewers and not handoffs:
        next_actions.append(
            {
                "action": "create-reviewer-handoffs",
                "reason": "reviewer handoff packets have not been written",
                "command": f"aiwfctl review handoff --review-id {review_id}",
            }
        )
    for reviewer in missing_reviewers:
        next_actions.append(
            {
                "action": "register-specialist-finding",
                "reviewer": reviewer,
                "reason": "required reviewer has not produced a structured finding",
                "command": (
                    f"aiwfctl review add-finding --review-id {review_id} --reviewer {reviewer} "
                    "--category <category> --severity <severity> --claim \"<claim>\" --verdict <verdict>"
                ),
            }
        )
    for issue in open_review_issues:
        finding_ids = [str(item) for item in issue.get("finding_ids", []) if str(item).strip()]
        next_actions.append(
            {
                "action": "reinspect-review-issue",
                "issue_id": str(issue.get("issue_id", "")),
                "reason": "blocking or high review issue remains open",
                "command": (
                    f"aiwfctl review reinspect --review-id {review_id} "
                    f"{' '.join(f'--finding-id {item}' for item in finding_ids)} "
                    "--status verified --reviewer <reviewer> --summary \"<summary>\""
                ).strip(),
            }
        )
    if not missing_reviewers and not open_review_issues and not challenge_completed:
        next_actions.append(
            {
                "action": "run-challenge-round",
                "reason": "challenge round must complete before evidence gate and verdict",
                "command": (
                    f"aiwfctl review challenge --review-id {review_id} "
                    "--challenger runtime-quality --summary \"<summary>\""
                ),
            }
        )
    if challenge_completed and not evidence_verified:
        next_actions.append(
            {
                "action": "run-evidence-gate",
                "reason": "evidence must be verified before verdict",
                "command": f"aiwfctl review evidence-gate --review-id {review_id}",
            }
        )
    if challenge_completed and evidence_verified and not verdict_value:
        next_actions.append(
            {
                "action": "decide-verdict",
                "reason": "all orchestration prerequisites are ready for verdict policy",
                "command": f"aiwfctl review verdict --review-id {review_id}",
            }
        )
    if verdict_value and not knowledge_captured:
        next_actions.append(
            {
                "action": "capture-review-knowledge",
                "reason": "Review Council verdict and artifacts should be captured for future RAG/Knowledge reuse",
                "command": f"aiwfctl review capture-knowledge --review-id {review_id}",
            }
        )

    if verdict_value and knowledge_captured:
        status = "orchestration-completed"
    elif challenge_blockers or evidence_blocked or open_review_issues:
        status = "orchestration-blocked"
    elif next_actions:
        status = "orchestration-waiting"
    else:
        status = "orchestration-ready"

    return {
        "schema_version": "1.0",
        "artifact_type": "review-council-orchestration",
        "adapter": "langgraph",
        "available": langgraph_available(),
        "execution_mode": "runtime-runbook",
        "graph_execution": {
            "engine": "runtime-runbook",
            "compiled": False,
            "trace": [item["node"] for item in node_results],
        },
        "run_id": run_id,
        "review_id": review_id,
        "work_id": session.get("work_id", ""),
        "status": status,
        "plan": build_langgraph_review_plan(session),
        "node_results": node_results,
        "next_actions": next_actions,
        "checks": {
            "required_reviewers": sorted(required_reviewers),
            "completed_reviewers": sorted(completed_reviewers),
            "missing_reviewers": missing_reviewers,
            "open_review_issue_ids": [str(item.get("issue_id", "")) for item in open_review_issues],
            "challenge_completed": challenge_completed,
            "challenge_blockers": len(challenge_blockers),
            "evidence_verified": evidence_verified,
            "evidence_blocked": evidence_blocked,
            "verdict": verdict_value,
            "knowledge_captured": knowledge_captured,
        },
    }


def evaluate_langgraph_review_state(session: dict[str, Any], *, run_id: str = "") -> dict[str, Any]:
    if langgraph_available():
        try:
            return _evaluate_with_langgraph(session, run_id=run_id)
        except Exception as exc:
            result = _evaluate_review_state_rules(session, run_id=run_id)
            result["execution_mode"] = "runtime-runbook"
            result["graph_execution"] = {
                "engine": "runtime-runbook",
                "compiled": False,
                "trace": [item["node"] for item in result.get("node_results", [])],
                "fallback_reason": f"langgraph_execution_failed: {exc}",
            }
            return result
    return _evaluate_review_state_rules(session, run_id=run_id)
