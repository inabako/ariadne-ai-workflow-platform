# test_mcp_server_group_workflow.py

このファイルは `runtime/tests/test_mcp_server_group_workflow.py` の pytest node id 単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 12 |

## ケース一覧

#### RT-UT-CASE-MCP-GROUP-001

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_parse_components_defaults_and_unknown
```

- 確認内容: MCP component指定のdefault展開と未知componentの扱いを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:29`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: default componentが選択され、未知componentがhuman check対象として分類される。

#### RT-UT-CASE-MCP-GROUP-002

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_resolve_work_dir_requires_work_id_without_explicit_work_dir
```

- 確認内容: 明示的なwork dirがない場合にwork idを必須にすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:43`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: work idなしではエラーになり、明示work dirがある場合は解決できる。

#### RT-UT-CASE-MCP-GROUP-003

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_analyze_creates_context_and_human_check_for_invalid_boundary
```

- 確認内容: 不正なMCP構成境界をanalyzeした場合にcontextとHuman Checkを生成することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:48`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: analyze contextが保存され、境界違反がhuman_checksに記録される。

#### RT-UT-CASE-MCP-GROUP-004

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_analyze_reports_unknown_only_selection_as_human_check
```

- 確認内容: 未知componentだけが選択された場合にHuman Checkへ戻すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:64`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: unknown selectionがhuman check対象となり、後続のtemplate copyへ進まない。

#### RT-UT-CASE-MCP-GROUP-005

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_analyze_flags_agent_runtime_without_mcp_client
```

- 確認内容: agent runtimeだけを選びMCP clientがない構成を警告できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:81`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: agent runtimeとMCP clientの責務境界不足がhuman checkに残る。

#### RT-UT-CASE-MCP-GROUP-006

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_init_copies_selected_templates
```

- 確認内容: 選択されたMCP templateをwork配下へcopyし、Context First evidenceを残すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:95`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: selected templateがwork配下へ展開され、init contextとmanifestが生成される。

#### RT-UT-CASE-MCP-GROUP-007

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_init_reports_existing_copies_and_force_refreshes_template
```

- 確認内容: 既存copyがある場合の保持と、force指定時のrefreshを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:112`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: forceなしでは既存copyを保持し、forceありではtemplateを安全に再展開する。

#### RT-UT-CASE-MCP-GROUP-008

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_init_reports_missing_template_without_copying
```

- 確認内容: template原本がない場合にcopyせずmissing templateとして報告することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:148`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: missing-template statusとなり、存在しないtemplateを生成したように扱わない。

#### RT-UT-CASE-MCP-GROUP-009

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_explicit_work_dir_can_be_relative_or_absolute
```

- 確認内容: 明示work dirが相対pathでも絶対pathでも解決できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:162`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: relative and absolute work dir specimens
- 期待結果: 相対pathはrepo root基準、絶対pathはそのままwork dirとして扱われる。

#### RT-UT-CASE-MCP-GROUP-010

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_format_result_includes_human_checks_and_artifacts
```

- 確認内容: MCP group結果表示にhuman checksとartifact pathが含まれることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:185`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: formatted result specimen
- 期待結果: CLI表示でstatus、human checks、context/evidence artifactを確認できる。

#### RT-UT-CASE-MCP-GROUP-011

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_ctl_parser_and_run_mcp_group_namespace
```

- 確認内容: `aiwfctl mcp group` のparser namespaceとrun dispatchを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:206`
  - fixture/arg: `monkeypatch`, `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: patched MCP group command functions
- 期待結果: CLI namespaceが正しく構築され、analyze/init系処理へ委譲される。

#### RT-UT-CASE-MCP-GROUP-012

- pytest node id:

```text
runtime/tests/test_mcp_server_group_workflow.py::test_run_uses_explicit_repo_root_and_delegates_to_build_context
```

- 確認内容: explicit repo rootを使ってrunがcontext生成処理へ委譲されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_server_group_workflow.py:238`
  - fixture/arg: `monkeypatch`, `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: explicit repo root and patched context builder
- 期待結果: 明示repo rootが尊重され、context生成結果がCLI resultへ返る。
