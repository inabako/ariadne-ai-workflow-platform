# test_coverage_audit.py

このファイルは `runtime/tests/test_coverage_audit.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 6 |

## ケース一覧

#### RT-UT-CASE-067

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_static_runtime_audit_counts_cli_and_branch_markers
```

- 確認内容: pytest case `static runtime audit counts cli and branch markers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:10`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-068

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_run_skip_run_writes_json_and_markdown
```

- 確認内容: pytest case `run skip run writes json and markdown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:61`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `saved`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-069

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_run_coverage_measurement_removes_stale_json_before_commands
```

- 確認内容: pytest case `run coverage measurement removes stale json before commands` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:89`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `commands`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-070

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_coverage_audit_static_edges_and_blocked_measurement
```

- 確認内容: pytest case `coverage audit static edges and blocked measurement` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:127`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-071

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_coverage_audit_command_and_format_edges
```

- 確認内容: pytest case `coverage audit command and format edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:163`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-072

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_coverage_audit_render_main_and_script_load_paths
```

- 確認内容: pytest case `coverage audit render main and script load paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:180`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `audit`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
