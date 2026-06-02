# /rag-load

RAG Load Skill を使って、開発フローに入る前に file-based RAG から関連知識を読み込んでください。

既定では日本語で応答してください。

方針:

1. task context、対象 repository、branch、要件、Issue、比較レポートから 3〜5 個の検索クエリを作る。
2. `runtime/rag/rag_dispatcher.py` を実行する。
3. dispatcher が `runtime/rag/retrieve_context.py` をクエリごとに並列実行する。
4. RAG 圧縮は `retrieve_context.py` の既存 context pack 生成を使う。
5. 生成された `rag/retrieval/*_rag-load-dispatch.md` と `rag/retrieval/*_context-pack.md` を読み、開発前の前提知識として要約する。

RAG index または embedding が存在しない場合は、先に `/rag-build` を実行してください。
