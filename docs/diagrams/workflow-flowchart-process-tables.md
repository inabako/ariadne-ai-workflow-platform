# Workflow Flowchart Process Tables

`workflow-flowcharts.md` の Mermaid 図を、業務工程ごとの表として読み替えるための解説です。

この document は実行手順の source of truth ではありません。詳細手順、停止条件、成果物形式は `docs/workflows/`、`skills/<skill-name>/SKILL.md`、`templates/` を優先します。

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
| 改善実装 | Corrective Action Fix | target repository / branch、改善report | base checkout、RAG、Issue、branch、実装、test、human gate、PR材料 | issue branch、PR材料、知識回収候補 | Issue作成、push、PRは人間承認gateを通す |
| Docs同期 | Docs Sync | target repository / branch | docs drift analysis JSON、Issue、docs-only update、commit / push | docs差分、RAG候補 | code変更を混ぜない |
| GitHub知識保守 | GitHub Knowledge Maintenance | target repository、scan / repair mode | GitHub metadata収集、知識gap発見、repair proposal、Human Review、GitHub sync、RAG publish | analysis JSON、repair proposal、RAG候補 | GitHub mutation と RAG publish は承認後 |
| VSCode環境整備 | VSCode Environment | target workspace | workspace requirement、validation、design、preflight、`.vscode` 実装、test evidence | `.vscode/*`、workspace docs、test evidence | validation fail は open questions へ戻す |
| 完了後知識回収 | Knowledge Capture | 完了Issue作業 | PR材料、Mermaid sequence、evidence確認、push、PR、RAG/docs候補、archive readiness | PR文面、RAG候補、archive準備 | evidence不足ならpush/PR前に停止 |
| RAG構築/読込 | RAG Build / Load | Markdown source reports | JSON正規化、chunk化、index、local embeddings、dispatcher、context pack | `rag/normalized/`、`rag/chunks/`、`rag/retrieval/` | source report のmetadata不足は補正または停止 |
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
| chunk/index | Chunk documents / Build JSONL indexes | 検索単位とindexを作る | indexes | source traceを残す |
| embedding | Local embeddings | local baselineで検索可能にする | embeddings | 外部providerに依存しない |
| 検索/配布 | RAG dispatcher / Context packs | 後続workflowへ圧縮contextを渡す | development / review workflow | raw bodyを無制限に持ち回らない |

## External Web RAG

| 工程 | Flowchart node | 目的 | 出力 / 次工程 | Gate / Stop |
| --- | --- | --- | --- | --- |
| gap定義 | Knowledge gap / knowledge-sources.md | 何を外部Webで補うか明確にする | source reviewer | 広く雑に収集しない |
| source review | External Web Source Reviewer | 一次情報や信頼できる出典を確認する | claims / metadata / notes | 出典と検証メモを残す |
| RAG化 | rag/external-web category files / Dispatcher | categoryごとに再利用可能にする | specialist review | 外部記事本文の過剰保存を避ける |
| 採用判断 | Specialist review / Trusted external knowledge record | 採用/不採用claimと検証方法を記録する | Internal RAG candidate | 内部RAG化は承認後 |
