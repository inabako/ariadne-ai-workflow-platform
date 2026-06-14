# Documentation Guide

この `docs/` は、Intent-Driven Robotics AI Workflow を運用するための日本語ドキュメント置き場です。

Repository root の `README.md` は入口と索引に絞り、workflow の詳細手順、runtime、RAG、template、skill discovery などはここに分散します。

## 読む順番

1. [Workflows](workflows/README.md)
   - どの slash command / Skill を使うかを決める。
2. [Repository Structure](reference/repository-structure.md)
   - この repository の directory 役割を確認する。
3. [Runtime](reference/runtime.md)
   - workflow を支える CLI と副作用境界を確認する。
4. [Templates](reference/templates.md)
   - 要件、設計、process report、test evidence のひな形を確認する。
5. [RAG](reference/rag.md)
   - corrective action report を検索可能な知識へ変換する流れを確認する。
6. [Test Artifact Storage](reference/test-artifact-storage.md)
   - テスト仕様書、QTest、結合疎通証跡、target repo docsへの保存先を確認する。
7. [Mermaid Diagrams](diagrams/README.md)
   - 各AI workflowの動作イメージをflowchartで確認する。

## Workflow Docs

| Document | Purpose |
| --- | --- |
| [Workflow Index](workflows/README.md) | 全workflowの選択基準と入出力 |
| [Requirement Discovery](workflows/requirement-discovery.md) | 箇条書き草案から完成版要件定義書を作る |
| [Robotics New System](workflows/robotics-new-system.md) | 新しいrobotics systemを立ち上げる |
| [Robotics New System + IaC](workflows/robotics-new-system-iac.md) | 新システム設計からShared Artifacts検証、realtime IaC連携までを一気通貫で行う |
| [Robotics Feature Maintenance](workflows/robotics-feature-maintenance.md) | 既存systemの新機能追加、bug fix、保守開発を行う |
| [Realtime IaC](workflows/realtime-iac.md) | リアルタイムシステム向けIaCを設計、生成、レビュー、検証、文書化する |
| [Corrective Action Report](workflows/corrective-action-report.md) | repository / branchをread-onlyで調査し、改善reportを作る |
| [Corrective Action Fix](workflows/corrective-action-fix.md) | report作成からIssue、branch、修正、test、pushまで進める |
| [Docs Sync](workflows/docs-sync.md) | 実装とdocsの差分を検出し、docsだけを同期する |
| [GitHub Knowledge Maintenance](workflows/github-knowledge-maintenance.md) | GitHub Issue / PR / docs / CARを知識資産として保守する |
| [VSCode Environment](workflows/vscode-environment.md) | VSCode workspace as code、tasks、launch、extensions、terminal、AI workflow entrypoints、evidenceを整備する |
| [Knowledge Capture](workflows/knowledge-capture.md) | 完了IssueからPR文面、RAG候補、docs候補、archive準備を作る |
| [RAG Build / Load](workflows/rag-build-load.md) | RAG作成と開発前RAG読み込みを行う |
| [External Web RAG](workflows/external-web-rag.md) | 要件定義、設計、改善flowで不足した知識を外部Web一次情報から補う |
| [Workflow Flowcharts](diagrams/workflow-flowcharts.md) | 各AI workflowのMermaid式flowchart |

## Reference Docs

| Document | Purpose |
| --- | --- |
| [Repository Structure](reference/repository-structure.md) | root directory、work directory、artifact保存先 |
| [Runtime](reference/runtime.md) | runtime CLI、GitHub/SCM/環境ファイル |
| [Templates](reference/templates.md) | templates配下の成果物ひな形と品質ルール |
| [Test Artifact Storage](reference/test-artifact-storage.md) | テスト仕様書、QTest、結合疎通証跡の保存先 |
| [Skill Discovery](reference/skill-discovery.md) | VS Code prompt候補とCodex Skill候補の違い |
| [Agent Inventory](reference/agent-inventory.md) | 既存Agentの責務、RAG利用、専門Agent候補の棚卸し |
| [Data Model](reference/data-model.md) | `.github/schemas/` と `work/<id>/context/*.json` |
| [RAG](reference/rag.md) | internal / external-web RAG pipeline、出力artifact、境界 |
| [Operations](reference/operations.md) | commit rule、human gate、encoding、archiveの運用注意 |

## Source Of Truth

- 実行手順の詳細は `skills/<skill-name>/SKILL.md` を最優先します。
- Runtime CLI の詳細は `runtime/**/README.md` と実装を確認します。
- 成果物の形式は `templates/` と `.github/schemas/` を確認します。
- `docs/` は、運用者が迷わず入口を選ぶための整理された案内として使います。
