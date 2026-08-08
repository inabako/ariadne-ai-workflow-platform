# Workflow Flowchart Process Tables

`workflow-flowcharts.md` の Mermaid 図を、業務工程ごとの表として読み替えるための解説です。

この document は実行手順の source of truth ではありません。詳細手順、停止条件、成果物形式は `docs/workflows/`、`.agents/skills/<skill-name>/SKILL.md`、`templates/` を優先します。

## 読み方

| 項目 | 意味 |
| --- | --- |
| 業務工程 | 人間やAIが判断しやすい作業単位 |
| 対象workflow | 主に対応する flowchart / slash command / Skill |
| 入口 | その工程を始めるために必要な入力 |
| 主な作業 | 図のnodeを業務作業へ言い換えたもの |
| 出力 | 次工程へ渡す成果物 |
| Gate / Stop | 人間確認、停止条件、差し戻し条件 |

## 全体の工程マップ

| 業務工程 | 対象workflow | 入口 | 主な作業 | 出力 | Gate / Stop |
| --- | --- | --- | --- | --- | --- |
| 要件化 | Requirement Discovery | 箇条書き草案 | 草案確認、Noise Reduction、Human Interview、不足質問、RAG / 外部Web補助、review draft作成 | 完成版要件定義書 | Noise ReductionがBLOCK、またはHuman OKなしの場合は完成版として保存しない |
| 新規システム設計 | Ariadne New System | 完成版要件定義書 | intake、Issue / branch、RAG load、intent、安全、architecture、runtime / network / deployment、test strategy | `work/<receipt-id>/` の設計/試験成果物 | STOP、通信断、起動安全、終了安全が未定義なら実装しない |
| 新規システム + IaC連携 | Ariadne New System + Realtime IaC | 完成版要件定義書 | 新システム設計、Shared Artifacts生成、validator、IaC handoff | validated Shared Artifacts、IaC handoff | validator が fail の場合は IaC へ進まない |
| 既存システム保守 | Ariadne Feature Maintenance | 完成版要件定義書またはincident | repository sync、current state、impact、risk、change design、test plan、implementation | issue branch、変更、検証証跡 | 影響範囲やriskが未整理なら実装へ進まない |
| IaC設計/生成 | Realtime IaC | 完成版要件定義書、shared artifacts | repo mode判定、RAG load、shared artifact gate、network/security/runtime/observability設計、IaC実装、検証 | IaC artifacts、検証証跡、docs | 必須shared artifacts、公開範囲、secret source、firewall policyが未定義なら停止 |
| 改善点調査 | Corrective Action Report | target repository / branch | read-only調査、RAG load、必要時外部Web / specialist review、finding整理 | corrective action report、RAG候補 | source変更はしない |
| 専門レビュー構造化 | Review Council Runtime | intent、変更file、evidence、review対象 | review plan、session、handoff、specialist review、finding、challenge、evidence gate、verdict、knowledge capture | Review Council session、summary、verdict、RAG候補 | blocking issue、未検証evidence、未完了challenge、Human Gate不足があれば承認扱いにしない |
| 期待駆動設計 | Expectation-Driven Design Flow | requirement、usage note、design candidate | usage context、expectation extraction、candidate scaffold、feasibility、review、multi-axis、trade-off、comparison、Human Gate、refinement、contracts、verification、feedback | expectation artifacts、design comparison report、selected design、interaction contracts、verification / feedback | confidence / evidence_refs不足、Critical違反、Review Council blocker、Human decision不足があれば次工程へ渡さない |
| Runtime追跡 | Runtime Observability / Trace | workflow prompt、aiwfctl command、active trace state | trace begin / command event / trace status / trace end、sequence管理、runtime event log、test log出力 | `logs/runtime/runtime-events.log`、`logs/runtime/active-trace.json`、`logs/test/...` | workflow単位で追跡する場合はactive traceを開始し、終了漏れを残さない |
| 改善実装 | Corrective Action Fix | target repository / branch、改善report | base checkout、RAG、Issue、branch、実装、test、human gate、PR材料 | issue branch、PR材料、知識回収候補 | Issue作成、push、PRは人間承認gateを通す |
| Docs同期 | Docs Sync | target repository / branch | docs drift analysis JSON、Issue、docs-only update、commit / push | docs差分、RAG候補 | code変更を混ぜない |
| GitHub知識保守 | GitHub Knowledge Maintenance | target repository、scan / repair mode | GitHub metadata収集、知識gap発見、repair proposal、Human Review、GitHub sync、RAG publish | analysis JSON、repair proposal、RAG候補 | GitHub mutation と RAG publish は承認後 |
| VSCode環境整備 | VSCode Environment | target workspace | workspace requirement、validation、design、preflight、`.vscode` 実装、test evidence | `.vscode/*`、workspace docs、test evidence | validation fail は open questions へ戻す |
| 完了後知識回収 | Knowledge Capture | 完了Issue作業 | PR材料、Mermaid sequence、evidence確認、push、PR、RAG/docs候補、archive readiness | PR文面、RAG候補、archive準備 | evidence不足ならpush/PR前に停止 |
| RAG構築/読込 | RAG Build / Load | Markdown source reports | JSON正規化、chunk化、ingestion optimization、optimized chunks、index、local embeddings、任意のDuckDB migration、dispatcher、context pack | `work/db/ariadne-knowledge-platform/rag/normalized/`、`chunks/`、`optimized-chunks/`、`indexes/`、`embeddings/`、`retrieval/`、`rag-build-run-latest.json` | source report のmetadata不足、吸収品質不足、Human Check対象chunkは補正または停止 |
| 外部Web知識補助 | External Web RAG | knowledge gap | source reviewer、claims / metadata / verification notes、category file、dispatcher、specialist review | trusted external knowledge record、内部RAG候補 | 外部知識はrepo evidenceや人間承認済み知見を上書きしない |

