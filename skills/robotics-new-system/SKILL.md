---
name: robotics-new-system
description: Start the Intent-Driven Robotics AI Workflow for creating a new robotics system, robot runtime, remote operation system, device integration, or architecture-level system launch. Use when the user selects /robotics-new-system or asks to begin a new robotics system development flow from a completed requirement document in work/requirements/.
---

# Robotics New System

## Slash Command

Use this skill when the user specifies:

```text
/robotics-new-system
```

This skill delegates the detailed workflow to:

```text
.github/prompts/new-robotics-system-development.prompt.md
```

## Intake Gate

Before starting the workflow, run or require the intake harness.

```powershell
python runtime/intake/intake_requirements.py --workflow new-robotics-system-development
```

The harness must reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not treat chat history as a substitute for an accepted requirement document.

## Workflow

1. Run `/pre-development-preparation`.
2. Confirm repository sync, requirement comparison, GitHub Issue, and `feature/issue-<issue-number>` branch.
3. Run `/new-robotics-system-development`.
4. Preserve artifacts under `work/<receipt-id>/`.
5. Record decisions, QA, risks, test evidence, and handoff context as JSON where schemas exist.

## Required Focus

- Intent / mission definition
- operational context
- hazard analysis and safety requirements
- system architecture
- runtime / network / deployment design
- test strategy before implementation
- integration, bench test, limited field test, release handover

Implementation must not start while STOP behavior, communication loss behavior, startup safe state, or shutdown safe state is unresolved.
