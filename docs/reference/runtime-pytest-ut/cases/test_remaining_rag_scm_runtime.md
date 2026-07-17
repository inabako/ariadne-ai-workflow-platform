# test_remaining_rag_scm_runtime.py

このファイルは `runtime/tests/test_remaining_rag_scm_runtime.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 10 |

## ケース一覧

#### RT-UT-CASE-397

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_jsonize_rag_tree_should_convert_skips_uuid_json_and_readme_by_default
```

- 確認内容: pytest case `jsonize rag tree should convert skips uuid json and readme by default` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:24`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-398

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_jsonize_rag_tree_reads_jsonl_with_parse_errors
```

- 確認内容: pytest case `jsonize rag tree reads jsonl with parse errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:44`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-399

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_jsonize_rag_tree_run_converts_supported_sources_and_excludes_output_dir
```

- 確認内容: pytest case `jsonize rag tree run converts supported sources and excludes output dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:56`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-400

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_jsonize_rag_tree_delete_source_removes_converted_files
```

- 確認内容: pytest case `jsonize rag tree delete source removes converted files` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:86`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-401

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_jsonize_rag_tree_parser_payload_clean_missing_main_and_script_paths
```

- 確認内容: pytest case `jsonize rag tree parser payload clean missing main and script paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:107`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`, `source_format`, `payload`, `text`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-402

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_compare_requirements_safe_git_returns_error_text
```

- 確認内容: pytest case `compare requirements safe git returns error text` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:187`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-403

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_compare_requirements_parser_main_script_and_no_requirements
```

- 確認内容: pytest case `compare requirements parser main script and no requirements` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:204`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`, `markdown`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-404

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_compare_requirements_first_lines_limits_and_reports_read_errors
```

- 確認内容: pytest case `compare requirements first lines limits and reports read errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:265`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-405

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_compare_requirements_writes_reports_and_artifact_index
```

- 確認内容: pytest case `compare requirements writes reports and artifact index` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:273`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `json_report`, `markdown`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-406

- pytest node id:

```text
runtime/tests/test_remaining_rag_scm_runtime.py::test_compare_requirements_requires_work_and_source_dirs
```

- 確認内容: pytest case `compare requirements requires work and source dirs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_rag_scm_runtime.py:328`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
