output "compose_files" {
  value = lookup(local.compose_files_by_profile, var.compose_profile, [])
}

