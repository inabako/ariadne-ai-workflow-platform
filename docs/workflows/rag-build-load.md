# RAG Build / Load

Corrective Action Report などのMarkdown reportを file-based RAG artifactへ変換し、開発前に検索して圧縮済みcontextを読み込むworkflowです。

この文書は、RAG build / load の実行手順を扱います。RAG全体の概念、source分類、cleanup分類は [RAG](../reference/rag.md)、DuckDB read model の再構築と検索は [DuckDB RAG Read Model](../rag/duckdb-read-model.md)、吸収品質評価は [RAG Knowledge Quality Metrics](../rag/knowledge-quality-metrics.md) を参照してください。

## Commands

```text
/rag-build
/rag-load
```

通常実行の入口は `aiwfctl rag ...` です。
内部moduleの直接実行例は、runtime module開発や単体確認のための参照として扱います。

## RAG Build

標準pipeline:

```text
source markdown
  -> normalized UUID JSON document
  -> raw chunk JSON
  -> ingestion optimization
  -> accepted optimized chunk JSON
  -> JSONL indexes
  -> local embeddings
  -> compressed JSON context pack
```

主なコマンド:

### Integrated CLI

`/rag-build` は、個別CLIを順番に手実行する代わりに、次の統合CLIでも実行できます。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag build `
  --work-id "<work-id>" `
  --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report `
  --document-type corrective-action-report `
  --clean-output
```

このCLIは `normalize`、`chunk`、`ingestion optimization`、`index`、`embedding` のstage結果を `work/db/ariadne-knowledge-platform/rag/retrieval/rag-build-run-latest.json` に保存します。

RAG吸収最適化を一時的に外す場合だけ `--skip-optimization` を指定します。通常は、`work/db/ariadne-knowledge-platform/rag/optimized-chunks` に出力された `ACCEPT` 済みchunkだけがindex / embedding対象になります。

`--work-id` を指定した場合は、`work/<work-id>/context/context-manifest.json` に `rag-build-run` を登録します。

RAG source reportのrenameを避けたい場合は `--skip-standardize` を指定します。source report filenameの標準化も行う場合は、必要に応じて `--replace-references` を付けます。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag standardize `
  --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report `
  --replace-references

.\runtime\windows-script\aiwf.cmd ctl rag normalize `
  --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report `
  --output-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --document-type corrective-action-report `
  --clean-output

.\runtime\windows-script\aiwf.cmd ctl rag chunk `
  --input-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --output-dir work/db/ariadne-knowledge-platform/rag/chunks `
  --clean-output

.\runtime\windows-script\aiwf.cmd ctl rag optimize `
  --chunks-dir work/db/ariadne-knowledge-platform/rag/chunks `
  --output-dir work/db/ariadne-knowledge-platform/rag/optimized-chunks `
  --evidence-dir db/rag/evidence/ingestion `
  --clean-output

.\runtime\windows-script\aiwf.cmd ctl rag index `
  --normalized-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --chunks-dir work/db/ariadne-knowledge-platform/rag/optimized-chunks `
  --output-dir work/db/ariadne-knowledge-platform/rag/indexes

.\runtime\windows-script\aiwf.cmd ctl rag embed `
  --chunks-index work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl `
  --output work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl
```

外部Web RAGも、同じJSON pipelineへ載せます。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag normalize `
  --source-dir work/db/ariadne-knowledge-platform/rag/external-web/network `
  --output-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --document-type external-web-knowledge

.\runtime\windows-script\aiwf.cmd ctl rag chunk `
  --input-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --output-dir work/db/ariadne-knowledge-platform/rag/chunks

.\runtime\windows-script\aiwf.cmd ctl rag index `
  --normalized-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --chunks-dir work/db/ariadne-knowledge-platform/rag/chunks `
  --output-dir work/db/ariadne-knowledge-platform/rag/indexes
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
.\runtime\windows-script\aiwf.cmd ctl rag load `
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
.\runtime\windows-script\aiwf.cmd ctl rag load `
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

各artifactのcleanup分類やsource of truth上の位置づけは [RAG](../reference/rag.md#cleanup-classification) を参照してください。

| Path | Purpose |
| --- | --- |
| `work/db/ariadne-knowledge-platform/rag/normalized/*.json` | Markdown reportをmetadata付きUUID JSON documentに変換した最終knowledge record |
| `work/db/ariadne-knowledge-platform/rag/chunks/*.json` | retrieval / embeddings用chunk |
| `work/db/ariadne-knowledge-platform/rag/optimized-chunks/*.json` | ingestion optimizationで `ACCEPT` されたindex / embedding対象chunk |
| `work/db/ariadne-knowledge-platform/rag/indexes/documents.jsonl` | document-level index |
| `work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl` | chunk-level index |
| `work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl` | local sparse embedding index |
| `work/db/ariadne-knowledge-platform/rag/retrieval/*.json` | dispatch plan、retrieval result、dispatch aggregate、context pack |

## Boundary

この repository では、deterministic keyword retrieval、local embedding cosine similarity、hybrid reranking、extractive compression までを扱います。

Vector DB、provider-based embeddings、高度な semantic search、reranking model は、将来の別repository / MCP側の責務として扱います。

## Source Skills

```text
skills/rag-build/SKILL.md
skills/rag-load/SKILL.md
```

## Semantic Hints

Semantic hint は、RAG検索時に「どの知識を優先的に思い出すべきか」を補助する短い意味手がかりです。

特定project向けの注意事項を `.ariadne/` の汎用prompt本文へ残さない場合は、まず knowledge platform 側へ退避します。

```text
work/db/ariadne-knowledge-platform/semantic-hints/*.json
```

退避JSONをRAG source Markdownへ変換します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag semantic-hints generate `
  --source-dir work/db/ariadne-knowledge-platform/semantic-hints `
  --output-dir work/db/ariadne-knowledge-platform/rag/semantic-hints
```

生成済みsemantic hintをRAG artifactへ吸収します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag semantic-hints build `
  --skip-optimization
```

退避済みまたは生成済みsemantic hintを確認します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag semantic-hints read `
  --semantic-hint "GUI simulator"
```

DuckDB read modelへ反映する場合は、build時に `--duckdb-migrate` を付けるか、通常のDuckDB rebuildを実行します。
