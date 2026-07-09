---
name: rag-build
description: Build or refresh the Intent-Driven Robotics AI Workflow file-based RAG artifacts from Markdown reports. Use when the user selects /rag-build, asks to create RAG, update RAG, accumulate corrective action reports into RAG, normalize reports, chunk documents, build indexes, or create local embeddings.
---

# RAG Build Skill

## Slash Command

Use this skill when the user specifies:

```text
/rag-build
```

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

## Purpose

Create or refresh file-based RAG artifacts from Markdown reports.

This is the RAG creation flow. It does not retrieve context unless the user explicitly asks for retrieval too. Use `rag-load` for RAG reading before development work.

RAG artifact filenames are UUID-based. Search must use JSON content and metadata, not filename semantics.

Default workflow repository root:

```text
C:\github\ariadne-ai-workflow-platform
```

Default source reports:

```text
rag/corrective-action-report
```

External Web RAG source examples:

```text
rag/external-web/network
rag/external-web/go-runtime
rag/external-web/architecture
```

## Parameters

- `source-dir`: default `rag/corrective-action-report`
- `document-type`: default `corrective-action-report`
- `normalized-dir`: default `rag/normalized`
- `chunks-dir`: default `rag/chunks`
- `indexes-dir`: default `rag/indexes`
- `embeddings-output`: default `rag/embeddings/chunks-embeddings.jsonl`
- `jsonized-dir`: default `rag/jsonized`

If unspecified, use all defaults.

## Command Confirmation Policy

Do not ask conversational confirmation before read-only inspection commands.

If the execution environment requires approval for sandbox, filesystem, or write permissions, request that approval with a clear justification.

## Pipeline

Run commands from:

```powershell
cd C:\github\ariadne-ai-workflow-platform
```

### 0. Standardize Corrective Action Report Filenames

```powershell
python runtime/rag/standardize_corrective_report_names.py `
  --source-dir rag/corrective-action-report `
  --replace-references
```

Corrective action report Markdown filenames must use:

```text
YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md
```

### 1. Normalize Documents

```powershell
python runtime/rag/normalize_documents.py `
  --source-dir rag/corrective-action-report `
  --output-dir rag/normalized `
  --document-type corrective-action-report `
  --clean-output
```

For external-web RAG, normalize category Markdown into the same JSON document format while preserving provenance metadata:

```powershell
python runtime/rag/normalize_documents.py `
  --source-dir rag/external-web/network `
  --output-dir rag/normalized `
  --document-type external-web-knowledge
```

The normalizer preserves external-web front matter such as:

- `source_type`
- `category`
- `topic`
- `trust_level`
- `retrieved_at`
- `verify_before_use`
- `sources`
- `claims`
- `verification_notes`

### 2. Chunk Documents

```powershell
python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks `
  --clean-output
```

### 3. Build Index

```powershell
python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes
```

### 4. Build Local Embeddings

```powershell
python runtime/rag/embed_chunks.py `
  --chunks-index rag/indexes/chunks.jsonl `
  --output rag/embeddings/chunks-embeddings.jsonl
```

### Optional: JSONize Existing RAG Markdown Files

Use this when existing non-UUID JSON, JSONL, Markdown, or text files under `rag/` should be mirrored as UUID-named JSON wrapper artifacts.

```powershell
python runtime/rag/jsonize_rag_tree.py `
  --rag-dir rag `
  --output-dir rag/jsonized `
  --clean-output
```

Do not pass `--delete-source` unless the user explicitly requests removing original Markdown files.

## Output Files

Expected outputs:

```text
rag/normalized/*.json
rag/chunks/*.json
rag/indexes/documents.jsonl
rag/indexes/chunks.jsonl
rag/embeddings/chunks-embeddings.jsonl
rag/jsonized/*.json
```

## Workflow

1. Inspect the source report directory.
2. Run normalize, chunk, build index, and local embeddings in order.
3. Stop on the first failed stage and report the failed command.
4. Summarize document count, chunk count, embedding count, and output paths in Japanese.

## Workflow Feedback Output

During every AI workflow run, capture actionable workflow friction or improvement candidates in `work/feedback/`.
Create or update a Feedback report when you observe ambiguity, repeated checks, missing context/docs, runtime observation gaps, noisy handoffs, encoding issues, or a reusable workflow improvement.

Use the existing helper when creating a new report:

```powershell
python runtime/workflow/self_improvement.py create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

Keep the initial `Review Status` as `Proposed`. Do not run `/self-improvement` automatically inside this workflow; `/self-improvement` is executed later when feedback has accumulated and a human is ready to review Accepted / Rejected / Deferred decisions.

## Guardrails

- Do not delete existing RAG artifacts unless the user explicitly requests cleanup.
- Do not overwrite source reports manually.
- If Python is not available as `python`, use an available local Python after identifying it.
