---
name: corrective-action-fix
description: Create a corrective action report for a specified GitHub repository and branch, store the base branch under work/<branch>, build/load RAG, create a GitHub Issue, create a separate work/issue-XXX folder with feature/issue-XXX branch, implement fixes, test, request human startup/integration approval, then push. Use when the user selects /corrective-action-fix or asks to move from improvement report creation into corrective implementation.
---

# Corrective Action Fix Skill

## Default Language

Respond to the user in Japanese by default. Human-facing reports, docs, reviews, evidence, and RAG source Markdown must follow `.ariadne/shared/output-language-policy.md`.

## Required Inputs

- target repository: GitHub URL, Markdown link to a GitHub URL, git URL, owner/repo, repository name with `GITHUB_OWNER`, or local path
- target branch: branch name to inspect and base the fix on

Optional input:

- corrective action report path: a Markdown report previously created by `/corrective-action-report`. If omitted, this workflow creates a new Corrective Action Report before Issue creation and implementation.

Example:

```text
/corrective-action-fix [owner/target-system.git](https://github.com/owner/target-system.git) develop
```

If `.env` has `GITHUB_OWNER=owner`, this shorter form is also valid:

```text
/corrective-action-fix target-system develop
```

Use an existing `/corrective-action-report` output:

```text
/corrective-action-fix target-system develop work/db/ariadne-knowledge-platform/rag/corrective-action-report/260704120000_ABC12345_target-system.md
```

## Directory Model

Use two work folders:

- `work/<target-branch>/source/repository`: original/base branch checkout, for report, RAG, and reference
- `work/issue-<issue-number>/source/repository`: fix branch checkout, for implementation, tests, integration checks, and push

Keep the Git branch name as `feature/issue-<issue-number>`.

Do not use `feature/issue-<issue-number>` directly as a work folder name because the slash becomes a nested path on Windows.

## Workflow

Run commands from:

```powershell
cd C:\github\ariadne-ai-workflow-platform
```

### 1. Initialize Base Work Area

Create `work/<target-branch>`:

```powershell
python runtime/workflow/init_corrective_action_fix.py `
  --repository "<target-repository>" `
  --target-branch "<target-branch>"
```

For `develop`, the default `work_id` is `develop`.

If `work/<target-branch>` already exists, stop and ask the user to confirm whether to reuse it. Do not overwrite or silently reuse the existing base checkout. After confirmation, rerun with:

```powershell
python runtime/workflow/init_corrective_action_fix.py `
  --repository "<target-repository>" `
  --target-branch "<target-branch>" `
  --reuse-existing
```

### 2. Prepare Base Repository / Branch

Clone or fetch the target branch into `work/<target-branch>/source/repository`:

```powershell
python runtime/scm/prepare_repository.py `
  --work-id "<target-branch>" `
  --repository "<target-repository>" `
  --target-branch "<target-branch>"
```

### 3. Read or Create Corrective Action Report

If the user supplied a report path, read that Markdown report as the `/corrective-action-report` output and keep it as the improvement source.

If no report path was supplied, create a new Corrective Action Report by running the same read-only analysis rules as `/corrective-action-report`.

Write the report to:

```text
work/db/ariadne-knowledge-platform/rag/corrective-action-report/YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md
```

The report must include:

- prioritized findings
- recommended actions
- affected files/components
- expected unit tests
- startup/integration check expectations
- human-check items

### 3.5 Environment Preflight Gate

Before moving to the next workflow phase, check whether required local tools are available.

Create a preflight report:

```powershell
python runtime/environment/preflight.py `
  --profile corrective-action-fix `
  --work-id "<target-branch>"
```

If the result status is `ready`, continue to the next flow.

If the result status is `install-list-required`:

1. Read the generated `work/<target-branch>/process-report/environment-preflight-*.md`.
2. Show the missing required tools and install commands to the user.
3. Stop and ask whether installation is approved.
4. Do not install anything until the user explicitly approves.

