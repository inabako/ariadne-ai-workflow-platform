---
name: robotics-feature-maintenance
description: Start the Intent-Driven Robotics AI Workflow for adding a new feature to an existing robotics system or performing maintenance development such as bug fix, hardware replacement, network change, deployment change, field issue response, or operational improvement. Use when the user selects /robotics-feature-maintenance or asks to begin feature or maintenance work from a completed requirement document in work/requirements/.
---

# Robotics Feature Maintenance

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.github/shared/output-language-policy.md`.

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
python runtime/intake/intake_requirements.py `
  --workflow robotics-maintenance-development `
  --id-prefix FEAT
```

The harness must reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not treat chat history as a substitute for an accepted requirement document.

## Workflow

1. Run `/pre-development-preparation`.
2. Confirm repository sync, requirement comparison, GitHub Issue, and `feature/issue-<issue-number>` branch.
3. Run the GaC / UaC GUI Mode Dispatcher. If `work/requirements/svg-input/FEAT_*.svg` exists, claim it into the Issue work area and generate GUI difference / PyQt6 / QTest candidates before normal implementation. If no SVG exists, record `skipped` and continue.
4. Run `/rag-load` before entering the development body. Derive parallel retrieval queries from the requirement, repository, branch, comparison report, and issue summary.
5. If impact analysis, change design, or test planning depends on specialist knowledge, run the relevant Specialist Agent review before implementation.
6. Run `/robotics-maintenance-development` only after relevant RAG context has been loaded and summarized.
7. Before implementation, create the issue test case tables and evidence plan.
8. If the change includes a Next.js dashboard, admin, monitoring, or business webapp screen, run the Next.js Webapp Implementation Preparation Gate before source changes.
9. If matching `work/requirements/svg-input/WEB_FEAT_*.svg` exists, run the Web SVG Layout Mode and validate `web-ui/` before source changes.
9. Preserve artifacts under `work/<receipt-id>/`.
10. Record decisions, QA, risks, test evidence, RAG context references, specialist review references, Next.js webapp preparation result, and handoff context as JSON where schemas exist.

## GaC / UaC GUI Mode Gate

Before the workflow starts, the human places SVG files under:

```text
work/requirements/svg-input/FEAT_<name>.svg
work/requirements/svg-input/WEB_FEAT_<name>.svg
```

After the Issue work area exists, dispatch:

```powershell
python runtime/workflow/gui_mode.py run --issue-id "<FEAT-receipt-id>"
```

Use `.github/prompts/gac-uac-gui-mode.prompt.md` for the sub-workflow contract.

Rules:

- The runtime moves matching `FEAT_*.svg` files into `work/<receipt-id>/input/gui/`.
- No matching SVG: continue the parent workflow without GUI artifacts.
- SVG exists: validate `gac-uac/` before implementation.
- Compare generated candidates with existing Widgets, signals, styles, and tests.
- Review integration points, affected areas, and regression tests as FEAT mode.
- Do not overwrite existing source from `generated/`.

## Required Focus

- change intent
- current state capture
- impact analysis
- risk classification
- change design and rollback plan
- test plan based on risk
- Next.js webapp implementation preparation when the change includes a Next.js screen app
- PyQt QTest source plan when the changed system includes a PyQt / Qt GUI
- verification, deployment plan, post-change observation

Safety behavior, network authority, runtime process ownership, and operator workflow changes must be reviewed before implementation.

## Next.js Webapp Implementation Preparation Gate

Run this gate before source changes when the maintenance change includes a Next.js dashboard, admin, monitoring, or business webapp screen.

Use:

```text
.github/prompts/nextjs-webapp-implementation-prep.prompt.md
templates/process-report/nextjs-webapp-implementation-prep-template.md
```

Save the preparation result under:

```text
work/<receipt-id>/process-report/nextjs-webapp-implementation-prep.md
```

Rules:

- Classify the work as `existing-app-feature` or `corrective-fix` unless a new app is explicitly required.
- Treat `templates/boilerplates/nextjs-webapp-template/` as reference-only for existing apps.

## Web SVG Layout Mode Gate

Run this gate after Next.js Webapp Implementation Preparation and before source changes when the maintenance change includes a Next.js screen and a matching SVG exists.

Use:

```text
.github/prompts/web-svg-layout-mode.prompt.md
runtime/workflow/web_svg_layout_mode.py
templates/web-svg-layout/
```

Input:

```text
work/requirements/svg-input/WEB_FEAT_<name>.svg
```

Output:

```text
work/<receipt-id>/web-ui/
```

Rules:

- Treat generated React and Playwright files as candidates only.
- Preserve existing routing, design system, test runner, and env conventions.
- Do not infer API contract, auth, role, env, loading, empty, or error state from SVG alone.
- Preserve existing routing, design system, test runner, env conventions, and app-specific architecture.
- Define route, screen purpose, user action, UI state, API contract, auth/session policy, env/secret boundary, and test evidence before implementation.
- Do not start implementation unless `Implementation may start: yes`.

## Test Case And Evidence Flow

Before unit tests, QTest, integration checks, startup checks, or human checks, create the test case tables for the Issue.

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

Use `unit-test-cases.md` for unit test cases, `integration-test-cases.md` for integration / connectivity and QTest candidates, and `human-check-list.md` for human confirmation items.

`runtime/workflow/knowledge_capture.py` creates missing scaffold directories and `README.md` files, but scaffold files alone are not evidence. Do not push until actual test case files and required evidence files are present, or the skip reason is recorded in the test specification.

## Issue Title

Use the new-feature flow prefix for GitHub Issues:

```text
[新規機能フロー] <issue-title>
```

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
