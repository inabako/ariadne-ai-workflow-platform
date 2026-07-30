# Ariadne New System + Realtime IaC

新しい対象システムを作り、その設計結果を Shared Artifacts として固定してから realtime IaC workflow へ渡す統合workflowです。

## Command

```text
/ariadne-new-system-iac
```

## Flow

```text
新システムワークフロー
  -> Shared Artifacts生成
  -> Shared Artifact Validator
  -> IaCワークフロー
```

## Required Input

完成版の要件定義書が必要です。

```text
work/requirements/<completed-requirements>.md
```

要件定義書には `Repository Control` を含めます。

## Phase Overview

```text
Intake
  -> Pre-development Preparation
  -> New System Workflow
  -> Shared Artifacts Generation
  -> Shared Artifact Validator
  -> Realtime IaC Handoff
  -> Realtime IaC Workflow
  -> Commit / Push / Pull Request
```

## Shared Artifacts

必須成果物:

```text
work/<receipt-id>/design-document/shared-artifacts-index.md
work/<receipt-id>/design-document/requirements.md
work/<receipt-id>/design-document/communication-specification.md
work/<receipt-id>/design-document/port-definition.md
work/<receipt-id>/design-document/network-boundary-definition.md
work/<receipt-id>/design-document/architecture-decision-record.md
work/<receipt-id>/process-report/shared-artifact-validation.md
work/<receipt-id>/context/shared-artifact-validation.json
work/<receipt-id>/context/realtime-iac-handoff.json
work/<receipt-id>/context/execution-plan.json
```

必要に応じて:

```text
work/<receipt-id>/design-document/software-inventory.md
```

## Shared Artifact Validator

Validatorは、Shared ArtifactsがIaC workflowへ渡せる品質かを判定します。

| Judgment | Meaning | Next Step |
| --- | --- | --- |
| pass | IaCへ渡せる | `/realtime-iac` |
| conditional-pass | 一部制約付きでIaCへ渡せる | residual riskを記録して `/realtime-iac` |
| fail | IaCへ渡すと危険または不完全 | 新システム設計またはShared Artifacts生成へ戻る |

## Context First Handoff

Shared Artifact Validator が `pass` または human-approved `conditional-pass` の場合、Realtime IaCへ進む前に handoff context と execution plan を作成します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl workflow iac-handoff create `
  --work-id <receipt-id> `
  --validator-judgment <pass|conditional-pass|fail> `
  --source-artifact work/<receipt-id>/design-document/shared-artifacts-index.md
```

生成物:

```text
work/<receipt-id>/context/realtime-iac-handoff.json
work/<receipt-id>/context/execution-plan.json
work/<receipt-id>/context/context-manifest.json
```

`execution-plan.json` は、`/realtime-iac` へ渡す前に必要な `environment-selection`、停止条件、次commandを明示します。
Realtime IaC開始前には Docker environment gate を確認します。

```powershell
aiwfctl env select docker --work-id <receipt-id>
uv run --project runtime python runtime/ctl/ctl.py --repo-root . context require-environment `
  --work-dir work/<receipt-id> `
  --environment docker
```

## Stop Rules

次の場合はIaCへ進みません。

- requirementsが未完成
- communication specificationが不足または矛盾
- port definitionが不足または矛盾
- network boundary definitionが不足または矛盾
- ADRが主要decisionを説明していない
- safety behaviorがtraceできない
- repository modeが不明
- software inventoryが必要なのに不足
- Validator judgmentが`fail`

## Templates

```text
templates/artifacts/shared-artifacts/shared-artifacts-index-template.md
templates/artifacts/shared-artifacts/port-definition-template.md
templates/artifacts/shared-artifacts/network-boundary-definition-template.md
templates/artifacts/shared-artifacts/architecture-decision-record-template.md
templates/workflows/iac/communication-specification-template.md
templates/workflows/iac/software-inventory-template.md
```

## Source Skills

```text
skills/ariadne-new-system/SKILL.md
skills/realtime-iac/SKILL.md
skills/ariadne-new-system-iac/SKILL.md
```
