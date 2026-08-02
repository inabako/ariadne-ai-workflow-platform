# test_expectation_design_runtime.py

このファイルは `runtime/tests/test_expectation_design_runtime.py` の pytest node id 単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 7 |

## ケース一覧

#### RT-UT-CASE-018A

- pytest node id:

```text
runtime/tests/test_expectation_design_runtime.py::test_expectation_weight_normalization_and_critical_gate
```

- 確認内容: Expectation weight が正規化され、Critical expectation 違反が候補推薦を止めることを確認します。
- 入力値:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_expectation_design_runtime.py:13`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `expectations`
- 期待結果: candidate score、critical violation count、recommendable flag が expectation evaluator contract と一致します。

#### RT-UT-CASE-018B

- pytest node id:

```text
runtime/tests/test_expectation_design_runtime.py::test_expectation_violation_detection_classifies_design_risks
```

- 確認内容: Design expectation violation detection が critical、major、minor、ambiguous、unverified、positive-surprise risk を分類することを確認します。
- 入力値:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_expectation_design_runtime.py:52`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `expectations`
- 期待結果: violation severity と summary count が設計risk categoryを網羅します。

#### RT-UT-CASE-018C

- pytest node id:

```text
runtime/tests/test_expectation_design_runtime.py::test_design_expectation_cli_initializes_compares_and_gates
```

- 確認内容: `aiwfctl design expectation` が sample artifact の初期化、候補比較、Human Gate decision 記録を実行できることを確認します。
- 入力値:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_expectation_design_runtime.py:101`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし case=なし
  - inline input: `init_args`, `init_payload`, `expectation_set`, `usage_context`, `expectation_conflicts`, `weights`
- 期待結果: JSON artifact、comparison report section、artifact index entry、approved Human Gate output が生成されます。

#### RT-UT-CASE-018D

- pytest node id:

```text
runtime/tests/test_expectation_design_runtime.py::test_design_expectation_requires_json_source_artifacts
```

- 確認内容: Expectation-Driven Design の source artifact が JSON のみで生成されることを確認します。
- 入力値:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_expectation_design_runtime.py:305`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし case=なし
  - inline input: `init_args`, `compare_args`, `payload`
- 期待結果: 必要な JSON artifact が存在し、YAML variant は存在せず、comparison が成功します。

#### RT-UT-CASE-018E

- pytest node id:

```text
runtime/tests/test_expectation_design_runtime.py::test_design_expectation_remaining_workflow_commands_generate_artifacts
```

- 確認内容: 残りの expectation design command が scaffold、feasibility、extraction、review、refinement、contract、verification、feedback、dispatch artifact を生成することを確認します。
- 入力値:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_expectation_design_runtime.py:333`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし case=なし
  - inline input: `init_args`, `scaffold_args`, `scaffold_payload`, `candidate_generate_args`, `feasibility_args`, `feasibility_payload`
- 期待結果: workflow command が期待される status code で完了し、schema-backed artifact と event log entry が生成されます。

#### RT-UT-CASE-018F

- pytest node id:

```text
runtime/tests/test_expectation_design_runtime.py::test_design_expectation_agent_extraction_and_review_council_sync
```

- 確認内容: Agent extraction request と Review Council sync が design comparison と Human Gate 判断材料へ反映されることを確認します。
- 入力値:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_expectation_design_runtime.py:491`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし case=なし
  - inline input: `init_args`, `request_args`, `request_payload`, `extract_args`, `extract_payload`, `expectation_set`
- 期待結果: agent output が取り込まれ、dispatch が期待 reviewer を選択し、council feedback が comparison report を更新し、未解決blocking issueはgateをpendingにします。

#### RT-UT-CASE-018G

- pytest node id:

```text
runtime/tests/test_expectation_design_runtime.py::test_expectation_design_schema_files_are_registered
```

- 確認内容: Expectation-Driven Design schema constant が実在する JSON Schema file を指すことを確認します。
- 入力値:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_expectation_design_runtime.py:681`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `payload`
- 期待結果: 登録済み schema file が読み込め、draft 2020-12 の object schema を宣言しています。
