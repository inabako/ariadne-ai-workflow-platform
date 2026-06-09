---
name: docs-sync
description: Compare implementation and docs on a target branch, store docs drift analysis as JSON, create an Issue, create feature/issue-XXX, update docs only, push after approval, then prepare RAG capture and archive.
argument-hint: "<target-repository> <target-branch>"
agent: agent
---

# Documentation Sync Workflow

## Purpose

This workflow keeps repository documentation aligned with the actual implementation.

It is not an implementation workflow. It must update docs only.

## Required Inputs

- Target repository
- Target branch, normally `develop`

Example:

```text
/docs-sync localty-system-gui develop
```

## Delegated Agent

Use:

```text
.github/agents/docs-drift-analyzer-agent.prompt.md
```

## Workflow

1. Fetch the target branch from GitHub into `work/<target-branch>/`.
2. Compare implementation and `docs/` content. RAG reference is allowed.
3. Store the drift result as JSON.
4. Convert the JSON into an Issue body.
5. Create a GitHub Issue after human approval.
6. Create `feature/issue-<issue-number>` from the target branch.
7. Clone the issue branch under `work/issue-<issue-number>/`.
8. Update `docs/` based on the JSON.
9. Commit and push the issue branch after human approval.
10. Create a Pull Request to `develop` after human approval.
11. Prepare knowledge capture and RAG candidates.
11. Move the work folder to `work/close/issue-<issue-number>` after human approval.

## Runtime Helpers

Initialize base work:

```powershell
python runtime/workflow/docs_sync.py init `
  --repository "<target-repository>" `
  --target-branch "<target-branch>"
```

Prepare base checkout:

```powershell
python runtime/scm/prepare_repository.py `
  --work-id "<target-branch>" `
  --repository "<target-repository>" `
  --target-branch "<target-branch>"
```

Create an empty analysis scaffold when useful:

```powershell
python runtime/workflow/docs_sync.py analysis-template `
  --work-id "<target-branch>"
```

Create Issue body from the JSON:

```powershell
python runtime/workflow/docs_sync.py issue-body `
  --work-id "<target-branch>"
```

Create the Issue:

```powershell
python runtime/github/issue_manager.py `
  --work-id "<target-branch>" `
  --title "<issue-title>" `
  --flow-label improvement `
  --body-file "work/<target-branch>/process-report/docs-sync-issue-body-YYYYMMDD_HHMMSS.md" `
  --create
```

Create and clone the issue branch:

```powershell
python runtime/workflow/docs_sync.py init `
  --repository "<target-repository>" `
  --target-branch "<target-branch>" `
  --work-id "issue-<issue-number>" `
  --base-work-id "<target-branch>"

python runtime/scm/create_issue_branch.py `
  --work-id "issue-<issue-number>" `
  --issue-number "<issue-number>" `
  --repository "<target-repository>" `
  --base-branch "<target-branch>" `
  --link-to-issue
```

Commit and push:

```powershell
python runtime/scm/commit_changes.py `
  --work-id "issue-<issue-number>" `
  --message "docs: sync documentation with implementation" `
  --all

python runtime/scm/push_branch.py `
  --work-id "issue-<issue-number>" `
  --human-check approved `
  --set-upstream
```

Create Pull Request to `develop` after push:

```powershell
python runtime/github/pull_request_manager.py `
  --work-id "issue-<issue-number>" `
  --base develop `
  --create `
  --human-check approved
```

## Required JSON

The drift analysis must be saved before Issue creation:

```text
work/<target-branch>/context/docs-drift-analysis.json
```

Schema:

```text
.github/schemas/docs-drift-analysis.schema.json
```

## Guardrails

- Do not edit docs in `work/<target-branch>/source/repository`.
- Do not change implementation code in the issue branch.
- Do not create an Issue from a free-form summary; use `docs-drift-analysis.json`.
- Do not push without human approval.
- Do not create Pull Requests without human approval.
- Do not run RAG registration or move archives without human approval.
- If docs and implementation conflict, current implementation evidence wins unless the human says otherwise.
- If implementation behavior is unclear, ask or record an unresolved question.

## Completion

The workflow is complete when:

- docs drift analysis JSON exists
- GitHub Issue exists
- issue branch exists as `feature/issue-<issue-number>`
- docs-only changes are committed and pushed
- RAG/docs candidates are prepared
- work folder is ready to move to `work/close/issue-<issue-number>`
