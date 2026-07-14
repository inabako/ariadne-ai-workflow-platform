# Workflow Index

このページは、Ariadne AI Workflow の入口を選ぶための一覧です。

## Entry Points

| Command / Skill | 使う場面 | 主な入力 | 主な出力 |
| --- | --- | --- | --- |
| `/requirement-discovery` | 箇条書き草案から要件定義書を完成させたい | `work/requirements/draft/<draft>` | `work/requirements/<requirements>.md` |
| `/ariadne-new-system` | 新しい対象システム、runtime、remote operation、device integrationを開始する | 完成版要件定義書 | `work/<receipt-id>/` |
| `/ariadne-new-system-iac` | 新しい対象システムを設計し、Shared Artifactsを検証してからrealtime IaCへ渡す | 完成版要件定義書 | `work/<receipt-id>/`, validated Shared Artifacts, IaC artifacts |
| `/ariadne-feature-maintenance` | 既存対象システムの新機能追加、bug fix、保守開発を行う | 完成版要件定義書 | `work/<receipt-id>/` |
| `/realtime-iac` | リアルタイムシステム向けIaC、開発・CI/CD・監視platform基盤、DB基盤、Redis middleware基盤、OpenLDAP identity基盤を設計、生成、レビュー、検証、文書化する | 完成版要件定義書、共有通信/port/network成果物、platform / database / middleware / identity component inventory | `work/<receipt-id>/`, IaC artifacts |
| `/corrective-action-report` | repository / branchをread-onlyで調査し、改善reportだけ作る | target repository, target branch | `rag/corrective-action-report/*.md` |
| `/corrective-action-fix` | 改善reportからIssue、branch、修正、test、pushまで進める | target repository, target branch | `work/<branch>/`, `work/issue-<number>/` |
| `/docs-sync` | 実装とdocsのズレを検出し、docsだけ修正する | target repository, target branch | `docs-drift-analysis.json`, issue branch |
| `/self-improvement` | workflow実行中の摩擦を採用判断し、改善Issueへつなぐ | workflow feedback | `work/feedback/*.md`, issue body, evidence scaffold |
| `/github-knowledge-maintenance` | GitHub Issue / PR / docs / CARを知識資産として保守する | target repository, scan mode, repair mode | `github-knowledge-analysis.json`, repair plan, RAG candidates |
| `/vscode-environment` | VSCode workspace as code、task、terminal、AI workflow、evidenceを整備する | なし、target workspace path、またはcustom-design draft | `.vscode/*`, `workspace-test.md` |
| `/flutter-multiplatform` | Flutterアプリの対象platform、環境、boilerplate、test、build計画、evidenceを整理する | `work/<work-id>/requirements/flutter-targets.yaml` または `--targets` | `flutter-development-context.json`, `flutter-multiplatform-report.md` |
| `/knowledge-capture` | 完了IssueのPR材料、RAG候補、docs候補、archive準備を作る | `work/issue-<number>` | `knowledge-capture-report.md` |
| `/rag-build` | Markdown reportをRAG artifactへ変換する | `rag/corrective-action-report/*.md` | `rag/normalized/`, `rag/chunks/`, `rag/indexes/`, `rag/embeddings/` |
| `/rag-load` | 開発前に過去知識を検索し、圧縮contextを読む | task, repository, branch | `rag/retrieval/*.json` |
| `/runtime-health-check` | Ariadne自身のruntime、pytest、UT仕様書、Context First、docs品質を自己診断する | なし | `runtime/.pytest_cache/pytest-ut-spec-sync-report.*`, `context-manifest.json` |
| External Web RAG | 要件定義、設計、改善flowで知見不足の領域を外部Web一次情報で補う | `rag/external-web/knowledge-sources.md` | `rag/external-web/<category>/*.md` |
| Specialist Review | 内部/外部RAGを読んだ後、成果物を専門Agentがreviewする | draft artifact, RAG context | `work/<id>/process-report/specialist-review-<domain>.md` |
| Noise Reduction Phase | 要件定義前に未知用語、用語衝突、表記揺れ、資料矛盾、曖昧表現を除去する | requirement draft, related docs, RAG, glossary | `work/requirements/draft/<draft-stem>-noise-reduction/` |
| GaC / UaC GUI Mode | 親workflow内でSVGをGUI設計・PyQt6・QTest候補へ変換する | `work/requirements/svg-input/<PREFIX>_*.svg` | `work/<issue-id>/gac-uac/` |
| Next.js Webapp Implementation Prep | 親workflow内でNext.js画面機能の実装前準備を行う | requirements, UI/API contract, target app path | `work/<id>/process-report/nextjs-webapp-implementation-prep.md` |
| Web SVG Layout Mode | 親workflow内でSVGをWeb layout・React候補・Playwright候補へ変換する | `work/requirements/svg-input/WEB_<PREFIX>_*.svg` | `work/<issue-id>/web-ui/` |
| MCP Server Group Implementation | MCP Server群、MCP Client、Agent Runtime、Discord Gateway boilerplateを境界確認付きで展開する | `--components local-model-mcp-server,mcp-client,local-ai-agent-runtime,discord-gateway` | `work/<work-id>/implementation/mcp-server-group/` |
| PyQt QTest Integration | PyQt / Qt GUIの結合疎通試験をテスト仕様書からQTestソースへ落とす | test case table | `src/tests/qt/test_<feature>_integration.py` |

