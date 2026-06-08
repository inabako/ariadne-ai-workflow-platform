# Workflow Index

このページは、Intent-Driven Robotics AI Workflow の入口を選ぶための一覧です。

## Entry Points

| Command / Skill | 使う場面 | 主な入力 | 主な出力 |
| --- | --- | --- | --- |
| `/requirement-discovery` | 箇条書き草案から要件定義書を完成させたい | `work/requirements/draft/<draft>` | `work/requirements/<requirements>.md` |
| `/robotics-new-system` | 新しいrobotics system、runtime、remote operation、device integrationを開始する | 完成版要件定義書 | `work/<receipt-id>/` |
| `/robotics-feature-maintenance` | 既存robotics systemの新機能追加、bug fix、保守開発を行う | 完成版要件定義書 | `work/<receipt-id>/` |
| `/corrective-action-report` | repository / branchをread-onlyで調査し、改善reportだけ作る | target repository, target branch | `rag/corrective-action-report/*.md` |
| `/corrective-action-fix` | 改善reportからIssue、branch、修正、test、pushまで進める | target repository, target branch | `work/<branch>/`, `work/issue-<number>/` |
| `/docs-sync` | 実装とdocsのズレを検出し、docsだけ修正する | target repository, target branch | `docs-drift-analysis.json`, issue branch |
| `/knowledge-capture` | 完了IssueのPR材料、RAG候補、docs候補、archive準備を作る | `work/issue-<number>` | `knowledge-capture-report.md` |
| `/rag-build` | Markdown reportをRAG artifactへ変換する | `rag/corrective-action-report/*.md` | `rag/normalized/`, `rag/chunks/`, `rag/indexes/`, `rag/embeddings/` |
| `/rag-load` | 開発前に過去知識を検索し、圧縮contextを読む | task, repository, branch | `rag/retrieval/*.json` |
| External Web RAG | 要件定義、設計、改善flowで知見不足の領域を外部Web一次情報で補う | `rag/external-web/knowledge-sources.md` | `rag/external-web/<category>/*.md` |

## Decision Guide

| 状況 | 選ぶworkflow |
| --- | --- |
| まだ要件が箇条書きだけ | [Requirement Discovery](requirement-discovery.md) |
| 新しいrobotics systemを作る | [Robotics New System](robotics-new-system.md) |
| 既存systemへ機能追加、bug fix、保守対応をする | [Robotics Feature Maintenance](robotics-feature-maintenance.md) |
| まず改善点を洗い出したいが、sourceは変更しない | [Corrective Action Report](corrective-action-report.md) |
| 改善点の修正まで進めたい | [Corrective Action Fix](corrective-action-fix.md) |
| codeは変えず、docsだけ実装に合わせたい | [Docs Sync](docs-sync.md) |
| 作業完了後にPR文面と知識回収を整えたい | [Knowledge Capture](knowledge-capture.md) |
| 過去reportを検索可能にしたい | [RAG Build / Load](rag-build-load.md) |
| 要件定義、設計、改善flowで知らない技術領域が出た | [External Web RAG](external-web-rag.md) |

## Common Rules

- Repository / branch は user input または要件定義書の `Repository Control` を source of truth にします。
- 会話ログだけで intake 済みとは扱いません。
- GitHub Issue 作成、branch作成、push、install、archive移動などの副作用は、人間承認gateを通します。
- `work/<branch>/` はbase調査用、`work/issue-<number>/` は実装修正用に分けます。
- 成果物は `work/<id>/context/artifact-index.json` に登録できる形で残します。
- RAG化する成果物は、metadata、evidence、open questions、stable section order を保ちます。
- 外部Web RAGは current code、test evidence、人間承認済み運用知見を上書きしません。
- 改善flowで外部WebRAGを使う場合、findingは必ず対象repository evidenceへ結び直します。
