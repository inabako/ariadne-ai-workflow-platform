# Responsibility Boundary

## Gateway Owns

- Discord connection and interaction handling.
- Slash command registry and sync boundaries.
- Authorization based on Discord subject context.
- Runtime command DTO mapping.
- Runtime client calls.
- Notification formatting and delivery.
- Human Check presentation and response submission.
- Gateway audit and local UI state.

## Gateway Does Not Own

- Job state source of truth.
- Human Check source of truth.
- Agent loop.
- Workflow execution.
- MCP connection.
- MCP tool execution.
- Model inference.

