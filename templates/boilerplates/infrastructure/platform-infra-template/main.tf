module "platform_catalog" {
  source = "./modules/platform_catalog"

  environment        = var.environment
  platform_name      = var.platform_name
  enabled_components = var.enabled_components
  admin_cidrs        = var.admin_cidrs
  secret_source      = var.secret_source
  enable_backup      = var.enable_backup
}

module "docker_compose_manifest" {
  source = "./modules/docker_compose_manifest"

  environment        = var.environment
  compose_profile    = var.compose_profile
  enabled_components = var.enabled_components
}

