# Integration Guide

Replace the in-memory mock server with an official MCP SDK transport adapter.

Application code should depend on `MCPClient`, not SDK internals. This keeps Agent Runtime, Gateway, CLI, and test harness integrations consistent.

