---
name: corrective-action-report
description: Analyze the current state of a user-specified repository and branch, identify improvement points, risks, missing documentation, test gaps, architecture concerns, and workflow opportunities, then write a corrective action report for RAG accumulation. Use when the user selects /corrective-action-report or asks for a current improvement report, corrective action report, repository health review, or cross-project improvement findings.
---

# Corrective Action Report Skill

## Slash Command

Use this skill when the user specifies:

```text
/corrective-action-report
```

## Required Inputs

Before analyzing, ensure both inputs are known:

- target repository: local path, GitHub URL, or owner/repo
- target branch: branch name to inspect

If either value is missing, ask the user for it before proceeding.

Do not infer the branch from the current shell state unless the user explicitly approves using the current branch.

## Output Location

Write the report to:

```text
C:\github\intent-driven-robotics-ai-workflow\rag\corrective-action-report
```

Recommended filename:

```text
yyyyMMdd_HHmmss_<repository-name>_<branch-name>_corrective-action-report.md
```

Sanitize `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`, and whitespace in filename parts.

## Analysis Scope

Review the repository from these angles:

- architecture and responsibility boundaries
- safety, security, and operational risk
- runtime, deployment, observability, and rollback readiness
- test strategy, test gaps, and missing evidence
- documentation gaps and unclear intent
- code health, maintainability, duplication, and complexity
- GitHub workflow readiness: issue, branch, commit, CI, review flow
- RAG candidates: knowledge worth preserving for future Agents

For robotics repositories, prioritize STOP behavior, communication loss behavior, startup / shutdown safe state, operator responsibility, field operation assumptions, telemetry, and incident capture.

## Workflow

1. Ask for target repository and target branch if missing.
2. Resolve the repository locally or note that it must be cloned/fetched.
3. Confirm the inspected branch and commit hash when possible.
4. Inspect repository structure, docs, tests, runtime scripts, CI, and major source boundaries.
5. Identify findings with severity and rationale.
6. Separate immediate corrective actions from later improvements.
7. Write the report to the output location.
8. Tell the user the report path and summarize the highest-value findings.

## Report Structure

Use this structure:

```markdown
---
type: corrective-action-report
repository: <target repository>
branch: <target branch>
commit: <commit hash or unknown>
status: draft
created_at: <ISO-8601>
tags:
  - corrective-action
  - repository-review
---

# Corrective Action Report: <repository> / <branch>

## Executive Summary

## Inspection Scope

## Repository State

## Findings

| ID | Severity | Area | Finding | Why It Matters | Recommended Action |
| --- | --- | --- | --- | --- | --- |

## Immediate Corrective Actions

## Medium-Term Improvements

## RAG Capture Candidates

## Open Questions

## Evidence
```

Severity values:

- critical
- high
- medium
- low
- info

## Guardrails

Keep the first pass read-only unless the user explicitly asks for fixes.

Do not create GitHub Issues, branches, commits, or code edits from this skill unless the user explicitly escalates from report creation to implementation.

If the repository or branch cannot be accessed, write no report unless there is enough evidence to produce a useful blocked report. Prefer asking the user for the missing path, clone, credential, or branch.
