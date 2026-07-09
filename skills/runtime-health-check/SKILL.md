# Runtime Health Check Skill

## Purpose

Use this skill when the user selects `/runtime-health-check` or asks to run a self health check for Ariadne AI Workflow Platform itself.

This workflow verifies the workflow platform runtime rather than a target application repository.

## Scope

The workflow checks:

- runtime pytest
- UT specification synchronization
- `workflow_doctor`
- `aiwfctl doctor`
- Context First `test-evidence` registration
- human-readable runtime quality report
- Japanese Markdown output guard

It does not create GitHub Actions workflows.

## Inputs

No required argument.

Optional inputs:

- `work_id`: work id for Context First evidence registration. Default: `runtime-health-check`.
- `report_dir`: output directory for generated reports. Default: `runtime/.pytest_cache`.

## Standard execution

Run from repository root unless otherwise noted.

```powershell
cd C:\github\ariadne-ai-workflow-platform\runtime
```

Run pytest:

```powershell
.\tools\uv.cmd run --project . --group dev pytest tests -q
```

Run UT specification synchronization and register Context First test evidence:

```powershell
.\tools\uv.cmd run --project . --group dev python tools\pytest_ut_spec_sync.py `
  --spec ..\docs\reference\runtime-pytest-ut-case-specification.md `
  --runtime-root . `
  check `
  --repo-root .. `
  --work-dir runtime\.pytest_cache\runtime-health-check `
  --report .pytest_cache\pytest-ut-spec-sync-report.json `
  --markdown .pytest_cache\pytest-ut-spec-sync-report.md `
  --register-context `
  --required-context
```

Run workflow doctor:

```powershell
.\tools\uv.cmd run --project . --group dev python workflow\workflow_doctor.py `
  --repo-root .. `
  --fail-on-warning
```

Run aiwfctl doctor:

```powershell
.\tools\uv.cmd run --project . --group dev python ctl.py `
  --repo-root .. `
  doctor `
  --json `
  --fail-on-warning
```

Run Japanese Markdown guard:

```powershell
.\tools\uv.cmd run --project . --group dev python workflow\validate_output_language.py `
  --paths ..\docs\reference\runtime-pytest-ut-test-items.md ..\docs\reference\runtime-pytest-ut-case-specification.md ..\.github\schemas\README.md ..\.github\agents\runtime-quality-gate-agent.prompt.md `
  --fail-on-violation
```

## Stop conditions

Stop and report when:

- pytest fails.
- UT specification sync reports missing, stale, order mismatch, or input-position mismatch.
- Context First `test-evidence` registration fails.
- `workflow_doctor --fail-on-warning` fails.
- `aiwfctl doctor --fail-on-warning` fails.
- Japanese Markdown guard fails.

## Outputs

Expected local outputs:

- `runtime/.pytest_cache/pytest-ut-spec-sync-report.json`
- `runtime/.pytest_cache/pytest-ut-spec-sync-report.md`
- `runtime/.pytest_cache/runtime-health-check/context/context-manifest.json`

These are local evidence artifacts and are not committed.

## Completion criteria

The workflow is complete when all standard commands pass and the final report states:

- pytest count
- UT spec sync status
- doctor status
- aiwfctl doctor status
- Context First `test-evidence` path
- remaining warnings, if any


## Workflow Feedback Output

During every AI workflow run, capture actionable workflow friction or improvement candidates in `work/feedback/`.
Create or update a Feedback report when you observe ambiguity, repeated checks, missing context/docs, runtime observation gaps, noisy handoffs, encoding issues, or a reusable workflow improvement.

Use the existing helper when creating a new report:

```powershell
python runtime/workflow/self_improvement.py create-feedback `
  --target-workflow "<slash-command>" `
  --reporter "AI workflow" `
  --situation "<what was happening>" `
  --friction "<observed friction>" `
  --impact "<impact on quality, speed, or safety>" `
  --proposed-improvement "<candidate improvement>"
```

Keep the initial `Review Status` as `Proposed`. Do not run `/self-improvement` automatically inside this workflow; `/self-improvement` is executed later when feedback has accumulated and a human is ready to review Accepted / Rejected / Deferred decisions.
