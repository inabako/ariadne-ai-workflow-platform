# Runtime pytest 単体試験仕様書（533ケース）

作成日: 2026-07-07

この文書は、`runtime/tests` 配下で収集されるpytest nodeを、単体試験仕様として1ケースずつ列挙したものです。
上位のUT項目表は [Runtime pytest UT Test Items](test-items.md) を参照します。
coverage推移と監査履歴は repository root の `Runtime pytest 分岐・CLI・coverage監査レポート.md` を参照します。

この仕様書では、長い `pytest node id` でMarkdownプレビューが横に広がらないよう、ケース一覧を表ではなくブロック形式で記載します。

## サマリ

| 項目 | 値 |
| --- | ---: |
| pytest files | 31 |
| pytest test functions | 520 |
| pytest collected cases | 533 |
| pytest result | `533 passed` |
| statement coverage | 100.00% |
| total coverage | 99.73% |

## 共通前提

- 実行起点は `C:\github\ariadne-ai-workflow-platform\runtime` です。
- pytest / coverage は `runtime/pyproject.toml` の `dev` dependency groupで管理します。
- 外部I/O、GitHub API、Git操作、Docker、MSYS2、Go、VSCode task runnerは、原則mock、dry-run、または明示的なmissing検出として検証します。
- 期待結果は、pytest assertionがすべて成功し、対象runtimeが意図したJSON、Markdown、context、manifest、error boundaryを返すことです。

## 実行コマンド

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\tools\uv.cmd run --project . --group dev pytest tests -q
```

収集ケースを確認する場合:

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
.\tools\uv.cmd run --project . --group dev pytest --collect-only -q tests
```

## ケース一覧

### Close Archive

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
  - source: `runtime/tests/test_close_archive.py:203`
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
  - specimen signals: defensive_specimen
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
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-008

- pytest node id:

```text
runtime/tests/test_close_archive.py::test_rag_summary_formatting_and_report_builder
```

- 確認内容: pytest case `rag summary formatting and report builder` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_close_archive.py:253`
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
  - source: `runtime/tests/test_close_archive.py:314`
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
  - source: `runtime/tests/test_close_archive.py:331`
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
  - source: `runtime/tests/test_close_archive.py:371`
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
  - source: `runtime/tests/test_close_archive.py:395`
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
  - source: `runtime/tests/test_close_archive.py:417`
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
  - source: `runtime/tests/test_close_archive.py:476`
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
  - source: `runtime/tests/test_close_archive.py:526`
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
  - source: `runtime/tests/test_close_archive.py:554`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `rmtree_calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Common Runtime

#### RT-UT-CASE-017

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_slugify_and_relative_to_repo_are_stable
```

- 確認内容: pytest case `slugify and relative to repo are stable` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:34`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-018

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_ensure_work_tree_creates_standard_directories
```

- 確認内容: pytest case `ensure work tree creates standard directories` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:45`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-019

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_artifact_index_upsert_replaces_existing_artifact
```

- 確認内容: pytest case `artifact index upsert replaces existing artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:53`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-020

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_write_json_writes_utf8_json_with_parent_dirs
```

- 確認内容: pytest case `write json writes utf8 json with parent dirs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:65`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-021

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_common_root_receipt_json_and_markdown_edges
```

- 確認内容: pytest case `common root receipt json and markdown edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:73`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-022

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_env_line_and_repository_slug_normalization
```

- 確認内容: pytest case `env line and repository slug normalization` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:94`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-023

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_env_file_process_and_github_resolution_edges
```

- 確認内容: pytest case `env file process and github resolution edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:111`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-024

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_extract_repository_config_from_markdown_text
```

- 確認内容: pytest case `extract repository config from markdown text` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:140`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-025

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_defensive_specimen_repository_config_ignores_empty_values_and_remote_alias
```

- 確認内容: defensive specimen repository config ignores empty values and remote alias を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:158`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `text`
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-026

- pytest node id:

```text
runtime/tests/test_common_runtime.py::test_requirement_config_files_and_artifact_index_edges
```

- 確認内容: pytest case `requirement config files and artifact index edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_common_runtime.py:158`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Context First

#### RT-UT-CASE-027

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_manifest_registers_dispatcher_context
```

- 確認内容: pytest case `context manifest registers dispatcher context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:27`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-028

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_require_reports_missing_dispatcher_context
```

- 確認内容: pytest case `context first require reports missing dispatcher context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:63`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-029

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_require_passes_when_context_exists
```

- 確認内容: pytest case `context first require passes when context exists` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:75`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Uncategorized

#### RT-UT-CASE-030

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_loads_test_evidence_context
```

- 確認内容: pytest case `context first loads test evidence context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:101`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Context First

#### RT-UT-CASE-031

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_parser_show_and_main_status_paths
```

- 確認内容: pytest case `context first parser show and main status paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:126`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed_show`, `parsed_require`, `parsed_environment`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-032

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_require_environment_rejects_missing_entry_after_status_ready
```

- 確認内容: pytest case `context first require environment rejects missing entry after status ready` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:183`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-033

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_require_environment_rejects_invalid_selection_document
```

- 確認内容: pytest case `context first require environment rejects invalid selection document` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:214`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-034

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_module_can_be_loaded_as_script_path
```

- 確認内容: pytest case `context first module can be loaded as script path` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:240`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-035

- pytest node id:

```text
runtime/tests/test_context_first.py::test_requirement_intake_registers_context_manifest
```

- 確認内容: pytest case `requirement intake registers context manifest` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:246`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-036

- pytest node id:

```text
runtime/tests/test_context_first.py::test_corrective_action_fix_init_registers_context_manifest
```

- 確認内容: pytest case `corrective action fix init registers context manifest` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:278`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-037

- pytest node id:

```text
runtime/tests/test_context_first.py::test_vscode_environment_init_registers_context_manifest
```

- 確認内容: pytest case `vscode environment init registers context manifest` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:299`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-038

- pytest node id:

```text
runtime/tests/test_context_first.py::test_gui_mode_requires_environment_selection_before_run
```

- 確認内容: pytest case `gui mode requires environment selection before run` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:320`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-039

- pytest node id:

```text
runtime/tests/test_context_first.py::test_gui_mode_registers_state_after_environment_selection
```

- 確認内容: pytest case `gui mode registers state after environment selection` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:342`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-040

- pytest node id:

```text
runtime/tests/test_context_first.py::test_web_svg_layout_mode_rejects_gui_environment_selection
```

- 確認内容: pytest case `web svg layout mode rejects gui environment selection` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:378`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-041

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_require_environment_checks_expected_environment
```

- 確認内容: pytest case `context first require environment checks expected environment` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:414`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-042

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_require_environment_rejects_mismatch
```

- 確認内容: pytest case `context first require environment rejects mismatch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:439`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-043

- pytest node id:

```text
runtime/tests/test_context_first.py::test_iac_handoff_context_registers_execution_plan_and_handoff
```

- 確認内容: pytest case `iac handoff context registers execution plan and handoff` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:466`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `execution_plan`, `handoff`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-044

- pytest node id:

```text
runtime/tests/test_context_first.py::test_iac_handoff_context_parser_paths_and_handoff_defaults
```

- 確認内容: pytest case `iac handoff context parser paths and handoff defaults` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:498`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-045

- pytest node id:

```text
runtime/tests/test_context_first.py::test_iac_handoff_context_reuses_existing_handoff_and_rejects_invalid_existing
```

- 確認内容: pytest case `iac handoff context reuses existing handoff and rejects invalid existing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:551`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-046

- pytest node id:

```text
runtime/tests/test_context_first.py::test_iac_handoff_context_main_and_script_load_paths
```

- 確認内容: pytest case `iac handoff context main and script load paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:581`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-047

- pytest node id:

```text
runtime/tests/test_context_first.py::test_dispatcher_context_init_registers_phase3_contexts
```

- 確認内容: pytest case `dispatcher context init registers phase3 contexts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:607`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `tool_selection`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-048

- pytest node id:

```text
runtime/tests/test_context_first.py::test_dispatcher_context_init_preserves_existing_context_without_force
```

- 確認内容: pytest case `dispatcher context init preserves existing context without force` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:655`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `existing`, `args`, `preserved`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-049

- pytest node id:

```text
runtime/tests/test_context_first.py::test_dispatcher_context_auto_selects_clear_workflow_candidate
```

- 確認内容: pytest case `dispatcher context auto selects clear workflow candidate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:686`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `selection`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-050

- pytest node id:

```text
runtime/tests/test_context_first.py::test_dispatcher_context_auto_scores_tool_candidates
```

- 確認内容: pytest case `dispatcher context auto scores tool candidates` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:744`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `tool_selection`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-051

- pytest node id:

```text
runtime/tests/test_context_first.py::test_dispatcher_context_tool_candidate_human_check_for_docker
```

- 確認内容: pytest case `dispatcher context tool candidate human check for docker` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:828`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `tool_selection`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-052

- pytest node id:

```text
runtime/tests/test_context_first.py::test_rag_build_registers_pipeline_context
```

- 確認内容: pytest case `rag build registers pipeline context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:898`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `artifact`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-053

- pytest node id:

```text
runtime/tests/test_context_first.py::test_corrective_action_report_registers_report_context
```

- 確認内容: pytest case `corrective action report registers report context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:943`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `context`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-054

- pytest node id:

```text
runtime/tests/test_context_first.py::test_corrective_action_fix_prefers_manifest_report_when_argument_missing
```

- 確認内容: pytest case `corrective action fix prefers manifest report when argument missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:995`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `fix_context`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-055

- pytest node id:

```text
runtime/tests/test_context_first.py::test_docs_sync_registers_manifest_contexts
```

- 確認内容: pytest case `docs sync registers manifest contexts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:1036`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-056

- pytest node id:

```text
runtime/tests/test_context_first.py::test_docs_sync_analysis_requires_scm_state_for_new_work
```

- 確認内容: pytest case `docs sync analysis requires scm state for new work` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:1070`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-057

- pytest node id:

```text
runtime/tests/test_context_first.py::test_github_knowledge_registers_tool_selection_and_gate
```

- 確認内容: pytest case `github knowledge registers tool selection and gate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:1096`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `gate`, `tool_selection`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-058

