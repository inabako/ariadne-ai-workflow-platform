output "selected_services" {
  description = "Selected platform services and default ports."
  value       = module.platform_catalog.selected_services
}

output "compose_files" {
  description = "Docker Compose files to apply in the copied target repository."
  value       = module.docker_compose_manifest.compose_files
}

output "validation_checks" {
  description = "Human-readable validation checks required before completion."
  value       = module.platform_catalog.validation_checks
}

