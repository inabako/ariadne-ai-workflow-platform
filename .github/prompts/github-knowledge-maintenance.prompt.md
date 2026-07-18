---
name: github-knowledge-maintenance
description: Maintain a GitHub repository as a reusable knowledge asset without erasing Git history or changing commit source.
argument-hint: "<target-repository> <scan-mode> <repair-mode> [rag]"
agent: agent
---

# GitHub Repository Knowledge Maintenance Workflow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

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

Initialize:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

Create analysis scaffold:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge analysis-template `
  --work-id "<work-id>"
```

Create repair plan:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge repair-plan `
  --work-id "<work-id>"
```

Detect small rebase candidates:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge detect-rebase `
  --work-id "<work-id>" `
  --base "HEAD~30" `
  --head "HEAD"
```

Create GitHub sync plan:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge sync-plan `
  --work-id "<work-id>"
```

Execute approved GitHub sync action:

```powershell
aiwfctl github-knowledge sync-apply `
  --work-id "<work-id>" `
  --action-id "<action-id>" `
  --human-check approved
```

Create high-risk rebase review plan:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge rebase-plan `
  --work-id "<work-id>"
```

Execute approved rebase candidate:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge rebase-package `
  --work-id "<work-id>" `
  --target-branch "<branch>" `
  --apply-mode direct
```

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge rebase-apply `
  --work-id "<work-id>" `
  --package-path "work/<work-id>/context/rebase-replay-package.json" `
  --human-check approved
```

Create RAG candidate:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge rag-candidate `
  --work-id "<work-id>"
```

Publish RAG candidate only after approval:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . github-knowledge rag-candidate `
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
9. Generate `rebase-replay-package.json` only with `aiwfctl github-knowledge rebase-package` from candidates whose `approval_status: approved`; do not hand-write replay JSON or generate ad hoc Python helpers under `work/<work-id>/context/`.
10. Execute existing commit message/body rewrite or small rebase only when the high-risk Git rewrite review plan is explicitly approved and the target candidate has `approval_status: approved`.
11. Generate an approval-gated GitHub documentation sync plan only after rebase candidates are resolved.
12. Execute only approved GitHub CLI/API updates through `github-sync-apply` / `aiwfctl github-knowledge sync-apply`.
13. Generate Knowledge DB and RAG candidates.
14. Publish RAG candidates only after human approval.

## Guardrails

- Do not erase Git history or hide historical evidence.
- Do not change commit source, source code, README content, or configuration content in the target repository.
- Existing commit message/body rewrite requires explicit item-level human approval, before/after SHA mapping, rollback plan, and reviewed force-push command when needed.
- 1-3 file commit leakage rebase requires detection, `rebase-plan`, item-level human approval, before/after SHA mapping, rollback plan, and verification commands.
- Approved small rebase packages must be generated by `aiwfctl github-knowledge rebase-package`; do not hand-write replay JSON or create temporary `*.py` helpers in `work/<work-id>/context/`.
- Use the `rebase-plan` legend to resolve legitimate detected diffs as `keep-with-evidence` or false positives as `no-rewrite`; do not leave them pending.
- Run rebase maintenance before GitHub sync when candidates exist. If no rebase candidates are detected, GitHub sync may proceed after Human Check.
- Do not run `github-sync-apply` while unresolved `history_rewrite_candidates` remain.
- Do not mark rebase maintenance complete by attaching a new Issue/message to a useless commit. Completion requires absorb/split/drop/no-rewrite/keep-with-evidence disposition and reviewed evidence.
- Do not accept body-only repairs when the GitHub commit-list subject remains vague.
- Avoid weak semantic subjects such as "対応", "修正", "更新", file-name-only subjects, or repository-name-only scopes when source evidence supports a more precise scope.
- Prefer GitHub CLI/API; clone only after explicit human approval.
- Do not mutate GitHub from a free-form summary. Update `github-knowledge-analysis.json` first.
- Do not execute `gh issue edit`, `gh issue comment`, `gh pr edit`, `gh pr comment`, or `gh api` mutation commands without item-level human approval.
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
