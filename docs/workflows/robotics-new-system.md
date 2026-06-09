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
  -> RAG Load / Prior Findings
  -> Specialist Review Dispatch
  -> Intent / Mission
  -> Operational Context
  -> Hazard Analysis / Safety Requirements
  -> System Architecture
  -> Runtime / Network / Deployment Design
  -> Test Strategy
  -> PyQt QTest Source Plan when GUI uses PyQt / Qt
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
