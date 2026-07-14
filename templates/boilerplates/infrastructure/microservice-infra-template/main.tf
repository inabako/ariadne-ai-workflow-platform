module "network" {
  source = "./modules/network"

  environment          = var.environment
  service_name         = var.service_name
  service_host         = var.service_host
  inbound_tcp_ports    = var.inbound_tcp_ports
  inbound_udp_ports    = var.inbound_udp_ports
  allowed_client_cidrs = var.allowed_client_cidrs
  allowed_device_cidrs = var.allowed_device_cidrs
  allowed_admin_cidrs  = var.allowed_admin_cidrs
}

module "runtime" {
  source = "./modules/runtime"

  environment       = var.environment
  service_name      = var.service_name
  service_image     = var.service_image
  runtime_type      = var.runtime_type
  health_port       = var.health_port
  metrics_port      = var.metrics_port
  inbound_tcp_ports = var.inbound_tcp_ports
  inbound_udp_ports = var.inbound_udp_ports
}

module "security" {
  source = "./modules/security"

  environment          = var.environment
  service_name         = var.service_name
  inbound_tcp_ports    = var.inbound_tcp_ports
  inbound_udp_ports    = var.inbound_udp_ports
  allowed_client_cidrs = var.allowed_client_cidrs
  allowed_device_cidrs = var.allowed_device_cidrs
  allowed_admin_cidrs  = var.allowed_admin_cidrs
  health_port          = var.health_port
  metrics_port         = var.metrics_port
}

module "observability" {
  source = "./modules/observability"

  environment       = var.environment
  service_name      = var.service_name
  health_port       = var.health_port
  metrics_port      = var.metrics_port
  enable_metrics    = var.enable_metrics
  enable_alert      = var.enable_alert
  alert_webhook_url = var.alert_webhook_url
}

module "dns" {
  source = "./modules/dns"

  environment    = var.environment
  service_name   = var.service_name
  service_host   = var.service_host
  enable_dns     = var.enable_dns
  gateway_domain = var.gateway_domain
}
