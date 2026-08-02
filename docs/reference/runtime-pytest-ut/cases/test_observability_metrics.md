# test_observability_metrics.py

このファイルは `runtime/tests/test_observability_metrics.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 22 |

## ケース一覧

#### RT-UT-CASE-208

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_monthly_log_path_uses_year_month_suffix
```

- 確認内容: pytest case `monthly log path uses year month suffix` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:23`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-209

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_resolve_log_path_rotates_base_runtime_metrics_file
```

- 確認内容: pytest case `resolve log path rotates base runtime metrics file` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:31`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-210

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_resolve_log_path_can_disable_rotation_for_base_or_directory
```

- 確認内容: pytest case `resolve log path can disable rotation for base or directory` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:39`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-211

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_append_jsonl_appends_one_record_per_line
```

- 確認内容: pytest case `append jsonl appends one record per line` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:46`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-212

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_append_jsonl_returns_warning_without_raising_when_parent_is_file
```

- 確認内容: pytest case `append jsonl returns warning without raising when parent is file` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:57`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-212TRACE

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_generate_trace_id_returns_24_hex_characters
```

- 確認内容: Runtime Event Log の自動生成 trace id が衝突しにくい24桁hexで生成されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:67`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `logger.generate_trace_id()`
- 期待結果: 生成された trace id は24文字で、hex文字列として解釈できる。

#### RT-UT-CASE-212A

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_runtime_event_logger_writes_pipe_prefixed_json_line
```

- 確認内容: runtime event logger が `timestamp | trace-id | sequence | json` の1行形式でイベントを保存し、sensitive key を mask することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:67`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `payload`
- 期待結果: `logs/runtime/runtime-events.log` に同一traceの連番イベントが保存され、JSON payload の機密値が `***` へmaskされる。

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_active_runtime_trace_state_is_used_by_default
```

- 確認内容: active runtime trace state が存在する場合、`RuntimeEventLogger` が既定で同じ trace id を使うことを確認します。
- 入力値:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_observability_metrics.py:108`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成されるfixtureとassertion
- 期待結果: `active-trace.json` の trace id が `runtime-events.log` に使われ、trace end 後は active trace id が空になる。

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_active_runtime_trace_begin_blocks_existing_trace_without_force
```

- 確認内容: active trace が残っている状態で別 workflow trace を誤って開始しないよう、`--force` なしの begin が blocked になることを確認します。
- 入力値:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_observability_metrics.py:123`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成されるfixtureとassertion
- 期待結果: 既存 active trace がある場合は blocked になり、`--force` 指定時だけ新しい workflow trace state へ置き換わる。

#### RT-UT-CASE-212B

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_runtime_event_logger_rotates_when_max_bytes_is_exceeded
```

- 確認内容: runtime event logger が最大サイズ超過時に log file を rotation し、新しいイベントを現行ファイルへ保存することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:94`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: size limit を超えたとき `runtime-events.log.1` が作成され、現行 `runtime-events.log` には最新イベントが残る。

#### RT-UT-CASE-213

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_schema_helpers_sanitize_negative_and_invalid_values
```

- 確認内容: pytest case `schema helpers sanitize negative and invalid values` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:114`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-214

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_runtime_metric_record_falls_back_to_runtime_error_for_unknown_event
```

- 確認内容: pytest case `runtime metric record falls back to runtime error for unknown event` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:125`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-215

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_duration_timer_records_elapsed_duration
```

- 確認内容: pytest case `duration timer records elapsed duration` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:133`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-216

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_defaults_log_dir_under_repo_logs
```

- 確認内容: pytest case `collector defaults log dir under repo logs` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:140`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-217

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_records_non_fatal_log_write_warning
```

- 確認内容: pytest case `collector records non fatal log write warning` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:146`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-218

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_records_workflow_agent_token_context_and_monthly_jsonl
```

- 確認内容: pytest case `collector records workflow agent token context and monthly jsonl` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:157`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-219

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_records_human_check_evidence_and_runtime_error
```

- 確認内容: pytest case `collector records human check evidence and runtime error` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:193`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-220

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_failed_workflow_saves_human_check_required_evidence
```

- 確認内容: pytest case `collector failed workflow saves human check required evidence` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:208`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `payload`
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-221

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_saves_workflow_evidence_and_registers_context
```

- 確認内容: pytest case `collector saves workflow evidence and registers context` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:221`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `manifest`
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-222

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_evidence_summary_can_skip_work_dir_or_manifest_registration
```

- 確認内容: pytest case `collector evidence summary can skip work dir or manifest registration` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:245`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-223

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_evidence_summary_returns_warning_without_raising
```

- 確認内容: pytest case `collector evidence summary returns warning without raising` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:259`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-224

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_register_runtime_metrics_context_uses_runtime_metrics_type
```

- 確認内容: pytest case `register runtime metrics context uses runtime metrics type` に対応し、Runtime Observabilityの月次ローテーション、JSONL追記、evidence出力、Context First登録、token/context/cost処理、非致命write warningを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:271`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.
