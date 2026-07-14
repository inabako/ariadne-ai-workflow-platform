module "middleware_infra" {
  source = "../.."

  environment           = "local"
  middleware_stack_name = "ariadne-redis-local"
  redis_version         = "7.2"
  redis_purposes        = ["cache", "session"]
  compose_profile       = "redis"
  external_exposure     = false
  tls_enabled           = false
  max_memory            = "256mb"
  eviction_policy       = "allkeys-lru"
  persistence_mode      = "aof"
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

