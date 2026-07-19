# Deployment Modes

## Phase 1: Terraform + Docker Compose

Terraform selects components and outputs compose files. Docker Compose starts the selected services.

## Phase 2: Ansible

Ansible can consume the same component selection contract for host provisioning.

## Phase 3: Kubernetes

Kubernetes manifests or Helm charts can be added under each product directory without changing `common/` responsibilities.

## Phase 4: Terraform Provider Resources

Cloud or platform provider resources can be added behind modules while preserving the same environment and validation contract.

