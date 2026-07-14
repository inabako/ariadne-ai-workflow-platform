module "database_infra" {
  source = "../.."

  environment             = "local"
  database_stack_name     = "ariadne-database-local"
  enabled_engines         = ["postgresql"]
  compose_profile         = "single-instance"
  database_name           = "app_db"
  app_username_secret_ref = "database.username"
  app_password_secret_ref = "database.password"
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

output "database_connection_contracts" {
  value = module.database_infra.database_connection_contracts
}

