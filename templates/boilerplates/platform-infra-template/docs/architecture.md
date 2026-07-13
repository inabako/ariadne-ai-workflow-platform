# Architecture

Platform Infrastructure Template separates shared infrastructure contracts from product-specific deploy units.

## Layers

| Layer | Responsibility |
| --- | --- |
| Terraform | component selection, environment settings, compose manifest, validation handoff |
| Docker Compose | local/dev/stg/prod deploy unit for selected platform components |
| common | network, storage, secrets, certificates, backup, rollback, evidence contracts |
| product directories | product-specific config, scripts, tests, docs |
| integrated-platform | combined development, observability, and full platform profiles |

## Boundary

This template does not implement application runtime infrastructure. Use `realtime-gateway-infra-template/` for application execution infrastructure.

