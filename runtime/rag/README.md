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
  external-web/              external-web source index and category Markdown
  specialist-review/         specialist review Markdown after approval
  normalized/                normalized RAG documents
  chunks/                    chunk JSON files
  indexes/                   documents.jsonl / chunks.jsonl
  embeddings/                local embedding index
  retrieval/                 temporary retrieval results and prompts
```

External Web RAG uses the same JSON pipeline. Provenance metadata from front matter is preserved under `metadata`.

Specialist review RAG also uses the same JSON pipeline. It is project-specific internal knowledge, and should record trusted external-web RAG, rejected or limited claims, repository evidence, and verification results.

## CLI

### 1. Normalize Documents

```powershell
python runtime/rag/normalize_documents.py `
  --source-dir rag/corrective-action-report `
  --output-dir rag/normalized `
  --document-type corrective-action-report `
  --clean-output
```

### 2. Chunk Documents

```powershell
python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks `
  --clean-output
```

External Web RAG normalize example:

```powershell
python runtime/rag/normalize_documents.py `
  --source-dir rag/external-web/network `
  --output-dir rag/normalized `
  --document-type external-web-knowledge
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

External-web only retrieval:

```powershell
python runtime/rag/retrieve_context.py `
  "Go realtime gateway NAT traversal" `
  --source-type external-web `
  --category network `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

`retrieve_context.py` は、local JSONL index に対する keyword retrieval、local embedding cosine similarity、hybrid reranking、extractive compression を行います。

Vector DB、embeddings、semantic search、reranking は、将来の MCP repository 側で担当します。この local workflow では、MCP へ渡しやすい deterministic な context pack を作るところまでを責務にします。

Local embeddings は `local-hash-embedding-v1` による deterministic sparse embedding です。外部APIを使わず、MCP repository 側の本格embedding / Vector DBへ移行する前の local baseline として扱います。

RAG artifact のファイル名は UUID にします。検索はファイル名ではなく JSON の `content` と metadata を対象にします。

Corrective action report Markdown は、RAG build前に `runtime/rag/standardize_corrective_report_names.py` で `YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md` へ統一します。標準は8桁です。

### 5. Dispatch Parallel RAG Load

開発前の RAG 読み込みでは、dispatcher を使って複数queryを計画・並列検索し、`retrieve_context.py` の圧縮済みcontext packを集約します。

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "MainWindow 分離 責務集中" `
  --repository "C:\github\localty-system-gui" `
  --branch develop `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

### 6. JSONize Existing Markdown Artifacts

```powershell
python runtime/rag/jsonize_rag_tree.py `
  --rag-dir rag `
  --output-dir rag/jsonized `
  --clean-output
```

元の Markdown を削除する場合だけ、明示的に `--delete-source` を指定します。

## Output Files

| Path | Purpose |
| --- | --- |
| `rag/normalized/*.json` | source report を metadata 付きの RAG document として保存 |
| `rag/chunks/*.json` | retrieval しやすい単位に分割した chunk |
| `rag/indexes/documents.jsonl` | document-level index |
| `rag/indexes/chunks.jsonl` | chunk-level index |
| `rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `rag/jsonized/*.json` | 非UUID JSON、JSONL、Markdown、text artifact を UUID名 JSON wrapper 化したもの |
| `rag/retrieval/<uuid>.json` (`artifact_type: rag-load-dispatch`) | 複数query retrieval の集約結果 |
| `rag/retrieval/<uuid>.json` (`artifact_type: rag-retrieval-result`) | query、selected chunks、dropped chunks、filters |
| `rag/retrieval/<uuid>.json` (`artifact_type: rag-context-pack`) | Agent投入用の圧縮済みcontext pack |
| `rag/external-web/<category>/*.md` | external-web claims / metadata / verification notes のsource Markdown |
| `rag/specialist-review/<domain>/*.md` | specialist review results and trusted external knowledge records |

Markdown出力はデバッグ用途です。必要な場合だけ `--write-markdown` を指定します。

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

External-web source Markdown should also include:

- source_type
- category
- topic
- trust_level
- retrieved_at
- verify_before_use
- sources
- claims
- verification_notes

Specialist review Markdown should also include:

- artifact_type: specialist-review
- source_type: internal-work
- domain
- review_agent
- reviewed_artifacts
- internal_rag_used
- external_web_rag_used
- trusted_external_knowledge
- verification_notes

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
