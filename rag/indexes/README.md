# RAG Indexes

このディレクトリには、file-based RAG の index を保存します。

生成元:

```text
runtime/rag/build_index.py
```

主な出力:

```text
documents.jsonl
chunks.jsonl
```

現段階では JSONL index として扱い、将来的に embeddings / vector DB / SQL DB へ移行できます。
