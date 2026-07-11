# test_rag_retrieve_context.py

このファイルは `runtime/tests/test_rag_retrieve_context.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 17 |

## ケース一覧

#### RT-UT-CASE-354

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_read_jsonl_reports_line_number_for_invalid_json
```

- 確認内容: pytest case `read jsonl reports line number for invalid json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:45`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-355

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_read_jsonl_requires_existing_file_and_ignores_non_object_rows
```

- 確認内容: pytest case `read jsonl requires existing file and ignores non object rows` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:53`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-356

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_tokenize_sparse_embedding_and_cosine_cover_cjk_and_empty_values
```

- 確認内容: pytest case `tokenize sparse embedding and cosine cover cjk and empty values` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:64`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-357

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_filter_row_applies_all_optional_filters
```

- 確認内容: pytest case `filter row applies all optional filters` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:76`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `row`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-358

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_retrieve_filters_rows_and_selects_keyword_matches
```

- 確認内容: pytest case `retrieve filters rows and selects keyword matches` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:100`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `rows`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-359

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_retrieve_scores_semantic_hybrid_no_match_and_below_top_k
```

- 確認内容: pytest case `retrieve scores semantic hybrid no match and below top k` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:138`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `rows`, `embeddings`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-360

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_retrieve_context_edges_for_empty_terms_embeddings_and_tiny_budget
```

- 確認内容: pytest case `retrieve context edges for empty terms embeddings and tiny budget` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:158`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `row`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-361

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_retrieve_requires_positive_top_k
```

- 確認内容: pytest case `retrieve requires positive top k` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:199`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-362

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_split_units_and_compress_chunk_cover_matching_fallback_and_truncation
```

- 確認内容: pytest case `split units and compress chunk cover matching fallback and truncation` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:217`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `content`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-363

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_build_context_respects_budget_and_preserves_source_metadata
```

- 確認内容: pytest case `build context respects budget and preserves source metadata` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:236`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `selected`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-364

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_write_context_markdown_lists_sources
```

- 確認内容: pytest case `write context markdown lists sources` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:266`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-365

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_run_keyword_retrieval_writes_context_pack_and_markdown
```

- 確認内容: pytest case `run keyword retrieval writes context pack and markdown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:285`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `row`, `args`, `context_pack`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-366

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_run_hybrid_retrieval_uses_embeddings_and_absolute_output_dir
```

- 確認内容: pytest case `run hybrid retrieval uses embeddings and absolute output dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:336`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `row`, `retrieval`, `context_pack`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-367

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_run_can_retrieve_from_duckdb_backend
```

- 確認内容: pytest case `run can retrieve from duckdb backend` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:389`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `retrieval_result`, `context_pack`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
#### RT-UT-CASE-368

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_run_rejects_non_positive_max_chars
```

- 確認内容: pytest case `run rejects non positive max chars` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:446`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-369

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_semantic_search_requires_embeddings_index
```

- 確認内容: pytest case `semantic search requires embeddings index` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:451`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-370

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_main_prints_json
```

- 確認内容: pytest case `main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:479`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
