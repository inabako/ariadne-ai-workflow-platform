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

- 確認内容: Review Council startがReview Packetをfreezeし、session、index、人間が読めるreport artifactを出力することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_start_review_freezes_packet_and_writes_artifacts
  - source: `runtime/tests/test_review_council_runtime.py:30`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `start_args`
- 期待結果: review sessionが `packet-frozen` になり、required reviewerが保持され、packet hashが安定した長さで、期待するartifactがすべて存在する。

#### RT-UT-CASE-REVIEW-002

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_plan_review_selects_specialists_and_writes_plan_artifacts
```

- 確認内容: Review Council planがpacket signalからrequired specialist reviewerを選択し、plan artifactを出力することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_plan_review_selects_specialists_and_writes_plan_artifacts
  - source: `runtime/tests/test_review_council_runtime.py:42`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: runtime/security/logging/test intent, changed file, evidence
- 期待結果: plan statusが `planned` になり、runtime/security/observability/testing reviewerが選択され、start commandがpacket argsを保持し、JSON/Markdown plan artifactが存在する。

#### RT-UT-CASE-REVIEW-003

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_handoff_review_writes_per_reviewer_packets
```

- 確認内容: Review Council handoffがrequired reviewerごとにreviewer packetを出力し、session statusへ記録することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_handoff_review_writes_per_reviewer_packets
  - source: `runtime/tests/test_review_council_runtime.py:69`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: frozen session with security/runtime reviewers
- 期待結果: handoff statusが `handoff-ready` になり、reviewer packet Markdown fileが存在し、各packetにstructured `add-finding` commandが含まれる。

#### RT-UT-CASE-REVIEW-004

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_orchestrate_review_waits_for_missing_reviewer
```

- 確認内容: Review Council orchestrationがrequired reviewerの不足を検出し、次のspecialist finding actionを生成することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_orchestrate_review_waits_for_missing_reviewer
  - source: `runtime/tests/test_review_council_runtime.py:95`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: frozen session, reviewer handoffs, one completed security finding
- 期待結果: orchestration statusが `orchestration-waiting` になり、runtime reviewer不足、`add-finding` next action、artifact生成、session status更新が記録される。

#### RT-UT-CASE-REVIEW-005

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_next_action_prefers_specialist_run_for_missing_reviewer
```

- 確認内容: Review Council next-action が、未実施reviewer作業をspecialist run commandへ変換することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_next_action_prefers_specialist_run_for_missing_reviewer
  - source: `runtime/tests/test_review_council_runtime.py:143`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: frozen session, handoff artifacts, orchestration result
- 期待結果: next action status が `action-required`、selected action が `register-specialist-finding` となり、`agent_command` が `aiwfctl review run-specialist` を使う。

#### RT-UT-CASE-REVIEW-006

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_run_specialist_review_writes_agent_packet
```

- 確認内容: Review Council specialist run が、prompt、handoff、output、finding registration commandを含むAgent execution packetを出力することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_run_specialist_review_writes_agent_packet
  - source: `runtime/tests/test_review_council_runtime.py:167`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: security reviewer prompt file and frozen session
- 期待結果: specialist run status が `ready` になり、security reviewer agentが選択され、prompt、handoff、artifactが作成され、session statusが `specialist-ready` になる。

#### RT-UT-CASE-REVIEW-026

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_execute_specialist_review_requires_human_check
```

- 確認内容: 明示的なHuman Check承認が与えられるまで、Specialist Agent execution がblockされることを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_execute_specialist_review_requires_human_check
  - source: `runtime/tests/test_review_council_runtime.py:196`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: Review Council session, existing specialist prompt, `execute-specialist` with `human_check=pending`
- 期待結果: execution artifact type が `review-council-specialist-execution`、status が `human-check-required` となり、local Agent commandを呼ばずにexecution evidence JSONが出力される。

