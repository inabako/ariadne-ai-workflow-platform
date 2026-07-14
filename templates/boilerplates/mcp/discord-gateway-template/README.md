# Discord Gateway Template

Python-based boilerplate for an independent Discord Gateway that converts Discord interactions into Agent Runtime commands and converts Runtime events into Discord notifications.

Copy this directory into a new gateway repository, then edit only the copy.

## Responsibilities

- Receive Discord slash commands, buttons, select menus, and modal submissions through an adapter.
- Convert Discord-specific inputs into runtime command DTOs.
- Authorize Discord users, roles, guilds, and channels before calling the Runtime API.
- Call Agent Runtime through a dedicated client boundary.
- Present job status, artifacts, errors, and Human Check prompts.
- Apply gateway rate limits, mention sanitization, token masking, and event deduplication.

## Non Responsibilities

- Agent loop, workflow execution, checkpointing, model inference, or completion judgment.
- MCP Client or MCP Server implementation.
- Direct MCP tool execution.
- Storing Discord bot tokens, real guild IDs, user IDs, channel IDs, or runtime logs in the template.
- Treating Gateway state as the source of truth for jobs or Human Check status.

## Commands

```powershell
python -m pytest
python -m discord_agent_gateway.main --demo
```

On Unix-like shells:

```bash
./scripts/validate.sh
./scripts/run-gateway.sh
```

## Initial Capabilities

- `/agent submit`
- `/agent status`
- `/agent pause`
- `/agent resume`
- `/agent cancel`
- `/agent artifacts`
- `/agent health`
- Human Check approve / reject token flow
- Runtime event to Discord message mapping
- Mock Discord adapter and mock Runtime client for tests

## Guardrails

- Discord-specific types stop at the adapter boundary.
- Runtime commands use stable DTOs.
- Bot tokens come from environment variables through `DiscordTokenProvider`.
- Mentions are escaped before sending messages.
- Runtime events are deduplicated before notification delivery.