## Requirement Discovery

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| 草案受領 | Draft requirement bullets | 箇条書きや未整理メモを入口にする | draft inspection | draftが無い場合は開始しない |
| 草案確認 | Inspect draft | repository、branch、安全、通信断などの不足を確認する | blocking clarification判定 | critical blockerがあれば質問へ |
| ノイズ除去 | Noise Reduction Phase / Human Interview sheet | 未知語、用語衝突、別名、文書矛盾、曖昧表現、AI誤認ポイント、業務ルール欠落を洗い出す | noise-reduction成果物、Project Glossary、Readiness | ReadinessがBLOCKならreview draftへ進まない |
| 人間質問 | Ask human questions / Review answers | 推測で補完せず、人間に確認する | 回答反映済みdraft | 回答不足なら再質問 |
| 知識補助 | Internal RAG / External Web RAG / Specialist QA support | 要件化に必要な知識gapを補う | review draft素材 | 外部知識はsupporting reference扱い |
| 要件draft作成 | Requirement review draft | 人間が確認できる完成候補を作る | review draft | Human OK が必要 |
| 完成保存 | Save completed requirement | 後続workflowの正式入力を作る | `work/requirements/<requirements>.md` | OKなしでは保存しない |

## Ariadne New System

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| 受領/準備 | Completed requirement / Intake / repository sync | 要件とrepository controlを確認する | Issue draft | intake未完了なら停止 |
| GitHub作業準備 | Issue draft / create / Create linked issue branch | 作業単位とbranchを固定する | issue branch | 副作用は人間承認後 |
| 知識読込 | RAG load | 過去finding、設計判断、test gapを読む | context pack | 関連知識がある場合は記録 |
| 目的/運用整理 | Intent / operational context | system目的、利用場面、責務を明確にする | safety工程 | operator責務不明ならQA |
| 安全設計 | Hazard and safety requirements | STOP、通信断、起動安全、終了安全を定義する | architecture | safety-critical未定義なら実装不可 |
| architecture設計 | Architecture | component、責務境界、通信を設計する | runtime / network / deployment | 境界不明なら戻す |
| 実行/配備設計 | Runtime / network / deployment design | runtime、network、deploymentを整理する | test strategy | port / deployment不明ならQA |
| 試験戦略 | Test strategy / QTest source plan / Web SVG Layout Mode | unit、integration、bench、human check、QTest候補、Web layout / Playwright候補を整理する | implementation | test case tableなし、またはWeb SVG候補未reviewのまま実装へ進まない |
| 実装/検証 | Implementation / Integration / bench test / Limited field test | 実装し、段階的に確認する | release / handover | bench / field未実施はriskとして残す |