After approval, run:

```powershell
python runtime/environment/preflight.py `
  --profile corrective-action-fix `
  --work-id "<target-branch>" `
  --install `
  --human-check approved
```

Re-run the non-install preflight after installation. Continue only when the required checks are ready, or when the user explicitly accepts the remaining risk.

### 4. Build RAG

Run `/rag-build` or the equivalent pipeline:

```powershell
python runtime/rag/standardize_corrective_report_names.py `
  --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report `
  --replace-references

python runtime/rag/normalize_documents.py `
  --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report `
  --output-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --document-type corrective-action-report `
  --clean-output

python runtime/rag/chunk_documents.py `
  --input-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --output-dir work/db/ariadne-knowledge-platform/rag/chunks `
  --clean-output

python runtime/rag/build_index.py `
  --normalized-dir work/db/ariadne-knowledge-platform/rag/normalized `
  --chunks-dir work/db/ariadne-knowledge-platform/rag/chunks `
  --output-dir work/db/ariadne-knowledge-platform/rag/indexes

python runtime/rag/embed_chunks.py `
  --chunks-index work/db/ariadne-knowledge-platform/rag/indexes/chunks.jsonl `
  --output work/db/ariadne-knowledge-platform/rag/embeddings/chunks-embeddings.jsonl
```

### 5. Load RAG Before Implementation

Run `/rag-load` with the report, repository, branch, and intended fix as context:

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "<corrective action fix summary>" `
  --repository "<target-repository>" `
  --branch "<target-branch>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

Read the generated `artifact_type: rag-load-dispatch` JSON and referenced `artifact_type: rag-context-pack` JSON before implementation.

### 5.1 External Web RAG Support Gate

If the corrective action involves an unfamiliar implementation area, standards-sensitive behavior, network/runtime behavior, or technology-specific constraints, dispatch external-web RAG as supporting context before finalizing the Issue body or implementation plan.

Examples:

- Go realtime gateway
- UDP / TCP / QUIC behavior
- NAT traversal
- GStreamer pipeline behavior
- Docker / Windows / Raspberry Pi platform behavior
- Prometheus / OpenTelemetry design

Use saved external-web RAG first:

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "<unknown implementation area>" `
  --source-type external-web `
  --category "<category>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

If there is no suitable saved external-web RAG, use the external-web source reviewer flow:

```text
work/db/ariadne-knowledge-platform/rag/external-web/knowledge-sources.md
.ariadne/agents/external-web-source-reviewer-agent.prompt.md
.ariadne/agents/external-web-rag-dispatcher-agent.prompt.md
```

Record external-web references as supporting references in:

```text
work/<target-branch>/process-report/
work/issue-<issue-number>/process-report/
```

External-web RAG may shape the implementation plan, test specification, and risk checks. It must not override current source code, test evidence, or the corrective action report.

### 5.2 Specialist Review Gate

If the Issue scope, implementation plan, or test specification depends on domain-specific interpretation, run the relevant Specialist Agent review after external-web RAG dispatch and before finalizing the Issue body or implementation plan.

Use this gate for areas such as:

- Go realtime gateway
- Python GUI / runtime
- UDP / TCP / QUIC / NAT traversal
- GStreamer / video pipeline
- Windows / Linux / Raspberry Pi / Docker / MSYS2 platform behavior
- Prometheus / OpenTelemetry / logging / metrics
- pytest / Go test / fault injection / packet evidence
- STOP / communication loss / safe state / watchdog

Save review outputs under:

```text
work/<target-branch>/process-report/specialist-review-<domain>.md
work/issue-<issue-number>/process-report/specialist-review-<domain>.md
```

The review must record trusted external-web RAG, rejected or limited claims, repository evidence, required tests, and unresolved human-check items. High or critical specialist findings must be resolved before implementation or push.

### 5.5 Dependency / Support Component Gate

