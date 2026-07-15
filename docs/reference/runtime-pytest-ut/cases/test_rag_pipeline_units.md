# test_rag_pipeline_units.py

このファイルは `runtime/tests/test_rag_pipeline_units.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 23 |

## ケース一覧

#### RT-UT-CASE-331

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_normalize_document_preserves_front_matter_and_headings
```

- 確認内容: pytest case `normalize document preserves front matter and headings` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:20`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-332

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_normalize_documents_parser_and_scalar_helpers
```

- 確認内容: pytest case `normalize documents parser and scalar helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:58`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-333

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_normalize_documents_front_matter_helper_edges
```

- 確認内容: pytest case `normalize documents front matter helper edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:98`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-334

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_normalize_document_includes_external_web_metadata_and_defaults
```

- 確認内容: pytest case `normalize document includes external web metadata and defaults` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:127`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-335

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_normalize_documents_run_cleans_json_output_and_accepts_absolute_paths
```

- 確認内容: pytest case `normalize documents run cleans json output and accepts absolute paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:184`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-336

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_normalize_documents_missing_source_and_main_paths
```

- 確認内容: pytest case `normalize documents missing source and main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:237`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-337

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_normalize_documents_module_can_be_loaded_as_script_path
```

- 確認内容: pytest case `normalize documents module can be loaded as script path` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:267`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-338

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_discover_sources_ignores_readme
```

- 確認内容: pytest case `discover sources ignores readme` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:273`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-339

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_split_content_validates_chunk_settings
```

- 確認内容: pytest case `split content validates chunk settings` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:283`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-340

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_documents_parser_and_heading_path_edges
```

- 確認内容: pytest case `chunk documents parser and heading path edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:291`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-341

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_split_content_short_empty_and_overlap_edges
```

- 確認内容: pytest case `split content short empty and overlap edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:323`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-342

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_split_content_defensive_fallback_preserves_text_when_splitter_yields_no_parts
```

- 確認内容: pytest case `split content defensive fallback preserves text when splitter yields no parts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:340`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-343

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_document_writes_chunk_with_heading_path
```

- 確認内容: pytest case `chunk document writes chunk with heading path` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:355`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-344

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_document_rejects_non_object_json
```

- 確認内容: pytest case `chunk document rejects non object json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:384`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-345

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_discover_documents_errors_and_sorts_recursively
```

- 確認内容: pytest case `discover documents errors and sorts recursively` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:399`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-346

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_documents_run_cleans_output_and_supports_absolute_dirs
```

- 確認内容: pytest case `chunk documents run cleans output and supports absolute dirs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:417`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-347

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_documents_main_paths
```

- 確認内容: pytest case `chunk documents main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:473`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-348

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_build_index_writes_document_and_chunk_jsonl
```

- 確認内容: pytest case `build index writes document and chunk jsonl` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:494`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `documents`, `chunks`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-349

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_build_index_parser_invalid_rows_empty_discovery_main_and_script
```

- 確認内容: pytest case `build index parser invalid rows empty discovery main and script` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:544`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-350

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_embed_chunks_is_deterministic_and_validates_dimensions
```

- 確認内容: pytest case `embed chunks is deterministic and validates dimensions` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:602`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `row`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-351

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_embed_chunks_parser_jsonl_edges_and_empty_embedding
```

- 確認内容: pytest case `embed chunks parser jsonl edges and empty embedding` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:623`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-352

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_embed_chunks_run_writes_jsonl
```

- 確認内容: pytest case `embed chunks run writes jsonl` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:661`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-353

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_embed_chunks_main_success_error_and_script_load
```

- 確認内容: pytest case `embed chunks main success error and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:684`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
