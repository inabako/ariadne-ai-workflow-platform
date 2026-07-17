# /rag-load

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

RAG Load Skill を使って、開発フローに入る前に file-based RAG から関連知識を読み込んでください。

既定では日本語で応答してください。

方針:

1. task context、対象 repository、branch、要件、Issue、比較レポートから 3〜5 個の検索クエリを作る。
2. `runtime/rag/rag_dispatcher.py` を実行する。
3. dispatcher が `runtime/rag/retrieve_context.py` をクエリごとに並列実行する。
4. RAG 圧縮は `retrieve_context.py` の既存 context pack 生成を使う。
5. 生成された `artifact_type: rag-load-dispatch` の `rag/retrieval/<uuid>.json` と、参照先の `artifact_type: rag-context-pack` の `rag/retrieval/<uuid>.json` を読み、開発前の前提知識として要約する。

検索はファイル名ではなく JSON の `content` と metadata を対象にしてください。RAG artifact のファイル名は UUID です。

RAG index または embedding が存在しない場合は、先に `/rag-build` を実行してください。
