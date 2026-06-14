---
name: robotics-new-system
description: Start the Intent-Driven Robotics AI Workflow for creating a new robotics system, robot runtime, remote operation system, device integration, or architecture-level system launch. Use when the user selects /robotics-new-system or asks to begin a new robotics system development flow from a completed requirement document in work/requirements/.
---

# Robotics New System

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

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
6. Before implementation, create the issue test case tables and evidence plan.
7. Before implementation, run the Boilerplate Template Selection Gate. If a matching boilerplate template exists under `templates/boilerplate-templates/`, use it as the starting point. If no matching template exists, record the reason and continue with traditional coding.
8. Preserve artifacts under `work/<receipt-id>/`.
9. Record decisions, QA, risks, test evidence, RAG context references, specialist review references, boilerplate selection result, and handoff context as JSON where schemas exist.

## Required Focus

- Intent / mission definition
- operational context
- hazard analysis and safety requirements
- system architecture
- runtime / network / deployment design
- test strategy before implementation
- boilerplate template applicability before implementation
- PyQt QTest source plan when the system includes a PyQt / Qt GUI
- integration, bench test, limited field test, release handover

Implementation must not start while STOP behavior, communication loss behavior, startup safe state, or shutdown safe state is unresolved.

## Boilerplate Template Selection Gate

Run this gate after architecture, runtime / network / deployment design, and test strategy are approved, and before implementation starts.

Template root:

```text
templates/boilerplate-templates/
```

Current supported mappings:

| Target | Template path | Instruction |
| --- | --- | --- |
| Go gateway service | `templates/boilerplate-templates/gateway-template/` | `gateway-template_組み込み指示書.md` |
| PyQt / Qt GUI app | `templates/boilerplate-templates/pyqt-template/` | `pyqt-template_組み込み指示書.md` |

Rules:

- Inspect the target system components and decide whether a supported boilerplate combination applies.
- Check that the mapped template directory exists and contains the expected files before using it.
- If the matching template exists, copy the template to the new service / app directory and edit only the copied destination.
- Do not edit the boilerplate template itself during product implementation.
- Preserve the template's responsibility boundaries unless the approved architecture explicitly changes them.
- If no matching boilerplate template exists, record `decision: traditional-coding` and implement with the existing workflow.
- Save the selection result under `work/<receipt-id>/process-report/boilerplate-template-selection.md`.

Required report template:

```text
templates/process-report/boilerplate-template-selection-report-template.md
```

## Test Case And Evidence Flow

Before unit tests, QTest, integration / bench checks, limited field checks, or human checks, create the test case tables for the Issue.

Work artifacts:

```text
work/<receipt-id>/test-specifications/
work/<receipt-id>/test-evidence/
```

Target repository durable artifacts:

```text
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/ut/
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/integration/
work/<receipt-id>/source/repository/docs/evidence/issue-<issue-number>/human_check/
```

Use `unit-test-cases.md` for unit test cases, `integration-test-cases.md` for integration / connectivity, bench, limited-field, and QTest candidates, and `human-check-list.md` for human confirmation items.

`runtime/workflow/knowledge_capture.py` creates missing scaffold directories and `README.md` files, but scaffold files alone are not evidence. Do not push until actual test case files and required evidence files are present, or the skip reason is recorded in the test specification.

## Issue Title

Use the initial development prefix for GitHub Issues:

```text
[初期開発] <issue-title>
```

## Specialist Review Gate

Use Specialist Agent review when a draft artifact depends on domain-specific knowledge such as Go realtime gateway, Python GUI/runtime, network protocols, GStreamer, platform deployment, observability, test fault injection, or robot safety control.

Save review outputs under:

```text
work/<receipt-id>/process-report/specialist-review-<domain>.md
```

The review must record trusted external-web RAG, rejected or limited claims, repository evidence, required tests, and unresolved human-check items. High or critical specialist findings must return the workflow to design or test strategy before implementation.

## PyQt QTest Integration Gate

When the new system includes a PyQt / Qt GUI, convert automatable GUI integration test cases from the approved test specification into QTest-based test sources.

Keep physical robot behavior, real camera quality, physical STOP, and field network checks as bench / human-check evidence.
