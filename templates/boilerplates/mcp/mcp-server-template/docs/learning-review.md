# Learning Review

This boilerplate teaches the boundary between a capability provider and an autonomous runtime:

- MCP Server publishes prompts, resources, and tools.
- MCP Server validates inputs and workspace boundaries.
- MCP Server does not own planning, long-running job state, or completion judgment.
- Agent Runtime may consume this server through an MCP Client.