Before creating the Issue branch, confirm whether the target fix needs support repositories, local tools, Python packages, MSYS2 packages, or runtime devices. At this stage, create the dependency plan and include it in the Issue body. Run repository preparation commands after `work/issue-<issue-number>` exists.

Use the loaded RAG context, semantic hints, and current repository evidence first. If the target repository has a project-specific runtime contract, shared package, simulator, support service, device SDK, or communication protocol, treat it as a required dependency only when that requirement is stated by evidence.

Example package dependency:

```toml
dependencies = [
  "target-system-protocol>=1.0.0"
]
```

Preferred verification:

```powershell
pip install "target-system-protocol>=1.0.0"
python -c "import target_system_protocol; print('ok')"
```

Use the published package first when the project declares one. Do not assume an editable sibling checkout unless the repository evidence, semantic hint, or human instruction requires it.

If the published package cannot be fetched or installed, prepare the required support repository under the same issue source folder level after step 7:

```powershell
python runtime/scm/prepare_support_repository.py `
  --work-id "issue-<issue-number>" `
  --name "target-system-protocol" `
  --repository "owner/target-system-protocol" `
  --branch "<target-branch>"
```

Only use this fallback when the package path is unavailable or the target workflow explicitly requires source-level integration. Prepare simulator, mock, or support-service repositories only when the fix requires a runnable counterpart.

For libraries or packages that must be installed, list the missing items, install commands, and fallback repository commands first, then stop for human approval. Do not install automatically until the user approves.

Record discovered support components and missing tools in:

```text
work/<work-id>/context/support-repositories.json
work/<work-id>/process-report/
```

### 6. Create GitHub Issue

Create an issue body from the corrective action report and loaded RAG context.
When the target repository has `.github/ISSUE_TEMPLATE.md`, use that project-local template as the issue body base.

Issue title must use the corrective-action prefix:

```text
[改善フロー] <issue-title>
```

Minimum sections:

- Intent
- Corrective action report path
- Findings to fix in this branch
- Implementation scope
- Supporting references, including external-web RAG when used
- Specialist review references when used
- Unit tests
- Startup / integration check
- Human check gate
- Acceptance criteria

Issue body source priority:

1. Explicit `--body-file`
2. Target repository `.github/ISSUE_TEMPLATE.md`
3. Runtime fallback body generated by `runtime/github/issue_manager.py`

Before GitHub creation, review the generated draft under:

```text
work/<target-branch>/process-report/github-issue-*.md
```

Create a draft unless the user explicitly approves GitHub mutation:

```powershell
python runtime/github/issue_manager.py `
  --work-id "<target-branch>" `
  --title "<issue-title>" `
  --flow-label improvement `
  --body-file "<issue-body.md>"
```

When approved:

```powershell
python runtime/github/issue_manager.py `
  --work-id "<target-branch>" `
  --title "<issue-title>" `
  --flow-label improvement `
  --body-file "<issue-body.md>" `
  --create
```

### 7. Initialize Issue Work Area And Branch

After an issue number exists, create `work/issue-<issue-number>`:

```powershell
python runtime/workflow/init_corrective_action_fix.py `
  --repository "<target-repository>" `
  --target-branch "<target-branch>" `
  --work-id "issue-<issue-number>" `
  --base-work-id "<target-branch>"
```

If `work/issue-<issue-number>` already exists, stop and ask the user to confirm whether this is the same Issue work area. After confirmation, rerun with `--reuse-existing`.

Create the GitHub branch first, then clone that branch into the issue work folder:

```powershell
python runtime/scm/create_issue_branch.py `
  --work-id "issue-<issue-number>" `
  --issue-number "<issue-number>" `
  --repository "<target-repository>" `
  --base-branch "<target-branch>" `
  --link-to-issue
```

The work folder is `work/issue-<issue-number>`, and the Git branch is:

```text
feature/issue-<issue-number>
```

### 7.5 Encoding / Mojibake Gate

If source files show mojibake or unreadable non-ASCII text during analysis or implementation, treat it as a workflow concern.

