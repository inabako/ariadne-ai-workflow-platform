---
project:
receipt_id:
repository:
branch:
commit:
workflow: ariadne-new-system-development
phase: boilerplate-template-selection
status: draft
language: ja-JP
created_at:
---

# Boilerplate Template Selection

## Intent

実装前に、承認済みarchitecture / runtime design / test strategyに対して利用可能なboilerplate templateがあるか確認し、採用または従来実装の判断を残す。

## Inputs

| Artifact | Path | Status |
| --- | --- | --- |
| Requirements |  |  |
| Architecture |  |  |
| Runtime / Network / Deployment Design |  |  |
| Test Strategy |  |  |
| Specialist Review |  |  |

## Component Classification

| Component | Type | Language / Framework | Template Candidate | Match |
| --- | --- | --- | --- | --- |
|  | Go gateway / Next.js webapp / PyQt GUI / Flutter app / realtime gateway IaC / platform infrastructure / database infrastructure / middleware infrastructure / identity infrastructure / MCP server / MCP client / agent runtime / Discord gateway / other |  | go-microservice-template / nextjs-app-template / pyqt-app-template / flutter-app-template / microservice-infra-template / platform-infra-template / database-infra-template / middleware-infra-template / identity-infra-template / local-model-mcp-server-template / mcp-client-template / local-ai-agent-runtime-template / discord-gateway-template / none | yes / no |

## Template Availability

| Template | Expected Path | Exists | Docs |
| --- | --- | --- | --- |
| go-microservice-template | `templates/boilerplates/services/go-microservice-template/` | yes / no | `docs/reference/templates.md` |
| nextjs-app-template | `templates/boilerplates/apps/nextjs-app-template/` | yes / no | `docs/workflows/nextjs-webapp-implementation-prep.md` |
| pyqt-app-template | `templates/boilerplates/apps/pyqt-app-template/` | yes / no | `docs/reference/templates.md` |
| flutter-app-template | `templates/boilerplates/apps/flutter-app-template/` | yes / no | `docs/workflows/flutter-multiplatform.md` |
| microservice-infra-template | `templates/boilerplates/infrastructure/microservice-infra-template/` | yes / no | `docs/workflows/realtime-iac.md` |
| platform-infra-template | `templates/boilerplates/infrastructure/platform-infra-template/` | yes / no | `docs/workflows/realtime-iac.md` |
| database-infra-template | `templates/boilerplates/infrastructure/database-infra-template/` | yes / no | `docs/workflows/realtime-iac.md` |
| middleware-infra-template | `templates/boilerplates/infrastructure/middleware-infra-template/` | yes / no | `docs/workflows/realtime-iac.md` |
| identity-infra-template | `templates/boilerplates/infrastructure/identity-infra-template/` | yes / no | `docs/workflows/realtime-iac.md` |
| local-model-mcp-server-template | `templates/boilerplates/mcp/local-model-mcp-server-template/` | yes / no | `docs/workflows/mcp-server-group-implementation.md` |
| mcp-client-template | `templates/boilerplates/mcp/mcp-client-template/` | yes / no | `docs/workflows/mcp-server-group-implementation.md` |
| local-ai-agent-runtime-template | `templates/boilerplates/mcp/local-ai-agent-runtime-template/` | yes / no | `docs/workflows/mcp-server-group-implementation.md` |
| discord-gateway-template | `templates/boilerplates/mcp/discord-gateway-template/` | yes / no | `docs/workflows/mcp-server-group-implementation.md` |

## Decision

| Component | Decision | Reason |
| --- | --- | --- |
|  | use-template / traditional-coding / blocked |  |

## Copy Plan

Use only when `decision: use-template`.

| Component | Source Template | Destination | Rename / Replace Rules |
| --- | --- | --- | --- |
|  |  |  |  |

## Responsibility Boundary Check

| Boundary | Template Default | Project Decision | Changed? | Reason |
| --- | --- | --- | --- | --- |
| config |  |  | yes / no |  |
| logger |  |  | yes / no |  |
| lifecycle |  |  | yes / no |  |
| transport / network |  |  | yes / no |  |
| dispatcher / service / viewmodel |  |  | yes / no |  |
| health / metrics |  |  | yes / no |  |
| route / screen / UI state |  |  | yes / no |  |
| API client / auth / environment boundary |  |  | yes / no |  |
| network / runtime / security / observability / dns |  |  | yes / no |  |
| platform component / CI/CD / monitoring / backup / restore |  |  | yes / no |  |
| database engine / connection contract / migration / backup / restore |  |  | yes / no |  |
| Redis purpose / TTL / eviction / persistence / backup / restore |  |  | yes / no |  |
| OpenLDAP Base DN / OU / bind account / TLS / LDIF / backup / restore |  |  | yes / no |  |
| MCP Server / MCP Client / Agent Runtime / Gateway ownership |  |  | yes / no |  |

