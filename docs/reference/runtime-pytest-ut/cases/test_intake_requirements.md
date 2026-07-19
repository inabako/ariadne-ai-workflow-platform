# test_intake_requirements.py

このファイルは `runtime/tests/test_intake_requirements.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 8 |

## ケース一覧

#### RT-UT-CASE-193

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_parser_and_workflow_mapping_helpers
```

- 確認内容: pytest case `parser and workflow mapping helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:41`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-194

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_discover_requirement_documents_rejects_invalid_inputs
```

- 確認内容: pytest case `discover requirement documents rejects invalid inputs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:99`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-195

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_repository_control_and_unique_destination
```

- 確認内容: pytest case `repository control and unique destination` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:129`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-196

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_initialize_context_and_manifest_registration
```

- 確認内容: pytest case `initialize context and manifest registration` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:152`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `agent_context`, `handoff`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-197

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_run_with_explicit_requirements_copies_and_uses_unique_names
```

- 確認内容: pytest case `run with explicit requirements copies and uses unique names` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:183`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `agent_context`, `artifact_index`, `handoff`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-198

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_run_discovers_single_requirement_moves_and_generates_receipt
```

- 確認内容: pytest case `run discovers single requirement moves and generates receipt` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:225`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-199

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_run_rejects_missing_explicit_requirement
```

- 確認内容: pytest case `run rejects missing explicit requirement` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:255`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-200

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_main_outputs_json_and_reports_error
```

- 確認内容: pytest case `main outputs json and reports error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:266`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
