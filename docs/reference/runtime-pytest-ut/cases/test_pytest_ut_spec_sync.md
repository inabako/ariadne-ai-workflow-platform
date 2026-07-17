# test_pytest_ut_spec_sync.py

このファイルは `runtime/tests/test_pytest_ut_spec_sync.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 20 |

## ケース一覧

#### RT-UT-CASE-252

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_normalize_collected_node_and_parse_spec_cases
```

- 確認内容: pytest case `normalize collected node and parse spec cases` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:14`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-253

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_collect_pytest_nodes_filters_noise_and_reports_collect_error
```

- 確認内容: pytest case `defensive specimen collect pynodes filters noise and reports collect error` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:41`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-254

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_script_path_load_exposes_helpers
```

- 確認内容: pytest case `defensive specimen script path load exposes helpers` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:73`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-255

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_parse_spec_closing_fence_without_node
```

- 確認内容: pytest case `defensive specimen parse spec closing fence without node` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:80`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-256

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_ast_decorator_shapes_are_ignored_or_reduced
```

- 確認内容: pytest case `defensive specimen ast decorator shapes are ignored or reduced` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:94`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-257

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_ast_input_helpers_preserve_only_explainable_inputs
```

- 確認内容: pytest case `defensive specimen ast input helpers preserve only explainable inputs` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:127`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-258

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_function_info_and_input_lines_for_no_inline_inputs
```

- 確認内容: pytest case `defensive specimen function info and input lines for no inline inputs` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:156`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-259

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_input_lines_include_source_fixture_parameter_and_inline_values
```

- 確認内容: pytest case `input lines include source fixture parameter and inline values` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:177`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-260

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_replace_input_sections_preserves_confirmation_expected_order
```

- 確認内容: pytest case `replace input sections preserves confirmation expected order` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:207`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `spec`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-261

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_replace_input_sections_skips_legacy_multiline_input_until_next_field
```

- 確認内容: pytest case `defensive specimen replace input sections skips legacy multiline input until next field` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:241`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-262

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_replace_input_sections_keeps_confirm_without_node_id
```

- 確認内容: defensive specimen replace input sections keeps confirm without node id を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:275`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-263

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_check_spec_reports_missing_stale_order_and_bad_input
```

- 確認内容: pytest case `check spec reports missing stale order and bad input` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:292`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-264

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_check_spec_reads_split_case_files
```

- 確認内容: pytest case `check spec reads split case files` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:320`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-265

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_main_fix_inputs_and_check_json_output
```

- 確認内容: pytest case `main fix inputs and check json output` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:350`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `payload`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-266

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_main_fix_inputs_updates_split_case_files
```

- 確認内容: pytest case `main fix inputs updates split case files` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:390`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `payload`, `updated`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-267

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_default_paths_and_register_context_requires_work_dir
```

- 確認内容: pytest case `defensive specimen default paths and register context requires work dir` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:433`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-268

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_report_payload_and_context_first_registration
```

- 確認内容: pytest case `report payload and context first registration` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:451`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `check_result`, `payload`, `saved`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-269

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_main_uses_default_report_paths_when_registering_context
```

- 確認内容: pytest case `defensive specimen main uses default report paths when registering context` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:498`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-270

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_main_writes_report_without_context_registration
```

- 確認内容: pytest case `defensive specimen main writes report without context registration` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:554`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-271

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_main_check_writes_report_and_registers_context
```

- 確認内容: pytest case `main check writes report and registers context` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:585`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`, `manifest`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。
