variable "environment" { type = string }
variable "database_stack_name" { type = string }
variable "enabled_engines" { type = set(string) }
variable "database_name" { type = string }
variable "app_username_secret_ref" { type = string }
variable "app_password_secret_ref" { type = string }
variable "timezone" { type = string }
variable "max_connections" { type = number }
variable "enable_backup" { type = bool }
variable "enable_restore_test" { type = bool }
variable "enable_migration" { type = bool }
variable "retention_days" { type = number }
variable "external_exposure" { type = bool }
variable "tls_enabled" { type = bool }

