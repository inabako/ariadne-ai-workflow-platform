# Runtime RAG

`runtime/rag/` は、review report や corrective action report などの Markdown artifact を、Agent が再利用しやすい file-based RAG 形式へ変換する runtime です。

現時点では vector DB ではなく、以下の段階に分けます。

```text
source markdown
  -> normalized UUID JSON document
  -> raw chunk JSON
  -> ingestion optimization
  -> accepted optimized chunk JSON
  -> JSONL indexes
  -> optional DuckDB generated read model
  -> local embeddings
  -> compressed context pack
```

DuckDBはsource of truthではなく、file-based RAG artifactから再生成できるread modelです。詳細は `docs/rag/duckdb-read-model.md` を参照します。

RAG吸収の標準運用は、作業中の `work/<workflow-id>/process-report/*.md` をHuman承認後に `work/db/ariadne-knowledge-platform` 側へ登録し、DuckDB read modelへ再構築する流れです。詳細は `docs/rag/duckdb-read-model.md` の「RAG吸収標準フロー」を参照します。

これにより、あとから OpenAI embeddings、PostgreSQL + pgvector、FAISS、Chroma などへ移行できます。

## Directory Flow

```text
rag/
  corrective-action-report/  source markdown reports
  external-web/              external-web source index and category Markdown
  specialist-review/         specialist review Markdown after approval
  normalized/                normalized RAG documents
  chunks/                    raw chunk JSON files
  optimized-chunks/          accepted chunk JSON files after ingestion optimization
  evidence/ingestion/        ingestion optimization evidence
  indexes/                   documents.jsonl / chunks.jsonl
  duckdb/                    generated DuckDB read model, Git ignored
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

### 3. Optimize Ingestion

```powershell
python runtime/rag/ingestion_optimizer.py `
  --chunks-dir rag/chunks `
  --output-dir rag/optimized-chunks `
  --evidence-dir db/rag/evidence/ingestion `
  --clean-output
```

This stage evaluates chunk candidates before indexing and embedding. It writes `ACCEPT / REWRITE / HUMAN_CHECK / REJECT` evidence under `db/rag/evidence/ingestion`.

### 4. Build Index

```powershell
python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/optimized-chunks `
  --output-dir rag/indexes
```

Optional DuckDB read model:

```powershell
python runtime/rag/duckdb_store.py init
python runtime/rag/duckdb_store.py migrate --source rag/optimized-chunks
python runtime/rag/duckdb_store.py rebuild --reset
python runtime/rag/duckdb_store.py search --query "PyQt GUI smoke test" --limit 10
python runtime/rag/duckdb_store.py export-context --query "PyQt GUI smoke test" --output work/issue-123/context/knowledge.json
python runtime/rag/duckdb_store.py verify --query workflow --query runtime --query RAG --work-dir db/rag/evidence --work-id duckdb-reference-check
```

`db/rag/ariadne-knowledge.duckdb` は生成物です。Git管理せず、必要なタイミングで再生成します。

ただし、生成物であっても運用上のread model実体です。`db/rag/` はcleanup対象にしないでください。欠落した場合は `workflow_doctor` / `aiwfctl doctor` が警告し、`aiwfctl knowledge rebuild --source-repo work/db/ariadne-knowledge-platform --reset` で再生成します。

`aiwfctl` から呼ぶ場合:

```powershell
aiwfctl knowledge source clone
aiwfctl knowledge source status
aiwfctl knowledge source import-local --clean
aiwfctl knowledge rebuild --source-repo work/db/ariadne-knowledge-platform --reset
aiwfctl knowledge search --query "PyQt GUI smoke test" --limit 10
aiwfctl knowledge export-context --query "PyQt GUI smoke test" --output work/issue-123/context/knowledge.json
aiwfctl knowledge verify --query workflow --query runtime --query RAG --source-repo work/db/ariadne-knowledge-platform --work-dir db/rag/evidence --work-id duckdb-reference-check
```

`source clone` は `inabako/ariadne-knowledge-platform.git` を `work/db/ariadne-knowledge-platform` にcloneします。`source import-local --clean` は、既存のローカル `rag/chunks`、`rag/jsonized`、`rag/normalized` などをknowledge repo cloneへコピーします。

`rebuild --source-repo ... --reset` は、knowledge repo clone内の標準RAGソースから既存JSONを投入します。投入後の参照確認は `db/rag/evidence/reference-check.json` に保存されます。

汎用のDuckDB smoke / reference checkでは、`--work-dir db/rag/evidence --work-id duckdb-reference-check` を指定し、`db/rag/evidence/context/context-manifest.json` に `rag-duckdb-reference-check` contextを登録します。後続workflowは、このmanifestからDuckDB参照可否を読み取れます。

特定Issueや実行中workflowに紐づく確認では、`--work-id <work-id>` を指定し、`work/<work-id>/context/context-manifest.json` に登録します。

`retrieve_context.py` からDuckDB read modelを使う場合:

```powershell
python runtime/rag/retrieve_context.py `
  "PyQt GUI smoke test" `
  --backend duckdb `
  --duckdb-path db/rag/ariadne-knowledge.duckdb `
  --tag gui
```

`rag_dispatcher.py` からDuckDB read modelを使う場合:

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "PyQt GUI smoke test" `
  --retrieval-backend duckdb `
  --duckdb-path db/rag/ariadne-knowledge.duckdb `
  --tag gui
```

`rag_build.py` からRAG build成果物としてDuckDB migration evidenceを残す場合:

```powershell
python runtime/rag/rag_build.py `
  --duckdb-migrate `
  --work-id issue-123
```

この場合、`db/rag/evidence/migration-summary.json` を出力し、`work/<work-id>/context/context-manifest.json` に `rag-duckdb-migration` contextを登録します。

### 5. Retrieve And Compress Context

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

### 6. Dispatch Parallel RAG Load

開発前の RAG 読み込みでは、dispatcher を使って `rag-dispatch-plan` を作成し、複数queryを計画・並列検索し、`retrieve_context.py` の圧縮済みcontext packを集約します。

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

既存の計画をAgent間で引き継ぐ場合は、`--dispatch-plan` で `artifact_type: rag-dispatch-plan` のJSONを渡します。

```powershell
python runtime/rag/rag_dispatcher.py `
  --dispatch-plan rag/retrieval/<plan-uuid>.json `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

### 7. JSONize Existing Markdown Artifacts

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
| `rag/normalized/*.json` | source report を metadata 付きのUUID名 RAG document として保存する最終knowledge record |
| `rag/chunks/*.json` | retrieval しやすい単位に分割した raw chunk |
| `rag/optimized-chunks/*.json` | RAG吸収最適化で `ACCEPT` された embedding 対象chunk |
| `db/rag/evidence/ingestion/*.json*` | chunk候補、評価、判定、Human Check、reject、summary |
| `db/rag/evidence/migration-summary.json` | rag-buildからDuckDB read modelを再生成したmigration evidence |
| `rag/indexes/documents.jsonl` | document-level index |
| `rag/indexes/chunks.jsonl` | chunk-level index |
| `db/rag/ariadne-knowledge.duckdb` | file-based RAG artifactから再生成するDuckDB read model |
| `work/<work-id>/context/knowledge.json` | DuckDB read model検索結果から生成するAgent向けContext JSON |
| `rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `rag/jsonized/*.json` | 非UUID JSON、JSONL、Markdown、text artifact を UUID名 JSON wrapper 化したもの |
| `rag/retrieval/<uuid>.json` (`artifact_type: rag-dispatch-plan`) | 検索前のintent、metadata、semantic hint、query計画 |
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
