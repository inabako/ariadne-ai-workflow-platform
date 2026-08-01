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
work/db/ariadne-knowledge-platform/rag/
  corrective-action-report/  source markdown reports
  external-web/              external-web source index and category Markdown
  specialist-review/         specialist review Markdown after approval

db/rag/
  normalized/                normalized RAG documents
  chunks/                    raw chunk JSON files
  optimized-chunks/          accepted chunk JSON files after ingestion optimization
  evidence/ingestion/        ingestion optimization evidence
  indexes/                   documents.jsonl / chunks.jsonl
  ariadne-knowledge.duckdb   generated DuckDB read model, Git ignored
  embeddings/                local embedding index
  retrieval/                 temporary retrieval results and prompts
```

External Web RAG uses the same JSON pipeline. Provenance metadata from front matter is preserved under `metadata`.

Specialist review RAG also uses the same JSON pipeline. It is project-specific internal knowledge, and should record trusted external-web RAG, rejected or limited claims, repository evidence, and verification results.

## CLI

### 1. Normalize Documents

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag normalize `
  --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report `
  --output-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --document-type corrective-action-report `
  --clean-output
```

### 2. Chunk Documents

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag chunk `
  --input-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --output-dir work/db/ariadne-knowledge-platform/rag/chunks `
  --clean-output
```

External Web RAG normalize example:

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag normalize `
  --source-dir work/db/ariadne-knowledge-platform/rag/external-web/network `
  --output-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --document-type external-web-knowledge
```

### 3. Optimize Ingestion

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag optimize `
  --chunks-dir work/db/ariadne-knowledge-platform/rag/chunks `
  --output-dir work/db/ariadne-knowledge-platform/rag/optimized-chunks `
  --evidence-dir db/rag/evidence/ingestion `
  --clean-output
```

This stage evaluates chunk candidates before indexing and embedding. It writes `ACCEPT / REWRITE / HUMAN_CHECK / REJECT` evidence under `db/rag/evidence/ingestion`.

### 4. Build Index

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag index `
  --normalized-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --chunks-dir work/db/ariadne-knowledge-platform/rag/optimized-chunks `
  --output-dir work/db/ariadne-knowledge-platform/rag/indexes
```

Optional DuckDB read model:

```powershell
.\runtime\windows-script\aiwf.cmd ctl knowledge init
.\runtime\windows-script\aiwf.cmd ctl knowledge migrate --source work/db/ariadne-knowledge-platform/rag/optimized-chunks
.\runtime\windows-script\aiwf.cmd ctl rag duckdb rebuild --reset
.\runtime\windows-script\aiwf.cmd ctl knowledge search --query "PyQt GUI smoke test" --limit 10
.\runtime\windows-script\aiwf.cmd ctl knowledge export-context --query "PyQt GUI smoke test" --output work/issue-123/context/knowledge.json
.\runtime\windows-script\aiwf.cmd ctl rag duckdb verify --query workflow --query runtime --query RAG --work-dir db/rag/evidence --work-id duckdb-reference-check
```

`db/rag/ariadne-knowledge.duckdb` は生成物です。Git管理せず、必要なタイミングで再生成します。

ただし、生成物であっても運用上のread model実体です。`db/rag/` はcleanup対象にしないでください。欠落した場合は `workflow_doctor` / `aiwfctl doctor` が警告し、`aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset` で再生成します。

`aiwfctl` から呼ぶ場合:

```powershell
aiwfctl knowledge source clone
aiwfctl knowledge source status
aiwfctl knowledge source import-local --clean
aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset
aiwfctl knowledge search --query "PyQt GUI smoke test" --limit 10
aiwfctl knowledge export-context --query "PyQt GUI smoke test" --output work/issue-123/context/knowledge.json
aiwfctl rag duckdb verify --query workflow --query runtime --query RAG --source-repo work/db/ariadne-knowledge-platform --work-dir db/rag/evidence --work-id duckdb-reference-check
```

`source clone` は `inabako/ariadne-knowledge-platform.git` を `work/db/ariadne-knowledge-platform` にcloneします。`source import-local --clean` は、既存のローカル `work/db/ariadne-knowledge-platform/rag/chunks`、`work/db/ariadne-knowledge-platform/rag/jsonized`、`work/db/ariadne-knowledge-platform/rag/normalized` などをknowledge repo cloneへコピーします。

`rebuild --source-repo ... --reset` は、knowledge repo clone内の標準RAGソースから既存JSONを投入します。投入後の参照確認は `db/rag/evidence/reference-check.json` に保存されます。

汎用のDuckDB smoke / reference checkでは、`--work-dir db/rag/evidence --work-id duckdb-reference-check` を指定し、`db/rag/evidence/context/context-manifest.json` に `rag-duckdb-reference-check` contextを登録します。後続workflowは、このmanifestからDuckDB参照可否を読み取れます。

特定Issueや実行中workflowに紐づく確認では、`--work-id <work-id>` を指定し、`work/<work-id>/context/context-manifest.json` に登録します。

`aiwfctl rag retrieve` からDuckDB read modelを使う場合:

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag retrieve `
  "PyQt GUI smoke test" `
  --backend duckdb `
  --duckdb-path db/rag/ariadne-knowledge.duckdb `
  --tag gui
```

`aiwfctl rag load` からDuckDB read modelを使う場合:

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag load `
  --task "PyQt GUI smoke test" `
  --retrieval-backend duckdb `
  --duckdb-path db/rag/ariadne-knowledge.duckdb `
  --tag gui
