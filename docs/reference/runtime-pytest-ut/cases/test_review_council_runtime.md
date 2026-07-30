# test_review_council_runtime.py

このファイルは `runtime/tests/test_review_council_runtime.py` の pytest node id 単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 28 |

## ケース一覧

#### RT-UT-CASE-REVIEW-001

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_start_review_freezes_packet_and_writes_artifacts
```

- Confirm: Review Council start freezes a Review Packet and writes session, index, and human-readable report artifacts.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_start_review_freezes_packet_and_writes_artifacts
  - source: `runtime/tests/test_review_council_runtime.py:30`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: `start_args`
- Expected: The review session is `packet-frozen`, required reviewers are preserved, packet hash is stable length, and all expected artifacts exist.

#### RT-UT-CASE-REVIEW-002

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_plan_review_selects_specialists_and_writes_plan_artifacts
```

- Confirm: Review Council plan selects required specialist reviewers from packet signals and writes plan artifacts.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_plan_review_selects_specialists_and_writes_plan_artifacts
  - source: `runtime/tests/test_review_council_runtime.py:42`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: runtime/security/logging/test intent, changed file, evidence
- Expected: Plan status is `planned`, runtime/security/observability/testing reviewers are selected, start command preserves packet args, and JSON/Markdown plan artifacts exist.

#### RT-UT-CASE-REVIEW-003

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_handoff_review_writes_per_reviewer_packets
```

- Confirm: Review Council handoff writes one reviewer packet per required reviewer and records it in session status.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_handoff_review_writes_per_reviewer_packets
  - source: `runtime/tests/test_review_council_runtime.py:69`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: frozen session with security/runtime reviewers
- Expected: Handoff status is `handoff-ready`, reviewer packet Markdown files exist, and each packet contains the structured `add-finding` command.

#### RT-UT-CASE-REVIEW-004

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_orchestrate_review_waits_for_missing_reviewer
```

- Confirm: Review Council orchestration detects missing required reviewers and produces the next specialist finding action.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_orchestrate_review_waits_for_missing_reviewer
  - source: `runtime/tests/test_review_council_runtime.py:95`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: frozen session, reviewer handoffs, one completed security finding
- Expected: Orchestration status is `orchestration-waiting`, runtime reviewer is missing, an `add-finding` next action is emitted, artifacts exist, and session status is updated.

#### RT-UT-CASE-REVIEW-005

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_next_action_prefers_specialist_run_for_missing_reviewer
```

- Confirm: Review Council next-action converts missing reviewer work into a specialist run command.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_next_action_prefers_specialist_run_for_missing_reviewer
  - source: `runtime/tests/test_review_council_runtime.py:143`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: frozen session, handoff artifacts, orchestration result
- Expected: Next action status is `action-required`, selected action is `register-specialist-finding`, and `agent_command` uses `aiwfctl review run-specialist`.

#### RT-UT-CASE-REVIEW-006

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_run_specialist_review_writes_agent_packet
```

- Confirm: Review Council specialist run writes an Agent execution packet with prompt, handoff, output, and finding registration command.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_run_specialist_review_writes_agent_packet
  - source: `runtime/tests/test_review_council_runtime.py:167`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: security reviewer prompt file and frozen session
- Expected: Specialist run status is `ready`, security reviewer agent is selected, prompt exists, handoff is prepared, artifacts exist, and session status becomes `specialist-ready`.

#### RT-UT-CASE-REVIEW-026

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_execute_specialist_review_requires_human_check
```

- Confirm: Specialist Agent execution is blocked until explicit Human Check approval is supplied.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_execute_specialist_review_requires_human_check
  - source: `runtime/tests/test_review_council_runtime.py:196`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: Review Council session, existing specialist prompt, `execute-specialist` with `human_check=pending`
- Expected: The execution artifact type is `review-council-specialist-execution`, status is `human-check-required`, and execution evidence JSON is written without invoking a local Agent command.

#### RT-UT-CASE-REVIEW-027

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_execute_specialist_review_runs_command_and_drafts_findings
```

