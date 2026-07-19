module "gateway_infra" {
  source = "../.."

  environment          = "dev"
  service_name         = var.service_name
  service_image        = var.service_image
  service_host         = var.service_host
  runtime_type         = var.runtime_type
  health_port          = var.health_port
  metrics_port         = var.metrics_port
  inbound_tcp_ports    = var.inbound_tcp_ports
  inbound_udp_ports    = var.inbound_udp_ports
  allowed_client_cidrs = var.allowed_client_cidrs
  allowed_device_cidrs = var.allowed_device_cidrs
  allowed_admin_cidrs  = var.allowed_admin_cidrs
  enable_metrics       = var.enable_metrics
  enable_dns           = var.enable_dns
  gateway_domain       = var.gateway_domain
  enable_alert         = var.enable_alert
  alert_webhook_url    = var.alert_webhook_url
}
