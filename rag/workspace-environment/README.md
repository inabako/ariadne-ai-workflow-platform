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

## Build

```powershell
uv run python runtime/rag/standardize_corrective_report_names.py `
  --source-dir rag/workspace-environment `
  --replace-references

uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/workspace-environment `
  --output-dir rag/normalized `
  --document-type workspace-environment-pattern
```
