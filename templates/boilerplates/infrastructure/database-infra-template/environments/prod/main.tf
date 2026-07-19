module "database_infra" {
  source = "../.."

  environment             = "prod"
  database_stack_name     = "ariadne-database-prod"
  enabled_engines         = ["postgresql"]
  compose_profile         = "single-instance"
  database_name           = "app_db"
  app_username_secret_ref = "prod/database/username"
  app_password_secret_ref = "prod/database/password"
  timezone                = "Asia/Tokyo"
  max_connections         = 300
  enable_backup           = true
  enable_restore_test     = true
  enable_migration        = true
  retention_days          = 30
  external_exposure       = false
  tls_enabled             = true
}

output "compose_files" {
  value = module.database_infra.compose_files
}

output "validation_checks" {
  value = module.database_infra.validation_checks
}

