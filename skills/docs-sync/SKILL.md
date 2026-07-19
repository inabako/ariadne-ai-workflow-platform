---
name: docs-sync
description: Compare implementation and docs on a target branch, store docs drift analysis as JSON, create a GitHub Issue, create feature/issue-XXX from the target branch, update docs only, push after human approval, then prepare RAG capture and archive. Use when the user selects /docs-sync or asks to synchronize repository docs with implementation.
---

# Documentation Sync Skill

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

## Purpose

実装と `docs/` 配下のドキュメントのズレを検出し、Issue 化して、docs だけを修正する workflow です。

この workflow は実装修正を行いません。

## Required Inputs

- target repository
- target branch, usually `develop`

Example:

```text
/docs-sync localty-system-gui develop
```

## Directory Model

Use two work folders:

- `work/<target-branch>/source/repository`: base checkout for read-only analysis
- `work/issue-<issue-number>/source/repository`: issue branch checkout for docs edits

The Git branch name is:

```text
feature/issue-<issue-number>
```

## Workflow

Run from:

```powershell
cd C:\github\ariadne-ai-workflow-platform
```

### 1. Initialize Base Work Area

```powershell
python runtime/workflow/docs_sync.py init `
  --repository "<target-repository>" `
  --target-branch "<target-branch>"
```

For `develop`, the default base work folder is:

```text
work/develop
```

If the folder already exists, stop and ask whether to reuse it. After confirmation, rerun with `--reuse-existing`.

### 2. Fetch Target Branch

```powershell
python runtime/scm/prepare_repository.py `
  --work-id "<target-branch>" `
  --repository "<target-repository>" `
  --target-branch "<target-branch>"
```

### 3. Compare Implementation And Docs

Use `.github/agents/docs-drift-analyzer-agent.prompt.md`.

Read:

```text
work/<target-branch>/source/repository
work/<target-branch>/source/repository/docs
```

RAG may be used as supporting context:

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "docs sync <target-repository> <target-branch>" `
  --repository "<target-repository>" `
  --branch "<target-branch>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

Current implementation and current docs are the primary evidence. RAG is not allowed to override current code.

### 4. Store Analysis JSON

Save the analysis before creating the Issue:

```text
work/<target-branch>/context/docs-drift-analysis.json
```

Schema:

```text
.github/schemas/docs-drift-analysis.schema.json
```

If helpful, create a scaffold:

```powershell
python runtime/workflow/docs_sync.py analysis-template `
  --work-id "<target-branch>"
```

### 5. Create Issue Body From JSON

```powershell
python runtime/workflow/docs_sync.py issue-body `
  --work-id "<target-branch>"
```

Generated:

```text
work/<target-branch>/process-report/docs-sync-issue-body-*.md
```

Do not create an Issue from a free-form summary. Update the JSON first.

### 6. Create GitHub Issue

Use the improvement flow prefix:

```text
[改善フロー] <issue-title>
```

Create a draft first unless the user has approved GitHub mutation:

```powershell
python runtime/github/issue_manager.py `
  --work-id "<target-branch>" `
  --title "<issue-title>" `
  --flow-label improvement `
  --body-file "<issue-body.md>"
```

After approval:

```powershell
python runtime/github/issue_manager.py `
  --work-id "<target-branch>" `
  --title "<issue-title>" `
  --flow-label improvement `
  --body-file "<issue-body.md>" `
  --create
```

### 7. Create Issue Branch And Clone

After the issue number exists:

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

The local work folder is:

```text
work/issue-<issue-number>
```

### 8. Update Docs Only

Use:

```text
work/<target-branch>/context/docs-drift-analysis.json
```

Update docs under:

```text
work/issue-<issue-number>/source/repository/docs
```

Rules:

- Do not change implementation code.
- Do not change tests, scripts, configs, or runtime files unless the Issue explicitly approves a docs-only metadata file outside `docs/`.
- If code behavior is unclear, stop and ask.
- Keep docs changes traceable to drift item IDs.

### 9. Commit And Push

Commit:

```powershell
python runtime/scm/commit_changes.py `
  --work-id "issue-<issue-number>" `
  --message "docs: sync documentation with implementation" `
  --all
```

Before push, confirm:

- only docs files are changed
- branch is `feature/issue-<issue-number>`
- source dir is `work/issue-<issue-number>/source/repository`

Push after human approval:

```powershell
python runtime/scm/push_branch.py `
  --work-id "issue-<issue-number>" `
  --human-check approved `
  --set-upstream
```

After push, create a Pull Request to `develop`.

Draft PR record:

```powershell
python runtime/github/pull_request_manager.py `
  --work-id "issue-<issue-number>" `
  --base develop
```

Create PR after human approval:

```powershell
python runtime/github/pull_request_manager.py `
  --work-id "issue-<issue-number>" `
  --base develop `
  --create `
  --human-check approved
```

The Pull Request title must use the GitHub Issue title.

### 10. Knowledge Capture / RAG

Prepare RAG candidates after push:

```text
work/issue-<issue-number>/process-report
work/<target-branch>/context/docs-drift-analysis.json
```

RAG registration requires explicit human approval. After approval, run `/rag-build` or the equivalent runtime RAG pipeline.

### 11. Archive

After approval:

```text
work/issue-<issue-number>
  -> work/close/improvement/issue-<issue-number> report-only archive
```

Before deleting `work/<target-branch>`, preserve base-phase process reports:

```text
work/<target-branch>/process-report
  -> work/close/improvement/issue-<issue-number>/links.md and summary reports
```

Do not prepare close archive, prune source/cache, or delete folders without explicit human approval.

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

- Do not implement code changes.
- Do not edit base checkout docs.
- Do not create GitHub Issues without approval.
- Do not push without approval.
- Do not create Pull Requests without approval.
- Do not run RAG registration / rebuild without approval.
- Do not prepare/prune close archive or delete base work without approval.
- Do not let old RAG override current repository evidence.