- pytest node id:

```text
runtime/tests/test_context_first.py::test_github_knowledge_sync_plan_requires_mutation_gate
```

- 確認内容: pytest case `github knowledge sync plan requires mutation gate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:1122`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-059

- pytest node id:

```text
runtime/tests/test_context_first.py::test_knowledge_capture_prefers_manifest_context_then_records_resolution
```

- 確認内容: pytest case `knowledge capture prefers manifest context then records resolution` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:1160`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-060

- pytest node id:

```text
runtime/tests/test_context_first.py::test_knowledge_capture_requires_manifest_scm_state_for_active_work
```

- 確認内容: pytest case `knowledge capture requires manifest scm state for active work` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:1205`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Corrective Action Report

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

#### RT-UT-CASE-065

- pytest node id:

```text
runtime/tests/test_corrective_action_report.py::test_corrective_action_report_register_missing_report_and_show_missing
```

- 確認内容: pytest case `corrective action report register missing report and show missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_corrective_action_report.py:181`
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
  - source: `runtime/tests/test_corrective_action_report.py:211`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `register_args`, `show_args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Coverage Audit

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

### aiwfctl / Help / Env

#### RT-UT-CASE-073

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_parser_uses_aiwfctl_program_name
```

- 確認内容: pytest case `ctl parser uses aiwfctl program name` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:16`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-074

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_without_modifier_warns_and_does_not_show_list
```

- 確認内容: pytest case `ctl without modifier warns and does not show list` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:24`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-075

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_without_modifier_warns_and_does_not_show_list
```

- 確認内容: pytest case `ctl help without modifier warns and does not show list` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:36`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-076

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_warning_can_be_colored_yellow
```

- 確認内容: pytest case `ctl warning can be colored yellow` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:48`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-077

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_gui_mode_returns_windows_msys2_profile
```

- 確認内容: pytest case `ctl env select gui mode returns windows msys2 profile` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:58`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-078

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_web_svg_returns_wsl_web_profile
```

- 確認内容: pytest case `ctl env select web svg returns wsl web profile` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:71`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-079

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_unknown_requires_human_check
```

- 確認内容: pytest case `ctl env select unknown requires human check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:84`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-080

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_without_subcommand_shows_environment_management
```

- 確認内容: pytest case `ctl env without subcommand shows environment management` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:101`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-081

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_list_shows_public_environments_not_raw_profile_list
```

- 確認内容: pytest case `ctl env list shows public environments not raw profile list` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:114`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-082

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_show_uses_public_environment_name
```

- 確認内容: pytest case `ctl env show uses public environment name` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:127`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-083

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_tool_name_requires_human_check_with_candidate
```

- 確認内容: pytest case `ctl env select tool name requires human check with candidate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:144`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-084

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_writes_workflow_context
```

- 確認内容: pytest case `ctl env select writes workflow context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:156`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `data`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-085

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_warns_before_overwriting_different_context
```

- 確認内容: pytest case `ctl env select warns before overwriting different context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:203`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `data`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-086

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_list_contains_workflow_commands
```

- 確認内容: pytest case `ctl help list contains workflow commands` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:259`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-087

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_show_includes_arguments_and_details
```

- 確認内容: pytest case `ctl help show includes arguments and details` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:281`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-088

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_corrective_action_fix_help_declares_report_source
```

- 確認内容: pytest case `corrective action fix help declares report source` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:294`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-089

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_vscode_environment_help_declares_repo_local_tools_path
```

- 確認内容: pytest case `vscode environment help declares repo local tools path` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:306`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-090

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_realtime_iac_help_declares_docker_context_gate
```

- 確認内容: pytest case `realtime iac help declares docker context gate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:320`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-091

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_robotics_new_system_iac_help_declares_execution_plan_handoff
```

- 確認内容: pytest case `robotics new system iac help declares execution plan handoff` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:330`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-092

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_context_init_creates_phase3_contexts
```

- 確認内容: pytest case `ctl context init creates phase3 contexts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:341`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Uncategorized

#### RT-UT-CASE-093

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_doctor_runs_workflow_doctor
```

- 確認内容: pytest case `ctl doctor runs workflow doctor` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:384`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### aiwfctl / Help / Env

#### RT-UT-CASE-094

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_defensive_specimen_ctl_doctor_formats_warning_paths
```

- 確認内容: pytest case `defensive specimen ctl doctor formats warning paths` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:412`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-095

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_search_finds_svg_gui_workflows
```

- 確認内容: pytest case `ctl help search finds svg gui workflows` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:412`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-096

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_show_includes_svg_extension_details
```

- 確認内容: pytest case `ctl help show includes svg extension details` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:423`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-097

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_markdown_writes_searchable_file
```

- 確認内容: pytest case `ctl help markdown writes searchable file` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:438`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-098

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_workflow_help_registry_referenced_files_exist
```

- 確認内容: pytest case `workflow help registry referenced files exist` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:462`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-099

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_environment_profile_registry_referenced_docs_exist
```

- 確認内容: pytest case `environment profile registry referenced docs exist` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:484`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-100

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_registry_and_search_helper_edge_cases
```

- 確認内容: pytest case `ctl registry and search helper edge cases` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:506`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-101

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_environment_selection_mapping_branches
```

- 確認内容: pytest case `ctl environment selection mapping branches` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:547`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-102

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_environment_formatting_and_context_warning_helpers
```

- 確認内容: pytest case `ctl environment formatting and context warning helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:586`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `profile`, `context`, `record`, `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-103

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_formatting_empty_lists_and_open_search_paths
```

- 確認内容: pytest case `ctl help formatting empty lists and open search paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:719`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `registry`, `open_args`, `markdown_args`, `search_args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-104

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_color_mode_and_main_output
```

- 確認内容: pytest case `ctl color mode and main output` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:765`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-105

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_run_manual_error_and_json_branches
```

- 確認内容: pytest case `ctl run manual error and json branches` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:791`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Dispatcher Context

#### RT-UT-CASE-106

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_registry_loaders_and_text_helpers_use_safe_defaults
```

- 確認内容: pytest case `registry loaders and text helpers use safe defaults` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:38`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-107

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_select_workflow_record_requires_human_check_for_no_candidate
```

- 確認内容: pytest case `select workflow record requires human check for no candidate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:59`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-108

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_select_workflow_record_requires_human_check_for_ambiguous_candidate
```

- 確認内容: pytest case `select workflow record requires human check for ambiguous candidate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:73`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-109

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_select_workflow_record_requires_human_check_for_low_confidence
```

- 確認内容: pytest case `select workflow record requires human check for low confidence` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:102`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-110

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_workflow_candidate_boundary_paths_cover_empty_limits_and_medium_auto
```

- 確認内容: pytest case `workflow candidate boundary paths cover empty limits and medium auto` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:126`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-111

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_candidate_branch_edges_cover_no_command_and_unmatched_candidates
```

- 確認内容: pytest case `candidate branch edges cover no command and unmatched candidates` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:162`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-112

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_tool_selection_edges_cover_manual_fallback_and_auto_human_check
```

- 確認内容: pytest case `tool selection edges cover manual fallback and auto human check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:210`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-113

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_tool_candidate_boundary_paths_cover_exact_phrase_manual_and_missing_record
```

- 確認内容: pytest case `tool candidate boundary paths cover exact phrase manual and missing record` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:277`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-114

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_context_builders_preserve_existing_files_and_add_environment_context
```

- 確認内容: pytest case `context builders preserve existing files and add environment context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:349`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-115

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_run_init_marks_human_check_and_force_rewrites_context
```

- 確認内容: pytest case `run init marks human check and force rewrites context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:372`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `rewritten`, `plan`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-116

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_parser_and_main_status_paths
```

- 確認内容: pytest case `parser and main status paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:400`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-117

- pytest node id:

```text
runtime/tests/test_dispatcher_context.py::test_module_can_be_loaded_as_script_path_without_running_main
```

- 確認内容: pytest case `module can be loaded as script path without running main` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_dispatcher_context.py:438`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Docs Sync

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
  - source: `runtime/tests/test_docs_sync_workflow.py:225`
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
  - source: `runtime/tests/test_docs_sync_workflow.py:250`
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
  - source: `runtime/tests/test_docs_sync_workflow.py:263`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### GitHub Knowledge Maintenance

#### RT-UT-CASE-129

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_build_parser_parses_every_subcommand
```

- 確認内容: pytest case `build parser parses every subcommand` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:130`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-130

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_repository_name_and_default_work_id_variants
```

- 確認内容: pytest case `repository name and default work id variants` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:140`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-131

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_init_work_rejects_existing_without_reuse_and_script_load
```

- 確認内容: pytest case `init work rejects existing without reuse and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:155`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-132

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_gate_and_tool_selection_proposal_mode_do_not_require_human_check
```

- 確認内容: pytest case `gate and tool selection proposal mode do not require human check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:177`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-133

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_register_github_knowledge_contexts_skips_missing_files_and_registers_existing
```

- 確認内容: pytest case `register github knowledge contexts skips missing files and registers existing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:192`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-134

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_markdown_helpers_render_empty_values_booleans_lists_and_titles
```

- 確認内容: pytest case `markdown helpers render empty values booleans lists and titles` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:212`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-135

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_load_analysis_reports_missing_work_missing_file_and_non_object
```

- 確認内容: pytest case `load analysis reports missing work missing file and non object` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:228`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-136

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_default_analysis_ignores_non_string_assumptions_and_analysis_template_missing_work
```

- 確認内容: pytest case `default analysis ignores non string assumptions and analysis template missing work` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:243`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-137

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_require_github_operation_gate_reports_missing_contexts
```

- 確認内容: pytest case `require github operation gate reports missing contexts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:264`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-138

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_require_github_operation_gate_rejects_unapproved_mutation_and_rag
```

- 確認内容: pytest case `require github operation gate rejects unapproved mutation and rag` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:272`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-139

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_build_repair_sync_and_rag_markdown_include_dynamic_sections
```

- 確認内容: pytest case `build repair sync and rag markdown include dynamic sections` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:283`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-140

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_build_sync_plan_renders_empty_action_placeholder
```

- 確認内容: pytest case `build sync plan renders empty action placeholder` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:298`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-141

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_repair_plan_writes_output_and_registers_artifact
```

- 確認内容: pytest case `create repair plan writes output and registers artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:305`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-142

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_rag_candidate_requires_human_approval_for_publish
```

