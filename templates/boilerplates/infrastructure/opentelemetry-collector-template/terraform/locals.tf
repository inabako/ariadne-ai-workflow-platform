locals {
  collector_ports = {
    otlp_grpc    = var.otlp_grpc_port
    otlp_http    = var.otlp_http_port
    health_check = var.health_check_port
  }
}
