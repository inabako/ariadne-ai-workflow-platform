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
3. Run `/rag-load` before entering the development body. Derive parallel retrieval queries from the requirement, repository, branch, comparison report, and issue summary.
4. If architecture, runtime, network, deployment, safety, or test strategy depends on specialist knowledge, run the relevant Specialist Agent review before implementation.
5. Run `/new-robotics-system-development` only after relevant RAG context has been loaded and summarized.
6. Preserve artifacts under `work/<receipt-id>/`.
7. Record decisions, QA, risks, test evidence, RAG context references, specialist review references, and handoff context as JSON where schemas exist.

## Required Focus

- Intent / mission definition
- operational context
- hazard analysis and safety requirements
- system architecture
- runtime / network / deployment design
- test strategy before implementation
- integration, bench test, limited field test, release handover

Implementation must not start while STOP behavior, communication loss behavior, startup safe state, or shutdown safe state is unresolved.

## Specialist Review Gate

Use Specialist Agent review when a draft artifact depends on domain-specific knowledge such as Go realtime gateway, Python GUI/runtime, network protocols, GStreamer, platform deployment, observability, test fault injection, or robot safety control.

Save review outputs under:

```text
work/<receipt-id>/process-report/specialist-review-<domain>.md
```

The review must record trusted external-web RAG, rejected or limited claims, repository evidence, required tests, and unresolved human-check items. High or critical specialist findings must return the workflow to design or test strategy before implementation.
