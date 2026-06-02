# RAG Retrieval Workspace

このディレクトリは、retrieval 結果、圧縮済みcontext pack、Agent投入用promptを保存する作業領域です。

例:

```text
rag/retrieval/<timestamp>_<query-name>.json
rag/retrieval/<timestamp>_<query-name>.md
```

標準出力:

```text
<timestamp>_<query-name>_retrieval-result.json
<timestamp>_<query-name>_context-pack.json
<timestamp>_<query-name>_context-pack.md
```

`runtime/rag/retrieve_context.py` が、local JSONL index と local embeddings から候補chunkを選び、hybrid reranking と extractive compression によって context pack を生成します。