#### RT-UT-CASE-REVIEW-027

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_execute_specialist_review_runs_command_and_drafts_findings
```

- 確認内容: 承認済みSpecialist Agent execution が stdout/stderr を取得し、review reportを実体化し、reportからdraft findingを作成することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_execute_specialist_review_runs_command_and_drafts_findings
  - source: `runtime/tests/test_review_council_runtime.py:223`
  - fixture/arg: `tmp_path` (temporary filesystem), monkeypatched `subprocess.run`
  - parameter: names=なし, case=なし
  - inline input: approved local agent command template, specialist packet stdin, stdout review report with one finding
- 期待結果: execution statusが `completed` になり、stdout evidenceとoutput reportが存在し、finding draftが1件生成され、sessionにcompleted specialist executionが記録される。

#### RT-UT-CASE-REVIEW-007

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_draft_findings_extracts_structured_report_and_commands
```

- 確認内容: Review Council draft-findingsがspecialist review reportからstructured Finding candidateを抽出し、formal findingを変更せずregistration commandを出力することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_draft_findings_extracts_structured_report_and_commands
  - source: `runtime/tests/test_review_council_runtime.py:195`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: structured security specialist report with severity, verdict, evidence, required test, and requested action
- 期待結果: draft findingが1件生成され、draftがblockingで、JSON/Markdown artifactが存在し、`registration_command` が `aiwfctl review add-finding` を使い、statusが `finding-draft-ready` を報告する。

#### RT-UT-CASE-REVIEW-008

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_orchestrate_review_routes_reinspection_for_blocking_issue
```

- 確認内容: Review Council orchestrationがopen blocking issueまたはhigh issueをreinspection nodeへ送ることを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_orchestrate_review_routes_reinspection_for_blocking_issue
  - source: `runtime/tests/test_review_council_runtime.py:251`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: one high `changes-required` security finding
- 期待結果: orchestration status が `orchestration-blocked` になり、issue `RI-001` がopenで、`reinspect-review-issue` actionが出力され、reinspection nodeがreadyになる。

#### RT-UT-CASE-REVIEW-009

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_summary_review_exports_snapshot_and_next_actions
```

- 確認内容: Review Council summaryがreviewer進捗、issue、gate、next actionを含む機械可読および人間可読snapshotを出力することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_summary_review_exports_snapshot_and_next_actions
  - source: `runtime/tests/test_review_council_runtime.py:298`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: one high changes-required finding, orchestration result, and summary export id
- 期待結果: Summary JSON/Markdown artifactが存在し、countにfinding 1件とblocking open issue 1件が含まれ、selected actionがreinspectionを要求し、session statusが `orchestration-blocked` のままになる。

#### RT-UT-CASE-REVIEW-010

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_human_gate_review_records_blocked_and_approved_decisions
```

- 確認内容: Review Council human-gateがblocked/approvedのHuman Gate decisionをrestart guidanceとsummary artifact付きで記録することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_human_gate_review_records_blocked_and_approved_decisions
  - source: `runtime/tests/test_review_council_runtime.py:367`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: summary export, pending final-verdict gate, approved final-verdict gate
- 期待結果: pending gateはrepair command付きでblockされ、approved gateはJSON/Markdown artifactを出力し、statusが永続化済みhuman gate approvalを報告する。

#### RT-UT-CASE-REVIEW-011

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_human_gate_risk_acceptance_feeds_approved_with_risk_verdict
```

- 確認内容: non-blocking issueが残る場合、Review Council risk acceptance Human Gateがverdict policyへ反映されることを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_human_gate_risk_acceptance_feeds_approved_with_risk_verdict
  - source: `runtime/tests/test_review_council_runtime.py:418`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: non-blocking warning finding, pass finding, pending verdict, approved risk-acceptance gate
- 期待結果: pending verdictはhuman decisionを要求し、approved risk gateでは `APPROVED_WITH_RISK` が許可され、verdictに `human_check=approved` が記録される。

#### RT-UT-CASE-REVIEW-012

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_challenge_review_generates_counterexample_plan_for_open_issues
```

- 確認内容: Review Council challengeが選択されたopen issueと関連findingに対するcounterexample planを作成することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_challenge_review_generates_counterexample_plan_for_open_issues
  - source: `runtime/tests/test_review_council_runtime.py:506`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: one high changes-required finding and challenge with no explicit issue id
- 期待結果: Challengeが `RI-001` を対象にし、`FND-001` をlinkし、open issue向けcounterexample checkを保存する。

#### RT-UT-CASE-REVIEW-013

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_reinspection_records_issue_linkage_and_evidence_results
```

