# test_workflow_doctor.py

このファイルは `runtime/tests/test_workflow_doctor.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 20 |

## ケース一覧

#### RT-UT-CASE-505

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

#### RT-UT-CASE-506

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

#### RT-UT-CASE-507

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

#### RT-UT-CASE-508

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

#### RT-UT-CASE-509

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_human_gate_registry_flags_schema_responsibility_boundary
```

- 確認内容: pytest case `human gate registry flags schema responsibility boundary` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:80`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-510

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_human_gate_registry_findings_accepts_missing_or_valid_registry
```

- 確認内容: pytest case `human gate registry findings accepts missing or valid registry` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:92`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-511

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_close_archive_findings_reports_partial_archive
```

- 確認内容: pytest case `close archive findings reports partial archive` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:102`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-512

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_close_archive_findings_accepts_missing_root_and_complete_archive
```

- 確認内容: pytest case `close archive findings accepts missing root and complete archive` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:112`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-513

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

#### RT-UT-CASE-514

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

#### RT-UT-CASE-515

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_fail_on_warning_turns_warning_into_fail
```

- 確認内容: pytest case `workflow doctor fail on warning turns warning into fail` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:197`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-516

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_run_reports_all_warning_types
```

- 確認内容: pytest case `workflow doctor run reports all warning types` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:213`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-517

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_run_passes_without_warnings
```

- 確認内容: pytest case `workflow doctor run passes without warnings` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:240`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-518

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_main_prints_pass_json
```

- 確認内容: pytest case `workflow doctor main prints pass json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:254`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-519

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_main_returns_one_on_fail_on_warning
```

- 確認内容: pytest case `workflow doctor main returns one on fail on warning` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:269`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-520

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_workflow_doctor_ut_spec_sync_findings_and_skip
```

- 確認内容: pytest case `workflow doctor ut spec sync findings and skip` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:287`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-521

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_reports_missing_ut_spec_inputs
```

- 確認内容: pytest case `defensive specimen workflow doctor reports missing ut spec inputs` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:320`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-522

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_reports_stale_and_bad_position_only
```

- 確認内容: pytest case `defensive specimen workflow doctor reports stale and bad position only` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:332`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.

#### RT-UT-CASE-523

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_reports_stale_without_bad_position
```

- 確認内容: defensive specimen workflow doctor reports stale without bad position を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:358`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-524

- pytest node id:

```text
runtime/tests/test_workflow_doctor.py::test_defensive_specimen_workflow_doctor_accepts_clean_ut_spec_sync
```

- 確認内容: pytest case `defensive specimen workflow doctor accepts clean ut spec sync` records defensive specimen for runtime observability, doctor, UT spec sync, CLI output, or error boundary behavior.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_workflow_doctor.py:379`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: case passes and the unusual or defensive runtime path remains documented as an intentional specimen.