## Ariadne New System + Realtime IaC

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| 新システム設計 | New system workflow / Intent / safety / architecture | アプリ/システム側の目的と責務を固める | runtime / network / deployment design | safetyや責務が未定義なら戻す |
| Shared Artifacts生成 | Requirements / Communication specification / Port definition / Network boundary / ADR / Software inventory | IaCへ渡すsingle source of truthを作る | Shared Artifact Validator | port、route、公開範囲を推測しない |
| Validator | Shared Artifact Validator / Validation judgment | IaCへ渡せる品質か判定する | pass / conditional-pass / fail | failはopen questionsまたは設計へ戻す |
| 条件付き承認 | Human approves conditions? | residual risk付きで進めてよいか確認する | Realtime IaC handoff | 承認なしなら戻す |
| IaC連携 | Realtime IaC handoff / Realtime IaC workflow | validated artifactをIaC工程へ渡す | IaC design / generation / validation / docs | handoff JSONにsource artifactを明示 |

## Ariadne Feature Maintenance

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| 受領/準備 | Completed requirement or incident / Intake / repository sync | 変更要望またはincidentを正式な作業にする | Issue / branch | 要件が曖昧なら要件化へ戻す |
| 現状把握 | Current state capture | 現行実装、docs、テスト、運用状態を確認する | impact analysis | current state不明のまま設計しない |
| 影響分析 | Impact analysis / Specialist review / Risk classification | 変更影響、安全/通信/runtime riskを整理する | change design | high riskは専門reviewへ |
| 変更設計 | Change design | 最小変更と責務境界を決める | test plan | 既存挙動の暗黙変更は禁止 |
| 試験計画 | Test plan / QTest source plan / Web SVG Layout Mode | 回帰、結合、human check、QTest候補、Web layout / Playwright候補を作る | implementation | test planなし、またはWeb SVG候補未reviewのまま実装しない |
| 実装/確認 | Implementation / Verification / Deployment plan / Post-change observation | 実装、検証、配備計画、変更後観察を行う | 完了報告 | observation不足はresidual risk |

## Realtime IaC

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| 受領/準備 | Completed requirement / Pre-development preparation | repository modeと前提を確認する | repository mode判定 | Repository Controlなしは停止 |
| repository mode分岐 | existing / precreated-new | 既存repoか新規precreated repoかで順序を分ける | issue branchまたはinitial branch | empty repoはinitial push後にissue branch |
| 知識読込 | RAG load | deployment、startup、network、security、observabilityの過去知識を読む | shared artifact gate | relevant findingを記録 |
| Shared Artifact Gate | Required shared artifacts present? | 通信仕様、port、network boundary、software inventoryを確認する | requirements organization | 不足時は `open-questions.md` で停止 |
| 設計 | Requirements organization / Network security / Runtime / Observability | IaCの設計入力を固定する | IaC implementation | public exposure、secret source、firewall不明なら停止 |
| 実装 | IaC implementation | Docker Compose、systemd、firewall、monitoring、docsなどを生成する | security review | `.env` やreal secretは生成しない |
| security review | Security review / High critical finding? | 公開port、secret、権限、firewall整合を確認する | validation | high / critical は設計へ戻す |
| 検証/引継ぎ | Docker Desktop / Linux runtime / Integration / Documentation | 段階的に検証し運用docsへ残す | handoff | 実行不可項目はskip reasonとriskを記録 |

