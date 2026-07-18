# test_workflow_doctor.py

このファイルは `runtime/tests/test_workflow_doctor.py` の pytest node id 単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 29 |

## ケース一覧

#### RT-UT-CASE-DOCTOR-001

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_run_git_allows_returncode_one_and_filters_blank_lines
```

- 確認内容: git command helperがreturncode 1を許容し、空行を除外することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:11`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 許容returncodeの結果が例外にならず、空行除外後の行リストを返す。

#### RT-UT-CASE-DOCTOR-002

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_run_git_raises_for_unexpected_returncode
```

- 確認内容: 想定外returncodeのgit commandでエラーを返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:27`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 想定外returncodeがRuntimeErrorとして扱われる。

#### RT-UT-CASE-DOCTOR-003

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_tracked_policy_violations_allows_work_readme_but_blocks_rag_files
```

- 確認内容: tracked policyが許可されるwork READMEと禁止されるRAG fileを区別することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:41`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 許可対象はwarningにならず、禁止対象はpolicy violationとして報告される。

#### RT-UT-CASE-DOCTOR-004

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_missing_required_files_reports_core_runtime_assets
```

- 確認内容: core runtime assetの欠落をdoctorが報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:59`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: required file欠落がwarningとして列挙される。

#### RT-UT-CASE-DOCTOR-PYTEST-RUNTIME-BOUNDARY

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_pytest_runtime_boundary_findings_blocks_root_config_and_cache
```

- 確認内容: root `pytest.ini` / `.pytest_cache` を workflow noise として検出し、pytest 生成物を runtime 配下へ閉じ込めることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: root pytest config/cache and runtime pytest config/cache
- 期待結果: root 生成物は warning path として報告され、runtime-local pytest 境界が守られる。

#### RT-UT-CASE-DOCTOR-005

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_human_gate_registry_flags_schema_responsibility_boundary
```

- 確認内容: human gate registryのschema responsibility boundary違反を検出することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:80`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: schema/責務境界の不整合がwarningとして報告される。

#### RT-UT-CASE-DOCTOR-006

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_human_gate_registry_findings_accepts_missing_or_valid_registry
```

- 確認内容: human gate registryが未配置またはvalidな場合の扱いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:92`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 未配置またはvalid registryは不要なwarningを出さない。

#### RT-UT-CASE-DOCTOR-007

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_close_archive_findings_reports_partial_archive
```

- 確認内容: close archiveが部分的な状態の場合にdoctorが報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:102`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 不完全なarchive状態がwarningとして検出される。

#### RT-UT-CASE-DOCTOR-008

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_close_archive_findings_accepts_missing_root_and_complete_archive
```

- 確認内容: close archive root未配置または完全archiveを許容することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:112`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 問題のないarchive状態ではwarningが発生しない。

#### RT-UT-CASE-DOCTOR-009

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_vscode_utf8_first_findings_accepts_complete_settings
```

- 確認内容: VSCode UTF-8 first設定が完全な場合にdoctorが受け入れることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:123`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: UTF-8 first contractが揃っている場合はwarningが出ない。

#### RT-UT-CASE-DOCTOR-010

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_vscode_utf8_first_findings_reports_missing_contract_parts
```

- 確認内容: VSCode UTF-8 first contractの欠落部分を報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:168`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 不足しているUTF-8 contract要素がwarningとして列挙される。

#### RT-UT-CASE-DOCTOR-011

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_vscode_utf8_first_findings_reports_missing_or_invalid_settings
```

- 確認内容: VSCode settingsが未配置またはinvalid JSONの場合に報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:197`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: settings欠落またはinvalid JSONがwarningになる。

#### RT-UT-CASE-DOCTOR-012

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_vscode_utf8_first_findings_reports_wrong_terminal_shapes_and_editorconfig_snippets
```

- 確認内容: terminal profile形状やeditorconfig snippetの誤りを報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:212`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: UTF-8 firstに必要なterminal/editorconfig設定の不足が検出される。

#### RT-UT-CASE-DOCTOR-013

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_vscode_utf8_first_findings_ignores_non_powershell_profiles
```

- 確認内容: PowerShell以外のterminal profileをUTF-8 first検査対象から除外することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:238`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 対象外profileによる不要なwarningが発生しない。

#### RT-UT-CASE-DOCTOR-014

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_duckdb_read_model_findings_reports_missing_read_model_when_sources_exist
```

- 確認内容: source artifactがあるのにDuckDB read modelがない場合に報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:275`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: read model未生成がwarningとして報告される。

#### RT-UT-CASE-DOCTOR-015

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_duckdb_read_model_findings_accepts_missing_sources_or_existing_db
```

- 確認内容: sourceがない場合や既存DuckDBがある場合を許容することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:290`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: read model上の問題がない場合はwarningが発生しない。

#### RT-UT-CASE-DOCTOR-016

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workspace_layout_literal_findings_reports_runtime_path_joins
```

