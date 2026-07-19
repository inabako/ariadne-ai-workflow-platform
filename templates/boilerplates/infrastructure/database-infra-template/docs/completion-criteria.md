# Completion Criteria

## Boilerplate

- `database-infra-template/` is copied into the target repository.
- Terraform `fmt`, `init`, `validate`, and `plan` pass for the selected environment.
- Docker Compose config is valid for selected engines.
- PostgreSQL and MySQL are managed independently.
- Common contracts are under `common/`.
- Evidence output is configured.

## PostgreSQL

- Starts with Docker Compose.
- Creates the target database.
- Creates or receives the application user through approved secret injection.
- Read / write succeeds.
- Data remains after restart.
- Backup succeeds.
- Restore succeeds.
- Migration entrypoint is executed or explicitly marked not applicable.
- Validation evidence is saved.

## MySQL

- Starts with Docker Compose.
- Creates the target database.
- Creates or receives the application user through approved secret injection.
- Read / write succeeds.
- Data remains after restart.
- Backup succeeds.
- Restore succeeds.
- Migration entrypoint is executed or explicitly marked not applicable.
- Validation evidence is saved.

## Integration

- Application boilerplates consume the connection contract.
- Platform infrastructure can refer to the DB contract without embedding DB construction.
- Admin credentials are not passed to application users.
- Secrets do not appear in Git or evidence.

