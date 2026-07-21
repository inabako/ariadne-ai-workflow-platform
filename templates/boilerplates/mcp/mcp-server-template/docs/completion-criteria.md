# Completion Criteria

The initial boilerplate is complete when:

- Prompt, resource, and tool lists are discoverable.
- Workspace reads are limited to the input root.
- Artifact writes are limited to the output root.
- Secret-like filenames are denied by default.
- Local model invocation goes through an adapter.
- Tests pass without requiring a real model.
- FastMCP references are limited to `adapters/inbound/fastmcp/`.
- Application and domain code run without FastMCP installed.
- Docker smoke start can run without Ariadne installed.

