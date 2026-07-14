output "selected_databases" {
  description = "Selected database engines and connection contracts."
  value       = module.database_catalog.selected_databases
}

output "compose_files" {
  description = "Docker Compose files to apply in the copied target repository."
  value       = module.docker_compose_manifest.compose_files
}

output "validation_checks" {
  description = "Validation checks required before completion."
  value       = module.database_catalog.validation_checks
}

output "database_connection_contracts" {
  description = "Connection contracts for application and platform boilerplates."
  value       = module.database_catalog.connection_contracts
}

