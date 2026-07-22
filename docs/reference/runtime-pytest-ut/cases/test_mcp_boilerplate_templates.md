# test_mcp_boilerplate_templates.py

このファイルは `runtime/tests/test_mcp_boilerplate_templates.py` の pytest node id 単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 3 |

## ケース一覧

#### RT-UT-CASE-MCP-001

- pytest node id:

```text
runtime/tests/test_mcp_boilerplate_templates.py::test_mcp_layered_boilerplates_have_required_template_contract
```

- 確認内容: MCP server、MCP client、AI Agent Runtime、Discord gateway の各boilerplateが必須ファイル契約を満たすことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_boilerplate_templates.py:10`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `expected`, `missing`
- 期待結果: 必須template fileが欠落せず、MCP系boilerplateの層分離契約が維持される。

#### RT-UT-CASE-MCP-002

- pytest node id:

```text
runtime/tests/test_mcp_boilerplate_templates.py::test_boilerplate_index_lists_mcp_layered_templates
```

- 確認内容: boilerplate index と infrastructure / MCP reference が、MCP系layered templateを索引できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_boilerplate_templates.py:113`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `index`, `reference`
- 期待結果: index/referenceに主要MCP boilerplate名が含まれ、利用者がtemplateを発見できる。

#### RT-UT-CASE-MCP-003

- pytest node id:

```text
runtime/tests/test_mcp_boilerplate_templates.py::test_opentelemetry_collector_boilerplate_has_required_template_contract
```

- 確認内容: OpenTelemetry Collector boilerplate templateの必須ファイル、component manifest、Terraform scaffold、script、docs、base configを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_mcp_boilerplate_templates.py:127`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `required`, `base_config`
- 期待結果: 必須template fileがすべて存在し、base configに`otlp`、`memory_limiter`、`batch`、`debug`、`health_check`、`pipelines`が含まれる。
