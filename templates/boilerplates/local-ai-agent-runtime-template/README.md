# Local AI Agent Runtime Template

Python-based boilerplate for an independent local agent runtime that accepts jobs, executes workflow steps, checkpoints progress, and evaluates completion with evidence.

Copy this directory into a new runtime repository, then edit only the copy.

## Responsibilities

- Accept and track jobs.
- Execute workflow steps in order.
- Maintain checkpointable state.
- Request human checks for unsafe or ambiguous steps.
- Use model and MCP client adapters through narrow interfaces.
- Judge completion from workflow criteria and evidence, not model self-report.

## Non Responsibilities

- MCP server capability implementation.
- Discord, Slack, or Web UI API ownership.
- Arbitrary OS automation.
- Model binary distribution.
- Push, PR, deployment, or external mutation without an approved gateway/policy layer.

## Commands

```powershell
python -m pytest
python -m local_agent_runtime.main --demo
```

On Unix-like shells:

```bash
./scripts/validate.sh
./scripts/run-runtime.sh
```

## Runtime Flow

```text
Command Gateway
  -> Job Manager
  -> Workflow Engine
  -> Agent Worker
     -> Model Adapter
     -> MCP Client Adapter
  -> Completion Evaluator
  -> Evidence
```

## Guardrails

- A job is complete only when required steps and evidence checks pass.
- Human check requests stop execution at a safe boundary.
- Checkpoints are written before pause, failure, or completion.
- Runtime code does not import Discord or MCP server implementations directly.

## Phase 2 Additions

- Runtime clock models the default 8 hour execution budget.
- Retry policy separates transient failures from unsafe retries.
- Command API covers pause, resume, and cancel boundaries.
- Completion evidence is written beside checkpoints.
- Artifact and event registries provide handoff points for gateways and dashboards.

## Phase 3 Additions

- SQLite job store provides a local durable state baseline.
- Worker lease manager models heartbeat and lease expiry.
- Runtime saves completed job state to SQLite in addition to JSON checkpoints and evidence.