- Confirm: Approved Specialist Agent execution captures stdout/stderr, materializes the review report, and creates draft findings from the report.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_execute_specialist_review_runs_command_and_drafts_findings
  - source: `runtime/tests/test_review_council_runtime.py:223`
  - fixture/arg: `tmp_path` (temporary filesystem), monkeypatched `subprocess.run`
  - parameter: names=None case=None
  - inline input: approved local agent command template, specialist packet stdin, stdout review report with one finding
- Expected: The execution status is `completed`, stdout evidence and output report exist, one finding draft is generated, and the session records the completed specialist execution.

#### RT-UT-CASE-REVIEW-007

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_draft_findings_extracts_structured_report_and_commands
```

- Confirm: Review Council draft-findings extracts structured Finding candidates from a specialist review report and writes registration commands without mutating formal findings.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_draft_findings_extracts_structured_report_and_commands
  - source: `runtime/tests/test_review_council_runtime.py:195`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: structured security specialist report with severity, verdict, evidence, required test, and requested action
- Expected: One draft finding is produced, the draft is blocking, JSON/Markdown artifacts exist, `registration_command` uses `aiwfctl review add-finding`, and status reports `finding-draft-ready`.

#### RT-UT-CASE-REVIEW-008

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_orchestrate_review_routes_reinspection_for_blocking_issue
```

- Confirm: Review Council orchestration routes open blocking or high issues into the reinspection node.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_orchestrate_review_routes_reinspection_for_blocking_issue
  - source: `runtime/tests/test_review_council_runtime.py:251`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: one high `changes-required` security finding
- Expected: Orchestration status is `orchestration-blocked`, issue `RI-001` is open, a `reinspect-review-issue` action is emitted, and the reinspection node is ready.

#### RT-UT-CASE-REVIEW-009

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_summary_review_exports_snapshot_and_next_actions
```

- Confirm: Review Council summary exports a machine-readable and human-readable snapshot with reviewer progress, issues, gates, and next actions.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_summary_review_exports_snapshot_and_next_actions
  - source: `runtime/tests/test_review_council_runtime.py:298`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: one high changes-required finding, orchestration result, and summary export id
- Expected: Summary JSON/Markdown artifacts exist, counts include one finding and one blocking open issue, selected action requests reinspection, and session status remains orchestration-blocked.

#### RT-UT-CASE-REVIEW-010

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_human_gate_review_records_blocked_and_approved_decisions
```

- Confirm: Review Council human-gate records blocked and approved Human Gate decisions with restart guidance and summary artifacts.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_human_gate_review_records_blocked_and_approved_decisions
  - source: `runtime/tests/test_review_council_runtime.py:367`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: summary export, pending final-verdict gate, approved final-verdict gate
- Expected: Pending gate is blocked with repair command, approved gate writes JSON/Markdown artifacts, and status reports persisted human gate approval.

#### RT-UT-CASE-REVIEW-011

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_human_gate_risk_acceptance_feeds_approved_with_risk_verdict
```

- Confirm: Review Council risk acceptance Human Gate feeds verdict policy when non-blocking issues remain.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_human_gate_risk_acceptance_feeds_approved_with_risk_verdict
  - source: `runtime/tests/test_review_council_runtime.py:418`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: non-blocking warning finding, pass finding, pending verdict, approved risk-acceptance gate
- Expected: Pending verdict requires human decision, approved risk gate allows `APPROVED_WITH_RISK`, and verdict records `human_check=approved`.

#### RT-UT-CASE-REVIEW-012

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_challenge_review_generates_counterexample_plan_for_open_issues
```

- Confirm: Review Council challenge creates a counterexample plan for selected open issues and related findings.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_challenge_review_generates_counterexample_plan_for_open_issues
  - source: `runtime/tests/test_review_council_runtime.py:506`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: one high changes-required finding and challenge with no explicit issue id
- Expected: Challenge targets `RI-001`, links `FND-001`, and stores a counterexample check for the open issue.

