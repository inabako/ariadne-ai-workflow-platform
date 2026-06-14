# RAG Workspace

このディレクトリは、workflow で作成された report や field knowledge を、Agent が再利用しやすい知識として整える場所です。

## Structure

```text
rag/
  corrective-action-report/
  workspace-environment/
  normalized/
  chunks/
  indexes/
  embeddings/
  retrieval/
```

| Directory | Purpose |
| --- | --- |
| `corrective-action-report/` | 人間が読む元の改善レポート |
| `normalized/` | RAG投入用に metadata と本文をJSON化したUUID名の最終knowledge document |
| `chunks/` | retrieval しやすい単位に分割した chunk JSON |
| `indexes/` | document / chunk の JSONL index |
| `embeddings/` | local sparse embedding index |
| `retrieval/` | 検索結果、圧縮済みcontext pack、Agent投入用promptの保存先 |

## Pipeline

```text
runtime/rag/normalize_documents.py
  -> runtime/rag/chunk_documents.py
  -> runtime/rag/build_index.py
  -> runtime/rag/embed_chunks.py
  -> runtime/rag/retrieve_context.py
```

現段階では file-based RAG として運用します。

将来的には、`rag/indexes/chunks.jsonl` を embeddings / vector DB / SQL DB に投入できます。

## Workspace Environment RAG

Store reusable VSCode environment knowledge in:

```text
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Use this source area for patterns such as Localty terminal roles, VSCode tasks, launch configurations, extension policy, runtime preflight, and trial-run evidence.

This Markdown is the human-reviewable source. After approval, the final machine-readable knowledge lands as:

```text
rag/normalized/<uuid>.json
```

## Local Context Compression

`runtime/rag/retrieve_context.py` は、`rag/indexes/chunks.jsonl` と必要に応じて `rag/embeddings/chunks-embeddings.jsonl` から query に合う chunk を選び、文字数予算に収まる context pack を作ります。

出力:

```text
rag/retrieval/*_retrieval-result.json
rag/retrieval/*_context-pack.json
rag/retrieval/*_context-pack.md
```

この local workflow では deterministic な keyword retrieval、local embedding cosine similarity、hybrid reranking、extractive compression までを扱います。

Vector DB、provider-based embeddings、高度な semantic search、reranking model は、将来の MCP repository 側で担当します。
