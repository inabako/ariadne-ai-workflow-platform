# Deployment Modes

## Phase 1: Terraform + Docker Compose

Terraform selects database engines and environment policy. Docker Compose starts PostgreSQL and/or MySQL.

## Phase 2: Ansible / VM / Bare Metal

Host provisioning can consume the same database configuration contract.

## Phase 3: Kubernetes / Helm

Kubernetes manifests or Helm charts can be added under engine-specific directories.

## Phase 4: Managed Database

AWS RDS / Aurora, Cloud SQL, Azure Database, and other managed services can be added under future managed database directories.

