variable "collector_name" {
  type    = string
  default = "ariadne-otel-collector"
}

variable "collector_image" {
  type    = string
  default = "otel/opentelemetry-collector-contrib:0.156.0"
}

variable "collector_config_path" {
  type    = string
  default = "../config/generated/collector.yaml"
}

variable "network_name" {
  type    = string
  default = "ariadne_observability"
}

variable "otlp_grpc_port" {
  type    = number
  default = 4317
}

variable "otlp_http_port" {
  type    = number
  default = 4318
}

variable "health_check_port" {
  type    = number
  default = 13133
}

variable "environment_variables" {
  type      = map(string)
  sensitive = true
  default   = {}
}
