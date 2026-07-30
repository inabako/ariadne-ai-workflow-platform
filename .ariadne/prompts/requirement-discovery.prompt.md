---
name: requirement-discovery
description: Human bullet-list draft files under work/requirements/draft are inspected, clarified through questions, converted into a reviewed target-system requirement document, and saved to work/requirements after human OK.
argument-hint: "[draft-file]"
agent: agent
---

# Requirement Discovery Workflow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.ariadne/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

This workflow converts a human-written bullet-list draft into a completed target-system requirement document.

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

## Optional SDK Program Input

SDK program files are optional input for this requirement discovery run.

Place them here:

```text
work/requirements/sdk/
```

If the directory is missing, empty, contains excluded-only files, or is intentionally skipped, do not block the workflow. Record that SDK pre-analysis was skipped and continue.

If analyzable SDK input exists, run SDK pre-analysis before creating the requirement review draft:

```powershell
aiwfctl sdk analyze --work-id <work-id>
aiwfctl sdk discover --work-id <work-id>
```

Outputs:

```text
work/<work-id>/reports/sdk-analysis-report.md
work/<work-id>/context/sdk-analysis-context.json
work/<work-id>/context/sdk-files.json
work/<work-id>/requirements/sdk-integration-requirements.md
work/<work-id>/reports/sdk-external-discovery-report.md
work/<work-id>/context/sdk-external-discovery.json
work/<work-id>/requirements/sdk-external-requirements.md
```

Carry `sdk-integration-requirements.md`, `sdk-analysis-context.json`, `sdk-external-requirements.md`, and `sdk-external-discovery.json` into the requirement review draft as supporting context.

Do not finalize SDK adoption, license acceptability, vendor lock-in, credential management, production network use, cost, deprecated / unsupported status, or unclear security behavior without human confirmation.

External discovery is a search plan and evidence handoff. Prefer official docs, package registry, official repository, release notes, changelog, migration guide, security advisory, and deprecation notice. Do not store full external page bodies.

For AWS / GCP SDKs, carry cloud provider, language, package manager, SDK generation, candidate services, credential model, region / project requirements, local test options, and cloud-specific Human Checks into the requirement review draft.

For Stripe SDKs, carry payment vendor, payment services, API key / webhook signing secret handling, test mode, idempotency, PCI boundary, refund / chargeback / tax / currency concerns, and payment-specific Human Checks into the requirement review draft.

## Delegated Agent

Use:

```text
.ariadne/agents/requirement-discovery-agent.prompt.md
```

## Flow

1. Human writes a bullet-list draft in `work/requirements/draft/`.
2. AI inspects the draft.
3. AI runs Noise Reduction Phase and creates terminology, conflict, ambiguity, Human Interview, glossary, and readiness artifacts.
4. If Noise Reduction readiness is `BLOCK`, AI stops and sends Human Interview questions back to the human.
5. AI checks whether `work/requirements/sdk/` exists and has analyzable files.
6. If SDK input exists, AI runs `aiwfctl sdk analyze --work-id <work-id>` and `aiwfctl sdk discover --work-id <work-id>`, then registers `sdk-analysis` and `sdk-external-discovery` contexts. If not, AI skips without blocking.
7. AI identifies both clarification gaps and technical knowledge gaps.
8. If saved internal RAG is relevant, AI reads prior findings through `/rag-load`.
9. If external knowledge is needed, AI uses `work/db/ariadne-knowledge-platform/rag/external-web/knowledge-sources.md` and the external-web agents to create or dispatch external-web RAG.
10. If specialist knowledge is needed to ask good questions or frame constraints, AI uses Specialist Agent QA support.
11. If the draft is unclear, AI sends questions back to the human.
12. Human answers.
13. AI inspects the draft, answers, Noise Reduction outputs, SDK analysis context, and cited RAG context again.
14. AI creates a requirement review draft under `work/requirements/draft/`.
15. Human reviews the requirement review draft.
16. After explicit human OK, AI saves the completed requirement document under `work/requirements/`.

## Noise Reduction Phase

Use this sub-flow before creating the requirement review draft:

```text
.ariadne/prompts/noise-reduction-phase.prompt.md
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
work/db/ariadne-knowledge-platform/rag/external-web/knowledge-sources.md
```

Agents:

```text
.ariadne/agents/external-web-source-reviewer-agent.prompt.md
.ariadne/agents/external-web-rag-dispatcher-agent.prompt.md
```

Flow:

```text
要件を聞く
  -> 知らない領域が出る
  -> knowledge-sources.md からsource候補を選ぶ
  -> 外部Webを精査し、claims / metadata / verification notesだけを保存する
  -> work/db/ariadne-knowledge-platform/rag/external-web/<category>/ に蓄積する
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
