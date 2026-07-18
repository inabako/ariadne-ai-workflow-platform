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

## Output Language

Write the report in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

If the user explicitly requests another language, use the requested language.

## Output Location

Write the report to:

```text
C:\github\ariadne-ai-workflow-platform\rag\corrective-action-report
```

Recommended filename:

```text
YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md
```

Sanitize `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`, and whitespace in filename parts.
Use a short random token in the filename to avoid collisions and do not include branch or language suffixes in the filename. Keep branch and language in front matter / tags instead.

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

For target repositories, prioritize STOP behavior, communication loss behavior, startup / shutdown safe state, operator responsibility, field operation assumptions, telemetry, and incident capture.

## Workflow

1. Ask for target repository and target branch if missing.
2. Resolve the repository locally or note that it must be cloned/fetched.
3. Confirm the inspected branch and commit hash when possible.
4. Inspect repository structure, docs, tests, runtime scripts, CI, and major source boundaries.
5. Load internal RAG when prior project findings, risks, or test gaps may help.
6. If an unfamiliar technical area affects finding quality, dispatch external-web RAG as supporting reference.
7. If findings depend on domain-specific interpretation, run the relevant Specialist Agent review before finalizing the report.
8. Identify findings with severity, rationale, and repository evidence.
9. Separate immediate corrective actions from later improvements.
10. Write the report to the output location.
11. Register the report as Context First artifact with `runtime/workflow/corrective_action_report.py register`.
12. Tell the user the report path and summarize the highest-value findings.

Context registration example:

```powershell
python runtime/workflow/corrective_action_report.py register `
  --repository "<target repository>" `
  --target-branch "<target branch>" `
  --report-path "rag/corrective-action-report/<report>.md"
```

## External Web RAG Support

Use external-web RAG only to strengthen review viewpoints, not to prove findings by itself.

Good uses:

- expand risk viewpoints
- identify standards / official-docs comparison points
- improve test-gap analysis
- clarify implementation or runtime constraints
- propose verification checks

Required source index:

```text
rag/external-web/knowledge-sources.md
```

Helpful retrieval example:

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "<repository review topic>" `
  --source-type external-web `
  --category "<category>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

If saved external-web RAG is not enough, use:

```text
.github/agents/external-web-source-reviewer-agent.prompt.md
.github/agents/external-web-rag-dispatcher-agent.prompt.md
```

External-web RAG must be recorded as `supporting_reference`, not as primary evidence.

Every final finding must still be tied to current repository evidence:

- file / line / component
- behavior
- docs gap
- log / runtime evidence
- test gap
- reproducible inspection result

## Specialist Review Support

Use Specialist Agent review when repository findings depend on domain depth such as Python/Go runtime behavior, realtime networking, GStreamer, platform deployment, observability, test fault injection, remote access security, or safety control behavior.

Save review outputs under:

```text
work/<target-branch>/process-report/specialist-review-<domain>.md
```

The review must record:

- internal RAG used
- external-web RAG used
- external claims accepted
- external claims rejected or limited
- repository evidence connected to the review
- verification required
- unresolved QA

Specialist review output is a supporting reference. It does not replace current repository evidence for a final finding.

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

## Supporting References

| Finding ID | Reference Type | Source | How It Was Used | Verification Required |
| --- | --- | --- | --- | --- |

## Specialist Review References

| Domain | Review Path | Trusted External Knowledge | Repository Evidence | Result |
| --- | --- | --- | --- | --- |

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

## Workflow Feedback Output

During every AI workflow run, capture actionable workflow friction or improvement candidates in `work/feedback/`.
Create or update a Feedback report when you observe ambiguity, repeated checks, missing context/docs, runtime observation gaps, noisy handoffs, encoding issues, or a reusable workflow improvement.

Use the existing helper when creating a new report:

```powershell
uv run --project runtime python runtime/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

Keep the initial `Review Status` as `Proposed`. Do not run `/self-improvement` automatically inside this workflow; `/self-improvement` is executed later when feedback has accumulated and a human is ready to review Accepted / Rejected / Deferred decisions.

## Guardrails

Keep the first pass read-only unless the user explicitly asks for fixes.

Do not create GitHub Issues, branches, commits, or code edits from this skill unless the user explicitly escalates from report creation to implementation.

If the repository or branch cannot be accessed, write no report unless there is enough evidence to produce a useful blocked report. Prefer asking the user for the missing path, clone, credential, or branch.

Do not assert a corrective finding from external-web RAG alone. External-web references can support a finding, but the report must include current repository evidence for the finding.