Detection examples:

- Japanese comments display as fragments such as `縺`, `繧`, `譁`, `謗`, or replacement characters such as `�`. <!-- text-boundary: allow-mojibake-example -->
- Patch context fails because non-ASCII comments are unreadable or unstable.
- PowerShell output and file content disagree about Japanese text.

Procedure:

1. If mojibake is found in the read-only base checkout, do not edit the base branch. Record it in the corrective action report or issue body.
2. After the issue branch exists, check whether the target repository already has `.editorconfig` at its repository root.
3. If it does not, add `.editorconfig` from `templates/repository/editorconfig/target-repository.editorconfig` into `work/issue-<issue-number>/source/repository/.editorconfig`.
4. Preserve `.bat` / `.cmd` Shift_JIS operation by keeping `charset = unset` and `end_of_line = crlf` for those files.
5. Ask the user to reload the editor/session for the target repository after adding `.editorconfig`.
6. Re-read the affected files after reload before continuing implementation. Do not rely on previously garbled buffers.
7. If the file still contains unstable or unreadable non-ASCII text, avoid using garbled text as patch context. Use stable ASCII anchors, IDs, function names, or deliberately inserted ASCII markers to make the smallest mechanical replacement possible.
8. When ASCII markers are inserted only to protect an edit boundary, remove them before finishing unless they are useful comments or test fixtures.
9. Do not mass-convert existing files unless the Issue explicitly includes encoding normalization. For ordinary fixes, add `.editorconfig`, re-read the file, and keep code changes scoped.

### 7.6 GaC / UaC GUI Mode Gate

Before the workflow starts, the human places corrective GUI SVG files under:

```text
work/requirements/svg-input/FIX_<name>.svg
```

After `work/issue-<issue-number>` and its Issue branch exist, dispatch the shared GUI sub-workflow with the logical FIX prefix while preserving the existing corrective-action work directory:

```powershell
python runtime/workflow/gui_mode.py run `
  --issue-id "FIX-<issue-number>" `
  --work-dir "work/issue-<issue-number>" `
  --mode corrective-improvement
