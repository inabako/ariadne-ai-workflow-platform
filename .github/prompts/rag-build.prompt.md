# /rag-build

RAG Build Skill を使って、Intent-Driven Robotics AI Workflow の Markdown report を file-based RAG artifact に変換してください。

既定では日本語で応答してください。

実行する既定 pipeline:

1. `runtime/rag/normalize_documents.py`
2. `runtime/rag/chunk_documents.py`
3. `runtime/rag/build_index.py`
4. `runtime/rag/embed_chunks.py`
5. 必要に応じて `runtime/rag/jsonize_rag_tree.py`

`rag/corrective-action-report` 配下の Markdown report は、build前に `runtime/rag/standardize_corrective_report_names.py --source-dir rag/corrective-action-report --replace-references` で `YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md` に統一してください。標準は8桁です。

RAG artifact のファイル名は UUID にしてください。検索はファイル名ではなく JSON の `content` と metadata を対象にします。

`normalize_documents.py`、`chunk_documents.py`、`jsonize_rag_tree.py` は標準で `--clean-output` を使い、旧ファイル名artifactを混在させないでください。

既存 artifact は、ユーザーが明示しない限り削除しないでください。
