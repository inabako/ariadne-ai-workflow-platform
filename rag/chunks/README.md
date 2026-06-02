# RAG Chunks

このディレクトリには、normalized RAG document を retrieval しやすい単位へ分割した chunk JSON を保存します。

生成元:

```text
runtime/rag/chunk_documents.py
```

chunk は `rag/indexes/chunks.jsonl` に集約され、後続の retrieval や embeddings の入力になります。