#### RT-UT-CASE-REVIEW-013

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_reinspection_records_issue_linkage_and_evidence_results
```

- Confirm: Review Council reinspection records related issue ids, previous finding status, and evidence path checks.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_reinspection_records_issue_linkage_and_evidence_results
  - source: `runtime/tests/test_review_council_runtime.py:555`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: one high finding and one reinspection evidence file
- Expected: Reinspection links `RI-001`, records previous `FND-001` status as open, and evidence result exists.

#### RT-UT-CASE-REVIEW-014

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_evidence_gate_records_artifact_level_results
```

- Confirm: Review Council evidence gate records evidence path and Review Council artifact checks.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_evidence_gate_records_artifact_level_results
  - source: `runtime/tests/test_review_council_runtime.py:605`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: evidence file, required test text, and generated Review Council artifacts
- Expected: Evidence gate is verified, evidence result exists, artifact checks are present, and no review artifacts are missing.

#### RT-UT-CASE-REVIEW-015

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_orchestrate_review_suggests_verdict_after_challenge_and_evidence
```

- Confirm: Review Council orchestration suggests verdict after specialist review, challenge round, and evidence gate complete.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_orchestrate_review_suggests_verdict_after_challenge_and_evidence
  - source: `runtime/tests/test_review_council_runtime.py:656`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: pass finding, completed challenge round, verified evidence gate
- Expected: Challenge and evidence checks are true, a `decide-verdict` next action is emitted, and the verdict-policy node is ready.

#### RT-UT-CASE-REVIEW-016

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_review_knowledge_capture_writes_rag_candidates_after_verdict
```

- Confirm: Review Council knowledge capture writes RAG candidates after verdict and updates orchestration checks.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_review_knowledge_capture_writes_rag_candidates_after_verdict
  - source: `runtime/tests/test_review_council_runtime.py:721`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: approved review flow and capture-knowledge command
- Expected: Knowledge capture status is `captured`, RAG candidates are present, artifacts exist, and orchestration reports knowledge captured.

#### RT-UT-CASE-REVIEW-024

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_review_rag_build_writes_source_markdown_and_manifest
```

- Confirm: Review Council RAG build bridge exports a RAG source Markdown document and a manifest without running the full RAG pipeline.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_review_rag_build_writes_source_markdown_and_manifest
  - source: `runtime/tests/test_review_council_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: Review Council session, summary export, `review rag-build` with `run=False`
- Expected: The bridge artifact type is `review-council-rag-build`, source Markdown exists under `work/db/.../rag/review-council/...`, and the manifest contains an `aiwfctl rag build` command.

#### RT-UT-CASE-REVIEW-025

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_review_rag_build_can_run_existing_pipeline
```

- Confirm: Review Council RAG build bridge can call the existing file-based RAG build pipeline when explicitly requested.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_review_rag_build_can_run_existing_pipeline
  - source: `runtime/tests/test_review_council_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem), monkeypatched `rag_build.run`
  - parameter: names=None case=None
  - inline input: Review Council session, `review rag-build` with `run=True`, `duckdb_migrate=True`, `skip_optimization=True`
- Expected: The bridge returns the RAG build result and passes `document_type=review-council`, generated `source_dir`, DuckDB migration flag, and optimization flag to the existing RAG pipeline.

#### RT-UT-CASE-REVIEW-017

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_add_finding_groups_issue_and_verdict_blocks_on_required_change
```

- Confirm: Review Council add-finding normalizes a specialist finding, groups it into a Review Issue, and blocks the verdict when a required reviewer is missing.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_add_finding_groups_issue_and_verdict_blocks_on_required_change
  - source: `runtime/tests/test_review_council_runtime.py:800`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: `start_args`, `add_finding`, `decide_verdict`
- Expected: A high `changes-required` finding becomes a blocking `RI-001` issue, and verdict returns `HUMAN_DECISION_REQUIRED` with missing reviewer and blocking issue checks.

#### RT-UT-CASE-REVIEW-018

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_verdict_approves_after_required_reviewers_and_gates_pass
```

