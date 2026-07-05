---
name: robotics-new-system-iac
description: Run the integrated new robotics system plus realtime IaC workflow. Use when the user selects /robotics-new-system-iac or asks to create a new robotics system and then generate validated Shared Artifacts for the realtime IaC workflow.
---

# Robotics New System + IaC

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

## Slash Command

Use this skill when the user specifies:

```text
/robotics-new-system-iac
```

This skill delegates the detailed workflow to:

```text
.github/prompts/robotics-new-system-iac.prompt.md
```

## Purpose

Create a new robotics system and hand it to the realtime IaC workflow through validated Shared Artifacts.

The integrated flow is:

```text
New System Workflow
  -> Shared Artifacts generation
  -> Shared Artifact Validator
  -> Realtime IaC Workflow
```

## Intake Gate

Before starting, run or require the intake harness.

```powershell
uv run python runtime/intake/intake_requirements.py --workflow robotics-new-system-iac
```

The harness must reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not treat chat history as a substitute for an accepted requirement document.

## Required Shared Artifacts

The new system workflow must produce or explicitly reference these artifacts before IaC starts:

```text
work/<receipt-id>/design-document/shared-artifacts-index.md
work/<receipt-id>/design-document/requirements.md
work/<receipt-id>/design-document/communication-specification.md
work/<receipt-id>/design-document/port-definition.md
work/<receipt-id>/design-document/network-boundary-definition.md
work/<receipt-id>/design-document/architecture-decision-record.md
work/<receipt-id>/process-report/shared-artifact-validation.md
```

The IaC workflow must not infer missing values. If any required Shared Artifact is missing, contradictory, or not traceable to requirements, stop and write:

```text
work/<receipt-id>/design-document/open-questions.md
```

## Workflow

1. Run `/pre-development-preparation`.
2. Run the new system workflow phases through architecture, runtime, network, deployment, and test strategy.
3. Generate the Shared Artifacts:
   - requirements
   - communication specification
   - port definition
   - network boundary definition
   - architecture decision records
4. Run Shared Artifact Validator.
5. If validation is `pass`, run `/realtime-iac` using the Shared Artifacts as the source of truth. The `/realtime-iac` Boilerplate Template Selection Gate must consider `templates/boilerplates/realtime-gateway-infra-template/` when realtime gateway infrastructure is in scope.
6. If validation is `conditional-pass`, only proceed to IaC for non-blocked areas and record residual risks.
7. If validation is `fail`, return to the new system design phases. Do not start IaC.
8. Preserve artifacts under `work/<receipt-id>/`.
9. Record decisions, QA, findings, validation results, RAG context references, specialist review references, and handoff context as JSON where schemas exist.

## Shared Artifact Validator

The validator checks:

- requirement coverage
- communication flow completeness
- port definition completeness
- network boundary completeness
- ADR coverage for major architecture / infrastructure decisions
- safety-critical behavior references
- software / infrastructure responsibility separation
- repository mode and branch readiness
- IaC readiness

Validator outputs:

```text
work/<receipt-id>/process-report/shared-artifact-validation.md
work/<receipt-id>/context/shared-artifact-validation.json
```

Judgment:

| Judgment | Meaning | Next Step |
| --- | --- | --- |
| pass | IaC can proceed. | Start `/realtime-iac`. |
| conditional-pass | IaC can proceed only for named non-blocked areas. | Start `/realtime-iac` with residual risks recorded. |
| fail | Missing or contradictory Shared Artifacts would cause unsafe IaC generation. | Return to new system workflow. |

## Realtime IaC Handoff

Before starting `/realtime-iac`, create:

```text
work/<receipt-id>/context/realtime-iac-handoff.json
work/<receipt-id>/context/execution-plan.json
```

The handoff must include:

- source artifact paths
- validator judgment
- blocked areas
- residual risks
- IaC repository mode
- target repository
- target branch or initial branch
- required human approvals
- recommended `/realtime-iac` next command
- boilerplate template selection expectation for realtime gateway infrastructure

Create and register the handoff context and execution plan with the runtime helper:

```powershell
uv run python runtime/workflow/iac_handoff_context.py `
  --work-id <receipt-id> `
  --validator-judgment <pass|conditional-pass|fail> `
  --source-artifact work/<receipt-id>/design-document/shared-artifacts-index.md
```

The helper must register both `realtime-iac-handoff` and `execution-plan` in `work/<receipt-id>/context/context-manifest.json`.
Before actually starting `/realtime-iac`, verify the Docker environment context:

```powershell
aiwfctl env select docker --work-id <receipt-id>
uv run python runtime/workflow/context_first.py `
  --work-dir work/<receipt-id> `
  require-environment --environment docker
```

## Stop Rules

Stop before IaC when any of these are unresolved:

- requirements are incomplete
- communication specification is missing or contradictory
- port definition is missing or contradictory
- network boundary definition is missing or contradictory
- ADR is missing for a major architecture / infrastructure decision
- safety behavior is not traceable
- repository mode is unclear
- software inventory is missing when IaC must install, package, start, supervise, proxy, monitor, or document software
- validator judgment is `fail`

## Templates

Use these templates for Shared Artifacts:

```text
templates/shared-artifacts/shared-artifacts-index-template.md
templates/shared-artifacts/port-definition-template.md
templates/shared-artifacts/network-boundary-definition-template.md
templates/shared-artifacts/architecture-decision-record-template.md
templates/iac/communication-specification-template.md
templates/iac/software-inventory-template.md
```

Use this boilerplate template when realtime gateway IaC / infrastructure is in scope and the selection gate approves it:

```text
templates/boilerplates/realtime-gateway-infra-template/
```

## Source Workflows

This integrated skill composes:

```text
skills/robotics-new-system/SKILL.md
skills/realtime-iac/SKILL.md
```
