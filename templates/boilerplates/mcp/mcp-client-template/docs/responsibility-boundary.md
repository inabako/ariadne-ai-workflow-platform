# Responsibility Boundary

## Client Owns

- Server registry.
- Connection lifecycle.
- Capability cache.
- Prompt, resource, and tool request forwarding.
- Retry classification and structured result conversion.

## Client Does Not Own

- Agent loop or workflow state.
- Tool choice.
- MCP server capability implementation.
- Local model invocation.
- Gateway UI or Discord command parsing.

