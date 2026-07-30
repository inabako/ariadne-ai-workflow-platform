# Runtime Contract

This template is contract-first. Framework runtimes, MCP clients, model providers, and gateways must adapt to the runtime contract instead of changing application or domain code.

## Contract Files

Runtime contracts live in `contracts/`.

| Contract | Purpose |
| --- | --- |
| `workflow-request.schema.json` | Workflow start request from a gateway or ARIADNE-generated caller |
| `workflow-result.schema.json` | Workflow final or current result |
| `runtime-context.schema.json` | Normalized runtime context used inside the runtime |
| `execution-metadata.schema.json` | Traceable execution metadata |
| `agent-task.schema.json` | Task sent to an agent worker |
| `agent-result.schema.json` | Result returned by an agent worker |
| `tool-request.schema.json` | Tool call through a Tool Port or MCP Client Adapter |
| `tool-result.schema.json` | Tool call result |
| `checkpoint.schema.json` | Resume-safe runtime checkpoint |
| `evidence.schema.json` | Verifiable runtime evidence |
| `human-check.schema.json` | Human approval request |
| `runtime-error.schema.json` | Normalized runtime error |

## Rules

- `trace_id` is 24 lowercase hexadecimal characters.
- Framework state must stay in adapter-owned code or `framework_metadata`.
- Secrets, API keys, tokens, and credentials must not be stored in contract payloads.
- MCP is an optional Tool Adapter path, not a core runtime dependency.
- Completion is based on required steps and evidence, not model self-report.

## Adapter Boundary

```text
Workflow / Agent Worker
  -> Tool Port
  -> Tool Adapter
  -> MCP Client Adapter, CLI, HTTP, Repository, Database, or FileSystem
```

Agent Runtime must not import MCP Server internals, Discord SDK objects, or framework-native state into the domain model.
