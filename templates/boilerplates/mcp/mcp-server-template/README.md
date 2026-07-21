# Local Model MCP Server Template

Python-based boilerplate for an independent MCP server that exposes local model and workspace capabilities through prompts, resources, and tools.

Copy this directory into a new MCP server repository, then edit only the copy.

FastMCP is an inbound adapter in this template. The application and domain layers do not import FastMCP and can be called from another inbound adapter such as CLI, REST, or another MCP SDK adapter.

```text
MCP Client
  -> FastMCP Adapter
  -> Application Port
  -> Application Use Case
  -> Outbound Port
  -> Infrastructure Adapter
```

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
.\scripts\test.ps1
python -m local_model_mcp --health
```

On Unix-like shells:

```bash
./scripts/validate.sh
./scripts/test.sh
./scripts/run-stdio.sh
```

FastMCP integration is optional:

```bash
python -m pip install -e ".[mcp]"
```

Docker smoke start:

```bash
docker build -t local-model-mcp-template .
docker run --rm local-model-mcp-template
```

## Project Structure

```text
src/local_model_mcp/
  bootstrap.py
  server.py
  application/
    dto/
    ports/
    use_cases/
  domain/
  adapters/
    inbound/fastmcp/
    outbound/
```

`server.py` is a compatibility facade for local smoke checks and stdio dispatch. New protocol-specific behavior belongs under `adapters/inbound/`.

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

## Phase 4 Additions

- FastMCP adapter boundary under `adapters/inbound/fastmcp/`.
- Application DTOs, inbound ports, outbound ports, and use cases.
- Bootstrap container that wires config, workspace adapter, model adapter, audit, and use case.
- Architecture test that keeps FastMCP references out of application and domain code.
- Dockerfile, compose file, and Windows/Unix run and test scripts.

## Documentation

- `docs/architecture.md`
- `docs/dependency-rules.md`
- `docs/adding-a-tool.md`
- `docs/adding-an-adapter.md`
- `docs/deployment.md`
