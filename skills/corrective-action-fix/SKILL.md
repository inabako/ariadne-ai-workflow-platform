---
name: corrective-action-fix
description: Create a corrective action report for a specified GitHub repository and branch, store the base branch under work/<branch>, build/load RAG, create a GitHub Issue, create a separate work/issue-XXX folder with feature/issue-XXX branch, implement fixes, test, request human startup/integration approval, then push. Use when the user selects /corrective-action-fix or asks to move from improvement report creation into corrective implementation.
---

# Corrective Action Fix Skill

## Default Language

Respond to the user in Japanese by default.

## Required Inputs

- target repository: GitHub URL, Markdown link to a GitHub URL, git URL, owner/repo, or local path
- target branch: branch name to inspect and base the fix on

Example:

```text
/corrective-action-fix [inabako/localty-system-gui.git](https://github.com/inabako/localty-system-gui.git) develop
```

## Directory Model

Use two work folders:

- `work/<target-branch>/source/repository`: original/base branch checkout, for report, RAG, and reference
- `work/issue-<issue-number>/source/repository`: fix branch checkout, for implementation, tests, integration checks, and push

Keep the Git branch name as `feature/issue-<issue-number>`.

Do not use `feature/issue-<issue-number>` directly as a work folder name because the slash becomes a nested path on Windows.

## Workflow

Run commands from:

```powershell
cd C:\github\intent-driven-robotics-ai-workflow
```

### 1. Initialize Base Work Area

Create `work/<target-branch>`:

```powershell
python runtime/workflow/init_corrective_action_fix.py `
  --repository "<target-repository>" `
  --target-branch "<target-branch>"
```

For `develop`, the default `work_id` is `develop`.

### 2. Prepare Base Repository / Branch

Clone or fetch the target branch into `work/<target-branch>/source/repository`:

```powershell
python runtime/scm/prepare_repository.py `
  --work-id "<target-branch>" `
  --repository "<target-repository>" `
  --target-branch "<target-branch>"
```

### 3. Create Corrective Action Report

Run the same read-only analysis rules as `/corrective-action-report`.

Write the report to:

```text
rag/corrective-action-report/YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md
```

The report must include:

- prioritized findings
- recommended actions
- affected files/components
- expected unit tests
- startup/integration check expectations
- human-check items

### 4. Build RAG

Run `/rag-build` or the equivalent pipeline:

```powershell
python runtime/rag/standardize_corrective_report_names.py `
  --source-dir rag/corrective-action-report `
  --replace-references

python runtime/rag/normalize_documents.py `
  --source-dir rag/corrective-action-report `
  --output-dir rag/normalized `
  --document-type corrective-action-report `
  --clean-output

python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks `
  --clean-output

python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes

python runtime/rag/embed_chunks.py `
  --chunks-index rag/indexes/chunks.jsonl `
  --output rag/embeddings/chunks-embeddings.jsonl
```

### 5. Load RAG Before Implementation

Run `/rag-load` with the report, repository, branch, and intended fix as context:

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "<corrective action fix summary>" `
  --repository "<target-repository>" `
  --branch "<target-branch>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

Read the generated `artifact_type: rag-load-dispatch` JSON and referenced `artifact_type: rag-context-pack` JSON before implementation.

### 6. Create GitHub Issue

Create an issue body from the corrective action report and loaded RAG context.

Minimum sections:

- Intent
- Corrective action report path
- Findings to fix in this branch
- Implementation scope
- Unit tests
- Startup / integration check
- Human check gate
- Acceptance criteria

Create a draft unless the user explicitly approves GitHub mutation:

```powershell
python runtime/github/issue_manager.py `
  --work-id "<target-branch>" `
  --title "<issue-title>" `
  --body-file "<issue-body.md>"
```

When approved:

```powershell
python runtime/github/issue_manager.py `
  --work-id "<target-branch>" `
  --title "<issue-title>" `
  --body-file "<issue-body.md>" `
  --create
```

### 7. Initialize Issue Work Area And Branch

After an issue number exists, create `work/issue-<issue-number>`:

```powershell
python runtime/workflow/init_corrective_action_fix.py `
  --repository "<target-repository>" `
  --target-branch "<target-branch>" `
  --work-id "issue-<issue-number>" `
  --base-work-id "<target-branch>"
```

Clone/fetch the base branch into the issue work folder:

```powershell
python runtime/scm/prepare_repository.py `
  --work-id "issue-<issue-number>" `
  --repository "<target-repository>" `
  --target-branch "<target-branch>"
```

Create the Git branch:

```powershell
python runtime/scm/create_issue_branch.py `
  --work-id "issue-<issue-number>" `
  --issue-number "<issue-number>"
```

The work folder is `work/issue-<issue-number>`, and the Git branch is:

```text
feature/issue-<issue-number>
```

### 8. Implement Corrective Fixes

Implement in `work/issue-<issue-number>/source/repository` according to the corrective action report and loaded RAG.

Rules:

- Keep changes scoped to the Issue.
- Preserve safety behavior.
- If a safety-critical finding cannot be resolved, stop and report the blocker.
- Record implementation notes in `work/issue-<issue-number>/process-report/`.

### 9. Add And Run Unit Tests

Create or update unit tests that prove the fix.

Record commands and results in `work/issue-<issue-number>/test-evidence/`.

### 10. Startup / Integration Check

Run the appropriate startup or integration check for the target repository.

Record commands, logs, screenshots if useful, and outcome in `work/issue-<issue-number>/test-evidence/`.

### 11. Human Check Gate

Stop after startup/integration evidence is ready.

Ask the user to verify the startup/integration result.

Do not push until the user explicitly confirms the check is approved.

### 12. Push Issue Branch

After human approval:

```powershell
python runtime/scm/push_branch.py `
  --work-id "issue-<issue-number>" `
  --human-check approved `
  --set-upstream
```

## Guardrails

- Do not push before human startup/integration approval.
- Do not create GitHub Issues unless the user has approved mutation or the environment policy allows it for this flow.
- Do not skip RAG build/load.
- Do not implement on the target branch directly.
- Keep `/corrective-action-report` read-only; use this skill for implementation.
