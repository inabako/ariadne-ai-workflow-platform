# test_coverage_audit.py

このファイルは `runtime/tests/test_coverage_audit.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 11 |

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

#### RT-UT-CASE-072-A

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_text_encoding_guard_does_not_flag_saved_mojibake_without_dataset
```

- 確認内容: text encoding guard が直指定markerを使わず、UTF-8として保存済みの文字化け候補を固定パターンだけで断定しないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:234`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `original`
- 期待結果: `scan` は `ok` を返し、固定marker由来のfindingを作らない。

#### RT-UT-CASE-072-B

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_text_encoding_convert_inspects_and_converts_cp932_to_utf8
```

- 確認内容: text encoding convert が CP932 / Shift_JIS / UTF-8 の候補をstrict decodeで検査し、CP932文書をUTF-8へ安全に変換することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:252`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `original`, `args`
- 期待結果: `inspect` が CP932 をpreferred encodingにし、`convert --write` が `.encoding-bak` を残してUTF-8本文へ変換する。

#### RT-UT-CASE-072-C

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_text_encoding_convert_preview_shows_hex_and_decode_candidates
```

- 確認内容: text encoding convert の preview がhex bytes、encoding別decode preview、UTF-8保存済み文字化け候補と非UTF-8候補の分類を出力することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:275`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `original`
- 期待結果: UTF-8保存済み文字化け候補は `utf8-compatible-with-other-decoders`、CP932文書は `non-utf8-candidate` と分類され、CLIも `text-encoding-preview` を出力する。

#### RT-UT-CASE-072-D

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_text_encoding_convert_blocks_unsafe_cp932_conversion_for_utf8_file
```

- 確認内容: text encoding convert が既にUTF-8として読める文書をCP932扱いで変換しようとした場合に、安全側でブロックすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:324`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `original`, `args`
- 期待結果: 変換は blocked となり、backupは作成されず、対象ファイルのUTF-8本文は維持される。

#### RT-UT-CASE-072-E

- pytest node id:

```text
runtime/tests/test_coverage_audit.py::test_text_encoding_guard_reports_lossy_damage_without_writing
```

- 確認内容: text encoding guard が連続した疑問符のような不可逆な欠落を検出し、自動修復せず blocked として報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_coverage_audit.py:343`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: lossy-marker finding が記録され、対象ファイルは書き換えられない。
