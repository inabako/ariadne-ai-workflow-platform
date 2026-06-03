# Robotics Maintenance Development Flow

## Purpose

既存 robotics system に対する bug fix、改善、hardware 交換、network 変更、field issue 対応を安全に進めるための flow です。

保守開発では、変更量よりも影響範囲と安全性を重視します。

## Entry Conditions

- bug fix
- performance improvement
- device / sensor / camera replacement
- control logic change
- UI / operator workflow change
- network / deployment change
- incident / field feedback からの改善

## Phase 0: Pre-development Preparation

保守開発の本体に入る前に `/pre-development-preparation` を実行します。

確認:

- GitHubから対象repository / target branch を取得した
- 要件定義書またはincident reportとrepository stateを比較した
- 修正内容、影響範囲、acceptance criteriaをGitHub Issueへ記載した
- Issue番号から `feature/issue-<issue-number>` branch を作成した
- `work/<採番ID>/context/scm-state.json` にbranch情報が記録されている
- `/rag-load` を実行し、過去の corrective action report から関連する prior finding / risk / test gap / architecture concern を読み込んだ
- `artifact_type: rag-context-pack` の `rag/retrieval/<uuid>.json` の圧縮済み context を確認し、変更前状態と影響分析に反映した

この準備が未完了の場合、implementation へ進みません。

RAG loading rule:

- RAG index / embedding が無い場合は `/rag-build` を先に実行する
- `/rag-load` では 3〜5 個の検索クエリを並列実行し、`runtime/rag/retrieve_context.py` の既存圧縮機能を使う
- safety-critical な未解決指摘が見つかった場合は、Phase 1 以降へ進む前に blocker として扱う

## Phase 1: Change Intent

なぜ変更するのかを定義します。

出力:

- `change-intent.md`
- issue / incident reference
- expected improvement
- non-goals

分類:

- bug fix
- safety improvement
- reliability improvement
- usability improvement
- observability improvement
- device replacement
- network migration
- operational procedure update

## Phase 2: Current State Capture

変更前の状態を記録します。

出力:

- current behavior
- related architecture
- related runtime process
- related hardware / device
- known logs / telemetry
- reproduction steps where possible

確認すること:

- どの個体 / version / environment で起きたか
- field condition は何だったか
- operator action は何だったか
- safety state はどうだったか
- workaround はあるか

## Phase 3: Impact Analysis

影響範囲を洗い出します。

対象:

- control
- video
- telemetry
- safety
- network
- runtime
- deployment
- operator UI
- operation procedure
- hardware compatibility

Quality Gate:

- safety behavior に影響がある変更は Safety Reviewer に回す
- network / remote operation に影響がある変更は Security / Network Reviewer に回す
- runtime process に影響がある変更は Observability / Runtime 観点を確認する

## Phase 4: Risk Classification

変更 risk を分類します。

| Level | Examples | Required Checks |
| --- | --- | --- |
| low | docs、ログ追加、UI文言、非制御領域の軽微修正 | targeted test |
| medium | telemetry表示、operator UI状態、network設定、runtime restart | regression + integration |
| high | control logic、timeout、STOP、sensor handling、deployment topology | safety review + bench test |
| critical | emergency stop、motor output、remote command authority、人や設備への直接危険 | formal safety gate + limited field test |

## Phase 5: Change Design

実装前に、変更方法を決めます。

出力:

- `change-design.md`
- responsibility delta
- protocol / timeout / port delta
- rollback plan
- required QA
- required tests

確認すること:

- 既存 architecture の責務境界を壊していないか
- failure domain を広げていないか
- operator の判断点を変えていないか
- rollback できる単位か

## Phase 6: Test Plan

risk level に応じた test plan を作ります。

出力:

- test matrix
- regression target
- safety check target
- simulation / mock / bench / field の要否

最低確認:

- changed behavior
- previous behavior
- error path
- timeout / stale data
- startup / shutdown
- observability

## Phase 7: Implementation

小さい差分で実装します。

原則:

- unrelated refactor を混ぜない
- safety-critical constants を黙って変更しない
- protocol compatibility を確認する
- logs / metrics を必要に応じて追加する
- unresolved QA は隠さず記録する

## Phase 8: Verification

test plan に沿って確認します。

確認例:

- unit test
- integration test
- smoke test
- simulation test
- bench test
- field reproduction test
- rollback rehearsal

Quality Gate:

- high / critical change は、実機前に bench または限定環境で検証する
- regression failure がある場合は release しない
- rollback 手順が未確認なら field deployment しない

## Phase 9: Deployment Plan

どこに、いつ、どう戻せる状態で反映するかを決めます。

出力:

- deployment plan
- affected robots / environments
- maintenance window
- operator notice
- rollback procedure
- post-deploy monitoring plan

## Phase 10: Post-change Observation

反映後に観測します。

確認すること:

- logs / telemetry
- operator feedback
- error rate
- reconnect / restart behavior
- safety events
- field notes

出力:

- post-change report
- incident / near-miss if any
- RAG candidate notes
- next improvements

## Exit Conditions

- change intent が満たされた
- required tests が完了
- regression risk が許容範囲
- rollback plan がある
- post-change observation が記録された
- field learning が knowledge-inbox に保存された
