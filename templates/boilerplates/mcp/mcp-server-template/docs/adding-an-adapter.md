# Adding An Adapter

Inbound adapters call the same application port. A CLI, REST, scheduler, or alternate MCP SDK adapter should not require changes in domain or application code.

```text
FastMCP Adapter
CLI Adapter
REST Adapter
  -> Application Port
  -> Application Use Case
```

Add a new inbound adapter under:

```text
src/local_model_mcp/adapters/inbound/<adapter-name>/
```

The adapter should:

- Parse protocol-specific input.
- Map input to application DTOs.
- Create an application `RequestContext`.
- Call the inbound port.
- Map the result to protocol-specific output.
- Map internal exceptions to safe public errors.

Do not import the new adapter from application or domain code.
