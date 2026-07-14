# Transport Selection

The template supports three transport boundaries:

- `in_memory`: mock transport for tests and examples.
- `stdio`: boundary for an official MCP SDK stdio client or managed subprocess.
- `streamable_http`: boundary for an official MCP SDK Streamable HTTP client.

Do not duplicate protocol internals in application code. Replace transport classes with SDK adapters when moving beyond the template.

