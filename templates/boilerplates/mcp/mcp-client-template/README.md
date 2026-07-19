# Reusable MCP Client Template

Python-based reusable MCP client boilerplate for applications that need to connect to one or more MCP servers through a stable facade.

Copy this directory into a new client repository, then edit only the copy.

## Responsibilities

- Manage server descriptors and connection state.
- Expose a small application-facing facade.
- Cache prompts, resources, and tools after connection.
- Execute explicitly requested prompt, resource, and tool operations.
- Enforce retry and security policy boundaries.

## Non Responsibilities

- Agent planning, job queues, workflow steps, or completion judgment.
- MCP server capability implementation.
- Local model inference.
- Discord or other gateway command parsing.
- Tool selection by semantic intent.

## Application Interface

```python
client = MCPClient()
await client.connect("local-model")
await client.list_tools("local-model")
await client.call_tool("local-model", "health_check", {})
await client.disconnect_all()
```

## Commands

```powershell
python -m pytest
python -m reusable_mcp_client.client --list-servers
```

On Unix-like shells:

```bash
./scripts/validate.sh
./scripts/list-servers.sh
```

## Guardrails

- Applications pass a `server_id` explicitly.
- The client does not decide which tool should be used.
- Resource URIs are not treated as local filesystem paths.
- Sessions are not reused after disconnect.
- Real server tokens and runtime session cache are not part of this template.

## Phase 2 Additions

- Retry policy distinguishes retryable transport failures from unsafe operation retries.
- Audit records mask secret-like argument keys.
- Notification and progress DTOs provide stable integration points.
- Credential provider reads server tokens from environment variables without storing them in config.

## Phase 3 Additions

- Transport factory selects in-memory, stdio, or Streamable HTTP boundaries.
- Stdio transport includes request building and an explicit SDK replacement point.
- Timeout helper wraps awaited transport operations.
