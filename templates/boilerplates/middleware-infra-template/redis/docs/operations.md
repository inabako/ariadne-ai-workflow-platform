# Redis Operations

Operational completion requires more than container startup.

Minimum checks:

- authenticated PING
- unauthenticated connection rejected
- SET / GET
- TTL creation and expiry
- maxmemory and maxmemory-policy inspection
- persistence restart test when persistence is enabled
- backup creation and non-zero file size
- restore confirmation
- evidence redaction for secrets

