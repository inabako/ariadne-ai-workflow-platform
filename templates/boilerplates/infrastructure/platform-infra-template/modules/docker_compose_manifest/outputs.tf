output "compose_files" {
  value = {
    environment = var.environment
    profile     = var.compose_profile
    integrated  = local.integrated_compose_files[var.compose_profile]
    components  = local.selected_component_files
  }
}

