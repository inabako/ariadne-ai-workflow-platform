# Documentation Guide

この `docs/` は、Ariadne AI Workflow Platform を運用するための日本語ドキュメント置き場です。

Repository root の `README.md` は入口と索引に絞り、workflow の詳細手順、runtime、RAG、template、skill discovery などはここに分散します。

## 読む順番

1. [Brand Guide](brand/README.md)
   - Ariadneという名前、Context Firstの思想、糸巻の意味、AIと人間の役割を確認する。
2. [Platform Governance](governance/ariadne/README.md)
   - 改善時に守る設計思想、責任境界、Platform Fit Checkを確認する。
3. [Workflows](workflows/README.md)
   - どの slash command / Skill を使うかを決める。
4. [Repository Structure](reference/repository-structure.md)
   - この repository の directory 役割を確認する。
5. [Runtime](reference/runtime.md)
   - workflow を支える CLI と副作用境界を確認する。
6. [Context First Architecture](reference/context-first-architecture.md)
   - Dispatcher Contextを先に作り、WorkflowがContextを第一入力にする原則を確認する。
7. [Environment Selection](reference/environment-selection.md)
   - `aiwfctl env` による実行環境 profile 選択を確認する。
8. [Templates](reference/templates.md)
   - 要件、設計、process report、test evidence のひな形を確認する。
9. [Workflow Feedback](reference/workflow-feedback.md)
   - 各AI workflow実行時に改善候補を `work/feedback/` へ残し、後で `/self-improvement` で採用判断する流れを確認する。
10. [RAG](reference/rag.md)
   - corrective action report を検索可能な知識へ変換する流れを確認する。
11. [Test Artifact Storage](reference/test-artifact-storage.md)
   - テスト仕様書、QTest、結合疎通証跡、target repo docsへの保存先を確認する。
12. [Mermaid Diagrams](diagrams/README.md)
   - 各AI workflowの動作イメージをflowchartで確認する。
   - Dispatcher群とWorkflowの関係は [Dispatcher / Workflow Map](diagrams/dispatcher-workflow-map.md) を確認する。
13. [Architecture Overview](architecture/overview.md)
   - OSS公開前に、aiwfctl、runtime、workflow dispatch、state、artifact、evidence、Human Gate、復帰処理の全体像を確認する。
14. [Release Policy](release/release-policy.md)
   - release checklist、versioning、manifest、公開前検証の流れを確認する。
15. [License Policy](legal/license-policy.md)
   - `AGPL-3.0-or-later` 方針、生成物への非波及方針、公開前の法務レビュー事項を確認する。

## Governance Docs

| Document | Purpose |
| --- | --- |
| [Platform Governance](governance/ariadne/README.md) | Governance全体の入口、各文書へのリンク、Self-Improvement Workflowとの関係 |
| [Platform Governance Charter](governance/ariadne/platform-governance.md) | Ariadne全体のMission、Philosophy、Core Principles、Non Goals |
| [Architecture Principles](governance/ariadne/architecture-principles.md) | 責務分離、Context First、Dispatcher First、Human Check、UTF-8などの設計原則 |
| [Workflow Evolution Policy](governance/ariadne/workflow-evolution-policy.md) | Feedback、Issue、Human Review、Evidenceへつなぐworkflow改善方針 |
| [Human Responsibility](governance/ariadne/human-responsibility.md) | HumanとAI Agentの責任境界 |
| [Platform Fit Check](governance/ariadne/platform-fit-check.md) | 改善案がplatform思想に適合するか判断するchecklist |
| [Repository Governance](governance/ariadne/repository-governance.md) | Repository Curation、branch、Issue、Evidence、UTF-8、RAG、DuckDB運用方針 |
| [Implementation Governance](governance/implementation/README.md) | Ariadneが生成・変更・保守する成果物の実装規約 |

## Brand Docs

| Document | Purpose |
| --- | --- |
| [Brand Guide](brand/README.md) | Ariadneの名前、物語、思想、logo motifを読む入口 |
| [Prologue — Ariadne AI Workflow Platform](brand/prologue.md) | このplatformが生まれた背景と最初の問い |
| [Philosophy — Ariadne AI Workflow Platform](brand/philosophy.md) | Mission、Value、Human Responsibility、Design Principle |
| [なぜ糸巻なのか？](brand/why-a-spool.md) | 糸巻というlogo motifが象徴するContext、Evidence、Human Check、帰還路 |
| [Epilogue — Ariadne AI Workflow Platform](brand/epilogue.md) | Ariadneという名前とContext Firstの物語的背景 |
| [商標とブランド利用](brand/trademarks.md) | ARIADNEの名称、logo、visual identityの利用境界 |
| [Trademarks](brand/trademarks.en.md) | English trademark and brand usage policy |

## Workflow Docs

