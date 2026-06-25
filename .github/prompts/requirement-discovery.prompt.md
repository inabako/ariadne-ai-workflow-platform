---
name: requirement-discovery
description: Human bullet-list draft files under work/requirements/draft are inspected, clarified through questions, converted into a reviewed robotics requirement document, and saved to work/requirements after human OK.
argument-hint: "[draft-file]"
agent: agent
---

# Requirement Discovery Workflow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

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
3. AI runs Noise Reduction Phase and creates terminology, conflict, ambiguity, Human Interview, glossary, and readiness artifacts.
4. If Noise Reduction readiness is `BLOCK`, AI stops and sends Human Interview questions back to the human.
5. AI identifies both clarification gaps and technical knowledge gaps.
6. If saved internal RAG is relevant, AI reads prior findings through `/rag-load`.
7. If external knowledge is needed, AI uses `rag/external-web/knowledge-sources.md` and the external-web agents to create or dispatch external-web RAG.
8. If specialist knowledge is needed to ask good questions or frame constraints, AI uses Specialist Agent QA support.
9. If the draft is unclear, AI sends questions back to the human.
10. Human answers.
11. AI inspects the draft, answers, Noise Reduction outputs, and cited RAG context again.
12. AI creates a requirement review draft under `work/requirements/draft/`.
13. Human reviews the requirement review draft.
14. After explicit human OK, AI saves the completed requirement document under `work/requirements/`.

## Noise Reduction Phase

Use this sub-flow before creating the requirement review draft:

```text
.github/prompts/noise-reduction-phase.prompt.md
```

Output directory:

```text
work/requirements/draft/<draft-stem>-noise-reduction/
```

Required artifacts:

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

- This phase reduces misunderstanding; it does not start design or implementation.
- Do not use general knowledge to override project-specific meanings.
- Do not guess missing business rules, state names, API meanings, or document conflicts.
- Always create a Human Interview sheet.
- Always create a Project Glossary.
- If Readiness is `BLOCK`, do not create the requirement review draft or completed requirement document.
- If Readiness is `WARNING`, carry unresolved items into `Open Questions`.

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

## External Web Knowledge Gap Reference

When the requirement draft contains a domain that is not understood well enough to ask good questions or write safe requirements, use external-web RAG.

Source index:

```text
rag/external-web/knowledge-sources.md
```

Agents:

```text
.github/agents/external-web-source-reviewer-agent.prompt.md
.github/agents/external-web-rag-dispatcher-agent.prompt.md
```

Flow:

```text
要件を聞く
  -> 知らない領域が出る
  -> knowledge-sources.md からsource候補を選ぶ
  -> 外部Webを精査し、claims / metadata / verification notesだけを保存する
  -> rag/external-web/<category>/ に蓄積する
  -> 必要な外部Web RAGをdispatch / aggregateする
  -> requirement review draftに、根拠pathと未確認事項を反映する
```

Rules:

- Do not store full external page bodies.
- Prefer official docs, standards, RFCs, and authoritative registries.
- Treat external-web RAG as supporting context only.
- If external-web RAG conflicts with internal evidence or human answers, ask the human.
- Critical items still require human confirmation.

## Specialist QA Support

Specialist Agent review may be used to improve requirement questions, constraints, risk framing, and test-readiness.

It must not finalize requirements by itself.

Save specialist QA outputs under:

```text
work/requirements/draft/<draft-stem>-specialist-review-<domain>.md
```

The output must record trusted external-web RAG, rejected or limited claims, unresolved human questions, and what should be carried into downstream design or testing.

## Output Artifacts

Intermediate artifacts stay under:

```text
work/requirements/draft/
```

Recommended intermediate files:

```text
<draft-stem>-inspection.md
<draft-stem>-knowledge-gaps.md
<draft-stem>-questions.md
<draft-stem>-requirements-review.md
<draft-stem>-specialist-review-<domain>.md
```

The completed document is saved only after human OK:

```text
work/requirements/<requirement-name>.md
```

After completion, `work/requirements/` should contain exactly one completed requirement document for the next intake workflow.
