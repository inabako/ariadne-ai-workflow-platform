# test_corrective_action_report.py

このファイルは `runtime/tests/test_corrective_action_report.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 6 |

## ケース一覧

#### RT-UT-CASE-061

- pytest node id:

```text
runtime/tests/test_corrective_action_report.py::test_corrective_action_report_parse_helpers
```

- 確認内容: pytest case `corrective action report parse helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_corrective_action_report.py:33`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-062

- pytest node id:

```text
runtime/tests/test_corrective_action_report.py::test_corrective_action_report_count_section_items
```

- 確認内容: pytest case `corrective action report count section items` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_corrective_action_report.py:62`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-063

- pytest node id:

```text
runtime/tests/test_corrective_action_report.py::test_corrective_action_report_build_context_existing_and_missing_report
```

- 確認内容: pytest case `corrective action report build context existing and missing report` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_corrective_action_report.py:87`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-064

- pytest node id:

```text
runtime/tests/test_corrective_action_report.py::test_corrective_action_report_register_with_explicit_work_dir_and_show
```

- 確認内容: pytest case `corrective action report register with explicit work dir and show` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_corrective_action_report.py:140`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `context`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-064A

- pytest node id:

```text
runtime/tests/test_corrective_action_report.py::test_corrective_action_report_registers_approved_work_db_report_for_cleanup
```

- 確認内容: 承認済みCorrective Action Report sourceが `work/db/...` 配下でlong-lived Knowledge cleanup evidenceとして登録されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_corrective_action_report.py:191`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果:
  - `work_cleanup.ready_for_check` is true
  - `next_action.action == "check-work-cleanup"`
  - 汎用 `work cleanup-check` が `status == "ready"` を返す

#### RT-UT-CASE-065

- pytest node id:

```text
runtime/tests/test_corrective_action_report.py::test_corrective_action_report_register_missing_report_and_show_missing
```

- 確認内容: pytest case `corrective action report register missing report and show missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_corrective_action_report.py:212`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `context`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-066

- pytest node id:

```text
runtime/tests/test_corrective_action_report.py::test_corrective_action_report_parser_and_main_paths
```

- 確認内容: pytest case `corrective action report parser and main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_corrective_action_report.py:242`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `register_args`, `show_args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
