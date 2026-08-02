# test_e2e_runtime.py

このファイルは `runtime/tests/test_e2e_runtime.py` の pytest node id と確認観点を記録します。

| Item | Value |
| --- | ---: |
| cases | 18 |

## Cases

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_runtime_full_flow_counts_and_writes_artifacts
```

- 確認内容: E2E runtime が plan、contract、readiness、run、observe、verify、explain の成果物を作成し、verify 後に Review Council 接続導線を出す。
- 入力値: `tmp_path`, `work_id`, stub file, test command, expectation, ready contract
- 期待結果: `verification` が `pass` になり、`e2e review-plan` が next action に含まれる。

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_review_plan_bridges_verification_to_review_council
```

- 確認内容: verification evidence から Review Council bridge を作成する。
- 入力値: `tmp_path`, `work_id`, dry-run evidence, verification, review_id, changed file
- 期待結果: `e2e-test-review-plan` が `review-ready` になり、reviewer、evidence、review command が保存される。

#### RT-UT-CASE-AUTO-003

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_coverage_reports_contract_and_evidence_completion
```

- 確認内容: contract field と required evidence の coverage を集計する。
- 入力値: `tmp_path`, `work_id`, ready contract, completed run evidence, observation, verification
- 期待結果: required evidence が揃っている場合、`e2e-coverage` が `pass` になり、`coverage.md` が作成される。

#### RT-UT-CASE-AUTO-004

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_final_gate_records_human_approval_after_review
```

- 確認内容: verification、Review Council bridge、coverage、explanation を入力に Human final gate を記録する。
- 入力値: `tmp_path`, `work_id`, verification, review-plan, coverage, explanation, human decision, reviewer
- 期待結果: `--human-decision approved` と reviewer 指定時に `e2e-human-final-gate` が `pass` になり、`approved_at` が記録される。

#### RT-UT-CASE-AUTO-005

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_final_gate_guides_missing_prerequisite_commands
```

- 確認内容: final gate に必要な prerequisite evidence が不足している場合、具体的な復旧 command を提示する。
- 入力値: `tmp_path`, `work_id`, approved human decision, missing verification/review-plan/explanation
- 期待結果: `blocked` になり、`e2e verify`、`e2e review-plan`、`e2e explain` が next action に含まれる。

#### RT-UT-CASE-AUTO-006

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_evidence_package_summarizes_artifacts_for_handoff
```

- 確認内容: E2E evidence package が plan、contract、各 evidence、Human final gate を handoff 用に集約する。
- 入力値: `tmp_path`, `work_id`, approved final gate, completed evidence set
- 期待結果: `e2e-evidence-package` が `pass` になり、`evidence-package.md` が作成される。

#### RT-UT-CASE-AUTO-007

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_evidence_package_links_trace_and_detects_unresolved_loop
```

- 確認内容: evidence package が trace/log 参照を保存し、未解決 loop を release blocker として検出する。
- 入力値: `tmp_path`, `work_id`, trace_id, output path, explicit unresolved loop
- 期待結果: `blocked` になり、trace/log command、`output_path`、未解決 loop blocker が保存される。

#### RT-UT-CASE-AUTO-008

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_runtime_run_requires_human_check_before_execution
```

- 確認内容: `aiwfctl e2e run` 相当の実行が Human Check なしでは外部 command を実行しない。
- 入力値: `monkeypatch`, `tmp_path`, `work_id`, dry-run execution guard
- 期待結果: `run-result.json` が `blocked` になり、dry-run では command が実行されない。

#### RT-UT-CASE-AUTO-009

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_runtime_reports_missing_plan_and_stub_readiness
```

- 確認内容: test plan 不足および required stub 不足を readiness で検出する。
- 入力値: `tmp_path`, `work_id`, missing stub path
- 期待結果: readiness が `blocked` になり、不足 plan / stub が blockers に記録される。

#### RT-UT-CASE-AUTO-010

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_contract_requires_all_verification_fields
```

