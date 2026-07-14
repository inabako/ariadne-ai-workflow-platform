# /mcp-server-group-implementation

Use this extension when a workflow needs to implement a group of MCP-related services from the repo boilerplates.

## Procedure

1. Confirm the intended work id and selected components.
2. Run `aiwfctl mcp-group analyze --work-id <work-id> --components <components>` before copying templates.
3. Stop for Human Check when the context reports `human-check-required`.
4. Run `aiwfctl mcp-group init --work-id <work-id> --components <components>` after the component boundary is approved.
5. Keep generated services under `work/<work-id>/implementation/mcp-server-group/` until the parent workflow review accepts the implementation shape.
6. Run each copied template's own tests before feature implementation.
7. Pass `mcp-server-group-implementation-context.json` and `mcp-server-group-implementation-report.md` to the parent workflow.

## Components

- `local-model-mcp-server`: local model capability provider exposed as an MCP Server.
- `mcp-client`: reusable client facade used by runtimes and gateways.
- `local-ai-agent-runtime`: job and workflow execution runtime.
- `discord-gateway`: Discord operation gateway.

Default selection is `local-model-mcp-server,mcp-client`.

## Hard Rules

- Do not let Discord Gateway own Agent Runtime state.
- Do not pass Discord library objects into Agent Runtime.
- Do not let Agent Runtime call MCP Servers directly; use the MCP Client boundary.
- Do not treat MCP Server as a job scheduler or completion evaluator.
- Do not copy generated templates into target source without parent workflow review.

## CLI

```powershell
aiwfctl mcp-group analyze --work-id <work-id>
aiwfctl mcp-group init --work-id <work-id> --components local-model-mcp-server,mcp-client,local-ai-agent-runtime
aiwfctl mcp-group run-workflow --work-id <work-id> --components local-model-mcp-server,mcp-client,local-ai-agent-runtime,discord-gateway
```
