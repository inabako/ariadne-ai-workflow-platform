# /knowledge-capture

## Purpose

改善作業完了後、PR資料、テストエビデンス、RAG投入候補、docs投入候補、Archive対象を整理します。

Knowledge Capture Agent を呼び出し、今回得られた知識を未来のAIと人間が再利用できる形に変換します。

コード修正や設計変更は行いません。

## Input

```text
/knowledge-capture \
  --issue issue-11 \
  --repository localty-system-gui \
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
.github/agents/knowledge-capture-agent.prompt.md
```

## Execute

Run from repository root:

```powershell
python runtime/workflow/knowledge_capture.py `
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
docs/<issue-id>/unit_test
docs/<issue-id>/integration_connectivity_test
```

These paths are inside the target repository checkout:

```text
work/<issue-id>/source/repository/docs/<issue-id>/
```

If missing, report the missing path and stop before push.

## 3. Push Gate

After test cases and evidence are stored under `docs/<issue-id>/`, push only the issue branch:

```powershell
python runtime/scm/push_branch.py `
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

## 6. Archive

Check:

```text
work/<issue-id>
  -> work/close/<issue-id>
```

Do not move the folder until the user approves archive.

## 7. Base Work Reset

Before deleting the base work folder, preserve the base-phase process reports:

```text
work/<base-work-id>/process-report
  -> work/close/<issue-id>/process-report/base-work-<base-work-id>
```

Verify copied file names and sizes before deletion.

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
Preserve work/develop/process-report under work/close/issue-11
Delete work/develop
Move work/issue-11 to work/close/issue-11
```

## Constraints

Do not:

- change code
- change design
- install libraries
- push without human approval
- run RAG registration without human approval
- move archive without human approval
- delete base work without preserving process-report and receiving human approval
- delete evidence
