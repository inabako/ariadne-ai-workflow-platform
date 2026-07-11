# test_rag_build.py

このファイルは `runtime/tests/test_rag_build.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 8 |

## ケース一覧

#### RT-UT-CASE-291

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_small_helpers
```

- 確認内容: pytest case `rag build small helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:51`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-292

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_artifact_defaults_and_human_check_reasons
```

- 確認内容: pytest case `rag build artifact defaults and human check reasons` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:77`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `stages`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-293

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_register_rag_build_context_uses_work_dir_name
```

- 確認内容: pytest case `register rag build context uses work dir name` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:156`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-294

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_run_with_standardize_and_context_registration
```

- 確認内容: pytest case `rag build run with standardize and context registration` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:182`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `stage_calls`, `artifact`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-295

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_run_skip_standardize_and_explicit_work_dir
```

- 確認内容: pytest case `rag build run skip standardize and explicit work dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:266`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `stage_names`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-296

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_run_can_skip_ingestion_optimization
```

- 確認内容: pytest case `rag build run can skip ingestion optimization` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:317`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `stage_names`, `artifact`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-297

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_run_can_register_duckdb_migration_context
```

- 確認内容: pytest case `rag build run can register duckdb migration context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:363`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `stage_names`, `migration_calls`, `evidence`, `artifact`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
#### RT-UT-CASE-298

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_parser_and_main_paths
```

- 確認内容: pytest case `rag build parser and main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:446`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
