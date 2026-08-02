# RAG

この文書は、Ariadne の RAG artifact 全体の概念、source of truth、配置責務、cleanup分類を説明します。

実行手順は [RAG Build / Load](../workflows/rag-build-load.md)、DuckDB read model の運用は [DuckDB RAG Read Model](../rag/duckdb-read-model.md)、吸収品質評価は [RAG Knowledge Quality Metrics](../rag/knowledge-quality-metrics.md) を参照してください。

## 文書責務

| Document | 役割 |
| --- | --- |
| この文書 | RAG全体の概念、source分類、artifact配置、cleanup分類 |
| [RAG Build / Load](../workflows/rag-build-load.md) | `aiwfctl rag build/load` の実行手順、Context First連携、出力確認 |
| [DuckDB RAG Read Model](../rag/duckdb-read-model.md) | `db/rag/ariadne-knowledge.duckdb` の生成、検索、再構築、Git管理境界 |
| [RAG Knowledge Quality Metrics](../rag/knowledge-quality-metrics.md) | ingestion optimizationの評価項目、判定、evidence |

## Source Of Truth

Ariadne の RAG source of truth は、Markdown、JSON、JSONLなどのfile-based artifactです。

`work/db/ariadne-knowledge-platform/` は、標準では `ariadne-knowledge-platform` repository のcloneとして扱います。長期保存するknowledge sourceはこのclone側で管理し、Ariadne本体側の `db/rag/**` は検索、検証、移行、context出力のための生成物として扱います。

`db/rag/ariadne-knowledge.duckdb` はsource of truthではありません。削除されても、knowledge sourceから再生成できるread modelです。

## Workspace Environment Source

VSCode Workspace-as-Code のknowledgeは、人間がreviewできる内部project RAG source Markdownとして保存します。

```text
work/db/ariadne-knowledge-platform/rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Human承認後、approved noteを `document-type: workspace-environment-pattern` としてnormalizeします。具体的なcommandは [RAG Build / Load](../workflows/rag-build-load.md) を参照してください。

最終的なdurable knowledge recordは、生成されたUUID名JSONです。

```text
work/db/ariadne-knowledge-platform/rag/normalized/<uuid>.json
```

Chunk JSON、index、embedding、retrieval result、context packは、このnormalized JSONから派生します。`work/db/ariadne-knowledge-platform/rag/jsonized/<uuid>.json` は既存の非UUID artifactを包む互換wrapperであり、primary final RAG knowledge recordではありません。

## GitHub Knowledge Source

承認済みの GitHub Repository Knowledge Maintenance 出力は、内部project RAGとして保存します。

```text
work/db/ariadne-knowledge-platform/rag/github-knowledge/YYYYMMDD_HHMMSS_<topic>.md
```

Human承認後、approved noteを `document-type: github-repository-knowledge` としてnormalizeします。具体的なcommandは [RAG Build / Load](../workflows/rag-build-load.md) を参照してください。

このrepoのRAGは、現場やreviewから得た知識、または外部Webの一次情報から抽出した補助知識を、次のworkflowで再利用するためのfile-based pipelineです。

## Source Reports

主なsourceは Corrective Action Report です。

```text
work/db/ariadne-knowledge-platform/rag/corrective-action-report/
```

専門Agentのreview結果は、作業中は `work/<id>/process-report/` に保存し、RAG登録承認後に内部RAG候補として扱います。

```text
work/<id>/process-report/specialist-review-<domain>.md
work/db/ariadne-knowledge-platform/rag/specialist-review/<domain>/
```

外部Web由来のsource indexとRAG候補は次に置きます。

```text
work/db/ariadne-knowledge-platform/rag/external-web/knowledge-sources.md
work/db/ariadne-knowledge-platform/rag/external-web/<category>/
```

推奨ファイル名:

```text
YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md
```

## Pipeline

```text
source markdown
  -> normalized UUID JSON document
  -> raw chunk JSON
  -> ingestion optimization
  -> accepted optimized chunk JSON
  -> JSONL indexes
  -> local embeddings
  -> dispatch plan
  -> retrieval result / context pack
  -> load dispatch aggregate
