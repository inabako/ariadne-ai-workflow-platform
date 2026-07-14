# Requirements Definition

DB IaC requirements must confirm:

- purpose
- engine
- version
- deployment target
- database name
- application user
- connection source
- persistence
- backup
- restore test
- migration

Conditional checks:

- multiple databases
- replica
- high availability
- external exposure
- TLS
- monitoring
- performance
- retention
- RPO
- RTO
- existing data migration

Do not infer unknown items. Stop for Human Check when a missing answer affects data loss, exposure, credential handling, backup, restore, migration, RPO, or RTO.

