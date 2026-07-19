# Responsibility Boundary

## Runtime Owns

- Job lifecycle.
- Workflow step state.
- Agent loop boundaries.
- Human check requests.
- Checkpointing.
- Completion evaluation.
- Artifact and evidence registration.

## Runtime Does Not Own

- MCP server implementation.
- Discord API handling.
- Slack API handling.
- Model provider internals.
- Deployment or GitHub mutation.

