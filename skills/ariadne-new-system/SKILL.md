---
name: ariadne-new-system
description: Start the Ariadne AI Workflow for creating a new target system, runtime, remote operation system, device integration, or architecture-level system launch. Use when the user selects /ariadne-new-system or asks to begin an Ariadne New System flow from a completed requirement document in work/requirements/.
---

# Ariadne New System

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.ariadne/shared/output-language-policy.md`.

## Slash Command

Use this skill when the user specifies:

```text
/ariadne-new-system
```

This skill delegates the detailed workflow to:

```text
.ariadne/prompts/ariadne-new-system-development.prompt.md
```

## Intake Gate

Before starting the workflow, run or require the intake harness.

```powershell
python runtime/intake/intake_requirements.py `
  --workflow ariadne-new-system-development `
  --id-prefix SYS
```

The harness must reject the order when:

- `work/requirements/` has no completed requirement document
- `work/requirements/` has two or more requirement documents
- the requirement document does not contain readable `Repository Control`

Do not treat chat history as a substitute for an accepted requirement document.

## Workflow

1. Run `/pre-development-preparation`.
2. Confirm repository sync, requirement comparison, GitHub Issue, and `feature/issue-<issue-number>` branch.
3. Run the GaC / UaC GUI Mode Dispatcher. If `work/requirements/svg-input/SYS_*.svg` exists, claim it into the Issue work area and generate GUI design / PyQt6 / QTest candidates before normal implementation. If no SVG exists, record `skipped` and continue.
4. Run `/rag-load` before entering the development body. Derive parallel retrieval queries from the requirement, repository, branch, comparison report, and issue summary.
5. If architecture, runtime, network, deployment, safety, or test strategy depends on specialist knowledge, run the relevant Specialist Agent review before implementation.
6. Run `/ariadne-new-system-development` only after relevant RAG context has been loaded and summarized.
7. Before implementation, create the issue test case tables and evidence plan.
8. Before implementation, run the Boilerplate Template Selection Gate. If a matching boilerplate template exists under `templates/boilerplates/`, use it as the starting point. If no matching template exists, record the reason and continue with traditional coding.
9. If the system includes a Next.js dashboard, admin, monitoring, or business webapp, run the Next.js Webapp Implementation Preparation Gate before source changes.
10. If matching `work/requirements/svg-input/WEB_SYS_*.svg` exists, run the Web SVG Layout Mode and validate `web-ui/` before source changes.
11. Preserve artifacts under `work/<receipt-id>/`.
12. Record decisions, QA, risks, test evidence, RAG context references, specialist review references, boilerplate selection result, Next.js webapp preparation result, and handoff context as JSON where schemas exist.

## GaC / UaC GUI Mode Gate

Before the workflow starts, the human places SVG files under:

```text
work/requirements/svg-input/SYS_<name>.svg
work/requirements/svg-input/WEB_SYS_<name>.svg
```

Initialize the shared input inbox when needed:

```powershell
python runtime/workflow/gui_mode.py init-input
```

After the Issue work area exists, dispatch:

```powershell
python runtime/workflow/gui_mode.py run --issue-id "<SYS-receipt-id>"
```

Use `.ariadne/prompts/gac-uac-gui-mode.prompt.md` for the sub-workflow contract.

Rules:

- The runtime moves matching `SYS_*.svg` files into `work/<receipt-id>/input/gui/`.
- No matching SVG: continue the parent workflow without GUI artifacts.
- SVG exists: validate `gac-uac/` before implementation.
- Treat generated PyQt6 / QTest as candidates, not source replacements.
- Review MainWindow, Panel responsibility, expansion points, and initial QTest structure as SYS mode.

## Required Focus

- Intent / mission definition
- operational context
- hazard analysis and safety requirements
- system architecture
- runtime / network / deployment design
- test strategy before implementation
- boilerplate template applicability before implementation
- Next.js webapp implementation preparation when the system includes a Next.js screen app
- PyQt QTest source plan when the system includes a PyQt / Qt GUI
- integration, bench test, limited field test, release handover

Implementation must not start while STOP behavior, communication loss behavior, startup safe state, or shutdown safe state is unresolved.

## Boilerplate Template Selection Gate

Run this gate after architecture, runtime / network / deployment design, and test strategy are approved, and before implementation starts.

Template root:

```text
templates/boilerplates/
```

Current supported mappings:

| Target | Template path | Docs |
| --- | --- | --- |
| Go gateway service | `templates/boilerplates/services/go-microservice-template/` | `docs/reference/templates.md` |
| Next.js dashboard / admin webapp | `templates/boilerplates/apps/nextjs-app-template/` | `docs/workflows/nextjs-webapp-implementation-prep.md` |
| PyQt / Qt GUI app | `templates/boilerplates/apps/pyqt-app-template/` | `docs/reference/templates.md` |
| Realtime gateway IaC / infrastructure | `templates/boilerplates/infrastructure/microservice-infra-template/` | `docs/workflows/realtime-iac.md` |

Rules:

- Inspect the target system components and decide whether a supported boilerplate combination applies.
- Check that the mapped template directory exists and contains the expected files before using it.
- If the matching template exists, copy the template to the new service / app directory and edit only the copied destination.
- Do not edit the boilerplate template itself during product implementation.
- Preserve the template's responsibility boundaries unless the approved architecture explicitly changes them.
- For IaC template use, preserve the shared artifact, software inventory, public exposure, secret source, firewall policy, rollback, and Terraform validation gates.
- If no matching boilerplate template exists, record `decision: traditional-coding` and implement with the existing workflow.
- Save the selection result under `work/<receipt-id>/process-report/boilerplate-template-selection.md`.

Required report template:

```text
templates/artifacts/process-report/boilerplate-template-selection-report-template.md
```

## Next.js Webapp Implementation Preparation Gate

Run this gate after boilerplate selection and before source changes when the new system includes a Next.js dashboard, admin, monitoring, or business webapp.

Use:

```text
.ariadne/prompts/nextjs-webapp-implementation-prep.prompt.md
templates/artifacts/process-report/nextjs-webapp-implementation-prep-template.md
```

Save the preparation result under:

```text
work/<receipt-id>/process-report/nextjs-webapp-implementation-prep.md
```

Rules:

- Classify the work as `new-app`, `existing-app-feature`, or `corrective-fix`.
- For `new-app`, evaluate `templates/boilerplates/apps/nextjs-app-template/` as the copy source.
- For existing apps, treat `nextjs-app-template` as reference-only and preserve existing routing, design system, test runner, and env conventions.

## Web SVG Layout Mode Gate

Run this gate after Next.js Webapp Implementation Preparation and before source changes when the new system includes a Next.js screen and a matching SVG exists.

Use:

```text
.ariadne/prompts/web-svg-layout-mode.prompt.md
runtime/workflow/web_svg_layout_mode.py
templates/workflows/web-svg-layout/
```

Input:

```text
work/requirements/svg-input/WEB_SYS_<name>.svg
```

Output:

```text
work/<receipt-id>/web-ui/
```

Rules:

- Do not copy generated React or Playwright candidates into target source without review.
- Do not infer API contract, auth, role, env, loading, empty, or error state from SVG alone.
- Validate `web-ui/` before implementation and reflect accepted items into the Next.js preparation report.
- Define route, screen purpose, user action, UI state, API contract, auth/session policy, env/secret boundary, and test evidence before implementation.
- Do not start implementation unless `Implementation may start: yes`.

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

Use Specialist Agent review when a draft artifact depends on domain-specific knowledge such as Go realtime gateway, Python GUI/runtime, network protocols, GStreamer, platform deployment, observability, test fault injection, or safety control.

Save review outputs under:

```text
work/<receipt-id>/process-report/specialist-review-<domain>.md
```

The review must record trusted external-web RAG, rejected or limited claims, repository evidence, required tests, and unresolved human-check items. High or critical specialist findings must return the workflow to design or test strategy before implementation.

## PyQt QTest Integration Gate

When the new system includes a PyQt / Qt GUI, convert automatable GUI integration test cases from the approved test specification into QTest-based test sources.

Keep physical controlled-system behavior, real camera quality, physical STOP, and field network checks as bench / human-check evidence.


## Workflow Feedback Output

During every AI workflow run, capture actionable workflow friction or improvement candidates in `work/feedback/`.
Create or update a Feedback report when you observe ambiguity, repeated checks, missing context/docs, runtime observation gaps, noisy handoffs, encoding issues, or a reusable workflow improvement.

Use the existing helper when creating a new report:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

Keep the initial `Review Status` as `Proposed`. Do not run `/self-improvement` automatically inside this workflow; `/self-improvement` is executed later when feedback has accumulated and a human is ready to review Accepted / Rejected / Deferred decisions.
