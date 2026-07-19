variable "environment" {
  description = "Deployment environment."
  type        = string

  validation {
    condition     = contains(["local", "dev", "stg", "prod"], var.environment)
    error_message = "environment must be one of local, dev, stg, or prod."
  }
}

variable "database_stack_name" {
  description = "Database infrastructure stack name."
  type        = string
  default     = "ariadne-database"

  validation {
    condition     = length(trimspace(var.database_stack_name)) > 0
    error_message = "database_stack_name is required."
  }
}

variable "enabled_engines" {
  description = "Database engines to include."
  type        = set(string)
  default     = ["postgresql"]

  validation {
    condition = alltrue([
      for engine in var.enabled_engines : contains(["postgresql", "mysql"], engine)
    ])
    error_message = "enabled_engines can contain only postgresql and mysql."
  }
}

variable "compose_profile" {
  description = "Integrated compose profile."
  type        = string
  default     = "single-instance"

  validation {
    condition     = contains(["single-instance", "multi-database", "application-stack-example"], var.compose_profile)
    error_message = "compose_profile must be single-instance, multi-database, or application-stack-example. primary-replica is documented but not implemented in phase 1."
  }
}

variable "database_name" {
  description = "Application database name."
  type        = string
  default     = "app_db"
}

variable "app_username_secret_ref" {
  description = "Secret reference for application database username."
  type        = string
  default     = "database.username"
}

variable "app_password_secret_ref" {
  description = "Secret reference for application database password."
  type        = string
  default     = "database.password"
}

variable "timezone" {
  description = "Database timezone."
  type        = string
  default     = "Asia/Tokyo"
}

variable "max_connections" {
  description = "Database max connections."
  type        = number
  default     = 100

  validation {
    condition     = var.max_connections > 0
    error_message = "max_connections must be greater than 0."
  }
}

variable "enable_backup" {
  description = "Enable backup validation."
  type        = bool
  default     = true
}

variable "enable_restore_test" {
  description = "Enable restore validation."
  type        = bool
  default     = true
}

variable "enable_migration" {
  description = "Enable migration entrypoint."
  type        = bool
  default     = true
}

variable "retention_days" {
  description = "Backup retention days."
  type        = number
  default     = 7

  validation {
    condition     = var.retention_days > 0
    error_message = "retention_days must be greater than 0."
  }
}

variable "external_exposure" {
  description = "Whether database ports are externally exposed."
  type        = bool
  default     = false
}

variable "tls_enabled" {
  description = "Whether TLS is required."
  type        = bool
  default     = false
}

