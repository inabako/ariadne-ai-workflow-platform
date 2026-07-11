# test_scm_runtime.py

このファイルは `runtime/tests/test_scm_runtime.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 53 |

## ケース一覧

#### RT-UT-CASE-430

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

#### RT-UT-CASE-431

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

#### RT-UT-CASE-432

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

#### RT-UT-CASE-433

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

#### RT-UT-CASE-434

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

#### RT-UT-CASE-435

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

#### RT-UT-CASE-436

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

#### RT-UT-CASE-437

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

#### RT-UT-CASE-438

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

#### RT-UT-CASE-439

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

#### RT-UT-CASE-440

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

#### RT-UT-CASE-441

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

#### RT-UT-CASE-442

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

#### RT-UT-CASE-443

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

#### RT-UT-CASE-444

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

#### RT-UT-CASE-445

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

#### RT-UT-CASE-446

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

#### RT-UT-CASE-447

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

#### RT-UT-CASE-448

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

#### RT-UT-CASE-449

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

#### RT-UT-CASE-450

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

#### RT-UT-CASE-451

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

#### RT-UT-CASE-452

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
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-453

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_local_only_creates_missing_branch_and_script_load
```

- 確認内容: pytest case `create issue branch local only creates missing branch and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:863`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-454

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_remote_branch_ref_then_clone
```

- 確認内容: pytest case `create issue branch remote branch ref then clone` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:905`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `clone_calls`, `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-455

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_remote_dry_run_fills_repository_from_github_repo
```

- 確認内容: pytest case `create issue branch remote dry run fills repository from github repo` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:955`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-456

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_remote_linked_branch_checks_out_existing_source
```

- 確認内容: pytest case `create issue branch remote linked branch checks out existing source` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:979`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `checkout_calls`, `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-457

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_requires_github_repo_for_remote_creation
```

- 確認内容: pytest case `create issue branch requires github repo for remote creation` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1031`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-458

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_create_issue_branch_main_prints_json
```

- 確認内容: pytest case `create issue branch main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1052`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-459

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_dry_run_refuses_non_issue_branch
```

- 確認内容: pytest case `push branch dry run refuses non issue branch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1079`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-460

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_requires_existing_source_repository
```

- 確認内容: pytest case `push branch requires existing source repository` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1102`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-461

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_refuses_workflow_repository_itself
```

- 確認内容: pytest case `push branch refuses workflow repository itself` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1119`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-462

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_dry_run_writes_push_record_for_issue_branch
```

- 確認内容: pytest case `push branch dry run writes push record for issue branch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1136`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-463

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_uses_current_branch_when_state_has_no_working_branch
```

- 確認内容: pytest case `push branch uses current branch when state has no working branch` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1164`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-464

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_non_dry_run_uses_token_env_and_set_upstream
```

- 確認内容: pytest case `push branch non dry run uses token env and set upstream` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1190`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-465

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_push_branch_main_prints_json
```

- 確認内容: pytest case `push branch main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1225`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-466

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_rejects_non_semantic_message
```

- 確認内容: pytest case `commit changes rejects non semantic message` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1253`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-467

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_parser_main_script_and_plain_commit
```

- 確認内容: pytest case `commit changes parser main script and plain commit` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1271`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`, `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-468

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_dry_run_records_status_without_commit
```

- 確認内容: pytest case `commit changes dry run records status without commit` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1355`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-469

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_missing_source_dir_is_reported
```

- 確認内容: pytest case `commit changes missing source dir is reported` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1384`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-470

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_requires_changes_unless_allow_empty
```

- 確認内容: pytest case `commit changes requires changes unless allow empty` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1400`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-471

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_commit_changes_non_dry_run_allows_empty_and_configures_user
```

- 確認内容: pytest case `commit changes non dry run allows empty and configures user` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1426`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-472

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_requires_human_approval_for_initial_push
```

- 確認内容: pytest case `bootstrap repository requires human approval for initial push` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1465`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-473

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_rejects_non_semantic_message
```

- 確認内容: pytest case `bootstrap repository rejects non semantic message` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1485`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-474

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_parser_main_and_script_load
```

- 確認内容: pytest case `bootstrap repository parser main and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1504`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-475

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_requires_existing_work_directory
```

- 確認内容: pytest case `bootstrap repository requires existing work directory` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1571`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-476

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_dry_run_uses_scm_state_repository_and_writes_record
```

- 確認内容: pytest case `bootstrap repository dry run uses scm state repository and writes record` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1591`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-477

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_rejects_workflow_repo_as_source
```

- 確認内容: pytest case `bootstrap repository rejects workflow repo as source` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1623`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-478

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_requires_github_repo_when_state_is_empty
```

- 確認内容: pytest case `bootstrap repository requires github repo when state is empty` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1642`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-479

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_set_remote_adds_or_updates
```

- 確認内容: pytest case `bootstrap repository set remote adds or updates` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1661`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `get_url_returncode`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-480

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_non_dry_run_commits_and_pushes
```

- 確認内容: pytest case `bootstrap repository non dry run commits and pushes` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1690`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-481

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_non_dry_run_skips_commit_when_head_exists
```

- 確認内容: pytest case `bootstrap repository non dry run skips commit when head exists` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1747`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`, `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-482

- pytest node id:

```text
runtime/tests/test_scm_runtime.py::test_bootstrap_repository_non_dry_run_requires_files_when_no_head
```

- 確認内容: pytest case `bootstrap repository non dry run requires files when no head` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_scm_runtime.py:1791`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
