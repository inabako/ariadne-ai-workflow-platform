# Robotics Feature Maintenance

既存 robotics system の新機能追加、bug fix、hardware replacement、network change、deployment change、field issue response、運用改善を扱うworkflowです。

## Command

```text
/robotics-feature-maintenance
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
  -> Change Intent
  -> Current State Capture
  -> Impact Analysis
  -> Specialist Review Dispatch
  -> Risk Classification
  -> Change Design
  -> Test Plan
  -> Implementation
  -> Verification
  -> Deployment Plan
  -> Post-change Observation
  -> Semantic Commit
```

## Required Focus

- 変更量より影響範囲を優先する。
- Safety behavior、network authority、runtime process ownership、operator workflow に影響する変更は実装前にreview対象へ上げる。
- 既存のSTOP、communication loss、rollback意図を壊さない。
- test evidence と human check gate を残す。

## Specialist Review Gate

内部RAGと外部Web RAGを読んだあと、変更の影響が専門領域に入る場合はSpecialist Agentへreviewを渡します。

特に次はreview対象です。

- STOP、communication loss、safe state、watchdog
- robot command authority、operator workflow
- UDP / TCP / QUIC / NAT / routing
- Python / Go runtime、thread、async、process lifecycle
- GStreamer、video latency、receiver behavior
- Docker、MSYS2、Windows/Linux/Raspberry Pi差分
- pytest、Go test、fault injection、packet evidence

review結果は次に保存します。

```text
work/<receipt-id>/process-report/specialist-review-<domain>.md
```

Specialist Agentは、採用した外部Web RAG、採用しなかったclaim、current repository evidence、必要なtest evidenceを明示します。

High / critical finding がある場合は、Change DesignまたはTest Planへ戻し、未解決のままImplementationへ進めません。

完了後、review結果は [Knowledge Capture](knowledge-capture.md) でRAG候補として抽出します。

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
skills/robotics-feature-maintenance/SKILL.md
```