- 確認内容: pytest case `create rag candidate requires human approval for publish` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:328`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-143

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_rag_candidate_writes_explicit_output_with_ready_gate
```

- 確認内容: pytest case `create rag candidate writes explicit output with ready gate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:347`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-144

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_rag_candidate_default_and_publish_outputs
```

- 確認内容: pytest case `create rag candidate default and publish outputs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:371`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-145

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_run_dispatches_commands_and_rejects_unknown
```

- 確認内容: pytest case `run dispatches commands and rejects unknown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:407`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-146

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_main_prints_json
```

- 確認内容: pytest case `main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:425`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### GitHub Runtime

#### RT-UT-CASE-147

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_api_urls_support_dotcom_and_enterprise_hosts
```

- 確認内容: pytest case `github api urls support dotcom and enterprise hosts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:23`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-148

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_defensive_specimen_issue_body_report_path_returns_empty_without_car_artifact
```

- 確認内容: defensive specimen issue body report path returns empty without car artifact を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:35`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-149

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_token_is_required
```

- 確認内容: pytest case `github token is required` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:49`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-150

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_api_json_sends_request_and_parses_response
```

- 確認内容: pytest case `github api json sends request and parses response` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:54`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `seen`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-151

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_api_json_reports_http_and_url_errors
```

- 確認内容: pytest case `github api json reports http and url errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:77`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-152

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_graphql_json_returns_data_and_reports_errors
```

- 確認内容: pytest case `github graphql json returns data and reports errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:112`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-153

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_graphql_json_reports_http_and_url_errors
```

- 確認内容: pytest case `github graphql json reports http and url errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:122`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-154

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_get_branch_sha_requires_commit_sha
```

- 確認内容: pytest case `get branch sha requires commit sha` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:157`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-155

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_get_branch_sha_returns_commit_sha
```

- 確認内容: pytest case `get branch sha returns commit sha` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:164`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-156

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_get_repository_issue_graphql_context_returns_ids_and_validates_required_fields
```

- 確認内容: pytest case `get repository issue graphql context returns ids and validates required fields` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:170`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-157

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_linked_branch_uses_context_and_defaults_missing_linked_ref
```

- 確認内容: pytest case `create linked branch uses context and defaults missing linked ref` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:208`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-158

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_branch_ref_returns_ref_and_validates_response
```

- 確認内容: pytest case `create branch ref returns ref and validates response` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:228`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-159

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_normalize_issue_title_applies_prefix_once
```

- 確認内容: pytest case `normalize issue title applies prefix once` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:238`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-160

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[robotics-new-system-\u521d\u671f\u958b\u767a]
```

- 確認内容: pytest case `infer flow label from agent context[robotics-new-system-\u521d\u671f\u958b\u767a]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:257`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`robotics-new-system-\u521d\u671f\u958b\u767a`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-161

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[robotics-feature-maintenance-\u65b0\u898f\u6a5f\u80fd\u30d5\u30ed\u30fc]
```

- 確認内容: pytest case `infer flow label from agent context[robotics-feature-maintenance-\u65b0\u898f\u6a5f\u80fd\u30d5\u30ed\u30fc]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:257`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`robotics-feature-maintenance-\u65b0\u898f\u6a5f\u80fd\u30d5\u30ed\u30fc`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-162

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[corrective-action-fix-\u6539\u5584\u30d5\u30ed\u30fc]
```

- 確認内容: pytest case `infer flow label from agent context[corrective-action-fix-\u6539\u5584\u30d5\u30ed\u30fc]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:257`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`corrective-action-fix-\u6539\u5584\u30d5\u30ed\u30fc`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-163

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[docs-sync-\u6539\u5584\u30d5\u30ed\u30fc]
```

- 確認内容: pytest case `infer flow label from agent context[docs-sync-\u6539\u5584\u30d5\u30ed\u30fc]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:257`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`docs-sync-\u6539\u5584\u30d5\u30ed\u30fc`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-164

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[unknown-]
```

- 確認内容: pytest case `infer flow label from agent context[unknown-]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:257`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`unknown-`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-165

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_default_issue_body_uses_project_template_and_corrective_report
```

- 確認内容: pytest case `default issue body uses project template and corrective report` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:267`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-166

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_issue_body_from_args_reads_body_file
```

- 確認内容: pytest case `issue body from args reads body file` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:313`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-167

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_issue_manager_template_default_and_package_guard_edges
```

- 確認内容: pytest case `issue manager template default and package guard edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:326`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-168

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_draft_writes_body_record_and_artifact_index
```

- 確認内容: pytest case `manage issue draft writes body record and artifact index` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:360`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-169

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_create_uses_defaults_and_updates_artifact_status
```

- 確認内容: pytest case `manage issue create uses defaults and updates artifact status` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:397`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-170

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_requires_work_dir_and_github_repo
```

- 確認内容: pytest case `manage issue requires work dir and github repo` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:444`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-171

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_rejects_repo_without_owner
```

- 確認内容: pytest case `manage issue rejects repo without owner` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:467`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-172

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_rejects_slug_without_owner_after_resolution
```

- 確認内容: pytest case `manage issue rejects slug without owner after resolution` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:490`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-173

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_issue_with_api_extracts_number_from_url_when_missing
```

- 確認内容: pytest case `create issue with api extracts number from url when missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:513`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-174

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_issue_with_api_builds_url_from_number_and_rejects_missing_url
```

- 確認内容: pytest case `create issue with api builds url from number and rejects missing url` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:549`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `payloads`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-175

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_issue_manager_main_prints_json
```

- 確認内容: pytest case `issue manager main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:577`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-176

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_create_requires_human_approval
```

- 確認内容: pytest case `pull request create requires human approval` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:608`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-177

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_defaults_use_latest_issue_title_and_base_work_id
```

- 確認内容: pytest case `pull request defaults use latest issue title and base work id` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:630`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-178

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_uses_title_and_body_files_and_create_path
```

- 確認内容: pytest case `pull request uses title and body files and create path` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:653`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-179

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_requires_work_repo_and_head
```

- 確認内容: pytest case `pull request requires work repo and head` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:697`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-180

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_pull_request_with_api_posts_payload
```

- 確認内容: pytest case `create pull request with api posts payload` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:726`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `seen`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-181

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_draft_writes_record_and_updates_scm_state
```

- 確認内容: pytest case `pull request draft writes record and updates scm state` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:755`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-182

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_parser_file_defaults_main_and_script_paths
```

- 確認内容: pytest case `pull request parser file defaults main and script paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:782`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Corrective Action Fix Init

#### RT-UT-CASE-183

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

#### RT-UT-CASE-184

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

#### RT-UT-CASE-185

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

#### RT-UT-CASE-186

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

#### RT-UT-CASE-187

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
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-188

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
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-189

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_run_with_argument_report_and_reuse_existing
```

- 確認内容: pytest case `init corrective action fix run with argument report and reuse existing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:188`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `agent`, `artifact_index`, `report_context`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-190

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_run_missing_report_has_no_report_artifact
```

- 確認内容: pytest case `init corrective action fix run missing report has no report artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:222`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-191

- pytest node id:

```text
runtime/tests/test_init_corrective_action_fix.py::test_init_corrective_action_fix_parser_and_main_paths
```

- 確認内容: pytest case `init corrective action fix parser and main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_init_corrective_action_fix.py:235`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Requirement Intake

#### RT-UT-CASE-192

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_parser_and_workflow_mapping_helpers
```

- 確認内容: pytest case `parser and workflow mapping helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:41`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-193

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_discover_requirement_documents_rejects_invalid_inputs
```

- 確認内容: pytest case `discover requirement documents rejects invalid inputs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:99`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-194

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_repository_control_and_unique_destination
```

- 確認内容: pytest case `repository control and unique destination` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:129`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-195

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_initialize_context_and_manifest_registration
```

- 確認内容: pytest case `initialize context and manifest registration` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:152`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `agent_context`, `handoff`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-196

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_run_with_explicit_requirements_copies_and_uses_unique_names
```

- 確認内容: pytest case `run with explicit requirements copies and uses unique names` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:183`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `agent_context`, `artifact_index`, `handoff`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-197

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_run_discovers_single_requirement_moves_and_generates_receipt
```

- 確認内容: pytest case `run discovers single requirement moves and generates receipt` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:225`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-198

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_run_rejects_missing_explicit_requirement
```

- 確認内容: pytest case `run rejects missing explicit requirement` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:255`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-199

- pytest node id:

```text
runtime/tests/test_intake_requirements.py::test_main_outputs_json_and_reports_error
```

- 確認内容: pytest case `main outputs json and reports error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_intake_requirements.py:266`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Knowledge Capture

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
  - source: `runtime/tests/test_knowledge_capture.py:155`
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
  - source: `runtime/tests/test_knowledge_capture.py:215`
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
  - source: `runtime/tests/test_knowledge_capture.py:254`
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
  - source: `runtime/tests/test_knowledge_capture.py:278`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `issue`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Observability Metrics

