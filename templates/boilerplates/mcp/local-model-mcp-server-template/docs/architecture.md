# Architecture

The template keeps MCP server concerns separate from agent runtime concerns.

```text
MCP Client
  -> Local Model MCP Server
     -> prompts
     -> resources
     -> tools
        -> workspace policy
        -> local model adapter
```

The server accepts requests, validates capability inputs, executes bounded tools, and returns structured results. It does not decide work goals or completion.