```

The runtime moves matching `FIX_*.svg` files into `work/issue-<issue-number>/input/gui/`. If no matching SVG exists, continue with `status: skipped`.

If SVG exists:

- validate `work/issue-<issue-number>/gac-uac/` before implementation;
- treat generated source and QTest as candidates only;
- compare candidates with the current GUI and apply only reviewed minimal changes;
- prioritize existing behavior, fixed-coordinate removal, responsibility separation, and regression prevention;
- keep actual tests in the target repository's normal test tree after review.

### 7.7 Next.js Webapp Implementation Preparation Gate

If the corrective issue includes a Next.js dashboard, admin, monitoring, or business webapp screen, create the preparation report before source changes:

```text
work/issue-<issue-number>/process-report/nextjs-webapp-implementation-prep.md
```

Use:

```text
.ariadne/prompts/nextjs-webapp-implementation-prep.prompt.md
templates/artifacts/process-report/nextjs-webapp-implementation-prep-template.md
```

Rules:

- Classify the work as `existing-app-feature` or `corrective-fix` unless a new app is explicitly required by the Issue.
- Treat `templates/boilerplates/apps/nextjs-app-template/` as reference-only for existing apps.

### 7.8 Web SVG Layout Mode Gate

If the corrective issue includes a Next.js screen and matching SVG input exists, run the Web SVG Layout Mode after Next.js Webapp Implementation Preparation and before source changes:

```text
work/requirements/svg-input/WEB_FIX_<name>.svg
```

Use:

```text
.ariadne/prompts/web-svg-layout-mode.prompt.md
runtime/workflow/web_svg_layout_mode.py
templates/workflows/web-svg-layout/
```

Output:

```text
work/issue-<issue-number>/web-ui/
```

Rules:

- Treat generated React and Playwright files as candidates only.
- Preserve existing screen behavior and keep the corrective scope minimal.
- Do not infer API contract, auth, role, env, loading, empty, or error state from SVG alone.
- Preserve existing routing, design system, test runner, env conventions, and app-specific architecture.
- Define route, screen purpose, user action, UI state, API contract, auth/session policy, env/secret boundary, and test evidence before implementation.
- Do not start implementation unless `Implementation may start: yes`.

### 8. Implement Corrective Fixes

Implement in `work/issue-<issue-number>/source/repository` according to the corrective action report and loaded RAG.

Rules:

- Keep changes scoped to the Issue.
- Preserve safety behavior.
- Treat external-web RAG as supporting context only; verify the adopted behavior with local tests or integration evidence.
- Treat Specialist Agent review as supporting context; connect accepted external knowledge to tests or human checks.
- If a safety-critical finding cannot be resolved, stop and report the blocker.
- Record implementation notes in `work/issue-<issue-number>/process-report/`.

### 8.5 Create Test Specification

Before running unit tests, startup checks, or integration / communication checks, write the test specification and test case table.

Use:

```text
templates/artifacts/test-specifications/ariadne-test-specification-template.md
```

Save the issue-specific test specification under:

```text
work/issue-<issue-number>/test-specifications/
```

Before push, split the durable target-repository test case tables into:

```text
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md
```

Use `unit-test-cases.md` for unit test cases, `integration-test-cases.md` for integration / connectivity and QTest candidates, and `human-check-list.md` for human confirmation items.

The test specification must include:

- Change-based test viewpoints derived from the corrective action report, Issue scope, implementation plan, and expected code / behavior changes.
- Unit test cases for the corrective fix.
- Integration / communication test cases for the affected runtime path.
- PyQt QTest source plan when the target repository uses PyQt / Qt GUI.
- Startup checks required before integration testing.
- Human-check items and pass criteria.
- Required evidence and save locations under `work/issue-<issue-number>/test-evidence/`.
- Target repository docs save locations under `docs/evidence/issue-<issue-number>/`.
- Known constraints or accepted risks.

For each planned change, add at least one test case or explicitly record why it is not directly testable. Cover normal behavior, boundary / error behavior, regression risk, safety impact, and observability such as logs, metrics, or UI display when applicable.

For target systems with simulator, controller, device, or support-service integration, include test cases for discovery, connection, command send / receive, observable state display, telemetry or event receive, error handling, logging, and human confirmation when manual verification remains necessary. Derive exact scenarios from semantic hints, RAG context, and current repository evidence.

Do not start unit tests or integration / communication checks until the required test cases and pass criteria are written, unless the user explicitly approves skipping the test specification for a trivial change.

### 9. Add And Run Unit Tests

Create or update unit tests that prove the fix according to the test specification.

Record commands and results in `work/issue-<issue-number>/test-evidence/`.

### 9.5 Create PyQt QTest Integration Sources

If the target repository uses PyQt / Qt GUI, convert automatable integration / connectivity test cases from the approved test specification into QTest-based test sources before manual startup or human integration checks.

QTest source candidates include:

- Connect / Disconnect button behavior
- control key send and UI state change
- telemetry receive display
- sensor override UI
- Event Log / Packet display
- FPS label or video state label
- show / close lifecycle
- startup with external I/O disabled or stubbed

Recommended target location:

```text
work/issue-<issue-number>/source/repository/src/tests/qt/test_<feature>_integration.py
```

Each QTest test must reference the source Test Case ID in comments, test names, or evidence notes.

Default policy:

- Use `PyQt6.QtTest.QTest` or the target repository's existing Qt test pattern.
- Prefer fixtures/stubs that prevent real UDP sockets, GStreamer receivers, RobotController instances, hardware services, or external processes from starting unless the test case explicitly requires them.
- Do not use QTest to silently broaden the Issue scope.
- If a test case cannot be automated with QTest, record the reason and keep it as manual / human-check evidence.

Record QTest commands and results in:

```text
work/issue-<issue-number>/test-evidence/qtest_integration/
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/integration/qtest/
```

### 10. Startup / Integration Check

Before startup or integration checks, run target-specific preflight when the repository has setup scripts or external runtime dependencies.

For fixes that involve communication between the target application and a simulator, mock, device adapter, or support service, prepare and start all required runtime processes before asking for human confirmation:

- `work/issue-<issue-number>/source/repository`: primary target repository
- `work/issue-<issue-number>/source/<support-component>`: simulator, mock, adapter, or support service when required

The integration check must keep both processes running at the same time while waiting for the user result. Record launch commands, important environment variables, ports, logs, and the human result in `work/issue-<issue-number>/test-evidence/`.

Run the default corrective-action preflight, or a target-specific profile when the repository evidence declares one:

```powershell
python runtime/environment/preflight.py `
  --profile corrective-action-fix `
  --work-id "issue-<issue-number>" `
  --source-dir "work/issue-<issue-number>/source/repository"
```

