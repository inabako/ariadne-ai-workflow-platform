# test_preflight.py

このファイルは `runtime/tests/test_preflight.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 36 |

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
runtime/tests/test_preflight.py::test_preflight_parser_accepts_runtime_dev_profile
```
- Confirm: Placeholder; regenerated input details are maintained by pytest_ut_spec_sync.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:77`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `args`
- Expected: Placeholder; pytest assertion defines the expected result.


- 遒ｺ隱榊・螳ｹ: preflight parser縺・`runtime-dev` profile繧貞女縺大叙繧後ｋ縺薙→繧堤｢ｺ隱阪＠縺ｾ縺吶・
- 蜈･蜉帛､:
  - pytest node: 荳願ｨ倥さ繝ｼ繝峨ヶ繝ｭ繝・け縺ｮnode id
  - source: `runtime/tests/test_preflight.py`
  - fixture/arg: 縺ｪ縺・
  - parameter: names=縺ｪ縺・ case=縺ｪ縺・
  - inline input: test髢｢謨ｰ蜀・〒逕滓・縺輔ｌ繧句崋螳壼・蜉帙・
- 譛溷ｾ・ｵ先棡: `--profile runtime-dev` 縺後ヱ繝ｼ繧ｹ縺輔ｌ繧九・

#### RT-UT-CASE-227A

- pytest node id:

```text
runtime/tests/test_preflight.py::test_uv_runtime_check_uses_repo_local_wrapper_when_uv_is_not_on_path
```
- Confirm: Placeholder; regenerated input details are maintained by pytest_ut_spec_sync.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:128`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- Expected: Placeholder; pytest assertion defines the expected result.


- 遒ｺ隱榊・螳ｹ: PATH荳翫↓uv縺後↑縺・ｴ蜷医〒繧・repo-local `runtime/windows-script/uv.cmd` 繧呈､懷・縺ｧ縺阪ｋ縺薙→繧堤｢ｺ隱阪＠縺ｾ縺吶・
- 蜈･蜉帛､:
  - pytest node: 荳願ｨ倥さ繝ｼ繝峨ヶ繝ｭ繝・け縺ｮnode id
  - source: `runtime/tests/test_preflight.py`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=縺ｪ縺・ case=縺ｪ縺・
  - inline input: test髢｢謨ｰ蜀・〒逕滓・縺輔ｌ繧句崋螳壼・蜉帙・
- 譛溷ｾ・ｵ先棡: `exe:uv` check縺後Ξ繝昴・繝医Μwrapper繧呈､懷・縺吶ｋ縲・

#### RT-UT-CASE-227B

- pytest node id:

```text
runtime/tests/test_preflight.py::test_windows_aiwf_cmd_wraps_powershell_with_process_bypass
```
- Confirm: Placeholder; regenerated input details are maintained by pytest_ut_spec_sync.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:99`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `text`
- Expected: Placeholder; pytest assertion defines the expected result.


- 遒ｺ隱榊・螳ｹ: Windows runtime wrapper縺梧律譁ｰ荳譎ゅ・process-scoped ExecutionPolicy Bypass縺ｧPS1 runtime縺ｫ蟋碑ｭｲ縺吶ｋ縺薙→繧堤｢ｺ隱阪＠縺ｾ縺吶・
- 蜈･蜉帛､:
  - pytest node: 荳願ｨ倥さ繝ｼ繝峨ヶ繝ｭ繝・け縺ｮnode id
  - source: `runtime/tests/test_preflight.py`
  - fixture/arg: 縺ｪ縺・
  - parameter: names=縺ｪ縺・ case=縺ｪ縺・
  - inline input: `root`, `wrapper`, `tools_shim`
- 譛溷ｾ・ｵ先棡: `runtime/windows-script/aiwf.cmd` 縺・Bypass蜻ｼ縺ｳ蜃ｺ縺励～runtime/windows-script/aiwf.cmd` 縺ｯshim縺ｨ縺励※蟋碑ｭｲ縺吶ｋ縲・

#### RT-UT-CASE-227C

- pytest node id:

```text
runtime/tests/test_preflight.py::test_env_path_check_reads_repo_env
```

- 確認内容: pytest case `env path check reads repo env` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:111`
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
  - source: `runtime/tests/test_preflight.py:128`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-227E

- pytest node id:

```text
runtime/tests/test_preflight.py::test_runtime_pytest_check_uses_uv_project_command
```
- Confirm: Placeholder; regenerated input details are maintained by pytest_ut_spec_sync.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:144`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- Expected: Placeholder; pytest assertion defines the expected result.


