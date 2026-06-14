---
name: github-knowledge-maintenance
description: Maintain a GitHub repository as a reusable knowledge asset without rewriting Git history or changing source code.
argument-hint: "<target-repository> <scan-mode> <repair-mode> [rag]"
agent: agent
---

# GitHub Repository Knowledge Maintenance Workflow

## Purpose

This workflow maintains GitHub Repository knowledge assets for future AI workflows and RAG.

It treats Git history as historical fact and improves Issue, Pull Request, comment, Documentation, Corrective Action Report, Knowledge DB, and RAG candidate quality without rewriting commits.

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
uv run python runtime/workflow/github_knowledge_maintenance.py init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

Create analysis scaffold:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py analysis-template `
  --work-id "<work-id>"
```

Create repair plan:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py repair-plan `
  --work-id "<work-id>"
```

Create GitHub sync plan:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py github-sync-plan `
  --work-id "<work-id>"
```

Create RAG candidate:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
  --work-id "<work-id>"
```

Publish RAG candidate only after approval:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
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
5. Create repair proposals.
6. Stop for human review.
7. Generate an approval-gated GitHub documentation sync plan.
8. Execute only approved GitHub CLI/API updates.
9. Generate Knowledge DB and RAG candidates.
10. Publish RAG candidates only after human approval.

## Guardrails

- Do not rewrite Git history.
- Do not alter commit SHA history.
- Do not change source code.
- Prefer GitHub CLI/API; clone only after explicit human approval.
- Do not mutate GitHub from a free-form summary. Update `github-knowledge-analysis.json` first.
- Do not execute `gh issue edit`, `gh issue comment`, `gh pr edit`, `gh pr comment`, or `gh api` mutation commands without item-level human approval.
- Do not run RAG publication without explicit human approval.

## Completion

The workflow is complete when:

- Repository metadata was collected or the missing collection was recorded.
- Knowledge assets were extracted.
- Narrative gaps were detected or explicitly recorded as none.
- Repair proposals were generated.
- Human review was completed.
- Only approved GitHub documentation assets were updated.
- Knowledge DB candidates were generated.
- RAG candidates were generated when requested.