#### RT-UT-CASE-207

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_monthly_log_path_uses_year_month_suffix
```

- 確認内容: pytest case `monthly log path uses year month suffix` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:17`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-208

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_resolve_log_path_rotates_base_runtime_metrics_file
```

- 確認内容: pytest case `resolve log path rotates base runtime metrics file` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:25`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-209

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_resolve_log_path_can_disable_rotation_for_base_or_directory
```

- 確認内容: pytest case `resolve log path can disable rotation for base or directory` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:33`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-210

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_append_jsonl_appends_one_record_per_line
```

- 確認内容: pytest case `append jsonl appends one record per line` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:40`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-211

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_append_jsonl_returns_warning_without_raising_when_parent_is_file
```

- 確認内容: pytest case `append jsonl returns warning without raising when parent is file` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:51`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-212

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_schema_helpers_sanitize_negative_and_invalid_values
```

- 確認内容: pytest case `schema helpers sanitize negative and invalid values` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:61`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-213

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_runtime_metric_record_falls_back_to_runtime_error_for_unknown_event
```

- 確認内容: pytest case `runtime metric record falls back to runtime error for unknown event` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:72`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-214

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_duration_timer_records_elapsed_duration
```

- 確認内容: pytest case `duration timer records elapsed duration` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:80`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-215

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_defaults_log_dir_under_runtime_logs
```

- 確認内容: pytest case `collector defaults log dir under runtime logs` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:87`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-216

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_records_non_fatal_log_write_warning
```

- 確認内容: pytest case `collector records non fatal log write warning` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:93`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-217

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_records_workflow_agent_token_context_and_monthly_jsonl
```

- 確認内容: pytest case `collector records workflow agent token context and monthly jsonl` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:104`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-218

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_records_human_check_evidence_and_runtime_error
```

- 確認内容: pytest case `collector records human check evidence and runtime error` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:140`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-219

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_failed_workflow_saves_human_check_required_evidence
```

- 確認内容: pytest case `collector failed workflow saves human check required evidence` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:155`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `payload`
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-220

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_saves_workflow_evidence_and_registers_context
```

- 確認内容: pytest case `collector saves workflow evidence and registers context` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:168`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `manifest`
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-221

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_evidence_summary_can_skip_work_dir_or_manifest_registration
```

- 確認内容: pytest case `collector evidence summary can skip work dir or manifest registration` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:192`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-222

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_collector_evidence_summary_returns_warning_without_raising
```

- 確認内容: pytest case `collector evidence summary returns warning without raising` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:206`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

#### RT-UT-CASE-223

- pytest node id:

```text
runtime/tests/test_observability_metrics.py::test_register_runtime_metrics_context_uses_runtime_metrics_type
```

- 確認内容: pytest case `register runtime metrics context uses runtime metrics type` checks Runtime Observability monthly rotation, JSONL append, evidence output, Context First registration, token/context/cost handling, and non-fatal write warnings.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_observability_metrics.py:218`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and Runtime Observability metrics are recorded without breaking workflow execution.

### Preflight

#### RT-UT-CASE-224

- pytest node id:

```text
runtime/tests/test_preflight.py::test_docker_compose_check_reports_missing_docker
```

- 確認内容: pytest case `docker compose check reports missing docker` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:15`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-225

- pytest node id:

```text
runtime/tests/test_preflight.py::test_basic_checks_report_detected_state
```

- 確認内容: pytest case `basic checks report detected state` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:27`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-226

- pytest node id:

```text
runtime/tests/test_preflight.py::test_python_module_check_uses_current_interpreter
```

- 確認内容: pytest case `python module check uses current interpreter` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:55`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-227

- pytest node id:

```text
runtime/tests/test_preflight.py::test_docker_compose_check_uses_compose_version
```

- 確認内容: pytest case `docker compose check uses compose version` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:71`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-228

- pytest node id:

```text
runtime/tests/test_preflight.py::test_docker_compose_check_reports_compose_error
```

- 確認内容: pytest case `docker compose check reports compose error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:86`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-229

- pytest node id:

```text
runtime/tests/test_preflight.py::test_localty_protocol_check_uses_msys2_python_when_available
```

- 確認内容: pytest case `localty protocol check uses msys2 python when available` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:100`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-230

- pytest node id:

```text
runtime/tests/test_preflight.py::test_localty_protocol_check_uses_fallback_repository
```

- 確認内容: pytest case `localty protocol check uses fallback repository` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:121`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-231

- pytest node id:

```text
runtime/tests/test_preflight.py::test_localty_protocol_check_reports_missing_without_work_id
```

- 確認内容: pytest case `localty protocol check reports missing without work id` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:140`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-232

- pytest node id:

```text
runtime/tests/test_preflight.py::test_localty_protocol_check_reports_missing_with_fallback_command
```

- 確認内容: pytest case `localty protocol check reports missing with fallback command` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:156`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-233

- pytest node id:

```text
runtime/tests/test_preflight.py::test_msys2_package_check_missing_bash_and_success
```

- 確認内容: pytest case `msys2 package check missing bash and success` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:175`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-234

- pytest node id:

```text
runtime/tests/test_preflight.py::test_docker_compose_profile_declares_required_docker_checks
```

- 確認内容: pytest case `docker compose profile declares required docker checks` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:195`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-235

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_profiles_add_expected_checks[corrective-action-fix-expected_ids0]
```

- 確認内容: pytest case `build checks profiles add expected checks[corrective-action-fix-expected_ids0]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:228`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`corrective-action-fix-expected_ids0`
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-236

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_profiles_add_expected_checks[web-nextjs-expected_ids1]
```

- 確認内容: pytest case `build checks profiles add expected checks[web-nextjs-expected_ids1]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:228`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`web-nextjs-expected_ids1`
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-237

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_profiles_add_expected_checks[vscode-environment-expected_ids2]
```

- 確認内容: pytest case `build checks profiles add expected checks[vscode-environment-expected_ids2]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:228`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`vscode-environment-expected_ids2`
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-238

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_localty_gui_and_profiles_without_source_dir
```

- 確認内容: pytest case `build checks localty gui and profiles without source dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:256`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `gui_args`, `localty_args`, `vscode_args`, `web_args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-239

- pytest node id:

```text
runtime/tests/test_preflight.py::test_install_requires_human_approval_before_running_commands
```

- 確認内容: pytest case `install requires human approval before running commands` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:304`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-240

- pytest node id:

```text
runtime/tests/test_preflight.py::test_install_missing_runs_required_commands_and_fallback
```

- 確認内容: pytest case `install missing runs required commands and fallback` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:316`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `checks`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-241

- pytest node id:

```text
runtime/tests/test_preflight.py::test_install_missing_breaks_without_fallback_or_when_fallback_fails
```

- 確認内容: pytest case `install missing breaks without fallback or when fallback fails` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:354`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `checks`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-242

- pytest node id:

```text
runtime/tests/test_preflight.py::test_install_missing_runs_msys2_package_with_bash
```

- 確認内容: pytest case `install missing runs msys2 package with bash` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:408`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-243

- pytest node id:

```text
runtime/tests/test_preflight.py::test_markdown_report_includes_fallback_command
```

- 確認内容: pytest case `markdown report includes fallback command` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:433`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-244

- pytest node id:

```text
runtime/tests/test_preflight.py::test_markdown_report_includes_missing_optional_items
```

- 確認内容: pytest case `markdown report includes missing optional items` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:461`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-245

- pytest node id:

```text
runtime/tests/test_preflight.py::test_markdown_report_iterates_multiple_required_missing_items
```

- 確認内容: pytest case `markdown report iterates multiple required missing items` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:496`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-246

- pytest node id:

```text
runtime/tests/test_preflight.py::test_markdown_report_reports_none_when_all_checks_ready
```

- 確認内容: pytest case `markdown report reports none when all checks ready` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:531`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-247

- pytest node id:

```text
runtime/tests/test_preflight.py::test_write_reports_creates_json_and_markdown
```

- 確認内容: pytest case `write reports creates json and markdown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:556`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-248

- pytest node id:

```text
runtime/tests/test_preflight.py::test_main_writes_report_and_returns_ready
```

- 確認内容: pytest case `main writes report and returns ready` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:572`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-249

- pytest node id:

```text
runtime/tests/test_preflight.py::test_main_returns_two_when_required_check_missing
```

- 確認内容: pytest case `main returns two when required check missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:598`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-250

- pytest node id:

```text
runtime/tests/test_preflight.py::test_main_runs_install_after_human_approval_and_module_script_load
```

- 確認内容: pytest case `main runs install after human approval and module script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:624`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### UT Spec Sync

#### RT-UT-CASE-251

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_normalize_collected_node_and_parse_spec_cases
```

- 確認内容: pytest case `normalize collected node and parse spec cases` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:9`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-252

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_collect_pytest_nodes_filters_noise_and_reports_collect_error
```

- 確認内容: pytest case `defensive specimen collect pynodes filters noise and reports collect error` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:41`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-253

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_script_path_load_exposes_helpers
```

- 確認内容: pytest case `defensive specimen script path load exposes helpers` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:73`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-254

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_parse_spec_closing_fence_without_node
```

- 確認内容: pytest case `defensive specimen parse spec closing fence without node` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:80`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-255

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_ast_decorator_shapes_are_ignored_or_reduced
```

- 確認内容: pytest case `defensive specimen ast decorator shapes are ignored or reduced` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:94`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-256

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_ast_input_helpers_preserve_only_explainable_inputs
```

- 確認内容: pytest case `defensive specimen ast input helpers preserve only explainable inputs` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:127`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-257

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_function_info_and_input_lines_for_no_inline_inputs
```

- 確認内容: pytest case `defensive specimen function info and input lines for no inline inputs` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:156`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-258

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_input_lines_include_source_fixture_parameter_and_inline_values
```

- 確認内容: pytest case `input lines include source fixture parameter and inline values` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:34`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-259

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_replace_input_sections_preserves_confirmation_expected_order
```

- 確認内容: pytest case `replace input sections preserves confirmation expected order` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:64`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `spec`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-260

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_replace_input_sections_skips_legacy_multiline_input_until_next_field
```

- 確認内容: pytest case `defensive specimen replace input sections skips legacy multiline input until next field` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:241`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-261

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_replace_input_sections_keeps_confirm_without_node_id
```

- 確認内容: defensive specimen replace input sections keeps confirm without node id を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:275`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-262

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_check_spec_reports_missing_stale_order_and_bad_input
```

- 確認内容: pytest case `check spec reports missing stale order and bad input` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:98`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-263

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_main_fix_inputs_and_check_json_output
```

- 確認内容: pytest case `main fix inputs and check json output` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:126`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `payload`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-264

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_default_paths_and_register_context_requires_work_dir
```

- 確認内容: pytest case `defensive specimen default paths and register context requires work dir` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:343`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-265

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_report_payload_and_context_first_registration
```

- 確認内容: pytest case `report payload and context first registration` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:166`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `check_result`, `payload`, `saved`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

#### RT-UT-CASE-266

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_main_uses_default_report_paths_when_registering_context
```

- 確認内容: pytest case `defensive specimen main uses default report paths when registering context` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:408`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-267

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_defensive_specimen_main_writes_report_without_context_registration
```

