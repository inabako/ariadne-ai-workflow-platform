# Retry Policy

Retry only temporary failures such as model timeouts, MCP connection timeout before execution, or transient local IO.

Do not retry when a tool may have already performed a mutation.

