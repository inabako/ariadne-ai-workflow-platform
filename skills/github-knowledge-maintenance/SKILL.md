---
name: github-knowledge-maintenance
description: Maintain a GitHub repository as a long-lived knowledge asset without erasing Git history. Use GitHub CLI/API first, discover Issue/PR/docs/CAR/commit-source/commit-message/semantic-subject knowledge gaps, create human-reviewed repair proposals, optionally sync approved GitHub documentation assets, and prepare Knowledge DB/RAG candidates.
---

# GitHub Knowledge Maintenance Skill

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

## Purpose

GitHub Repositoryを、未来のAI workflowとRAGが再利用できるKnowledge Baseとして継続保守します。

This workflow does not erase Git history or make historical evidence disappear. If commit semantic subjects, commit bodies, PR titles, PR bodies, or source documentation are missing, vague, or misleading, record the gap, prepare a reviewed repair proposal, and route the learned content to RAG. Existing commit rewriting is a separate high-risk action and requires explicit item-level approval plus before/after SHA mapping.

Semantic commit quality is part of the repair target. The commit subject shown in the GitHub commit list must carry useful meaning by itself, using `type(scope): responsibility/result`, and the body must preserve intent, scope, decision, impact, and reusable maintenance knowledge.

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

Reference guideline:

```text
docs/reference/semantic-commit-message-guideline.md
```

Approved RAG publication target:

```text
rag/github-knowledge/
```

This target stores approved source Markdown reports named:

```text
YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

After publishing source Markdown, regenerate the RAG artifacts in this order:

1. normalize approved source Markdown into UUID JSON
2. chunk normalized JSON
3. rebuild indexes
4. rebuild embeddings

Normalize:

```powershell
uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/github-knowledge `
  --output-dir rag/normalized `
  --document-type github-repository-knowledge
```

Chunk:

```powershell
uv run python runtime/rag/chunk_documents.py `
  --input-dir rag/normalized `
  --output-dir rag/chunks
```

Index:

```powershell
uv run python runtime/rag/build_index.py `
  --normalized-dir rag/normalized `
  --chunks-dir rag/chunks `
  --output-dir rag/indexes
```

Embedding:

```powershell
uv run python runtime/rag/embed_chunks.py `
  --chunks-index rag/indexes/chunks.jsonl `
  --output rag/embeddings/chunks-embeddings.jsonl
```

Final durable landing:

```text
rag/normalized/<uuid>.json
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

Before metadata collection, check whether GitHub CLI is available:

```powershell
gh --version
```

If `gh` is not available, record the missing tool in the analysis JSON, ask for human approval, then install GitHub CLI with:

```powershell
winget install --id GitHub.cli
```

After installation, open a new terminal or refresh PATH, then verify:

```powershell
gh --version
gh auth status
```

If the repository `.env` contains `GITHUB_TOKEN`, note that the token is available to repository runtime helpers via `load_env()`, even when `$env:GITHUB_TOKEN` is not set in the current PowerShell process. Do not print token values.

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
- Commit Source / Message Gap
- Semantic Commit Subject Gap
- Pull Request Title Gap

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
- for PR title repair, the current title, proposed title, and exact `gh pr edit --title` command
- whether the action is additive repair or approved commit-message/source correction
- whether the proposed semantic subject is meaningful in GitHub commit list view
- for any commit rewrite, the before/after SHA mapping and rollback plan
- exact Git / GitHub CLI/API command

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

Then normalize the approved published report to UUID JSON with `runtime/rag/normalize_documents.py`, and rebuild chunks, indexes, and embeddings.

## Guardrails

- Do not erase Git history or hide historical evidence.
- Do not treat "no history erasure" as permission to leave weak commit messages or source explanations uncorrected.
- Do not leave semantic commit subjects vague. Avoid broad scopes and weak wording such as "対応", "修正", "更新", or repository-name-only scopes when a more precise responsibility scope exists.
- Do not leave PR titles vague. A merged PR title must be useful in the GitHub PR list without opening the body.
- For commit message repair, propose both a GitHub-list-readable subject and a body that records intent, scope, decision, impact, and reusable maintenance knowledge.
- Prefer additive repair first: PR body, follow-up documentation commit, README/docs supplement, CAR supplement, or RAG candidate.
- Existing commit-message/source correction with `git rebase`, `git commit --amend`, or force push is allowed only when the human explicitly approves that high-risk path and a before/after SHA mapping is recorded.
- Do not change source code.
- Do not clone by default.
- Do not mutate GitHub without explicit human approval.
- Do not install missing tools silently. For missing `gh`, record the install command `winget install --id GitHub.cli`, get human approval, then verify with `gh --version`.
- Do not convert a free-form observation into a GitHub update; write it to `github-knowledge-analysis.json` first.
- Do not run RAG publication without explicit human approval.
- Route the knowledge learned from commit-source/message repairs into RAG candidates after human review.
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
