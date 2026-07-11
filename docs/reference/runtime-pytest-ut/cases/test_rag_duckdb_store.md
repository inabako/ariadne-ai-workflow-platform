# test_rag_duckdb_store.py

このファイルは `runtime/tests/test_rag_duckdb_store.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 15 |

## ケース一覧

#### RT-UT-CASE-309

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_init_creates_generated_schema
```

- 確認内容: pytest case `duckdb store init creates generated schema` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:47`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-310

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_ingests_skips_duplicate_and_updates_same_id
```

- 確認内容: pytest case `duckdb store ingests skips duplicate and updates same id` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:60`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-311

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_skips_same_content_with_different_id
```

- 確認内容: pytest case `duckdb store skips same content with different id` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:103`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `content`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-312

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_migrate_continues_after_invalid_records
```

- 確認内容: pytest case `duckdb store migrate continues after invalid records` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:120`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `errors`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-313

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_cli_and_fallback_paths
```

- 確認内容: pytest case `duckdb store cli and fallback paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:147`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-314

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_requires_content_and_source_directory
```

- 確認内容: pytest case `duckdb store requires content and source directory` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:184`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-315

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_helper_fallbacks_and_generated_ids
```

- 確認内容: pytest case `duckdb store helper fallbacks and generated ids` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:196`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `payload`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-316

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_run_migrate_and_empty_error_log
```

- 確認内容: pytest case `duckdb store run migrate and empty error log` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:223`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-317

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_defensive_error_paths
```

- 確認内容: pytest case `duckdb store defensive error paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:247`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `unsupported`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
#### RT-UT-CASE-318

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_search_ranks_keyword_and_metadata_filters
```

- 確認内容: pytest case `duckdb store search ranks keyword and metadata filters` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:275`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-319

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_search_returns_zero_results_without_error
```

- 確認内容: pytest case `duckdb store search returns zero results without error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:332`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-320

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_export_context_writes_agent_json
```

- 確認内容: pytest case `duckdb store export context writes agent json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:366`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `data`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-321

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_cli_search_and_export_context
```

- 確認内容: pytest case `duckdb store cli search and export context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:409`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-322

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_rebuild_standard_sources_records_history
```

- 確認内容: pytest case `duckdb store rebuild standard sources records history` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:462`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `source_metadata`
- 期待結果: 標準RAGソースからDuckDB read modelを再構築し、schema versionとmigration履歴が保存される。

#### RT-UT-CASE-323

- pytest node id:

```text
runtime/tests/test_rag_duckdb_store.py::test_duckdb_store_verify_references_writes_evidence
```

- 確認内容: pytest case `duckdb store verify references writes evidence` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_duckdb_store.py:522`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `evidence`, `manifest`
- 期待結果: 参照確認evidenceをJSONで保存し、検索0件のqueryがある場合は `human-check-required` として検出される。
