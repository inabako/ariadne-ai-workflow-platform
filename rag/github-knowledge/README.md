# GitHub Knowledge RAG

このdirectoryは、承認済みのGitHub Repository Knowledge Maintenance source reportを保存します。

Issue、Pull Request、comment、documentation、Corrective Action Report、承認済みrepair outcomeから抽出したknowledgeを保存するために使います。

raw GitHub thread dumpは保存しません。source reference、evidence summary、limit、再利用可能knowledgeを簡潔に残します。

## Naming

RAG source area共通のMarkdown report naming styleを使います。

```text
YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

例:

```text
20260614203235_Q7M4KD_localty-system-robot-github-knowledge.md
```

このdirectoryには次だけを置きます。

- `README.md`
- `YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md` 形式のapproved source Markdown file

sidecar JSON、normalized JSON、chunk JSON、indexes、embeddings、retrieval resultsはこのdirectoryに置きません。

## Publish Flow

まず `work/<work-id>/process-report/` にcandidateを生成します。Human approval後にのみ、source Markdownをこのdirectoryへpublishします。

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
  --work-id "<work-id>" `
  --publish-rag `
  --human-check approved
```

その後、RAG artifactを次の順序で再生成します。

1. approved source MarkdownをUUID JSONへnormalizeする。
2. normalized JSONをchunk化する。
3. indexesを再構築する。
4. embeddingsを再構築する。

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

最終着地:

```text
rag/normalized/<uuid>.json
```

normalized UUID JSONを耐久的なmachine-readable RAG recordとして扱います。Chunk JSON、indexes、embeddings、retrieval results、context packsは派生artifactです。

## Current Normalized Output

```text
rag/normalized/f9c9b5fc-c59c-50cf-bc09-769655f65129.json
```
