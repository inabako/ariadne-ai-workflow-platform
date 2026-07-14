module "middleware_infra" {
  source = "../.."

  environment           = "prod"
  middleware_stack_name = "ariadne-redis-prod"
  redis_version         = "7.2"
  redis_purposes        = ["cache", "session"]
  compose_profile       = "redis"
  external_exposure     = false
  tls_enabled           = true
  max_memory            = "2gb"
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

