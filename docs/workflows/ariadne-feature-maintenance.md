# Ariadne Feature Maintenance

既存対象システムの新機能追加、bug fix、hardware replacement、network change、deployment change、field issue response、運用改善を扱うworkflowです。

## Command

```text
/ariadne-feature-maintenance
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
  -> Claim FEAT_*.svg and run GaC / UaC GUI Mode
  -> Change Intent
  -> Current State Capture
  -> Impact Analysis
  -> Specialist Review Dispatch
  -> Risk Classification
  -> Change Design
  -> Test Plan
  -> PyQt QTest Source Plan when GUI uses PyQt / Qt
  -> Next.js Webapp Implementation Prep when change includes Next.js
  -> Web SVG Layout Mode when WEB_FEAT SVG exists
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
- control command authority、operator workflow
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

既存対象システムの変更対象にPyQt / Qt GUIが含まれる場合、Test Planで作成したテストケース表から、QTestで自動化できる結合疎通試験をソース化します。

優先対象:

- changed GUI behavior
- connect / disconnect / reconnect UI
- control key send
- telemetry / packet / event log display
- sensor override
- show / close lifecycle
- external I/O disabled or stubbed startup

実機、実カメラ、physical STOP、router / VPN / field networkは、QTestだけで完了扱いにせず、人間確認またはbench evidenceを残します。

## GaC / UaC GUI Mode

`work/requirements/svg-input/FEAT_*.svg`が存在する場合、Issue作業領域へ取り込んでから、通常実装の前に[GaC / UaC GUI Mode](gui-mode.md)を実行します。

生成物は既存GUIへの追加候補です。既存Widgetとの接続点、追加Panel、signal/slot、影響範囲、既存test維持をreviewし、必要な差分だけをsourceへ統合します。

## Next.js Webapp Implementation Prep

変更対象にNext.js dashboard / admin / monitoring / business webapp画面が含まれる場合、Implementation前に[Next.js Webapp Implementation Prep](nextjs-webapp-implementation-prep.md)を実行します。

出力:

```text
work/<receipt-id>/process-report/nextjs-webapp-implementation-prep.md
```

既存appへの機能追加では `nextjs-app-template` はreference-onlyとし、既存routing、design system、test runner、env conventionを優先します。

確認すること:

- 既存Next.js app path、App Router有無、TypeScript有無
- route、screen、user action、loading / empty / error state
- API request / response / error response / auth
- `.env.example`、`NEXT_PUBLIC_*`、server-only env、secret ownership
- typecheck、lint、unit、e2e、health、UI smoke、API connectivity

`Implementation may start: yes` になるまでImplementationへ進みません。

## Web SVG Layout Mode

変更対象にNext.js画面が含まれ、`work/requirements/svg-input/WEB_FEAT_*.svg` が存在する場合、Issue作業領域へ取り込んでから、Implementation前に[Web SVG Layout Mode](web-svg-layout-mode.md)を実行します。

出力:

```text
work/<receipt-id>/web-ui/
```

既存appでは生成されたReact / Playwright候補をそのまま上書きせず、既存routing、design system、test fixtureとの差分としてreviewします。

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
skills/ariadne-feature-maintenance/SKILL.md
```
