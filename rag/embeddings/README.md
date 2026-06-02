# RAG Embeddings

このディレクトリには、RAG chunk から生成した embedding index を保存します。

ローカル版では外部APIやVector DBに依存せず、`local-hash-embedding-v1` による deterministic sparse embedding を使います。

生成元:

```text
runtime/rag/embed_chunks.py
```

標準出力:

```text
rag/embeddings/chunks-embeddings.jsonl
```

MCP repository 側で本物の embedding provider / Vector DB を使う場合も、このJSONLを移行元または比較用baselineとして扱えます。