## Required Tests

| Test Area | Required By Template | Project Test Case ID | Evidence Target |
| --- | --- | --- | --- |
| config loading | yes / no |  |  |
| lifecycle start / stop | yes / no |  |  |
| health endpoint | yes / no |  |  |
| TypeScript typecheck | yes / no |  |  |
| lint | yes / no |  |  |
| webapp unit test | yes / no |  |  |
| webapp e2e / UI smoke | yes / no |  |  |
| API connectivity | yes / no |  |  |
| protocol encode / decode | yes / no |  |  |
| GUI smoke / QTest | yes / no |  |  |
| graceful shutdown | yes / no |  |  |
| terraform fmt / validate | yes / no |  |  |
| terraform plan | yes / no |  |  |
| Docker Compose config | yes / no |  |  |
| GitLab runner registration | yes / no |  |  |
| Jenkins sample job | yes / no |  |  |
| Grafana datasource / dashboard | yes / no |  |  |
| Zabbix item / problem / recovery | yes / no |  |  |
| database connection | yes / no |  |  |
| database read / write | yes / no |  |  |
| database persistence | yes / no |  |  |
| database backup / restore | yes / no |  |  |
| database migration | yes / no |  |  |
| Redis authenticated PING | yes / no |  |  |
| Redis SET / GET / TTL | yes / no |  |  |
| Redis maxmemory / eviction policy | yes / no |  |  |
| Redis persistence / restart | yes / no |  |  |
| Redis backup / restore | yes / no |  |  |
| OpenLDAP administrator / application bind | yes / no |  |  |
| OpenLDAP user / group / membership search | yes / no |  |  |
| OpenLDAP LDIF apply / reapply | yes / no |  |  |
| OpenLDAP TLS | yes / no |  |  |
| OpenLDAP backup / restore | yes / no |  |  |
| environment tfvars example review | yes / no |  |  |
| firewall / exposure consistency | yes / no |  |  |
| secret placeholder check | yes / no |  |  |
| rollback / operation docs | yes / no |  |  |

## Guardrails

- Template本体を直接編集しない。
- コピー先service / app / IaC directoryのみ編集する。
- 既存Next.js appへ画面機能を追加する場合、`nextjs-app-template` はreference-onlyとし、既存sourceへ丸ごと上書きしない。
- Next.js webapp実装前は `templates/artifacts/process-report/nextjs-webapp-implementation-prep-template.md` で画面契約、API契約、auth、env、testを確認する。
- Architecture、protocol、port、safety behaviorを黙って変更しない。
- STOP、communication loss、startup safe state、shutdown safe stateのtestを省略しない。
- IaC template採用時は、shared artifacts、software inventory、public exposure、secret source、firewall policy、rollbackを省略しない。
- platform infrastructure template採用時は、Terraform component selection、Docker Compose profile、admin CIDR、secret source、backup / restore、product別validation evidenceを省略しない。
- database infrastructure template採用時は、DB engine、DB version、database name、app user、connection source、persistence、backup / restore、migration、connection contract、secret redaction、evidenceを省略しない。
- middleware infrastructure template採用時は、Redis purpose、auth、maxmemory、eviction policy、TTL、persistence、backup / restore、connection contract、secret redaction、evidenceを省略しない。
- identity infrastructure template採用時は、OpenLDAP Base DN、OU、bind account separation、TLS、LDIF、backup / restore、identity connection contract、secret redaction、evidenceを省略しない。
- `.env`、real secret、production password、private keyを生成しない。
- Templateが存在しない場合は、従来実装へ進む理由を記録する。

## Open QA

| ID | Question | Blocks Implementation | Owner |
| --- | --- | --- | --- |
| QA-001 |  | yes / no |  |

## Handoff

| Field | Value |
| --- | --- |
| Implementation may start | yes / no |
| Selected templates |  |
| Traditional coding components |  |
| Blockers |  |
