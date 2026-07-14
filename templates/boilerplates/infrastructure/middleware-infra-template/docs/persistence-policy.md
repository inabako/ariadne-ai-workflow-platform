# Persistence Policy

Supported persistence modes:

- none
- rdb
- aof
- rdb-aof

Persistence must be validated by restart behavior and aligned with loss tolerance. Cache-only Redis may disable backup, but the reason must be recorded in requirements and evidence.

