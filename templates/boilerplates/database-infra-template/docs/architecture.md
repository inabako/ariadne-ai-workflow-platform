# Architecture

Database Infrastructure Template separates database construction from application, gateway, and platform boilerplates.

## Layers

| Layer | Responsibility |
| --- | --- |
| Terraform | engine selection, environment settings, compose manifest, connection contract, validation handoff |
| Docker Compose | local/dev deployment unit for PostgreSQL and MySQL |
| common | engine-neutral config, network, storage, secrets, backup, restore, migration, health check, evidence |
| postgresql | PostgreSQL-specific compose, config, init SQL, scripts, tests, docs |
| mysql | MySQL-specific compose, config, init SQL, scripts, tests, docs |
| integrated | reusable usage profiles and application connection examples |

## Boundary

Applications consume `database_connection_contracts`. They do not create DB admin users, volumes, backup jobs, or restore procedures internally.

