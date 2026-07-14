module "platform_infra" {
  source = "../.."

  environment        = "prod"
  platform_name      = "ariadne-platform-prod"
  enabled_components = ["gitlab", "jenkins", "grafana", "zabbix"]
  compose_profile    = "full-platform"
  admin_cidrs        = ["203.0.113.10/32"]
  secret_source      = "prod-secret-manager-reference"
  enable_backup      = true
}

output "compose_files" {
  value = module.platform_infra.compose_files
}

