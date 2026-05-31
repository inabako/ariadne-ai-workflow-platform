---
name: robotics-feature-maintenance
description: Start the Intent-Driven Robotics AI Workflow for adding a new feature to an existing robotics system or performing maintenance development such as bug fix, hardware replacement, network change, deployment change, field issue response, or operational improvement. Use when the user selects /robotics-feature-maintenance or asks to begin feature or maintenance work from a completed requirement document in work/requirements/.
---

# Robotics Feature Maintenance

## Slash Command

Use this skill when the user specifies:

```text
/robotics-feature-maintenance
```

This skill delegates the detailed workflow to:

```text
.github/prompts/robotics-maintenance-development.prompt.md
```

## Intake Gate

Before starting the workflow, run or require the intake harness.

```powershell
python runtime/intake/intake_requirements.py --workflow robotics-maintenance-development
```

The harness must reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not treat chat history as a substitute for an accepted requirement document.

## Workflow

1. Run `/pre-development-preparation`.
2. Confirm repository sync, requirement comparison, GitHub Issue, and `feature/issue-<issue-number>` branch.
3. Run `/robotics-maintenance-development`.
4. Preserve artifacts under `work/<receipt-id>/`.
5. Record decisions, QA, risks, test evidence, and handoff context as JSON where schemas exist.

## Required Focus

- change intent
- current state capture
- impact analysis
- risk classification
- change design and rollback plan
- test plan based on risk
- verification, deployment plan, post-change observation

Safety behavior, network authority, runtime process ownership, and operator workflow changes must be reviewed before implementation.