## Decision Guide

| 状況 | 選ぶworkflow |
| --- | --- |
| まだ要件が箇条書きだけ | [Requirement Discovery](requirement-discovery.md) |
| 要件化前に未知用語、表記揺れ、資料矛盾、曖昧表現を整理したい | [Noise Reduction Phase](noise-reduction-phase.md) |
| 新しい対象システムを作る | [Ariadne New System](ariadne-new-system.md) |
| 新しい対象システムを作り、そのままDocker Compose、systemd、firewall、監視などのIaCまで連携したい | [Ariadne New System + IaC](ariadne-new-system-iac.md) |
| 既存対象システムへ機能追加、bug fix、保守対応をする | [Ariadne Feature Maintenance](ariadne-feature-maintenance.md) |
| Docker Compose、systemd、firewall、reverse proxy、監視、GitLab / Jenkins / Grafana / Zabbix基盤、PostgreSQL / MySQL基盤、Redis基盤、OpenLDAP基盤を整備したい | [Realtime IaC](realtime-iac.md) |
| まず改善点を洗い出したいが、sourceは変更しない | [Corrective Action Report](corrective-action-report.md) |
| 改善点の修正まで進めたい | [Corrective Action Fix](corrective-action-fix.md) |
| codeは変えず、docsだけ実装に合わせたい | [Docs Sync](docs-sync.md) |
| workflowの摩擦や改善候補をIssue化したい | [Self-Improvement](self-improvement.md) |
| Git履歴を変えずにIssue / PR / docs / CARの説明資産を育てたい | [GitHub Knowledge Maintenance](github-knowledge-maintenance.md) |
| VSCode workspace as code、terminal、task、AI workflow起動を整えたい | [VSCode Environment](vscode-environment.md) |
| Flutterアプリのmulti-platform target、環境、test、build計画を整理したい | [Flutter Multi-platform](flutter-multiplatform.md) |
| 作業完了後にPR文面と知識回収を整えたい | [Knowledge Capture](knowledge-capture.md) |
| 過去reportを検索可能にしたい | [RAG Build / Load](rag-build-load.md) |
| Ariadne自身のruntime、pytest、UT仕様書、Context First、docs品質を確認したい | [Runtime Health Check](runtime-health-check.md) |
| 要件定義、設計、改善flowで知らない技術領域が出た | [External Web RAG](external-web-rag.md) |
| 成果物の妥当性が専門知識に依存する | [Agent Inventory](../reference/agent-inventory.md) |
| PyQt GUIの結合疎通試験を自動化したい | [Corrective Action Fix](corrective-action-fix.md) |
| SVGを渡して画面実装候補とQTest候補を作りたい | [GaC / UaC GUI Mode](gui-mode.md) |
| Next.js画面機能を実装する前に、画面/API/auth/env/testを揃えたい | [Next.js Webapp Implementation Prep](nextjs-webapp-implementation-prep.md) |
| SVGを渡してWeb画面のlayout、React候補、Playwright候補を作りたい | [Web SVG Layout Mode](web-svg-layout-mode.md) |
| MCP Server群をboilerplateから境界分離した形で実装準備したい | [MCP Server Group Implementation](mcp-server-group-implementation.md) |

