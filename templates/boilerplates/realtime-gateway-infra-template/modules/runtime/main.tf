locals {
  runtime_priority = ["docker", "systemd", "k3s", "ecs"]
  contract = {
    environment       = var.environment
    service_name      = var.service_name
    service_image     = var.service_image
    runtime_type      = var.runtime_type
    health_port       = var.health_port
    metrics_port      = var.metrics_port
    inbound_tcp_ports = var.inbound_tcp_ports
    inbound_udp_ports = var.inbound_udp_ports
    restart_policy    = var.environment == "prod" ? "required" : "recommended"
    health_check      = "required"
    runtime_priority  = local.runtime_priority
  }
}

resource "terraform_data" "runtime_contract" {
  input = local.contract
}
