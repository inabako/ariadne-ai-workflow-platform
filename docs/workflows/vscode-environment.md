# VSCode Environment

`/vscode-environment` builds a reproducible VSCode Workspace-as-Code setup for a target repository or workspace.

## Command

```text
/vscode-environment <target-workspace-path>
```

When the command has no argument, the workflow reads the draft directory:

```text
work/requirements/devlop-edit-draft/
```

In that directory, `README.md` is the scaffold. Filled drafts should be saved as `README_*.md`, for example `README_20260614.md`. Legacy `.txt` drafts may also be inspected.

Example:

```text
/vscode-environment C:\github\localty-system-gui
```

## Outputs

Workflow artifacts:

```text
work/<work-id>/design-document/workspace-requirements.md
work/<work-id>/design-document/open-questions.md
work/<work-id>/design-document/vscode-design.md
work/<work-id>/design-document/terminal-design.md
work/<work-id>/context/workspace-shared-artifact-validation.json
work/<work-id>/process-report/
work/<work-id>/test-evidence/
```

Target workspace artifacts:

```text
.vscode/settings.json
.vscode/tasks.json
.vscode/launch.json
.vscode/extensions.json
workspace.code-workspace
```

Reference: [VSCode Environment](../reference/vscode-environment.md)

## Flow

1. Place or create the draft README scaffold at `work/requirements/devlop-edit-draft/README.md`.
2. Save a filled draft such as `work/requirements/devlop-edit-draft/README_20260614.md`.
3. Create `open-questions.md` from blank, `TODO`, missing, or contradictory items when required details are missing.
4. Wait for human review and approval.
5. Initialize `work/<work-id>` with the confirmed target workspace.
6. Analyze workspace requirements.
7. Validate shared artifacts.
8. Run environment preflight.
9. Design VSCode settings, tasks, launch configs, extensions, and workspace file.
10. Design terminal profiles and terminal roles.
11. Implement `.vscode` files after validation.
12. Test tasks, terminal startup, Docker/runtime integration, and AI workflow entry tasks.
13. Record evidence.
14. Update setup and troubleshooting docs.
15. Capture reusable workspace knowledge under `rag/workspace-environment/` as human-reviewable source Markdown.
16. After human approval, normalize the source Markdown into UUID-named JSON under `rag/normalized/`.
17. Treat `rag/normalized/<uuid>.json` as the final machine-readable knowledge artifact; chunk, index, embedding, and retrieval files are derived from it.

## Stop Rules

Stop and create `open-questions.md` when the command has no target argument, no filled `README_*.md` draft exists, unresolved `TODO` items remain, or required tools, extensions, terminal profiles, AI workflow entry tasks, or evidence requirements are missing or contradictory.

Stop for human approval before installing tools/extensions, replacing existing `.vscode` files, changing default terminal behavior, or accepting `conditional-pass`.

## RAG Capture

Reusable Localty VSCode environment knowledge is stored as source Markdown under:

```text
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Create a correctly named note with:

```powershell
uv run python runtime/workflow/vscode_environment.py rag-template `
  --work-id "vscode-environment" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

The Markdown note is the review source. The final knowledge artifact must be UUID-named JSON.

After human approval, normalize it as `workspace-environment-pattern`:

```powershell
uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/workspace-environment `
  --output-dir rag/normalized `
  --document-type workspace-environment-pattern
```

Final landing:

```text
rag/normalized/<uuid>.json
```

After normalization, build derived RAG artifacts as needed:

```powershell
uv run python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks

uv run python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes

uv run python runtime/rag/embed_chunks.py `
  --chunks-index rag/indexes/chunks.jsonl `
  --output rag/embeddings/chunks-embeddings.jsonl
```

## Source Skill

```text
skills/vscode-environment/SKILL.md
```
