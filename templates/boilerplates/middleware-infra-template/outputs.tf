output "redis_connection_contract" {
  description = "Shared Redis connection contract for application and platform templates."
  value       = module.redis_catalog.redis_connection_contract
  sensitive   = true
}

output "validation_checks" {
  description = "Required Redis validation checks."
  value       = module.redis_catalog.validation_checks
}

output "human_check_items" {
  description = "Redis decisions that require human review."
  value       = module.redis_catalog.human_check_items
}

output "compose_files" {
  description = "Docker Compose files selected by Terraform."
  value       = module.docker_compose_manifest.compose_files
}

output "evidence_plan" {
  description = "Evidence records that must be captured."
  value       = module.redis_catalog.evidence_plan
}

