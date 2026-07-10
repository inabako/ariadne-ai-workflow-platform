# test_docs_sync_workflow.py

このファイルは `runtime/tests/test_docs_sync_workflow.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 11 |

## ケース一覧

#### RT-UT-CASE-118

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_docs_sync_build_parser_and_name_helpers
```

- 確認内容: pytest case `docs sync build parser and name helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:60`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-119

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_register_docs_sync_contexts_registers_only_existing_contexts
```

- 確認内容: pytest case `register docs sync contexts registers only existing contexts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:71`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-120

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_init_work_creates_contexts_and_rejects_unapproved_reuse
```

- 確認内容: pytest case `init work creates contexts and rejects unapproved reuse` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:88`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `agent_context`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-121

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_default_analysis_uses_scm_state_and_fallback_docs_root
```

- 確認内容: pytest case `default analysis uses scm state and fallback docs root` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:124`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-122

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_require_docs_sync_scm_state_covers_manifest_fallback_allowed_and_error
```

- 確認内容: pytest case `require docs sync scm state covers manifest fallback allowed and error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:145`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-123

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_create_analysis_template_with_allow_missing_and_explicit_output
```

- 確認内容: pytest case `create analysis template with allow missing and explicit output` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:178`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-124

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_create_analysis_template_reports_missing_work_dir
```

- 確認内容: pytest case `create analysis template reports missing work dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:198`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-125

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_markdown_helpers_and_issue_body_render_full_and_empty_sections
```

- 確認内容: pytest case `markdown helpers and issue body render full and empty sections` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:211`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-126

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_create_issue_body_writes_markdown_and_registers_artifact
```

- 確認内容: pytest case `create issue body writes markdown and registers artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:229`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-127

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_create_issue_body_reports_missing_work_and_analysis
```

- 確認内容: pytest case `create issue body reports missing work and analysis` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:254`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-128

- pytest node id:

```text
runtime/tests/test_docs_sync_workflow.py::test_run_dispatches_and_main_prints_json
```

- 確認内容: pytest case `run dispatches and main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_docs_sync_workflow.py:267`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