| Document | Purpose |
| --- | --- |
| [Workflow Index](workflows/README.md) | 全workflowの選択基準と入出力 |
| [Requirement Discovery](workflows/requirement-discovery.md) | 箇条書き草案から完成版要件定義書を作る |
| [Noise Reduction Phase](workflows/noise-reduction-phase.md) | 要件定義前に未知用語、表記揺れ、資料矛盾、曖昧表現、Human Interview、Project Glossaryを作る |
| [Ariadne New System](workflows/ariadne-new-system.md) | 新しい対象システムを立ち上げる |
| [Ariadne New System + IaC](workflows/ariadne-new-system-iac.md) | 新システム設計からShared Artifacts検証、realtime IaC連携までを一気通貫で行う |
| [Ariadne Feature Maintenance](workflows/ariadne-feature-maintenance.md) | 既存対象システムの新機能追加、bug fix、保守開発を行う |
| [GaC / UaC GUI Mode](workflows/gui-mode.md) | 親workflow内でSVGをSemantic Layout、PyQt6候補、QTest候補へ変換する |
| [Next.js Webapp Implementation Prep](workflows/nextjs-webapp-implementation-prep.md) | 親workflow内でNext.js画面機能の実装前準備を行う |
| [Web SVG Layout Mode](workflows/web-svg-layout-mode.md) | 親workflow内でSVGをWeb layout、React候補、Playwright候補へ変換する |
| [MCP Server Group Implementation](workflows/mcp-server-group-implementation.md) | MCP Server群、MCP Client、Agent Runtime、Discord Gateway boilerplateを境界確認付きで展開する |
| [Flutter Multi-platform](workflows/flutter-multiplatform.md) | Flutterアプリの対象platform、環境、boilerplate、test、build計画、evidenceを整理する |
| [Realtime IaC](workflows/realtime-iac.md) | リアルタイムシステム向けIaCを設計、生成、レビュー、検証、文書化する |
| [Corrective Action Report](workflows/corrective-action-report.md) | repository / branchをread-onlyで調査し、改善reportを作る |
| [Corrective Action Fix](workflows/corrective-action-fix.md) | report作成からIssue、branch、修正、test、pushまで進める |
| [Docs Sync](workflows/docs-sync.md) | 実装とdocsの差分を検出し、docsだけを同期する |
| [Self-Improvement](workflows/self-improvement.md) | Workflow実行中の摩擦をFeedback reportへ保存し、採用判断後に改善Issueへつなぐ |
| [GitHub Knowledge Maintenance](workflows/github-knowledge-maintenance.md) | GitHub Issue / PR / docs / CARを知識資産として保守する |
| [VSCode Environment](workflows/vscode-environment.md) | VSCode workspace as code、tasks、launch、extensions、terminal、AI workflow entrypoints、evidenceを整備する |
| [Knowledge Capture](workflows/knowledge-capture.md) | 完了IssueからPR文面、RAG候補、docs候補、archive準備を作る |
| [RAG Build / Load](workflows/rag-build-load.md) | RAG作成と開発前RAG読み込みを行う |
| [Runtime Health Check](workflows/runtime-health-check.md) | Ariadne自身のruntime、pytest、UT仕様書、Context First、docs品質を自己診断する |
| [External Web RAG](workflows/external-web-rag.md) | 要件定義、設計、改善flowで不足した知識を外部Web一次情報から補う |
| [Workflow Flowcharts](diagrams/workflow-flowcharts.md) | 各AI workflowのMermaid式flowchart |
| [Workflow Flowchart Process Tables](diagrams/workflow-flowchart-process-tables.md) | flowchartを業務工程、入力、出力、gateの表で解説する横断資料 |
| [Dispatcher / Workflow Map](diagrams/dispatcher-workflow-map.md) | Dispatcher群と各Workflowの関係、Context First gate、RAG dispatchの位置づけ |

## Reference Docs

