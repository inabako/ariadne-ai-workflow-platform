variable "environment" {
  type        = string
  description = "Deployment environment."
  default     = "local"

  validation {
    condition     = contains(["local", "dev", "stg", "prod"], var.environment)
    error_message = "environment must be local, dev, stg, or prod."
  }
}

variable "middleware_stack_name" {
  type        = string
  description = "Logical Redis middleware stack name."
  default     = "ariadne-redis"
}

variable "redis_version" {
  type        = string
  description = "Redis image version. Do not use latest."
  default     = "7.2"
}

variable "redis_purposes" {
  type        = set(string)
  description = "Redis purpose list, such as cache, session, distributed-lock, rate-limit, pubsub, queue-helper, temporary-state."
  default     = ["cache"]

  validation {
    condition = alltrue([
      for purpose in var.redis_purposes :
      contains(["cache", "session", "temporary-state", "distributed-lock", "rate-limit", "pubsub", "queue-helper"], purpose)
    ])
    error_message = "redis_purposes contains an unsupported purpose."
  }
}

variable "redis_port" {
  type        = number
  description = "Redis internal port."
  default     = 6379
}

variable "compose_profile" {
  type        = string
  description = "Docker Compose profile to apply."
  default     = "redis"

  validation {
    condition     = contains(["redis", "application-stack-example"], var.compose_profile)
    error_message = "compose_profile must be redis or application-stack-example."
  }
}

variable "external_exposure" {
  type        = bool
  description = "Expose Redis outside the internal Docker network."
  default     = false
}

variable "tls_enabled" {
  type        = bool
  description = "Whether TLS is required. Initial compose unit documents TLS but does not generate certificates."
  default     = false
}

variable "password_secret_ref" {
  type        = string
  description = "Secret reference for Redis password."
  default     = "redis.password"
}

variable "max_memory" {
  type        = string
  description = "Redis maxmemory value."
  default     = "512mb"
}

variable "eviction_policy" {
  type        = string
  description = "Redis maxmemory-policy."
  default     = "allkeys-lru"

  validation {
    condition     = contains(["noeviction", "allkeys-lru", "volatile-lru", "allkeys-lfu", "volatile-lfu", "allkeys-random", "volatile-random", "volatile-ttl"], var.eviction_policy)
    error_message = "eviction_policy is not a supported Redis maxmemory-policy."
  }
}

variable "persistence_mode" {
  type        = string
  description = "Redis persistence mode."
  default     = "aof"

  validation {
    condition     = contains(["none", "rdb", "aof", "rdb-aof"], var.persistence_mode)
    error_message = "persistence_mode must be none, rdb, aof, or rdb-aof."
  }
}

variable "volume_name" {
  type        = string
  description = "Redis persistent volume name."
  default     = "redis_data"
}

variable "default_ttl_seconds" {
  type        = number
  description = "Default TTL used by application contracts and validation."
  default     = 3600
}

variable "enable_backup" {
  type        = bool
  description = "Enable backup flow."
  default     = true
}

variable "enable_restore_test" {
  type        = bool
  description = "Enable restore validation flow."
  default     = true
}

variable "retention_days" {
  type        = number
  description = "Backup retention days."
  default     = 7
}

variable "evidence_enabled" {
  type        = bool
  description = "Enable evidence output."
  default     = true
}