When a semantic hint or repository document declares a specific runtime profile or dependency verification command, run it after the default preflight and record the result. If a package cannot be fetched, use the fallback support repository command documented in the dependency plan, then rerun preflight.

If required tools or MSYS2 packages are missing, create the install list, stop, and ask the user for approval before installing.

After approval:

```powershell
python runtime/environment/preflight.py `
  --profile corrective-action-fix `
  --work-id "issue-<issue-number>" `
  --source-dir "work/issue-<issue-number>/source/repository" `
  --install `
  --human-check approved
```

Run the appropriate startup or integration check for the target repository.

Record commands, logs, screenshots if useful, and outcome in `work/issue-<issue-number>/test-evidence/`.

### 11. Human Check Gate

Stop after startup/integration evidence is ready.

Ask the user to verify the startup/integration result.

Do not push until the user explicitly confirms the check is approved.

### 12. Finalize PR Material And Docs Evidence

Before pushing, create the final PR material and confirm test evidence docs placement.

Run:

```powershell
python runtime/workflow/knowledge_capture.py `
  --issue "issue-<issue-number>" `
  --repository "<target-repository>" `
  --branch "feature/issue-<issue-number>" `
  --base-work-id "<target-branch>"
```

Generated files:

```text
work/issue-<issue-number>/process-report/pull-request-title.md
work/issue-<issue-number>/process-report/pull-request-description.md
work/issue-<issue-number>/process-report/merge-comment.md
work/issue-<issue-number>/process-report/knowledge-capture-report.md
```

Store the test case tables and evidence in the target repository docs tree before push:

```text
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/unit-test-cases.md
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/integration-test-cases.md
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/test_specifications/human-check-list.md
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/ut/
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/integration/
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/human_check/
```

`knowledge_capture.py` creates missing evidence directories and scaffold `README.md` files automatically.
Do not push if required docs evidence files are missing, or if the required directories contain only scaffold `README.md` files.

### 13. Push Issue Branch

After human approval:

Before pushing, confirm:

- `work/issue-<issue-number>/context/scm-state.json` points to the repository given in step 1.
- `source_dir` is `work/issue-<issue-number>/source/repository`.
- `working_branch` is `feature/issue-<issue-number>`.
- The push target is not `ariadne-ai-workflow-platform`.

```powershell
python runtime/scm/push_branch.py `
  --work-id "issue-<issue-number>" `
  --human-check approved `
  --set-upstream
```

### 14. Create Pull Request To Develop

After the issue branch is pushed, create a Pull Request to `develop`.

The Pull Request title must use the GitHub Issue title.

The Pull Request body must include a Mermaid sequence diagram showing the change flow.

Draft PR record:

```powershell
python runtime/github/pull_request_manager.py `
  --work-id "issue-<issue-number>" `
  --base develop
```

Create PR after human approval:

```powershell
python runtime/github/pull_request_manager.py `
  --work-id "issue-<issue-number>" `
  --base develop `
  --create `
  --human-check approved
```

