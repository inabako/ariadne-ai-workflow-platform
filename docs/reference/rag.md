# RAG

## Workspace Environment Source

VSCode Workspace-as-Code knowledge starts as human-reviewable internal project RAG source Markdown:

```text
work/db/ariadne-knowledge-platform/rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

After human approval, normalize approved notes with:

```powershell
uv run --project runtime python runtime/rag/normalize_documents.py `
  --source-dir work/db/ariadne-knowledge-platform/rag/workspace-environment `
  --output-dir db/rag/normalized `
  --document-type workspace-environment-pattern
```

The final durable knowledge record is the generated UUID-named JSON:

```text
db/rag/normalized/<uuid>.json
```

Chunk JSON, indexes, embeddings, retrieval results, and context packs are derived from this normalized JSON. `db/rag/jsonized/<uuid>.json` is only a wrapper path for existing non-UUID artifacts and is not the primary final RAG knowledge record.

## GitHub Knowledge Source

Approved GitHub Repository Knowledge Maintenance outputs are stored as internal project RAG:

```text
work/db/ariadne-knowledge-platform/rag/github-knowledge/YYYYMMDD_HHMMSS_<topic>.md
```

Normalize approved notes with:

```powershell
uv run --project runtime python runtime/rag/normalize_documents.py `
  --source-dir work/db/ariadne-knowledge-platform/rag/github-knowledge `
  --output-dir db/rag/normalized `
  --document-type github-repository-knowledge
```

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
  -> chunk JSON
  -> JSONL indexes
  -> local embeddings
  -> dispatch plan
  -> retrieval result / context pack
  -> load dispatch aggregate
```

## Output Files

| Path | Purpose |
| --- | --- |
| `db/rag/normalized/*.json` | Markdown reportをmetadata付きUUID JSON documentに変換した最終knowledge record |
| `db/rag/chunks/*.json` | retrieval / embeddings用chunk |
| `db/rag/indexes/documents.jsonl` | document-level index |
| `db/rag/indexes/chunks.jsonl` | chunk-level index |
| `db/rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `db/rag/retrieval/*.json` | dispatch plan、retrieval result、dispatch aggregate、context pack |
| `db/rag/jsonized/*.json` | 既存Markdown / JSONLなどをUUID名JSON wrapperにしたもの |
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
  -> db/rag/normalized/*.json
  -> db/rag/chunks/*.json
  -> db/rag/indexes/*.jsonl
  -> db/rag/embeddings/*.jsonl
  -> db/rag/retrieval/*.json
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
python runtime/rag/retrieve_context.py `
  "Go realtime gateway NAT traversal" `
  --source-type external-web `
  --category network
```

詳しくは [External Web RAG](../workflows/external-web-rag.md) を参照してください。

## Build

```powershell
python runtime/rag/standardize_corrective_report_names.py `
  --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report `
  --replace-references

python runtime/rag/normalize_documents.py `
  --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report `
  --output-dir db/rag/normalized `
  --document-type corrective-action-report `
  --clean-output

python runtime/rag/chunk_documents.py `
  --input-dir db/rag/normalized `
  --output-dir db/rag/chunks `
  --clean-output

python runtime/rag/build_index.py `
  --normalized-dir db/rag/normalized `
  --chunks-dir db/rag/chunks `
  --output-dir db/rag/indexes

python runtime/rag/embed_chunks.py `
  --chunks-index db/rag/indexes/chunks.jsonl `
  --output db/rag/embeddings/chunks-embeddings.jsonl
```

## Load

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "<task summary>" `
  --repository "<target-repository>" `
  --branch "<target-branch>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

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
