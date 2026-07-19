# Prompt Migration Guide

Move workflow prompt content into MCP capabilities by separating:

- Goal and workflow instruction: Prompt.
- File or repository context: Resource.
- File read, model invocation, and artifact write: Tool.
- Completion judgment: Agent Runtime, not MCP Server.

Example:

```text
Before: "Read README, analyze tests, write report, decide done."
After:
  Prompt: repository_analysis
  Resource: project://context
  Tools: read_workspace_file, invoke_local_model, write_output_artifact
  Completion: handled by Agent Runtime
```