- 確認内容: pytest case `defensive specimen main writes report without context registration` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:464`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-268

- pytest node id:

```text
runtime/tests/test_pytest_ut_spec_sync.py::test_main_check_writes_report_and_registers_context
```

- 確認内容: pytest case `main check writes report and registers context` に対応するUT仕様書とpytest実体の同期チェック、入力値抽出、差分検知、Context First manifest接続の単体振る舞いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_pytest_ut_spec_sync.py:213`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`, `manifest`
- 期待結果: 該当caseがpassし、UT仕様書とpytest実体の同期検査、入力値生成、Context First manifest登録が仕様どおりに確認される。

### RAG Artifact Migration

#### RT-UT-CASE-269

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_renames_legacy_json_and_rewrites_references
```

- 確認内容: pytest case `migrate retrieval artifacts renames legacy json and rewrites references` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:25`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `migrated_context`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-270

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_deletes_duplicate_markdown_for_migrated_companion
```

- 確認内容: pytest case `migrate retrieval artifacts deletes duplicate markdown for migrated companion` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:86`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-271

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_repairs_from_jsonized_wrapper
```

- 確認内容: pytest case `migrate retrieval artifacts repairs from jsonized wrapper` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:115`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `payload`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-272

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_defensive_specimen_migration_does_not_duplicate_existing_legacy_path
```

- 確認内容: defensive specimen migration does not duplicate existing legacy path を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:153`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `payload`
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-273

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_jsonizes_non_duplicate_markdown
```

- 確認内容: pytest case `migrate retrieval artifacts jsonizes non duplicate markdown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:153`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `payload`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-274

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_parser_and_helper_edges
```

- 確認内容: pytest case `migrate retrieval artifacts parser and helper edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:180`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-275

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_missing_retrieval_dir_fails
```

- 確認内容: pytest case `migrate retrieval artifacts missing retrieval dir fails` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:236`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-276

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_delete_source_and_generic_artifact
```

- 確認内容: pytest case `migrate retrieval artifacts delete source and generic artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:252`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `payload`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-277

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_jsonized_repair_skips_invalid_wrappers
```

- 確認内容: pytest case `migrate retrieval artifacts jsonized repair skips invalid wrappers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:280`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `wrappers`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-278

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_prunes_legacy_migration_outputs
```

- 確認内容: pytest case `migrate retrieval artifacts prunes legacy migration outputs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:326`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-279

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_delete_markdown_source_and_skip_readme
```

- 確認内容: pytest case `migrate retrieval artifacts delete markdown source and skip readme` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:381`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-280

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_migrate_retrieval_artifacts_main_paths
```

- 確認内容: pytest case `migrate retrieval artifacts main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:407`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-281

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_renames_legacy_report_and_updates_references
```

- 確認内容: pytest case `standardize report names renames legacy report and updates references` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:428`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-282

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_skips_already_standard_and_readme
```

- 確認内容: pytest case `standardize report names skips already standard and readme` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:470`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-283

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_rejects_source_dir_outside_repo
```

- 確認内容: pytest case `standardize report names rejects source dir outside repo` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:492`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-284

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_parser_and_helper_fallbacks
```

- 確認内容: pytest case `standardize report names parser and helper fallbacks` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:507`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-285

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_missing_dir_and_target_collision
```

- 確認内容: pytest case `standardize report names missing dir and target collision` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:566`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-286

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_replace_text_references_updates_supported_files
```

- 確認内容: pytest case `standardize report names replace text references updates supported files` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:592`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `old_rel`, `new_rel`, `files`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-287

- pytest node id:

```text
runtime/tests/test_rag_artifact_migration.py::test_standardize_report_names_main_paths
```

- 確認内容: pytest case `standardize report names main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_artifact_migration.py:627`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### RAG Build

#### RT-UT-CASE-288

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_small_helpers
```

- 確認内容: pytest case `rag build small helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:41`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-289

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_artifact_defaults_and_human_check_reasons
```

- 確認内容: pytest case `rag build artifact defaults and human check reasons` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:67`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `stages`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-290

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_register_rag_build_context_uses_work_dir_name
```

- 確認内容: pytest case `register rag build context uses work dir name` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:111`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-291

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_run_with_standardize_and_context_registration
```

- 確認内容: pytest case `rag build run with standardize and context registration` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:137`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `stage_calls`, `artifact`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-292

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_run_skip_standardize_and_explicit_work_dir
```

- 確認内容: pytest case `rag build run skip standardize and explicit work dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:210`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `stage_names`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-293

- pytest node id:

```text
runtime/tests/test_rag_build.py::test_rag_build_parser_and_main_paths
```

- 確認内容: pytest case `rag build parser and main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_build.py:256`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### RAG Dispatcher

#### RT-UT-CASE-294

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_planning_helpers_cover_context_and_explicit_paths
```

- 確認内容: pytest case `dispatcher planning helpers cover context and explicit paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:71`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `query_items_for_append`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-295

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_execution_plan_and_plan_normalization_paths
```

- 確認内容: pytest case `dispatcher execution plan and plan normalization paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:158`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `manifest`, `plan`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-296

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_existing_plan_validation_and_execution_plan_override
```

- 確認内容: pytest case `dispatcher existing plan validation and execution plan override` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:231`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-297

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_command_index_build_and_aggregation_helpers
```

- 確認内容: pytest case `dispatcher command index build and aggregation helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:270`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `query_item`, `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-298

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_run_failure_paths_and_markdown_main
```

- 確認内容: pytest case `dispatcher run failure paths and markdown main` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:374`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `retrieval_calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-299

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_run_command_json_boundaries
```

- 確認内容: pytest case `dispatcher run command json boundaries` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:484`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-300

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_writes_query_plan_before_dispatch
```

- 確認内容: pytest case `dispatcher writes query plan before dispatch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:514`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `plan`, `dispatch`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-301

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_can_reuse_existing_query_plan
```

- 確認内容: pytest case `dispatcher can reuse existing query plan` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:574`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `plan`, `args`, `dispatch`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-302

- pytest node id:

```text
runtime/tests/test_rag_dispatcher.py::test_dispatcher_warns_when_work_id_has_no_execution_plan
```

- 確認内容: pytest case `dispatcher warns when work id has no execution plan` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_dispatcher.py:632`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `plan`, `dispatch`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### RAG Pipeline Units

#### RT-UT-CASE-303

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

#### RT-UT-CASE-304

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

#### RT-UT-CASE-305

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

#### RT-UT-CASE-306

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

#### RT-UT-CASE-307

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

#### RT-UT-CASE-308

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_normalize_documents_missing_source_and_main_paths
```

- 確認内容: pytest case `normalize documents missing source and main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:219`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-309

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_normalize_documents_module_can_be_loaded_as_script_path
```

- 確認内容: pytest case `normalize documents module can be loaded as script path` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:249`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-310

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_discover_sources_ignores_readme
```

- 確認内容: pytest case `discover sources ignores readme` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:255`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-311

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_split_content_validates_chunk_settings
```

- 確認内容: pytest case `split content validates chunk settings` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:265`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-312

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_documents_parser_and_heading_path_edges
```

- 確認内容: pytest case `chunk documents parser and heading path edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:273`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-313

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_split_content_short_empty_and_overlap_edges
```

- 確認内容: pytest case `split content short empty and overlap edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:305`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-314

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_split_content_defensive_fallback_preserves_text_when_splitter_yields_no_parts
```

- 確認内容: pytest case `split content defensive fallback preserves text when splitter yields no parts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:322`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-315

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_document_writes_chunk_with_heading_path
```

- 確認内容: pytest case `chunk document writes chunk with heading path` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:337`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-316

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_document_rejects_non_object_json
```

- 確認内容: pytest case `chunk document rejects non object json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:366`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-317

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_discover_documents_errors_and_sorts_recursively
```

- 確認内容: pytest case `discover documents errors and sorts recursively` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:381`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-318

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_documents_run_cleans_output_and_supports_absolute_dirs
```

- 確認内容: pytest case `chunk documents run cleans output and supports absolute dirs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:399`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-319

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_chunk_documents_main_paths
```

- 確認内容: pytest case `chunk documents main paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:442`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-320

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_build_index_writes_document_and_chunk_jsonl
```

- 確認内容: pytest case `build index writes document and chunk jsonl` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:463`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `documents`, `chunks`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-321

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_build_index_parser_invalid_rows_empty_discovery_main_and_script
```

- 確認内容: pytest case `build index parser invalid rows empty discovery main and script` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:513`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-322

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_embed_chunks_is_deterministic_and_validates_dimensions
```

- 確認内容: pytest case `embed chunks is deterministic and validates dimensions` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:571`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `row`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-323

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_embed_chunks_parser_jsonl_edges_and_empty_embedding
```

- 確認内容: pytest case `embed chunks parser jsonl edges and empty embedding` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:592`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-324

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_embed_chunks_run_writes_jsonl
```

- 確認内容: pytest case `embed chunks run writes jsonl` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:630`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-325

- pytest node id:

```text
runtime/tests/test_rag_pipeline_units.py::test_embed_chunks_main_success_error_and_script_load
```

- 確認内容: pytest case `embed chunks main success error and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_pipeline_units.py:653`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### RAG Retrieve Context

#### RT-UT-CASE-326

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_read_jsonl_reports_line_number_for_invalid_json
```