## Corrective Action Report

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| 調査準備 | Target repository / branch | 調査対象を固定する | read-only inspection | source変更しない |
| repo evidence収集 | Read-only inspection | 実装、docs、tests、workflow gapを確認する | RAG load | evidenceなしfindingを避ける |
| 知識補助 | Internal RAG load / External Web RAG / Specialist review | 過去知見や外部一次情報で補助する | findings | 外部claimはrepo evidenceへ結び直す |
| report作成 | Findings with repo evidence / Corrective action report | 改善点、risk、missing testsを整理する | RAG capture candidates | 修正は行わない |

## Review Council Runtime

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| review計画 | Review plan / Review Council session | intent、変更file、evidence、guardrails、必要reviewerを固定する | review session | review対象とrevisionが曖昧なら開始しない |
| handoff | Reviewer handoff packets / Orchestrate / next action | reviewer別に読むべきcontextと次アクションを切り出す | specialist run packet | Runtimeが専門Agentを無承認で起動しない |
| finding登録 | Run specialist / Draft findings / Add finding | Specialist reportをFinding contractへ寄せ、必要なものだけ正式登録する | Review issue aggregation | draft findingを未確認のままverdictへ混ぜない |
| 反証/再検査 | Challenge round / Human gate / reinspection | counterexample、未解決issue、修正後evidenceを確認する | evidence gate | counterexampleが残る場合はHuman Gateまたは再検査へ戻す |
| evidence確認 | Evidence gate | finding evidence、required tests、Review Council artifactの存在を検査する | verdict policy | evidence未検証なら承認扱いにしない |
| verdict/知識化 | Verdict policy / Knowledge capture / Review Council RAG build bridge | `APPROVED`、`APPROVED_WITH_RISK`、`CHANGES_REQUIRED` などを判定し、再利用知識へ接続する | Review Council summary、verdict、RAG source候補 | risk acceptanceやfinal verdictのHuman Gate不足を残す |

## Expectation-Driven Design Flow

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| 初期化 | Expectation design init / Usage context scaffold / Expectation set | `work/<work-id>/design/expectation/` に期待駆動設計の作業領域とJSON artifactを作る | usage-context、expectation-set、weights、critical expectations | JSON source artifactを正本にし、YAMLへ戻さない |
| 候補scaffold | Design candidate scaffold / Candidate concept / flow / wireframe | 自動生成ではなく、人間が比較できる候補の器を作る | `candidates/<id>/concept.md`、`flow.json`、`wireframe.svg` | 候補を削除せず、制約付き候補はconstrainedとして残す |
| 実現性確認 | Feasibility report | 実装可能性、標準component可否、accessibility、testability、future extensibilityを構造化する | `feasibility-report.json/md` | 実現不能案も判断材料として残す |
| 期待抽出/確認 | Expectation extraction / Expectation review report | usage contextと要件文から期待を抽出し、観測可能性、重み根拠、競合、抜け漏れ、UI手段固定化を確認する | expectation-set、expectation-review-report | confidenceとevidence_refsがない期待は採用しない |
| 候補評価 | Candidate evaluation / Multi-axis evaluation / Trade-off analysis | 期待充足、UX、identity、delight、accessibility、cost、maintenance、technical feasibilityを比較する | multi-axis-evaluation、trade-off-analysis、comparison report | Critical違反や未検証項目を総合点で相殺しない |
| Review Council連携 | Review Council dispatch / Review Council feedback | 必要なcontextだけをreviewerへ渡し、UX / Accessibility / Frontend Architectureなどの指摘を比較reportへ戻す | review-council-dispatch、comparison feedback | blocking issueが残る場合はHuman decision前に戻す |
| 人間判断/精緻化 | Human decision / Selected design refinement | 選択または複数案統合の整合性を再評価し、単純な足し合わせを防ぐ | selected-design/design-specification.md | Human decisionなしではselected designへ進めない |
| 契約/検証/feedback | Interaction contracts / Expectation verification / Expectation feedback | Given/When/Then/Must Not形式の契約、設計時推定値と実装後検証値、predicted vs observedを残す | interaction-contracts、expectation-verification、expectation-feedback | verification evidenceやhuman reviewを紐付ける |