- 確認内容: workspace layout literal guardがruntime内の直接的なpath joinを報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:307`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: work / context / source repositoryを直書きした一時runtime file
- 期待結果: hard-coded workspace layout literalがhelper hint付きで報告される。
#### RT-UT-CASE-DOCTOR-017

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workspace_layout_literal_findings_ignores_constants_and_tests
```

- 確認内容: workspace layout literal guardがconstantsとtestsを検知対象外にすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:329`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: constants / tests / helper runtimeの一時file
- 期待結果: 許可されたhelper配置ではworkspace-layout-literal warningが発生しない。
#### RT-UT-CASE-DOCTOR-018

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_path_constant_literal_findings_reports_runtime_path_constants
```

- 確認内容: canonical path literal guardがruntime内のRAG / DB / schema系直書きpathを報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:348`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: RAG / DB / knowledge source / schemaを直書きした一時runtime file
- 期待結果: hard-coded canonical path literalがconstants hint付きで報告される。
#### RT-UT-CASE-DOCTOR-019

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_path_constant_literal_findings_ignores_constants_and_tests
```

- 確認内容: canonical path literal guardがconstantsとtestsを検知対象外にすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:371`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: constants / tests / helper runtimeの一時file
- 期待結果: 許可されたconstants / tests配置ではpath-constant-literal warningが発生しない。

#### RT-UT-CASE-DOCTOR-020

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_fail_on_warning_turns_warning_into_fail
```

- 確認内容: `--fail-on-warning` 相当の設定でwarningをfail扱いにすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:307`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: warningがある場合にdoctor statusがfailへ変換される。

#### RT-UT-CASE-DOCTOR-021

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_run_reports_all_warning_types
```

- 確認内容: workflow_doctor runが全warning種別をまとめて報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:324`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: policy、required files、archive、UTF-8、DuckDBなどのwarningが集約される。

#### RT-UT-CASE-DOCTOR-022

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_run_passes_without_warnings
```

- 確認内容: warningがない場合にworkflow_doctorがpassすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:357`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: statusがpassになり、warning_countが0になる。

#### RT-UT-CASE-DOCTOR-TEXT-BOUNDARY-001

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_text_boundary_scan_and_repair_recovers_utf8_saved_mojibake
```

- 確認内容: UTF-8として保存された文字化け行を text-boundary repair が復元できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: mojibake marker を含む Markdown file
- 期待結果: repair 後に remaining findings が空になり、`.encoding-bak` backup が作成される。

#### RT-UT-CASE-DOCTOR-TEXT-BOUNDARY-002

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_repair_encoding_clears_text_boundary_warning
```

- 確認内容: doctor gate が text-boundary warning で停止し、`--repair-encoding` 後に同じ doctor gate から pass へ復帰することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `repair_encoding=False` then `repair_encoding=True`
- 期待結果: repair 後の `gate_restart` は `restart_from=doctor-gate` と `next_on_pass=return-to-calling-workflow-after-gate` を返す。

#### RT-UT-CASE-DOCTOR-023

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_main_prints_pass_json
```

- 確認内容: workflow_doctor CLI mainがpass JSONを出力することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:372`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: mainがJSONをstdoutへ出力し、成功exit codeを返す。

#### RT-UT-CASE-DOCTOR-024

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_main_returns_one_on_fail_on_warning
```

- 確認内容: fail-on-warning時にCLI mainが非ゼロ終了することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:388`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: fail-on-warning指定時にexit code 1が返る。

#### RT-UT-CASE-DOCTOR-025

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_ut_spec_sync_findings_and_skip
```

- 確認内容: UT spec sync findingsとskip optionの扱いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:407`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: sync不整合がwarningになり、skip指定時は検査を省略できる。

#### RT-UT-CASE-DOCTOR-026

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_reports_missing_ut_spec_inputs
```

- 確認内容: UT spec input section欠落をdoctorが報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:441`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 入力値欄欠落がdoctor warningとして出る。

#### RT-UT-CASE-DOCTOR-027

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_reports_stale_and_bad_position_only
```

- 確認内容: stale caseとbad input positionだけがあるsync結果をdoctorが報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:453`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: stale nodeとbad input positionがwarningに反映される。

#### RT-UT-CASE-DOCTOR-028

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_reports_stale_without_bad_position
```

- 確認内容: stale caseのみのsync結果をdoctorが報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:479`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: stale nodeだけがwarningとして報告される。

#### RT-UT-CASE-DOCTOR-029

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_accepts_clean_ut_spec_sync
```

- 確認内容: cleanなUT spec sync結果をdoctorが受け入れることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:500`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: missing/stale/bad positionがない場合、UT spec sync warningは発生しない。
