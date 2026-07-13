module "database_catalog" {
  source = "./modules/database_catalog"

  environment             = var.environment
  database_stack_name     = var.database_stack_name
  enabled_engines         = var.enabled_engines
  database_name           = var.database_name
  app_username_secret_ref = var.app_username_secret_ref
  app_password_secret_ref = var.app_password_secret_ref
  timezone                = var.timezone
  max_connections         = var.max_connections
  enable_backup           = var.enable_backup
  enable_restore_test     = var.enable_restore_test
  enable_migration        = var.enable_migration
  retention_days          = var.retention_days
  external_exposure       = var.external_exposure
  tls_enabled             = var.tls_enabled
}

module "docker_compose_manifest" {
  source = "./modules/docker_compose_manifest"

  environment     = var.environment
  compose_profile = var.compose_profile
  enabled_engines = var.enabled_engines
}

