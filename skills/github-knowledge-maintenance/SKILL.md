---
name: github-knowledge-maintenance
description: Maintain a GitHub repository as a long-lived knowledge asset without rewriting Git history or changing source code. Use GitHub CLI/API first, discover Issue/PR/docs/CAR knowledge gaps, create human-reviewed repair proposals, optionally sync approved GitHub documentation assets, and prepare Knowledge DB/RAG candidates.
---

# GitHub Knowledge Maintenance Skill

## Default Language

Respond to the user in Japanese by default.

## Purpose

GitHub Repositoryを、未来のAI workflowとRAGが再利用できるKnowledge Baseとして継続保守します。

This workflow does not rewrite Git history, amend commits, force push, or change source code.

## Required Inputs

- repository URL, slug, or repository name
- scan mode: `repository`, `issue`, `pull-request`, `recent`, or `full`
- repair mode: `proposal` or `apply`
- whether RAG output is required

Example:

```text
/github-knowledge-maintenance localty-system-gui recent proposal rag
```

## Directory Model

Primary work folder:

```text
work/github-knowledge-<repository>-<mode>/
```

Primary artifacts:

```text
work/<work-id>/context/github-knowledge-analysis.json
work/<work-id>/process-report/github-knowledge-repair-plan-*.md
work/<work-id>/process-report/github-documentation-sync-plan-*.md
work/<work-id>/process-report/github-knowledge-rag-candidate-*.md
```

Approved RAG publication target:

```text
rag/github-knowledge/
```

## Workflow

Run from:

```powershell
cd C:\github\intent-driven-robotics-ai-workflow
```

### 1. Initialize Work Area

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py init `
  --repository "<target-repository>" `
  --scan-mode recent `
  --repair-mode proposal `
  --rag-output
```

If the work folder already exists, stop and ask whether to reuse it. After confirmation, rerun with `--reuse-existing`.

### 2. Create Analysis Scaffold

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py analysis-template `
  --work-id "<work-id>"
```

Generated:

```text
work/<work-id>/context/github-knowledge-analysis.json
```

Schema:

```text
.github/schemas/github-knowledge-analysis.schema.json
```

### 3. Repository Discovery

Use:

```text
.github/agents/repository-discovery-agent.prompt.md
```

Confirm repository identity, scan scope, and whether clone is forbidden or conditionally allowed.

### 4. GitHub Metadata Collection

Use:

```text
.github/agents/github-metadata-collector-agent.prompt.md
```

Prefer GitHub CLI/API:

```powershell
gh issue list --repo "<owner/repo>" --state all --limit 100
gh issue view "<number>" --repo "<owner/repo>" --comments
gh pr list --repo "<owner/repo>" --state all --limit 100
gh pr view "<number>" --repo "<owner/repo>" --comments
gh pr diff "<number>" --repo "<owner/repo>"
gh api repos/<owner>/<repo>/releases
```

Do not clone unless GitHub CLI/API evidence is insufficient and the human explicitly approves the clone reason.

### 5. Knowledge Asset Discovery

Use:

```text
.github/agents/knowledge-asset-discovery-agent.prompt.md
```

Extract:

- Intent
- Scope
- Design Decision
- Corrective Action
- Maintenance Knowledge
- Shared Artifact
- Future RAG Candidate

Record findings in `github-knowledge-analysis.json`.

### 6. Narrative Analysis

Use:

```text
.github/agents/narrative-analyzer-agent.prompt.md
```

Check the chain:

```text
Issue -> Pull Request -> Review -> Comment -> Documentation
```

Record narrative gaps and open questions in `github-knowledge-analysis.json`.

### 7. Repair Planning

Use:

```text
.github/agents/documentation-repair-agent.prompt.md
```

Create the human review plan:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py repair-plan `
  --work-id "<work-id>"
```

This is a proposal. It does not mutate GitHub.

### 8. Human Review Gate

Before any GitHub mutation, the human must confirm:

- repair reason
- repair target
- before / after summary
- no Git history rewrite
- exact GitHub CLI/API command

### 9. GitHub Documentation Sync

Use:

```text
.github/agents/github-documentation-sync-agent.prompt.md
```

Create the sync plan:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py github-sync-plan `
  --work-id "<work-id>"
```

Allowed operations after item-level approval:

```text
gh issue edit
gh issue comment
gh pr edit
gh pr comment
gh api
```

Do not execute commands marked `pending`.

### 10. Knowledge DB / RAG Candidate Generation

Use:

```text
.github/agents/knowledge-db-registrar-agent.prompt.md
```

Create a candidate note:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
  --work-id "<work-id>"
```

Publish to `rag/github-knowledge/` only after explicit approval:

```powershell
uv run python runtime/workflow/github_knowledge_maintenance.py rag-candidate `
  --work-id "<work-id>" `
  --publish-rag `
  --human-check approved
```

## Guardrails

- Do not rewrite Git history.
- Do not use `git rebase`, `git commit --amend`, force push, or any operation that changes commit SHA history.
- Do not change source code.
- Do not clone by default.
- Do not mutate GitHub without explicit human approval.
- Do not convert a free-form observation into a GitHub update; write it to `github-knowledge-analysis.json` first.
- Do not run RAG publication without explicit human approval.
- If evidence is missing, record an open question instead of guessing.

## Output Summary

Use:

```text
=== GitHub Knowledge Maintenance Summary ===

Repository
  <owner/repo>

Analysis JSON
  work/<work-id>/context/github-knowledge-analysis.json

Knowledge Assets
  <count>

Narrative Gaps
  Critical: 0
  High: 0
  Medium: 0
  Low: 0

Repair Proposals
  <count>

GitHub Sync
  Pending Approval: <count>

RAG Candidates
  <count>

Next Action
  Human Review / GitHub Sync Approval / RAG Approval
```