## Common Rules

- Repository / branch は user input または要件定義書の `Repository Control` を source of truth にします。
- 会話ログだけで intake 済みとは扱いません。
- `/requirement-discovery` では、要件review draft作成前にNoise Reduction Phaseを実行し、Readinessが`BLOCK`の場合は完成版要件定義書を保存しません。
- GitHub Issue 作成、branch作成、push、install、report-only close archive準備 / pruneなどの副作用は、人間承認gateを通します。
- GitHub Issue title は workflow label をprefixにします: `[新規機能フロー]`、`[改善フロー]`、`[初期開発]`、`[IaC]`。
- `work/<branch>/` はbase調査用、`work/issue-<number>/` は実装修正用に分けます。
- 各AI workflow実行中に摩擦、迷い、手戻り、docs不足、runtime観測不足、重複確認などの改善候補を見つけた場合は、`work/feedback/` 直下へFeedback reportを保存します。
- 通常workflowではFeedback reportを `Proposed` として残し、`/self-improvement` は自動実行しません。Feedbackがたまった後に `/self-improvement` を実行して採用 / 不採用 / 保留を判断します。
- `/self-improvement` のFeedbackは `work/feedback/` 直下のreportに保存し、採用 / 不採用 / 保留は同じreportへ追記します。詳細は [Workflow Feedback](../reference/workflow-feedback.md) を確認します。
- 成果物は `work/<id>/context/artifact-index.json` に登録できる形で残します。
- `/ariadne-new-system-iac` では、新システム設計後に Shared Artifacts を生成し、Shared Artifact Validator の `pass` または human-approved `conditional-pass` を得るまで IaC に進みません。
- RAG化する成果物は、metadata、evidence、open questions、stable section order を保ちます。
- 外部Web RAGは current code、test evidence、人間承認済み運用知見を上書きしません。
- 改善flowで外部WebRAGを使う場合、findingは必ず対象repository evidenceへ結び直します。
- Specialist Agent reviewは作業中は `work/<id>/process-report/` に保存し、人間承認後に内部RAG候補として扱います。
- Specialist Agent reviewでは、採用した外部Web RAG、採用しなかったclaim、検証方法を残します。
- 実装系workflow（`/ariadne-new-system`、`/ariadne-feature-maintenance`、`/corrective-action-fix`）では、テスト実行前に `unit-test-cases.md`、`integration-test-cases.md`、`human-check-list.md` を作成します。
- 実装系workflowはIssue作成後に`work/requirements/svg-input/`から`SYS_`、`FEAT_`、`FIX_`のSVGを取り込み、SVGが無ければ`skipped`で通常flowを継続します。
- GaC / UaCの`generated/`は候補であり、既存sourceへ無条件上書きしません。
- Next.js画面機能を実装する場合、Implementation前に `nextjs-webapp-implementation-prep.md` を作成し、新規appか既存app拡張か、template採用可否、画面契約、API契約、auth、env、test evidenceを明示します。
- Web画面向けSVGがある場合は`WEB_SYS_`、`WEB_FEAT_`、`WEB_FIX_`を使い、`web-ui/generated/`は候補としてreview後に採用部分だけ統合します。
- Flutterを扱う場合は、`work/<work-id>/requirements/flutter-targets.yaml` または `aiwfctl flutter ... --targets` で対象platformを明示します。未指定時にAndroid/iOS/Web/Desktop全部とはみなしません。
- `/realtime-iac` では、IaC検証前に `iac-test-cases.md` を作成し、Docker Desktop、Linux runtime、integration、human check の分類を明示します。
- `/github-knowledge-maintenance` では、GitHub mutation前に `github-knowledge-analysis.json` と human-reviewed sync plan を必ず作成します。
- PyQt / Qt GUIでは、テストケース表からQTest化できる結合疎通試験を選別し、外部I/Oは原則stub / disableします。
- target repositoryへ残すテスト証跡は `docs/evidence/issue-<issue-number>/` に保存します。
- Issue branch push後は、Issue titleをPR titleとして `develop` へPull Requestを作成します。
