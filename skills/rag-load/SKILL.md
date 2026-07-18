---
name: rag-load
description: Load prior knowledge from the Ariadne AI Workflow file-based RAG before development work. Use when the user selects /rag-load, asks to read RAG, search RAG, load RAG context, retrieve prior corrective action reports, prepare context before development flow, or run parallel RAG retrieval and compression.
---

# RAG Load Skill

## Slash Command

Use this skill when the user specifies:

```text
/rag-load
```

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

## Purpose

Read existing file-based RAG knowledge before development work by running `runtime/rag/rag_dispatcher.py`.

The dispatcher creates or accepts multiple retrieval queries, runs `runtime/rag/retrieve_context.py` in parallel, and aggregates the compressed context packs. Compression remains implemented by `retrieve_context.py`.

Search uses JSON content and metadata from the indexes. Do not rely on RAG filenames; artifact filenames are UUID-based.

This is the RAG reading flow. Use `rag-build` to create or refresh RAG indexes.

Default workflow repository root:

```text
C:\github\ariadne-ai-workflow-platform
```

## Parameters

- `query`: main search query. Optional when task context exists.
- `queries`: explicit list of search queries. If provided, use these directly.
- `repository`: optional filter passed to `retrieve_context.py --repository`.
- `branch`: optional filter passed to `retrieve_context.py --branch`.
- `project`: optional filter passed to `retrieve_context.py --project`.
- `tag`: optional repeated filter passed to `retrieve_context.py --tag`.
- `search-mode`: default `hybrid`.
- `top-k`: default `5`.
- `max-chars`: default `4000`.
- `parallel`: default `true`.

## Query Planning

If the user does not provide explicit `queries`, derive 3 to 5 short queries from the current development task.

Use these query types when applicable:

- repository or system name
- feature / maintenance intent
- component names and files
- safety, STOP, communication loss, startup, shutdown, rollback, telemetry, observability
- architecture, responsibility boundary, test gap, documentation gap

Example:

```text
MainWindow 分離 責務集中
STOP shutdown safe state
TelemetryService Watchdog test gap
```

## Dispatcher

Use the dispatcher as the standard command:

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "<task summary>" `
  --repository "<repository>" `
  --branch "<branch>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

When explicit queries are known:

```powershell
python runtime/rag/rag_dispatcher.py `
  --query "MainWindow 分離 責務集中" `
  --query "STOP shutdown safe state" `
  --query "TelemetryService Watchdog test gap"
```

The dispatcher writes:

```text
rag/retrieval/<uuid>.json
```

Use each artifact's `artifact_type` to distinguish `rag-dispatch-plan`, `rag-load-dispatch`, `rag-retrieval-result`, and `rag-context-pack`.

The `rag-dispatch-plan` is the shared query planning artifact. It records intent, metadata filters, semantic hints, planned queries, query purposes, and stop conditions before retrieval starts.

When a prior plan should be reused across agents, pass it explicitly:

```powershell
python runtime/rag/rag_dispatcher.py `
  --dispatch-plan rag/retrieval/<plan-uuid>.json
```

Do not reimplement compression. Use the existing compression output from `retrieve_context.py`.

Markdown dispatch or context-pack files are optional debug artifacts and are written only when `--write-markdown` is explicitly used.

## Direct Retrieval Template

Use direct `retrieve_context.py` only for debugging a single query.

Run commands from:

```powershell
cd C:\github\ariadne-ai-workflow-platform
```

```powershell
python runtime/rag/retrieve_context.py `
  "<query>" `
  --chunks-index rag/indexes/chunks.jsonl `
  --embeddings-index rag/embeddings/chunks-embeddings.jsonl `
  --output-dir rag/retrieval `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

Add filters only when known:

```powershell
--project <project>
--repository <repository>
--branch <branch>
--tag <tag>
```

## Missing Index Handling

Before retrieval, verify these files exist:

```text
rag/indexes/chunks.jsonl
rag/embeddings/chunks-embeddings.jsonl
```

If missing or clearly stale, run `rag-build` first, then retry `rag-load`.

## Development Flow Integration

Before entering a development flow body, run `rag-load` after intake / repository preparation and before design or implementation.

Use the requirement document, target repository, target branch, comparison report, and issue summary to derive retrieval queries.

The loaded RAG context should inform:

- architecture and responsibility boundaries
- safety and STOP behavior
- communication loss behavior
- test strategy and regression risks
- documentation and operational gaps
- prior corrective action findings

## Workflow

1. Identify task context and target repository / branch if available.
2. Verify RAG indexes and embeddings exist.
3. Run `runtime/rag/rag_dispatcher.py`.
4. Read the generated UUID-named `rag-dispatch-plan` to confirm why retrieval was performed.
5. Read the generated UUID-named dispatch JSON and referenced UUID-named context-pack JSON files.
6. Summarize the loaded prior knowledge in Japanese.
7. Carry the RAG findings into the subsequent development plan or review.

## Workflow Feedback Output

During every AI workflow run, capture actionable workflow friction or improvement candidates in `work/feedback/`.
Create or update a Feedback report when you observe ambiguity, repeated checks, missing context/docs, runtime observation gaps, noisy handoffs, encoding issues, or a reusable workflow improvement.

Use the existing helper when creating a new report:

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

Keep the initial `Review Status` as `Proposed`. Do not run `/self-improvement` automatically inside this workflow; `/self-improvement` is executed later when feedback has accumulated and a human is ready to review Accepted / Rejected / Deferred decisions.

## Guardrails

- Do not delete RAG artifacts.
- Do not edit source reports during RAG loading.
- Do not proceed into implementation if RAG loading reveals unresolved safety-critical findings relevant to the task.
- If retrieval fails because indexes are missing, run `rag-build` rather than hand-searching reports.
