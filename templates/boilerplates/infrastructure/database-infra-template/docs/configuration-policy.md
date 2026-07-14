# Configuration Policy

- Keep environment differences in `environments/<env>/`.
- Keep engine-specific settings under `postgresql/` or `mysql/`.
- Keep secret values outside repository files.
- Keep application connection contracts separate from admin credentials.
- Default to no external DB exposure.
- Treat TLS, external exposure, backup retention, restore validation, RPO, and RTO as review items.

