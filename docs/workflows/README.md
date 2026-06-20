# Workflow Index

このページは、Intent-Driven Robotics AI Workflow の入口を選ぶための一覧です。

## Entry Points

| Command / Skill | 使う場面 | 主な入力 | 主な出力 |
| --- | --- | --- | --- |
| `/requirement-discovery` | 箇条書き草案から要件定義書を完成させたい | `work/requirements/draft/<draft>` | `work/requirements/<requirements>.md` |
| `/robotics-new-system` | 新しいrobotics system、runtime、remote operation、device integrationを開始する | 完成版要件定義書 | `work/<receipt-id>/` |
| `/robotics-new-system-iac` | 新しいrobotics systemを設計し、Shared Artifactsを検証してからrealtime IaCへ渡す | 完成版要件定義書 | `work/<receipt-id>/`, validated Shared Artifacts, IaC artifacts |
| `/robotics-feature-maintenance` | 既存robotics systemの新機能追加、bug fix、保守開発を行う | 完成版要件定義書 | `work/<receipt-id>/` |
| `/realtime-iac` | リアルタイムシステム向けIaCを設計、生成、レビュー、検証、文書化する | 完成版要件定義書、共有通信/port/network成果物 | `work/<receipt-id>/`, IaC artifacts |
| `/corrective-action-report` | repository / branchをread-onlyで調査し、改善reportだけ作る | target repository, target branch | `rag/corrective-action-report/*.md` |
| `/corrective-action-fix` | 改善reportからIssue、branch、修正、test、pushまで進める | target repository, target branch | `work/<branch>/`, `work/issue-<number>/` |
| `/docs-sync` | 実装とdocsのズレを検出し、docsだけ修正する | target repository, target branch | `docs-drift-analysis.json`, issue branch |
| `/github-knowledge-maintenance` | GitHub Issue / PR / docs / CARを知識資産として保守する | target repository, scan mode, repair mode | `github-knowledge-analysis.json`, repair plan, RAG candidates |
| `/vscode-environment` | VSCode workspace as code、task、terminal、AI workflow、evidenceを整備する | target workspace path | `.vscode/*`, `.vscode/workspace.code-workspace`, `workspace-test.md` |
| `/knowledge-capture` | 完了IssueのPR材料、RAG候補、docs候補、archive準備を作る | `work/issue-<number>` | `knowledge-capture-report.md` |
| `/rag-build` | Markdown reportをRAG artifactへ変換する | `rag/corrective-action-report/*.md` | `rag/normalized/`, `rag/chunks/`, `rag/indexes/`, `rag/embeddings/` |
| `/rag-load` | 開発前に過去知識を検索し、圧縮contextを読む | task, repository, branch | `rag/retrieval/*.json` |
| External Web RAG | 要件定義、設計、改善flowで知見不足の領域を外部Web一次情報で補う | `rag/external-web/knowledge-sources.md` | `rag/external-web/<category>/*.md` |
| Specialist Review | 内部/外部RAGを読んだ後、成果物を専門Agentがreviewする | draft artifact, RAG context | `work/<id>/process-report/specialist-review-<domain>.md` |
| GaC / UaC GUI Mode | 親workflow内でSVGをGUI設計・PyQt6・QTest候補へ変換する | `work/requirements/svg-input/<PREFIX>_*.svg` | `work/<issue-id>/gac-uac/` |
| PyQt QTest Integration | PyQt / Qt GUIの結合疎通試験をテスト仕様書からQTestソースへ落とす | test case table | `src/tests/qt/test_<feature>_integration.py` |

## Decision Guide

