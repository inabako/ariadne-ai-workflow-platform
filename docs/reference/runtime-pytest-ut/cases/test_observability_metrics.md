# test_observability_metrics.py

このファイルは `runtime/tests/test_observability_metrics.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 17 |

## ケース一覧

#### RT-UT-CASE-208

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_monthly_log_path_uses_year_month_suffix
```

- 確認内容: pytest case `monthly log path uses year month suffix` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:17`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-209

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_resolve_log_path_rotates_base_runtime_metrics_file
```

- 確認内容: pytest case `resolve log path rotates base runtime metrics file` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:25`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-210

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_resolve_log_path_can_disable_rotation_for_base_or_directory
```

- 確認内容: pytest case `resolve log path can disable rotation for base or directory` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:33`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-211

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_append_jsonl_appends_one_record_per_line
```

- 確認内容: pytest case `append jsonl appends one record per line` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:40`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-212

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_append_jsonl_returns_warning_without_raising_when_parent_is_file
```

- 確認内容: pytest case `append jsonl returns warning without raising when parent is file` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:51`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-213

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_schema_helpers_sanitize_negative_and_invalid_values
```

- 確認内容: pytest case `schema helpers sanitize negative and invalid values` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:61`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-214

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_runtime_metric_record_falls_back_to_runtime_error_for_unknown_event
```

- 確認内容: pytest case `runtime metric record falls back to runtime error for unknown event` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:72`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-215

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_duration_timer_records_elapsed_duration
```

- 確認内容: pytest case `duration timer records elapsed duration` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:80`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-216

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_defaults_log_dir_under_runtime_logs
```

- 確認内容: pytest case `collector defaults log dir under runtime logs` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:87`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-217

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_records_non_fatal_log_write_warning
```

- 確認内容: pytest case `collector records non fatal log write warning` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:93`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-218

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_records_workflow_agent_token_context_and_monthly_jsonl
```

- 確認内容: pytest case `collector records workflow agent token context and monthly jsonl` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:104`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-219

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_records_human_check_evidence_and_runtime_error
```

- 確認内容: pytest case `collector records human check evidence and runtime error` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:140`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-220

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_failed_workflow_saves_human_check_required_evidence
```

- 確認内容: pytest case `collector failed workflow saves human check required evidence` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:155`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `payload`
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-221

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_saves_workflow_evidence_and_registers_context
```

- 確認内容: pytest case `collector saves workflow evidence and registers context` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:168`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `manifest`
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-222

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_evidence_summary_can_skip_work_dir_or_manifest_registration
```

- 確認内容: pytest case `collector evidence summary can skip work dir or manifest registration` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:192`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-223

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_evidence_summary_returns_warning_without_raising
```

- 確認内容: pytest case `collector evidence summary returns warning without raising` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:206`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-224

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_register_runtime_metrics_context_uses_runtime_metrics_type
```

- 確認内容: pytest case `register runtime metrics context uses runtime metrics type` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:218`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.
