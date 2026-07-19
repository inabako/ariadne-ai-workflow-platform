# test_self_improvement_workflow.py

このファイルは `runtime/tests/test_self_improvement_workflow.py` の pytest node id 単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 14 |

## ケース一覧

#### RT-UT-CASE-SELF-001

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_parser_and_branch_name
```

- 確認内容: self-improvement workflowのparserとbranch name生成を確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:14`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: CLI parserが期待するsubcommandを受け取り、Issue branch名が安定して生成される。

#### RT-UT-CASE-SELF-002

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_init_and_create_feedback
```

- 確認内容: feedback workspace初期化とfeedback report作成を確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:25`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `text`
- 期待結果: feedback用README、report、Context First artifactが生成される。

#### RT-UT-CASE-SELF-003

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_init_feedback_preserves_existing_readme_and_template_reader
```

- 確認内容: 既存READMEを壊さず、template readerからfeedback初期化できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:52`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 既存READMEが保持され、template由来のfeedback scaffoldが生成される。

#### RT-UT-CASE-SELF-004

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_review_feedback_updates_status_and_human_check
```

- 確認内容: feedback reviewがstatusとHuman Check欄を更新することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:73`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: review結果がfeedback reportへ追記され、human review decisionが残る。

#### RT-UT-CASE-SELF-005

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_review_feedback_requires_existing_feedback
```

- 確認内容: review対象のfeedbackが存在しない場合にエラーとして扱うことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:99`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 存在しないfeedback reviewを成功扱いにせず、必要な入力不足として検出する。

#### RT-UT-CASE-SELF-006

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_feedback_decision_accepts_human_check_or_defaults_to_proposed
```

- 確認内容: feedback decisionがHuman Check入力を優先し、未指定時はproposedへfallbackすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:113`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: human decisionとdefault proposed decisionが期待どおり解釈される。

#### RT-UT-CASE-SELF-007

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_issue_body_requires_accepted_feedback_and_renders_fit_check
```

- 確認内容: accepted feedbackからIssue bodyを生成し、fit checkを描画することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:119`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: accepted statusのfeedbackだけが標準Issue bodyとして生成される。

#### RT-UT-CASE-SELF-008

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_issue_body_requires_existing_feedback
```

- 確認内容: Issue body生成時にfeedback reportの存在を必須にすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:190`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: feedbackが存在しない場合はIssue bodyを生成しない。

#### RT-UT-CASE-SELF-009

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_issue_body_can_render_unaccepted_feedback_to_explicit_output
```

- 確認内容: 未accepted feedbackでも明示output指定時には確認用Issue bodyを生成できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:202`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 標準flowを壊さず、明示outputにreview用bodyが生成される。

#### RT-UT-CASE-SELF-010

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_evidence_scaffold_registers_artifact_index
```

- 確認内容: evidence scaffold生成時にartifact indexへ登録されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:233`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `data`, `manifest_data`
- 期待結果: evidence directoryとartifact index entryが生成される。

#### RT-UT-CASE-SELF-011

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_evidence_scaffold_updates_existing_artifact_index_without_rewriting_readmes
```

- 確認内容: 既存artifact index更新時にREADMEを不用意に書き換えないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:245`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `artifact_index`
- 期待結果: artifact indexは更新され、既存READMEは保持される。

#### RT-UT-CASE-SELF-012

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_main_prints_json
```

- 確認内容: self-improvement CLI mainがJSON出力を返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:262`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: mainがJSONをstdoutへ出力し、期待するexit codeを返す。

#### RT-UT-CASE-SELF-013

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_workflow_skills_declare_feedback_output_contract
```

- 確認内容: workflow skill群がfeedback output contractを宣言していることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:274`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `missing`, `text`, `required`
- 期待結果: 対象skillにfeedback出力契約が含まれる。

#### RT-UT-CASE-SELF-014

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_workflow_help_declares_feedback_capture_for_all_commands
```

- 確認内容: workflow helpが各commandのfeedback captureを宣言していることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:303`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `missing`
- 期待結果: help registry上の対象commandにfeedback capture説明が含まれる。
