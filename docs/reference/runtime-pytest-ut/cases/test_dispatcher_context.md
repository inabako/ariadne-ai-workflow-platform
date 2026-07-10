# test_dispatcher_context.py

このファイルは `runtime/tests/test_dispatcher_context.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 12 |

## ケース一覧

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
