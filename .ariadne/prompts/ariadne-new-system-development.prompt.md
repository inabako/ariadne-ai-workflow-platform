# Ariadne New System Development Flow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.ariadne/shared/output-language-policy.md` を確認して日本語で作成してください。

## Purpose

新しい対象システムを、Intent から安全に動かせる現場運用まで段階的に育てるための flow です。

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
- `artifact_type: rag-context-pack` の `work/db/ariadne-knowledge-platform/rag/retrieval/<uuid>.json` の圧縮済み context を確認し、設計前提に反映した
- 必要な場合、Specialist Agent reviewを実行し、専門前提と採用した外部知識を `work/<採番ID>/process-report/` に記録した

この準備が未完了の場合、implementation へ進みません。

RAG loading rule:

- RAG index / embedding が無い場合は `/rag-build` を先に実行する
- `/rag-load` では 3〜5 個の検索クエリを並列実行し、RAG dispatcher 経由で `aiwfctl rag retrieve` の既存圧縮機能を使う
- safety-critical な未解決指摘が見つかった場合は、Phase 1 以降へ進む前に blocker として扱う

Specialist review rule:

- architecture、runtime、network、deployment、safety、test strategyが専門知識に依存する場合は、implementation前にSpecialist Agent reviewを実行する
- review結果は `work/<採番ID>/process-report/specialist-review-<domain>.md` に保存する
- 採用した外部Web RAG、採用しなかったclaim、repository evidence、required tests、unresolved human-check itemsを記録する
- high / critical findingがある場合は、Phase 4、Phase 5、またはPhase 6へ戻す

## Phase 0.5: GaC / UaC GUI Mode Dispatch

Issue作業領域作成後、`work/requirements/svg-input/SYS_*.svg`を確認し、対象SVGを`work/<採番ID>/input/gui/`へ取り込みます。

```powershell
.\runtime\windows-script\aiwf.cmd ctl gui run --issue-id "<SYS-採番ID>"
```

- SVGが無い場合は`skipped`としてPhase 1へ進む。
- SVGがある場合は`.ariadne/prompts/gac-uac-gui-mode.prompt.md`に従い、`gac-uac/`の設計・PyQt6・QTest候補を生成する。
- `aiwfctl gui validate`が`pass`になるまで通常実装へ進まない。
- generated配下は初期GUI architecture候補としてreviewし、MainWindow、主要Panel、責務分離、QTest初期構成の必要部分だけを取り込む。
- Web画面向けSVGは`WEB_SYS_*.svg`として配置し、Next.js Webapp Implementation Prep後に`.ariadne/prompts/web-svg-layout-mode.prompt.md`を確認して`web-ui/`のlayout、React候補、Playwright候補を生成する。

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

- `docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md`
- `docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md`
- `docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md`
- test matrix
- PyQt QTest source plan when GUI uses PyQt / Qt
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
- QTest automation candidates for GUI integration cases

テストケース表:

- `unit-test-cases.md`: unit testで確認する対象、入力、期待結果、pass criteria
- `integration-test-cases.md`: integration / connectivity、bench、limited field、QTest候補、manual / startup確認、外部I/O方針
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
- 実robot、実camera、physical STOP、field networkはbench / human-check evidenceとして残す

## Phase 6.5: Boilerplate Template Selection

実装前に、承認済みarchitectureとtest strategyに対して、利用可能なboilerplate templateがあるかを確認します。

Template root:

```text
templates/boilerplates/
```

現在の対応:

| 対象 | Template | 詳細Docs |
| --- | --- | --- |
| Go gateway service | `templates/boilerplates/services/go-microservice-template/` | `docs/reference/templates.md` |
| Next.js dashboard / admin webapp | `templates/boilerplates/apps/nextjs-app-template/` | `docs/workflows/nextjs-webapp-implementation-prep.md` |
| PyQt / Qt GUI app | `templates/boilerplates/apps/pyqt-app-template/` | `docs/reference/templates.md` |
| Realtime gateway IaC / infrastructure | `templates/boilerplates/infrastructure/microservice-infra-template/` | `docs/workflows/realtime-iac.md` |

出力:

- `work/<採番ID>/process-report/boilerplate-template-selection.md`

判定:

- 対象systemがGo gatewayを含み、`go-microservice-template/` が存在する場合は、`docs/reference/templates.md` を確認してtemplateをコピーしてから実装する。
- 対象systemがNext.js dashboard / admin webappを含み、`nextjs-app-template/` が存在する場合は、`docs/workflows/nextjs-webapp-implementation-prep.md` と `nextjs-webapp-implementation-prep` を確認してtemplate採用可否を判断する。
- 対象systemがPyQt / Qt GUIを含み、`pyqt-app-template/` が存在する場合は、`docs/reference/templates.md` を確認してtemplateをコピーしてから実装する。
- 対象systemがrealtime gateway IaC / infrastructureを含み、`microservice-infra-template/` が存在する場合は、`docs/workflows/realtime-iac.md` を確認してtemplateをコピーしてからIaC実装する。
- 対応するtemplateが存在しない場合、`decision: traditional-coding` と理由を記録し、従来どおり小さく実装する。
- template本体は直接編集しない。編集対象はコピー先service / appのみ。
- template採用時も、STOP、communication loss、startup safe state、shutdown safe state、test case table、evidence planは省略しない。
- template採用によりarchitecture、protocol、port、safety behaviorを黙って変更してはいけない。
- IaC template採用時も、shared artifacts、software inventory、public exposure、secret source、firewall policy、rollback、Terraform validationを省略しない。

Quality Gate:

- boilerplate template selection resultが記録されていない場合、Phase 7へ進まない。
- templateを採用する場合、コピー元、コピー先、採用理由、削除/無効化したcomponent、残した責務境界、必要testを記録する。
- templateがない場合、従来実装へ進む理由を記録する。

## Phase 6.7: Next.js Webapp Implementation Preparation

Next.js画面機能を含む場合、Implementation前に `.ariadne/prompts/nextjs-webapp-implementation-prep.prompt.md` に従い、次を作成します。

```text
work/<採番ID>/process-report/nextjs-webapp-implementation-prep.md
```

確認:

- 新規webappか既存webapp拡張か
- `nextjs-app-template` の採用可否
- route、screen、user action、loading / empty / error state
- `WEB_SYS_*.svg` がある場合の `web-ui/` responsive layout、component mapping、Playwright候補
- API request / response / error response / auth
- `.env.example`、`NEXT_PUBLIC_*`、server-only env、secret ownership
- typecheck、lint、unit、e2e、health、UI smoke、API connectivity、Docker smoke

Quality Gate:

- `Implementation may start: yes` になるまでPhase 7へ進まない。
- 新規app以外ではtemplateを既存sourceへ丸ごとコピーしない。
- API契約やauth policyが未定のまま画面実装を始めない。
- `WEB_SYS_*.svg` がある場合は、`.ariadne/prompts/web-svg-layout-mode.prompt.md`を実行し、`work/<採番ID>/web-ui/`のreviewとvalidateを確認してからsourceへ統合する。

## Phase 7: Implementation

承認された architecture、test strategy、PyQt QTest source plan、boilerplate template selection result に沿って実装します。

原則:

- 小さく実装する
- safety-critical behavior を暗黙に変更しない
- protocol / port / timeout を黙って変えない
- STOP path を常に優先する
- logs / telemetry を後付けにしない
- matching boilerplate templateが存在する場合は、それをコピーして開始する
- matching boilerplate templateが存在しない場合は、従来どおりにcodingする
- boilerplate template本体を直接編集しない
- template由来の責務分離を崩す場合は、承認済みarchitecture上の理由をimplementation reportに記録する

出力:

- source code
- tests
- implementation report
- boilerplate application notes when a template is used
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

実行結果は、test case IDに紐づけて次へ保存します。

```text
docs/evidence/issue-<issue-number>/ut/
docs/evidence/issue-<issue-number>/integration/
docs/evidence/issue-<issue-number>/human_check/
```

Quality Gate:

- critical / high safety finding が残っている場合は field test に進まない
- `unit-test-cases.md`、`integration-test-cases.md`、`human-check-list.md` の該当ファイルと実エビデンスが揃っていない場合はpushしない

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