- 確認内容: 検証契約の必須項目不足を `missing_contract_fields` と readiness blocker に記録する。
- 入力値: `tmp_path`, `work_id`, minimum plan
- 期待結果: contract が `draft-with-gaps` になり、不足項目が明示される。

#### RT-UT-CASE-AUTO-011

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_contract_scaffold_writes_draft_and_protects_existing
```

- 確認内容: `e2e contract scaffold` が編集用 draft を作成し、既存 contract を不用意に上書きしない。
- 入力値: `tmp_path`, `work_id`, plan objective, command, expectation
- 期待結果: 初回は `draft-with-gaps`、2回目は `blocked` になる。

#### RT-UT-CASE-AUTO-012

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_readiness_reports_contract_plan_consistency
```

- 確認内容: contract trigger / observable endpoint と plan.commands の軽量整合性を確認する。
- 入力値: `tmp_path`, `work_id`, mismatched trigger, UI observable endpoint, unit-test-like command
- 期待結果: trigger 不一致が blocker、UI観測点と command の弱い整合が warning になる。

#### RT-UT-CASE-AUTO-013

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_aiwfctl_e2e_command_routes_and_writes_json
```

- 確認内容: `aiwfctl e2e plan`、`contract`、`run --dry-run` が CLI から route される。
- 入力値: `tmp_path`, `work_id`, `plan_args`, `contract_args`, `dry_run_args`
- 期待結果: integration test 用 JSON artifact path が返る。

#### RT-UT-CASE-AUTO-014

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_aiwfctl_e2e_review_plan_routes_review_council_bridge
```

- 確認内容: `aiwfctl e2e review-plan` が CLI から route される。
- 入力値: `tmp_path`, `work_id`, review_id, reviewer, changed file
- 期待結果: `e2e-test-review-plan` が `review-ready` になり、review_id と reviewer が保存される。

#### RT-UT-CASE-AUTO-015

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_aiwfctl_e2e_final_gate_routes_human_decision
```

- 確認内容: `aiwfctl e2e final-gate` が CLI から route され、Human decision、判断理由、参照先を保存する。
- 入力値: `tmp_path`, `work_id`, approved human decision, reviewer, decision_reason, review_reference
- 期待結果: approved + reviewer 指定時に `human-final-gate.json` が作成され、監査項目が返る。

#### RT-UT-CASE-AUTO-016

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_aiwfctl_e2e_evidence_package_routes_handoff_bundle
```

- 確認内容: `aiwfctl e2e evidence-package` が CLI から route され、trace/log参照と output copy を持つ handoff bundle を作成する。
- 入力値: `tmp_path`, `work_id`, completed evidence set, approved final gate, trace_id, output path
- 期待結果: `e2e-evidence-package` が `pass` になり、`output_path` と runtime links が返る。

#### RT-UT-CASE-AUTO-017

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_e2e_loop_bundles_problem_fix_review_scm_and_retest
```

- 確認内容: 失敗した E2E 実行から、問題、修正指示、Review Council、SCM、再テスト導線を1つの loop artifact に束ねる。
- 入力値: `monkeypatch`, `tmp_path`, `work_id`, failing command result, trace_id, review_id, fix_summary, fix_commands
- 期待結果: `loop.json` / `loop.md` が作成され、status が `fix-required` になる。

#### RT-UT-CASE-AUTO-018

- pytest node id:

```text
runtime/tests/test_e2e_runtime.py::test_aiwfctl_e2e_loop_routes_explicit_problem
```

- 確認内容: `aiwfctl e2e loop` が CLI から route され、明示 problem を含む loop evidence を返す。
- 入力値: `tmp_path`, `work_id`, CLI args, explicit problem
- 期待結果: CLI exit code が Human Check 相当の `2` になり、`e2e-test-loop` JSON が返る。
