---
name: requirement-discovery
description: Create a completed robotics requirement document from a human bullet-list draft in work/requirements/draft by inspecting it, asking blocking clarification questions, using optional RAG context, preparing a review draft, and saving the final document to work/requirements only after human OK. Use when the user selects /requirement-discovery or asks to create requirements from draft bullets.
---

# Requirement Discovery

## Default Language

Respond to the user in Japanese by default.

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
3. Ask the human focused questions when clarification is required.
4. Review the human answers together with the original draft.
5. Optionally run `/rag-load` for prior findings, risks, or test gaps.
6. Create a requirement review draft under `work/requirements/draft/`.
7. Request human review.
8. After explicit human OK, save the completed requirement document under `work/requirements/`.

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
