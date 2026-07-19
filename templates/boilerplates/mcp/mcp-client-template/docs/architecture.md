# Architecture

```text
Application
  -> MCPClient facade
     -> server registry
     -> session manager
     -> capability cache
     -> transport adapter
        -> MCP server
```

The facade hides transport and session details from applications. It does not choose capabilities on behalf of the application.

