# test_ctl_help.py

このファイルは `runtime/tests/test_ctl_help.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 34 |

## ケース一覧

#### RT-UT-CASE-073

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_parser_uses_aiwfctl_program_name
```

- 確認内容: pytest case `ctl parser uses aiwfctl program name` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:17`
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
  - source: `runtime/tests/test_ctl_help.py:25`
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
  - source: `runtime/tests/test_ctl_help.py:38`
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
  - source: `runtime/tests/test_ctl_help.py:50`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-077

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_knowledge_usage_and_search_export_context
```

- 確認内容: pytest case `ctl knowledge usage and search export context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:61`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
#### RT-UT-CASE-078

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_gui_mode_returns_windows_msys2_profile
```

- 確認内容: pytest case `ctl env select gui mode returns windows msys2 profile` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:237`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-079

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_web_svg_returns_wsl_web_profile
```

- 確認内容: pytest case `ctl env select web svg returns wsl web profile` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:250`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-080

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_unknown_requires_human_check
```

- 確認内容: pytest case `ctl env select unknown requires human check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:263`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-081

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_without_subcommand_shows_environment_management
```

- 確認内容: pytest case `ctl env without subcommand shows environment management` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:280`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-082

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_list_shows_public_environments_not_raw_profile_list
```

- 確認内容: pytest case `ctl env list shows public environments not raw profile list` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:293`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-083

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_show_uses_public_environment_name
```

- 確認内容: pytest case `ctl env show uses public environment name` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:306`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-084

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_tool_name_requires_human_check_with_candidate
```

- 確認内容: pytest case `ctl env select tool name requires human check with candidate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:323`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-085

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_writes_workflow_context
```

- 確認内容: pytest case `ctl env select writes workflow context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:335`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `data`, `manifest`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-086

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_warns_before_overwriting_different_context
```

- 確認内容: pytest case `ctl env select warns before overwriting different context` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:382`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `data`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-087

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_list_contains_workflow_commands
```

- 確認内容: pytest case `ctl help list contains workflow commands` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:438`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-088

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_show_includes_arguments_and_details
```

- 確認内容: pytest case `ctl help show includes arguments and details` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:460`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-089

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_corrective_action_fix_help_declares_report_source
```

- 確認内容: pytest case `corrective action fix help declares report source` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:473`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-090

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_vscode_environment_help_declares_repo_local_tools_path
```

- 確認内容: pytest case `vscode environment help declares repo local tools path` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:485`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-091

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_realtime_iac_help_declares_docker_context_gate
```

- 確認内容: pytest case `realtime iac help declares docker context gate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:499`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-092

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_robotics_new_system_iac_help_declares_execution_plan_handoff
```

- 確認内容: pytest case `robotics new system iac help declares execution plan handoff` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:509`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-093

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_context_init_creates_phase3_contexts
```

- 確認内容: pytest case `ctl context init creates phase3 contexts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:520`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-094

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_doctor_runs_workflow_doctor
```

- 確認内容: pytest case `ctl doctor runs workflow doctor` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:563`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-095

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_defensive_specimen_ctl_doctor_formats_warning_paths
```

- 確認内容: pytest case `defensive specimen ctl doctor formats warning paths` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:591`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-096

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_search_finds_svg_gui_workflows
```

- 確認内容: pytest case `ctl help search finds svg gui workflows` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:627`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-097

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_show_includes_svg_extension_details
```

- 確認内容: pytest case `ctl help show includes svg extension details` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:638`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-098

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_markdown_writes_searchable_file
```

- 確認内容: pytest case `ctl help markdown writes searchable file` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:653`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `text`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-099

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_workflow_help_registry_referenced_files_exist
```

- 確認内容: pytest case `workflow help registry referenced files exist` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:677`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-100

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_environment_profile_registry_referenced_docs_exist
```

- 確認内容: pytest case `environment profile registry referenced docs exist` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:699`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-101

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_registry_and_search_helper_edge_cases
```

- 確認内容: pytest case `ctl registry and search helper edge cases` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:721`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-102

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_environment_selection_mapping_branches
```

- 確認内容: pytest case `ctl environment selection mapping branches` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:762`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-103

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_environment_formatting_and_context_warning_helpers
```

- 確認内容: pytest case `ctl environment formatting and context warning helpers` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:801`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `profile`, `context`, `record`, `registry`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-104

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_formatting_empty_lists_and_open_search_paths
```

- 確認内容: pytest case `ctl help formatting empty lists and open search paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:935`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `registry`, `open_args`, `markdown_args`, `search_args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-105

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_color_mode_and_main_output
```

- 確認内容: pytest case `ctl color mode and main output` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:981`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-106

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_run_manual_error_and_json_branches
```

- 確認内容: pytest case `ctl run manual error and json branches` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:1007`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
