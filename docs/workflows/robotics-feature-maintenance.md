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
  -> PyQt QTest Source Plan when GUI uses PyQt / Qt
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

## Issue Title

新規機能追加または保守開発のIssue titleは、次のprefixを付けます。

```text
[新規機能フロー] <issue-title>
```

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

## PyQt QTest Integration

既存systemの変更対象にPyQt / Qt GUIが含まれる場合、Test Planで作成したテストケース表から、QTestで自動化できる結合疎通試験をソース化します。

優先対象:

- changed GUI behavior
- connect / disconnect / reconnect UI
- control key send
- telemetry / packet / event log display
- sensor override
- show / close lifecycle
- external I/O disabled or stubbed startup

実robot、実camera、physical STOP、router / VPN / field networkは、QTestだけで完了扱いにせず、人間確認またはbench evidenceを残します。

## Test Case And Evidence Flow

Test Plan工程で、Issue単位のテストケース表を3つに分けて作成します。

```text
docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md
docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md
docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md
```

- `unit-test-cases.md`: UTのテストケース表。
- `integration-test-cases.md`: 結合試験、QTest候補、manual / startup確認のテストケース表。
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
skills/robotics-feature-maintenance/SKILL.md
```
