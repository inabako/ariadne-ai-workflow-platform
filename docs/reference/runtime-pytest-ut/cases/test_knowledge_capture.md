# test_knowledge_capture.py

このファイルは `runtime/tests/test_knowledge_capture.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 7 |

## ケース一覧

#### RT-UT-CASE-200

- pytest node id:

```text
runtime/tests/test_knowledge_capture.py::test_parser_and_small_helpers
```

- 確認内容: pytest case `parser and small helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_knowledge_capture.py:58`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `parsed`, `files`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-201

- pytest node id:

```text
runtime/tests/test_knowledge_capture.py::test_path_file_docs_candidate_and_scaffold_helpers
```

- 確認内容: pytest case `path file docs candidate and scaffold helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_knowledge_capture.py:97`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-202

- pytest node id:

```text
runtime/tests/test_knowledge_capture.py::test_latest_issue_title_and_pr_text_helpers
```

- 確認内容: pytest case `latest issue title and pr text helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_knowledge_capture.py:130`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-203

- pytest node id:

```text
runtime/tests/test_knowledge_capture.py::test_context_fallback_modes_and_errors
```

- 確認内容: pytest case `context fallback modes and errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_knowledge_capture.py:160`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-204

- pytest node id:

```text
runtime/tests/test_knowledge_capture.py::test_knowledge_capture_generates_reports_json_and_context
```

- 確認内容: pytest case `knowledge capture generates reports json and context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_knowledge_capture.py:220`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `issue`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-205

- pytest node id:

```text
runtime/tests/test_knowledge_capture.py::test_knowledge_capture_dry_run_close_archive_fallback_and_missing_work
```

- 確認内容: pytest case `knowledge capture dry run close archive fallback and missing work` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_knowledge_capture.py:259`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `issue`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-206

- pytest node id:

```text
runtime/tests/test_knowledge_capture.py::test_main_outputs_json_and_reports_error
```

- 確認内容: pytest case `main outputs json and reports error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_knowledge_capture.py:283`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `issue`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
