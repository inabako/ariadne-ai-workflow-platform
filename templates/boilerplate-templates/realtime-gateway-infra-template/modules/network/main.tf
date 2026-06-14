locals {
  contract = {
    environment          = var.environment
    service_name         = var.service_name
    service_host         = var.service_host
    inbound_tcp_ports    = var.inbound_tcp_ports
    inbound_udp_ports    = var.inbound_udp_ports
    allowed_client_cidrs = var.allowed_client_cidrs
    allowed_device_cidrs = var.allowed_device_cidrs
    allowed_admin_cidrs  = var.allowed_admin_cidrs
    extension_points     = ["vpc", "lan", "subnet", "routing", "vpn", "relay"]
  }
}

resource "terraform_data" "network_contract" {
  input = local.contract
}
