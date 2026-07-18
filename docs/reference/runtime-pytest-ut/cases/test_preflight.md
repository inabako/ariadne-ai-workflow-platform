# test_preflight.py

このファイルは `runtime/tests/test_preflight.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 28 |

## ケース一覧

#### RT-UT-CASE-225

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

#### RT-UT-CASE-226

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

#### RT-UT-CASE-227

- pytest node id:

```text
runtime/tests/test_preflight.py::test_env_path_check_reads_repo_env
```

- 確認内容: pytest case `env path check reads repo env` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:77`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `AIWF_TERRAFORM_EXE` がrepo `.env` から読み込まれ、存在する実行ファイルpathとして検出される。

#### RT-UT-CASE-227A

- pytest node id:

```text
runtime/tests/test_preflight.py::test_python_module_check_uses_current_interpreter
```

- 確認内容: pytest case `python module check uses current interpreter` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:94`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-228

- pytest node id:

```text
runtime/tests/test_preflight.py::test_docker_compose_check_uses_compose_version
```

- 確認内容: pytest case `docker compose check uses compose version` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:110`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-229

- pytest node id:

```text
runtime/tests/test_preflight.py::test_docker_compose_check_reports_compose_error
```

- 確認内容: pytest case `docker compose check reports compose error` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:125`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-230A

- pytest node id:

```text
runtime/tests/test_preflight.py::test_github_cli_checks_split_version_auth_and_env_token
```

- 確認内容: GitHub CLI preflight が `gh --version`、`gh auth status`、GitHub token ENV availabilityを別checkとして扱い、未認証時に `auth-required` と ENV login actionを返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:139`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: `gh --version` と `gh auth status` が別commandとして実行され、token値は `configured (masked)` として扱われ、auth checkには `--gh-login-from-env` actionが記録される。

#### RT-UT-CASE-230B

- pytest node id:

```text
runtime/tests/test_preflight.py::test_gh_login_from_env_uses_token_stdin_and_sanitizes_report
```

- 確認内容: ENV token login runtime が tokenをstdinで `gh auth login --with-token` に渡し、実行reportにtoken値を出力しないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:183`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `commands`
- 期待結果: `gh auth login --hostname github.com --with-token` と `gh auth setup-git --hostname github.com` が実行され、execution JSONにtoken値が含まれない。

#### RT-UT-CASE-230C

- pytest node id:

```text
runtime/tests/test_preflight.py::test_main_gh_login_from_env_requires_human_approval
```

- 確認内容: `--gh-login-from-env` が credential設定を伴うため、`--human-check approved` なしでは実行されないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:210`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: return code 1となり、stderrに `--gh-login-from-env requires --human-check approved` が出力される。

#### RT-UT-CASE-230

- pytest node id:

```text
runtime/tests/test_preflight.py::test_localty_protocol_check_uses_msys2_python_when_available
```

- 確認内容: pytest case `localty protocol check uses msys2 python when available` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:246`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-231

- pytest node id:

```text
runtime/tests/test_preflight.py::test_localty_protocol_check_uses_fallback_repository
```

- 確認内容: pytest case `localty protocol check uses fallback repository` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:267`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-232

- pytest node id:

```text
runtime/tests/test_preflight.py::test_localty_protocol_check_reports_missing_without_work_id
```

- 確認内容: pytest case `localty protocol check reports missing without work id` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:286`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-233

- pytest node id:

```text
runtime/tests/test_preflight.py::test_localty_protocol_check_reports_missing_with_fallback_command
```

- 確認内容: pytest case `localty protocol check reports missing with fallback command` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:302`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-234

- pytest node id:

```text
runtime/tests/test_preflight.py::test_msys2_package_check_missing_bash_and_success
```

- 確認内容: pytest case `msys2 package check missing bash and success` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:321`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-235

- pytest node id:

```text
runtime/tests/test_preflight.py::test_docker_compose_profile_declares_required_docker_checks
```

- 確認内容: pytest case `docker compose profile declares required docker checks` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:341`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-236

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_profiles_add_expected_checks[corrective-action-fix-expected_ids0]
```

- 確認内容: pytest case `build checks profiles add expected checks[corrective-action-fix-expected_ids0]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:379`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`corrective-action-fix-expected_ids0`
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-237

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_profiles_add_expected_checks[web-nextjs-expected_ids1]
```

- 確認内容: pytest case `build checks profiles add expected checks[web-nextjs-expected_ids1]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:379`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`web-nextjs-expected_ids1`
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-238

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_profiles_add_expected_checks[vscode-environment-expected_ids2]
```

- 確認内容: pytest case `build checks profiles add expected checks[vscode-environment-expected_ids2]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:379`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`vscode-environment-expected_ids2`
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-239

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_localty_gui_and_profiles_without_source_dir
```

- 確認内容: pytest case `build checks localty gui and profiles without source dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:407`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `gui_args`, `localty_args`, `vscode_args`, `web_args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-240

- pytest node id:

```text
runtime/tests/test_preflight.py::test_install_requires_human_approval_before_running_commands
```

- 確認内容: pytest case `install requires human approval before running commands` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:455`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-241

- pytest node id:

```text
runtime/tests/test_preflight.py::test_install_missing_runs_required_commands_and_fallback
```

- 確認内容: pytest case `install missing runs required commands and fallback` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:467`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `checks`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-242

- pytest node id:

```text
runtime/tests/test_preflight.py::test_install_missing_breaks_without_fallback_or_when_fallback_fails
```

- 確認内容: pytest case `install missing breaks without fallback or when fallback fails` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:505`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `checks`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-243

- pytest node id:

```text
runtime/tests/test_preflight.py::test_install_missing_runs_msys2_package_with_bash
```

- 確認内容: pytest case `install missing runs msys2 package with bash` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:559`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-244

- pytest node id:

```text
runtime/tests/test_preflight.py::test_markdown_report_includes_fallback_command
```

- 確認内容: pytest case `markdown report includes fallback command` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:584`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-245

- pytest node id:

```text
runtime/tests/test_preflight.py::test_markdown_report_includes_missing_optional_items
```

- 確認内容: pytest case `markdown report includes missing optional items` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:612`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-246

- pytest node id:

```text
runtime/tests/test_preflight.py::test_markdown_report_iterates_multiple_required_missing_items
```

- 確認内容: pytest case `markdown report iterates multiple required missing items` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:647`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-247

- pytest node id:

```text
runtime/tests/test_preflight.py::test_markdown_report_reports_none_when_all_checks_ready
```

- 確認内容: pytest case `markdown report reports none when all checks ready` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:682`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-248

- pytest node id:

```text
runtime/tests/test_preflight.py::test_write_reports_creates_json_and_markdown
```

- 確認内容: pytest case `write reports creates json and markdown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:707`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `result`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-249

- pytest node id:

```text
runtime/tests/test_preflight.py::test_main_writes_report_and_returns_ready
```

- 確認内容: pytest case `main writes report and returns ready` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:723`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-250

- pytest node id:

```text
runtime/tests/test_preflight.py::test_main_returns_two_when_required_check_missing
```

- 確認内容: pytest case `main returns two when required check missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:749`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-251

- pytest node id:

```text
runtime/tests/test_preflight.py::test_main_runs_install_after_human_approval_and_module_script_load
```

- 確認内容: pytest case `main runs install after human approval and module script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:775`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
