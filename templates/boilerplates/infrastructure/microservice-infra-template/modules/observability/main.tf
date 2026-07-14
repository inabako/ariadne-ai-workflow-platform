locals {
  contract = {
    environment              = var.environment
    service_name             = var.service_name
    health_port              = var.health_port
    metrics_port             = var.metrics_port
    enable_metrics           = var.enable_metrics
    enable_alert             = var.enable_alert
    alert_webhook_configured = var.alert_webhook_url != null
    required_signals         = ["service_status", "connection_count", "error_count", "restart_count", "last_communication_time"]
  }
}

resource "terraform_data" "observability_contract" {
  input = local.contract
}
