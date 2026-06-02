# Runtime RAG

`runtime/rag/` は、review report や corrective action report などの Markdown artifact を、Agent が再利用しやすい file-based RAG 形式へ変換する runtime です。

現時点では vector DB ではなく、以下の段階に分けます。

```text
source markdown
  -> normalized JSON document
  -> chunk JSON
  -> JSONL indexes
  -> local embeddings
  -> compressed context pack
```

これにより、あとから OpenAI embeddings、SQLite、DuckDB、PostgreSQL + pgvector、FAISS、Chroma などへ移行できます。

## Directory Flow

```text
rag/
  corrective-action-report/  source markdown reports
  normalized/                normalized RAG documents
  chunks/                    chunk JSON files
  indexes/                   documents.jsonl / chunks.jsonl
  embeddings/                local embedding index
  retrieval/                 temporary retrieval results and prompts
```

## CLI

### 1. Normalize Documents

```powershell
python runtime/rag/normalize_documents.py `
  --source-dir rag/corrective-action-report `
  --output-dir rag/normalized `
  --document-type corrective-action-report
```

### 2. Chunk Documents

```powershell
python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks
```

### 3. Build Index

```powershell
python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes
```

### 4. Retrieve And Compress Context

Optional local embeddings:

```powershell
python runtime/rag/embed_chunks.py `
  --chunks-index rag/indexes/chunks.jsonl `
  --output rag/embeddings/chunks-embeddings.jsonl
```

```powershell
python runtime/rag/retrieve_context.py `
  "MainWindow 分割 Qt smoke test" `
  --chunks-index rag/indexes/chunks.jsonl `
  --embeddings-index rag/embeddings/chunks-embeddings.jsonl `
  --output-dir rag/retrieval `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

`retrieve_context.py` は、local JSONL index に対する keyword retrieval、local embedding cosine similarity、hybrid reranking、extractive compression を行います。

Vector DB、embeddings、semantic search、reranking は、将来の MCP repository 側で担当します。この local workflow では、MCP へ渡しやすい deterministic な context pack を作るところまでを責務にします。

Local embeddings は `local-hash-embedding-v1` による deterministic sparse embedding です。外部APIを使わず、MCP repository 側の本格embedding / Vector DBへ移行する前の local baseline として扱います。

## Output Files

| Path | Purpose |
| --- | --- |
| `rag/normalized/*.json` | source report を metadata 付きの RAG document として保存 |
| `rag/chunks/*.json` | retrieval しやすい単位に分割した chunk |
| `rag/indexes/documents.jsonl` | document-level index |
| `rag/indexes/chunks.jsonl` | chunk-level index |
| `rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `rag/retrieval/*_retrieval-result.json` | query、selected chunks、dropped chunks、filters |
| `rag/retrieval/*_context-pack.json` | Agent投入用の圧縮済みcontext pack |
| `rag/retrieval/*_context-pack.md` | 人間が読める圧縮済みcontext |

## Quality Rule

RAG document には最低限以下を持たせます。

- document type
- source path
- project
- repository
- branch
- commit
- status
- tags
- headings
- content

metadata が不足している source report でも normalize できますが、retrieval 品質を上げるため、元の Markdown report には front matter を付けることを推奨します。

## Context Compression Rule

コンテキスト圧縮では、以下を必ず残します。

- query
- selected chunks
- dropped chunks and reason
- source paths
- heading path
- compression method
- max chars
- estimated tokens
- compressed context

圧縮は、元文書の要点を生成的に書き換えるのではなく、まず extractive に残します。判断根拠を追えることを優先します。
