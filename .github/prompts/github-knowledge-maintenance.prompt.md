---
name: github-knowledge-maintenance
description: Maintain a GitHub repository as a reusable knowledge asset without erasing Git history or changing commit source.
argument-hint: "<target-repository> <scan-mode> <repair-mode> [rag]"
agent: agent
---

# GitHub Repository Knowledge Maintenance Workflow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

## Runtime Entrypoint

Follow `.github/shared/runtime-entrypoint-policy.md`. Use `aiwfctl` / `runtime/ctl/ctl.py` as the official entrypoint for Context First, Human Check, GitHub knowledge maintenance, close archive, and self-improvement operations.

On Windows 11, start from `.\runtime\windows-ps1\aiwf.ps1 ctl ...`; the PS1 runtime handles PowerShell/UTF-8/path normalization and then delegates to `aiwfctl`.

## Purpose

This workflow maintains GitHub Repository knowledge assets for future AI workflows and RAG.

It treats Git history as historical evidence and improves Issue, Pull Request, merge comment, semantic commit subject, commit body, Documentation, Corrective Action Report, Knowledge DB, and RAG candidate quality without changing commit source.

Existing commit message/body rewrite is part of the workflow, but it is a high-risk repair path. It requires explicit item-level human approval, before/after SHA mapping, rollback plan, and reviewed force-push command when needed.

Small rebase maintenance for 1-3 file commit leakage is also a high-risk repair path. Run it as explicit stages: detect commit leakage, calculate the rebase execution plan, output the plan report, generate a schema-compliant replay package from approved candidates, and execute rebase only after Human Check approval.

Do not complete a useless or accidental commit by inventing a strange Issue reference, PR story, or commit message after the fact. The rebase repair must either absorb the files into the proper semantic commit, split them into a real independent responsibility, drop an empty/noise commit, or explicitly keep it with existing evidence.

Semantic commit subject quality is mandatory for commit repair. The subject shown in GitHub commit lists must be meaningful by itself and should follow `type(scope): responsibility/result`. The body then records intent, scope, decision, impact, and reusable maintenance knowledge.

## Required Inputs

- Target repository
- Scan mode: `repository`, `issue`, `pull-request`, `recent`, or `full`
- Repair mode: `proposal` or `apply`
- RAG output flag

## Delegated Agents

Use the agents in this order:

1. `.github/agents/repository-discovery-agent.prompt.md`
2. `.github/agents/github-metadata-collector-agent.prompt.md`
3. `.github/agents/knowledge-asset-discovery-agent.prompt.md`
4. `.github/agents/narrative-analyzer-agent.prompt.md`
5. `.github/agents/documentation-repair-agent.prompt.md`
6. `.github/agents/github-documentation-sync-agent.prompt.md`
7. `.github/agents/knowledge-db-registrar-agent.prompt.md`

## Runtime Helpers

Default work folders are short and branch-scoped:

```text
work/github/<target-branch>/<scan-mode>/
work/github/original/<scan-mode>/
```

Use `original` when no `--target-branch` is provided.

Initialize:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

Create analysis scaffold:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge analysis-template `
  --work-id "<work-id>"
```

Create repair plan:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge repair-plan `
  --work-id "<work-id>"
```

Detect small rebase candidates:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge detect-rebase `
  --work-id "<work-id>" `
  --base "HEAD~30" `
  --head "HEAD"
```

Create GitHub sync plan:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge sync-plan `
  --work-id "<work-id>"
```

Create the OK / NG review checklist for Issue / PR / comment repair actions:

```powershell
.\runtime\windows-ps1\aiwf.ps1 ctl github-knowledge sync-review-plan `
  --work-id "<work-id>"
```

Ingest the checked review plan through ctl:

```powershell
.\runtime\windows-ps1\aiwf.ps1 ctl github-knowledge sync-review-intake `
  --work-id "<work-id>" `
  --human-check approved
```

Execute one reviewed and approved GitHub sync action:

```powershell
aiwfctl github-knowledge sync-apply `
  --work-id "<work-id>" `
  --action-id "<action-id>" `
  --human-check approved
```

Create high-risk rebase review plan:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-plan `
  --work-id "<work-id>"
```

Execute approved rebase candidate:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-review-intake `
  --work-id "<work-id>" `
  --human-check approved
```

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-package `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --apply-mode direct
```

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rebase-apply `
  --work-id "<work-id>" `
  --package-path "work/<work-id>/context/rebase-replay-package.json" `
  --human-check approved
```

If the replay is already verified and only the remote reflection remains, do not regenerate the package or hand-edit workflow JSON. Use the push-only runtime:

```powershell
.\runtime\windows-ps1\aiwf.ps1 ctl github-knowledge publish-verified-replay `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --expected-remote-sha "<approved-remote-sha>" `
  --human-check approved
```

This command consumes the latest unpublished verified replay execution, checks tree equality and the exact remote SHA, then publishes the verified `new_tip` with `force-with-lease`.

After approved rebase repair is verified, run commit message/body repair before GitHub sync when weak semantic subjects remain:

```powershell
.\runtime\windows-ps1\aiwf.ps1 ctl github-knowledge message-repair-plan `
  --work-id "<work-id>" `
  --source-ref "origin/<branch>"
```

Ingest the single OK / NG checklist:

```powershell
.\runtime\windows-ps1\aiwf.ps1 ctl github-knowledge message-review-intake `
  --work-id "<work-id>" `
  --human-check approved
```

Generate the tree-preserving message repair package:

```powershell
.\runtime\windows-ps1\aiwf.ps1 ctl github-knowledge message-repair-package `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --source-ref "origin/<branch>" `
  --expected-remote-sha "<remote-sha>"
