# RAG Retrieval Workspace

このディレクトリは、RAG load の retrieval result、圧縮済み context pack、dispatch 結果を保存する作業領域です。

標準出力:

```text
rag/retrieval/<uuid>.json
```

JSON の種別はファイル名ではなく `artifact_type` で判定します。

```text
artifact_type: rag-retrieval-result
artifact_type: rag-context-pack
artifact_type: rag-load-dispatch
```

Markdown 出力はデバッグ用途です。通常は生成せず、必要な場合だけ `--write-markdown` を指定します。
