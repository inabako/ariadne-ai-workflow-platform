# Robotics New System

新しい robotics system、robot runtime、remote operation system、device integration、architecture-level launch を始めるworkflowです。

## Command

```text
/robotics-new-system
```

## Required Input

完成版の要件定義書が必要です。

```text
work/requirements/<completed-requirements>.md
```

要件定義書には `Repository Control` を含めます。

## Flow

```text
Intake
  -> Repository Sync
  -> Requirement Comparison
  -> GitHub Issue Draft / Create
  -> Working Branch Create
  -> Claim SYS_*.svg and run GaC / UaC GUI Mode
  -> RAG Load / Prior Findings
  -> Specialist Review Dispatch
  -> Intent / Mission
  -> Operational Context
  -> Hazard Analysis / Safety Requirements
  -> System Architecture
  -> Runtime / Network / Deployment Design
  -> Test Strategy
  -> PyQt QTest Source Plan when GUI uses PyQt / Qt
  -> Boilerplate Template Selection
  -> Next.js Webapp Implementation Prep when system includes Next.js
  -> Web SVG Layout Mode when WEB_SYS SVG exists
  -> Implementation
  -> Integration / Bench Test
  -> Limited Field Test
  -> Release / Operation Handover
  -> Semantic Commit
```

## Stop Rules

次が未定義なら先へ進めません。

- STOP / emergency stop behavior
- communication loss behavior
- startup safe state
- shutdown safe state
- rollback path
- observability

Critical / high safety finding が残っている場合、field testへ進めません。

## Issue Title

新しいsystemや初期開発のIssue titleは、次のprefixを付けます。

```text
[初期開発] <issue-title>
```

## Specialist Review Gate

内部RAGと外部Web RAGを読んだあと、新システムの成果物に専門前提が含まれる場合は、実装前にSpecialist Agentへreviewを渡します。

対象例:

- Go realtime gateway
- Python GUI / runtime
- UDP / TCP / QUIC / NAT traversal
- GStreamer / video pipeline
- Windows / Linux / Raspberry Pi / Docker deployment
- Prometheus / OpenTelemetry / logs / metrics
- STOP、communication loss、watchdog、safe state

review結果は次に保存します。

```text
work/<receipt-id>/process-report/specialist-review-<domain>.md
```

Specialist Agentは、どの外部Web RAGを信じたか、どのclaimを採用しなかったか、何で検証するかを `Trusted External Knowledge` として残します。

High / critical finding がある場合は、System Architecture、Runtime / Network / Deployment Design、またはTest Strategyへ戻します。

完了後、review結果は [Knowledge Capture](knowledge-capture.md) でRAG候補として抽出します。

## PyQt QTest Integration

新システムにPyQt / Qt GUIが含まれる場合、Test Strategyで作成したテストケース表から、QTestで自動化できる結合疎通試験をソース化します。

QTest化する対象は、GUI操作、widget状態、signal / slot、ログやpacket表示など、外部I/Oをstubまたはdisableして検証できるものです。

実robot、実camera、physical STOP、field networkなどは、QTestでは置き換えず、bench / limited field / human checkとして残します。

## GaC / UaC GUI Mode

`work/requirements/svg-input/SYS_*.svg`が存在する場合、Issue作業領域へ取り込んでから、通常設計・実装の前に[GaC / UaC GUI Mode](gui-mode.md)を実行します。

SVGからMainWindow、主要Panel、Widget責務、PyQt6候補、初期QTest候補を作ります。生成物は`gac-uac/`へ隔離し、初期architecture候補としてreviewした部分だけをsourceへ統合します。

## Boilerplate Template Selection

実装前に、承認済みarchitectureとtest strategyに対して利用可能なboilerplate templateを確認します。

置き場:

```text
templates/boilerplates/
```

現在の対応:

