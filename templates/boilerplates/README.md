# Boilerplate Templates

新システム開発で、既存の共通土台からservice / appを生成するためのboilerplate置き場です。

このディレクトリは、成果物ひな形ではなく、実装の出発点になるsource templateを置きます。

## Category Layout

| Category | Purpose |
| --- | --- |
| `apps/` | UI / app boilerplates such as Next.js, PyQt, and Flutter |
| `services/` | Service boilerplates that are not tied to a specific UI or MCP layer |
| `infrastructure/` | Realtime gateway, platform, database, middleware, identity, and observability collector IaC boilerplates |
| `integration/` | Test and emulator environments used by integration workflows |
| `mcp/` | MCP Server, MCP Client, Agent Runtime, and operation gateway boilerplates |

## Supported Template Names

| Template | Target | Docs | Status |
| --- | --- | --- | --- |
| `services/go-microservice-template/` | Go gateway service | `docs/reference/templates.md` | available |
| `apps/nextjs-app-template/` | Next.js dashboard / admin webapp | `docs/workflows/nextjs-webapp-implementation-prep.md` | available |
| `apps/pyqt-app-template/` | PyQt / Qt GUI app | `docs/reference/templates.md` | available |
| `apps/flutter-app-template/` | Flutter multi-platform app | `docs/workflows/flutter-multiplatform.md` | available |
| `infrastructure/microservice-infra-template/` | Realtime gateway IaC / infrastructure | `docs/workflows/realtime-iac.md` | available |
| `infrastructure/platform-infra-template/` | GitLab / Jenkins / Grafana / Zabbix platform infrastructure | `docs/workflows/realtime-iac.md` | available |
| `infrastructure/database-infra-template/` | PostgreSQL / MySQL shared database infrastructure | `docs/workflows/realtime-iac.md` | available |
| `infrastructure/middleware-infra-template/` | Redis shared middleware infrastructure | `docs/workflows/realtime-iac.md` | available |
| `infrastructure/identity-infra-template/` | OpenLDAP identity / directory infrastructure | `docs/workflows/realtime-iac.md` | available |
| `infrastructure/opentelemetry-collector-template/` | OpenTelemetry Collector receiver / processor / exporter infrastructure | `docs/workflows/realtime-iac.md` | available |
| `integration/cloud-emulators/` | Local cloud / external service emulator environment | `docs/workflows/system-integration-quality.md` | available |
| `mcp/local-model-mcp-server-template/` | Local model MCP server capability provider | `docs/workflows/mcp-server-group-implementation.md` | available |
| `mcp/mcp-client-template/` | Reusable MCP client facade / session manager | `docs/workflows/mcp-server-group-implementation.md` | available |
| `mcp/local-ai-agent-runtime-template/` | Local AI agent runtime / job workflow engine | `docs/workflows/mcp-server-group-implementation.md` | available |
| `mcp/discord-gateway-template/` | Discord operation gateway for local Agent Runtime | `docs/workflows/mcp-server-group-implementation.md` | available |

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
- OpenTelemetry Collector template採用時は、Receiver / Processor / Exporter / Connector / Extensionの選択、Distribution互換性、Custom Distribution Human Check、OTLP port、health endpoint、telemetry smoke evidenceを省略しません。
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
templates/artifacts/process-report/boilerplate-template-selection-report-template.md
```

Next.js webappを採用または参照する場合は、実装前に次の準備reportも作成します。

```text
templates/artifacts/process-report/nextjs-webapp-implementation-prep-template.md
```

Web画面向けSVGレイアウト案がある場合は、`WEB_SYS_*.svg`、`WEB_FEAT_*.svg`、`WEB_FIX_*.svg` として `work/requirements/svg-input/` に配置し、次のサブフローで `web-ui/` 候補を作成します。

```text
docs/workflows/web-svg-layout-mode.md
templates/workflows/web-svg-layout/
```
