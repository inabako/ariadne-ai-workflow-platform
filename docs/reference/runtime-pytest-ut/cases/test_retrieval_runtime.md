# test_retrieval_runtime.py

このファイルは `runtime/tests/test_retrieval_runtime.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 23 |

## ケース一覧

#### RT-UT-CASE-407

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_duplicate_task_ids
```

- 確認内容: pytest case `task plan rejects duplicate task ids` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:24`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-408

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload0-Task plan must be a JSON object]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload0-Task plan must be a JSON object]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload0-Task plan must be a JSON object`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-409

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload1-non-empty tasks array]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload1-non-empty tasks array]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload1-non-empty tasks array`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-410

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload2-non-empty tasks array]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload2-non-empty tasks array]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload2-non-empty tasks array`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-411

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload3-Each task must be a JSON object]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload3-Each task must be a JSON object]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload3-Each task must be a JSON object`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-412

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload4-non-empty id]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload4-non-empty id]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload4-non-empty id`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-413

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload5-non-empty id]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload5-non-empty id]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload5-non-empty id`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-414

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload6-depends_on must be a string array]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload6-depends_on must be a string array]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload6-depends_on must be a string array`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-415

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload7-depends_on must be a string array]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload7-depends_on must be a string array]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload7-depends_on must be a string array`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-416

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_unknown_dependencies
```

- 確認内容: pytest case `task plan rejects unknown dependencies` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:56`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-417

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_accepts_valid_dependencies_and_parser_options
```

- 確認内容: pytest case `task plan accepts valid dependencies and parser options` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:67`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-418

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_runner_dry_run_writes_reports_and_artifact_index
```

- 確認内容: pytest case `task runner dry run writes reports and artifact index` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:106`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-419

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_defaults_auto_to_parallel_and_uses_agent_context
```

- 確認内容: pytest case `run defaults auto to parallel and uses agent context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:144`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-420

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_rejects_missing_work_dir_and_unsupported_mode
```

- 確認内容: pytest case `run rejects missing work dir and unsupported mode` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:198`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-421

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_one_task_records_failure_logs
```

- 確認内容: pytest case `run one task records failure logs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:235`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `task`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-422

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_one_task_skips_missing_command_and_rejects_missing_cwd
```

- 確認内容: pytest case `run one task skips missing command and rejects missing cwd` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:247`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-423

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_one_task_records_success_and_returncode_failure
```

- 確認内容: pytest case `run one task records success and returncode failure` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:271`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-424

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_sequential_stop_on_failure_blocks_remaining
```

- 確認内容: pytest case `sequential stop on failure blocks remaining` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:322`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-425

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_sequential_blocks_failed_dependency_and_detects_cycle
```

- 確認内容: pytest case `sequential blocks failed dependency and detects cycle` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:349`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-426

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_parallel_blocks_failed_dependency_and_stop_on_failure_pending
```

- 確認内容: pytest case `parallel blocks failed dependency and stop on failure pending` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:390`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-427

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_result_to_dict_and_write_reports_include_optional_fields
```

- 確認内容: pytest case `result to dict and write reports include optional fields` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:444`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `markdown`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-428

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_main_prints_json_and_reports_errors
```

- 確認内容: pytest case `main prints json and reports errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:474`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-429

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_normalize_command_accepts_string_and_array
```

- 確認内容: pytest case `normalize command accepts string and array` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:504`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
