# Responsibility Boundary

## Server Owns

- Capability registration.
- Prompt, resource, and tool input contracts.
- Workspace path policy.
- Local model adapter invocation.
- Structured errors and audit records.

## Server Does Not Own

- Job scheduling.
- Long-running loops.
- Human check waiting state.
- Completion evaluation.
- External chat or gateway APIs.

