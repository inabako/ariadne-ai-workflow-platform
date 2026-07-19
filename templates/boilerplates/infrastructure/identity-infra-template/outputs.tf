output "identity_connection_contract" {
  description = "Shared OpenLDAP connection contract for application and platform templates."
  value       = module.identity_catalog.identity_connection_contract
  sensitive   = true
}

output "validation_checks" {
  description = "Required OpenLDAP validation checks."
  value       = module.identity_catalog.validation_checks
}

output "human_check_items" {
  description = "OpenLDAP decisions that require human review."
  value       = module.identity_catalog.human_check_items
}

output "compose_files" {
  description = "Docker Compose files selected by Terraform."
  value       = module.docker_compose_manifest.compose_files
}

output "evidence_plan" {
  description = "Evidence records that must be captured."
  value       = module.identity_catalog.evidence_plan
}

