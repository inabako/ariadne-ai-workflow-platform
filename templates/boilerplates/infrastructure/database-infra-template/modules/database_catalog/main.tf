locals {
  engine_catalog = {
    postgresql = {
      default_port = 5432
      encoding     = "UTF-8"
      compose_file = "postgresql/docker-compose/compose.yaml"
      validation   = ["process", "port", "admin-auth", "app-auth", "database", "schema", "read-write", "persistence", "backup", "restore", "migration"]
    }
    mysql = {
      default_port = 3306
      encoding     = "utf8mb4"
      compose_file = "mysql/docker-compose/compose.yaml"
      validation   = ["process", "port", "admin-auth", "app-auth", "database", "privileges", "read-write", "persistence", "backup", "restore", "migration"]
    }
  }

  selected_databases = {
    for engine, database in local.engine_catalog : engine => merge(database, {
      environment         = var.environment
      database_stack_name = var.database_stack_name
      database_name       = var.database_name
      timezone            = var.timezone
      max_connections     = var.max_connections
      backup              = var.enable_backup
      restore_test        = var.enable_restore_test
      migration           = var.enable_migration
      retention_days      = var.retention_days
      external_exposure   = var.external_exposure
      tls_enabled         = var.tls_enabled
    }) if contains(var.enabled_engines, engine)
  }

  connection_contracts = {
    for engine, database in local.selected_databases : engine => {
      engine              = engine
      host_ref            = "${engine}.host"
      port_ref            = "${engine}.port"
      database_ref        = "${engine}.database"
      username_secret_ref = var.app_username_secret_ref
      password_secret_ref = var.app_password_secret_ref
      ssl_mode            = var.tls_enabled ? "required" : "disabled"
      migration_owner     = "project-defined"
    }
  }

  validation_checks = flatten([
    for engine, database in local.selected_databases : [
      for check in database.validation : "${engine}:${check}"
    ]
  ])
}

