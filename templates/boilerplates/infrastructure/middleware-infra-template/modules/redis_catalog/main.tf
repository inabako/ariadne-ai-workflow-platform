locals {
  redis_connection_contract = {
    host_ref                = "redis.host"
    port_ref                = "redis.port"
    password_secret_ref     = var.password_secret_ref
    database_index          = 0
    tls_enabled             = var.tls_enabled
    connect_timeout_seconds = 5
    command_timeout_seconds = 3
    default_ttl_seconds     = var.default_ttl_seconds
    purpose                 = join(",", sort(tolist(var.redis_purposes)))
  }

  validation_checks = [
    "Redis process is running",
    "Redis port is reachable from approved sources",
    "unauthenticated connection is rejected",
    "authenticated PING succeeds",
    "SET / GET succeeds",
    "TTL is applied and expires as required",
    "maxmemory is configured as requested",
    "maxmemory-policy is configured as requested",
    "persistence mode matches the requirement",
    "data retention after restart matches the requirement",
    "backup file exists and has non-zero size when backup is enabled",
    "restore test verifies the expected key when restore test is enabled",
    "unnecessary external exposure is absent",
  ]

  human_check_items = concat(
    contains(var.redis_purposes, "session") && contains(["allkeys-lru", "allkeys-lfu", "allkeys-random"], var.eviction_policy) ? [
      "Session use with allkeys eviction can delete active sessions. Confirm acceptable loss behavior or change eviction policy."
    ] : [],
    contains(var.redis_purposes, "pubsub") ? [
      "Redis Pub/Sub does not provide durable redelivery. Confirm whether Redis Streams or another broker is required."
    ] : [],
    var.tls_enabled ? [
      "TLS is required. Provide certificate source and validation policy before production-like use."
    ] : []
  )

  evidence_plan = {
    requirement            = true
    redis_version          = var.redis_version
    purposes               = sort(tolist(var.redis_purposes))
    max_memory             = var.max_memory
    eviction_policy        = var.eviction_policy
    persistence_mode       = var.persistence_mode
    backup_enabled         = var.enable_backup
    restore_test_enabled   = var.enable_restore_test
    retention_days         = var.retention_days
    external_exposure      = var.external_exposure
    secret_values_redacted = true
    output_enabled         = var.evidence_enabled
  }
}

