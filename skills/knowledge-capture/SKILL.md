---
name: knowledge-capture
description: Finalize a completed corrective action issue by generating PR material, checking docs evidence placement, extracting RAG/docs candidates, and preparing archive readiness without changing implementation. Use when the user selects /knowledge-capture or asks to run finalization and knowledge recovery for work/issue-XXX.
---

# Knowledge Capture Skill

## Default Language

Respond to the user in Japanese by default.

## Purpose

改善作業完了後に、今回得られた知識と証跡を未来のAIと人間が再利用できる形へ整理します。

This skill does not implement code changes, alter design, push branches, run RAG registration, or move archives unless the user explicitly approves the specific action.

## Slash Command

```text
/knowledge-capture --issue issue-11 --repository localty-system-gui --branch feature/issue-11
```

Minimum:

```text
/knowledge-capture issue-11
```

## Source Work Folder

```text
work/<issue-id>/
```

Required source artifacts:

```text
work/<issue-id>/process-report/
work/<issue-id>/test-specifications/
work/<issue-id>/test-evidence/
```

Target repository docs evidence paths:

```text
work/<issue-id>/source/repository/docs/<issue-id>/unit_test/
work/<issue-id>/source/repository/docs/<issue-id>/integration_connectivity_test/
```

## Workflow

Run from repository root:

```powershell
cd C:\github\intent-driven-robotics-ai-workflow
```

### 1. Generate Knowledge Capture Package

```powershell
python runtime/workflow/knowledge_capture.py `
  --issue "<issue-id>" `
  --repository "<repository>" `
  --branch "<branch>" `
  --base-work-id "<base-work-id>"
```

Generated under `work/<issue-id>/process-report/`:

```text
pull-request-title.md
pull-request-description.md
merge-comment.md
knowledge-capture-report.md
knowledge-capture-*.json
```

### 2. Confirm Test Evidence Docs Placement

Confirm that test case tables and evidence are stored under:

```text
docs/<issue-id>/unit_test
docs/<issue-id>/integration_connectivity_test
```

If either path is missing or empty, report it and stop before push.

### 3. Push Gate

After docs evidence is present and human approval is recorded, push only the issue branch:

```powershell
python runtime/scm/push_branch.py `
  --work-id "<issue-id>" `
  --human-check approved `
  --set-upstream
```

### 4. RAG Candidate Extraction

Use the report to identify RAG candidates from:

```text
work/<issue-id>/process-report
work/<issue-id>/test-specifications
work/<issue-id>/test-evidence
```

Do not run `/rag-build` until the user approves RAG registration.

### 5. Docs Candidate Extraction

Classify durable operational knowledge that should become docs rather than only RAG.

Examples:

- Docker / UDP Broadcast
- Windows / MSYS2 / Docker Desktop differences
- GUI design
- Fault Injection design
- Packet Monitor design
- PyQt6 + QTimer + Thread design
- camera input design
- test evidence policy

### 6. Archive Readiness

Check whether the work folder can move:

```text
work/<issue-id>
  -> work/close/<issue-id>
```

### 7. Base Work Reset

Before deleting the base work folder, preserve the base-phase process reports:

```text
work/<base-work-id>/process-report
  -> work/close/<issue-id>/process-report/base-work-<base-work-id>
```

After the copy is verified, delete:

```text
work/<base-work-id>
```

This reset keeps the next corrective action flow from reusing stale base checkout or Issue-preparation artifacts.

Do not move the issue work folder or delete the base work folder until the user approves the specific action.

## Output Summary

Use:

```text
=== Knowledge Capture Summary ===

PR Documents
  OK

Test Evidence
  OK

RAG Candidates
  3

Docs Candidates
  2

Archive
  READY

Human Action
  Push feature/issue-XXX
  Run approved RAG build
  Move work/issue-XXX to work/close/issue-XXX
```

## Guardrails

- Do not change implementation code.
- Do not change design.
- Do not install libraries.
- Do not push without human approval.
- Do not run RAG registration / rebuild without human approval.
- Do not move archive without human approval.
- Do not delete `work/<base-work-id>` until its `process-report` has been preserved under `work/close/<issue-id>/process-report/base-work-<base-work-id>` and the copy has been verified.
- Do not delete evidence.
- Report missing docs evidence before push.
