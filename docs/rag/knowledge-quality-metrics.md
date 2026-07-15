# RAG Knowledge Quality Metrics

この文書は、RAGへKnowledgeを吸収する前に実行する品質評価の基準をまとめます。

RAG buildは、Markdownなどのsourceをそのままembeddingへ流しません。まずchunk候補を評価し、Knowledgeとして扱ってよい粒度、文脈、metadata、traceabilityを満たすものだけを後続のindex / embeddingへ渡します。

## 吸収フロー

```text
source report
  -> normalized document
  -> raw chunk candidate
  -> ingestion optimization
  -> accepted optimized chunk
  -> index
  -> embedding
```

`ingestion optimization` は `runtime/rag/ingestion_optimizer.py` が担当します。

## 評価項目

| 項目 | 目的 |
| --- | --- |
| `semantic_completeness` | chunk単体で意味があるか |
| `retrieval_usefulness` | 検索結果として再利用しやすいか |
| `source_reliability` | sourceの信頼度、review状態、commit、出典があるか |
| `metadata_completeness` | `chunk_id`、`document_id`、`source_path`、`content_hash`などが揃っているか |
| `context_independence` | 「上記」「これ」など前後依存の表現が少ないか |
| `traceability` | 元file、document、repository、branch、commit、sourceへ戻れるか |
| `noise_penalty` | 目次、未入力テンプレート、装飾だけの行、重複行を検出する |
| `duplication_penalty` | 同一content hashの重複を検出する |
| `ambiguity_penalty` | 曖昧語や参照不足を検出する |
| `oversize_penalty` | 大きすぎるchunkを検出する |
| `fragmentation_penalty` | 見出しだけ、断片だけ、コードブロックだけのchunkを検出する |
| `conflict_penalty` | 矛盾、廃止、互換性不一致などの候補を検出する |

重みと閾値は `runtime/rag/policies/knowledge-ingestion-policy.json` で管理します。

## 判定区分

| 判定 | 意味 |
| --- | --- |
| `ACCEPT` | Knowledgeとして吸収し、index / embedding対象にする |
| `REWRITE` | ノイズ除去や重複行除去で補正し、再評価する |
| `HUMAN_CHECK` | Governance、Security、Runtime Core、Encoding、矛盾候補など、人間確認が必要 |
| `REJECT` | 空、credential候補、完全重複、復元不能な断片など、吸収しない |

`REWRITE` は自動補正後に再評価します。再評価後も判断が割れる場合は `HUMAN_CHECK` に送ります。

## Evidence

標準出力先は `db/rag/evidence/ingestion` です。

| File | 内容 |
| --- | --- |
| `source-manifest.json` | 評価対象chunkとpolicy |
| `chunk-candidates.jsonl` | chunk候補一覧 |
| `optimization-evaluations.jsonl` | chunkごとのscore、判定、理由 |
| `accepted-chunks.jsonl` | ACCEPT済みchunk |
| `rewritten-chunks.jsonl` | REWRITEを通ったchunk |
| `human-check-required.jsonl` | Human Check対象 |
| `rejected-chunks.jsonl` | REJECT対象 |
| `ingestion-summary.json` | 件数、平均score、embedding可能件数 |

Evidenceは、最適化スコアを絶対的な正解として扱うためではなく、なぜ吸収したか、なぜ保留したかを後続workflowが読めるように残すためのものです。

## Embedding連携

`/rag-build` では、最適化後の `rag/optimized-chunks/*.json` だけを `build_index.py` に渡します。

そのため、`rag/embeddings/chunks-embeddings.jsonl` へ流れるのは、初期実装では `ACCEPT` 済みchunkのみです。`HUMAN_CHECK` のchunkは、人間承認後にsourceを修正し、再度RAG buildする運用を基本にします。

## DuckDB移行方針

JSON / JSONLをsource of truthにします。

DuckDBはsource of truthを置き換えるDBではなく、file-based RAG artifactから再生成するread modelとして導入します。Phase 1の実装と運用は `docs/rag/duckdb-read-model.md` を参照します。

DuckDBでは、次の単位をtable化しやすいように分けています。

- source manifest
- chunk candidates
- evaluations
- accepted chunks
- rewritten chunks
- human check required
- rejected chunks
- ingestion summary

## Workflow Feedback連携

同じ曖昧語、metadata不足、Human Check過多、REJECT率の偏りが繰り返される場合は、`/self-improvement` のfeedback候補にします。

初期実装では自動でfeedback reportまでは作成しません。`ingestion-summary.json` と `optimization-evaluations.jsonl` をRuntime Maintenance Workflowが読み、必要に応じて改善対象へ昇格します。
