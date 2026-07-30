# Adding A Tool

Use this order when adding a new MCP tool:

1. Add request DTOs in `application/dto/requests.py`.
2. Add response DTO fields in `application/dto/responses.py` when needed.
3. Add an inbound port method in `application/ports/inbound/use_case_port.py`.
4. Implement the use case in `application/use_cases/`.
5. Add or extend outbound ports under `application/ports/outbound/` when external I/O is required.
6. Implement outbound adapters under `adapters/outbound/`.
7. Add FastMCP request mapping under `adapters/inbound/fastmcp/mappers/`.
8. Add FastMCP response or error mapping when the public contract changes.
9. Add the tool adapter under `adapters/inbound/fastmcp/tools/`.
10. Register the tool in `adapters/inbound/fastmcp/server.py`.
11. Add application unit tests.
12. Add adapter tests.
13. Add contract tests for tool names, arguments, responses, and error shapes.
14. Update `README.md`.

Do not put business logic directly in a FastMCP-decorated function.
