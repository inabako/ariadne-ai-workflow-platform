# test_preflight.py

このファイルは `runtime/tests/test_preflight.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 27 |

## ケース一覧

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
