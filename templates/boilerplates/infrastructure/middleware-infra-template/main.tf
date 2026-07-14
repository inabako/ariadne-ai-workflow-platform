module "redis_catalog" {
  source = "./modules/redis_catalog"

  environment           = var.environment
  middleware_stack_name = var.middleware_stack_name
  redis_version         = var.redis_version
  redis_purposes        = var.redis_purposes
  redis_port            = var.redis_port
  external_exposure     = var.external_exposure
  tls_enabled           = var.tls_enabled
  password_secret_ref   = var.password_secret_ref
  max_memory            = var.max_memory
  eviction_policy       = var.eviction_policy
  persistence_mode      = var.persistence_mode
  volume_name           = var.volume_name
  default_ttl_seconds   = var.default_ttl_seconds
  enable_backup         = var.enable_backup
  enable_restore_test   = var.enable_restore_test
  retention_days        = var.retention_days
  evidence_enabled      = var.evidence_enabled
}

module "docker_compose_manifest" {
  source = "./modules/docker_compose_manifest"

  environment     = var.environment
  compose_profile = var.compose_profile
}

