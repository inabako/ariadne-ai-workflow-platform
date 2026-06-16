---
project:
receipt_id:
repository:
branch:
commit:
workflow: new-robotics-system-development
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
|  | Go gateway / PyQt GUI / realtime gateway IaC / other |  | gateway-template / pyqt-template / realtime-gateway-infra-template / none | yes / no |

## Template Availability

| Template | Expected Path | Exists | Instruction |
| --- | --- | --- | --- |
| gateway-template | `templates/boilerplates/gateway-template/` | yes / no | `gateway-template_組み込み指示書.md` |
| pyqt-template | `templates/boilerplates/pyqt-template/` | yes / no | `pyqt-template_組み込み指示書.md` |
| realtime-gateway-infra-template | `templates/boilerplates/realtime-gateway-infra-template/` | yes / no | `realtime-gateway-infra-template_実装指示書.md` |

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
| network / runtime / security / observability / dns |  |  | yes / no |  |

## Required Tests

| Test Area | Required By Template | Project Test Case ID | Evidence Target |
| --- | --- | --- | --- |
| config loading | yes / no |  |  |
| lifecycle start / stop | yes / no |  |  |
| health endpoint | yes / no |  |  |
| protocol encode / decode | yes / no |  |  |
| GUI smoke / QTest | yes / no |  |  |
| graceful shutdown | yes / no |  |  |
| terraform fmt / validate | yes / no |  |  |
| environment tfvars example review | yes / no |  |  |
| firewall / exposure consistency | yes / no |  |  |
| secret placeholder check | yes / no |  |  |
| rollback / operation docs | yes / no |  |  |

## Guardrails

- Template本体を直接編集しない。
- コピー先service / app / IaC directoryのみ編集する。
- Architecture、protocol、port、safety behaviorを黙って変更しない。
- STOP、communication loss、startup safe state、shutdown safe stateのtestを省略しない。
- IaC template採用時は、shared artifacts、software inventory、public exposure、secret source、firewall policy、rollbackを省略しない。
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
