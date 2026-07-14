variable "environment" { type = string }
variable "middleware_stack_name" { type = string }
variable "redis_version" { type = string }
variable "redis_purposes" { type = set(string) }
variable "redis_port" { type = number }
variable "external_exposure" { type = bool }
variable "tls_enabled" { type = bool }
variable "password_secret_ref" { type = string }
variable "max_memory" { type = string }
variable "eviction_policy" { type = string }
variable "persistence_mode" { type = string }
variable "volume_name" { type = string }
variable "default_ttl_seconds" { type = number }
variable "enable_backup" { type = bool }
variable "enable_restore_test" { type = bool }
variable "retention_days" { type = number }
variable "evidence_enabled" { type = bool }