| 状況 | 選ぶworkflow |
| --- | --- |
| まだ要件が箇条書きだけ | [Requirement Discovery](requirement-discovery.md) |
| 新しいrobotics systemを作る | [Robotics New System](robotics-new-system.md) |
| 新しいrobotics systemを作り、そのままDocker Compose、systemd、firewall、監視などのIaCまで連携したい | [Robotics New System + IaC](robotics-new-system-iac.md) |
| 既存systemへ機能追加、bug fix、保守対応をする | [Robotics Feature Maintenance](robotics-feature-maintenance.md) |
| Docker Compose、systemd、firewall、reverse proxy、監視などのIaCを整備したい | [Realtime IaC](realtime-iac.md) |
| まず改善点を洗い出したいが、sourceは変更しない | [Corrective Action Report](corrective-action-report.md) |
| 改善点の修正まで進めたい | [Corrective Action Fix](corrective-action-fix.md) |
| codeは変えず、docsだけ実装に合わせたい | [Docs Sync](docs-sync.md) |
| Git履歴を変えずにIssue / PR / docs / CARの説明資産を育てたい | [GitHub Knowledge Maintenance](github-knowledge-maintenance.md) |
| VSCode workspace as code、terminal、task、AI workflow起動を整えたい | [VSCode Environment](vscode-environment.md) |
| 作業完了後にPR文面と知識回収を整えたい | [Knowledge Capture](knowledge-capture.md) |
| 過去reportを検索可能にしたい | [RAG Build / Load](rag-build-load.md) |
| 要件定義、設計、改善flowで知らない技術領域が出た | [External Web RAG](external-web-rag.md) |
| 成果物の妥当性が専門知識に依存する | [Agent Inventory](../reference/agent-inventory.md) |
| PyQt GUIの結合疎通試験を自動化したい | [Corrective Action Fix](corrective-action-fix.md) |
| SVGを渡して画面実装候補とQTest候補を作りたい | [GaC / UaC GUI Mode](gui-mode.md) |

## Common Rules

- Repository / branch は user input または要件定義書の `Repository Control` を source of truth にします。
- 会話ログだけで intake 済みとは扱いません。
- GitHub Issue 作成、branch作成、push、install、archive移動などの副作用は、人間承認gateを通します。
- GitHub Issue title は workflow label をprefixにします: `[新規機能フロー]`、`[改善フロー]`、`[初期開発]`、`[IaC]`。
- `work/<branch>/` はbase調査用、`work/issue-<number>/` は実装修正用に分けます。
- 成果物は `work/<id>/context/artifact-index.json` に登録できる形で残します。
- `/robotics-new-system-iac` では、新システム設計後に Shared Artifacts を生成し、Shared Artifact Validator の `pass` または human-approved `conditional-pass` を得るまで IaC に進みません。
- RAG化する成果物は、metadata、evidence、open questions、stable section order を保ちます。
- 外部Web RAGは current code、test evidence、人間承認済み運用知見を上書きしません。
- 改善flowで外部WebRAGを使う場合、findingは必ず対象repository evidenceへ結び直します。
- Specialist Agent reviewは作業中は `work/<id>/process-report/` に保存し、人間承認後に内部RAG候補として扱います。
- Specialist Agent reviewでは、採用した外部Web RAG、採用しなかったclaim、検証方法を残します。
- 実装系workflow（`/robotics-new-system`、`/robotics-feature-maintenance`、`/corrective-action-fix`）では、テスト実行前に `unit-test-cases.md`、`integration-test-cases.md`、`human-check-list.md` を作成します。
- 実装系workflowはIssue作成後に`work/requirements/svg-input/`から`SYS_`、`FEAT_`、`FIX_`のSVGを取り込み、SVGが無ければ`skipped`で通常flowを継続します。
- GaC / UaCの`generated/`は候補であり、既存sourceへ無条件上書きしません。
- `/realtime-iac` では、IaC検証前に `iac-test-cases.md` を作成し、Docker Desktop、Linux runtime、integration、human check の分類を明示します。
- `/github-knowledge-maintenance` では、GitHub mutation前に `github-knowledge-analysis.json` と human-reviewed sync plan を必ず作成します。
- PyQt / Qt GUIでは、テストケース表からQTest化できる結合疎通試験を選別し、外部I/Oは原則stub / disableします。
- target repositoryへ残すテスト証跡は `docs/evidence/issue-<issue-number>/` に保存します。
- Issue branch push後は、Issue titleをPR titleとして `develop` へPull Requestを作成します。
