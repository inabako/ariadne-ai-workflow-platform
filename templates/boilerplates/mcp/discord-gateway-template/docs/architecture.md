# Architecture

```text
Discord
  -> Discord Adapter
  -> Interaction Router
  -> Authorization
  -> Command Mapper
  -> Runtime Client
  -> Agent Runtime API

Agent Runtime Event
  -> Event Consumer
  -> Deduplication
  -> Notification Formatter
  -> Discord Adapter
```

The Gateway is an input and notification boundary. It does not own runtime job execution.