- 確認内容: pytest case `read jsonl reports line number for invalid json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:36`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-327

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_read_jsonl_requires_existing_file_and_ignores_non_object_rows
```

- 確認内容: pytest case `read jsonl requires existing file and ignores non object rows` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:44`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-328

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_tokenize_sparse_embedding_and_cosine_cover_cjk_and_empty_values
```

- 確認内容: pytest case `tokenize sparse embedding and cosine cover cjk and empty values` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:55`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-329

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_filter_row_applies_all_optional_filters
```

- 確認内容: pytest case `filter row applies all optional filters` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:67`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `row`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-330

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_retrieve_filters_rows_and_selects_keyword_matches
```

- 確認内容: pytest case `retrieve filters rows and selects keyword matches` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:91`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `rows`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-331

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_retrieve_scores_semantic_hybrid_no_match_and_below_top_k
```

- 確認内容: pytest case `retrieve scores semantic hybrid no match and below top k` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:129`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `rows`, `embeddings`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-332

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_retrieve_context_edges_for_empty_terms_embeddings_and_tiny_budget
```

- 確認内容: pytest case `retrieve context edges for empty terms embeddings and tiny budget` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:149`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `row`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-333

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_retrieve_requires_positive_top_k
```

- 確認内容: pytest case `retrieve requires positive top k` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:190`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-334

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_split_units_and_compress_chunk_cover_matching_fallback_and_truncation
```

- 確認内容: pytest case `split units and compress chunk cover matching fallback and truncation` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:208`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `content`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-335

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_build_context_respects_budget_and_preserves_source_metadata
```

- 確認内容: pytest case `build context respects budget and preserves source metadata` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:227`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `selected`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-336

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_write_context_markdown_lists_sources
```

- 確認内容: pytest case `write context markdown lists sources` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:257`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-337

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_run_keyword_retrieval_writes_context_pack_and_markdown
```

- 確認内容: pytest case `run keyword retrieval writes context pack and markdown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:276`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `row`, `args`, `context_pack`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-338

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_run_hybrid_retrieval_uses_embeddings_and_absolute_output_dir
```

- 確認内容: pytest case `run hybrid retrieval uses embeddings and absolute output dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:327`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `row`, `retrieval`, `context_pack`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-339

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_run_rejects_non_positive_max_chars
```

- 確認内容: pytest case `run rejects non positive max chars` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:380`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-340

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_semantic_search_requires_embeddings_index
```

- 確認内容: pytest case `semantic search requires embeddings index` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:385`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-341

- pytest node id:

```text
runtime/tests/test_rag_retrieve_context.py::test_main_prints_json
```

- 確認内容: pytest case `main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_rag_retrieve_context.py:413`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Human Gate / VSCode Task Runner

#### RT-UT-CASE-342

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_load_registry_defaults_when_missing
```

- 確認内容: pytest case `human gate policy load registry defaults when missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:50`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-343

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_load_registry_adds_defaults_for_partial_file
```

- 確認内容: pytest case `human gate policy load registry adds defaults for partial file` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:59`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-344

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_list_returns_registry_path_and_gates
```

- 確認内容: pytest case `human gate policy list returns registry path and gates` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:70`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-345

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_check_blocks_pending_human_approval
```

- 確認内容: pytest case `human gate policy check blocks pending human approval` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:82`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-346

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_check_approves_when_value_matches
```

- 確認内容: pytest case `human gate policy check approves when value matches` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:98`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-347

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_non_required_gate_does_not_block
```

- 確認内容: pytest case `human gate policy non required gate does not block` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:109`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-348

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_unknown_gate_raises_key_error
```

- 確認内容: pytest case `human gate policy unknown gate raises key error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:120`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-349

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_main_list_prints_json
```

- 確認内容: pytest case `human gate policy main list prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:128`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-350

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_main_check_returns_one_when_blocked
```

- 確認内容: pytest case `human gate policy main check returns one when blocked` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:141`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-351

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_human_gate_policy_main_reports_error_for_unknown_gate
```

- 確認内容: pytest case `human gate policy main reports error for unknown gate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:158`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-352

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_refreshed_env_merges_registry_and_extra
```

- 確認内容: pytest case `vscode task runner refreshed env merges registry and extra` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:175`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-353

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_find_executable_uses_fallback
```

- 確認内容: pytest case `vscode task runner find executable uses fallback` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:185`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-354

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_run_process_uses_cwd_and_returns_code
```

- 確認内容: pytest case `vscode task runner run process uses cwd and returns code` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:193`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-355

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_command_display_posix_quotes_arguments
```

- 確認内容: pytest case `vscode task runner command display posix quotes arguments` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:215`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-356

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_windows_registry_paths_returns_empty_on_non_windows
```

- 確認内容: pytest case `vscode task runner windows registry paths returns empty on non windows` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:221`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-357

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_run_open_questions_invokes_helper
```

- 確認内容: pytest case `vscode task runner run open questions invokes helper` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:227`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-358

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_run_preflight_uses_refreshed_env
```

- 確認内容: pytest case `vscode task runner run preflight uses refreshed env` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:250`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-359

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_run_helper_help_invokes_vscode_environment_help
```

- 確認内容: pytest case `vscode task runner run helper help invokes vscode environment help` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:280`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-360

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_msys2_smoke_reports_missing_bash
```

- 確認内容: pytest case `vscode task runner msys2 smoke reports missing bash` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:288`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-361

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_run_docker_version_reports_missing_docker
```

- 確認内容: pytest case `vscode task runner run docker version reports missing docker` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:301`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-362

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_run_docker_version_uses_found_executable
```

- 確認内容: pytest case `vscode task runner run docker version uses found executable` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:315`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-363

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_run_go_version_reports_missing_go
```

- 確認内容: pytest case `vscode task runner run go version reports missing go` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:330`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-364

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_run_go_version_uses_found_executable
```

- 確認内容: pytest case `vscode task runner run go version uses found executable` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:344`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-365

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_skill_info_prints_command_and_skill
```

- 確認内容: pytest case `vscode task runner skill info prints command and skill` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:359`
  - fixture/arg: `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-366

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_main_dispatches_skill_info
```

- 確認内容: pytest case `vscode task runner main dispatches skill info` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:370`
  - fixture/arg: `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-367

- pytest node id:

```text
runtime/tests/test_remaining_policy_vscode_runtime.py::test_vscode_task_runner_windows_registry_and_remaining_edges
```

- 確認内容: pytest case `vscode task runner windows registry and remaining edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_remaining_policy_vscode_runtime.py:386`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `fake_winreg`, `calls`, `calls_process`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Remaining RAG / SCM

#### RT-UT-CASE-368

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

#### RT-UT-CASE-369

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

#### RT-UT-CASE-370

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

#### RT-UT-CASE-371

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

#### RT-UT-CASE-372

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

#### RT-UT-CASE-373

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

#### RT-UT-CASE-374

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

#### RT-UT-CASE-375

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

#### RT-UT-CASE-376

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

#### RT-UT-CASE-377

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

### Retrieval Task Runner

#### RT-UT-CASE-378

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_duplicate_task_ids
```

- 確認内容: pytest case `task plan rejects duplicate task ids` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:24`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-379

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload0-Task plan must be a JSON object]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload0-Task plan must be a JSON object]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload0-Task plan must be a JSON object`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-380

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload1-non-empty tasks array]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload1-non-empty tasks array]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload1-non-empty tasks array`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-381

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload2-non-empty tasks array]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload2-non-empty tasks array]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload2-non-empty tasks array`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-382

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload3-Each task must be a JSON object]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload3-Each task must be a JSON object]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload3-Each task must be a JSON object`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-383

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload4-non-empty id]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload4-non-empty id]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload4-non-empty id`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-384

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload5-non-empty id]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload5-non-empty id]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload5-non-empty id`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-385

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload6-depends_on must be a string array]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload6-depends_on must be a string array]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload6-depends_on must be a string array`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-386

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_invalid_shapes[payload7-depends_on must be a string array]
```

- 確認内容: pytest case `task plan rejects invalid shapes[payload7-depends_on must be a string array]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`payload`, `message`, case=`payload7-depends_on must be a string array`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-387

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_rejects_unknown_dependencies
```

- 確認内容: pytest case `task plan rejects unknown dependencies` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:56`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-388

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_plan_accepts_valid_dependencies_and_parser_options
```

- 確認内容: pytest case `task plan accepts valid dependencies and parser options` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:67`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-389

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_task_runner_dry_run_writes_reports_and_artifact_index
```

- 確認内容: pytest case `task runner dry run writes reports and artifact index` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:106`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-390

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_defaults_auto_to_parallel_and_uses_agent_context
```

- 確認内容: pytest case `run defaults auto to parallel and uses agent context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:144`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-391

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_rejects_missing_work_dir_and_unsupported_mode
```

- 確認内容: pytest case `run rejects missing work dir and unsupported mode` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:198`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-392

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_one_task_records_failure_logs
```

- 確認内容: pytest case `run one task records failure logs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:235`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `task`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-393

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_one_task_skips_missing_command_and_rejects_missing_cwd
```

- 確認内容: pytest case `run one task skips missing command and rejects missing cwd` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:247`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-394

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_run_one_task_records_success_and_returncode_failure
```

- 確認内容: pytest case `run one task records success and returncode failure` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:271`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-395

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_sequential_stop_on_failure_blocks_remaining
```

- 確認内容: pytest case `sequential stop on failure blocks remaining` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:322`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-396

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_sequential_blocks_failed_dependency_and_detects_cycle
```

- 確認内容: pytest case `sequential blocks failed dependency and detects cycle` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:349`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-397

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_parallel_blocks_failed_dependency_and_stop_on_failure_pending
```

- 確認内容: pytest case `parallel blocks failed dependency and stop on failure pending` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:390`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-398

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_result_to_dict_and_write_reports_include_optional_fields
```

- 確認内容: pytest case `result to dict and write reports include optional fields` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:444`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `markdown`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-399

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_main_prints_json_and_reports_errors
```

- 確認内容: pytest case `main prints json and reports errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:474`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-400

- pytest node id:

```text
runtime/tests/test_retrieval_runtime.py::test_normalize_command_accepts_string_and_array
```

- 確認内容: pytest case `normalize command accepts string and array` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_retrieval_runtime.py:504`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### SCM Runtime

#### RT-UT-CASE-401

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_require_success_raises_with_stderr_detail
```

- 確認内容: pytest case `require success raises with stderr detail` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:31`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-402

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_github_token_git_env_sets_non_interactive_auth
```

- 確認内容: pytest case `github token git env sets non interactive auth` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:38`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-403

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_scm_utils_dry_run_posix_askpass_and_git_helpers
```

- 確認内容: pytest case `scm utils dry run posix askpass and git helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:47`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-404

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_scm_utils_posix_askpass_branch
```

- 確認内容: pytest case `scm utils posix askpass branch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:86`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `writes`, `chmods`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-405

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_repository_dry_run_writes_scm_state_and_manifest
```

- 確認内容: pytest case `prepare repository dry run writes scm state and manifest` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:125`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-406

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_repository_parser_main_script_and_missing_work
```

