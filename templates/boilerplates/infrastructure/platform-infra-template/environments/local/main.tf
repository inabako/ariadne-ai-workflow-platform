module "platform_infra" {
  source = "../.."

  environment        = "local"
  platform_name      = "ariadne-platform-local"
  enabled_components = ["gitlab", "jenkins", "grafana", "zabbix"]
  compose_profile    = "full-platform"
  admin_cidrs        = ["127.0.0.1/32"]
  secret_source      = "local-placeholder-secret-source"
  enable_backup      = true
}

output "compose_files" {
  value = module.platform_infra.compose_files
}

output "validation_checks" {
  value = module.platform_infra.validation_checks
}

