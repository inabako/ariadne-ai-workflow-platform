# FastMCP Adapter Separation Refactoring Report

## Summary

The MCP server template separates FastMCP-facing code from application behavior. FastMCP is represented as an optional inbound adapter under `adapters/inbound/fastmcp/`.

## Changed Files

- Added application DTOs, inbound ports, outbound ports, and use cases.
- Added outbound adapters for workspace and local model access.
- Added FastMCP adapter, request mapper, response mapper, error mapper, context mapper, tool adapter, resource helper, and prompt helper.
- Refactored `server.py` into a compatibility facade backed by the application container.
- Added architecture and adapter tests.
- Added Docker, compose, and cross-platform run/test scripts.
- Updated README and architecture documentation.

## Architecture Before

```text
MCP-style request
  -> LocalModelMCPServer
  -> workspace policy / model adapter / audit
```

## Architecture After

```text
MCP Client
  -> FastMCP Adapter
  -> Application Port
  -> Application Use Case
  -> Outbound Port
  -> Infrastructure Adapter
```

## FastMCP Dependency Scope

FastMCP references are limited to:

```text
src/local_model_mcp/adapters/inbound/fastmcp/
```

The application and domain layers do not import FastMCP.

## Test Results

Template test:

```text
8 passed
```

Runtime boilerplate contract:

```text
3 passed
```

## Acceptance Criteria Result

Accepted for the boilerplate refactoring baseline. The generated project remains standalone and FastMCP is isolated to the inbound adapter layer.