- Confirm: Review Council verdict approves only after all required reviewers have provided structured findings and evidence/challenge gates pass.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_verdict_approves_after_required_reviewers_and_gates_pass
  - source: `runtime/tests/test_review_council_runtime.py:848`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: `start_args`, pass findings, evidence and challenge flags
- Expected: Required reviewer completion is detected, no Review Issues remain open, and the final verdict is `APPROVED`.

#### RT-UT-CASE-REVIEW-019

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_ctl_review_parser_and_json_flow
```

- Confirm: `aiwfctl review` parser and dispatch path create plan/start/handoff/orchestrate/next-action/summary/human-gate/run-specialist/draft-findings/status outputs through JSON.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_ctl_review_parser_and_json_flow
  - source: `runtime/tests/test_review_council_runtime.py:891`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: `ctl.build_parser`, `review plan`, `review start`, `review handoff`, `review orchestrate`, `review next-action`, `review summary`, `review human-gate`, `review run-specialist`, `review draft-findings`, `review status`
- Expected: The CTL route returns JSON for plan/session/operational commands, summary/human-gate/specialist/draft artifact types are returned, and status reports the persisted draft state.

#### RT-UT-CASE-REVIEW-020

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_challenge_and_evidence_gate_are_saved_for_verdict
```

- Confirm: Review Council challenge and evidence-gate results are persisted and reused by verdict without repeating CLI flags.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_challenge_and_evidence_gate_are_saved_for_verdict
  - source: `runtime/tests/test_review_council_runtime.py:1054`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: evidence file, unit test specification file, pass findings, challenge record, evidence gate
- Expected: Challenge status is `completed`, evidence gate status is `verified`, and verdict returns `APPROVED` using saved evidence/challenge state.

#### RT-UT-CASE-REVIEW-021

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_reinspection_closes_blocking_finding_before_verdict
```

- Confirm: Review Council reinspection can mark a blocking finding verified and remove the corresponding Review Issue before verdict.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_reinspection_closes_blocking_finding_before_verdict
  - source: `runtime/tests/test_review_council_runtime.py:1133`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: high changes-required finding, reinspection status, challenge, evidence gate
- Expected: The reinspection result is `verified`, evidence gate passes, and verdict returns `APPROVED`.

#### RT-UT-CASE-REVIEW-022

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_challenge_counterexample_blocks_verdict
```

- Confirm: Review Council verdict blocks when a challenge round records a counterexample.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_challenge_counterexample_blocks_verdict
  - source: `runtime/tests/test_review_council_runtime.py:1220`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: pass finding, challenge with counterexample, evidence gate
- Expected: Verdict returns `HUMAN_DECISION_REQUIRED` and reports one challenge blocker.

#### RT-UT-CASE-REVIEW-023

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_langgraph_adapter_returns_dependency_free_plan
```

- Confirm: LangGraph orchestration remains an adapter skeleton and does not leak dependency requirements into Review Council domain logic.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_langgraph_adapter_returns_dependency_free_plan
  - source: `runtime/tests/test_review_council_runtime.py:1291`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=None case=None
  - inline input: Review Council session and adapter plan builder
- Expected: The plan identifies LangGraph as the adapter, includes reviewer nodes and reinspection, and contains challenge-to-evidence orchestration edges.

#### RT-UT-CASE-REVIEW-028

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_langgraph_adapter_invokes_compiled_state_graph
```

- Confirm: Review Council uses a compiled LangGraph StateGraph execution path when LangGraph is available.
- Input:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_langgraph_adapter_invokes_compiled_state_graph
  - source: `runtime/tests/test_review_council_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem), fake LangGraph `StateGraph`
  - parameter: names=None case=None
  - inline input: Review Council session with missing reviewers and monkeypatched LangGraph graph API
- Expected: The orchestration result reports `execution_mode=langgraph`, `compiled=true`, records the visited graph node trace, and emits the next handoff action.
