# MCP Server Group Implementation

MCP Server Group Implementation は、Ariadne の MCP 系 boilerplate を使って、MCP Server 群、Reusable MCP Client、Local AI Agent Runtime、Discord Gateway を段階的に実装するための workflow extension です。

目的はテンプレートを単にコピーすることではなく、サービス間の責務境界を Context First artifact に残し、Human Check が必要な構成を先に止めることです。

## Scope

- Local Model MCP Server boilerplate を MCP capability provider として展開する。
- Reusable MCP Client boilerplate を runtime / gateway から使う境界として展開する。
- Local AI Agent Runtime boilerplate を job / workflow execution 層として展開する。
- Discord Gateway boilerplate を外部操作 gateway として展開する。
- 選択した component、template copy 結果、boundary check を `work/<work-id>/context/` と `work/<work-id>/reports/` に保存する。

## CLI

```powershell
aiwfctl mcp-group analyze --work-id <work-id>
aiwfctl mcp-group init --work-id <work-id> --components local-model-mcp-server,mcp-client
aiwfctl mcp-group run-workflow --work-id <work-id> --components local-model-mcp-server,mcp-client,local-ai-agent-runtime,discord-gateway
```

`analyze` は context と report だけを作成します。`init` と `run-workflow` は選択した boilerplate を `work/<work-id>/implementation/mcp-server-group/` へ展開します。

## Components

| Component | Template | Destination |
| --- | --- | --- |
| `local-model-mcp-server` | `templates/boilerplates/mcp/mcp-server-template` | `work/<work-id>/implementation/mcp-server-group/local-model-mcp-server` |
| `mcp-client` | `templates/boilerplates/mcp/mcp-client-template` | `work/<work-id>/implementation/mcp-server-group/mcp-client` |
| `local-ai-agent-runtime` | `templates/boilerplates/mcp/ai-agent-runtime-template` | `work/<work-id>/implementation/mcp-server-group/local-ai-agent-runtime` |
| `discord-gateway` | `templates/boilerplates/mcp/discord-gateway-template` | `work/<work-id>/implementation/mcp-server-group/discord-gateway` |

Default component は `local-model-mcp-server,mcp-client` です。

## Boundary Checks

次の条件は `human-check-required` として扱います。

- unknown component が指定されている。
- known component が1つも選択されていない。
- `discord-gateway` が選択され、`local-ai-agent-runtime` が選択されていない。
- `local-ai-agent-runtime` が選択され、`mcp-client` が選択されていない。

`mcp-client` だけを選び、local server を選ばない構成は、外部 MCP Server endpoint を後続工程で明示する前提として `planned` になります。

## Outputs

```text
work/<work-id>/
|-- context/
|   |-- mcp-server-group-implementation-context.json
|   `-- context-manifest.json
|-- reports/
|   `-- mcp-server-group-implementation-report.md
`-- implementation/
    `-- mcp-server-group/
        |-- local-model-mcp-server/
        |-- mcp-client/
        |-- local-ai-agent-runtime/
        `-- discord-gateway/
```

## Parent Workflow Handoff

この extension の output は、`ariadne-new-system`、`ariadne-feature-maintenance`、`corrective-action-fix` の実装準備 artifact として扱います。展開された boilerplate は target source へ即時反映せず、親 workflow の review 後に採用範囲を決めます。

## Rules

- Discord Gateway、Agent Runtime、MCP Client、MCP Server の状態所有を混ぜない。
- Discord library object を Agent Runtime へ渡さない。
- Agent Runtime は MCP Server を直接呼ばず、MCP Client を経由する。
- MCP Server を job scheduler や completion evaluator として扱わない。
- 各 boilerplate のテストを通してから feature 実装へ進む。