- 確認内容: pytest case `prepare repository parser main script and missing work` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:150`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-407

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_repository_uses_requirement_config_when_cli_repository_is_missing
```

- 確認内容: pytest case `prepare repository uses requirement config when cli repository is missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:227`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-408

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_repository_requires_repository_when_cli_and_requirements_are_empty
```

- 確認内容: pytest case `prepare repository requires repository when cli and requirements are empty` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:266`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-409

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_repository_rejects_existing_non_git_source_dir
```

- 確認内容: pytest case `prepare repository rejects existing non git source dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:284`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-410

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_repository_existing_git_repo_fetch_checkout_and_pull
```

- 確認内容: pytest case `prepare repository existing git repo fetch checkout and pull` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:304`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-411

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_repository_clone_repository_invokes_git_with_token_env
```

- 確認内容: pytest case `prepare repository clone repository invokes git with token env` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:343`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-412

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_repository_clone_dry_run_and_no_pull_branch
```

- 確認内容: pytest case `prepare repository clone dry run and no pull branch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:376`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-413

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_support_repository_dry_run_writes_state_report_and_artifacts
```

- 確認内容: pytest case `prepare support repository dry run writes state report and artifacts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:417`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `support_state`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-414

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_support_repository_replaces_existing_state_entry
```

- 確認内容: pytest case `prepare support repository replaces existing state entry` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:447`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `support_state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-415

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_support_repository_rejects_existing_non_git_source_dir
```

- 確認内容: pytest case `prepare support repository rejects existing non git source dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:482`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-416

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_support_repository_updates_existing_git_repo
```

- 確認内容: pytest case `prepare support repository updates existing git repo` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:502`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-417

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_prepare_support_repository_parser_clone_pull_main_and_script_paths
```

- 確認内容: pytest case `prepare support repository parser clone pull main and script paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:541`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`, `clone_calls`, `update_calls`, `update_args`, `dry_existing_args`, `missing_args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-418

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_dry_run_records_remote_branch_without_api
```

- 確認内容: pytest case `create issue branch dry run records remote branch without api` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:667`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-419

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_clone_issue_branch_uses_token_env
```

- 確認内容: pytest case `create issue branch clone issue branch uses token env` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:698`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-420

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_checkout_existing_repository_switches_existing_or_tracks_remote
```

- 確認内容: pytest case `create issue branch checkout existing repository switches existing or tracks remote` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:726`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-421

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_local_only_requires_source_repository
```

- 確認内容: pytest case `create issue branch local only requires source repository` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:763`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-422

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_local_only_switches_existing_branch
```

- 確認内容: pytest case `create issue branch local only switches existing branch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:784`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-423

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_defensive_specimen_create_issue_branch_local_only_dry_run_skips_switch
```

- 確認内容: defensive specimen create issue branch local only dry run skips switch を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:824`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-424

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_local_only_creates_missing_branch_and_script_load
```

- 確認内容: pytest case `create issue branch local only creates missing branch and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:824`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-425

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_remote_branch_ref_then_clone
```

- 確認内容: pytest case `create issue branch remote branch ref then clone` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:866`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `clone_calls`, `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-426

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_remote_dry_run_fills_repository_from_github_repo
```

- 確認内容: pytest case `create issue branch remote dry run fills repository from github repo` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:916`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-427

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_remote_linked_branch_checks_out_existing_source
```

- 確認内容: pytest case `create issue branch remote linked branch checks out existing source` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:940`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `checkout_calls`, `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-428

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_requires_github_repo_for_remote_creation
```

- 確認内容: pytest case `create issue branch requires github repo for remote creation` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:992`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-429

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_main_prints_json
```

- 確認内容: pytest case `create issue branch main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1013`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-430

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_dry_run_refuses_non_issue_branch
```

- 確認内容: pytest case `push branch dry run refuses non issue branch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1040`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-431

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_requires_existing_source_repository
```

- 確認内容: pytest case `push branch requires existing source repository` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1063`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-432

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_refuses_workflow_repository_itself
```

- 確認内容: pytest case `push branch refuses workflow repository itself` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1080`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-433

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_dry_run_writes_push_record_for_issue_branch
```

- 確認内容: pytest case `push branch dry run writes push record for issue branch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1097`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-434

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_uses_current_branch_when_state_has_no_working_branch
```

- 確認内容: pytest case `push branch uses current branch when state has no working branch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1125`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-435

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_non_dry_run_uses_token_env_and_set_upstream
```

- 確認内容: pytest case `push branch non dry run uses token env and set upstream` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1151`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-436

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_main_prints_json
```

- 確認内容: pytest case `push branch main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1186`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-437

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_rejects_non_semantic_message
```

- 確認内容: pytest case `commit changes rejects non semantic message` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1214`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-438

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_parser_main_script_and_plain_commit
```

- 確認内容: pytest case `commit changes parser main script and plain commit` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1232`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`, `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-439

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_dry_run_records_status_without_commit
```

- 確認内容: pytest case `commit changes dry run records status without commit` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1316`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-440

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_missing_source_dir_is_reported
```

- 確認内容: pytest case `commit changes missing source dir is reported` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1345`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-441

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_requires_changes_unless_allow_empty
```

- 確認内容: pytest case `commit changes requires changes unless allow empty` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1361`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-442

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_non_dry_run_allows_empty_and_configures_user
```

- 確認内容: pytest case `commit changes non dry run allows empty and configures user` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1387`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-443

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_requires_human_approval_for_initial_push
```

- 確認内容: pytest case `bootstrap repository requires human approval for initial push` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1426`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-444

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_rejects_non_semantic_message
```

- 確認内容: pytest case `bootstrap repository rejects non semantic message` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1446`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-445

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_parser_main_and_script_load
```

- 確認内容: pytest case `bootstrap repository parser main and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1465`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-446

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_requires_existing_work_directory
```

- 確認内容: pytest case `bootstrap repository requires existing work directory` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1532`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-447

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_dry_run_uses_scm_state_repository_and_writes_record
```

- 確認内容: pytest case `bootstrap repository dry run uses scm state repository and writes record` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1552`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-448

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_rejects_workflow_repo_as_source
```

- 確認内容: pytest case `bootstrap repository rejects workflow repo as source` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1584`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-449

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_requires_github_repo_when_state_is_empty
```

- 確認内容: pytest case `bootstrap repository requires github repo when state is empty` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1603`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-450

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_set_remote_adds_or_updates
```

- 確認内容: pytest case `bootstrap repository set remote adds or updates` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1622`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `get_url_returncode`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-451

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_non_dry_run_commits_and_pushes
```

- 確認内容: pytest case `bootstrap repository non dry run commits and pushes` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1651`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-452

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_non_dry_run_skips_commit_when_head_exists
```

- 確認内容: pytest case `bootstrap repository non dry run skips commit when head exists` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1708`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-453

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_non_dry_run_requires_files_when_no_head
```

- 確認内容: pytest case `bootstrap repository non dry run requires files when no head` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1752`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。


### Self-Improvement Workflow

#### RT-UT-CASE-454

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_parser_and_branch_name
```

- 確認内容: pytest case `parser and branch name` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:13`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-455

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_init_and_create_feedback
```

- 確認内容: pytest case `init and create feedback` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:24`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-456

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_review_feedback_updates_status_and_human_check
```

- 確認内容: pytest case `review feedback updates status and human check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:51`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-457

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_issue_body_requires_accepted_feedback_and_renders_fit_check
```

- 確認内容: pytest case `issue body requires accepted feedback and renders fit check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:77`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-458

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_evidence_scaffold_registers_artifact_index
```

- 確認内容: pytest case `evidence scaffold registers artifact index` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:148`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `data`, `manifest_data`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-459

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_main_prints_json
```

- 確認内容: pytest case `main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:160`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-460

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_workflow_skills_declare_feedback_output_contract
```

- 確認内容: pytest case `workflow skills declare feedback output contract` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:172`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `missing`, `text`, `required`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-461

- pytest node id:

```text
runtime/tests/test_self_improvement_workflow.py::test_workflow_help_declares_feedback_capture_for_all_commands
```

- 確認内容: pytest case `workflow help declares feedback capture for all commands` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_self_improvement_workflow.py:201`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `registry`, `missing`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### GUI / Web SVG Layout Modes

#### RT-UT-CASE-462

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_parse_model_render_and_validate_outputs
```

- 確認内容: pytest case `gui mode parse model render and validate outputs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:70`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-463

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_helpers_cover_prefix_discovery_claim_and_validation_errors
```

- 確認内容: pytest case `gui mode helpers cover prefix discovery claim and validation errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:99`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-464

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_renderers_and_failure_paths
```

- 確認内容: pytest case `gui mode renderers and failure paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:119`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-465

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_model_fallbacks_duplicate_ids_and_no_relationship_yaml
```

- 確認内容: pytest case `gui mode model fallbacks duplicate ids and no relationship yaml` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:147`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-466

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_input_init_inspect_and_claim_edge_paths
```

- 確認内容: pytest case `gui mode input init inspect and claim edge paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:196`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-467

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_validate_detects_policy_syntax_qtest_and_state_errors
```

- 確認内容: pytest case `gui mode validate detects policy syntax qtest and state errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:254`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-468

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_run_generate_complete_force_validation_error_and_self_test
```

- 確認内容: pytest case `gui mode run generate complete force validation error and self test` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:287`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-469

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_main_run_and_self_test_error_boundary
```

- 確認内容: pytest case `gui mode main run and self test error boundary` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:358`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-470

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_self_test_fails_if_existing_output_guard_does_not_raise
```

- 確認内容: pytest case `gui mode self test fails if existing output guard does not raise` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:398`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-471

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_gui_mode_run_generate_skips_when_no_svg_and_main_prints_json
```

- 確認内容: pytest case `gui mode run generate skips when no svg and main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:430`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-472

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_web_svg_mode_parse_model_render_and_validate_outputs
```

- 確認内容: pytest case `web svg mode parse model render and validate outputs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:467`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-473

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_web_svg_mode_helpers_cover_prefix_discovery_claim_and_modes
```

- 確認内容: pytest case `web svg mode helpers cover prefix discovery claim and modes` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:495`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-474

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_web_svg_mode_renderers_and_failure_paths
```

