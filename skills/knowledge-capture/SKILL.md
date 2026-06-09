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
work/<issue-id>/source/repository/docs/evidence/<issue-id>/test_specifications/
work/<issue-id>/source/repository/docs/evidence/<issue-id>/ut/
work/<issue-id>/source/repository/docs/evidence/<issue-id>/integration/
work/<issue-id>/source/repository/docs/evidence/<issue-id>/human_check/
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

The runtime also creates the target repository evidence scaffold when missing:

```text
work/<issue-id>/source/repository/docs/evidence/<issue-id>/README.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/test_specifications/README.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/ut/README.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/integration/README.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/integration/qtest/README.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/integration/manual/README.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/integration/startup/README.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/human_check/README.md
```

Scaffold `README.md` files keep empty directories visible to Git, but they are not test evidence.

`pull-request-title.md` must use the GitHub Issue title when an Issue record is available.

`pull-request-description.md` must include a Mermaid sequence diagram that shows the change flow from Issue to branch, tests, push, PR, and `develop`.

### 2. Confirm Test Evidence Docs Placement

Confirm that test case tables and evidence are stored under:

```text
docs/evidence/<issue-id>/test_specifications
docs/evidence/<issue-id>/test_specifications/unit-test-cases.md
docs/evidence/<issue-id>/test_specifications/integration-test-cases.md
docs/evidence/<issue-id>/test_specifications/human-check-list.md
docs/evidence/<issue-id>/ut
docs/evidence/<issue-id>/integration
docs/evidence/<issue-id>/human_check
```

If any required path is missing or empty, report it and stop before push.
If only scaffold `README.md` files exist, report that actual evidence is still missing.
If the expected test case files are missing, report which test layer is missing or why it is not required.

### 3. Push Gate

After docs evidence is present and human approval is recorded, push only the issue branch:

```powershell
python runtime/scm/push_branch.py `
  --work-id "<issue-id>" `
  --human-check approved `
  --set-upstream
```

### 4. Pull Request Gate

After the issue branch is pushed, create a Pull Request to `develop`.

Draft PR record:

```powershell
python runtime/github/pull_request_manager.py `
  --work-id "<issue-id>" `
  --base develop
```

Create PR after human approval:

```powershell
python runtime/github/pull_request_manager.py `
  --work-id "<issue-id>" `
  --base develop `
  --create `
  --human-check approved
```

Pull Request title uses the GitHub Issue title.

### 5. RAG Candidate Extraction

Use the report to identify RAG candidates from:

```text
work/<issue-id>/process-report
work/<issue-id>/test-specifications
work/<issue-id>/test-evidence
```

Do not run `/rag-build` until the user approves RAG registration.

### 6. Docs Candidate Extraction

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

### 7. Archive Readiness

Check whether the work folder can move:

```text
work/<issue-id>
  -> work/close/<issue-id>
```

### 8. Base Work Reset

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
  Open PR to develop
  Run approved RAG build
  Move work/issue-XXX to work/close/issue-XXX
```

## Guardrails

- Do not change implementation code.
- Do not change design.
- Do not install libraries.
- Do not push without human approval.
- Do not create Pull Requests without human approval.
- Do not run RAG registration / rebuild without human approval.
- Do not move archive without human approval.
- Do not delete `work/<base-work-id>` until its `process-report` has been preserved under `work/close/<issue-id>/process-report/base-work-<base-work-id>` and the copy has been verified.
- Do not delete evidence.
- Report missing docs evidence before push.
- Do not treat scaffold `README.md` files as actual evidence.
