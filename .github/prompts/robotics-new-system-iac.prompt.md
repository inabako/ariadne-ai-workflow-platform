# Robotics New System + Realtime IaC Workflow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

新しい robotics system を設計し、その結果を Shared Artifacts として固定してから realtime IaC workflow へ渡す統合flowです。

```text
新システムワークフロー
  -> Shared Artifacts生成
  -> Shared Artifact Validator
  -> IaCワークフロー
```

## Entry Conditions

- 完成版要件定義書が `work/requirements/` に1件だけ存在する
- 要件定義書に `Repository Control` が含まれる
- 新システムの目的、対象repository、repository modeが明確である
- IaCへ渡す必要があるruntime / network / deployment / observability scopeがある

## Phase 0: Pre-development Preparation

開発本体に入る前に `/pre-development-preparation` を実行します。

確認:

- target repository / target branch または precreated-new repository が明確である
- GitHub Issue と branch の作成順序がrepository modeに合っている
- `/rag-load` により過去の architecture / safety / network / deployment / IaC findingを読んだ
- 必要なSpecialist Agent reviewの候補を洗い出した

## Phase 1: New System Workflow

`/robotics-new-system` と同じ観点で、新システムの設計を進めます。

出力:

- intent / mission
- operational context
- hazard analysis
- safety requirements
- system architecture
- runtime / network / deployment design
- test strategy

Stop rules:

- STOP / communication loss / startup safe state / shutdown safe state が未定義
- system responsibility boundary が未定義
- operator responsibility が未定義
- repository mode が未定義

## Phase 2: Shared Artifacts Generation

IaCへ渡すため、Shared Artifactsを生成します。

必須:

```text
work/<receipt-id>/design-document/shared-artifacts-index.md
work/<receipt-id>/design-document/requirements.md
work/<receipt-id>/design-document/communication-specification.md
work/<receipt-id>/design-document/port-definition.md
work/<receipt-id>/design-document/network-boundary-definition.md
work/<receipt-id>/design-document/architecture-decision-record.md
```

必要に応じて:

```text
work/<receipt-id>/design-document/software-inventory.md
```

Templates:

```text
templates/shared-artifacts/shared-artifacts-index-template.md
templates/iac/communication-specification-template.md
templates/shared-artifacts/port-definition-template.md
templates/shared-artifacts/network-boundary-definition-template.md
templates/shared-artifacts/architecture-decision-record-template.md
templates/iac/software-inventory-template.md
```

Shared Artifactsは、アプリケーションworkflowとIaC workflowのsingle source of truthです。AIはport、protocol、network boundary、software inventory、repository modeを推測で補完しません。

## Phase 3: Shared Artifact Validator

Shared Artifact Validatorを実行します。

出力:

```text
work/<receipt-id>/process-report/shared-artifact-validation.md
work/<receipt-id>/context/shared-artifact-validation.json
```

確認:

- 要件定義の対象範囲がShared Artifactsに反映されている
- communication flowがsource / destination / protocol / port / boundary / security / failure behavior / evidenceまで持つ
- port definitionが重複、未所有、公開範囲不明のportを残していない
- network boundaryがpublic / private / host / container / fieldなどを区別している
- ADRが主要なarchitecture / infrastructure decisionを説明している
- safety-critical behaviorが設計とtest strategyにtraceされている
- IaCがinstall / package / start / supervise / proxy / monitor / documentするsoftwareがsoftware inventoryに載っている

Judgment:

| Judgment | Next Step |
| --- | --- |
| pass | `/realtime-iac` へ進む |
| conditional-pass | blocked areaを除いて `/realtime-iac` へ進み、residual riskを記録する |
| fail | 新システム設計またはShared Artifacts生成へ戻る |

## Phase 4: Realtime IaC Handoff

Validatorが`pass`または`conditional-pass`の場合、IaC handoffを作成します。

```text
work/<receipt-id>/context/realtime-iac-handoff.json
```

Handoff fields:

- source artifact paths
- validator judgment
- blocked areas
- residual risks
- target repository
- repository mode
- target branch or initial branch
- required human approvals
- next command: `/realtime-iac`

## Phase 5: Realtime IaC Workflow

`/realtime-iac` 側の Boilerplate Template Selection を必ず実行します。
realtime gateway infrastructure が対象に含まれる場合は、`templates/boilerplate-templates/realtime-gateway-infra-template/` を候補にし、採用または不採用の理由を次に記録します。

```text
work/<receipt-id>/process-report/boilerplate-template-selection.md
```

template採用時も、Shared Artifacts、software inventory、public exposure、secret source、firewall policy、rollback、Terraform validationを省略しません。

`/realtime-iac` を実行します。

Rules:

- Shared Artifactsをsource of truthにする
- Shared Artifactsと矛盾するIaCを生成しない
- missing itemが出た場合は、IaC側で推測せずShared Artifact Validatorへ戻す
- `.env` は生成しない。`.env.example` のみ生成する
- Docker Desktop -> Linux runtime -> integration の順に検証する

## Exit Conditions

- 新システム設計の主要成果物が存在する
- Shared Artifactsが存在する
- Shared Artifact Validatorが`pass`または明示的な`conditional-pass`
- realtime IaC handoffが存在する
- IaC workflowへ渡すrepository mode、branch、software inventory、communication specification、port definition、network boundaryが明確
- 未解決QAとresidual riskが記録されている
