module "collector" {
  source = "./modules/collector"

  collector_name          = var.collector_name
  collector_image         = var.collector_image
  collector_config_path   = abspath(var.collector_config_path)
  network_name            = var.network_name
  otlp_grpc_port          = var.otlp_grpc_port
  otlp_http_port          = var.otlp_http_port
  health_check_port       = var.health_check_port
  environment_variables   = var.environment_variables
}
