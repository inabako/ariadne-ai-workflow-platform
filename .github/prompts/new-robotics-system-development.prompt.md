# New Robotics System Development Flow

## Purpose

新しい robotics system を、Intent から安全に動かせる現場運用まで段階的に育てるための flow です。

この flow では、最初から完成形を決め切ることよりも、risk を見える化し、safe trial を重ねながら system boundary を固めることを重視します。

## Entry Conditions

- 新しい robot / device / runtime / remote operation system を作る
- 既存 system から大きく architecture を変える
- hardware、network、operator workflow を含む変更がある
- field operation を前提にした system を立ち上げる

## Phase 0: Pre-development Preparation

開発本体に入る前に `/pre-development-preparation` を実行します。

確認:

- GitHubから対象repository / target branch を取得した
- 要件定義書とrepository stateを比較した
- 修正内容をGitHub Issueへ記載した
- Issue番号から `feature/issue-<issue-number>` branch を作成した
- `work/<採番ID>/context/scm-state.json` にbranch情報が記録されている
- `/rag-load` を実行し、過去の corrective action report から関連する prior finding / risk / test gap / architecture concern を読み込んだ
- `artifact_type: rag-context-pack` の `rag/retrieval/<uuid>.json` の圧縮済み context を確認し、設計前提に反映した
- 必要な場合、Specialist Agent reviewを実行し、専門前提と採用した外部知識を `work/<採番ID>/process-report/` に記録した

この準備が未完了の場合、implementation へ進みません。

RAG loading rule:

- RAG index / embedding が無い場合は `/rag-build` を先に実行する
- `/rag-load` では 3〜5 個の検索クエリを並列実行し、`runtime/rag/retrieve_context.py` の既存圧縮機能を使う
- safety-critical な未解決指摘が見つかった場合は、Phase 1 以降へ進む前に blocker として扱う

Specialist review rule:

- architecture、runtime、network、deployment、safety、test strategyが専門知識に依存する場合は、implementation前にSpecialist Agent reviewを実行する
- review結果は `work/<採番ID>/process-report/specialist-review-<domain>.md` に保存する
- 採用した外部Web RAG、採用しなかったclaim、repository evidence、required tests、unresolved human-check itemsを記録する
- high / critical findingがある場合は、Phase 4、Phase 5、またはPhase 6へ戻す

## Phase 1: Intent / Mission Definition

何を達成する system なのかを定義します。

出力:

- `intent.md`
- mission statement
- primary users / operators
- target environment
- success criteria
- non-goals

確認すること:

- robot が何をするのか
- どこで使うのか
- 誰が操作するのか
- 何をしてはいけないのか
- 最初の usable scope はどこまでか

## Phase 2: Operational Context Definition

現場条件を定義します。

出力:

- `operational-context.md`
- environment assumptions
- operator assumptions
- connectivity assumptions
- device / sensor assumptions
- maintenance assumptions

確認すること:

- indoor / outdoor
- day / night
- network quality
- obstacles / people / vehicles
- manual intervention point
- emergency stop access
- battery / power constraints

## Phase 3: Hazard Analysis / Safety Requirements

実装前に、危険と安全要件を洗い出します。

出力:

- `hazard-analysis.md`
- `safety-requirements.md`
- open safety QA

確認すること:

- runaway
- collision
- stale command
- video loss
- sensor failure
- process crash
- wrong robot connection
- operator misunderstanding
- power failure

Quality Gate:

- STOP / safe stop behavior が未定義なら次へ進まない
- communication loss 時の behavior が未定義なら次へ進まない
- startup / shutdown safe state が未定義なら次へ進まない

## Phase 4: System Architecture

責務境界を設計します。

出力:

- `architecture.md`
- component diagram
- process diagram
- data / control flow
- failure domain
- recovery strategy

分離すべき領域:

- control
- video
- telemetry
- safety
- network
- runtime
- operator UI
- observability
- deployment

Quality Gate:

- control / video / telemetry の failure domain が理由なく結合していない
- safety responsibility が特定 component に隠れていない
- operator decision point が明確
- runtime process が観測可能

## Phase 5: Runtime / Network / Deployment Design

実行時の process、network、deployment を設計します。

出力:

- `runtime-design.md`
- `network-migration-plan.md`
- `deployment-architecture.md`

確認すること:

- process lifecycle
- watchdog / supervisor
- restart behavior
- health check
- LAN / VPN / relay / remote operation の段階計画
- deployment unit
- rollback unit

## Phase 6: Test Strategy

実機に触る前に、どこまで検証するかを決めます。

出力:

- `test-specification.md`
- test matrix
- required simulation / mock / bench tests
- field test plan

確認すること:

- unit test
- integration test
- simulation test
- hardware mock test
- bench test
- limited field test
- safety regression

## Phase 7: Implementation

承認された architecture と test strategy に沿って実装します。

原則:

- 小さく実装する
- safety-critical behavior を暗黙に変更しない
- protocol / port / timeout を黙って変えない
- STOP path を常に優先する
- logs / telemetry を後付けにしない

出力:

- source code
- tests
- implementation report
- unresolved QA

## Phase 8: Integration / Bench Test

実機投入前に、机上または限定環境で統合確認します。

確認すること:

- startup safe state
- shutdown safe state
- emergency stop
- communication loss
- video loss
- sensor stale / invalid
- process crash / restart
- operator UI state
- log / telemetry capture

Quality Gate:

- critical / high safety finding が残っている場合は field test に進まない

## Phase 9: Limited Field Test

現場で限定的に試します。

条件:

- observer / operator role が明確
- emergency stop 手段が確認済み
- fallback / rollback 手順がある
- test scenario が事前に定義済み
- incident capture の保存先が決まっている

出力:

- field-test-report.md
- incident / near-miss notes
- observed limitations
- next QA
- RAG candidate notes

## Phase 10: Release / Operation Handover

運用に渡せる状態にします。

出力:

- operation-guide.md
- troubleshooting.md
- release-notes.md
- rollback-plan.md
- monitoring checklist

確認すること:

- operator が通常状態と degraded state を区別できる
- incident 時の連絡 / 停止 / 復旧手順がある
- logs / telemetry の確認方法がある
- update / rollback の担当が明確

## Exit Conditions

- safety review が pass または conditional-pass
- required tests が完了
- field test の重大 finding が解消済み
- rollback plan が存在する
- operation handover document が存在する
- RAG に残すべき知識が capture されている
