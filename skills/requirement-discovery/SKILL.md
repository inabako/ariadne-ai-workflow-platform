---
name: requirement-discovery
description: Create a completed target-system requirement document from a human bullet-list draft in work/requirements/draft by inspecting it, asking blocking clarification questions, using optional RAG context, preparing a review draft, and saving the final document to work/requirements only after human OK. Use when the user selects /requirement-discovery or asks to create requirements from draft bullets.
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

## Optional SDK Program Input

SDK program files may be placed under the requirement input folder:

```text
work/requirements/sdk/
```

If this directory does not exist, is empty, or contains no analyzable SDK program files, skip SDK pre-analysis and continue requirement discovery.

When SDK input exists, run:

```powershell
aiwfctl sdk analyze --work-id <work-id>
aiwfctl sdk discover --work-id <work-id>
```

Main outputs:

```text
work/<work-id>/reports/sdk-analysis-report.md
work/<work-id>/context/sdk-analysis-context.json
work/<work-id>/context/sdk-files.json
work/<work-id>/requirements/sdk-integration-requirements.md
work/<work-id>/reports/sdk-external-discovery-report.md
work/<work-id>/context/sdk-external-discovery.json
work/<work-id>/requirements/sdk-external-requirements.md
```

The SDK analysis context is optional supporting context. It must not replace human confirmation for license, adoption, vendor lock-in, auth management, production network usage, cost, deprecated / unsupported SDK status, or unclear security behavior.

The SDK external discovery context is a search plan and evidence handoff. It identifies official docs, package registry, release notes, security advisory, and deprecation checks to perform. Do not store full external page bodies.

For AWS / GCP SDKs, the analysis also records cloud provider, language, package manager, SDK generation, candidate services, credential model, region / project requirements, local test options, and cloud-specific Human Checks.
For Stripe SDKs, the analysis records payment vendor, SDK language, package manager, candidate payment services, API key / webhook signing secret handling, test mode, idempotency, PCI boundary, refund / chargeback / tax concerns, and payment-specific Human Checks.

## Workflow

1. Read the human bullet-list draft.
2. Inspect for missing, unclear, or contradictory information.
3. Run the Noise Reduction Phase before creating a requirement review draft.
4. If Noise Reduction readiness is `BLOCK`, return the Human Interview sheet to the human and do not continue.
5. If a `work/requirements/sdk/` input exists, run SDK Pre-Analysis and SDK External Discovery, then register `sdk-analysis` and `sdk-external-discovery` into the Context First manifest.
6. Identify knowledge gaps where the team lacks enough technical context to ask good requirement questions.
7. If prior internal RAG is relevant, run `/rag-load` for prior findings, risks, or test gaps.
8. If external technical knowledge is needed, use `rag/external-web/knowledge-sources.md` as the source index.
9. If specialist knowledge is needed to ask good questions or frame constraints, run the relevant Specialist Agent as QA support.
10. Ask the human focused questions when clarification is required.
11. Review the human answers together with the original draft, Noise Reduction outputs, SDK analysis context, and any cited RAG context.
12. Create a requirement review draft under `work/requirements/draft/`.
13. Request human review.
14. After explicit human OK, save the completed requirement document under `work/requirements/`.

## Noise Reduction Phase Gate

Run this gate after first inspection and before requirement review draft creation.

Use:

```text
.github/prompts/noise-reduction-phase.prompt.md
templates/workflows/noise-reduction/
```

Runtime helper:

```powershell
python runtime/workflow/noise_reduction.py run --draft "work/requirements/draft/<draft-name>.txt"
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
- physical safety behavior
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
rag/external-web/system-design/
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
python runtime/intake/intake_requirements.py --workflow ariadne-new-system-development
```

or:

```powershell
python runtime/intake/intake_requirements.py --workflow ariadne-feature-maintenance-development
```

Use the workflow that matches the completed requirement document.


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
