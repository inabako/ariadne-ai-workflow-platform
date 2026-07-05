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
  -> normalized UUID JSON document
  -> chunk JSON
  -> JSONL indexes
  -> local embeddings
  -> compressed JSON context pack
```

主なコマンド:

### Integrated CLI

`/rag-build` は、個別CLIを順番に手実行する代わりに、次の統合CLIでも実行できます。

```powershell
python runtime/rag/rag_build.py `
  --work-id "<work-id>" `
  --source-dir rag/corrective-action-report `
  --document-type corrective-action-report `
  --clean-output
```

このCLIは `normalize`、`chunk`、`index`、`embedding` のstage結果を `rag/retrieval/rag-build-run-latest.json` に保存します。

`--work-id` を指定した場合は、`work/<work-id>/context/context-manifest.json` に `rag-build-run` を登録します。

RAG source reportのrenameを避けたい場合は `--skip-standardize` を指定します。source report filenameの標準化も行う場合は、必要に応じて `--replace-references` を付けます。

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

dispatcherは検索前に `artifact_type: rag-dispatch-plan` を保存します。
このplanには、intent、metadata filter、semantic hint、query、query purpose、stop conditionを残します。
後続Agentは、検索結果だけでなく「なぜこのRAGを読んだか」も確認できます。

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

### Context First

`/rag-load` は `--work-id` が指定された場合、対象workの `context-manifest.json` を確認します。

- `execution-plan`: manifestに存在する場合、RAG検索の上位目的としてdispatch planへ接続します。
- `rag-dispatch-plan`: 検索前のquery planをmanifestへ登録します。
- `rag-load-dispatch`: 検索結果、圧縮Context、dispatch結果をmanifestへ登録します。

これにより、RAG検索は単なる全文検索ではなく、Workflowが先に確定した実行計画に沿ったContext取得として扱えます。

`--work-id` を指定したのに `execution-plan` が見つからない場合、検索自体は止めません。
その代わり、dispatch plan / dispatch result に `human_check_required: true` と理由を記録し、Agentが検索意図を人間確認できるようにします。

## Outputs

| Path | Purpose |
| --- | --- |
| `rag/normalized/*.json` | Markdown reportをmetadata付きUUID JSON documentに変換した最終knowledge record |
| `rag/chunks/*.json` | retrieval / embeddings用chunk |
| `rag/indexes/documents.jsonl` | document-level index |
| `rag/indexes/chunks.jsonl` | chunk-level index |
| `rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `rag/retrieval/*.json` | dispatch plan、retrieval result、dispatch aggregate、context pack |

## Boundary

この repository では、deterministic keyword retrieval、local embedding cosine similarity、hybrid reranking、extractive compression までを扱います。

Vector DB、provider-based embeddings、高度な semantic search、reranking model は、将来の別repository / MCP側の責務として扱います。

## Source Skills

```text
skills/rag-build/SKILL.md
skills/rag-load/SKILL.md
```