- 確認内容: pytest case `web svg mode renderers and failure paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:544`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-475

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_web_svg_mode_model_fallbacks_duplicate_ids_and_component_edges
```

- 確認内容: pytest case `web svg mode model fallbacks duplicate ids and component edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:574`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-476

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_web_svg_validate_detects_policy_react_playwright_and_state_errors
```

- 確認内容: pytest case `web svg validate detects policy react playwright and state errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:629`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-477

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_web_svg_init_input_and_resolvers
```

- 確認内容: pytest case `web svg init input and resolvers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:669`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-478

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_web_svg_run_generate_complete_force_and_validation_error
```

- 確認内容: pytest case `web svg run generate complete force and validation error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:688`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-479

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_web_svg_main_run_and_error_boundary
```

- 確認内容: pytest case `web svg main run and error boundary` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:763`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-480

- pytest node id:

```text
runtime/tests/test_svg_layout_modes.py::test_web_svg_run_generate_skips_when_no_svg_and_main_prints_json
```

- 確認内容: pytest case `web svg run generate skips when no svg and main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_svg_layout_modes.py:803`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### VSCode Environment Workflow

#### RT-UT-CASE-481

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_build_parser_parses_all_commands
```

- 確認内容: pytest case `vscode environment build parser parses all commands` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:17`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-482

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_init_work_writes_state_and_runtime_context
```

- 確認内容: pytest case `vscode environment init work writes state and runtime context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:28`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `state`, `runtime_context`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-483

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_draft_template_and_discovery
```

- 確認内容: pytest case `vscode environment draft template and discovery` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:64`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-484

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_open_questions_records_drafts
```

- 確認内容: pytest case `vscode environment open questions records drafts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:82`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `open_questions`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-485

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_rag_filename_and_template
```

- 確認内容: pytest case `vscode environment rag filename and template` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:101`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-486

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_write_rag_template_requires_repo_local_source_dir
```

- 確認内容: pytest case `vscode environment write rag template requires repo local source dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:121`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-487

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_requirements_and_validation_templates
```

- 確認内容: pytest case `vscode environment requirements and validation templates` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:153`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `requirements`, `validation_json`, `validation_md`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-488

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_validation_markdown_empty_lists
```

- 確認内容: pytest case `vscode environment validation markdown empty lists` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:176`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-489

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_main_dispatch_success_and_error
```

- 確認内容: pytest case `vscode environment main dispatch success and error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:189`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-490

- pytest node id:

```text
runtime/tests/test_vscode_environment_workflow.py::test_vscode_environment_main_dispatches_remaining_commands_and_script_load
```

- 確認内容: pytest case `vscode environment main dispatches remaining commands and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_environment_workflow.py:204`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `commands`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### VSCode Workspace

#### RT-UT-CASE-491

- pytest node id:

```text
runtime/tests/test_vscode_workspace.py::test_aiwfctl_path_shell_task_is_provisioned
```

- 確認内容: pytest case `aiwfctl path shell task is provisioned` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_workspace.py:17`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-492

- pytest node id:

```text
runtime/tests/test_vscode_workspace.py::test_aiwfctl_cmd_exposes_path_usage
```

- 確認内容: pytest case `aiwfctl cmd exposes path usage` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_vscode_workspace.py:27`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Workflow Doctor

#### RT-UT-CASE-493

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_run_git_allows_returncode_one_and_filters_blank_lines
```

- 確認内容: pytest case `run git allows returncode one and filters blank lines` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:11`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-494

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_run_git_raises_for_unexpected_returncode
```

- 確認内容: pytest case `run git raises for unexpected returncode` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:27`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-495

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_tracked_policy_violations_allows_only_readme_under_work_and_rag
```

- 確認内容: pytest case `tracked policy violations allows only readme under work and rag` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:41`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-496

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_missing_required_files_reports_core_runtime_assets
```

- 確認内容: pytest case `missing required files reports core runtime assets` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:59`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-497

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_human_gate_registry_flags_schema_responsibility_boundary
```

- 確認内容: pytest case `human gate registry flags schema responsibility boundary` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:77`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-498

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_human_gate_registry_findings_accepts_missing_or_valid_registry
```

- 確認内容: pytest case `human gate registry findings accepts missing or valid registry` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:89`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-499

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_close_archive_findings_reports_partial_archive
```

- 確認内容: pytest case `close archive findings reports partial archive` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:99`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-500

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_close_archive_findings_accepts_missing_root_and_complete_archive
```

- 確認内容: pytest case `close archive findings accepts missing root and complete archive` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:109`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-501

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_vscode_utf8_first_findings_accepts_complete_settings
```

- 確認内容: pytest case `vscode utf8 first findings accepts complete settings` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:123`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-502

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_vscode_utf8_first_findings_reports_missing_contract_parts
```

- 確認内容: pytest case `vscode utf8 first findings reports missing contract parts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:168`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-503

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_fail_on_warning_turns_warning_into_fail
```

- 確認内容: pytest case `workflow doctor fail on warning turns warning into fail` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:120`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-504

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_run_reports_all_warning_types
```

- 確認内容: pytest case `workflow doctor run reports all warning types` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:135`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-505

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_run_passes_without_warnings
```

- 確認内容: pytest case `workflow doctor run passes without warnings` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:160`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-506

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_main_prints_pass_json
```

- 確認内容: pytest case `workflow doctor main prints pass json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:173`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-507

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_main_returns_one_on_fail_on_warning
```

- 確認内容: pytest case `workflow doctor main returns one on fail on warning` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:187`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Uncategorized

#### RT-UT-CASE-508

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_ut_spec_sync_findings_and_skip
```

- 確認内容: pytest case `workflow doctor ut spec sync findings and skip` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:204`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

### Workflow State / Noise / Validation

#### RT-UT-CASE-509

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_reports_missing_ut_spec_inputs
```

- 確認内容: pytest case `defensive specimen workflow doctor reports missing ut spec inputs` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:239`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-510

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_reports_stale_and_bad_position_only
```

- 確認内容: pytest case `defensive specimen workflow doctor reports stale and bad position only` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:251`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-511

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_reports_stale_without_bad_position
```

- 確認内容: defensive specimen workflow doctor reports stale without bad position を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:277`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-512

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_accepts_clean_ut_spec_sync
```

- 確認内容: pytest case `defensive specimen workflow doctor accepts clean ut spec sync` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:277`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-513

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

#### RT-UT-CASE-514

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
  - specimen signals: defensive_specimen
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-515

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_workflow_state_rejects_invalid_status
```

- 確認内容: pytest case `workflow state rejects invalid status` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:39`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-516

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_workflow_state_run_show_reports_missing_state
```

- 確認内容: pytest case `workflow state run show reports missing state` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:50`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-517

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_workflow_state_run_set_updates_relative_work_dir
```

- 確認内容: pytest case `workflow state run set updates relative work dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:64`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-518

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_workflow_state_main_show_prints_json
```

- 確認内容: pytest case `workflow state main show prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:86`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-519

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_blocks_when_critical_items_are_missing
```

- 確認内容: pytest case `noise reduction blocks when critical items are missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:107`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-520

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_can_reach_warning_when_only_unknown_terms_remain
```

- 確認内容: pytest case `noise reduction can reach warning when only unknown terms remain` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:126`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-521

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_passes_and_uses_default_output_dir
```

- 確認内容: pytest case `noise reduction passes and uses default output dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:148`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `readiness`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-522

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_helpers_cover_duplicate_unknown_and_missing_draft
```

- 確認内容: pytest case `noise reduction helpers cover duplicate unknown and missing draft` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:175`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-523

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_noise_reduction_parser_main_and_script_load_paths
```

- 確認内容: pytest case `noise reduction parser main and script load paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:184`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-524

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_detects_english_dominant_markdown
```

- 確認内容: pytest case `validate output language detects english dominant markdown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:220`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-525

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_ignores_code_blocks_and_allowed_terms
```

- 確認内容: pytest case `validate output language ignores code blocks and allowed terms` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:236`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-526

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_iter_markdown_skips_missing_non_md_and_excluded_paths
```

- 確認内容: pytest case `validate output language iter markdown skips missing non md and excluded paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:261`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-527

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_strip_non_prose_removes_frontmatter_urls_tables_and_inline_code
```

- 確認内容: pytest case `validate output language strip non prose removes frontmatter urls tables and inline code` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:290`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-528

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_main_returns_zero_when_only_warnings
```

- 確認内容: pytest case `validate output language main returns zero when only warnings` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:315`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-529

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_main_fails_on_violation
```

- 確認内容: pytest case `validate output language main fails on violation` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:345`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-530

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_main_prints_absolute_external_path_and_script_load
```

- 確認内容: pytest case `validate output language main prints absolute external path and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:375`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-531

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_output_language_main_reports_ok_for_japanese_dominant
```

- 確認内容: pytest case `validate output language main reports ok for japanese dominant` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:408`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-532

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_vscode_workspace_accepts_utf8_sig_json
```

- 確認内容: pytest case `validate vscode workspace accepts utf8 sig json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:424`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-533

- pytest node id:

```text
runtime/tests/test_workflow_state_noise_validation.py::test_validate_vscode_workspace_rejects_invalid_json
```

- 確認内容: pytest case `validate vscode workspace rejects invalid json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_state_noise_validation.py:433`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

## 更新ルール

- この文書は `pytest --collect-only -q tests` の収集結果を正として更新します。
- 同期確認は `cd runtime && .\tools\uv.cmd run --project . --group dev python tools\pytest_ut_spec_sync.py --spec ..\docs\reference\runtime-pytest-ut\case-specification.md --runtime-root . check` で実行します。
- 入力値欄の再生成は `cd runtime && .\tools\uv.cmd run --project . --group dev python tools\pytest_ut_spec_sync.py --spec ..\docs\reference\runtime-pytest-ut\case-specification.md --runtime-root . fix-inputs` で実行します。
- テスト関数を追加、削除、renameした場合は、この533ケース仕様書も更新します。
- `pytest.mark.parametrize` によって1つのtest functionから複数caseが収集される場合は、pytest node idのparameter表記まで仕様として残します。
- 個別caseの詳細な入力値やfixtureは、該当pytest sourceを正とします。
