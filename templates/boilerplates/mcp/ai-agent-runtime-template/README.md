# AI Agent Runtime Template

Python-based boilerplate for an independent local agent runtime that accepts jobs, executes workflow steps, checkpoints progress, and evaluates completion with evidence.

Copy this directory into a new runtime repository, then edit only the copy.

This template is the ARIADNE Agent Runtime baseline under `templates/boilerplates/mcp/`. Do not create a separate `templates/boilerplates/agent-runtime/` copy unless the workflow, references, and contract tests are moved together.

## Responsibilities

- Accept and track jobs.
- Execute workflow steps in order.
- Maintain checkpointable state.
- Request human checks for unsafe or ambiguous steps.
- Use model and MCP client adapters through narrow interfaces.
- Judge completion from workflow criteria and evidence, not model self-report.
- Implement the shared Runtime Contract in `contracts/`.

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
- ARIADNE core runtime does not depend on MCP SDKs; MCP is treated as an optional Tool Adapter for generated outcomes.
- Framework-specific state stays behind adapters or in `framework_metadata`.

## Contract First

Runtime contract schemas live in `contracts/`; see `docs/runtime-contract.md`.

- `trace_id` uses 24 lowercase hexadecimal characters.
- `WorkflowRequest` and `WorkflowResult` are framework-neutral.
- `ToolRequest` and `ToolResult` pass through Tool Ports, including the optional MCP Client Adapter.
- `Checkpoint`, `Evidence`, and `HumanCheckRequest` are stable across Native, LangGraph, Microsoft Agent Framework, CrewAI, and AutoGen compatibility variants.

## Expansion Order

Extend this template in the following order:

1. Common Runtime Contract
2. Native baseline
3. LangGraph adapter
4. CrewAI adapter and Microsoft Agent Framework adapter
5. AutoGen compatibility adapter

Do not implement framework adapters before the common contract and Native baseline pass contract tests.

Framework adapter skeletons live in `src/local_agent_runtime/framework_adapters/`; see `docs/framework-adapters.md`.

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
