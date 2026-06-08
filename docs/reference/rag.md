# RAG

このrepoのRAGは、現場やreviewから得た知識、または外部Webの一次情報から抽出した補助知識を、次のworkflowで再利用するためのfile-based pipelineです。

## Source Reports

主なsourceは Corrective Action Report です。

```text
rag/corrective-action-report/
```

外部Web由来のsource indexとRAG候補は次に置きます。

```text
rag/external-web/knowledge-sources.md
rag/external-web/<category>/
```

推奨ファイル名:

```text
YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md
```

## Pipeline

```text
source markdown
  -> normalized JSON document
  -> chunk JSON
  -> JSONL indexes
  -> local embeddings
  -> retrieval result / context pack
```

## Output Files

| Path | Purpose |
| --- | --- |
| `rag/normalized/*.json` | Markdown reportをmetadata付きdocumentに変換したもの |
| `rag/chunks/*.json` | retrieval / embeddings用chunk |
| `rag/indexes/documents.jsonl` | document-level index |
| `rag/indexes/chunks.jsonl` | chunk-level index |
| `rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `rag/retrieval/*.json` | retrieval result、dispatch aggregate、context pack |
| `rag/jsonized/*.json` | 既存Markdown / JSONLなどをUUID名JSON wrapperにしたもの |
| `rag/external-web/<category>/*.md` | 外部Web一次情報から抽出したclaims / metadata / verification notes |
| `rag/external-web/retrieval/*.md` | 外部Web RAG dispatcher の集約結果 |

## External Web RAG

要件定義、設計、改善flowで知らない領域が出た場合、`rag/external-web/knowledge-sources.md` を入口に外部Web一次情報を精査します。

保存先例:

```text
rag/external-web/
  network/
  robotics/
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

外部Web RAGも内部RAGと同じJSON pipelineで扱います。

```text
rag/external-web/<category>/*.md
  -> rag/normalized/*.json
  -> rag/chunks/*.json
  -> rag/indexes/*.jsonl
  -> rag/embeddings/*.jsonl
  -> rag/retrieval/*.json
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
  --source-dir rag/corrective-action-report `
  --replace-references

python runtime/rag/normalize_documents.py `
  --source-dir rag/corrective-action-report `
  --output-dir rag/normalized `
  --document-type corrective-action-report `
  --clean-output

python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks `
  --clean-output

python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes

python runtime/rag/embed_chunks.py `
  --chunks-index rag/indexes/chunks.jsonl `
  --output rag/embeddings/chunks-embeddings.jsonl
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
