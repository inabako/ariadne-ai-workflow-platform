# test_self_improvement_workflow.py

このファイルは `runtime/tests/test_self_improvement_workflow.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 8 |

## ケース一覧

#### RT-UT-CASE-466

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_parser_and_branch_name
```

- 確認内容: pytest case `parser and branch name` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:13`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-467

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_init_and_create_feedback
```

- 確認内容: pytest case `init and create feedback` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:24`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-468

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_review_feedback_updates_status_and_human_check
```

- 確認内容: pytest case `review feedback updates status and human check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:51`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-469

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_issue_body_requires_accepted_feedback_and_renders_fit_check
```

- 確認内容: pytest case `issue body requires accepted feedback and renders fit check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:77`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-470

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_evidence_scaffold_registers_artifact_index
```

- 確認内容: pytest case `evidence scaffold registers artifact index` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:148`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `data`, `manifest_data`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-471

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_main_prints_json
```

- 確認内容: pytest case `main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:160`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-472

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_workflow_skills_declare_feedback_output_contract
```

- 確認内容: pytest case `workflow skills declare feedback output contract` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:172`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `missing`, `text`, `required`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-473

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_workflow_help_declares_feedback_capture_for_all_commands
```

- 確認内容: pytest case `workflow help declares feedback capture for all commands` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:201`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `registry`, `missing`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