- 確認内容: Review Council reinspectionが関連issue id、previous finding status、evidence path checkを記録することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_reinspection_records_issue_linkage_and_evidence_results
  - source: `runtime/tests/test_review_council_runtime.py:555`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: one high finding and one reinspection evidence file
- 期待結果: Reinspectionが `RI-001` をlinkし、previous `FND-001` statusをopenとして記録し、evidence resultが存在する。

#### RT-UT-CASE-REVIEW-014

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_evidence_gate_records_artifact_level_results
```

- 確認内容: Review Council evidence gateがevidence pathとReview Council artifact checkを記録することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_evidence_gate_records_artifact_level_results
  - source: `runtime/tests/test_review_council_runtime.py:605`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: evidence file, required test text, and generated Review Council artifacts
- 期待結果: Evidence gateがverifiedになり、evidence resultとartifact checkが存在し、review artifact欠落がない。

#### RT-UT-CASE-REVIEW-015

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_orchestrate_review_suggests_verdict_after_challenge_and_evidence
```

- 確認内容: specialist review、challenge round、evidence gate完了後に、Review Council orchestrationがverdictを提案することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_orchestrate_review_suggests_verdict_after_challenge_and_evidence
  - source: `runtime/tests/test_review_council_runtime.py:656`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: pass finding, completed challenge round, verified evidence gate
- 期待結果: challengeとevidence checkがtrueになり、`decide-verdict` next actionが出力され、verdict-policy nodeがreadyになる。

#### RT-UT-CASE-REVIEW-016

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_review_knowledge_capture_writes_rag_candidates_after_verdict
```

- 確認内容: Review Council knowledge captureがverdict後にRAG candidateを出力し、orchestration checkを更新することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_review_knowledge_capture_writes_rag_candidates_after_verdict
  - source: `runtime/tests/test_review_council_runtime.py:721`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: approved review flow and capture-knowledge command
- 期待結果: knowledge capture statusが `captured` になり、RAG candidateとartifactが存在し、orchestrationがknowledge capturedを報告する。

#### RT-UT-CASE-REVIEW-024

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_review_rag_build_writes_source_markdown_and_manifest
```

- 確認内容: Review Council RAG build bridgeがfull RAG pipelineを実行せず、RAG source Markdown documentとmanifestを出力することを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_review_rag_build_writes_source_markdown_and_manifest
  - source: `runtime/tests/test_review_council_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: Review Council session, summary export, `review rag-build` with `run=False`
- 期待結果: bridge artifact typeが `review-council-rag-build` になり、source Markdownが `work/db/.../rag/review-council/...` 配下に存在し、manifestに `aiwfctl rag build` commandが含まれる。

#### RT-UT-CASE-REVIEW-025

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_review_rag_build_can_run_existing_pipeline
```

- 確認内容: 明示指定された場合、Review Council RAG build bridgeが既存のfile-based RAG build pipelineを呼び出せることを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_review_rag_build_can_run_existing_pipeline
  - source: `runtime/tests/test_review_council_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem), monkeypatched `rag_build.run`
  - parameter: names=なし, case=なし
  - inline input: Review Council session, `review rag-build` with `run=True`, `duckdb_migrate=True`, `skip_optimization=True`
- 期待結果: bridgeがRAG build resultを返し、`document_type=review-council`、生成された `source_dir`、DuckDB migration flag、optimization flagを既存RAG pipelineへ渡す。

#### RT-UT-CASE-REVIEW-017

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_add_finding_groups_issue_and_verdict_blocks_on_required_change
```

- 確認内容: Review Council add-findingがspecialist findingを正規化し、Review Issueへgroup化し、required reviewerが不足している場合にverdictをblockすることを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_add_finding_groups_issue_and_verdict_blocks_on_required_change
  - source: `runtime/tests/test_review_council_runtime.py:800`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `start_args`, `add_finding`, `decide_verdict`
- 期待結果: highの `changes-required` findingがblocking `RI-001` issueになり、verdictがmissing reviewerとblocking issue check付きで `HUMAN_DECISION_REQUIRED` を返す。

