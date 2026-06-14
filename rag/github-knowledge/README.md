# GitHub Knowledge RAG

This directory stores approved GitHub Repository Knowledge Maintenance source reports.

Use it for knowledge extracted from Issues, Pull Requests, comments, documentation, Corrective Action Reports, and approved repair outcomes.

Do not store raw GitHub thread dumps. Keep concise source references, evidence summaries, limits, and reusable knowledge.

## Naming

Use the same Markdown report naming style as the rest of the RAG source areas:

```text
YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Example:

```text
20260614203235_Q7M4KD_localty-system-robot-github-knowledge.md
```

Keep this directory limited to:

- `README.md`
- approved source Markdown files named `YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md`

Do not store sidecar JSON, normalized JSON, chunk JSON, indexes, embeddings, or retrieval results in this directory.

## Publish Flow

Generate candidates under `work/<work-id>/process-report/` first. Publish source Markdown here only after human approval:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
  --work-id "<work-id>" `
  --publish-rag `
  --human-check approved
```

Then regenerate RAG artifacts in this order:

1. normalize approved source Markdown into UUID JSON
2. chunk normalized JSON
3. rebuild indexes
4. rebuild embeddings

Normalize:

```powershell
uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/github-knowledge `
  --output-dir rag/normalized `
  --document-type github-repository-knowledge
```

Chunk:

```powershell
uv run python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks
```

Index:

```powershell
uv run python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes
```

Embedding:

```powershell
uv run python runtime/rag/embed_chunks.py `
  --chunks-index rag/indexes/chunks.jsonl `
  --output rag/embeddings/chunks-embeddings.jsonl
```

Final landing:

```text
rag/normalized/<uuid>.json
```

Use the normalized UUID JSON as the durable machine-readable RAG record. Chunk JSON, indexes, embeddings, retrieval results, and context packs are derived artifacts.

## Current Normalized Output

```text
rag/normalized/f9c9b5fc-c59c-50cf-bc09-769655f65129.json
```
