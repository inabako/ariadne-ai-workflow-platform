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
3. Run `/rag-load` before entering the development body. Derive parallel retrieval queries from the requirement, repository, branch, comparison report, and issue summary.
4. If impact analysis, change design, or test planning depends on specialist knowledge, run the relevant Specialist Agent review before implementation.
5. Run `/robotics-maintenance-development` only after relevant RAG context has been loaded and summarized.
6. Preserve artifacts under `work/<receipt-id>/`.
7. Record decisions, QA, risks, test evidence, RAG context references, specialist review references, and handoff context as JSON where schemas exist.

## Required Focus

- change intent
- current state capture
- impact analysis
- risk classification
- change design and rollback plan
- test plan based on risk
- PyQt QTest source plan when the changed system includes a PyQt / Qt GUI
- verification, deployment plan, post-change observation

Safety behavior, network authority, runtime process ownership, and operator workflow changes must be reviewed before implementation.

## Specialist Review Gate

Use Specialist Agent review when a change affects STOP behavior, communication loss, robot command authority, network routing/protocol behavior, runtime lifecycle, video pipeline, deployment platform, observability, or evidence strategy.

Save review outputs under:

```text
work/<receipt-id>/process-report/specialist-review-<domain>.md
```

The review must record trusted external-web RAG, rejected or limited claims, current repository evidence, required tests, and unresolved human-check items. High or critical specialist findings must return the workflow to impact analysis, change design, or test planning before implementation.

## PyQt QTest Integration Gate

When the changed system includes a PyQt / Qt GUI, convert automatable GUI integration test cases from the approved test specification into QTest-based test sources.

Keep physical robot behavior, real camera quality, physical STOP, router / VPN, and field network checks as bench / human-check evidence.
