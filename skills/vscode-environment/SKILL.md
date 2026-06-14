---
name: vscode-environment
description: Build or maintain reproducible VSCode Workspace-as-Code environments for AI workflows. Use when the user selects /vscode-environment or asks to standardize .vscode/settings.json, tasks.json, launch.json, extensions.json, workspace.code-workspace, terminal profiles, AI extension setup, Docker/Git/Python/Node/Java tooling, or evidence-backed VSCode environment setup.
---

# VSCode Environment Workflow

## Default Language

Respond to the user in Japanese by default.

## Purpose

Manage a VSCode development environment as Workspace as Code so AI agents and humans can reproduce the same terminal, task, debug, tool, Docker, Git, language runtime, and evidence workflow setup.

## Required Inputs

- filled draft README such as `README_20260614.md` under `work/requirements/devlop-edit-draft/`
- target workspace or repository path, either in the draft or human answers
- intended workflow entry points, such as software workflow, IaC workflow, test workflow, evidence workflow
- required tools and runtimes
- required VSCode extensions
- terminal profiles and default shell policy

`work/requirements/devlop-edit-draft/README.md` is the human-editable scaffold. Treat it as a template, not as a filled requirement draft.

Filled drafts should be saved in the same directory as `README_*.md`, for example `README_20260614.md`. Legacy `.txt` drafts in that directory may also be inspected.

If `/vscode-environment` has no argument, do not infer a target workspace from the current directory. Read `work/requirements/devlop-edit-draft/`, inspect filled draft files such as `README_*.md`, create `open-questions.md` for blank, `TODO`, missing, or contradictory items, and stop before implementation.

If any required item is missing from the draft, do not infer silently. Create `open-questions.md` and stop before implementation.

Example:

```text
/vscode-environment C:\github\localty-system-gui
```

## Directory Model

Draft scaffold / intake:

```text
work/requirements/devlop-edit-draft/README.md
work/requirements/devlop-edit-draft/README_YYYYMMDD.md
```

Workflow artifacts stay in this repository:

```text
work/<work-id>/design-document/
work/<work-id>/context/
work/<work-id>/process-report/
work/<work-id>/test-evidence/
```

Workspace files are written only to the target workspace after requirements and validation pass:

```text
<target-workspace>/.vscode/settings.json
<target-workspace>/.vscode/tasks.json
<target-workspace>/.vscode/launch.json
<target-workspace>/.vscode/extensions.json
<target-workspace>/.vscode/<name>.code-workspace
```

## Runtime Helpers

Create or refresh the draft README scaffold:

```powershell
uv run python runtime/workflow/vscode_environment.py draft-template
```

Create open questions from the draft README:

```powershell
uv run python runtime/workflow/vscode_environment.py open-questions `
  --work-id "vscode-environment"
```

Initialize a workflow work area:

```powershell
uv run python runtime/workflow/vscode_environment.py init `
  --work-id "vscode-environment" `
  --target-dir "<target-workspace>"
```

Create a requirements scaffold:

```powershell
uv run python runtime/workflow/vscode_environment.py requirements-template `
  --work-id "vscode-environment"
```

Create a shared artifact validation scaffold:

```powershell
uv run python runtime/workflow/vscode_environment.py validation-template `
  --work-id "vscode-environment"
```

Create a reusable VSCode environment RAG source note:

```powershell
uv run python runtime/workflow/vscode_environment.py rag-template `
  --work-id "vscode-environment" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

Run environment preflight:

```powershell
uv run python runtime/environment/preflight.py `
  --profile vscode-environment `
  --work-id "vscode-environment" `
  --source-dir "<target-workspace>"
```

## Workflow

### 1. Draft Intake

Start from a human-editable draft README scaffold and a filled draft:

```text
work/requirements/devlop-edit-draft/README.md           # scaffold
work/requirements/devlop-edit-draft/README_YYYYMMDD.md  # filled draft
```

If the command has no argument, inspect `work/requirements/devlop-edit-draft/` for filled drafts. If no filled draft exists, the filled draft is incomplete, or required items are missing, create:

```text
work/<work-id>/design-document/open-questions.md
```

Stop until the human answers and approves.

### 2. Requirements Analysis

Use `.github/agents/workspace-requirements-analyst-agent.prompt.md`.

Create:

```text
work/<work-id>/design-document/workspace-requirements.md
```

The requirements must list required tools, extensions, terminal profiles, default shell, tasks, debug targets, AI workflow entry tasks, Docker usage, Git expectations, language runtimes, evidence outputs, and placeholders for personal paths or secrets.