| 対象 | Template | 組み込み指示書 |
| --- | --- | --- |
| Go gateway service | `templates/boilerplates/gateway-template/` | `gateway-template_組み込み指示書.md` |
| Next.js dashboard / admin webapp | `templates/boilerplates/nextjs-webapp-template/` | `Next.jsボイラーテンプレート作成_作業指示書.md` |
| PyQt / Qt GUI app | `templates/boilerplates/pyqt-template/` | `pyqt-template_組み込み指示書.md` |
| Realtime gateway IaC / infrastructure | `templates/boilerplates/realtime-gateway-infra-template/` | `realtime-gateway-infra-template_実装指示書.md` |

ルール:

- 対応するtemplateが存在する場合、templateをコピーしてコピー先service / appだけを編集します。
- template本体は直接編集しません。
- 対応するtemplateが存在しない組み合わせでは、従来どおりcodingします。
- template採用の有無、コピー元、コピー先、採用理由、使わないcomponent、必要testを `work/<receipt-id>/process-report/boilerplate-template-selection.md` に記録します。
- template採用時も、STOP、communication loss、startup safe state、shutdown safe state、test case table、evidence planは省略しません。
- IaC template採用時も、shared artifacts、software inventory、public exposure、secret source、firewall policy、rollback、Terraform validationを省略しません。

template選定結果が未記録の場合、Implementationへ進みません。

## Next.js Webapp Implementation Prep

新システムにNext.js dashboard / admin / monitoring / business webappが含まれる場合、Implementation前に[Next.js Webapp Implementation Prep](nextjs-webapp-implementation-prep.md)を実行します。

出力:

```text
work/<receipt-id>/process-report/nextjs-webapp-implementation-prep.md
```

確認すること:

- 新規webappか既存webapp拡張か
- `nextjs-webapp-template` の採用可否
- route、screen、user action、loading / empty / error state
- API request / response / error response / auth
- `.env.example`、`NEXT_PUBLIC_*`、server-only env、secret ownership
- typecheck、lint、unit、e2e、health、UI smoke、API connectivity、Docker smoke

`Implementation may start: yes` になるまでImplementationへ進みません。

## Web SVG Layout Mode

新システムにNext.js画面が含まれ、`work/requirements/svg-input/WEB_SYS_*.svg` が存在する場合、Issue作業領域へ取り込んでから、Implementation前に[Web SVG Layout Mode](web-svg-layout-mode.md)を実行します。

出力:

```text
work/<receipt-id>/web-ui/
```

SVGからroute、section、component責務、responsive layout、React候補、Playwright候補を作ります。生成物は候補であり、Next.js Webapp Implementation Prepの画面契約、API契約、auth、env、test方針と照合してから採用します。

## Test Case And Evidence Flow

Test Strategy工程で、Issue単位のテストケース表を3つに分けて作成します。

```text
docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md
docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md
docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md
```

- `unit-test-cases.md`: UTのテストケース表。
- `integration-test-cases.md`: 結合試験、bench、limited field、QTest候補、manual / startup確認のテストケース表。
- `human-check-list.md`: 人間確認項目、確認条件、合否基準。

実行エビデンスは次へ保存します。

```text
docs/evidence/issue-<issue-number>/ut/
docs/evidence/issue-<issue-number>/integration/qtest/
docs/evidence/issue-<issue-number>/integration/manual/
docs/evidence/issue-<issue-number>/integration/startup/
docs/evidence/issue-<issue-number>/human_check/
```

保存先の詳細は [Test Artifact Storage](../reference/test-artifact-storage.md) に従います。
Knowledge Capture実行時にscaffoldは自動生成されますが、`README.md` だけではpush可能な証跡とはみなしません。

## Main Artifacts

```text
work/<receipt-id>/design-document/
work/<receipt-id>/process-report/
work/<receipt-id>/test-specifications/
work/<receipt-id>/test-evidence/
work/<receipt-id>/context/
```

## Source Skill

```text
skills/robotics-new-system/SKILL.md
```
