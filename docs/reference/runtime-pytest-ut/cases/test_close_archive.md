# test_close_archive.py

このファイルは `runtime/tests/test_close_archive.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 16 |

## ケース一覧

#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_parser_and_path_derivation_helpers
```

- 確認内容: pytest case `parser and path derivation helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:29`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `prepared`, `pruned`, `audited`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-002

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_resolve_paths_supports_issue_alias_explicit_dirs_and_repo_default
```

- 確認内容: pytest case `resolve paths supports issue alias explicit dirs and repo default` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:78`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-003

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_archive_path_safety_and_prune_target_detection
```

- 確認内容: pytest case `archive path safety and prune target detection` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:110`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-004

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_file_and_markdown_helpers
```

- 確認内容: pytest case `file and markdown helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:139`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-005

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_rag_reference_and_candidate_discovery
```

- 確認内容: pytest case `rag reference and candidate discovery` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:206`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-006

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_defensive_specimen_rag_discovery_keeps_missing_refs_and_low_scores_out
```

- 確認内容: defensive specimen rag discovery keeps missing refs and low scores out を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:256`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-007

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_defensive_specimen_first_heading_empty_after_prefix_removal
```

- 確認内容: defensive specimen first heading empty after prefix removal を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:271`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-008

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_rag_summary_formatting_and_report_builder
```

- 確認内容: pytest case `rag summary formatting and report builder` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:291`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `metadata`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-009

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_prepare_requires_rag_when_requested
```

- 確認内容: pytest case `prepare requires rag when requested` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:352`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-010

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_prepare_writes_rag_enriched_report_and_metadata
```

- 確認内容: pytest case `prepare writes rag enriched report and metadata` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:369`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `summary`, `metadata`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-011

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_prune_requires_human_approval_for_execute
```

- 確認内容: pytest case `prune requires human approval for execute` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:409`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-012

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_prune_dry_run_keeps_targets
```

- 確認内容: pytest case `prune dry run keeps targets` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:433`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-013

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_audit_reports_readiness_and_prepare_no_auto_explicit_rag
```

- 確認内容: pytest case `audit reports readiness and prepare no auto explicit rag` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:455`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `prepared_stdout`, `audit_stdout`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-014

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_prune_execute_removes_targets_and_refuses_missing_reports
```

- 確認内容: pytest case `prune execute removes targets and refuses missing reports` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:514`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-015

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_prune_execute_skips_disappeared_target
```

- 確認内容: pytest case `prune execute skips disappeared target` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:564`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-016

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_remove_helpers_retry_permission_errors
```

- 確認内容: pytest case `remove helpers retry permission errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:592`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `rmtree_calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
