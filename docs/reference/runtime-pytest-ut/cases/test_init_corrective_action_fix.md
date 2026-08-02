# test_init_corrective_action_fix.py

このファイルは `runtime/tests/test_init_corrective_action_fix.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 9 |

## ケース一覧

#### RT-UT-CASE-184

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_small_helpers
```

- 確認内容: pytest case `init corrective action fix small helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:34`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-185

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_report_context_from_work_dir_edges
```

- 確認内容: pytest case `init corrective action fix report context from work dir edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:56`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-186

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_resolves_manifest_from_base_or_branch_work
```

- 確認内容: pytest case `init corrective action fix resolves manifest from base or branch work` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:108`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-187

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_write_report_context_skips_empty_and_registers
```

- 確認内容: pytest case `init corrective action fix write report context skips empty and registers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:150`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `context`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-188

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_defensive_specimen_init_corrective_action_fix_accepts_absolute_report_paths
```

- 確認内容: defensive specimen init corrective action fix accepts absolute report paths を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:188`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `context`
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-189

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_defensive_specimen_report_context_from_manifest_accepts_absolute_path
```

- 確認内容: defensive specimen report context from manifest accepts absolute path を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:217`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-190

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_run_with_argument_report_and_reuse_existing
```

- 確認内容: pytest case `init corrective action fix run with argument report and reuse existing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:246`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `agent`, `artifact_index`, `report_context`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-190A

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_uses_work_db_report_as_cleanup_evidence
```

- 確認内容: corrective-action-fix initialization uses an existing `work/db/...` corrective action report as long-lived Knowledge cleanup evidence.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:280`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果:
  - `work_cleanup.ready_for_check` is true
  - `next_action.action == "check-work-cleanup"`
  - 汎用 `work cleanup-check` が `status == "ready"` を返す

#### RT-UT-CASE-191

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_run_missing_report_has_no_report_artifact
```

- 確認内容: pytest case `init corrective action fix run missing report has no report artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:298`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-192

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_parser_and_main_paths
```

- 確認内容: pytest case `init corrective action fix parser and main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:311`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
