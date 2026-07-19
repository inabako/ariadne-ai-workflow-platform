locals {
  contract = {
    environment    = var.environment
    service_name   = var.service_name
    service_host   = var.service_host
    enable_dns     = var.enable_dns
    gateway_domain = var.gateway_domain
    mode           = var.enable_dns ? "managed" : "disabled"
  }
}

resource "terraform_data" "dns_contract" {
  input = local.contract
}
