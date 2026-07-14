module "platform_infra" {
  source = "../.."

  environment        = "stg"
  platform_name      = "ariadne-platform-stg"
  enabled_components = ["gitlab", "jenkins", "grafana", "zabbix"]
  compose_profile    = "full-platform"
  admin_cidrs        = ["10.0.0.0/8"]
  secret_source      = "stg-secret-manager-reference"
  enable_backup      = true
}

output "compose_files" {
  value = module.platform_infra.compose_files
}

