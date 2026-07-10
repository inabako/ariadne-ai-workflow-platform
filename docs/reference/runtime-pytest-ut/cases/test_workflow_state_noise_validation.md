# test_workflow_state_noise_validation.py

このファイルは `runtime/tests/test_workflow_state_noise_validation.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 21 |

## ケース一覧

#### RT-UT-CASE-525

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_workflow_state_update_writes_state_and_history
```

- 確認内容: pytest case `workflow state update writes state and history` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:13`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-526

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_defensive_specimen_workflow_state_does_not_record_blank_previous_state
```

- 確認内容: defensive specimen workflow state does not record blank previous state を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:39`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-527

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_workflow_state_rejects_invalid_status
```

- 確認内容: pytest case `workflow state rejects invalid status` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:56`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-528

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_workflow_state_run_show_reports_missing_state
```

- 確認内容: pytest case `workflow state run show reports missing state` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:67`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-529

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_workflow_state_run_set_updates_relative_work_dir
```

- 確認内容: pytest case `workflow state run set updates relative work dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:81`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-530

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_workflow_state_main_show_prints_json
```

- 確認内容: pytest case `workflow state main show prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:103`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-531

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_blocks_when_critical_items_are_missing
```

- 確認内容: pytest case `noise reduction blocks when critical items are missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:124`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-532

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_can_reach_warning_when_only_unknown_terms_remain
```

- 確認内容: pytest case `noise reduction can reach warning when only unknown terms remain` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:143`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-533

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_passes_and_uses_default_output_dir
```

- 確認内容: pytest case `noise reduction passes and uses default output dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:165`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `readiness`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-534

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_helpers_cover_duplicate_unknown_and_missing_draft
```

- 確認内容: pytest case `noise reduction helpers cover duplicate unknown and missing draft` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:192`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-535

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_parser_main_and_script_load_paths
```

- 確認内容: pytest case `noise reduction parser main and script load paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:201`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-536

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_detects_english_dominant_markdown
```

- 確認内容: pytest case `validate output language detects english dominant markdown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:237`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-537

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_ignores_code_blocks_and_allowed_terms
```

- 確認内容: pytest case `validate output language ignores code blocks and allowed terms` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:253`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-538

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_iter_markdown_skips_missing_non_md_and_excluded_paths
```

- 確認内容: pytest case `validate output language iter markdown skips missing non md and excluded paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:278`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-539

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_strip_non_prose_removes_frontmatter_urls_tables_and_inline_code
```

- 確認内容: pytest case `validate output language strip non prose removes frontmatter urls tables and inline code` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:307`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-540

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_main_returns_zero_when_only_warnings
```

- 確認内容: pytest case `validate output language main returns zero when only warnings` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:332`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-541

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_main_fails_on_violation
```

- 確認内容: pytest case `validate output language main fails on violation` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:362`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-542

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_main_prints_absolute_external_path_and_script_load
```

- 確認内容: pytest case `validate output language main prints absolute external path and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:392`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-543

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_main_reports_ok_for_japanese_dominant
```

- 確認内容: pytest case `validate output language main reports ok for japanese dominant` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:425`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-544

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_vscode_workspace_accepts_utf8_sig_json
```

- 確認内容: pytest case `validate vscode workspace accepts utf8 sig json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:441`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-545

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_vscode_workspace_rejects_invalid_json
```

- 確認内容: pytest case `validate vscode workspace rejects invalid json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:450`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
