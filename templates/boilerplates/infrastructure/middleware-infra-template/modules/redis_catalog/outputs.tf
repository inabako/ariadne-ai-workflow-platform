output "redis_connection_contract" {
  value     = local.redis_connection_contract
  sensitive = true
}

output "validation_checks" {
  value = local.validation_checks
}

output "human_check_items" {
  value = local.human_check_items
}

output "evidence_plan" {
  value = local.evidence_plan
}

