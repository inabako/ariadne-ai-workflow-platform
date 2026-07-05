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
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

Create analysis scaffold:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py analysis-template `
  --work-id "<work-id>"
```

Create repair plan:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py repair-plan `
  --work-id "<work-id>"
```

Create GitHub sync plan:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py github-sync-plan `
  --work-id "<work-id>"
```

Create RAG candidate:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
  --work-id "<work-id>"
```

Publish RAG candidate only after approval:

```powershell
uv run --project runtime python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
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
6. Stop for human review.
7. Generate an approval-gated GitHub documentation sync plan.
8. Execute only approved GitHub CLI/API updates.
9. Execute existing commit message/body rewrite only when the high-risk Git rewrite review plan is explicitly approved.
10. Generate Knowledge DB and RAG candidates.
11. Publish RAG candidates only after human approval.

## Guardrails

- Do not erase Git history or hide historical evidence.
- Do not change commit source, source code, README content, or configuration content in the target repository.
- Existing commit message/body rewrite requires explicit item-level human approval, before/after SHA mapping, rollback plan, and reviewed force-push command when needed.
- Do not accept body-only repairs when the GitHub commit-list subject remains vague.
- Avoid weak semantic subjects such as "対応", "修正", "更新", file-name-only subjects, or repository-name-only scopes when source evidence supports a more precise scope.
- Prefer GitHub CLI/API; clone only after explicit human approval.
- Do not mutate GitHub from a free-form summary. Update `github-knowledge-analysis.json` first.
- Do not execute `gh issue edit`, `gh issue comment`, `gh pr edit`, `gh pr comment`, or `gh api` mutation commands without item-level human approval.
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
