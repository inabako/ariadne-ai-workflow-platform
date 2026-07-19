module "middleware_infra" {
  source = "../.."

  environment           = "stg"
  middleware_stack_name = "ariadne-redis-stg"
  redis_version         = "7.2"
  redis_purposes        = ["cache", "session", "pubsub"]
  compose_profile       = "redis"
  external_exposure     = false
  tls_enabled           = true
  max_memory            = "1gb"
  eviction_policy       = "volatile-lru"
  persistence_mode      = "rdb-aof"
  enable_backup         = true
  enable_restore_test   = true
  evidence_enabled      = true
}

output "redis_connection_contract" {
  value     = module.middleware_infra.redis_connection_contract
  sensitive = true
}

output "validation_checks" {
  value = module.middleware_infra.validation_checks
}

output "human_check_items" {
  value = module.middleware_infra.human_check_items
}

output "compose_files" {
  value = module.middleware_infra.compose_files
}

