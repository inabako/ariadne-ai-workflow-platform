module "database_infra" {
  source = "../.."

  environment             = "dev"
  database_stack_name     = "ariadne-database-dev"
  enabled_engines         = ["postgresql", "mysql"]
  compose_profile         = "multi-database"
  database_name           = "app_db"
  app_username_secret_ref = "dev/database/username"
  app_password_secret_ref = "dev/database/password"
  timezone                = "Asia/Tokyo"
  max_connections         = 100
  enable_backup           = true
  enable_restore_test     = true
  enable_migration        = true
  retention_days          = 7
  external_exposure       = false
  tls_enabled             = false
}

output "compose_files" {
  value = module.database_infra.compose_files
}

output "validation_checks" {
  value = module.database_infra.validation_checks
}

