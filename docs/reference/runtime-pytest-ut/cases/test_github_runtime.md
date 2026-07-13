# test_github_runtime.py

このファイルは `runtime/tests/test_github_runtime.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 36 |

## ケース一覧

#### RT-UT-CASE-148

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_api_urls_support_dotcom_and_enterprise_hosts
```

- 確認内容: pytest case `github api urls support dotcom and enterprise hosts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:23`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-149

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_defensive_specimen_issue_body_report_path_returns_empty_without_car_artifact
```

- 確認内容: defensive specimen issue body report path returns empty without car artifact を検証する。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:35`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 対象分岐が期待どおり処理され、pytest が成功する。

#### RT-UT-CASE-150

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_token_is_required
```

- 確認内容: pytest case `github token is required` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:53`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-151

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_api_json_sends_request_and_parses_response
```

- 確認内容: pytest case `github api json sends request and parses response` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:58`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `seen`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-152

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_api_json_reports_http_and_url_errors
```

- 確認内容: pytest case `github api json reports http and url errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:81`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-153

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_graphql_json_returns_data_and_reports_errors
```

- 確認内容: pytest case `github graphql json returns data and reports errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:116`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-154

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_github_graphql_json_reports_http_and_url_errors
```

- 確認内容: pytest case `github graphql json reports http and url errors` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:126`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-155

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_get_branch_sha_requires_commit_sha
```

- 確認内容: pytest case `get branch sha requires commit sha` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:161`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-156

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_get_branch_sha_returns_commit_sha
```

- 確認内容: pytest case `get branch sha returns commit sha` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:168`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-157

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_get_repository_issue_graphql_context_returns_ids_and_validates_required_fields
```

- 確認内容: pytest case `get repository issue graphql context returns ids and validates required fields` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:174`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-158

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_linked_branch_uses_context_and_defaults_missing_linked_ref
```

- 確認内容: pytest case `create linked branch uses context and defaults missing linked ref` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:212`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-159

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_branch_ref_returns_ref_and_validates_response
```

- 確認内容: pytest case `create branch ref returns ref and validates response` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:232`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-160

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_normalize_issue_title_applies_prefix_once
```

- 確認内容: pytest case `normalize issue title applies prefix once` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:242`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-161

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[ariadne-new-system-\u521d\u671f\u958b\u767a]
```

- 確認内容: pytest case `infer flow label from agent context[ariadne-new-system-\u521d\u671f\u958b\u767a]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:261`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`ariadne-new-system-\u521d\u671f\u958b\u767a`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-162

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[ariadne-feature-maintenance-\u65b0\u898f\u6a5f\u80fd\u30d5\u30ed\u30fc]
```

- 確認内容: pytest case `infer flow label from agent context[ariadne-feature-maintenance-\u65b0\u898f\u6a5f\u80fd\u30d5\u30ed\u30fc]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:261`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`ariadne-feature-maintenance-\u65b0\u898f\u6a5f\u80fd\u30d5\u30ed\u30fc`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-163

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[corrective-action-fix-\u6539\u5584\u30d5\u30ed\u30fc]
```

- 確認内容: pytest case `infer flow label from agent context[corrective-action-fix-\u6539\u5584\u30d5\u30ed\u30fc]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:261`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`corrective-action-fix-\u6539\u5584\u30d5\u30ed\u30fc`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-164

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[docs-sync-\u6539\u5584\u30d5\u30ed\u30fc]
```

- 確認内容: pytest case `infer flow label from agent context[docs-sync-\u6539\u5584\u30d5\u30ed\u30fc]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:261`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`docs-sync-\u6539\u5584\u30d5\u30ed\u30fc`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-165

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_infer_flow_label_from_agent_context[unknown-]
```

- 確認内容: pytest case `infer flow label from agent context[unknown-]` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:261`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=`workflow_name`, `expected`, case=`unknown-`
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-166

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_default_issue_body_uses_project_template_and_corrective_report
```

- 確認内容: pytest case `default issue body uses project template and corrective report` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:271`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-167

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_issue_body_from_args_reads_body_file
```

- 確認内容: pytest case `issue body from args reads body file` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:317`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-168

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_issue_manager_template_default_and_package_guard_edges
```

- 確認内容: pytest case `issue manager template default and package guard edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:330`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-169

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_draft_writes_body_record_and_artifact_index
```

- 確認内容: pytest case `manage issue draft writes body record and artifact index` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:364`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-170

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_create_uses_defaults_and_updates_artifact_status
```

- 確認内容: pytest case `manage issue create uses defaults and updates artifact status` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:401`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-171

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_requires_work_dir_and_github_repo
```

- 確認内容: pytest case `manage issue requires work dir and github repo` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:448`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-172

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_rejects_repo_without_owner
```

- 確認内容: pytest case `manage issue rejects repo without owner` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:471`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-173

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_manage_issue_rejects_slug_without_owner_after_resolution
```

- 確認内容: pytest case `manage issue rejects slug without owner after resolution` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:494`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-174

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_issue_with_api_extracts_number_from_url_when_missing
```

- 確認内容: pytest case `create issue with api extracts number from url when missing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:517`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-175

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_issue_with_api_builds_url_from_number_and_rejects_missing_url
```

- 確認内容: pytest case `create issue with api builds url from number and rejects missing url` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:553`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `payloads`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-176

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_issue_manager_main_prints_json
```

- 確認内容: pytest case `issue manager main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:581`
  - fixture/arg: `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-177

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_create_requires_human_approval
```

- 確認内容: pytest case `pull request create requires human approval` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:612`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-178

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_defaults_use_latest_issue_title_and_base_work_id
```

- 確認内容: pytest case `pull request defaults use latest issue title and base work id` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:634`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-179

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_uses_title_and_body_files_and_create_path
```

- 確認内容: pytest case `pull request uses title and body files and create path` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:657`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-180

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_requires_work_repo_and_head
```

- 確認内容: pytest case `pull request requires work repo and head` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:701`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-181

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_create_pull_request_with_api_posts_payload
```

- 確認内容: pytest case `create pull request with api posts payload` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:730`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `seen`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-182

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_draft_writes_record_and_updates_scm_state
```

- 確認内容: pytest case `pull request draft writes record and updates scm state` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:759`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `args`, `state`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-183

- pytest node id:

```text
runtime/tests/test_github_runtime.py::test_pull_request_parser_file_defaults_main_and_script_paths
```

- 確認内容: pytest case `pull request parser file defaults main and script paths` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_runtime.py:786`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: `parsed`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
