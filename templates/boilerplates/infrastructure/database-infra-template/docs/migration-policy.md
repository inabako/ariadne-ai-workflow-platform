# Migration Policy

Migration tooling is selected by the project.

Supported patterns include:

- SQL files
- Flyway
- Liquibase
- Prisma
- Drizzle
- Alembic
- project-specific migration runner

Required evidence:

- tool name and version
- migration command
- before version
- after version
- idempotency check or explicit reason it is not applicable
- failure behavior