```

## Cleanup Classification

`aiwfctl work cleanup-check/apply` removes temporary workflow work scopes only after long-lived Knowledge absorption is confirmed. RAG paths are classified as follows.

| Class | Paths | Cleanup Role |
| --- | --- | --- |
| Long-lived source Knowledge | `work/db/ariadne-knowledge-platform/rag/corrective-action-report/`, `github-knowledge/`, `workspace-environment/`, `external-web/<category>/`, `specialist-review/<domain>/` | May be registered in `artifact-index.json` as cleanup evidence after human approval or equivalent workflow verification. |
| Final durable Knowledge record | `work/db/ariadne-knowledge-platform/rag/normalized/*.json` | Primary machine-readable Knowledge record. May be used as cleanup evidence when produced from approved sources. |
| Compatibility Knowledge wrapper | `work/db/ariadne-knowledge-platform/rag/jsonized/*.json` | May be cleanup evidence for workflows that directly produce wrapper Knowledge, such as SDK analysis. It is not the preferred final RAG record when a normalized document exists. |
| Derived build artifacts | `chunks/`, `optimized-chunks/`, `indexes/`, `embeddings/` | Not cleanup evidence by themselves. They are rebuildable from source/normalized Knowledge and must not justify deleting a temporary work scope alone. |
| Retrieval artifacts | `retrieval/*.json`, `external-web/retrieval/*.md` | Not cleanup evidence. They are query/session outputs for loading context and may be regenerated. |
| Ingestion evidence | `db/rag/evidence/ingestion/` | Not cleanup evidence. It explains build quality decisions but does not prove Knowledge absorption. |
| Temporary workflow work | `work/<work-id>/`, `work/github/<scope>/<scan-mode>/` | Cleanup target only. Remove through `aiwfctl work cleanup-check` then `cleanup-apply --human-check approved`. |

Rules:

- `artifact-index.json` is the cleanup contract. A RAG file outside `artifact-index.json` does not automatically make cleanup safe.
- Draft or review-pending source notes should use `cleanup_ready: false` or omit cleanup evidence until approval.
- Derived build/retrieval artifacts must not be the only evidence for `work cleanup-check`.
- `work/db/<ARIADNE_KNOWLEDGE_REPOSITORY>/` is long-lived local Knowledge backup storage and is not a cleanup target.

## Output Files

| Path | Purpose |
| --- | --- |
| `work/db/ariadne-knowledge-platform/rag/normalized/*.json` | Markdown reportをmetadata付きUUID JSON documentに変換した最終knowledge record |
| `work/db/ariadne-knowledge-platform/rag/chunks/*.json` | retrieval / embeddings用chunk |
| `work/db/ariadne-knowledge-platform/rag/optimized-chunks/*.json` | ingestion optimizationで `ACCEPT` されたindex / embedding対象chunk |
| `work/db/ariadne-knowledge-platform/rag/indexes/documents.jsonl` | document-level index |
| `work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl` | chunk-level index |
| `work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `work/db/ariadne-knowledge-platform/rag/retrieval/*.json` | dispatch plan、retrieval result、dispatch aggregate、context pack |
| `work/db/ariadne-knowledge-platform/rag/jsonized/*.json` | 既存Markdown / JSONLなどをUUID名JSON wrapperにしたもの |
| `work/db/ariadne-knowledge-platform/rag/external-web/<category>/*.md` | 外部Web一次情報から抽出したclaims / metadata / verification notes |
| `work/db/ariadne-knowledge-platform/rag/external-web/retrieval/*.md` | 外部Web RAG dispatcher の集約結果 |
| `work/db/ariadne-knowledge-platform/rag/specialist-review/<domain>/*.md` | 専門Agent review結果、採用した外部知識、検証結果 |

## External Web RAG

要件定義、設計、改善flowで知らない領域が出た場合、`work/db/ariadne-knowledge-platform/rag/external-web/knowledge-sources.md` を入口に外部Web一次情報を精査します。

保存先例:

```text
work/db/ariadne-knowledge-platform/rag/external-web/
  network/
  system-design/
  ai-workflow/
  architecture/
  go-runtime/
  observability/
  video/
  platform/
  retrieval/
```

外部Web RAGは、URL、retrieved_at、source_type、trust_level、claims、verification_notes を保存します。

外部ページ本文を丸ごと保存しません。

## Specialist Review RAG

Specialist reviewは、内部RAG、外部Web RAG、current repository evidenceを読んだうえで、成果物に対して専門観点の判断を残す内部RAG候補です。

保存先例:

```text
work/db/ariadne-knowledge-platform/rag/specialist-review/
  python-runtime/
  go-runtime/
  network/
  video/
  observability/
  platform/
  testing/
  security/
  safety/
```

Specialist reviewには、必ず次を残します。

- reviewed artifacts
- internal RAG used
- external-web RAG used
- trusted external knowledge
- rejected or limited external claims
- repository evidence
- verification / test evidence
- unresolved QA

詳しくは [Agent Inventory](agent-inventory.md) と [External Web RAG](../workflows/external-web-rag.md) を参照してください。

外部Web RAGも内部RAGと同じJSON pipelineで扱います。

```text
work/db/ariadne-knowledge-platform/rag/external-web/<category>/*.md
  -> work/db/ariadne-knowledge-platform/rag/normalized/*.json
  -> work/db/ariadne-knowledge-platform/rag/chunks/*.json
  -> work/db/ariadne-knowledge-platform/rag/indexes/*.jsonl
  -> work/db/ariadne-knowledge-platform/rag/embeddings/*.jsonl
  -> work/db/ariadne-knowledge-platform/rag/retrieval/*.json
```

`normalize_documents.py` は external-web front matter を `metadata` に保持します。

```text
source_type
source_kind
source_owner
category
topic
trust_level
retrieved_at
freshness_policy
verify_before_use
sources
urls
claims
verification_notes
front_matter
```

外部Webだけを検索する場合は、`--source-type external-web` を使います。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag retrieve `
  "Go realtime gateway NAT traversal" `
  --source-type external-web `
  --category network
```

詳しくは [External Web RAG](../workflows/external-web-rag.md) を参照してください。

## 実行手順

この文書では、RAGの概念と配置責務だけを扱います。build / load の具体的なcommand、Context First manifest連携、出力確認は [RAG Build / Load](../workflows/rag-build-load.md) を参照してください。

標準の使い分けは次の通りです。

| やりたいこと | 参照先 |
| --- | --- |
| Markdown reportをRAG artifactへ変換する | [RAG Build / Load](../workflows/rag-build-load.md#rag-build) |
| 開発前にRAG contextを読み込む | [RAG Build / Load](../workflows/rag-build-load.md#rag-load) |
| DuckDB read modelを再構築する | [DuckDB RAG Read Model](../rag/duckdb-read-model.md) |
| RAG吸収品質を確認する | [RAG Knowledge Quality Metrics](../rag/knowledge-quality-metrics.md) |

dispatcherは検索前に `artifact_type: rag-dispatch-plan` を生成します。
このplanは、Intent、metadata filter、semantic hint、query purpose、stop conditionをAgent間で共有するための成果物です。

dispatcher設計と運用ノウハウは [RAG Dispatcher Design Notes](rag-dispatcher.md) を参照してください。

## Boundary

このrepositoryでは、local workflowのための deterministic baseline を扱います。

- keyword retrieval
- local sparse embedding
- cosine similarity
- hybrid reranking
- extractive compression

Vector DB、provider-based embeddings、高度なsemantic search、reranking modelは、将来の別repository / MCP側で扱います。

External-web RAGは current source code、test evidence、人間承認済み運用知見を上書きしません。

改善flowでは、外部WebRAGを `supporting_reference` として扱います。finding確定には、対象repositoryのfile、behavior、log、docs gap、test gapなどのevidenceが必要です。