```

`aiwfctl rag build` からRAG build成果物としてDuckDB migration evidenceを残す場合:

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag build `
  --duckdb-migrate `
  --work-id issue-123
```

この場合、`db/rag/evidence/migration-summary.json` を出力し、`work/<work-id>/context/context-manifest.json` に `rag-duckdb-migration` contextを登録します。

### 5. Retrieve And Compress Context

Optional local embeddings:

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag embed `
  --chunks-index work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl `
  --output work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl
```

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag retrieve `
  "MainWindow 分割 Qt smoke test" `
  --chunks-index work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl `
  --embeddings-index work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl `
  --output-dir work/db/ariadne-knowledge-platform/rag/retrieval `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

External-web only retrieval:

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag retrieve `
  "Go realtime gateway NAT traversal" `
  --source-type external-web `
  --category network `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

`aiwfctl rag retrieve` は、local JSONL index に対する keyword retrieval、local embedding cosine similarity、hybrid reranking、extractive compression を行います。

Vector DB、embeddings、semantic search、reranking は、将来の MCP repository 側で担当します。この local workflow では、MCP へ渡しやすい deterministic な context pack を作るところまでを責務にします。

Local embeddings は `local-hash-embedding-v1` による deterministic sparse embedding です。外部APIを使わず、MCP repository 側の本格embedding / Vector DBへ移行する前の local baseline として扱います。

RAG artifact のファイル名は UUID にします。検索はファイル名ではなく JSON の `content` と metadata を対象にします。

Corrective action report Markdown は、RAG build前に `aiwfctl rag standardize` で `YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md` へ統一します。標準は8桁です。

### 6. Dispatch Parallel RAG Load

開発前の RAG 読み込みでは、`aiwfctl rag load` を使って `rag-dispatch-plan` を作成し、複数queryを計画・並列検索し、`aiwfctl rag retrieve` の圧縮済みcontext packを集約します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag load `
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
.\runtime\windows-script\aiwf.cmd ctl rag load `
  --dispatch-plan work/db/ariadne-knowledge-platform/rag/retrieval/<plan-uuid>.json `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

### 7. JSONize Existing Markdown Artifacts

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag jsonize `
  --rag-dir work/db/ariadne-knowledge-platform/rag `
  --output-dir work/db/ariadne-knowledge-platform/rag/jsonized `
  --clean-output
```

元の Markdown を削除する場合だけ、明示的に `--delete-source` を指定します。

### 8. Migrate Legacy Root RAG Backups

`work/db/ariadne-knowledge-platform/legacy-root-rag-*` に退避された旧 root RAG は、次のruntimeで標準RAG sourceへ統合します。新しい `legacy-root-rag-*` は作らず、出力先は常に `work/db/ariadne-knowledge-platform/rag/` です。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag migrate-legacy-root `
  --legacy-dir work/db/ariadne-knowledge-platform/legacy-root-rag-<timestamp>
```

同一pathに既存ファイルがある場合、SHA-256が一致するものだけlegacy側を削除します。内容が違う衝突は停止します。

## Output Files

| Path | Purpose |
| --- | --- |
| `work/db/ariadne-knowledge-platform/rag/normalized/*.json` | source report を metadata 付きのUUID名 RAG document として保存する最終knowledge record |
| `work/db/ariadne-knowledge-platform/rag/chunks/*.json` | retrieval しやすい単位に分割した raw chunk |
| `work/db/ariadne-knowledge-platform/rag/optimized-chunks/*.json` | RAG吸収最適化で `ACCEPT` された embedding 対象chunk |
| `db/rag/evidence/ingestion/*.json*` | chunk候補、評価、判定、Human Check、reject、summary |
| `db/rag/evidence/migration-summary.json` | rag-buildからDuckDB read modelを再生成したmigration evidence |
| `work/db/ariadne-knowledge-platform/rag/indexes/documents.jsonl` | document-level index |
| `work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl` | chunk-level index |
| `db/rag/ariadne-knowledge.duckdb` | file-based RAG artifactから再生成するDuckDB read model |
| `work/<work-id>/context/knowledge.json` | DuckDB read model検索結果から生成するAgent向けContext JSON |
| `work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `work/db/ariadne-knowledge-platform/rag/jsonized/*.json` | 非UUID JSON、JSONL、Markdown、text artifact を UUID名 JSON wrapper 化したもの |
| `work/db/ariadne-knowledge-platform/rag/retrieval/<uuid>.json` (`artifact_type: rag-dispatch-plan`) | 検索前のintent、metadata、semantic hint、query計画 |
| `work/db/ariadne-knowledge-platform/rag/retrieval/<uuid>.json` (`artifact_type: rag-load-dispatch`) | 複数query retrieval の集約結果 |
| `work/db/ariadne-knowledge-platform/rag/retrieval/<uuid>.json` (`artifact_type: rag-retrieval-result`) | query、selected chunks、dropped chunks、filters |
| `work/db/ariadne-knowledge-platform/rag/retrieval/<uuid>.json` (`artifact_type: rag-context-pack`) | Agent投入用の圧縮済みcontext pack |
| `work/db/ariadne-knowledge-platform/rag/external-web/<category>/*.md` | external-web claims / metadata / verification notes のsource Markdown |
| `work/db/ariadne-knowledge-platform/rag/specialist-review/<domain>/*.md` | specialist review results and trusted external knowledge records |

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