```

Execute the package through the existing replay apply runtime:

```powershell
.\runtime\windows-ps1\aiwf.ps1 ctl github-knowledge rebase-apply `
  --work-id "<work-id>" `
  --package-path "work/<work-id>/context/message-repair-package.json" `
  --human-check approved `
  --push
```

Message repair must not change the final tree. The runtime records before/after SHA mapping and verifies repaired subjects with `git log --format="%H %s"` before GitHub sync may continue.

Create RAG candidate:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rag-candidate `
  --work-id "<work-id>"
```

Publish RAG candidate only after approval:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . github-knowledge rag-candidate `
  --work-id "<work-id>" `
  --publish-rag `
  --human-check approved
```

## Required JSON

All analysis and repair decisions must be recorded before GitHub mutation:

```text
work/<work-id>/context/github-knowledge-analysis.json
```

Schema:

```text
.github/schemas/github-knowledge-analysis.schema.json
```

## Workflow

1. Identify repository and scan scope.
2. Collect GitHub metadata with GitHub CLI/API.
3. Discover knowledge assets.
4. Analyze Issue -> Pull Request -> Review -> Comment -> Documentation narrative consistency.
5. Create repair proposals, including semantic subject and commit body supplement proposals when source changes are not sufficiently explained.
6. Detect 1-3 file commit leakage with `detect-rebase-candidates` and record candidates in `history_rewrite_candidates`.
7. Stop for human review.
8. Generate a `rebase-plan` execution report for any high-risk small rebase candidate.
9. Ingest the reviewed OK / NG checklist with `aiwfctl github-knowledge rebase-review-intake --human-check approved`; do not hand-edit `approval_status` or `repair_goal`.
10. Generate `rebase-replay-package.json` only with `aiwfctl github-knowledge rebase-package` from candidates whose `approval_status: approved`; do not hand-write replay JSON or generate ad hoc Python helpers under `work/<work-id>/context/`.
11. Execute approved small rebase packages with `rebase-apply` and verify before/after SHA mapping.
12. Execute existing commit message/body rewrite through `message-repair-plan`, `message-review-intake`, `message-repair-package`, and `rebase-apply` only when the high-risk Git rewrite review plan is explicitly approved and the target candidate has `approval_status: approved`.
13. Generate an approval-gated GitHub documentation sync plan only after rebase and message repair candidates are resolved.
14. Generate and ingest the `sync-review-plan` OK / NG checklist before any Issue / PR / comment repair execution.
15. Execute only reviewed and approved GitHub CLI/API updates through `github-sync-apply` / `aiwfctl github-knowledge sync-apply`.
16. Generate Knowledge DB and RAG candidates.
17. Publish RAG candidates only after human approval.

## Guardrails

- Do not erase Git history or hide historical evidence.
- Do not change commit source, source code, README content, or configuration content in the target repository.
- Existing commit message/body rewrite requires explicit item-level human approval, before/after SHA mapping, rollback plan, and reviewed force-push command when needed.
- 1-3 file commit leakage rebase requires detection, `rebase-plan`, item-level human approval, before/after SHA mapping, rollback plan, and verification commands.
- Approved small rebase packages must be generated by `aiwfctl github-knowledge rebase-package`; do not hand-write replay JSON or create temporary `*.py` helpers in `work/<work-id>/context/`.
- Approved message rewrite packages must be generated by `aiwfctl github-knowledge message-repair-package` and executed by `rebase-apply`; do not amend commits manually.
- Use the `rebase-plan` legend to resolve legitimate detected diffs as `keep-with-evidence` or false positives as `no-rewrite`; do not leave them pending.
- Run rebase maintenance before GitHub sync when candidates exist. If no rebase candidates are detected, GitHub sync may proceed after Human Check.
- Do not run `github-sync-apply` while unresolved `history_rewrite_candidates` remain.
- Do not run `github-sync-apply` while pending or approved `message_repair_candidates` remain unverified.
- Do not mark rebase maintenance complete by attaching a new Issue/message to a useless commit. Completion requires absorb/split/drop/no-rewrite/keep-with-evidence disposition and reviewed evidence.
- Do not accept body-only repairs when the GitHub commit-list subject remains vague.
- Avoid weak semantic subjects such as "対応", "修正", "更新", file-name-only subjects, or repository-name-only scopes when source evidence supports a more precise scope.
- Prefer GitHub CLI/API; clone only after explicit human approval.
- Do not mutate GitHub from a free-form summary. Update `github-knowledge-analysis.json` first.
- Do not execute `gh issue edit`, `gh issue comment`, `gh pr edit`, `gh pr comment`, or `gh api` mutation commands without item-level human approval.
- Do not mark `github_sync_actions` approved by hand; use `github-sync-review-intake` to record `human_review_decision: OK` and `human_review_source`.
- Do not manually run approved GitHub sync actions outside ctl/runtime. Use `github-sync-apply` so the execution result is written back to analysis JSON.
- Do not execute `git rebase`, `git commit --amend`, or force push without item-level human approval.
- Do not run RAG publication without explicit human approval.

## Completion

The workflow is complete when:

- Repository metadata was collected or the missing collection was recorded.
- Knowledge assets were extracted.
- Narrative gaps were detected or explicitly recorded as none.
- Repair proposals were generated, including semantic subject and commit body repair when needed.
- Human review was completed.
- Only approved GitHub documentation assets were updated.
- Only explicitly approved commit message/body rewrites were executed, semantic subject was verified in commit-list view, and before/after SHA mapping was recorded.
- Knowledge DB candidates were generated.
- RAG candidates were generated when requested.
