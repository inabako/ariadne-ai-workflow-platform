# test_ctl_help.py

このファイルは `runtime/tests/test_ctl_help.py` の pytest node id 単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 36 |

## ケース一覧

#### RT-UT-CASE-CTL-001

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_parser_uses_aiwfctl_program_name
```

- 確認内容: `aiwfctl` のparserが外部公開名として `aiwfctl` を使うことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:17`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: parserのprogram nameが `aiwfctl` として扱われる。

#### RT-UT-CASE-CTL-002

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_without_modifier_warns_and_does_not_show_list
```

- 確認内容: ルートコマンドだけを実行した場合に、一覧を直接表示せず利用方法の警告へ誘導することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:25`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 警告と次に実行すべき `aiwfctl help` / `aiwfctl path shell` の導線が表示される。

#### RT-UT-CASE-CTL-003

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_without_modifier_warns_and_does_not_show_list
```

- 確認内容: `aiwfctl help` 単体実行時に、help subcommandの指定を促すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:38`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: help listを無条件表示せず、利用可能なhelp操作とPATH導線を返す。

#### RT-UT-CASE-CTL-004

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_warning_can_be_colored_yellow
```

- 確認内容: 警告表示が色付き出力設定に従ってyellow ANSI escapeを付与できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:50`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: color有効時はyellow装飾され、無効時は通常テキストになる。

#### RT-UT-CASE-CTL-005

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_knowledge_usage_and_search_export_context
```

- 確認内容: `aiwfctl knowledge` のusage、検索、context export routeが動作し、Context First manifestへ登録できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:61`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `manifest`
- 期待結果: knowledge系commandが期待する出力、context file、manifest登録を生成する。

#### RT-UT-CASE-CTL-006

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_github_knowledge_sync_apply_dry_run_updates_analysis
```

- 確認内容: `aiwfctl github-knowledge sync-apply` が承認済みGitHub sync actionをruntime経由でdry-runし、analysis JSONへ結果を戻すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:236`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `updated`
- 期待結果: pytest case pass。`execution_status: dry-run` が `github_sync_actions` に記録される。

#### RT-UT-CASE-CTL-006A

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_gui_mode_returns_windows_msys2_profile
```

- 確認内容: `gui-mode` の環境選択がWindows/MSYS2 GUI向けprofileへ解決されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:236`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: `gui-mode` が想定profile、required tools、preflight情報を返す。

#### RT-UT-CASE-CTL-007

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_web_svg_returns_wsl_web_profile
```

- 確認内容: `web-svg` の環境選択がWSL/Web向けprofileへ解決されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:249`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: `web-svg` が想定profileと環境選択情報を返す。

#### RT-UT-CASE-CTL-008

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_unknown_requires_human_check
```

- 確認内容: 未知のenvironment指定時にHuman Checkへ戻すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:262`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: unknown environmentとして候補提示またはHuman Check reasonを返す。

#### RT-UT-CASE-CTL-009

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_without_subcommand_shows_environment_management
```

- 確認内容: `aiwfctl env` 単体実行時にEnvironment Management usageを表示することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:279`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: env list / show / select / check の利用方法が表示される。

#### RT-UT-CASE-CTL-010

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_list_shows_public_environments_not_raw_profile_list
```

- 確認内容: `env list` が内部profileではなく利用者向けenvironment名を表示することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:292`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: public environment一覧が表示され、raw profile listに依存しない。

#### RT-UT-CASE-CTL-011

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_show_uses_public_environment_name
```

- 確認内容: `env show` がpublic environment名で詳細を表示することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:305`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: backend、purpose、required tools、docsなどのenvironment detailが表示される。

#### RT-UT-CASE-CTL-012

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_tool_name_requires_human_check_with_candidate
```

- 確認内容: tool名らしい入力をenvironmentとして指定した場合に候補付きHuman Checkへ戻すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:322`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 候補environmentとHuman Check reasonが表示される。

#### RT-UT-CASE-CTL-013

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_writes_workflow_context
```

- 確認内容: `env select --work-id` が `environment-selection.json` とcontext manifestを生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:334`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `data`, `manifest`
- 期待結果: work配下にenvironment-selection context、process report、context manifestが書き込まれる。

#### RT-UT-CASE-CTL-014

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_env_select_warns_before_overwriting_different_context
```

- 確認内容: 既存のenvironment-selection contextと異なる選択を書き込む前に警告を残すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:381`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `data`
- 期待結果: context差分のwarningが記録され、上書き前提が可視化される。

#### RT-UT-CASE-CTL-015

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_list_contains_workflow_commands
```

- 確認内容: `help list` がworkflow command一覧を表示することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:437`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 主要workflow commandが一覧に含まれる。

#### RT-UT-CASE-CTL-016

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_show_includes_arguments_and_details
```

- 確認内容: `help show` が対象workflowの引数、詳細、docsを表示することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:461`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: workflow helpのdetail、arguments、docsが表示される。

#### RT-UT-CASE-CTL-017

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_corrective_action_fix_help_declares_report_source
```

- 確認内容: `/corrective-action-fix` helpがreport sourceを明示することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:474`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: report sourceに関する説明がhelp outputに含まれる。

