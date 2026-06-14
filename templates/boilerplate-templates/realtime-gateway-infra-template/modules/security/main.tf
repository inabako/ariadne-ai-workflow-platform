locals {
  public_exposure = length(var.inbound_tcp_ports) + length(var.inbound_udp_ports) > 0
  contract = {
    environment          = var.environment
    service_name         = var.service_name
    inbound_tcp_ports    = var.inbound_tcp_ports
    inbound_udp_ports    = var.inbound_udp_ports
    allowed_client_cidrs = var.allowed_client_cidrs
    allowed_device_cidrs = var.allowed_device_cidrs
    allowed_admin_cidrs  = var.allowed_admin_cidrs
    health_port          = var.health_port
    metrics_port         = var.metrics_port
    public_exposure      = local.public_exposure
    admin_restricted     = length(var.allowed_admin_cidrs) > 0
    default_policy       = "deny-by-default"
  }
}

resource "terraform_data" "security_contract" {
  input = local.contract
}
