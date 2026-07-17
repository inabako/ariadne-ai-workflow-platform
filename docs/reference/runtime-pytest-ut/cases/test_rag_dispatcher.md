# test_rag_dispatcher.py

このファイルは `runtime/tests/test_rag_dispatcher.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 10 |

## ケース一覧

#### RT-UT-CASE-299

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_planning_helpers_cover_context_and_explicit_paths
```

- 確認内容: pytest case `dispatcher planning helpers cover context and explicit paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:79`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `query_items_for_append`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-300

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_duckdb_backend_command_and_index_gate
```

- 確認内容: pytest case `dispatcher duckdb backend command and index gate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:170`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `query_item`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
#### RT-UT-CASE-301

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_execution_plan_and_plan_normalization_paths
```

- 確認内容: pytest case `dispatcher execution plan and plan normalization paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:216`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `manifest`, `plan`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-302

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_existing_plan_validation_and_execution_plan_override
```

- 確認内容: pytest case `dispatcher existing plan validation and execution plan override` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:289`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-303

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_command_index_build_and_aggregation_helpers
```

- 確認内容: pytest case `dispatcher command index build and aggregation helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:362`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `query_item`, `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-304

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_run_failure_paths_and_markdown_main
```

- 確認内容: pytest case `dispatcher run failure paths and markdown main` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:476`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `retrieval_calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-305

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_run_command_json_boundaries
```

- 確認内容: pytest case `dispatcher run command json boundaries` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:586`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-306

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_writes_query_plan_before_dispatch
```

- 確認内容: pytest case `dispatcher writes query plan before dispatch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:616`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `plan`, `dispatch`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-307

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_can_reuse_existing_query_plan
```

- 確認内容: pytest case `dispatcher can reuse existing query plan` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:676`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `plan`, `args`, `dispatch`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-308

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_warns_when_work_id_has_no_execution_plan
```

- 確認内容: pytest case `dispatcher warns when work id has no execution plan` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:734`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `plan`, `dispatch`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
