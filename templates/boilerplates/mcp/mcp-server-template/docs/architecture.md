# Architecture

This template is an independent MCP server project. FastMCP is treated as an inbound adapter, not as the application core.

```text
MCP Client
  -> FastMCP Inbound Adapter
  -> Application Port
  -> Application Use Case
  -> Domain / Service
  -> Outbound Port
  -> Infrastructure Adapter
```

## Responsibility Boundaries

- `adapters/inbound/fastmcp/` exposes MCP tools, resources, and prompts.
- `application/ports/inbound/` defines the use case boundary used by inbound adapters.
- `application/use_cases/` coordinates validation, domain calls, outbound ports, and result DTOs.
- `application/ports/outbound/` defines model and workspace interfaces.
- `adapters/outbound/` implements filesystem and local-model integration.
- `bootstrap.py` wires config, outbound adapters, use cases, and adapter factories.
- `server.py` remains a compatibility facade for simple smoke tests and stdio dispatch.

## Dependency Direction

```text
adapters -> application
adapters -> domain
application -> domain
bootstrap -> adapters
bootstrap -> application
```

Application and domain code must not import FastMCP. Replacing FastMCP with CLI, REST, or another MCP SDK should only affect inbound adapter code.

## FastMCP Scope

FastMCP imports are allowed only under:

```text
src/local_model_mcp/adapters/inbound/fastmcp/
```

The adapter maps MCP arguments to application DTOs, calls the inbound port, maps application results back to MCP responses, and hides internal exception details.

## Standalone Execution

The generated project must run without Ariadne installed:

```bash
python -m pytest
python -m local_model_mcp --health
```

FastMCP itself is optional in this boilerplate:

```bash
python -m pip install -e ".[mcp]"
```
