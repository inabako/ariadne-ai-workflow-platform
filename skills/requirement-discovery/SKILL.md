---
name: requirement-discovery
description: Create a completed robotics requirement document from a human bullet-list draft in work/requirements/draft by inspecting it, asking blocking clarification questions, using optional RAG context, preparing a review draft, and saving the final document to work/requirements only after human OK. Use when the user selects /requirement-discovery or asks to create requirements from draft bullets.
---

# Requirement Discovery

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

## Slash Command

Use this skill when the user specifies:

```text
/requirement-discovery
```

This skill delegates the detailed workflow to:

```text
.github/prompts/requirement-discovery.prompt.md
```

## Input Location

Human-written bullet-list drafts belong under:

```text
work/requirements/draft/
```

Preferred input:

```text
work/requirements/draft/<draft-name>.txt
```

If no draft exists, ask the human to place a draft there. If multiple drafts exist and the target was not specified, ask which one to process.

## Workflow

1. Read the human bullet-list draft.
2. Inspect for missing, unclear, or contradictory information.
3. Run the Noise Reduction Phase before creating a requirement review draft.
4. If Noise Reduction readiness is `BLOCK`, return the Human Interview sheet to the human and do not continue.
5. Identify knowledge gaps where the team lacks enough technical context to ask good requirement questions.
6. If prior internal RAG is relevant, run `/rag-load` for prior findings, risks, or test gaps.
7. If external technical knowledge is needed, use `rag/external-web/knowledge-sources.md` as the source index.
8. If specialist knowledge is needed to ask good questions or frame constraints, run the relevant Specialist Agent as QA support.
9. Ask the human focused questions when clarification is required.
10. Review the human answers together with the original draft, Noise Reduction outputs, and any cited RAG context.
11. Create a requirement review draft under `work/requirements/draft/`.
12. Request human review.
13. After explicit human OK, save the completed requirement document under `work/requirements/`.

## Noise Reduction Phase Gate

Run this gate after first inspection and before requirement review draft creation.

Use:

```text
.github/prompts/noise-reduction-phase.prompt.md
templates/noise-reduction/
```

Save outputs under:

```text
work/requirements/draft/<draft-stem>-noise-reduction/
```

Required outputs:

```text
unknown-words-report.md
terminology-conflict-report.md
terminology-alias-report.md
document-conflict-report.md
ambiguous-language-report.md
ai-confusion-report.md
missing-definition-report.md
human-interview-sheet.md
project-glossary.md
readiness-report.md
```

Rules:

- Do not start design or implementation in this phase.
- Do not fill unknown terms, business rules, or document conflicts with guesses.
- Always create a Human Interview sheet and Project Glossary.
- If `readiness-report.md` is `BLOCK`, stop and ask the human. Do not create a completed requirement document.
- If readiness is `WARNING`, carry unresolved items into the requirement review draft `Open Questions`.

## External Knowledge Gap Flow

Use this flow when the draft introduces a domain that is not understood well enough to write or review requirements.

Examples:

- realtime gateway
- NAT traversal
- Go network programming
- robot safety behavior
- video transport
- observability

Flow:

```text
要件を聞く
  -> 知見不足の領域を特定する
  -> rag/external-web/knowledge-sources.md から関連sourceを選ぶ
  -> external-web-source-reviewer-agent で外部Webを精査する
  -> rag/external-web/<category>/ に compact claim / metadata を保存する
  -> external-web-rag-dispatcher-agent で必要な外部Web RAGを集約する
  -> 要件定義review draftへ、根拠pathと未確認事項を反映する
```

External-web RAG is supporting context only.

Do not use external-web RAG to replace human confirmation for Critical items.

## Specialist QA Support

Specialist Agent review may be used during requirement discovery to improve questions, constraints, risk framing, and test-readiness.

It must not finalize requirements by itself.

Save specialist QA outputs under:

```text
work/requirements/draft/<draft-stem>-specialist-review-<domain>.md
```

The output must record trusted external-web RAG, rejected or limited claims, unresolved human questions, and what should be carried into downstream design or testing.

Source index:

```text
rag/external-web/knowledge-sources.md
```

Category output examples:

```text
rag/external-web/network/
rag/external-web/robotics/
rag/external-web/ai-workflow/
rag/external-web/architecture/
```

## Critical Gate

Do not create a completed requirement document if any of these are missing or ambiguous:

- Repository
- Target Branch
- Safety requirements
- STOP / emergency stop behavior
- Communication loss behavior

When information is missing:

- Do not invent design.
- Do not choose an implementation approach.
- Ask the human.

## Important Review Items

Clarify these before completion where relevant:

- Network
- UI
- Telemetry
- Simulator

If an item is not relevant, record why in the review draft.

## Nice To Have

Capture these when present:

- Article candidates
- Future extensions
- Performance improvements

These do not block completion unless the human says they are required.

## Output Artifacts

Intermediate artifacts:

```text
work/requirements/draft/<draft-stem>-inspection.md
work/requirements/draft/<draft-stem>-questions.md
work/requirements/draft/<draft-stem>-requirements-review.md
work/requirements/draft/<draft-stem>-knowledge-gaps.md
work/requirements/draft/<draft-stem>-specialist-review-<domain>.md
```

External-web RAG artifacts, when used:

```text
rag/external-web/<category>/*.md
rag/external-web/retrieval/*-aggregate.md
```

Final artifact after human OK:

```text
work/requirements/<requirement-name>.md
```

## Downstream Gate

After this workflow completes, development workflows can intake the completed requirement document with:

```powershell
python runtime/intake/intake_requirements.py --workflow new-robotics-system-development
```

or:

```powershell
python runtime/intake/intake_requirements.py --workflow robotics-maintenance-development
```

Use the workflow that matches the completed requirement document.
