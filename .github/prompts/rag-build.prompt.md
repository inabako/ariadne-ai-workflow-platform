# /rag-build

RAG Build Skill を使って、Intent-Driven Robotics AI Workflow の Markdown report を file-based RAG artifact に変換してください。

既定では日本語で応答してください。

実行する既定 pipeline:

1. `runtime/rag/normalize_documents.py`
2. `runtime/rag/chunk_documents.py`
3. `runtime/rag/build_index.py`
4. `runtime/rag/embed_chunks.py`

既存 artifact は、ユーザーが明示しない限り削除しないでください。
