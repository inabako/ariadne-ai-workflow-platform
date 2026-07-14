# Local Model MCP Server Template

Python-based boilerplate for an independent MCP server that exposes local model and workspace capabilities through prompts, resources, and tools.

Copy this directory into a new MCP server repository, then edit only the copy.

## Responsibilities

- Expose MCP-style prompts, resources, and tools.
- Validate tool inputs before execution.
- Keep all workspace file access inside configured input and output roots.
- Call a local model adapter through a narrow interface.
- Return structured results and audit-friendly errors.

## Non Responsibilities

- Agent planning, job queues, checkpointing, retry loops, or completion judgment.
- Discord, Slack, Web UI, or any external gateway concerns.
- Arbitrary shell execution, Git push, file deletion, or OS administration.
- Model binary distribution or secret storage.

## Commands

```powershell
python -m pytest
python -m local_model_mcp.server --health
```

On Unix-like shells:

```bash
./scripts/validate.sh
./scripts/run-stdio.sh
```

## Capabilities

Prompts:

- `workflow_instruction`
- `repository_analysis`
- `implementation_plan`

Resources:

- `workflow://definitions`
- `project://context`
- `model://information`
- `artifact://outputs`

Tools:

- `health_check`
- `list_workspace_files`
- `read_workspace_file`
- `invoke_local_model`
- `write_output_artifact`

## Guardrails

- Do not expose raw local file paths as resource URIs.
- Do not allow absolute paths or `..` traversal in tool inputs.
- Do not include model weights, runtime output, real secrets, or logs in this template.
- Treat this server as a capability provider, not as an autonomous agent.

## Phase 2 Additions

- Tool policy blocks denied operations such as arbitrary shell execution.
- Audit records capture workspace read and artifact write events.
- Binary file reads and over-limit writes are denied by default.
- HTTP host and origin checks are provided as a Streamable HTTP extension point.
- Prompt migration and learning review docs explain the MCP Server / Agent Runtime boundary.

## Phase 3 Additions

- Environment-backed config loader for template runtime paths.
- Ollama adapter boundary using standard library HTTP calls.
- JSON-line stdio dispatcher for prompt/resource/tool smoke checks.
- Transport docs explain where to replace template code with an official MCP SDK adapter.