#### RT-UT-CASE-REVIEW-018

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_verdict_approves_after_required_reviewers_and_gates_pass
```

- 確認内容: すべてのrequired reviewerがstructured findingを提出し、evidence/challenge gateがpassした後だけ、Review Council verdictがapproveすることを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_verdict_approves_after_required_reviewers_and_gates_pass
  - source: `runtime/tests/test_review_council_runtime.py:848`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `start_args`, pass findings, evidence and challenge flags
- 期待結果: required reviewer完了が検出され、openのReview Issueが残らず、final verdictが `APPROVED` になる。

#### RT-UT-CASE-REVIEW-019

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_ctl_review_parser_and_json_flow
```

- 確認内容: `aiwfctl review` parser and dispatch path create plan/start/handoff/orchestrate/next-action/summary/human-gate/run-specialist/draft-findings/status outputs through JSON.
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_ctl_review_parser_and_json_flow
  - source: `runtime/tests/test_review_council_runtime.py:891`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `ctl.build_parser`, `review plan`, `review start`, `review handoff`, `review orchestrate`, `review next-action`, `review summary`, `review human-gate`, `review run-specialist`, `review draft-findings`, `review status`
- 期待結果: CTL routeがplan/session/operational commandのJSONを返し、summary/human-gate/specialist/draft artifact typeが返され、statusが永続化済みdraft stateを報告する。

#### RT-UT-CASE-REVIEW-020

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_challenge_and_evidence_gate_are_saved_for_verdict
```

- 確認内容: Review Council challengeとevidence-gate resultが永続化され、CLI flagを再指定せずにverdictで再利用されることを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_challenge_and_evidence_gate_are_saved_for_verdict
  - source: `runtime/tests/test_review_council_runtime.py:1054`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: evidence file, unit test specification file, pass findings, challenge record, evidence gate
- 期待結果: challenge statusが `completed`、evidence gate statusが `verified` になり、保存済みevidence/challenge stateを使ってverdictが `APPROVED` を返す。

#### RT-UT-CASE-REVIEW-021

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_reinspection_closes_blocking_finding_before_verdict
```

- 確認内容: Review Council reinspectionがblocking findingをverifiedにし、verdict前に対応するReview Issueを削除できることを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_reinspection_closes_blocking_finding_before_verdict
  - source: `runtime/tests/test_review_council_runtime.py:1133`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: high changes-required finding, reinspection status, challenge, evidence gate
- 期待結果: reinspection resultが `verified` になり、evidence gateがpassし、verdictが `APPROVED` を返す。

#### RT-UT-CASE-REVIEW-022

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_challenge_counterexample_blocks_verdict
```

- 確認内容: challenge roundがcounterexampleを記録した場合、Review Council verdictがblockすることを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_challenge_counterexample_blocks_verdict
  - source: `runtime/tests/test_review_council_runtime.py:1220`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: pass finding, challenge with counterexample, evidence gate
- 期待結果: verdictが `HUMAN_DECISION_REQUIRED` を返し、challenge blocker 1件を報告する。

#### RT-UT-CASE-REVIEW-023

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_langgraph_adapter_returns_dependency_free_plan
```

- 確認内容: LangGraph orchestration がadapter skeletonに留まり、dependency requirementをReview Council domain logicへ漏らさないことを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_langgraph_adapter_returns_dependency_free_plan
  - source: `runtime/tests/test_review_council_runtime.py:1291`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: Review Council session and adapter plan builder
- 期待結果: planがLangGraphをadapterとして識別し、reviewer nodeとreinspectionを含み、challenge-to-evidence orchestration edgeを持つ。

#### RT-UT-CASE-REVIEW-028

- pytest node id:

```text
runtime/tests/test_review_council_runtime.py::test_langgraph_adapter_invokes_compiled_state_graph
```

- 確認内容: LangGraphが利用可能な場合、Review Council がcompile済みLangGraph StateGraph execution pathを使うことを確認します。
- 入力値:
  - pytest node: runtime/tests/test_review_council_runtime.py::test_langgraph_adapter_invokes_compiled_state_graph
  - source: `runtime/tests/test_review_council_runtime.py`
  - fixture/arg: `tmp_path` (temporary filesystem), fake LangGraph `StateGraph`
  - parameter: names=なし, case=なし
  - inline input: 未実施reviewerを持つReview Council sessionとmonkeypatch済みLangGraph graph API
- 期待結果: orchestration result が `execution_mode=langgraph`、`compiled=true` を報告し、visited graph node traceを記録し、次のhandoff actionを出力する。
