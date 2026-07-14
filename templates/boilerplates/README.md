# Boilerplate Templates

新システム開発で、既存の共通土台からservice / appを生成するためのboilerplate置き場です。

このディレクトリは、成果物ひな形ではなく、実装の出発点になるsource templateを置きます。

## Supported Template Names

| Template | Target | Instruction | Status |
| --- | --- | --- | --- |
| `gateway-template/` | Go gateway service | `gateway-template_組み込み指示書.md` | available |
| `nextjs-webapp-template/` | Next.js dashboard / admin webapp | `Next.jsボイラーテンプレート作成_作業指示書.md` | available |
| `pyqt-template/` | PyQt / Qt GUI app | `pyqt-template_組み込み指示書.md` | available |
| `realtime-gateway-infra-template/` | Realtime gateway IaC / infrastructure | `realtime-gateway-infra-template_実装指示書.md` | available |
| `platform-infra-template/` | GitLab / Jenkins / Grafana / Zabbix platform infrastructure | `Platform_Infrastructure_Boilerplate_追加実装指示書.md` | available |
| `database-infra-template/` | PostgreSQL / MySQL shared database infrastructure | `Database_Infrastructure_Boilerplate_追加実装指示書.md` | available |
| `middleware-infra-template/` | Redis shared middleware infrastructure | `Redis _OpenLDAP_Infrastructure_Boilerplate_追加実装指示書.md` | available |
| `identity-infra-template/` | OpenLDAP identity / directory infrastructure | `Redis _OpenLDAP_Infrastructure_Boilerplate_追加実装指示書.md` | available |
| `cloud-emulators/` | Local cloud / external service emulator environment | `docs/workflows/system-integration-quality.md` | available |
| `local-model-mcp-server-template/` | Local model MCP server capability provider | `Local_Model_MCP_Server_Boilerplate_追加実装指示書.md` | available |
| `mcp-client-template/` | Reusable MCP client facade / session manager | `Reusable_MCP_Client_Boilerplate_追加実装指示書.md` | available |
| `local-ai-agent-runtime-template/` | Local AI agent runtime / job workflow engine | `Local_AI_Agent_Runtime_Boilerplate_追加実装指示書.md` | available |
| `discord-gateway-template/` | Discord operation gateway for local Agent Runtime | `Discord_Gateway_Boilerplate_追加実装指示書.md` | available |

## Workflow Rule

- 新システム開発では、Implementation前にこのディレクトリを確認します。
- 対応するtemplate directoryが存在する場合、templateをコピーして新しいservice / app / IaC directoryを作ります。
- template本体は直接編集しません。
- 対応するtemplate directoryが存在しない場合、`decision: traditional-coding` と理由をprocess reportに残し、従来どおりcodingします。
- template採用時も、architecture、protocol、port、safety behavior、test case table、evidence planを省略しません。
- IaC template採用時も、shared artifacts、software inventory、public exposure、secret source、firewall policy、rollbackを省略しません。
- platform infrastructure template採用時は、Terraform component selection、Docker Compose profile、admin CIDR、secret source、backup / restore、product別validation evidenceを省略しません。
- database infrastructure template採用時は、DB engine、DB version、database name、app user、connection source、persistence、backup / restore、migration、connection contract、secret redaction、evidenceを省略しません。
- middleware infrastructure template採用時は、Redis purpose、auth、maxmemory、eviction policy、TTL、persistence、backup / restore、connection contract、secret redaction、evidenceを省略しません。
- identity infrastructure template採用時は、OpenLDAP Base DN、OU、bind account separation、TLS、LDIF、backup / restore、identity connection contract、secret redaction、evidenceを省略しません。
- cloud emulator template採用時も、本番credentialを使わず、`work/<work-id>/test-environment/emulator/` へコピーしてから起動し、`test-evidence/emulator/` に本番差分とHuman Checkを残します。
- MCP server template採用時は、MCP ServerをAgent Runtimeとして扱わず、Prompts / Resources / Tools、workspace境界、local model adapter、secret拒否を確認します。
- MCP client template採用時は、利用側から `server_id` とcapability名を明示し、ClientがTool選択やAgent Loopを持たないことを確認します。
- Agent runtime template採用時は、MCP Server / MCP Client / Discord Gatewayとの境界を分離し、Job、Workflow、Checkpoint、Human Check、Completion evidenceを確認します。
- Discord gateway template採用時は、Discord固有型をAgent Runtimeへ渡さず、Command DTO、Authorization、Rate Limit、Human Check token、Event deduplicationを確認します。

## Expected Selection Report

```text
work/<receipt-id>/process-report/boilerplate-template-selection.md
```

Report template:

```text
templates/process-report/boilerplate-template-selection-report-template.md
```

Next.js webappを採用または参照する場合は、実装前に次の準備reportも作成します。

```text
templates/process-report/nextjs-webapp-implementation-prep-template.md
```

Web画面向けSVGレイアウト案がある場合は、`WEB_SYS_*.svg`、`WEB_FEAT_*.svg`、`WEB_FIX_*.svg` として `work/requirements/svg-input/` に配置し、次のサブフローで `web-ui/` 候補を作成します。

```text
docs/workflows/web-svg-layout-mode.md
templates/web-svg-layout/
```