### 15. Finalization And Knowledge Capture

After the issue branch is pushed, run final knowledge recovery.

Required outputs:

```text
work/issue-<issue-number>/process-report/pull-request-title.md
work/issue-<issue-number>/process-report/pull-request-description.md
work/issue-<issue-number>/process-report/merge-comment.md
work/issue-<issue-number>/process-report/knowledge-capture-report.md
```

RAG source candidates:

```text
work/issue-<issue-number>/process-report
work/issue-<issue-number>/test-specifications
work/issue-<issue-number>/test-evidence
work/db/ariadne-knowledge-platform/rag/specialist-review/<domain>
```

RAG registration requires explicit human approval. After approval, run `/rag-build` or the equivalent runtime RAG pipeline.

Report-only close archive target:

```text
work/close/improvement/issue-<issue-number>/
  00-summary.md
  01-work-report.md
  02-test-report.md
  03-review-report.md
  04-human-check.md
  05-retrospective.md
  links.md
  metadata.json
```

Base work reset:

Before deleting `work/<target-branch>`, summarize and link base-phase process reports under the closed issue folder:

```text
work/<target-branch>/process-report
  -> work/close/improvement/issue-<issue-number>/links.md and summary reports
```

After the report-only archive is verified, delete `work/<target-branch>` so the next corrective flow starts from a clean base work folder.

Do not prepare or prune the close archive until the user approves archive.

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

## Guardrails

- Never push `ariadne-ai-workflow-platform` during this flow. This repository is only the workflow/RAG/report workspace.
- Push only the issue branch in the repository specified by the user in step 1.
- Treat `work/issue-<issue-number>/source/repository` as the only valid source directory for push unless the user explicitly overrides it after reviewing the push target.
- Do not silently reuse an existing `work/<branch>` or `work/issue-<issue-number>` folder. Stop and ask the user to confirm reuse first.
- Do not push before human startup/integration approval.
- Do not create a Pull Request before the issue branch is pushed and PR material has been generated.
- Do not create GitHub Issues unless the user has approved mutation or the environment policy allows it for this flow.
- When an Issue branch is created on GitHub, use the GraphQL `createLinkedBranch` path (`--link-to-issue`) so GitHub records it as the Issue linked branch.
- Do not install missing tools, Python packages, or MSYS2 pacman packages without explicit human approval.
- Do not run unit tests, startup checks, or integration / communication checks before writing the issue test specification and pass criteria, unless the user explicitly approves skipping it for a trivial change.
- For PyQt / Qt GUI repositories, do not skip QTest source planning for automatable integration cases unless the test specification records a reason.
- When `work/requirements/svg-input/FIX_*.svg` exists, do not skip the GaC / UaC GUI Mode Gate or copy generated candidates into source without review.
- For Next.js screen changes, do not skip `nextjs-webapp-implementation-prep.md` or start source changes before `Implementation may start: yes`.
- When `work/requirements/svg-input/WEB_FIX_*.svg` exists, do not skip the Web SVG Layout Mode Gate or copy generated candidates into source without review.
- Do not push before PR material is generated and docs evidence exists under `docs/evidence/issue-<issue-number>/test_specifications`, `docs/evidence/issue-<issue-number>/ut`, and `docs/evidence/issue-<issue-number>/integration`; add `docs/evidence/issue-<issue-number>/human_check` when human confirmation is required. Scaffold `README.md` files alone are not evidence.
- Do not run RAG registration / rebuild or prepare/prune `work/close/improvement/issue-<issue-number>` without explicit human approval.
- Do not delete `work/<target-branch>` until `work/<target-branch>/process-report` has been summarized / linked under `work/close/improvement/issue-<issue-number>/` and the report-only archive has been verified.
- Do not skip RAG build/load.
- Do not implement on the target branch directly.
- Keep `/corrective-action-report` read-only; use this skill for implementation.
