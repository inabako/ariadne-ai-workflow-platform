---
name: robotics-new-system-iac
description: Run the integrated new robotics system plus realtime IaC workflow. Use when the user selects /robotics-new-system-iac or asks to create a new robotics system and then generate validated Shared Artifacts for the realtime IaC workflow.
---

# Robotics New System + IaC

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
5. If validation is `pass`, run `/realtime-iac` using the Shared Artifacts as the source of truth.
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

## Source Workflows

This integrated skill composes:

```text
skills/robotics-new-system/SKILL.md
skills/realtime-iac/SKILL.md
```
