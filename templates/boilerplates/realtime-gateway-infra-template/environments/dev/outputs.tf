output "gateway_infra" {
  description = "Aggregated dev infrastructure contract."
  value = {
    network       = module.gateway_infra.network_contract
    runtime       = module.gateway_infra.runtime_contract
    security      = module.gateway_infra.security_contract
    observability = module.gateway_infra.observability_contract
    dns           = module.gateway_infra.dns_contract
  }
  sensitive = true
}
