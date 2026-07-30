# Ariadne Feature Maintenance Development Flow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.ariadne/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

既存対象システムに対する bug fix、改善、hardware 交換、network 変更、field issue 対応を安全に進めるための flow です。

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
- `artifact_type: rag-context-pack` の `work/db/ariadne-knowledge-platform/rag/retrieval/<uuid>.json` の圧縮済み context を確認し、変更前状態と影響分析に反映した
- 必要な場合、Specialist Agent reviewを実行し、専門前提と採用した外部知識を `work/<採番ID>/process-report/` に記録した

この準備が未完了の場合、implementation へ進みません。

RAG loading rule:

- RAG index / embedding が無い場合は `/rag-build` を先に実行する
- `/rag-load` では 3〜5 個の検索クエリを並列実行し、RAG dispatcher 経由で `aiwfctl rag retrieve` の既存圧縮機能を使う
- safety-critical な未解決指摘が見つかった場合は、Phase 1 以降へ進む前に blocker として扱う

Specialist review rule:

- impact analysis、change design、test planが専門知識に依存する場合は、implementation前にSpecialist Agent reviewを実行する
- review結果は `work/<採番ID>/process-report/specialist-review-<domain>.md` に保存する
- 採用した外部Web RAG、採用しなかったclaim、repository evidence、required tests、unresolved human-check itemsを記録する
- high / critical findingがある場合は、Phase 3、Phase 5、またはPhase 6へ戻す

## Phase 0.5: GaC / UaC GUI Mode Dispatch

Issue作業領域作成後、`work/requirements/svg-input/FEAT_*.svg`を確認し、対象SVGを`work/<採番ID>/input/gui/`へ取り込みます。

```powershell
.\runtime\windows-script\aiwf.cmd ctl gui run --issue-id "<FEAT-採番ID>"
```

- SVGが無い場合は`skipped`としてPhase 1へ進む。
- SVGがある場合は`.ariadne/prompts/gac-uac-gui-mode.prompt.md`に従い、既存GUIへの差分候補を生成する。
- `aiwfctl gui validate`が`pass`になるまで通常実装へ進まない。
- generated配下は既存Widgetとの接続点、追加Panel、signal/slot、影響範囲をreviewし、必要部分だけを取り込む。
- Web画面向けSVGは`WEB_FEAT_*.svg`として配置し、Next.js Webapp Implementation Prep後に`.ariadne/prompts/web-svg-layout-mode.prompt.md`に従って`web-ui/`のlayout、React候補、Playwright候補を生成する。

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

- `docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md`
- `docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md`
- `docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md`
- test matrix
- PyQt QTest source plan when GUI uses PyQt / Qt
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
- QTest automation candidates for GUI integration cases

テストケース表:

- `unit-test-cases.md`: unit testで確認する対象、入力、期待結果、pass criteria
- `integration-test-cases.md`: integration / connectivity、QTest候補、manual / startup確認、外部I/O方針
- `human-check-list.md`: 人間確認項目、確認者、確認条件、合否基準

target repositoryへ残す永続証跡:

```text
docs/evidence/issue-<issue-number>/test_specifications/
docs/evidence/issue-<issue-number>/ut/
docs/evidence/issue-<issue-number>/integration/qtest/
docs/evidence/issue-<issue-number>/integration/manual/
docs/evidence/issue-<issue-number>/integration/startup/
docs/evidence/issue-<issue-number>/human_check/
```

`aiwfctl workflow knowledge-capture` はscaffold用 `README.md` を自動生成しますが、READMEだけではテストケース表または証跡とはみなしません。

PyQt / Qt GUIを含む場合:

- テストケース表からQTestで自動化できる結合疎通試験を抽出する
- `src/tests/qt/test_<feature>_integration.py` などのtarget sourceを決める
- external I/Oは原則stub / disableし、実I/Oが必要な場合はtest caseに明示する
- 実robot、実camera、physical STOP、router / VPN / field networkはbench / human-check evidenceとして残す

## Phase 6.5: Next.js Webapp Implementation Preparation

Next.js画面機能を含む場合、Implementation前に `.ariadne/prompts/nextjs-webapp-implementation-prep.prompt.md` に従い、次を作成します。

```text
work/<採番ID>/process-report/nextjs-webapp-implementation-prep.md
```

既存appへの機能追加では `nextjs-app-template` はreference-onlyとし、既存routing、design system、test runner、env conventionを優先します。

確認:

- 既存Next.js app path、App Router有無、TypeScript有無
- route、screen、user action、loading / empty / error state
- `WEB_FEAT_*.svg` がある場合の `web-ui/` responsive layout、component mapping、Playwright候補
- API request / response / error response / auth
- `.env.example`、`NEXT_PUBLIC_*`、server-only env、secret ownership
- typecheck、lint、unit、e2e、health、UI smoke、API connectivity

Quality Gate:

- `Implementation may start: yes` になるまでPhase 7へ進まない。
- templateを既存sourceへ丸ごとコピーしない。
- API契約やauth policyが未定のまま画面実装を始めない。
- `WEB_FEAT_*.svg` がある場合は、`.ariadne/prompts/web-svg-layout-mode.prompt.md`を実行し、`work/<採番ID>/web-ui/`のreviewとvalidateを確認してからsourceへ統合する。

## Phase 7: Implementation

承認されたtest planとPyQt QTest source planに沿って、小さい差分で実装します。

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

実行結果は、test case IDに紐づけて次へ保存します。

```text
docs/evidence/issue-<issue-number>/ut/
docs/evidence/issue-<issue-number>/integration/
docs/evidence/issue-<issue-number>/human_check/
```

Quality Gate:

- high / critical change は、実機前に bench または限定環境で検証する
- regression failure がある場合は release しない
- rollback 手順が未確認なら field deployment しない
- `unit-test-cases.md`、`integration-test-cases.md`、`human-check-list.md` の該当ファイルと実エビデンスが揃っていない場合はpushしない

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
