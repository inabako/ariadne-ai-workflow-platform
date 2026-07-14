# Architecture

```text
Gateway or CLI
  -> Runtime API
     -> Job Manager
     -> Workflow Engine
     -> Worker
        -> Model Adapter
        -> MCP Client Adapter
     -> Completion Evaluator
     -> Checkpoint Store
```

The runtime owns orchestration state. MCP servers own capabilities. Gateways own external user interface and platform-specific events.

