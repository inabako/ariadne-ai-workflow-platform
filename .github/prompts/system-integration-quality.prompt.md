# /system-integration-quality

You are running Ariadne's System Integration Quality workflow.

The goal is to confirm that generated or modified code fits the target system, not merely that code was produced.

## Required behavior

- Inspect the target repository before deciding integration changes.
- Prefer existing architecture, Adapter / Port boundaries, configuration conventions, test helpers, evidence layout, and operation procedures.
- Reuse existing components when possible.
- Record why reuse is impossible when a new component is needed.
- Keep SDK-specific types, exceptions, credentials, endpoint settings, and cloud/payment calls behind Adapter / Port boundaries.
- Do not use production credentials or production cloud/payment endpoints without Human Check.
- Do not treat emulator success as production equivalence.

## Runtime commands

```powershell
aiwfctl integration analyze --work-id <work-id>
aiwfctl integration verify --work-id <work-id>
aiwfctl integration verify --work-id <work-id> --with-emulator
aiwfctl integration emulator prepare --work-id <work-id>
aiwfctl integration emulator health --work-id <work-id>
aiwfctl integration test-plan --work-id <work-id>
aiwfctl integration finalize --work-id <work-id>
```

Use `--target-repo` when the target repository is not under `work/<work-id>/source/repository`.

## Context First

Read these contexts when present:

```text
work/<work-id>/context/sdk-analysis-context.json
work/<work-id>/context/sdk-external-discovery.json
work/<work-id>/context/environment-selection.json
```

Write:

```text
work/<work-id>/reports/system-integration-report.md
work/<work-id>/context/integration-context.json
```

Register `integration-context.json` as Context First type `system-integration`.
Register `emulator-context.json` as Context First type `emulator-setup` when emulator templates are expanded.
Register `emulator-health-context.json` as Context First type `emulator-health` after template health/preflight is checked.
Register `integration-test-plan-context.json` as Context First type `integration-test-plan` before mutable Integration Test execution.
Register `integration-finalization-context.json` as Context First type `integration-finalization` after evidence has been collected and reviewed.

## Emulator policy

When cloud or external service metadata is present, classify local verification coverage as:

```text
emulator_verified
real_cloud_verification_required
unsupported_by_emulator
```

For AWS, prefer LocalStack candidates when service mapping exists.
For GCP, prefer official service emulators or reliable service-specific test doubles.
For Stripe, prefer Stripe CLI / test mode and still require Human Check for live billing behavior.

The workflow may plan emulator use and report required setup. It must not silently start real cloud resources or use production credentials.

Use these boilerplate roots when emulator setup is needed:

```text
templates/boilerplates/cloud-emulators/localstack/
templates/boilerplates/cloud-emulators/gcp-emulators/
templates/boilerplates/cloud-emulators/stripe-cli/
```

Copy them into `work/<work-id>/test-environment/emulator/` and edit only the copy. Store launch logs, health checks, and production differences under `work/<work-id>/test-evidence/emulator/`.

Use `aiwfctl integration emulator prepare --work-id <work-id>` to perform this copy safely. The prepare command does not start Docker, real cloud resources, or live payment services.

After prepare, use `aiwfctl integration emulator health --work-id <work-id>` to write `emulator-health-context.json` and `test-evidence/emulator/health-summary.md`. This health step is non-mutating and must not start Docker; `--probe-docker` only runs non-mutating version checks.

Before starting Docker or the target system, use `aiwfctl integration test-plan --work-id <work-id>` to write `integration-test-plan-context.json` and `test-evidence/integration-test/integration-test-runbook.md`. This is a planning gate only; external dependency startup, seed data, target system startup, and cleanup remain Human Check operations.

After Human-approved Integration Test execution has produced evidence, use `aiwfctl integration finalize --work-id <work-id>` to collect evidence, detect discomfort, check completion criteria, and write `integration-finalization-context.json` plus `reports/system-integration-final-report.md`. This finalize step is read-only over evidence and must not execute tests or capture whole source code into Knowledge.

## Completion

The workflow is complete when:

- target system structure was inspected;
- integration points are explicit;
- emulator / real-cloud verification boundaries are explicit;
- Integration Test and evidence expectations are recorded;
- Human Check items are visible;
- Knowledge handoff candidates are listed.
