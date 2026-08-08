---
name: knowledge-capture
description: Finalize a completed corrective action issue by generating PR material, checking docs evidence placement, extracting RAG/docs candidates, and preparing archive readiness without changing implementation. Use when the user selects /knowledge-capture or asks to run finalization and knowledge recovery for work/issue-XXX.
---

# Knowledge Capture Skill

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.ariadne/shared/output-language-policy.md`.

## Purpose

改善作業完了後に、今回得られた知識と証跡を未来のAIと人間が再利用できる形へ整理します。

This skill does not implement code changes, alter design, push branches, run RAG registration, create close archives, or prune archived source/cache unless the user explicitly approves the specific action.

## Slash Command

```text
/knowledge-capture --issue issue-11 --repository target-system --branch feature/issue-11
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
cd C:\github\ariadne-ai-workflow-platform
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

### 7. Report-only Close Archive Readiness

Check whether the completed issue can be summarized into a lightweight close archive:

```text
work/close/improvement/<issue-id>/
  00-summary.md
  01-work-report.md
  02-test-report.md
  03-review-report.md
  04-human-check.md
  05-retrospective.md
  links.md
  metadata.json
```

Prepare after human approval:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prepare --issue "<issue-id>" --require-rag
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive audit --issue "<issue-id>"
```

`close_archive.py prepare` はRAG source Markdownを自動検出し、吸収済みの具体的な知識をclose reportへ書き込みます。重要なRAG sourceが分かっている場合は、明示指定してください。

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prepare `
  --issue "<issue-id>" `
  --source-rag "work/db/ariadne-knowledge-platform/rag/normalized/<rag-source>.json" `
  --require-rag
```

薄いreportのままcloseしてはいけない作業では `--require-rag` を使います。自動検出を止め、明示指定した `--source-rag` だけを使いたい場合に限り `--no-auto-rag` を使います。

Do not keep source checkouts, `.git`, `.venv`, `node_modules`, build output, or cache files in `work/close`.

Prune is dry-run by default:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prune --issue "<issue-id>"
```

Actual pruning requires approval:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prune `
  --issue "<issue-id>" `
  --execute `
  --human-check approved
```

### 8. Base Work Reset

Before deleting the base work folder, summarize and link the base-phase process reports into the close archive:

```text
work/<base-work-id>/process-report
  -> work/close/improvement/<issue-id>/links.md and summary reports
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
  Prepare report-only close archive
  Optionally prune source/cache with approval
```

## Workflow Feedback Output

During every AI workflow run, capture actionable workflow friction or improvement candidates in `work/feedback/`.
Create or update a Feedback report when you observe ambiguity, repeated checks, missing context/docs, runtime observation gaps, noisy handoffs, encoding issues, or a reusable workflow improvement.

Use the existing helper when creating a new report:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

Keep the initial `Review Status` as `Proposed`. Do not run `/self-improvement` automatically inside this workflow; `/self-improvement` is executed later when feedback has accumulated and a human is ready to review Accepted / Rejected / Deferred decisions.

## Guardrails

- Do not change implementation code.
- Do not change design.
- Do not install libraries.
- Do not push without human approval.
- Do not create Pull Requests without human approval.
- Do not run RAG registration / rebuild without human approval.
- Do not create or prune close archive without human approval.
- Do not delete `work/<base-work-id>` until its `process-report` has been summarized / linked under `work/close/improvement/<issue-id>/` and the result has been verified.
- Do not delete evidence.
- Report missing docs evidence before push.
- Do not treat scaffold `README.md` files as actual evidence.