- 遒ｺ隱榊・螳ｹ: runtime pytest check縺・uv project / dev group繧剃ｽｿ縺｣縺ｦpytest version繧堤｢ｺ隱阪☆繧九％縺ｨ繧堤｢ｺ隱阪＠縺ｾ縺吶・
- 蜈･蜉帛､:
  - pytest node: 荳願ｨ倥さ繝ｼ繝峨ヶ繝ｭ繝・け縺ｮnode id
  - source: `runtime/tests/test_preflight.py`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=縺ｪ縺・ case=縺ｪ縺・
  - inline input: `calls`
- 譛溷ｾ・ｵ先棡: `uv run --project runtime --group dev pytest --version` 縺梧悄蠕・command縺ｨ縺励※螳溯｡後＆繧後ｋ縲・

#### RT-UT-CASE-228

- pytest node id:

```text
runtime/tests/test_preflight.py::test_docker_compose_check_uses_compose_version
```

- 確認内容: pytest case `docker compose check uses compose version` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:168`
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
  - source: `runtime/tests/test_preflight.py:183`
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
  - source: `runtime/tests/test_preflight.py:197`
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
  - source: `runtime/tests/test_preflight.py:241`
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
  - source: `runtime/tests/test_preflight.py:268`
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
  - source: `runtime/tests/test_preflight.py:304`
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
  - source: `runtime/tests/test_preflight.py:325`
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
  - source: `runtime/tests/test_preflight.py:344`
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
  - source: `runtime/tests/test_preflight.py:360`
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
  - source: `runtime/tests/test_preflight.py:379`
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
  - source: `runtime/tests/test_preflight.py:399`
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
  - source: `runtime/tests/test_preflight.py:449`
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
  - source: `runtime/tests/test_preflight.py:449`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`web-nextjs-expected_ids1`
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-238

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_profiles_add_expected_checks[runtime-dev-expected_ids2]
```

- 確認内容: pytest case `build checks profiles add expected checks[vscode-environment-expected_ids2]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:449`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`runtime-dev-expected_ids2`
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-239

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_profiles_add_expected_checks[vscode-environment-expected_ids3]
```
- Confirm: Placeholder; regenerated input details are maintained by pytest_ut_spec_sync.
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:449`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`vscode-environment-expected_ids3`
  - inline input: `args`
- Expected: Placeholder; pytest assertion defines the expected result.


- 遒ｺ隱榊・螳ｹ: pytest case `build checks profiles add expected checks[vscode-environment-expected_ids3]` 縺ｫ蟇ｾ蠢懊☆繧脚untime縺ｮ蜊倅ｽ捺険繧玖・縺・∝｢・阜譚｡莉ｶ縲‘rror boundary繧堤｢ｺ隱阪＠縺ｾ縺吶・
- 蜈･蜉帛､:
  - pytest node: 荳願ｨ倥さ繝ｼ繝峨ヶ繝ｭ繝・け縺ｮnode id
  - source: `runtime/tests/test_preflight.py`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=`profile`, `expected_ids`, case=`vscode-environment-expected_ids3`
  - inline input: `args`
- 譛溷ｾ・ｵ先棡: 隧ｲ蠖田ase縺継ass縺励∝ｯｾ雎｡runtime縺ｮ豁｣蟶ｸ邉ｻ縺ｾ縺溘・蠅・阜譚｡莉ｶ縺御ｻ墓ｧ倥←縺翫ｊ縺ｫ遒ｺ隱阪＆繧後ｋ縲・

#### RT-UT-CASE-239A

- pytest node id:

```text
runtime/tests/test_preflight.py::test_build_checks_localty_gui_and_profiles_without_source_dir
```

- 確認内容: pytest case `build checks localty gui and profiles without source dir` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_preflight.py:483`
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
  - source: `runtime/tests/test_preflight.py:531`
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
  - source: `runtime/tests/test_preflight.py:543`
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
  - source: `runtime/tests/test_preflight.py:581`
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
  - source: `runtime/tests/test_preflight.py:635`
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
  - source: `runtime/tests/test_preflight.py:660`
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
  - source: `runtime/tests/test_preflight.py:688`
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
  - source: `runtime/tests/test_preflight.py:723`
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
  - source: `runtime/tests/test_preflight.py:758`
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
  - source: `runtime/tests/test_preflight.py:783`
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
  - source: `runtime/tests/test_preflight.py:799`
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
  - source: `runtime/tests/test_preflight.py:827`
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
  - source: `runtime/tests/test_preflight.py:856`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `output`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
