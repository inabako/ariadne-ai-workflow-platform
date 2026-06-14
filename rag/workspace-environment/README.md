# Workspace Environment RAG

This directory stores reusable VSCode Workspace-as-Code knowledge for Localty and related robotics AI workflows.

Use it for:

- VSCode settings, tasks, launch, and extension patterns
- terminal role patterns
- runtime and preflight expectations
- trial-run evidence patterns
- reusable Localty environment decisions

Do not store:

- secrets, tokens, or personal credentials
- private machine-only paths unless explicitly marked as local-only evidence
- raw external article or documentation bodies
- unapproved guesses about target repository requirements

## Naming

Use the same Markdown report naming style as the rest of the RAG source areas:

```text
YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Example:

```text
20260612182244_K8M2Q7_localty-vscode-environment.md
```

Keep this directory limited to:

- `README.md`
- approved or draft source Markdown files named `YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md`

Do not store sidecar JSON, normalized JSON, chunk JSON, indexes, embeddings, or retrieval results in this directory.

## Build

Markdown files in this directory are human-reviewable source notes. They are not the final machine-readable RAG knowledge artifact.

After human approval, normalize approved notes into UUID-named JSON:

```powershell
uv run python runtime/rag/standardize_corrective_report_names.py `
  --source-dir rag/workspace-environment `
  --replace-references

uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/workspace-environment `
  --output-dir rag/normalized `
  --document-type workspace-environment-pattern
```

Final landing:

```text
rag/normalized/<uuid>.json
```

Use the normalized UUID JSON as the durable knowledge record. Chunk JSON, indexes, embeddings, retrieval results, and context packs are derived artifacts. Use `rag/jsonized/<uuid>.json` only when an existing non-UUID Markdown / JSON / JSONL / text artifact needs a UUID wrapper; it is not a substitute for the normalized RAG document.

## Current Normalized Outputs

Current source Markdown files in this directory have been normalized to:

```text
rag/normalized/4b8bf5b6-cad2-5bbd-9721-1ac0eb8994b2.json
rag/normalized/5f5fb26e-a2c6-50a0-bafd-6b45ddaa9b44.json
```
