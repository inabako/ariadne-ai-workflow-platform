# RAG

このrepoのRAGは、現場やreviewから得た知識を、次のworkflowで再利用するためのfile-based pipelineです。

## Source Reports

主なsourceは Corrective Action Report です。

```text
rag/corrective-action-report/
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
