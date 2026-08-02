# /knowledge-capture

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.ariadne/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

改善作業完了後、PR資料、テストエビデンス、RAG投入候補、docs投入候補、report-only close archive準備を整理します。

Knowledge Capture Agent を呼び出し、今回得られた知識を未来のAIと人間が再利用できる形に変換します。

コード修正や設計変更は行いません。

## Input

```text
/knowledge-capture \
  --issue issue-11 \
  --repository target-system \
  --branch feature/issue-11
```

Required:

- `--issue`: issue work folder name such as `issue-11`

Optional:

- `--repository`: target repository label
- `--branch`: issue branch name

## Agent

Use:

```text
.ariadne/agents/knowledge-capture-agent.prompt.md
```

## Execute

Run from repository root:

```powershell
.\runtime\windows-script\aiwf.cmd ctl workflow knowledge-capture `
  --issue "<issue-id>" `
  --repository "<repository>" `
  --branch "<branch>" `
  --base-work-id "<base-work-id>"
```

The runtime generates:

```text
work/<issue-id>/process-report/pull-request-title.md
work/<issue-id>/process-report/pull-request-description.md
work/<issue-id>/process-report/merge-comment.md
work/<issue-id>/process-report/knowledge-capture-report.md
work/<issue-id>/process-report/knowledge-capture-*.json
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

## 1. PR Documents

Generate:

```text
pull-request-title.md
pull-request-description.md
merge-comment.md
```

The documents must cover:

- improvement purpose
- changed behavior
- test summary
- integration / connectivity confirmation
- human confirmation items
- known constraints

## 2. Test Evidence Docs

Confirm:

```text
docs/evidence/<issue-id>/test_specifications
docs/evidence/<issue-id>/test_specifications/unit-test-cases.md
docs/evidence/<issue-id>/test_specifications/integration-test-cases.md
docs/evidence/<issue-id>/test_specifications/human-check-list.md
docs/evidence/<issue-id>/ut
docs/evidence/<issue-id>/integration
docs/evidence/<issue-id>/human_check
```

These paths are inside the target repository checkout:

```text
work/<issue-id>/source/repository/docs/evidence/<issue-id>/
```

If missing, report the missing path and stop before push.
If only scaffold `README.md` files exist, report that actual evidence is still missing.
If the expected test case files are missing, report which test layer is missing or why it is not required.

## 3. Push Gate

After test cases and evidence are stored under `docs/evidence/<issue-id>/`, push only the issue branch:

```powershell
.\runtime\windows-script\aiwf.cmd ctl scm push `
  --work-id "<issue-id>" `
  --human-check approved `
  --set-upstream
```

Do not push before docs evidence is present and human approval is recorded.

## 4. RAG Candidates

Extract RAG candidates from:

```text
work/<issue-id>/process-report
work/<issue-id>/test-specifications
work/<issue-id>/test-evidence
```

RAG registration / rebuild requires human approval.

After approval, use `/rag-build` or the equivalent runtime pipeline.

## 5. Docs Candidates

Extract docs candidates from durable operational knowledge.

Examples:

- Docker / UDP Broadcast
- Windows / MSYS2 / Docker Desktop differences
- GUI design
- Packet Monitor design
- Fault Injection design
- PyQt6 + QTimer + Thread design
- camera input design
- test evidence policy

## 6. Report-only Close Archive

Check:

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

After human approval, prepare and audit the archive:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prepare --issue "<issue-id>"
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive audit --issue "<issue-id>"
```

Do not retain source checkouts, `.git`, `.venv`, `node_modules`, build output, or cache files in `work/close`.
Pruning requires explicit approval:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prune `
  --issue "<issue-id>" `
  --execute `
  --human-check approved
```

## 7. Base Work Reset

Before deleting the base work folder, summarize and link the base-phase process reports:

```text
work/<base-work-id>/process-report
  -> work/close/improvement/<issue-id>/links.md and summary reports
```

Verify the generated archive reports before deletion.

Delete the base work folder only after human approval:

```text
work/<base-work-id>
```

## Output

```text
=== Knowledge Capture ===

PR Documents
OK

Evidence
OK

RAG
3 Candidates

Docs
2 Candidates

Archive
READY

Human Action
Push feature/issue-11
Run approved RAG build
Prepare report-only close archive for work/close/improvement/issue-11
Delete work/develop
Prune work/close/improvement/issue-11 after explicit approval
```

## Constraints

Do not:

- change code
- change design
- install libraries
- push without human approval
- run RAG registration without human approval
- prepare/prune close archive without human approval
- delete base work without summarizing / linking process-report and receiving human approval
- delete evidence
- treat scaffold `README.md` files as actual evidence