#### RT-UT-CASE-CTL-018

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_vscode_environment_help_declares_repo_local_tools_path
```

- 確認内容: `/vscode-environment` helpがrepo-local tools PATHの導線を明示することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:486`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: `aiwfctl path shell` などのPATH導線がhelpに含まれる。

#### RT-UT-CASE-CTL-019

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_realtime_iac_help_declares_docker_context_gate
```

- 確認内容: `/realtime-iac` helpがDocker environment context gateを明示することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:500`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: `aiwfctl env select docker` と environment-selection gate の説明が含まれる。

#### RT-UT-CASE-CTL-020

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ariadne_new_system_iac_help_declares_execution_plan_handoff
```

- 確認内容: `/ariadne-new-system-iac` helpがexecution plan handoffを明示することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:510`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: execution-plan handoffとRealtime IaCへの接続がhelpに含まれる。

#### RT-UT-CASE-CTL-021

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_context_init_creates_phase3_contexts
```

- 確認内容: `context init` がPhase 3向けの初期context群を生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:521`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: work配下に必要contextとmanifestが作成される。

#### RT-UT-CASE-CTL-022

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_doctor_runs_workflow_doctor
```

- 確認内容: `aiwfctl doctor` がworkflow_doctorへ委譲し、結果を整形することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:564`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: doctor結果がCLI outputとexit codeに反映される。

#### RT-UT-CASE-CTL-023

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_defensive_specimen_ctl_doctor_formats_warning_paths
```

- 確認内容: doctor warningのpath表示が見やすく整形されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:592`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: warning pathがCLIで確認しやすい形に整形される。

#### RT-UT-CASE-CTL-024

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_search_finds_svg_gui_workflows
```

- 確認内容: `help search` がSVG/GUI関連workflowを検索できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:628`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: SVG/GUIに関連するworkflow候補が検索結果に含まれる。

#### RT-UT-CASE-CTL-025

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_show_includes_svg_extension_details
```

- 確認内容: SVG extensionのhelp detailが表示されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:643`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: SVG extensionの目的、docs、関連commandが表示される。

#### RT-UT-CASE-CTL-026

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_show_includes_mcp_group_extension_details
```

- 確認内容: MCP group extensionのhelp detailが表示されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:658`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: MCP group extensionの目的、docs、関連commandが表示される。

#### RT-UT-CASE-CTL-027

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_markdown_writes_searchable_file
```

- 確認内容: `help markdown` が検索可能なMarkdownファイルを生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:671`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `text`
- 期待結果: workflow helpのMarkdown出力が生成され、検索語を含む。

#### RT-UT-CASE-CTL-028

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_workflow_help_registry_referenced_files_exist
```

- 確認内容: workflow help registryが参照するdocsやskill fileが存在することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:695`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: registry内の参照pathが欠落していない。

#### RT-UT-CASE-CTL-029

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_workflow_help_search_uses_intent_terms
```

- 確認内容: workflow help searchが明示的なintent/search termsを使って候補を返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:717`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 検索語に対応するworkflow候補が返る。

#### RT-UT-CASE-CTL-030

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_environment_profile_registry_referenced_docs_exist
```

- 確認内容: environment profile registryが参照するdocsが存在することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:736`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: profile docs referenceに欠落がない。

#### RT-UT-CASE-CTL-031

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_registry_and_search_helper_edge_cases
```

- 確認内容: registry読み込み、検索helper、未知command処理などの境界条件を確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:758`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: 空/未知/候補ありの検索境界が期待どおり処理される。

#### RT-UT-CASE-CTL-032

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_environment_selection_mapping_branches
```

- 確認内容: environment selection mappingの分岐を確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:799`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `registry`
- 期待結果: explicit mapping、keyword mapping、複数候補、未知入力が期待どおり分類される。

#### RT-UT-CASE-CTL-033

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_environment_formatting_and_context_warning_helpers
```

- 確認内容: environment selectionの表示整形とcontext warning helperを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:838`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `profile`, `context`, `record`, `registry`
- 期待結果: environment detail、Human Check表示、context warningが期待どおり整形される。

#### RT-UT-CASE-CTL-034

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_help_formatting_empty_lists_and_open_search_paths
```

- 確認内容: help formattingの空list境界とopen/search pathを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:972`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `registry`, `open_args`, `markdown_args`, `search_args`
- 期待結果: 空listや未検索時でもCLI outputが崩れず、open/search結果が扱える。

#### RT-UT-CASE-CTL-035

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_color_mode_and_main_output
```

- 確認内容: `AIWFCTL_COLOR` とmain outputの分岐を確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:1018`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: color modeとmain outputが設定に従って切り替わる。

#### RT-UT-CASE-CTL-036

- pytest node id:

```text
runtime/tests/test_ctl_help.py::test_ctl_run_manual_error_and_json_branches
```

- 確認内容: `ctl.run` のmanual error branchとJSON output branchを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_ctl_help.py:1044`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: error時のexit codeとmessage、JSON出力分岐が期待どおり返る。