| Document | Purpose |
| --- | --- |
| [Runtime pytest UT Specifications](reference/runtime-pytest-ut/README.md) | runtime pytest UT仕様書ディレクトリ、項目表、pytest node id別の単体試験仕様書 |
| [Runtime pytest UT Test Items](reference/runtime-pytest-ut/test-items.md) | runtime pytest UT項目表、test file別の観点、件数、coverage到達点 |
| [Runtime pytest UT Case Specification](reference/runtime-pytest-ut/case-specification.md) | runtime pytest 533ケース分の単体試験仕様書、pytest node id別の確認内容 |
| [Repository Structure](reference/repository-structure.md) | root directory、work directory、artifact保存先 |
| [Runtime](reference/runtime.md) | runtime CLI、GitHub/SCM/環境ファイル |
| [Templates](reference/templates.md) | templates配下の成果物ひな形と品質ルール |
| [Test Artifact Storage](reference/test-artifact-storage.md) | テスト仕様書、QTest、結合疎通証跡の保存先 |
| [VSCode Environment](reference/vscode-environment.md) | VSCode Workspace as Code、terminal profiles、task labels、preflight |
| [Skill Discovery](reference/skill-discovery.md) | VS Code prompt候補とCodex Skill候補の違い |
| [Agent Inventory](reference/agent-inventory.md) | 既存Agentの責務、RAG利用、専門Agent候補の棚卸し |
| [Data Model](reference/data-model.md) | `.ariadne/schemas/` と `work/<id>/context/*.json` |
| [Context First Architecture](reference/context-first-architecture.md) | Dispatcher Contextを標準インターフェース化する設計原則 |
| [Workflow Help CLI](reference/workflow-help.md) | `aiwfctl help` でprompt command、必須引数、処理概要、詳細を検索する |
| [Workflow Feedback](reference/workflow-feedback.md) | 各AI workflow実行時にFeedback reportを保存し、蓄積後に`/self-improvement`で採用判断する運用 |
| [Environment Selection](reference/environment-selection.md) | `aiwfctl env` でworkflow実行前にWindows / WSL / Docker profileを選ぶ |
| [RAG](reference/rag.md) | internal / external-web RAG pipeline、出力artifact、境界 |
| [RAG Dispatcher Design Notes](reference/rag-dispatcher.md) | dispatch plan、query planning、Agent間handoff、UUIDと意味検索の責任分離 |
| [Operations](reference/operations.md) | commit rule、human gate、encoding、archiveの運用注意 |

## Architecture文書

| Document | Purpose |
| --- | --- |
| [Architecture Overview](architecture/overview.md) | ARIADNE全体の構成、責務、設計文書への入口 |
| [aiwfctl Architecture](architecture/aiwfctl-architecture.md) | CLI entrypoint、subcommand dispatch、runtime境界 |
| [Runtime Architecture](architecture/runtime-architecture.md) | runtime packageの責務、構成、failure handling |
| [Workflow Dispatch](architecture/workflow-dispatch.md) | workflow選択、context作成、review境界 |
| [State and Artifact Management](architecture/state-and-artifact-management.md) | state、artifact、evidence保存方針 |
| [Evidence and Completion](architecture/evidence-and-completion.md) | 完了条件、test/review/release evidence |
| [Human Gate](architecture/human-gate.md) | 人間判断が必要な操作と記録項目 |
| [Retry and Resume](architecture/retry-and-resume.md) | 中断後の復帰、再実行、release再現性 |

## Release文書

| Document | Purpose |
| --- | --- |
| [Release Policy](release/release-policy.md) | releaseに必要な文書、検証、Human Gate |
| [Release Checklist](release/release-checklist.md) | 公開前、テスト、文書、release、post-release確認 |
| [Versioning Policy](release/versioning-policy.md) | tag、package version、development noteの関係 |
| [Citation Guide](citation/citation-guide.md) | `CITATION.cff` の未確定値と公開前確認 |
| [ScanCode GitHub Actions](security/scancode-github-actions.md) | OSS公開前のScanCode license audit workflowとローカル予行 |

## Legal文書

| Document | Purpose |
| --- | --- |
| [License Policy](legal/license-policy.md) | `AGPL-3.0-or-later` 方針、生成物方針、公開前確認 |
| [Generated Artifacts](legal/generated-artifacts.md) | ARIADNE利用による生成物への非波及方針 |
| [Component License Boundaries](legal/component-license-boundaries.md) | ARIADNE本体、外部入力、生成物の境界 |
| [Network Source Offer](legal/network-source-offer.md) | AGPL採用時に必要なnetwork source offer検討 |
| [Third-Party Licenses](legal/third-party-licenses.md) | dependency license auditの入口 |
| [Legal FAQ](legal/faq.md) | 公開前に利用者へ説明するライセンスFAQ |
| [Legal Evidence Index](legal/README.md#release-evidence) | 公開前のreview itemとrelease evidenceの入口 |
| [Legal Review Items](legal/evidence/legal-review-items.md) | 公開前に人間確認が必要な著作権者、公開URL、GitHub Security Advisories方針など |
| [Dependency License Report](legal/evidence/dependency-license-report.json) | third-party dependency license review状況 |
| [License Boundary Report](legal/evidence/license-boundary-report.json) | ARIADNE本体、生成物、外部入力のlicense boundary |
| [Release License Check](legal/evidence/release-license-check.json) | AGPL方針へのrelease license整合性確認 |

## Source Of Truth

- 実行手順の詳細は `skills/<skill-name>/SKILL.md` を最優先します。
- Runtime CLI の詳細は `runtime/**/README.md` と実装を確認します。
- 成果物の形式は `templates/` と `.ariadne/schemas/` を確認します。
- `docs/` は、運用者が迷わず入口を選ぶための整理された案内として使います。
