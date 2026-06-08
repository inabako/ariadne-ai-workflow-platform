# RAG Build / Load

Corrective Action Report などのMarkdown reportを file-based RAG artifactへ変換し、開発前に検索して圧縮済みcontextを読み込むworkflowです。

## Commands

```text
/rag-build
/rag-load
```

## RAG Build

標準pipeline:

```text
source markdown
  -> normalized JSON document
  -> chunk JSON
  -> JSONL indexes
  -> local embeddings
  -> compressed JSON context pack
```

主なコマンド:

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

外部Web RAGも、同じJSON pipelineへ載せます。

```powershell
python runtime/rag/normalize_documents.py `
  --source-dir rag/external-web/network `
  --output-dir rag/normalized `
  --document-type external-web-knowledge

python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks

python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes
```

外部Web用metadataは `metadata` に保持されます。

```text
source_type
category
topic
trust_level
retrieved_at
verify_before_use
sources
claims
verification_notes
```

## RAG Load

開発前にtask contextから複数queryを計画し、検索結果を圧縮します。

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "<development task>" `
  --repository "<target-repository>" `
  --branch "<target-branch>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

外部Web RAGだけを読む場合:

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "Go realtime gateway NAT traversal" `
  --source-type external-web `
  --category network `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

## Outputs

| Path | Purpose |
| --- | --- |
| `rag/normalized/*.json` | Markdown reportをmetadata付きdocumentに変換したもの |
| `rag/chunks/*.json` | retrieval / embeddings用chunk |
| `rag/indexes/documents.jsonl` | document-level index |
| `rag/indexes/chunks.jsonl` | chunk-level index |
| `rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `rag/retrieval/*.json` | retrieval result、dispatch aggregate、context pack |

## Boundary

この repository では、deterministic keyword retrieval、local embedding cosine similarity、hybrid reranking、extractive compression までを扱います。

Vector DB、provider-based embeddings、高度な semantic search、reranking model は、将来の別repository / MCP側の責務として扱います。

## Source Skills

```text
skills/rag-build/SKILL.md
skills/rag-load/SKILL.md
```