## Runtime Observability / Trace

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| trace開始 | Workflow prompt starts / aiwfctl trace begin | 1 workflow実行を1つのtrace idへ束ねる | `logs/runtime/active-trace.json` | 既存active traceがある場合は意図せず上書きしない |
| command記録 | aiwfctl command / Runtime Event Logger | command開始・完了・失敗を同じtrace idへ追記する | `logs/runtime/runtime-events.log` | secret、token、passwordなどはmaskする |
| sequence管理 | sequence continues | active trace配下ではworkflow全体で `00001` から連番にする | workflow全体の時系列 | active trace未開始時はcommand scoped traceとして `00001` / `00002` に戻る |
| 状態確認 | aiwfctl trace status | 現在のtrace id、workflow、last_sequenceを確認する | trace status JSON | 長時間workflowでは途中確認を証跡として使う |
| trace終了 | aiwfctl trace end / active trace closed | workflow完了時にactive traceを閉じる | active trace ended | 終了漏れは次workflowのtrace混入リスクとして扱う |
| 解析/再利用 | Workflow evidence / feedback analysis | Runtime logから失敗原因、blocked reason、復帰command、Feedback候補を抽出する | runtime evidence、self-improvement feedback | ログは観測sourceであり、正式判断はEvidenceやreportへ昇格して残す |

## Corrective Action Fix

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| base準備 | Base work checkout / Corrective action report | 対象branchと改善reportを揃える | RAG build / load | reportなしは先に調査へ |
| 知識補助 | RAG / External Web / Specialist review | 修正方針の根拠を強くする | Issue draft | high riskは設計へ戻す |
| Issue化 | Issue title prefix and Issue draft / Human approves Issue? | GitHub作業単位を作る | GitHub Issue | 承認なしでIssue作成しない |
| branch/実装 | Create linked issue branch / Implement fix | issue branchで修正する | test specification | scope外変更を混ぜない |
| 試験 | Test specification / QTest / Web SVG Layout / Unit integration tests | 修正の検証方法を固定し実行する | human startup / integration gate | startup/integrationは人間確認gate。Web SVG候補はreview後に採用 |
| 完了処理 | Knowledge capture / Push / Open PR | PR材料、push、PR作成へ進む | Pull Request | push/PRは承認後 |

## Docs Sync

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| drift分析 | Docs drift analysis JSON | 実装とdocsの差分を構造化する | Issue body | JSONなしでIssue化しない |
| Issue化 | Issue body / Human approves Issue? | docs-only修正の作業単位を作る | GitHub Issue | 承認なしでIssue作成しない |
| docs-only修正 | Create linked issue branch / Docs-only update | docsだけを実装に合わせる | commit / push | code変更を混ぜない |
| 知識回収 | Knowledge capture candidates | docs driftから再利用知見を抽出する | RAG candidate | RAG登録は承認後 |

