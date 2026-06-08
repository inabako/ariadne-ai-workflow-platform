---
name: requirement-discovery
description: Human bullet-list draft files under work/requirements/draft are inspected, clarified through questions, converted into a reviewed robotics requirement document, and saved to work/requirements after human OK.
argument-hint: "[draft-file]"
agent: agent
---

# Requirement Discovery Workflow

## Purpose

This workflow converts a human-written bullet-list draft into a completed robotics requirement document.

The workflow is for requirement discovery only. It must not start implementation, create a GitHub Issue, create a branch, or decide design details.

## Input Location

Human draft files belong here:

```text
work/requirements/draft/
```

Accepted draft extensions:

```text
.txt
.md
.markdown
```

The preferred input is one `.txt` bullet-list draft.

## Delegated Agent

Use:

```text
.github/agents/requirement-discovery-agent.prompt.md
```

## Flow

1. Human writes a bullet-list draft in `work/requirements/draft/`.
2. AI inspects the draft.
3. If the draft is unclear, AI sends questions back to the human.
4. Human answers.
5. AI inspects the draft and answers again.
6. AI creates a requirement review draft under `work/requirements/draft/`.
7. Human reviews the requirement review draft.
8. After explicit human OK, AI saves the completed requirement document under `work/requirements/`.

## Hard Stop Rules

Do not create a completed requirement document when any Critical item is missing or ambiguous:

- Repository
- Target Branch
- Safety requirements
- STOP / emergency stop behavior
- Communication loss behavior

When information is insufficient:

- Do not invent design.
- Do not choose implementation details.
- Ask the human.

## Priority Checklist

### Critical

- Repository
- Target Branch
- Safety requirements
- STOP
- Communication loss

### Important

- Network
- UI
- Telemetry
- Simulator

### Nice To Have

- Article candidates
- Future extensions
- Performance improvements

## Optional RAG Reference

RAG reference is allowed while drafting the requirement document.

Use `/rag-load` only to gather prior findings, known risks, or test gaps. RAG must not replace human confirmation for Critical items.

## Output Artifacts

Intermediate artifacts stay under:

```text
work/requirements/draft/
```

Recommended intermediate files:

```text
<draft-stem>-inspection.md
<draft-stem>-questions.md
<draft-stem>-requirements-review.md
```

The completed document is saved only after human OK:

```text
work/requirements/<requirement-name>.md
```

After completion, `work/requirements/` should contain exactly one completed requirement document for the next intake workflow.
