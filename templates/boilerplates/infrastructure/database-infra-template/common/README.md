# Common Database Infrastructure

`common/` contains database-engine-neutral contracts only. PostgreSQL-specific SQL and commands belong under `postgresql/`; MySQL-specific SQL and commands belong under `mysql/`.

Shared responsibilities:

- config schema
- network and port policy
- storage and volume policy
- secret reference policy
- backup / restore contract
- migration contract
- health check contract
- evidence contract
- validation contract