## GitHub Knowledge Maintenance

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| context初期化 | Target repository / scan mode / repair mode / Initialize work context | 対象repoと調査modeを固定する | metadata collection plan | repo未指定なら開始しない |
| GitHub evidence収集 | Read GitHub Issues / PRs / comments / releases | GitHub上の説明資産を集める | evidence判定 | CLI/API不足時はclone承認gate |
| 知識発見 | Knowledge asset discovery / Narrative analysis | intent、scope、decision、maintenance知識を抽出する | consistency analysis | Git履歴自体はなかったことにしない |
| 整合確認 | Issue -> PR -> Review -> Comment -> Docs consistency | 説明不足や不一致を見つける | repair proposals | source code修正ではなく説明資産修正 |
| 人間確認 | Human Review / Approved GitHub sync actions? | GitHub mutation可否を確認する | sync actionまたはproposal更新 | 承認なしでGitHub編集しない |
| publish | Knowledge DB candidates / RAG output approved? | RAG候補を正式公開する | approved RAG candidate | RAG publishは承認後 |

## VSCode Environment

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| 要件整理 | Target workspace / Workspace requirements | workspaceの目的と必要toolを整理する | validation | 入力不足はopen questions |
| validation | Shared artifact validation / Validation judgment | 実装してよい前提か確認する | designまたはopen questions | failは戻す、conditionalは承認gate |
| design | VSCode design / Terminal design | settings、tasks、launch、extensions、terminalを設計する | preflight | shellやtool未定義ならQA |
| 実装/検証 | Environment preflight / Implement .vscode files / Workspace tests and evidence | `.vscode` を作り検証する。multi-rootが必要な場合のみworkspace fileをoptionalで扱う | setup docs | evidenceなしで完了扱いにしない |
| docs化 | Setup and troubleshooting docs | 再現手順とトラブル対応を残す | 完了 | 日本語出力を基本にする |

## Knowledge Capture

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| PR材料作成 | Generate PR materials / Add Mermaid sequence diagram | PR説明、sequence、変更要約を作る | evidence確認 | issueとのtraceを残す |
| evidence確認 | Confirm docs evidence / Evidence complete? | test evidenceとdocs evidenceを確認する | pushまたはstop | 不足時はpush前に停止 |
| PR化 | Push issue branch / Open PR to develop | issue branchをpushしPRを作る | PR | push/PRは承認後 |
| 知識回収 | RAG / docs candidates / Archive readiness | 再利用知識とarchive準備を整える | RAG候補 | RAG登録/移動は承認後 |

## RAG Build / Load

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| 正規化 | Markdown source reports / Normalize JSON | Markdown reportを機械処理可能にする | normalized JSON | metadata不足は補正または停止 |
| chunk/最適化 | Chunk documents / Ingestion optimization / Optimized chunks | chunk候補を評価し、ACCEPT済みchunkだけをindex / embedding対象にする | optimized-chunks、ingestion evidence | HUMAN_CHECKやREJECTを無理に吸収しない |
| index/embedding | Build JSONL indexes / Local embeddings / rag-build-run-latest.json | file-based検索とlocal embeddingの生成結果を再現可能に残す | indexes、embeddings、rag-build-run | source traceを残し、外部providerに依存しない |
| DuckDB投影 | DuckDB migrate / Generated DuckDB read model | 必要な場合だけfile-based artifactを検索・監査用read modelへ投影する | `db/rag/ariadne-knowledge.duckdb`、migration evidence | DuckDBをsource of truthにしない |
| 検索/配布 | RAG load query planning / Retrieve / Context packs | 後続workflowへ圧縮contextを渡す | development / review workflow | raw bodyを無制限に持ち回らない |

## External Web RAG

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| gap定義 | Knowledge gap / knowledge-sources.md | 何を外部Webで補うか明確にする | source reviewer | 広く雑に収集しない |
| source review | External Web Source Reviewer | 一次情報や信頼できる出典を確認する | claims / metadata / notes | 出典と検証メモを残す |
| RAG化 | work/db/ariadne-knowledge-platform/rag/external-web category files / Dispatcher | categoryごとに再利用可能にする | specialist review | 外部記事本文の過剰保存を避ける |
| 採用判断 | Specialist review / Trusted external knowledge record | 採用/不採用claimと検証方法を記録する | Internal RAG candidate | 内部RAG化は承認後 |
