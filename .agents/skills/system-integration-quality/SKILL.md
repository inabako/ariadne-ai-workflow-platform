---
name: system-integration-quality
description: Verify that generated or modified code integrates safely into an existing target system, including SDKs, external APIs, cloud services, payments, databases, async processing, UI, batch jobs, monitoring, infrastructure settings, tests, operation model, evidence layout, and Knowledge handoff. Use when the user selects /system-integration-quality or asks for integration quality checks.
---

# System Integration Quality Workflow

Use this workflow when generated or modified code must be integrated into an existing target system, especially when SDKs, external APIs, cloud services, payment services, databases, async processing, UI, batch jobs, monitoring, or infrastructure settings are involved.

The purpose is not code generation by itself. Completion means the change fits the target system structure, test strategy, operation model, evidence layout, and Knowledge handoff.

## Runtime entrypoints

```powershell
aiwfctl integration analyze --work-id <work-id>
aiwfctl integration verify --work-id <work-id>
aiwfctl integration verify --work-id <work-id> --with-emulator
aiwfctl integration emulator prepare --work-id <work-id>
aiwfctl integration emulator health --work-id <work-id>
aiwfctl integration test-plan --work-id <work-id>
aiwfctl integration finalize --work-id <work-id>
```

Optional:

```powershell
aiwfctl integration analyze --work-id <work-id> --target-repo C:\path\to\repo
```

## Inputs

- `work/<work-id>/source/repository/`
- `work/<work-id>/context/sdk-analysis-context.json`
- `work/<work-id>/context/sdk-external-discovery.json`
- `work/<work-id>/context/environment-selection.json`
- target repository tests, docs, evidence, configuration, Docker / compose files, and existing Adapter / Port / Interface code

If SDK context is missing, continue with static repository analysis and record the missing context as a Human Check candidate.

## Outputs

```text
work/<work-id>/reports/system-integration-report.md
work/<work-id>/context/integration-context.json
work/<work-id>/context/emulator-context.json
work/<work-id>/context/emulator-health-context.json
work/<work-id>/context/integration-test-plan-context.json
work/<work-id>/context/integration-finalization-context.json
work/<work-id>/test-evidence/emulator/health-summary.md
work/<work-id>/test-evidence/integration-test/integration-test-runbook.md
work/<work-id>/reports/system-integration-final-report.md
work/<work-id>/context/context-manifest.json
```

`integration-context.json` is registered in the Context First manifest as `system-integration`.

## Rules

- Do not use production credentials for emulator or integration verification.
- Do not start real cloud resources without Human Check.
- Do not treat emulator success as production equivalence.
- Do not let SDK-specific types, exceptions, credentials, endpoint settings, or cloud/payment SDK calls leak into application logic without an Adapter / Port boundary.
- Use `emulator_verified`, `real_cloud_verification_required`, and `unsupported_by_emulator` to classify emulator coverage.
- If a target system has an existing testing / evidence convention, follow it instead of inventing a parallel structure.

## Workflow

1. Read requirement, design, SDK, environment, and existing Context First artifacts.
2. Inspect the target repository structure, package files, tests, evidence, configuration, and Adapter / Port candidates.
3. Identify integration points:
   - caller
   - called dependency
   - data mapping
   - exception mapping
   - credential injection
   - endpoint / region / project settings
   - retry / timeout / idempotency
   - logs / metrics / tracing
   - test double / emulator switch
4. Reuse existing components where possible. Record why reuse is impossible when new components are needed.
5. For AWS/GCP, derive emulator candidates from SDK cloud metadata.
6. For Stripe or other external services, derive service-specific test helper candidates.
7. Run static integration consistency checks and record warnings.
8. For verification, inspect integration evidence and emulator suitability.
9. Write the system integration report and Context First context.
10. Pass reusable decisions and constraints to the Knowledge capture / DuckDB flow after Human Review.

## Emulator boilerplates

Use these template roots when emulator setup is required:

```text
templates/boilerplates/integration/cloud-emulators/localstack/
templates/boilerplates/integration/cloud-emulators/gcp-emulators/
templates/boilerplates/integration/cloud-emulators/stripe-cli/
```

Copy templates into the work area before editing:

```text
work/<work-id>/test-environment/emulator/
work/<work-id>/test-evidence/emulator/
```

The template source must remain unchanged during issue work. Edit only the copied work directory.

Use this command for Phase 2 emulator template expansion:

```powershell
aiwfctl integration emulator prepare --work-id <work-id>
```

The command copies selected templates, creates evidence directories, writes `emulator-context.json`, and registers Context First type `emulator-setup`. It does not start Docker, real cloud resources, or Stripe live billing.

After template expansion, run this Phase 3 health gate:

```powershell
aiwfctl integration emulator health --work-id <work-id>
```

The health command writes `emulator-health-context.json`, creates `test-evidence/emulator/health-summary.md`, and registers Context First type `emulator-health`. It checks copied template files, evidence directories, and Docker CLI availability without starting Docker. Use `--probe-docker` only when a non-mutating `docker version` / `docker compose version` check is desired.

For Phase 4, create the Integration Test plan before any mutable execution:

```powershell
aiwfctl integration test-plan --work-id <work-id>
```

The test-plan command writes `integration-test-plan-context.json`, creates `test-evidence/integration-test/integration-test-runbook.md`, and registers Context First type `integration-test-plan`. It plans environment setup, external dependency startup, health check, seed data, target system startup, normal path, error path, log/data checks, and cleanup. It must not start Docker or the target system; mutable actions remain behind Human Check.

For Phase 5, finalize evidence after the Human-approved Integration Test work has produced artifacts:

```powershell
aiwfctl integration finalize --work-id <work-id>
```

The finalize command reads evidence artifacts, detects discomfort, checks completion criteria, writes `integration-finalization-context.json`, creates `reports/system-integration-final-report.md`, and registers Context First type `integration-finalization`. It must not execute tests, start Docker, or capture whole source code into Knowledge.

## Workflow Feedback Output

When workflow friction, missing boilerplate, missing Knowledge, unclear emulator setup, repeated Human Check, or integration discomfort appears during this workflow, save a Proposed Feedback report under `work/feedback/`.

The feedback report must include `Review Status: Proposed` and enough context for later human review.

Do not run `/self-improvement` automatically from this workflow. The normal workflow records the feedback candidate, and a human or later maintenance run decides whether to execute `/self-improvement`.

## Human Check

Human Check is required when:

- changing existing architecture or dependency direction;
- adding production credentials, real cloud permissions, or production network routes;
- using an SDK directly from application logic;
- creating or heavily changing shared components;
- emulator and production behavior differ materially;
- existing tests cannot verify the change;
- operational procedures become more complex;
- integration discomfort remains unresolved.
