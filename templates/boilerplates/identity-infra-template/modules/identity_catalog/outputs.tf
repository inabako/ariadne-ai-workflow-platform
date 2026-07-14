output "identity_connection_contract" {
  value     = local.identity_connection_contract
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

