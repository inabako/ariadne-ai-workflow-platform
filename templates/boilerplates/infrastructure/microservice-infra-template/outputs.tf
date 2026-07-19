output "network_contract" {
  description = "Network boundary contract."
  value       = module.network.contract
}

output "runtime_contract" {
  description = "Runtime contract."
  value       = module.runtime.contract
}

output "security_contract" {
  description = "Security exposure contract."
  value       = module.security.contract
}

output "observability_contract" {
  description = "Observability contract."
  value       = module.observability.contract
  sensitive   = true
}

output "dns_contract" {
  description = "DNS contract."
  value       = module.dns.contract
}
