# test_context_first.py

このファイルは `runtime/tests/test_context_first.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 34 |

## ケース一覧

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
  - source: `runtime/tests/test_context_first.py:78`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-030

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_loads_test_evidence_context
```

- 確認内容: pytest case `context first loads test evidence context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:105`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-031

- pytest node id:

```text
runtime/tests/test_context_first.py::test_context_first_parser_show_and_main_status_paths
```

- 確認内容: pytest case `context first parser show and main status paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_context_first.py:130`
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
  - source: `runtime/tests/test_context_first.py:187`
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
  - source: `runtime/tests/test_context_first.py:218`
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
  - source: `runtime/tests/test_context_first.py:244`
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
  - source: `runtime/tests/test_context_first.py:250`
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
  - source: `runtime/tests/test_context_first.py:282`
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
  - source: `runtime/tests/test_context_first.py:303`
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
  - source: `runtime/tests/test_context_first.py:324`
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
  - source: `runtime/tests/test_context_first.py:346`
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
  - source: `runtime/tests/test_context_first.py:382`
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
  - source: `runtime/tests/test_context_first.py:418`
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
  - source: `runtime/tests/test_context_first.py:443`
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
  - source: `runtime/tests/test_context_first.py:470`
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
  - source: `runtime/tests/test_context_first.py:502`
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
  - source: `runtime/tests/test_context_first.py:555`
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
  - source: `runtime/tests/test_context_first.py:585`
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
  - source: `runtime/tests/test_context_first.py:611`
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
  - source: `runtime/tests/test_context_first.py:659`
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
  - source: `runtime/tests/test_context_first.py:690`
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
  - source: `runtime/tests/test_context_first.py:748`
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
  - source: `runtime/tests/test_context_first.py:832`
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
  - source: `runtime/tests/test_context_first.py:902`
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
  - source: `runtime/tests/test_context_first.py:947`
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
  - source: `runtime/tests/test_context_first.py:999`
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
  - source: `runtime/tests/test_context_first.py:1040`
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
  - source: `runtime/tests/test_context_first.py:1074`
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
  - source: `runtime/tests/test_context_first.py:1100`
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
  - source: `runtime/tests/test_context_first.py:1126`
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
  - source: `runtime/tests/test_context_first.py:1164`
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
  - source: `runtime/tests/test_context_first.py:1209`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