### 3. Shared Artifact Validation

Use `.github/agents/workspace-shared-artifact-validator-agent.prompt.md`.

Validate that the requirements include:

- required tools
- required extensions
- required terminal profile structure
- required AI workflow entry points

If missing or contradictory, stop and write:

```text
work/<work-id>/design-document/open-questions.md
work/<work-id>/context/workspace-shared-artifact-validation.json
```

Do not implement `.vscode` files until validation is `pass` or human-approved `conditional-pass`.

### 4. VSCode Design

Use `.github/agents/vscode-architect-agent.prompt.md`.

Create:

```text
work/<work-id>/design-document/vscode-design.md
```

Design `settings.json`, `tasks.json`, `launch.json`, `extensions.json`, and `workspace.code-workspace`.

### 5. Terminal Design

Use `.github/agents/terminal-architect-agent.prompt.md`.

Create:

```text
work/<work-id>/design-document/terminal-design.md
```

Define terminal roles such as Dispatcher, Software Workflow, IaC Workflow, Docker Test, and Evidence. Keep personal paths as placeholders unless the user approves concrete local paths.

### 6. Implementation

Use `.github/agents/workspace-implementer-agent.prompt.md`.

Implement only after requirements, validation, and design artifacts exist. Preserve existing user settings unless the workflow explicitly replaces them. Prefer additive `.vscode` changes and document any migration.

### 7. Test And Evidence

Use `.github/agents/workspace-test-agent.prompt.md`.

Create:

```text
work/<work-id>/test-evidence/workspace-test.md
work/<work-id>/test-evidence/evidence/
```

Test JSON validity, task labels, terminal profile names, debug configs, Docker integration, language runtime commands, and AI workflow startup tasks. If a command needs human observation or external UI state, record it as human-check evidence.

### 8. Documentation

Use `.github/agents/workspace-documentation-writer-agent.prompt.md`.

Update the target workspace README or setup docs with setup steps, recommended extensions, tasks, troubleshooting, and evidence capture instructions.

### 9. RAG Capture And UUID JSON Finalization

When the VSCode environment pattern is reusable for Localty or another robotics workspace, save a Markdown source note under:

```text
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Use the runtime helper to create a correctly named draft:

```powershell
uv run python runtime/workflow/vscode_environment.py rag-template `
  --work-id "<work-id>" `
  --topic "localty-vscode-environment" `
  --repository "localty"
```

The Markdown file is the human-reviewable source note. It is not the final machine-readable knowledge artifact.

After human approval, normalize the approved source through the file-based RAG pipeline with `--source-dir rag/workspace-environment` and `--document-type workspace-environment-pattern`.

```powershell
uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/workspace-environment `
  --output-dir rag/normalized `
  --document-type workspace-environment-pattern
```

The final durable knowledge record is the generated UUID-named JSON document:

```text
rag/normalized/<uuid>.json
```

Chunk JSON, indexes, embeddings, and retrieval context packs are derived artifacts from that UUID-named normalized JSON. Use `rag/jsonized/<uuid>.json` only as a wrapper for existing non-UUID artifacts; it does not replace the normalized RAG document.

## Human Gates

Stop for human approval before:

- installing missing tools or extensions
- replacing existing `.vscode` files
- changing default terminal or shell behavior
- writing personal absolute paths
- running Docker Desktop or long-running tasks
- accepting `conditional-pass`

## Guardrails

- Do not depend on personal VSCode user settings.
- Do not store secrets in `.vscode`, `.code-workspace`, or committed docs.
- Do not infer missing terminal profile names, extension IDs, ports, runtime versions, or workflow task labels.
- Do not overwrite existing workspace files without reading and preserving useful content.
- Keep machine-specific values as placeholders when the workflow output is meant for a repository.
- Keep generated evidence under `work/<work-id>/test-evidence/`; put durable target-repository docs in the target workspace only when approved.

## Completion

The workflow is complete when:

- requirements and validation artifacts exist
- `.vscode` and optional `.code-workspace` files are valid JSON / JSONC
- required task and launch entries are testable or have recorded human-check evidence
- Docker / Git / runtime checks are recorded
- setup and troubleshooting docs are updated
- reusable VSCode environment knowledge is captured under `rag/workspace-environment/` when it should feed future RAG
- approved reusable knowledge is normalized into UUID-named JSON under `rag/normalized/` as the final RAG knowledge artifact
